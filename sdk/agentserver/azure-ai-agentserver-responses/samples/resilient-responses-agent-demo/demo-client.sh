#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Resilient Responses Research Agent — Demo Client
#
# Showcases four platform capabilities of the responses package
# (all empirically validated against a Foundry hosted deployment):
#   1. LONG-RUNNING RESPONSES — the underlying @multi_turn_task lease
#      renewals (every ~30s) keep the platform's sandbox idle-reclaim
#      timer fresh, so a single response stays warm well past the
#      eviction window without any client-side keepalive ingress.
#   2. CRASH RECOVERY — when the container dies, the platform's nanny
#      worker restarts it within ~1 min on its own (no new ingress
#      needed); the resilient response auto-resumes with
#      `context.is_recovery is True` from its last completed phase.
#   3. STEERING — sending a follow-up turn while one is still running
#      (POST with `previous_response_id`) queues the input; the agent
#      winds down at the next phase boundary and re-enters with the
#      new input as a fresh steered turn (`context.is_steered_turn`).
#   4. OPERATOR CANCEL — POST /responses/{id}/cancel forces the
#      response to `status=cancelled` regardless of what the handler
#      emits (B11 contract).
#
# Commands:
#   ./demo-client.sh start "<topic>"   Dispatch + stream a fresh response (bg+stream)
#   ./demo-client.sh stream            Reconnect to the active response (no fresh POST)
#   ./demo-client.sh steer "<topic>"   Queue a follow-up turn — agent winds down
#                                      current turn at next checkpoint and switches
#   ./demo-client.sh cancel            Operator cancel of the active response
#   ./demo-client.sh crash             Trigger demo-mode container crash
#   ./demo-client.sh delete            DELETE /responses/{id}
#   ./demo-client.sh status            Show local session info
#   ./demo-client.sh logs              Stream container stdout/stderr via azd
#   ./demo-client.sh reset             Clear local session state
# ─────────────────────────────────────────────────────────────────────────────

set -uo pipefail

# ── Config ────────────────────────────────────────────────────────────────────

# Endpoint resolution (see _require_endpoint / _azd_responses_endpoint): an
# explicitly-exported NON-placeholder ENDPOINT wins; otherwise it is
# auto-discovered from the azd environment (the same source `azd up` reads/
# writes), so no manual export is needed. A mis-run command refuses to fire at a
# placeholder rather than silently no-op'ing at a bogus host.
ENDPOINT="${ENDPOINT:-}"
API_VERSION="${API_VERSION:-}"
MODEL="${MODEL:-gpt-4.1-mini}"
SESSION_FILE=".demo-session"
# Live in-flight response id, published mid-stream so a command in ANOTHER
# terminal (steer/cancel/stream) can target the run that is currently streaming.
ACTIVE_ID_FILE=".demo-session.active"
_ENDPOINT_PLACEHOLDER_RE='<account>|<project>'
_ENDPOINT_DEFAULT="https://<account>.services.ai.azure.com/api/projects/<project>/agents/resilient-responses-agent-demo/endpoint/protocols/openai"

# ── Colors ────────────────────────────────────────────────────────────────────

BOLD='\033[1m'
DIM='\033[2m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
CYAN='\033[36m'
RESET='\033[0m'

# ── Timestamps (PY-9) ─────────────────────────────────────────────────────────
# UTC ISO-8601 to match the server log clock (azd ai agent monitor), so client
# actions can be lined up against crash → restart → reclaim → recover timestamps.
_now_iso() { date -u +%Y-%m-%dT%H:%M:%SZ; }

