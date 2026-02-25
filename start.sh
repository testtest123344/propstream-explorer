#!/bin/bash
# PropStream API Server + ngrok (two permanent static domains)
# - PropStream (port 5000): nonmenacing-flintiest-carla.ngrok-free.dev
# - OpenClaw gateway (port 18789): reggiebot-gateway.ngrok.app
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="/tmp"

# Kill any existing instances
pkill -f "python3.*propstream-server/api/server.py" 2>/dev/null
pkill -f "ngrok" 2>/dev/null
pkill -f "cloudflared" 2>/dev/null
sleep 2

# Start Flask server
cd "$SCRIPT_DIR"
python3 api/server.py &>"$LOG_DIR/propstream-server.log" &
FLASK_PID=$!
echo "Flask started (PID: $FLASK_PID)"

# Wait for Flask to be ready
for i in {1..10}; do
    curl -s http://localhost:5000/api/health >/dev/null 2>&1 && echo "Flask ready" && break
    sleep 1
done

# Start both ngrok tunnels (both have permanent static domains)
ngrok start --all > "$LOG_DIR/ngrok-all.log" 2>&1 &
NGROK_PID=$!
echo "ngrok started (PID: $NGROK_PID)"
sleep 5

echo "Tunnels:"
echo "  PropStream: https://nonmenacing-flintiest-carla.ngrok-free.dev"
echo "  Gateway:    https://reggiebot-gateway.ngrok.app"

# Save state
echo "{\"flask_pid\": $FLASK_PID, \"ngrok_pid\": $NGROK_PID, \"propstream_url\": \"https://nonmenacing-flintiest-carla.ngrok-free.dev\", \"gateway_url\": \"https://reggiebot-gateway.ngrok.app\", \"started\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" > "$SCRIPT_DIR/state.json"

# Keep alive — restart processes if they die (URLs are permanent, no Railway updates needed)
while true; do
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        echo "Flask died, restarting..."
        cd "$SCRIPT_DIR"
        python3 api/server.py &>"$LOG_DIR/propstream-server.log" &
        FLASK_PID=$!
        echo "Flask restarted (PID: $FLASK_PID)"
    fi
    if ! kill -0 $NGROK_PID 2>/dev/null; then
        echo "ngrok died, restarting..."
        ngrok start --all > "$LOG_DIR/ngrok-all.log" 2>&1 &
        NGROK_PID=$!
        echo "ngrok restarted (PID: $NGROK_PID)"
        # No Railway update needed — both URLs are permanent
    fi
    sleep 30
done
