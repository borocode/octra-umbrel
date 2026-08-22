import os
import sys

target_path = sys.argv[1] if len(sys.argv) > 1 else "main.cpp"

with open(target_path, "r", encoding="utf-8") as f:
    content = f.read()

target1 = "static bool is_loopback_host(std::string host, int port) {"
rep1 = """static bool is_loopback_host(std::string host, int port) {
    if (std::getenv("OCTRA_ALLOW_LAN")) return true;"""

target2 = "static bool is_allowed_webcli_origin(const std::string& origin, int port) {"
rep2 = """static bool is_allowed_webcli_origin(const std::string& origin, int port) {
    if (std::getenv("OCTRA_ALLOW_LAN")) return true;"""

if target1 in content:
    content = content.replace(target1, rep1)
if target2 in content:
    content = content.replace(target2, rep2)

with open(target_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully patched {target_path}")