# ── Endpoint discovery + guard (PY-8) ─────────────────────────────────────────
# Resolve the responses PROTOCOL-BASE endpoint (the client appends /responses…)
# from the azd environment — the authoritative source `azd up` reads/writes —
# so the demo works with no manual export. Sets globals ENDPOINT / API_VERSION.
_azd_responses_endpoint() {
    local raw="" env_name=""
    # 1. Preferred: azd env get-values (default-environment values).
    if command -v azd >/dev/null 2>&1; then
        raw=$(azd env get-values 2>/dev/null \
            | grep -E '^AGENT_[A-Z0-9_]*_RESPONSES_ENDPOINT=' | head -1 \
            | sed -E 's/^[^=]+=//; s/^"//; s/"$//')
    fi
    # 2. Fallback: parse ./.azure/<defaultEnvironment>/.env directly.
    if [[ -z "$raw" && -f ./.azure/config.json ]]; then
        env_name=$(python3 -c "import json;print(json.load(open('./.azure/config.json')).get('defaultEnvironment',''))" 2>/dev/null)
        if [[ -n "$env_name" && -f "./.azure/$env_name/.env" ]]; then
            raw=$(grep -E '^AGENT_[A-Z0-9_]*_RESPONSES_ENDPOINT=' "./.azure/$env_name/.env" | head -1 \
                | sed -E 's/^[^=]+=//; s/^"//; s/"$//')
        fi
    fi
    [[ -z "$raw" ]] && return 1
    # raw = https://…/endpoint/protocols/openai/responses?api-version=v1
    if [[ "$raw" == *"api-version="* ]]; then
        local ver="${raw##*api-version=}"; ver="${ver%%&*}"
        [[ -z "${API_VERSION:-}" ]] && API_VERSION="$ver"
    fi
    local base="${raw%%\?*}"    # drop query string
    base="${base%/responses}"   # drop trailing /responses → protocol base
    ENDPOINT="$base"
    return 0
}

# Every network command routes through ensure_token → _require_endpoint, so a
# command can never be silently fired at an unresolved placeholder host.
_require_endpoint() {
    # An explicitly-exported real ENDPOINT wins; otherwise auto-discover.
    if [[ -z "${ENDPOINT:-}" || "$ENDPOINT" =~ $_ENDPOINT_PLACEHOLDER_RE ]]; then
        _azd_responses_endpoint || true
    fi
    API_VERSION="${API_VERSION:-v1}"
    if [[ -z "${ENDPOINT:-}" || "$ENDPOINT" =~ $_ENDPOINT_PLACEHOLDER_RE ]]; then
        ENDPOINT="${ENDPOINT:-$_ENDPOINT_DEFAULT}"
        echo -e "${RED}ENDPOINT is unresolved (placeholder): ${ENDPOINT}${RESET}" >&2
        echo -e "${DIM}Run this from the demo directory (with ./.azure present) so it auto-resolves${RESET}" >&2
        echo -e "${DIM}from your azd env, or export a real ENDPOINT, e.g.:${RESET}" >&2
        echo -e "${DIM}  export ENDPOINT=https://<acct>.services.ai.azure.com/api/projects/<proj>/agents/resilient-responses-agent-demo/endpoint/protocols/openai${RESET}" >&2
        exit 1
    fi
}

# ── Session state ─────────────────────────────────────────────────────────────

load_session() {
    if [[ -f "$SESSION_FILE" ]]; then
        # shellcheck disable=SC1090
        source "$SESSION_FILE"
    fi
    # PY-7: if no RESPONSE_ID is persisted yet (a `start` is still streaming in
    # another terminal and only writes RESPONSE_ID to the session file when its
    # stream ends), fall back to the live id published mid-stream so cross-terminal
    # commands (steer / cancel / stream) can target the in-flight run.
    if [[ -z "${RESPONSE_ID:-}" && -f "$ACTIVE_ID_FILE" ]]; then
        RESPONSE_ID="$(cat "$ACTIVE_ID_FILE" 2>/dev/null || echo "")"
    fi
}

save_session() {
    {
        echo "RESPONSE_ID=\"${RESPONSE_ID:-}\""
        echo "PREV_RESPONSE_ID=\"${PREV_RESPONSE_ID:-}\""
        echo "LAST_SEQUENCE_NUMBER=\"${LAST_SEQUENCE_NUMBER:-0}\""
        echo "AGENT_SESSION_ID=\"${AGENT_SESSION_ID:-}\""
    } > "$SESSION_FILE"
}

# Mint a sandbox-affinity session id. agent_session_id is a top-level
# create-response body property and one session id == one sandbox/container, so
# pinning it makes start/steer/crash all land on the SAME sandbox — a 'crash'
# then kills the container actually running the in-flight response. uuidgen is
# not always installed, so fall back to python3.
mint_session_id() {
    if command -v uuidgen >/dev/null 2>&1; then
        echo "demo-$(uuidgen | tr 'A-Z' 'a-z' | tr -d '-' | cut -c1-12)"
    else
        echo "demo-$(python3 -c 'import uuid; print(uuid.uuid4().hex[:12])')"
    fi
}

