# 🧠 SentientMarket

**AI Reputation Oracle for Twin.fun Digital Twins** — powered by [OpenGradient](https://opengradient.ai)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FRumeyst%2Fsentientmarket)

SentientMarket tracks digital twins on [Twin.fun](https://twin.fun), builds persistent memory profiles using **MemSync**, scores their prediction accuracy against **on-chain forecast models**, and produces **TEE-verified reputation reports**. Every AI judgment comes with a cryptographic TEE signature — a tamper-proof proof that the analysis ran inside a secure enclave.

> **No private keys in this repo.** I use the OpenGradient SDK with server-side signing for x402 inference. Users connect their wallet via MetaMask to view proofs.

---

## 🏗️ Architecture

```
Twin.fun Data ─→ Memory Pipeline ─→ MemSync (persistent memory)
                       ↓
OG Workflow Models ─→ Forecast Comparator ─→ Accuracy Tracker
                       ↓
          TEE-Verified LLM (x402 via OG SDK)
                       ↓
        Reputation Score + TEE Cryptographic Proof
                       ↓
        Web Dashboard  ←──  MetaMask Wallet Connect
```

### Three OpenGradient Layers I Use

| Layer | Purpose | Integration |
|---|---|---|
| **MemSync** | Long-term memory for each twin's track record | REST API at `api.memchat.io` |
| **On-chain Models** | BTC/ETH/SOL/SUI price forecast workflows | OG SDK model reads |
| **x402 + TEE LLM** | Verifiable AI analysis with cryptographic proof | OG SDK `llm.chat()` with TEE attestation |

---

## 🚀 Quick Start

### Run Locally (Live TEE Proofs)

```bash
git clone https://github.com/Rumeyst/sentientmarket.git
cd sentientmarket
pip install -r requirements.txt

# Add your private key for live x402 inference
echo "OG_PRIVATE_KEY=0xYourKeyHere" > .env

python3.11 server.py
```

Open **http://localhost:8000** → click **🦊 Connect Wallet** → every twin gets a unique TEE-verified AI analysis.

### Deploy to Vercel (Demo Mode)

1. Push to GitHub
2. Import on [vercel.com/new](https://vercel.com/new)
3. Framework: **Other**
4. Deploy — Vercel handles the Python runtime automatically

> Vercel runs in demo mode by default. For live TEE proofs, run locally with `python3.11 server.py`.

---

## 🦊 Wallet Connect

Users connect directly in the browser:

- Click **Connect Wallet** → MetaMask prompts to add **Base Sepolia** (Chain 84532)
- Connected address displays in a banner with network status
- Auto-reconnects on page reload via `localStorage`
- Listens for `accountsChanged` and `chainChanged` events

Get OPG testnet tokens: **[faucet.opengradient.ai](https://faucet.opengradient.ai)**

---

## 📁 Project Structure

```
sentientmarket/
├── api/
│   └── index.py               # Vercel serverless entry point
├── static/
│   ├── index.html              # Leaderboard dashboard
│   ├── twin.html               # Twin detail page
│   ├── style.css               # Dual-theme (light/dark toggle)
│   └── app.js                  # ThemeManager + WalletManager
├── config.py                   # Environment config (keys optional)
├── og_client.py                # OG SDK wrapper (TEE LLM + forecasts)
├── memsync_client.py           # MemSync REST client (demo fallback)
├── twin_collector.py           # Twin.fun data collector (5 demo twins)
├── reputation_engine.py        # Core intelligence layer
├── server.py                   # FastAPI backend
├── vercel.json                 # Vercel deployment config
├── requirements.txt            # Python dependencies
├── .env.example                # Config template (all optional)
└── .gitignore                  # Clean repo for public push
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Leaderboard dashboard |
| `/twin/{id}` | GET | Twin detail page |
| `/api/leaderboard` | GET | Ranked reputation data (JSON) |
| `/api/twin/{id}` | GET | Full twin score + AI analysis |
| `/api/forecasts` | GET | OG on-chain price forecasts |
| `/api/network` | GET | OG chain config for MetaMask |
| `/api/health` | GET | System status check |

---

## 🔐 How Verification Works

```
1. Twin prediction data collected from Twin.fun
2. MemSync stores + searches memory profile
3. On-chain forecasts compared for accuracy scoring
4. TEE-verified LLM generates reputation analysis
   └─ GPT-4.1 runs inside a Trusted Execution Environment
   └─ Nobody — not even me — can tamper with the output
5. TEE signature returned → cryptographic proof of authentic AI analysis
```

Each twin's score includes a unique **TEE signature** — a cryptographic attestation proving the analysis was generated inside a tamper-proof secure enclave. The TEE ID identifies the hardware enclave, and each individual analysis has its own unique signature.

---

## 🎨 Design System

Custom dual-theme palette — toggle with ☀️/🌙:

| Token | Light Mode | Dark Mode |
|---|---|---|
| Primary (coral) | `#F24A72` | `#F24A72` |
| Secondary (navy) | `#333C83` | `#364E68` |
| Warm (orange) | `#FDAF75` | `#403121` |
| Highlight (yellow) | `#EAEA7F` | `#EAEA7F` |

Features: Outfit font, ambient gradient orbs, glassmorphism cards, responsive breakpoints (900/768/480px), `prefers-reduced-motion` support.

---

## 🔧 Optional Configuration

The dashboard works out-of-the-box in demo mode. For live TEE-verified inference:

| Variable | Purpose | Where to get |
|---|---|---|
| `OG_PRIVATE_KEY` | Server-side OG SDK x402 calls | Any ETH wallet (MetaMask export) |
| `MEMSYNC_API_KEY` | Live memory storage | [memsync.ai](https://memsync.ai) |
| `OPG` tokens | Payment for x402 LLM inference | [faucet.opengradient.ai](https://faucet.opengradient.ai) |

Set these in a local `.env` file, or in Vercel's project settings under **Environment Variables**.

---

## 📜 License

MIT
