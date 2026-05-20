#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Durable Research Agent — Demo Client
#
# Usage:
#   Terminal 1 (start research):   ./demo-client.sh start "quantum computing"
#   Terminal 2 (crash the agent):  ./demo-client.sh crash
#   Terminal 2 (cancel the task):  ./demo-client.sh cancel
#
# The session ID is shared via a file (.demo-session) so both terminals
# operate on the same agent session.
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────

ENDPOINT="https://e2e-tests-westus2-account.services.ai.azure.com/api/projects/e2e-tests-westus2/agents/durable-research-agent/endpoint/protocols"
API_VERSION="2025-11-15-preview"
SESSION_FILE=".demo-session"

# ── Colors ────────────────────────────────────────────────────────────────────

BOLD='\033[1m'
DIM='\033[2m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
CYAN='\033[36m'
RESET='\033[0m'

# ── Helpers ───────────────────────────────────────────────────────────────────

get_token() {
    az account get-access-token --resource https://ai.azure.com --query accessToken -o tsv 2>/dev/null
}

load_session() {
    if [[ -f "$SESSION_FILE" ]]; then
        source "$SESSION_FILE"
    fi
}

save_session() {
    echo "SESSION_ID=\"${SESSION_ID}\"" > "$SESSION_FILE"
    echo "INV_ID=\"${INV_ID}\"" >> "$SESSION_FILE"
    echo "LAST_EVENT_ID=\"${LAST_EVENT_ID:-0}\"" >> "$SESSION_FILE"
}

ensure_token() {
    if [[ -z "${TOKEN:-}" ]]; then
        echo -e "${DIM}Fetching access token...${RESET}"
        TOKEN=$(get_token)
        if [[ -z "$TOKEN" ]]; then
            echo -e "${RED}ERROR: Failed to get token. Run 'az login' first.${RESET}"
            exit 1
        fi
    fi
}

# ── SSE Stream Reader ─────────────────────────────────────────────────────────

# Stream result: set by stream_sse to indicate how the stream ended
STREAM_RESULT=""  # "complete", "crashed", "disconnected", "error"

stream_sse() {
    local url="$1"
    local method="${2:-GET}"
    local body="${3:-}"
    local headers_file
    headers_file=$(mktemp)
    STREAM_RESULT="disconnected"  # default: assume disconnect

    local curl_args=(
        -sN
        -X "$method"
        -D "$headers_file"
        -H "Authorization: Bearer $TOKEN"
        -H "Content-Type: application/json"
        -H "Accept: text/event-stream"
    )
    if [[ -n "$body" ]]; then
        curl_args+=(-d "$body")
    fi

    # Stream and parse SSE events, writing result to a temp file
    local result_file
    result_file=$(mktemp)
    echo "disconnected" > "$result_file"

    # Track event IDs in a temp file (subshell can't set parent vars)
    local event_id_file
    event_id_file=$(mktemp)
    echo "${LAST_EVENT_ID:-0}" > "$event_id_file"

    # Use || true on the pipeline to prevent set -e/pipefail from killing the script
    # when curl exits non-zero (e.g., connection reset by server crash)
    # We also track a "current_id" to implement client-side skip of already-seen events
    local skip_until
    skip_until="${LAST_EVENT_ID:-0}"

    ( curl "${curl_args[@]}" "$url" || true ) | while IFS= read -r line; do
        # Skip empty lines and comments
        [[ -z "$line" || "$line" == $'\r' ]] && continue
        [[ "$line" == :* ]] && continue

        # Parse "id: N" lines (SSE event ID for resumption)
        if [[ "$line" == id:* ]]; then
            local eid="${line#id: }"
            eid="${eid%$'\r'}"
            echo "$eid" > "$event_id_file"
            continue
        fi

        # Parse "data: {...}" lines
        if [[ "$line" == data:* ]]; then
            # Client-side skip: if current event ID ≤ last seen, suppress display
            local current_eid
            current_eid=$(cat "$event_id_file")
            if [[ "$current_eid" -le "$skip_until" && "$skip_until" -gt 0 ]]; then
                continue
            fi

            local json="${line#data: }"
            json="${json%$'\r'}"

            local type
            type=$(echo "$json" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('type',''))" 2>/dev/null || echo "")
            local display_content
            display_content=$(echo "$json" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('content',''), end='')" 2>/dev/null || echo "")

            case "$type" in
                token)
                    printf '%s' "$display_content"
                    ;;
                done)
                    local full_text
                    full_text=$(echo "$json" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('full_text',''))" 2>/dev/null || echo "")
                    if [[ "$full_text" == *"crashing"* ]]; then
                        echo "crashed" > "$result_file"
                    else
                        echo "complete" > "$result_file"
                    fi
                    echo ""
                    break
                    ;;
                error)
                    echo -e "\n${RED}ERROR: $display_content${RESET}"
                    echo "error" > "$result_file"
                    break
                    ;;
            esac
        else
            # Non-SSE line — likely a JSON error response from the platform/server
            echo -e "${DIM}[debug] ${line}${RESET}" >&2
        fi
    done || true

    STREAM_RESULT=$(cat "$result_file")
    LAST_EVENT_ID=$(cat "$event_id_file")
    save_session
    rm -f "$result_file" "$event_id_file"

    # Check HTTP status from response headers
    if [[ -f "$headers_file" ]]; then
        local http_status
        http_status=$(head -1 "$headers_file" 2>/dev/null | tr -d '\r' || true)
        if [[ -n "$http_status" && "$http_status" != *" 200 "* ]]; then
            echo -e "${DIM}[debug] HTTP: ${http_status}${RESET}" >&2
        fi
        rm -f "$headers_file"
    fi
}

