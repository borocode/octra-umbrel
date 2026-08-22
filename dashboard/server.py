import http.server
import socketserver
import json
import urllib.request
import urllib.error
import os
import sys

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
WALLET_BACKEND = "http://127.0.0.1:8420"
DAEMON_RPC = "http://127.0.0.1:8081"

class OctraDashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        self.send_header("Access-Control-Max-Age", "600")
        self.end_headers()

    def proxy_to_wallet(self, method):
        # Translate /wallet or /wallet/ to /
        target_path = self.path
        if target_path == "/wallet" or target_path == "/wallet/":
            target_path = "/"
        elif target_path.startswith("/wallet/"):
            target_path = target_path[7:]

        url = f"{WALLET_BACKEND}{target_path}"
        body = None
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            body = self.rfile.read(content_length)

        headers = {k: v for k, v in self.headers.items() if k.lower() not in ["host", "content-length"]}
        headers["Host"] = "127.0.0.1:8420"

        try:
            req = urllib.request.Request(url, data=body, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=30) as resp:
                self.send_response(resp.status)
                for k, v in resp.getheaders():
                    if k.lower() not in ["transfer-encoding", "content-length"]:
                        self.send_header(k, v)
                self.send_header("Access-Control-Allow-Origin", "*")
                content = resp.read()
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            for k, v in e.headers.items():
                if k.lower() not in ["transfer-encoding", "content-length"]:
                    self.send_header(k, v)
            self.send_header("Access-Control-Allow-Origin", "*")
            err_content = e.read()
            self.send_header("Content-Length", str(len(err_content)))
            self.end_headers()
            self.wfile.write(err_content)
        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": f"Wallet service offline: {e}"}).encode("utf-8"))

    def do_GET(self):
        if self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            node_status = {
                "status": "online",
                "role": os.environ.get("NODE_ROLE", "observer"),
                "node_name": os.environ.get("NODE_NAME", "umbrel-octra-node"),
                "network": "Octra Devnet",
                "p2p_port": 9000,
                "consensus_port": 19000,
                "api_port": 8081,
                "wallet_port": 8420,
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

        # Check if route should be forwarded to wallet backend
        wallet_routes = [
            "/api/", "/wallet", "/cipher", "/circles", "/swap", "/bridge",
            "/style.css", "/cipher.css", "/cipher.js", "/wallet.js",
            "/circles.js", "/swap.js", "/bridge.js", "/templates/",
            "/icons/", "/circle_asset_chunks.js", "/circle_bridge_policy.js",
            "/circle_public_prelude.js"
        ]
        
        if any(self.path.startswith(r) for r in wallet_routes):
            self.proxy_to_wallet("GET")
        else:
            super().do_GET()

    def do_POST(self):
        self.proxy_to_wallet("POST")

    def do_PUT(self):
        self.proxy_to_wallet("PUT")

    def do_DELETE(self):
        self.proxy_to_wallet("DELETE")

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    with socketserver.TCPServer(("", PORT), OctraDashboardHandler) as httpd:
        print(f"Octra Dashboard Gateway running on http://0.0.0.0:{PORT}")
        httpd.serve_forever()
