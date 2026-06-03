#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Durable Research Agent — Demo Client
#
# Showcases three platform capabilities of the durable-task primitive
# (all empirically validated against e2e-tests-westus2):
#   1. LONG-RUNNING TASKS — the framework's PATCH .../tasks/<id> lease
#      renewals (every ~30s) keep the platform's sandbox idle-reclaim
#      timer fresh, so a single run stays warm well past the 15-min
#      eviction window without any client-side keepalive ingress.
#   2. CRASH RECOVERY — when the container dies, the platform's nanny
#      worker restarts it within ~1 min on its own (no new ingress
#      needed); the durable task auto-resumes from its last checkpoint.
#   3. STEERING — sending a new turn while a turn is still running
#      causes the agent to wind down at the next checkpoint and start
#      fresh on the new topic.
#
# Commands:
#   ./demo-client.sh start "<topic>"   Dispatch and stream a fresh research run
#   ./demo-client.sh stream            Reconnect to the active run (no fresh POST)
#   ./demo-client.sh steer "<topic>"   Queue a steering input — agent winds down
#                                      current turn at next checkpoint and switches
#   ./demo-client.sh crash             Kill the process (DEMO_MODE=1 on server)
#   ./demo-client.sh cancel            Operator cancel of the active run
#   ./demo-client.sh status            Show local session info
#   ./demo-client.sh logs              Stream container stdout/stderr via azd
#   ./demo-client.sh reset             Clear local session state
# ─────────────────────────────────────────────────────────────────────────────

set -uo pipefail

# ── Config ────────────────────────────────────────────────────────────────────

ENDPOINT="https://e2e-tests-westus2-account.services.ai.azure.com/api/projects/e2e-tests-westus2/agents/durable-research-agent/endpoint/protocols"
API_VERSION="v1"
SESSION_FILE=".demo-session"

# ── Colors ────────────────────────────────────────────────────────────────────

BOLD='\033[1m'
DIM='\033[2m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
CYAN='\033[36m'
MAGENTA='\033[35m'
BLUE='\033[34m'
RESET='\033[0m'

# ── Session state ─────────────────────────────────────────────────────────────

load_session() {
    if [[ -f "$SESSION_FILE" ]]; then
        # shellcheck disable=SC1090
        source "$SESSION_FILE"
    fi
}

save_session() {
    {
        echo "SESSION_ID=\"${SESSION_ID:-}\""
        echo "INV_ID=\"${INV_ID:-}\""
        echo "LAST_EVENT_ID=\"${LAST_EVENT_ID:-0}\""
    } > "$SESSION_FILE"
}

ensure_token() {
    if [[ -z "${TOKEN:-}" ]]; then
        TOKEN=$(az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv 2>/dev/null)
        if [[ -z "$TOKEN" ]]; then
            echo -e "${RED}Failed to get Azure token. Run 'az login' first.${RESET}" >&2
            exit 1
        fi
    fi
}

# ── SSE stream renderer ───────────────────────────────────────────────────────

# Pretty-prints stream events from agent.py. Recognised types:
#   run_start, recovered, phase_start, subcall_start, token, subcall_end,
#   phase_end, run_complete, winding_down, done
#
# Every block-style event is prefixed with [HH:MM:SSZ] — the client's local
# UTC wall-clock at render time, so you can compare against `server_time=`
# (the server's UTC at emit time) and `uptime=` (the server process's
# monotonic seconds-since-boot, which resets to ~0 on crash recovery).

_now_utc() {
    date -u +'%H:%M:%SZ'
}