# ── Commands ──────────────────────────────────────────────────────────────────

dispatch_task() {
    # POST to dispatch the task (fire-and-forget). Returns immediately.
    # Captures invocation_id + session_id from the JSON response body.
    local topic="$1"
    local url="${ENDPOINT}/invocations?api-version=${API_VERSION}&agent_session_id=${SESSION_ID}"
    local body="{\"message\": \"${topic}\"}"

    local response
    response=$(curl -s -X POST "$url" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "$body")

    # Parse invocation_id and session_id from response JSON
    local inv sess status
    inv=$(echo "$response" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('invocation_id',''))" 2>/dev/null || echo "")
    sess=$(echo "$response" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('session_id',''))" 2>/dev/null || echo "")
    status=$(echo "$response" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('status',''))" 2>/dev/null || echo "")

    if [[ -n "$inv" ]]; then
        INV_ID="$inv"
    fi
    if [[ -n "$sess" ]]; then
        SESSION_ID="$sess"
    fi
    save_session

    echo -e "${DIM}Task ${status}: inv=${INV_ID:0:30}...${RESET}"
}

stream_via_get() {
    # GET /invocations/{inv_id} — streams SSE from the active task
    if [[ -z "${INV_ID:-}" ]]; then
        echo -e "${RED}No invocation ID. Cannot stream.${RESET}"
        return 1
    fi
    local url="${ENDPOINT}/invocations/${INV_ID}?api-version=${API_VERSION}"
    # Append last_event_id query param for server-side skip on reconnect
    if [[ -n "${LAST_EVENT_ID:-}" && "${LAST_EVENT_ID:-0}" != "0" ]]; then
        url="${url}&last_event_id=${LAST_EVENT_ID}"
    fi
    stream_sse "$url" "GET" ""
}

cmd_start() {
    local topic="${1:-Research the history and future of quantum computing}"

    # Generate new session or reuse existing
    if [[ -f "$SESSION_FILE" ]]; then
        load_session
        echo -e "${YELLOW}Reusing session: ${SESSION_ID}${RESET}"
    else
        SESSION_ID="demo-$(uuidgen | tr '[:upper:]' '[:lower:]')"
        INV_ID=""
        LAST_EVENT_ID="0"
        save_session
        echo -e "${GREEN}New session: ${SESSION_ID}${RESET}"
    fi

    ensure_token

    echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${BOLD}${CYAN}║  Durable Research Agent — Starting                      ║${RESET}"
    echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════════════╝${RESET}"
    echo -e "${DIM}Topic: ${topic}${RESET}"
    echo -e "${DIM}Session: ${SESSION_ID}${RESET}"
    echo ""

    # Step 1: POST dispatches task (fire-and-forget, returns immediately)
    dispatch_task "$topic"

    # Step 2: GET streams SSE results
    stream_via_get

    # Handle stream result
    case "$STREAM_RESULT" in
        complete)
            echo -e "${GREEN}━━━ Research complete ━━━${RESET}"
            ;;
        crashed|disconnected)
            echo -e "${YELLOW}━━━ Stream interrupted (${STREAM_RESULT}) ━━━${RESET}"
            reconnect_loop "$topic"
            ;;
        error)
            echo -e "${RED}━━━ Stream error ━━━${RESET}"
            ;;
    esac
}

reconnect_loop() {
    local topic="${1:-reconnect}"

    local attempt=0
    while true; do
        attempt=$((attempt + 1))
        echo ""
        echo -e "${YELLOW}⚡ Reconnecting (attempt ${attempt})...${RESET}"
        echo -e "${DIM}Session: ${SESSION_ID}${RESET}"
        sleep 5

        ensure_token

        # POST again with same session — gets new invocation ID
        # (platform preserves mapping because POST returned 202 immediately)
        dispatch_task "$topic"

        # GET with new invocation ID to stream
        stream_via_get

        case "$STREAM_RESULT" in
            complete)
                echo -e "${GREEN}━━━ Research complete ━━━${RESET}"
                return 0
                ;;
            crashed|disconnected)
                echo -e "${YELLOW}━━━ Stream interrupted again (${STREAM_RESULT}). Retrying... ━━━${RESET}"
                ;;
            error)
                echo -e "${RED}━━━ Error on reconnect. Retrying in 5s... ━━━${RESET}"
                sleep 5
                ;;
        esac
    done
}

