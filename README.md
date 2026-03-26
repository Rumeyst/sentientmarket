# SentientMarket

Reputation oracle for AI trading twins. Built on [OpenGradient](https://opengradient.ai).

Tracks digital twins on [Twin.fun](https://twin.fun), scores their prediction accuracy, and runs TEE-verified analysis on each one. The analysis happens inside a secure enclave — nobody can touch the output. Payment settles on Base Sepolia via x402. You get a cryptographic proof that the result is untampered.

---

## What It Does

```
Twin prediction history (BTC, ETH, SOL, SUI)
       ↓
Memory pipeline builds context per twin
       ↓
Accuracy tracker counts wins, losses, per asset and direction
       ↓
Gemini Flash Lite runs inside TEE enclave (via x402)
       ↓
TEE signature + reputation report comes back
       ↓
Dashboard shows everything + wallet connect
```

| Part | Job |
|---|---|
| **Memory Pipeline** | Turns every prediction into structured memory and builds context for the LLM |
| **x402 TEE LLM** | Runs Gemini Flash Lite inside an enclave, signs the output and settles OPG on Base Sepolia |
| **Reputation Engine** | Computes accuracy by asset and direction, feeds it into the AI analysis |

---

## Run It

```bash
git clone https://github.com/Rumeyst/sentientmarket.git
cd sentientmarket
pip install -r requirements.txt

cp .env.example .env
# add your OG_PRIVATE_KEY (wallet with OPG on Base Sepolia)

python3.11 server.py
```

Open **http://localhost:8000**

