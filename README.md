# ⚡ Octra Lite Node for Umbrel & Community App Store

[![Umbrel OS](https://img.shields.io/badge/Umbrel-Community%20App-00ff66?style=for-the-badge&logo=docker)](https://umbrel.com)
[![Architecture](https://img.shields.io/badge/Arch-amd64%20%7C%20arm64-blue?style=for-the-badge)](https://github.com/borocode/octra-umbrel)
[![License](https://img.shields.io/badge/License-MIT-black?style=for-the-badge)](LICENSE)

Run a sovereign, self-hosted **Octra Network Lite Node** directly on your **Umbrel server** (Raspberry Pi 4/5 or x86_64 Home Server). This repository serves as both a standalone **Umbrel Community App Store** and the source package ready for official submission to `getumbrel/umbrel-apps`.

---

## 🌟 Features

- **1-Click Umbrel Deployment:** Pre-configured Docker orchestration with persistent chain state at `/var/lib/octra`.
- **Integrated Web Status Dashboard:** Built-in dark/cyberpunk telemetry dashboard exposed on port `8080` (accessible via Umbrel reverse proxy).
- **Multi-Architecture Support:** Native multi-stage builds compiled for both `linux/amd64` (PC / Intel / AMD) and `linux/arm64` (Raspberry Pi 4/5).
- **Zero-Friction Sync:** Automatically bootstraps with the official Octra Devnet configuration.

---

## 📦 Umbrel App Store Installation

### Method 1: Add as a Community App Store (Instant 1-Click)

1. Open your **Umbrel Dashboard** (e.g. `http://umbrel.local`).
2. Navigate to **App Store** $\to$ Click the **Three Dots (⋮)** in the top right $\to$ **Community App Stores**.
3. Paste this repository URL:
   ```text
   https://github.com/borocode/octra-umbrel
   ```
4. Click **Add**. The **Octra Lite Node** will appear in your App Store ready to install!

---

### Method 2: Manual Local Installation via SSH

If you want to test the container directly on your Umbrel node before adding the store:

```bash
# 1. SSH into your Umbrel server
ssh umbrel@10.0.0.67

# 2. Navigate to your app-data directory
mkdir -p ~/umbrel/app-data/octra-node/data
cd ~/umbrel/app-data/octra-node

# 3. Clone this repository
git clone https://github.com/borocode/octra-umbrel.git temp
cp -r temp/octra-node/* .
rm -rf temp

# 4. Start the app via Docker Compose
docker compose up -d
```

---

## 🌐 Network & Port Allocations

| Port | Protocol | Purpose |
| :--- | :--- | :--- |
| **`8080`** | `HTTP` | Umbrel Web Status Dashboard & RPC Proxy |
| **`9000`** | `TCP/UDP` | Octra P2P Swarm Gossip |
| **`19000`** | `TCP` | Octra Consensus Network & State Sync |

---

## 🛠️ Upstream Submission to Official Umbrel App Store

To submit to the official [`getumbrel/umbrel-apps`](https://github.com/getumbrel/umbrel-apps) store:

1. Fork `getumbrel/umbrel-apps`.
2. Copy the `octra-node/` directory from this repository into the root of your fork.
3. Verify formatting with `npm test` or `npx prettier`.
4. Open a Pull Request: `feat: Add Octra Lite Node`.

---

## 📜 License

Packaged with ⚡ by [borocode](https://github.com/borocode).  
Octra Network core node is developed by [Octra Labs](https://github.com/octra-labs/lite_node).