ensure_token() {
    _require_endpoint
    if [[ "${LOCAL_NOAUTH:-0}" == "1" ]]; then
        TOKEN="local-noauth"
        return
    fi
    if [[ -z "${TOKEN:-}" ]]; then
        TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv 2>/dev/null)
        if [[ -z "$TOKEN" ]]; then
            echo -e "${RED}Failed to get Azure token. Run 'az login' first.${RESET}" >&2
            exit 1
        fi
    fi
}

# Extract a top-level JSON field. Returns empty string on missing/null.
_jq() {
    local json="$1"
    local key="$2"
    echo "$json" | python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    v = d.get('$key')
    print('' if v is None else v)
except Exception:
    print('')
" 2>/dev/null
}

# ── SSE stream renderer (Python — see comment) ───────────────────────────────

# Why a python renderer instead of bash:
#  - At LLM emit rate (50-100 tok/s) a bash 'while read | printf' loop
#    makes the real interactive terminal the bottleneck — one printf-per-
#    token causes syscall thrash. The python renderer batches writes per
#    SSE event, keeping the terminal responsive even on slow links.
#  - We also need a single place to persist LAST_SEQUENCE_NUMBER for
#    later reconnects.

stream_sse() {
    local url="$1"
    local extra_header="${2:-}"
    local method="${3:-GET}"
    local post_body="${4:-}"
    ensure_token

    local hdrs=(-H "Authorization: Bearer $TOKEN"
                -H "Accept: text/event-stream"
                -H "Foundry-Features: HostedAgents=V1Preview")
    if [[ -n "$extra_header" ]]; then
        hdrs+=(-H "$extra_header")
    fi

    # Use a pipe + python to render; on exit (Ctrl-C or stream end) the
    # renderer prints the last sequence number AND the discovered response
    # id (if the stream came from POST /responses) to sidecar files we read
    # back into LAST_SEQUENCE_NUMBER / RESPONSE_ID.
    #
    # PY-7: sidecars are PID-PRIVATE ($$) so a concurrent invocation in another
    # terminal (e.g. `crash` while `start` streams) can't rm/clobber the
    # streaming command's files. The captured id is ALSO published to the shared
    # ACTIVE_ID_FILE the instant it is seen, so cross-terminal commands can find
    # the in-flight run before this stream ends.
    local seq_file=".demo-session.lastseq.$$"
    local id_file=".demo-session.rid.$$"
    rm -f "$seq_file" "$id_file"

    STREAM_RESULT="ok"
    local curl_args=("${hdrs[@]}")
    if [[ "$method" == "POST" ]]; then
        curl_args+=(-X POST -H "Content-Type: application/json" --data "$post_body")
    fi
    curl -sS -N "${curl_args[@]}" "$url" 2>/dev/null | ACTIVE_ID_FILE="$ACTIVE_ID_FILE" python3 -u -c "
import json, sys, os, signal

SEQ_FILE = '$seq_file'
ID_FILE = '$id_file'
ACTIVE_FILE = os.environ.get('ACTIVE_ID_FILE', '')

def _save_seq(n):
    try:
        with open(SEQ_FILE, 'w') as f:
            f.write(str(n))
    except Exception:
        pass

def _save_id(rid):
    for path in (ID_FILE, ACTIVE_FILE):
        if not path:
            continue
        try:
            with open(path, 'w') as f:
                f.write(str(rid))
        except Exception:
            pass

def _clear_active():
    # The run reached a terminal — it is no longer the in-flight target.
    if ACTIVE_FILE:
        try:
            os.remove(ACTIVE_FILE)
        except OSError:
            pass

_last = 0
_id_saved = False

def _handle_sigint(*_):
    _save_seq(_last)
    sys.exit(0)

signal.signal(signal.SIGINT, _handle_sigint)

current_event = None
current_data = []

for raw in sys.stdin:
    line = raw.rstrip('\n')
    if not line:
        if current_event and current_data:
            data = '\n'.join(current_data)
            try:
                payload = json.loads(data)
            except Exception:
                payload = {'_raw': data}
            seq = payload.get('sequence_number')
            if isinstance(seq, int):
                _last = seq
            # Extract response id from the first lifecycle event we see and
            # publish it (PID-private + shared active file) immediately.
            if not _id_saved:
                resp = payload.get('response') or {}
                rid = resp.get('id')
                if rid:
                    _save_id(rid)
                    _id_saved = True
            t = payload.get('type', current_event)
            if t == 'response.output_text.delta':
                sys.stdout.write(payload.get('delta', ''))
                sys.stdout.flush()
            elif t in ('response.created', 'response.in_progress', 'response.completed',
                       'response.failed', 'response.cancelled', 'response.incomplete'):
                resp = payload.get('response') or {}
                status = resp.get('status') or t.split('.')[-1]
                sys.stdout.write('\n\033[2m[' + t + ' status=' + str(status) + ']\033[0m\n')
                sys.stdout.flush()
                if t in ('response.completed', 'response.failed',
                         'response.cancelled', 'response.incomplete'):
                    _clear_active()
        current_event = None
        current_data = []
        continue
    if line.startswith('event:'):
        current_event = line.split(':', 1)[1].strip()
    elif line.startswith('data:'):
        current_data.append(line.split(':', 1)[1].lstrip())

_save_seq(_last)
print()
"
    local rc=$?
    if [[ -f "$id_file" ]]; then
        local new_id
        new_id=$(cat "$id_file" 2>/dev/null || echo "")
        if [[ -n "$new_id" ]]; then
            RESPONSE_ID="$new_id"
        fi
        rm -f "$id_file"
    fi
    if [[ -f "$seq_file" ]]; then
        LAST_SEQUENCE_NUMBER=$(cat "$seq_file" 2>/dev/null || echo "0")
        rm -f "$seq_file"
    fi
    save_session
    if [[ "$rc" -ne 0 && "$rc" -ne 130 ]]; then
        STREAM_RESULT="error"
    fi
}

