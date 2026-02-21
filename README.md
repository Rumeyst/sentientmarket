# 🧠 SentientMarket

**AI Reputation Oracle for Twin.fun Digital Twins** — powered by [OpenGradient](https://opengradient.ai)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FRumeyst%2Fsentientmarket)

SentientMarket tracks digital twins on [Twin.fun](https://twin.fun), builds persistent memory profiles using **MemSync**, scores their prediction accuracy against **on-chain forecast models**, and produces **TEE-verified reputation reports**. Every AI judgment links to its cryptographic proof on the OpenGradient block explorer.

> **No private keys in this repo.** Users connect their wallet via MetaMask in the browser.

---

## 🏗️ Architecture

```
Twin.fun Data ─→ Memory Pipeline ─→ MemSync (persistent memory)
                       ↓
OG Workflow Models ─→ Forecast Comparator ─→ Accuracy Tracker
                       ↓
          TEE-Verified LLM (x402 Gateway)
                       ↓
             Reputation Score + On-Chain Proof
                       ↓
        Web Dashboard  ←──  MetaMask Wallet Connect
```

### Three OpenGradient Layers Used

| Layer | Purpose | Integration |
|---|---|---|
| **MemSync** | Long-term memory for each twin's track record | REST API at `api.memchat.io` |
| **On-chain Models** | BTC/ETH/SOL/SUI price forecast workflows | OG SDK model reads |
| **x402 + TEE LLM** | Verifiable AI analysis with on-chain proof | `SETTLE_INDIVIDUAL_WITH_METADATA` |

---

## 🚀 Quick Start

### Run Locally

```bash
git clone https://github.com/Rumeyst/sentientmarket.git
cd sentientmarket
pip install -r requirements.txt
python server.py
```

Open **http://localhost:8000** → click **🦊 Connect Wallet** → done.

### Deploy to Vercel

1. Push to GitHub
2. Import on [vercel.com/new](https://vercel.com/new)
3. Framework: **Other**
4. Deploy — Vercel handles the Python runtime automatically

> No environment variables needed for the demo. Add optional keys in Vercel's project settings if you want live OG features.

---

## 🦊 Wallet Connect

No `.env` private key needed — users connect directly in the browser:

- Click **Connect Wallet** → MetaMask prompts to add **OpenGradient** (Chain 10744)
- Connected address displays in a banner with network status
- Auto-reconnects on page reload via `localStorage`
- Listens for `accountsChanged` and `chainChanged` events

Get testnet tokens: **[faucet.opengradient.ai](https://faucet.opengradient.ai)**

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
1. Twin prediction data collected
2. MemSync stores + searches memory profile
3. On-chain forecasts compared for accuracy
4. TEE-verified LLM generates reputation analysis
   └─ Uses SETTLE_INDIVIDUAL_WITH_METADATA
   └─ Full prompt + response recorded on-chain
5. Proof hash returned → verifiable on block explorer
```

Every score links to its **cryptographic proof** on the [OpenGradient Block Explorer](https://explorer.opengradient.ai).

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

The dashboard works out-of-the-box in demo mode. For live OG features:

| Variable | Purpose | Where to get |
|---|---|---|
| `OG_PRIVATE_KEY` | Server-side OG SDK calls | Any ETH wallet (MetaMask export) |
| `MEMSYNC_API_KEY` | Live memory storage | [memsync.ai](https://memsync.ai) |
| `OUSDC` tokens | Payment for x402 LLM inference | [faucet.opengradient.ai](https://faucet.opengradient.ai) |

Set these in Vercel's project settings under **Environment Variables**, or in a local `.env` file.

---

## 📜 License

MIT
