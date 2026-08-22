import http.server
import socketserver
import json
import urllib.request
import urllib.error
import os
import sys

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
DAEMON_RPC = "http://127.0.0.1:8081"

class OctraDashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            
            node_status = {
                "status": "online",
                "role": os.environ.get("NODE_ROLE", "observer"),
                "node_name": os.environ.get("NODE_NAME", "umbrel-octra-node"),
                "network": "Octra Devnet",
                "p2p_port": 9000,
                "consensus_port": 19000,
                "api_port": 8081,
                "data_dir": os.environ.get("OCTRA_DATA_DIR", "/var/lib/octra/devnet")
            }
            
            # Query local Octra daemon RPC
            try:
                with urllib.request.urlopen(f"{DAEMON_RPC}/", timeout=1) as resp:
                    daemon_data = json.loads(resp.read().decode("utf-8"))
                    node_status.update(daemon_data)
                    node_status["status"] = daemon_data.get("status", "running")
            except Exception as e:
                node_status["status"] = "connecting"
                node_status["error"] = str(e)

            self.wfile.write(json.dumps(node_status).encode("utf-8"))
            return

        super().do_GET()

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    with socketserver.TCPServer(("", PORT), OctraDashboardHandler) as httpd:
        print(f"Octra Dashboard Gateway running on http://0.0.0.0:{PORT}")
        httpd.serve_forever()
