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

# Ensure nodes.config exists in cwd (/opt/octra) and data directory
if [ ! -f /opt/octra/nodes.config ]; then
  echo "[]" > /opt/octra/nodes.config
fi
if [ ! -f "$DATA_DIR/nodes.config" ]; then
  cp /opt/octra/nodes.config "$DATA_DIR/nodes.config" 2>/dev/null || true
fi

# Clean up any partial/interrupted initial store from an earlier crashed run
if [ -d "$DATA_DIR/irmin_store" ] && [ ! -f "$DATA_DIR/irmin_store/HEAD.json" ]; then
  echo "⚠️ Detected incomplete store from interrupted run. Reinitializing fresh store..."
  rm -rf "$DATA_DIR/irmin_store"
fi

# Set node daemon environment variables
export OCTRA_API_PORT=8081
export OCTRA_P2P_PORT=9000
export OCTRA_DATA_DIR="$DATA_DIR"
export OCTRA_SYNC_STAGE="$SYNC_DIR"
export OCTRA_CHAIN_ID="octra-devnet"

# Start Web Status Dashboard on port 8080 in background
echo "📊 Launching Web Dashboard on port 8080..."
python3 /opt/octra/dashboard/server.py &
DASHBOARD_PID=$!

# Handle graceful shutdown
trap 'echo "🛑 Stopping Octra Node..."; kill $DASHBOARD_PID $NODE_PID 2>/dev/null; exit 0' SIGTERM SIGINT

echo "🚀 Executing Octra Node binary in role: $NODE_ROLE..."

/opt/octra/bin/octra_node.exe &

NODE_PID=$!
wait $NODE_PID