render_event() {
    local json="$1"
    local etype
    etype=$(echo "$json" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('type',''))" 2>/dev/null || true)

    local now
    now=$(_now_utc)

    case "$etype" in
        run_start)
            local topic entry_mode total uptime srv
            topic=$(_jq "$json" topic)
            entry_mode=$(_jq "$json" entry_mode)
            total=$(_jq "$json" total_phases)
            uptime=$(_jq "$json" server_uptime_sec)
            srv=$(_jq "$json" server_time_utc)
            local prior
            prior=$(_jq "$json" prior_topic)
            echo ""
            echo -e "${BOLD}${CYAN}══════════════════════════════════════════════════════════════${RESET}"
            echo -e "${DIM}[${now}]${RESET} ${BOLD}${CYAN}▶ Run start${RESET}    topic=${BOLD}${topic}${RESET}  (${total} phases)"
            [[ -n "$prior" && "$prior" != "None" ]] && \
                echo -e "  ${YELLOW}(steered from prior topic: ${prior})${RESET}"
            echo -e "  entry_mode=${entry_mode}   server_time=${srv}   uptime=${uptime}s"
            echo -e "${BOLD}${CYAN}══════════════════════════════════════════════════════════════${RESET}"
            ;;
        recovered)
            local completed total srv uptime
            completed=$(_jq "$json" completed_phases)
            total=$(_jq "$json" total_phases)
            srv=$(_jq "$json" server_time_utc)
            uptime=$(_jq "$json" server_uptime_sec)
            echo ""
            echo -e "${DIM}[${now}]${RESET} ${BOLD}${GREEN}🔁 Recovered from crash${RESET}   resuming from phase ${completed}/${total}"
            echo -e "  server_time=${srv}   uptime=${uptime}s  ${DIM}(uptime ~0s = fresh container)${RESET}"
            ;;
        phase_start)
            local phase total title srv uptime
            phase=$(_jq "$json" phase)
            total=$(_jq "$json" total)
            title=$(_jq "$json" title)
            srv=$(_jq "$json" server_time_utc)
            uptime=$(_jq "$json" server_uptime_sec)
            echo ""
            echo -e "${BOLD}${BLUE}──────────────────────────────────────────────────────────────${RESET}"
            echo -e "${DIM}[${now}]${RESET} ${BOLD}${BLUE}▶ Phase ${phase}/${total}${RESET} — ${title}"
            echo -e "  ⏰ server_time=${srv}   uptime=${uptime}s"
            echo -e "${BOLD}${BLUE}──────────────────────────────────────────────────────────────${RESET}"
            ;;
        subcall_start)
            local role idx of
            role=$(_jq "$json" role)
            idx=$(_jq "$json" index)
            of=$(_jq "$json" of)
            echo ""
            echo -e "${DIM}  [${now}]  [${role} ${idx}/${of}] ───${RESET}"
            ;;
        token)
            local content
            content=$(echo "$json" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('content',''), end='')" 2>/dev/null || true)
            printf '%s' "$content"
            ;;
        subcall_end)
            echo ""
            ;;
        phase_end)
            local phase total title srv uptime duration
            phase=$(_jq "$json" phase)
            total=$(_jq "$json" total)
            title=$(_jq "$json" title)
            srv=$(_jq "$json" server_time_utc)
            uptime=$(_jq "$json" server_uptime_sec)
            duration=$(_jq "$json" duration_sec)
            echo ""
            echo -e "${DIM}[${now}]${RESET} ${GREEN}✅ Phase ${phase}/${total} done${RESET} — ${title}"
            echo -e "  ⏰ server_time=${srv}   uptime=${uptime}s   ⏱  duration=${duration}s"
            ;;
        winding_down)
            local cause completed total pending srv uptime
            cause=$(_jq "$json" cause)
            completed=$(_jq "$json" completed_phases)
            total=$(_jq "$json" total_phases)
            pending=$(_jq "$json" pending_steering_inputs)
            srv=$(_jq "$json" server_time_utc)
            uptime=$(_jq "$json" server_uptime_sec)
            echo ""
            echo -e "${DIM}[${now}]${RESET} ${BOLD}${MAGENTA}↓ Winding down${RESET}   cause=${cause}   completed=${completed}/${total}   pending_steers=${pending}"
            echo -e "  ⏰ server_time=${srv}   uptime=${uptime}s"
            ;;
        run_complete)
            local total srv uptime
            total=$(_jq "$json" phases_completed)
            srv=$(_jq "$json" server_time_utc)
            uptime=$(_jq "$json" server_uptime_sec)
            echo ""
            echo -e "${BOLD}${GREEN}══════════════════════════════════════════════════════════════${RESET}"
            echo -e "${DIM}[${now}]${RESET} ${BOLD}${GREEN}✅ Run complete${RESET}   ${total} phases   ⏰ ${srv}   uptime=${uptime}s"
            echo -e "${BOLD}${GREEN}══════════════════════════════════════════════════════════════${RESET}"
            ;;
        done)
            local reason
            reason=$(_jq "$json" reason)
            echo ""
            if [[ -n "$reason" && "$reason" != "None" ]]; then
                echo -e "${DIM}[${now}]${RESET} ${YELLOW}══ Stream done (${reason}) ══${RESET}"
            else
                echo -e "${DIM}[${now}]${RESET} ${GREEN}══ Stream done ══${RESET}"
            fi
            ;;
        *)
            echo -e "${DIM}[${now}] [unknown event] ${json}${RESET}"
            ;;
    esac
}

