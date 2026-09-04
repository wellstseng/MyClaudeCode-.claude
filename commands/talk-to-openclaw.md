# /talk-to-openclaw — Send a message to OpenClaw via Gateway WebSocket

When this skill is invoked, send a message to the local OpenClaw agent.

## Usage

```
/talk-to-openclaw <message>
```

## Implementation

1. Run the gateway-chat.js script:
   ```bash
   node C:/Users/holyl/.claude/scripts/gateway-chat.js "<user's message>"
   ```

2. The script:
   - Connects to Gateway WebSocket at ws://127.0.0.1:18789/ws
   - Authenticates with token from openclaw.json
   - Sends the message to session `agent:main:main`
   - Waits for streaming response (up to 2 minutes)
   - Outputs JSON result

3. Parse the output:
   - `{"status":"sent","runId":"..."}` → message accepted, waiting for response
   - `{"status":"complete","response":"..."}` → OpenClaw responded
   - `{"status":"timeout","response":null}` → OpenClaw LLM may not be running
   - `{"status":"error","error":"..."}` → connection or auth failure

4. If Gateway is not running (connection refused), inform the user:
   > "OpenClaw Gateway is not running. Start it with `openclaw gateway` or via OpenClaw Panel."

5. Report the result to the user.

## Alternative: File-based messaging (if WebSocket fails)

If the WebSocket approach fails, fall back to the Bridge endpoint:
```bash
node C:/Users/holyl/.claude/scripts/send-to-openclaw.js "<message>"
```
This writes to `.openclaw/workspace/claude-messages.jsonl` which OpenClaw can read.

## Environment Variables (optional overrides)

- `OPENCLAW_SESSION` — target session (default: `agent:main:main`)
- `OPENCLAW_TIMEOUT` — timeout in ms (default: `120000`)
- `OPENCLAW_GATEWAY_TOKEN` — gateway auth token (default: from openclaw.json)