# ── Commands ──────────────────────────────────────────────────────────────────

cmd_start() {
    local topic="${1:-Research the future of quantum computing}"
    RESPONSE_ID=""
    PREV_RESPONSE_ID=""
    LAST_SEQUENCE_NUMBER="0"
    AGENT_SESSION_ID="$(mint_session_id)"  # fresh sandbox-affinity session per run
    rm -f "$ACTIVE_ID_FILE"                 # drop any stale in-flight id from a prior run
    save_session
    ensure_token

    echo -e "${GREEN}Starting a fresh research response${RESET}"
    echo -e "${DIM}Topic: ${topic}${RESET}"
    echo -e "${DIM}Session: ${AGENT_SESSION_ID}${RESET}"

    local body
    body=$(python3 -c "
import json, sys
print(json.dumps({
    'model': '$MODEL',
    'input': sys.argv[1],
    'agent_session_id': sys.argv[2],
    'stream': True,
    'store': True,
    'background': True,
}))
" "$topic" "$AGENT_SESSION_ID")

    local response
    # POST with stream=true returns SSE; pipe through stream_sse which
    # extracts response_id from the first response.created event,
    # renders the rest, and persists LAST_SEQUENCE_NUMBER on exit.
    echo ""
    echo -e "${BOLD}Streaming. ${DIM}Use Ctrl-C to detach; reconnect later with './demo-client.sh stream'.${RESET}"
    stream_sse "${ENDPOINT}/responses?api-version=${API_VERSION}" "" POST "$body"
    if [[ -z "${RESPONSE_ID:-}" ]]; then
        echo -e "${RED}Failed to dispatch (no response.id captured from SSE).${RESET}"
        exit 1
    fi
    echo -e "${DIM}Dispatched: response_id=${RESPONSE_ID}${RESET}"
    _report_stream_result
}

cmd_stream() {
    load_session
    if [[ -z "${RESPONSE_ID:-}" ]]; then
        echo -e "${RED}No active response. Run './demo-client.sh start \"<topic>\"' first.${RESET}" >&2
        exit 1
    fi
    ensure_token

    echo -e "${DIM}Reconnecting to response ${RESPONSE_ID}${RESET}"
    local url="${ENDPOINT}/responses/${RESPONSE_ID}?stream=true&api-version=${API_VERSION}"
    if [[ "${LAST_SEQUENCE_NUMBER:-0}" != "0" ]]; then
        url="${url}&starting_after=${LAST_SEQUENCE_NUMBER}"
        echo -e "${DIM}Resuming from sequence_number ${LAST_SEQUENCE_NUMBER}${RESET}"
    fi
    stream_sse "$url"
    _report_stream_result
}

cmd_steer() {
    local topic="${1:-}"
    if [[ -z "$topic" ]]; then
        echo -e "${RED}Usage: ./demo-client.sh steer \"<new topic>\"${RESET}" >&2
        exit 1
    fi
    load_session
    if [[ -z "${RESPONSE_ID:-}" ]]; then
        echo -e "${RED}No active response to steer. Run './demo-client.sh start' first.${RESET}" >&2
        exit 1
    fi
    ensure_token

    echo -e "${YELLOW}Steering: queuing follow-up turn on response ${RESPONSE_ID}${RESET}"
    echo -e "${DIM}New topic: ${topic}${RESET}"

    local body
    body=$(python3 -c "
import json, sys
print(json.dumps({
    'model': '$MODEL',
    'input': sys.argv[1],
    'previous_response_id': sys.argv[2],
    'agent_session_id': sys.argv[3],
    'stream': True,
    'store': True,
    'background': True,
}))
" "$topic" "$RESPONSE_ID" "${AGENT_SESSION_ID:-}")

    PREV_RESPONSE_ID="$RESPONSE_ID"
    RESPONSE_ID=""
    LAST_SEQUENCE_NUMBER="0"
    save_session

    echo ""
    echo -e "${BOLD}Streaming the steered turn.${RESET}"
    # POST returns SSE (stream=true) — stream_sse captures the new
    # response_id from the first response.created event.
    stream_sse "${ENDPOINT}/responses?api-version=${API_VERSION}" "" POST "$body"
    if [[ -z "${RESPONSE_ID:-}" ]]; then
        echo -e "${RED}Failed to steer (no response.id captured from SSE).${RESET}"
        RESPONSE_ID="$PREV_RESPONSE_ID"
        save_session
        exit 1
    fi
    echo -e "${DIM}New response_id=${RESPONSE_ID} (steered after ${PREV_RESPONSE_ID})${RESET}"
    _report_stream_result
}

cmd_cancel() {
    load_session
    if [[ -z "${RESPONSE_ID:-}" ]]; then
        echo -e "${RED}No active response.${RESET}" >&2
        exit 1
    fi
    ensure_token

    echo -e "${YELLOW}Cancelling response ${RESPONSE_ID}${RESET}"
    curl -sS -X POST \
        -H "Authorization: Bearer $TOKEN" \
        -H "Foundry-Features: HostedAgents=V1Preview" \
        "${ENDPOINT}/responses/${RESPONSE_ID}/cancel?api-version=${API_VERSION}" | python3 -m json.tool
}

cmd_crash() {
    load_session
    ensure_token

    # Pin the crash to the run's session so it kills the sandbox actually running
    # the in-flight response (not an unrelated replica). If no session is
    # persisted (crash invoked standalone), mint one so the request is at least
    # sandbox-consistent.
    if [[ -z "${AGENT_SESSION_ID:-}" ]]; then
        AGENT_SESSION_ID="$(mint_session_id)"
        save_session
    fi

    echo -e "${RED}✖ crash fired @ $(_now_iso) — input=\"crash\", session=${AGENT_SESSION_ID}${RESET}"
    echo -e "${DIM}(bare agent_session_id-pinned crash — NOT a previous_response_id steer, which would${RESET}"
    echo -e "${DIM} only run AFTER the current turn; requires DEMO_MODE=1 on the server)${RESET}"

    local body
    body=$(python3 -c "
import json, sys
print(json.dumps({
    'model': '$MODEL',
    'input': 'crash',
    'agent_session_id': sys.argv[1],
    'stream': True,
    'store': True,
    'background': True,
}))
" "$AGENT_SESSION_ID")
    # The crash POST returns SSE briefly (response.created + response.failed
    # if our handler emits before exit) — pipe through stream_sse so we see
    # whatever comes out before the container dies. The renderer's
    # accumulated curl will then error out when the connection drops.
    stream_sse "${ENDPOINT}/responses?api-version=${API_VERSION}" "" POST "$body"

    echo ""
    echo -e "${DIM}Container will exit shortly. Platform nanny restarts within ~1 min.${RESET}"
    echo -e "${DIM}If you had an active response, './demo-client.sh stream' after restart will${RESET}"
    echo -e "${DIM}reconnect and resume from the last completed phase.${RESET}"
}

cmd_delete() {
    load_session
    if [[ -z "${RESPONSE_ID:-}" ]]; then
        echo -e "${RED}No active response.${RESET}" >&2
        exit 1
    fi
    ensure_token

    echo -e "${YELLOW}Deleting response ${RESPONSE_ID}${RESET}"
    curl -sS -X DELETE \
        -H "Authorization: Bearer $TOKEN" \
        -H "Foundry-Features: HostedAgents=V1Preview" \
        "${ENDPOINT}/responses/${RESPONSE_ID}?api-version=${API_VERSION}" | python3 -m json.tool
}

cmd_status() {
    load_session
    echo -e "${BOLD}Local session state${RESET} ${DIM}(${SESSION_FILE})${RESET}"
    echo "  RESPONSE_ID:          ${RESPONSE_ID:-<none>}"
    echo "  PREV_RESPONSE_ID:     ${PREV_RESPONSE_ID:-<none>}"
    echo "  LAST_SEQUENCE_NUMBER: ${LAST_SEQUENCE_NUMBER:-0}"
    echo ""
    if [[ -n "${RESPONSE_ID:-}" ]]; then
        ensure_token
        echo -e "${BOLD}Server-side snapshot${RESET}"
        curl -sS \
            -H "Authorization: Bearer $TOKEN" \
            -H "Foundry-Features: HostedAgents=V1Preview" \
            "${ENDPOINT}/responses/${RESPONSE_ID}?api-version=${API_VERSION}" | python3 -m json.tool
    fi
}

cmd_logs() {
    azd ai agent monitor resilient-responses-agent-demo --follow "$@"
}

cmd_reset() {
    rm -f "$SESSION_FILE" "$ACTIVE_ID_FILE" .demo-session.lastseq.* .demo-session.rid.*
    echo -e "${DIM}Cleared ${SESSION_FILE}.${RESET}"
}

_report_stream_result() {
    case "$STREAM_RESULT" in
        ok)    : ;;
        error) echo -e "${RED}Stream errored; try './demo-client.sh stream' to reconnect.${RESET}" >&2 ;;
    esac
}

usage() {
    cat <<'USAGE'
Resilient Responses Research Agent — Demo Client

Usage:
  ./demo-client.sh start "<topic>"   Dispatch + stream a fresh research response
  ./demo-client.sh stream            Reconnect to the active response (no fresh POST)
  ./demo-client.sh steer "<topic>"   Queue a follow-up turn — agent winds down
                                     current turn at next checkpoint and switches
  ./demo-client.sh cancel            Operator cancel of the active response
  ./demo-client.sh crash             Trigger demo-mode container crash
  ./demo-client.sh delete            DELETE /responses/{id}
  ./demo-client.sh status            Show local session info + server snapshot
  ./demo-client.sh logs              Stream container stdout/stderr via azd
  ./demo-client.sh reset             Clear local session state

Environment overrides:
  ENDPOINT     Responses protocol-base endpoint (…/endpoint/protocols/openai).
               Auto-discovered from your azd environment when unset — only
               export this to override. A placeholder/unresolved value is
               refused (the command fails loudly instead of silently no-op'ing).
  API_VERSION  Auto-discovered from the azd endpoint; default: v1.
  MODEL        Default: gpt-4.1-mini.
USAGE
}

# ── Dispatch ──────────────────────────────────────────────────────────────────

# PY-9: UTC ISO-8601 banners (to stderr, so they never pollute SSE stdout) so the
# client timeline can be lined up against the timestamped server log.
_CMD="${1:-help}"
_START_EPOCH=$(date +%s)
echo -e "${CYAN}▶ command '${_CMD}' triggered @ $(_now_iso)${RESET}" >&2
_end_banner() {
    local rc=$?
    echo -e "${CYAN}⏹ '${_CMD}' ended @ $(_now_iso) (elapsed $(( $(date +%s) - _START_EPOCH ))s, exit ${rc})${RESET}" >&2
}
trap _end_banner EXIT

case "${1:-}" in
    start)   shift; cmd_start "${1:-}" ;;
    stream)  cmd_stream ;;
    steer)   shift; cmd_steer "${1:-}" ;;
    cancel)  cmd_cancel ;;
    crash)   cmd_crash ;;
    delete)  cmd_delete ;;
    status)  cmd_status ;;
    logs)    shift; cmd_logs "$@" ;;
    reset)   cmd_reset ;;
    -h|--help|help|"") usage ;;
    *)
        echo -e "\033[31mUnknown command: $1\033[0m" >&2
        usage
        exit 1
        ;;
esac