cmd_crash() {
    load_session

    if [[ -z "${SESSION_ID:-}" ]]; then
        echo -e "${RED}No active session. Run './demo-client.sh start' first.${RESET}"
        exit 1
    fi

    ensure_token

    echo -e "${RED}${BOLD}💥 Crashing the agent...${RESET}"
    echo -e "${DIM}Session: ${SESSION_ID}${RESET}"

    # POST with "crash" message — server dispatches crash signal and returns 202
    local url="${ENDPOINT}/invocations?api-version=${API_VERSION}&agent_session_id=${SESSION_ID}"
    local response
    response=$(curl -s -X POST "$url" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"message": "crash"}')

    echo -e "${DIM}Response: ${response}${RESET}"
    echo -e "\n${RED}Agent process killed (os._exit). Supervisor will restart it.${RESET}"
    echo -e "${DIM}Terminal 1 will auto-reconnect when the process restarts.${RESET}"
}

cmd_cancel() {
    load_session

    if [[ -z "${INV_ID:-}" ]]; then
        echo -e "${RED}No invocation ID. Run './demo-client.sh start' first.${RESET}"
        exit 1
    fi

    ensure_token

    echo -e "${YELLOW}🛑 Cancelling task...${RESET}"
    echo -e "${DIM}Invocation: ${INV_ID}${RESET}"

    local url="${ENDPOINT}/invocations/${INV_ID}/cancel?api-version=${API_VERSION}"
    local response
    response=$(curl -s -X POST "$url" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{}')

    echo -e "${GREEN}${response}${RESET}"
}

cmd_reset() {
    rm -f "$SESSION_FILE"
    echo -e "${GREEN}Session cleared. Next 'start' will create a fresh session.${RESET}"
}

cmd_status() {
    load_session
    if [[ -f "$SESSION_FILE" ]]; then
        echo -e "${CYAN}Session ID:${RESET}    ${SESSION_ID:-<none>}"
        echo -e "${CYAN}Invocation ID:${RESET} ${INV_ID:-<none>}"
    else
        echo -e "${DIM}No active session.${RESET}"
    fi
}

cmd_logs() {
    load_session
    if [[ -z "${SESSION_ID:-}" ]]; then
        echo -e "${RED}No active session. Run './demo-client.sh start' first.${RESET}"
        exit 1
    fi

    ensure_token

    echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════════════╗${RESET}"
    echo -e "${BOLD}${CYAN}║  Container Logs — Streaming                             ║${RESET}"
    echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════════════╝${RESET}"
    echo -e "${DIM}Session: ${SESSION_ID}${RESET}"
    echo -e "${DIM}Polling GET every 3s for server-side logs (Ctrl-C to stop)${RESET}"
    echo ""

    # Poll the agent's health/status endpoint or just show SSE stream with debug info
    # For now: continuously tail the GET stream showing all raw data
    while true; do
        if [[ -n "${INV_ID:-}" ]]; then
            local url="${ENDPOINT}/invocations/${INV_ID}?api-version=${API_VERSION}"
            echo -e "${DIM}[$(date +%H:%M:%S)] Connecting to inv=${INV_ID:0:30}...${RESET}"
            ( curl -sN -X GET "$url" \
                -H "Authorization: Bearer $TOKEN" \
                -H "Accept: text/event-stream" 2>/dev/null || true ) | while IFS= read -r line; do
                [[ -z "$line" || "$line" == $'\r' ]] && continue
                echo -e "${DIM}[$(date +%H:%M:%S)]${RESET} $line"
            done || true
        fi
        sleep 3
        ensure_token  # refresh token if needed
    done
}

# ── Main ──────────────────────────────────────────────────────────────────────

usage() {
    echo -e "${BOLD}Durable Research Agent — Demo Client${RESET}"
    echo ""
    echo "Usage:"
    echo "  ./demo-client.sh start [topic]   Start research (auto-reconnects on disconnect)"
    echo "  ./demo-client.sh crash           Crash the agent (run from second terminal)"
    echo "  ./demo-client.sh cancel          Cancel the running task"
    echo "  ./demo-client.sh logs            Stream raw SSE data (run in third terminal)"
    echo "  ./demo-client.sh status          Show current session info"
    echo "  ./demo-client.sh reset           Clear session (start fresh)"
    echo ""
    echo "Demo workflow:"
    echo "  Terminal 1: ./demo-client.sh start \"quantum computing\""
    echo "  Terminal 2: ./demo-client.sh crash"
    echo "  (Terminal 1 auto-reconnects and shows recovery)"
    echo "  Terminal 3: ./demo-client.sh logs   (optional: watch raw events)"
}

case "${1:-}" in
    start)   cmd_start "${2:-}" ;;
    crash)   cmd_crash ;;
    cancel)  cmd_cancel ;;
    logs)    cmd_logs ;;
    status)  cmd_status ;;
    reset)   cmd_reset ;;
    *)       usage ;;
esac
