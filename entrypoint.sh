#!/usr/bin/env bash
set -e

echo "=================================================="
echo "⚡ Starting Octra Lite Node for Umbrel"
echo "=================================================="

DATA_DIR="${OCTRA_DATA_DIR:-/var/lib/octra/devnet}"
SYNC_DIR="${OCTRA_SYNC_DIR:-/var/lib/octra/devnet.state_sync}"
NODE_ROLE="${NODE_ROLE:-observer}"
NODE_NAME="${NODE_NAME:-umbrel-octra-node}"
PUBLIC_HOST="${PUBLIC_HOST:-127.0.0.1}"

mkdir -p "$DATA_DIR" "$SYNC_DIR" /var/lib/octra/logs

# Start Web Status Dashboard in background
echo "📊 Launching Web Dashboard on port 8080..."
python3 /opt/octra/dashboard/server.py &
DASHBOARD_PID=$!

# Handle graceful shutdown
trap 'echo "🛑 Stopping Octra Node..."; kill $DASHBOARD_PID $NODE_PID 2>/dev/null; exit 0' SIGTERM SIGINT

echo "🚀 Executing Octra Node binary in role: $NODE_ROLE..."

/opt/octra/bin/octra_node.exe \
  --role "$NODE_ROLE" \
  --name "$NODE_NAME" \
  --advertise "$PUBLIC_HOST:19000" \
  --api-port 8081 \
  --consensus-port 19000 \
  --p2p-port 9000 \
  --data-dir "$DATA_DIR" \
  --sync-stage "$SYNC_DIR" \
  --network /opt/octra/config/network.env &

NODE_PID=$!
wait $NODE_PID