_jq() {
    # Read a top-level JSON field. Returns empty string on missing/null.
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

# ── SSE reader ───────────────────────────────────────────────────────────────

STREAM_RESULT=""  # "complete" | "disconnected" | "error"

stream_sse() {
    local url="$1"
    STREAM_RESULT="disconnected"

    local event_id_file result_file
    event_id_file=$(mktemp)
    result_file=$(mktemp)
    echo "${LAST_EVENT_ID:-0}" > "$event_id_file"
    echo "disconnected" > "$result_file"

    ( curl -sN -X GET \
        -H "Authorization: Bearer $TOKEN" \
        -H "Accept: text/event-stream" \
        -H "Foundry-Features: HostedAgents=V1Preview" \
        "$url" || true ) | while IFS= read -r line; do
        [[ -z "$line" || "$line" == $'\r' ]] && continue
        [[ "$line" == :* ]] && continue

        if [[ "$line" == id:* ]]; then
            local eid="${line#id: }"
            eid="${eid%$'\r'}"
            echo "$eid" > "$event_id_file"
            continue
        fi

        if [[ "$line" == data:* ]]; then
            local json="${line#data: }"
            json="${json%$'\r'}"

            local etype
            etype=$(_jq "$json" type)

            render_event "$json"

            if [[ "$etype" == "done" || "$etype" == "run_complete" ]]; then
                echo "complete" > "$result_file"
                break
            fi
        else
            echo -e "${DIM}[non-SSE line] ${line}${RESET}" >&2
        fi
    done || true

    STREAM_RESULT=$(cat "$result_file")
    LAST_EVENT_ID=$(cat "$event_id_file")
    save_session
    rm -f "$event_id_file" "$result_file"
}

# ── Commands ──────────────────────────────────────────────────────────────────

cmd_start() {
    local topic="${1:-Research the future of quantum computing}"
    SESSION_ID="demo-$(uuidgen | tr '[:upper:]' '[:lower:]')"
    INV_ID=""
    LAST_EVENT_ID="0"
    save_session
    ensure_token

    echo -e "${GREEN}New session: ${SESSION_ID}${RESET}"
    echo -e "${DIM}Topic: ${topic}${RESET}"

    local response
    response=$(curl -s -X POST \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -H "Foundry-Features: HostedAgents=V1Preview" \
        -d "{\"message\": \"${topic}\"}" \
        "${ENDPOINT}/invocations?api-version=${API_VERSION}&agent_session_id=${SESSION_ID}")
    INV_ID=$(_jq "$response" invocation_id)
    SESSION_ID=$(_jq "$response" session_id)
    save_session
    echo -e "${DIM}Dispatched: invocation_id=${INV_ID}${RESET}"

    echo ""
    echo -e "${BOLD}Streaming. ${DIM}Use Ctrl-C to detach; reconnect later with './demo-client.sh stream'.${RESET}"
    stream_sse "${ENDPOINT}/invocations/${INV_ID}?api-version=${API_VERSION}"
    _report_stream_result
}

cmd_stream() {
    load_session
    if [[ -z "${INV_ID:-}" ]]; then
        echo -e "${RED}No active session. Run './demo-client.sh start \"<topic>\"' first.${RESET}" >&2
        exit 1
    fi
    ensure_token

    echo -e "${DIM}Reconnecting to invocation ${INV_ID}${RESET}"
    local url="${ENDPOINT}/invocations/${INV_ID}?api-version=${API_VERSION}"
    if [[ "${LAST_EVENT_ID:-0}" != "0" ]]; then
        url="${url}&last_event_id=${LAST_EVENT_ID}"
        echo -e "${DIM}Resuming from event ${LAST_EVENT_ID}${RESET}"
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
    if [[ -z "${SESSION_ID:-}" ]]; then
        echo -e "${RED}No active session. Run './demo-client.sh start \"<topic>\"' first.${RESET}" >&2
        exit 1
    fi
    ensure_token

    echo -e "${BOLD}${MAGENTA}Steering session ${SESSION_ID} to: ${topic}${RESET}"

    # Send a fresh POST. Because the task is steerable and an in-progress
    # run exists, the framework queues this as a steering input.
    local response
    response=$(curl -s -X POST \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -H "Foundry-Features: HostedAgents=V1Preview" \
        -d "{\"message\": \"${topic}\"}" \
        "${ENDPOINT}/invocations?api-version=${API_VERSION}&agent_session_id=${SESSION_ID}")
    echo -e "${DIM}Response: ${response}${RESET}"
    local new_inv
    new_inv=$(_jq "$response" invocation_id)
    if [[ -n "$new_inv" ]]; then
        INV_ID="$new_inv"
        LAST_EVENT_ID="0"
        save_session
        echo -e "${DIM}New invocation: ${INV_ID}. Use './demo-client.sh stream' to attach.${RESET}"
    fi
}

cmd_crash() {
    load_session
    if [[ -z "${SESSION_ID:-}" ]]; then
        echo -e "${RED}No active session. Run './demo-client.sh start \"<topic>\"' first.${RESET}" >&2
        exit 1
    fi
    ensure_token

    echo -e "${RED}${BOLD}💥 Crashing the agent container...${RESET}"
    echo -e "${DIM}Session: ${SESSION_ID}${RESET}"

    # The platform only proxies /invocations* — we use the special
    # "crash" sentinel message, which the agent (when DEMO_MODE=1)
    # interprets as "exit the process".
    local response
    response=$(curl -s -X POST \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -H "Foundry-Features: HostedAgents=V1Preview" \
        -d '{"message": "crash"}' \
        "${ENDPOINT}/invocations?api-version=${API_VERSION}&agent_session_id=${SESSION_ID}")
    echo -e "${DIM}Response: ${response}${RESET}"
    echo ""
    echo -e "${YELLOW}The container will exit. The platform's nanny worker brings it back${RESET}"
    echo -e "${YELLOW}within ~1 min on its own (no client ingress needed) and the durable${RESET}"
    echo -e "${YELLOW}task auto-recovers from its last checkpoint.${RESET}"
    echo ""
    echo -e "${DIM}Run './demo-client.sh stream' whenever you're ready to reconnect.${RESET}"
    echo -e "${DIM}Look for a 'Recovered from crash' marker (uptime resets to ~0).${RESET}"
}

cmd_cancel() {
    load_session
    if [[ -z "${INV_ID:-}" ]]; then
        echo -e "${RED}No active session. Run './demo-client.sh start \"<topic>\"' first.${RESET}" >&2
        exit 1
    fi
    ensure_token

    echo -e "${YELLOW}🛑 Cancelling invocation ${INV_ID}${RESET}"
    local response
    response=$(curl -s -X POST \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -H "Foundry-Features: HostedAgents=V1Preview" \
        -d '{}' \
        "${ENDPOINT}/invocations/${INV_ID}/cancel?api-version=${API_VERSION}")
    echo -e "${GREEN}${response}${RESET}"
}

cmd_status() {
    load_session
    if [[ -f "$SESSION_FILE" ]]; then
        echo -e "${CYAN}Session ID:${RESET}    ${SESSION_ID:-<none>}"
        echo -e "${CYAN}Invocation ID:${RESET} ${INV_ID:-<none>}"
        echo -e "${CYAN}Last event ID:${RESET} ${LAST_EVENT_ID:-0}"
    else
        echo -e "${DIM}No local session.${RESET}"
    fi
}

cmd_logs() {
    load_session
    if [[ -z "${SESSION_ID:-}" ]]; then
        echo -e "${RED}No active session. Run './demo-client.sh start \"<topic>\"' first.${RESET}" >&2
        exit 1
    fi
    echo -e "${DIM}Streaming container stdout/stderr for session ${SESSION_ID}${RESET}"
    azd ai agent monitor --session-id "${SESSION_ID}" --follow
}

cmd_reset() {
    rm -f "$SESSION_FILE"
    echo -e "${GREEN}Session cleared.${RESET}"
}

_report_stream_result() {
    case "$STREAM_RESULT" in
        complete)
            ;;
        disconnected)
            echo ""
            echo -e "${YELLOW}── Stream disconnected ──${RESET}"
            echo -e "${DIM}The agent may still be running on the server.${RESET}"
            echo -e "${DIM}Reconnect with: ./demo-client.sh stream${RESET}"
            ;;
        error)
            echo -e "${RED}── Stream error ──${RESET}" ;;
    esac
}

