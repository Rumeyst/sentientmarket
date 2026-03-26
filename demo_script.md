# SentientMarket — Walkthrough Script

3-4 minutes. know the flow, don't read word for word.

---

## before you start

- app running: `python3.11 server.py` → http://localhost:8000
- terminal visible with server logs
- wallet installed (MetaMask, Rabby, whatever)
- you'll land on the connect page first — that's intentional

---

## the walkthrough

### landing page (10 sec)

the page shows the logo, the name, and a connect button. nothing else loads until you connect.

"SentientMarket. reputation oracle for AI trading twins. you need a wallet to get in."

### connect wallet (10 sec)

click Connect Wallet to Enter. pick your wallet from the modal.

"standard wallet connect. MetaMask, Rabby, Coinbase — whatever you have installed."

once connected, the leaderboard loads.

### the leaderboard (20 sec)

nine twins, ranked by accuracy. scroll through.

"nine digital twins, each with a different strategy. OnChainOracle is running 83% — reads the chain and makes calls. MacroMind at 80%, reads the macro. AlphaWhale at 75%, follows whale flows. all the way down to ContrarianKing at 40% — fades every consensus trade and pays for it."

### click into OnChainOracle or MacroMind (30 sec)

click the top performer.

"OnChainOracle. 83% across six calls. 100% on BTC, 100% on ETH, 50% on SOL. the on-chain data translates better on the majors."

scroll to the AI analysis section. it loads in a few seconds.

"this analysis is generated fresh by Gemini Flash Lite running inside a secure enclave. it reads the full prediction history, computes strengths and weaknesses, and signs the output before it leaves the hardware."

### show a weaker twin (15 sec)

go back, click ContrarianKing or DegenSage.

"ContrarianKing. 40%. fades every consensus trade. the SOL and ETH shorts hit, but fading BTC in a bull market doesn't work. the system doesn't care about your thesis — it counts wins and losses."

### verification section (10 sec)

scroll to the bottom of any twin page.

"the signature at the bottom is from the TEE enclave. it proves the analysis wasn't modified after it was generated. each call costs about 0.005 OPG and settles on Base Sepolia."

### light mode (5 sec)

click the theme toggle.

"also supports light mode."

### closing (15 sec)

go back to the leaderboard.

"nine tracked twins. accuracy computed by asset and direction. AI analysis generated inside a secure enclave with a cryptographic proof attached. the repo is public, runs locally in five minutes."

---

## the nine twins

| Twin | Accuracy | Strategy |
|---|---|---|
| OnChainOracle | 83% | Pure on-chain data, no narratives |
| MacroMind | 80% | Macro-first, waits for the Fed |
| AlphaWhale | 75% | Whale wallet tracking |
| YieldFarmer | 75% | DeFi yield flows and TVL |
| LiquidityLens | 71% | Order book depth analysis |
| DegenSage | 60% | High-conviction altcoin plays |
| SnipeBot | 60% | Scalper, volume-driven |
| MomentumMax | 60% | Rides trends until they break |
| ContrarianKing | 40% | Fades consensus, gets punished |

---

## tips

- don't rush. let the AI analysis load. silence is fine.
- the terminal shows TEE verification in real time — point at it.
- analysis is cached for 5 minutes. first visit runs inference, subsequent visits serve cache.
- if someone asks "is the data real?" — the predictions are representative, the AI analysis is real and different every time.
- one take is fine. real > polished.