# ── Main ──────────────────────────────────────────────────────────────────────

usage() {
    cat <<EOF
${BOLD}Durable Research Agent — Demo Client${RESET}

Commands:
  ${BOLD}start "<topic>"${RESET}    Dispatch a fresh research run and stream it
  ${BOLD}stream${RESET}             Reconnect to the active run (resumes from last_event_id)
  ${BOLD}steer "<topic>"${RESET}    Queue a steering input — agent winds down at next
                     checkpoint and starts fresh on the new topic
  ${BOLD}crash${RESET}              Kill the container (POST /invocations with message="crash";
                     requires DEMO_MODE=1 on the server image)
  ${BOLD}cancel${RESET}             Cooperative cancel of the active run
  ${BOLD}status${RESET}             Show local session info
  ${BOLD}logs${RESET}               Stream container stdout/stderr (azd ai agent monitor)
  ${BOLD}reset${RESET}              Clear local session state

Three-terminal workflow:
  Terminal 1: ./demo-client.sh start "quantum computing"     # streams ~33 min of phases
  Terminal 2: ./demo-client.sh logs                          # peek at server logs
  Terminal 3: ./demo-client.sh crash                         # any time → nanny restores ~1 min later
              ./demo-client.sh steer "fusion energy"         # mid-run pivot
EOF
}

case "${1:-}" in
    start)   shift; cmd_start "${1:-}" ;;
    stream)  cmd_stream ;;
    steer)   shift; cmd_steer "${1:-}" ;;
    crash)   cmd_crash ;;
    cancel)  cmd_cancel ;;
    status)  cmd_status ;;
    logs)    cmd_logs ;;
    reset)   cmd_reset ;;
    *)       usage ;;
esac
