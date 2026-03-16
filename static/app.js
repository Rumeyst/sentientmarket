/**
 * SentientMarket — Frontend Application
 * Leaderboard, twin detail, theme toggle, and MetaMask wallet connect.
 * No private keys needed — users connect their own wallet in-browser.
 */

// ── Theme Management ─────────────────────────────────────────

const ThemeManager = {
    STORAGE_KEY: 'sentientmarket-theme',

    init() {
        const saved = localStorage.getItem(this.STORAGE_KEY);
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const theme = saved || (prefersDark ? 'dark' : 'light');
        this.apply(theme);

        document.querySelectorAll('#theme-toggle').forEach(btn => {
            btn.addEventListener('click', () => this.toggle());
            btn.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); this.toggle(); }
            });
        });
    },

    apply(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(this.STORAGE_KEY, theme);
        document.querySelectorAll('#theme-toggle').forEach(btn => {
            btn.textContent = theme === 'dark' ? '🌙' : '☀️';
            btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
        });
    },

    toggle() {
        const current = document.documentElement.getAttribute('data-theme') || 'light';
        this.apply(current === 'dark' ? 'light' : 'dark');
    },
};

// ── Wallet Connect (MetaMask via ethers.js) ──────────────────

const WalletManager = {
    provider: null,
    signer: null,
    address: null,
    chainId: null,
    onConnectCallbacks: [],

    init() {
        // Bind connect buttons
        document.querySelectorAll('#connect-wallet').forEach(btn => {
            btn.addEventListener('click', () => this.connect());
        });

        // Bind disconnect buttons
        document.querySelectorAll('#disconnect-wallet').forEach(btn => {
            btn.addEventListener('click', () => this.disconnect());
        });

        // Auto-reconnect if wallet was previously connected
        if (window.ethereum && localStorage.getItem('sm-wallet-connected') === 'true') {
            this.connect(true);
        }

        // Listen for account/chain changes
        if (window.ethereum) {
            window.ethereum.on('accountsChanged', (accounts) => {
                if (accounts.length === 0) this.disconnect();
                else { this.address = accounts[0]; this.updateUI(); }
            });
            window.ethereum.on('chainChanged', () => window.location.reload());
        }
    },

    async connect(silent = false) {
        if (!window.ethereum) {
            if (!silent) alert('No wallet detected. Please install MetaMask or Rabby to connect.');
            return;
        }

        try {
            this.provider = new ethers.BrowserProvider(window.ethereum);
            const accounts = await this.provider.send('eth_requestAccounts', []);
            this.signer = await this.provider.getSigner();
            this.address = accounts[0];

            const network = await this.provider.getNetwork();
            this.chainId = Number(network.chainId);

            localStorage.setItem('sm-wallet-connected', 'true');
            this.updateUI();

            // Fire connect callbacks (e.g. re-render proof button)
            this.onConnectCallbacks.forEach(cb => cb(this.address));

            // Prompt to switch to Base Sepolia if not already on it
            if (this.chainId !== 84532) {
                await this.switchToBaseSepolia();
            }
        } catch (err) {
            if (!silent) console.error('Wallet connect failed:', err);
        }
    },

    async switchToBaseSepolia() {
        const BASE_SEPOLIA_HEX = '0x14a34'; // 84532
        try {
            await window.ethereum.request({
                method: 'wallet_switchEthereumChain',
                params: [{ chainId: BASE_SEPOLIA_HEX }],
            });
        } catch (switchErr) {
            if (switchErr.code === 4902) {
                await window.ethereum.request({
                    method: 'wallet_addEthereumChain',
                    params: [{
                        chainId: BASE_SEPOLIA_HEX,
                        chainName: 'Base Sepolia',
                        rpcUrls: ['https://sepolia.base.org'],
                        blockExplorerUrls: ['https://sepolia.basescan.org'],
                        nativeCurrency: { name: 'ETH', symbol: 'ETH', decimals: 18 },
                    }],
                });
            }
        }
        try {
            const network = await this.provider.getNetwork();
            this.chainId = Number(network.chainId);
            this.updateUI();
        } catch (err) {
            console.warn('Network switch failed:', err);
        }
    },

    disconnect() {
        this.provider = null;
        this.signer = null;
        this.address = null;
        this.chainId = null;
        localStorage.removeItem('sm-wallet-connected');
        this.updateUI();
    },

    updateUI() {
        const connected = !!this.address;
        const truncAddr = connected
            ? this.address.slice(0, 6) + '···' + this.address.slice(-4)
            : '';
        const networkName = this.chainId === 84532 ? 'Base Sepolia' : `Chain ${this.chainId || '?'}`;

        // Update connect buttons
        document.querySelectorAll('#connect-wallet').forEach(btn => {
            if (connected) {
                btn.classList.add('connected');
                btn.querySelector('.wallet-icon').textContent = '✓';
                btn.querySelector('.wallet-label').textContent = truncAddr;
            } else {
                btn.classList.remove('connected');
                btn.querySelector('.wallet-icon').textContent = '🦊';
                btn.querySelector('.wallet-label').textContent = btn.classList.contains('btn-wallet-sm') ? 'Connect' : 'Connect Wallet';
            }
        });

        // Update banners
        document.querySelectorAll('#wallet-banner').forEach(banner => {
            banner.style.display = connected ? 'flex' : 'none';
        });

        document.querySelectorAll('#wallet-address').forEach(el => {
            el.textContent = truncAddr;
        });

        document.querySelectorAll('#wallet-network').forEach(el => {
            el.textContent = connected ? networkName : '';
            el.style.color = this.chainId === 84532 ? '' : 'var(--yellow)';
        });
    },
};

// ── Utilities ────────────────────────────────────────────────

const getAccuracyClass = (pct) =>
    pct >= 65 ? 'accuracy-high' : pct >= 50 ? 'accuracy-mid' : 'accuracy-low';

const getBarColor = (pct) =>
    pct >= 65 ? 'green' : pct >= 50 ? 'yellow' : 'red';

const getBiasClass = (bias) => `bias-${bias || 'neutral'}`;
const getRiskClass = (risk) => `risk-${risk || 'medium'}`;

const getRankClass = (rank) => {
    if (rank === 1) return 'gold';
    if (rank === 2) return 'silver';
    if (rank === 3) return 'bronze';
    return '';
};

const truncateHash = (hash) => {
    if (!hash || hash.length < 16) return hash || '—';
    return hash.slice(0, 8) + '···' + hash.slice(-6);
};

const timeAgo = (ts) => {
    const s = Math.floor(Date.now() / 1000) - ts;
    if (s < 60) return 'just now';
    if (s < 3600) return Math.floor(s / 60) + 'm ago';
    if (s < 86400) return Math.floor(s / 3600) + 'h ago';
    return Math.floor(s / 86400) + 'd ago';
};

const fmtPrice = (p) => {
    if (p >= 1000) return '$' + p.toLocaleString('en-US', { maximumFractionDigits: 0 });
    if (p >= 1) return '$' + p.toFixed(2);
    return '$' + p.toFixed(4);
};

// ── Leaderboard ──────────────────────────────────────────────

const loadLeaderboard = async () => {
    const container = document.getElementById('leaderboard-container');
    if (!container) return;

    try {
        const res = await fetch('/api/leaderboard');
        const data = await res.json();

        if (!data || !data.length) {
            container.innerHTML = '<div class="loading"><div class="loading-text">No twins tracked yet.</div></div>';
            return;
        }

        const totalCalls = data.reduce((s, t) => s + t.total_calls, 0);
        const avgAcc = (data.reduce((s, t) => s + t.accuracy_pct, 0) / data.length).toFixed(1);

        document.getElementById('stat-twins').textContent = data.length;
        document.getElementById('stat-accuracy').textContent = avgAcc + '%';
        document.getElementById('stat-predictions').textContent = totalCalls;
        document.getElementById('stat-proofs').textContent = data.filter(t => t.payment_hash).length;
        document.getElementById('badge-status').textContent = '⚡ ' + data.length + ' Scored';

        let html = `<div class="leaderboard animate-in">
            <div class="leaderboard-header" role="row">
                <div role="columnheader">#</div>
                <div role="columnheader">Twin</div>
                <div role="columnheader">Accuracy</div>
                <div role="columnheader">Record</div>
                <div role="columnheader">Bias</div>
                <div role="columnheader">Risk</div>
                <div role="columnheader"></div>
            </div>`;

        data.forEach((t, i) => {
            const rank = i + 1;
            html += `
            <div class="twin-row" role="row" onclick="window.location.href='/twin/${t.twin_id}'"
                 tabindex="0" aria-label="View ${t.name} profile"
                 onkeydown="if(event.key==='Enter')window.location.href='/twin/${t.twin_id}'">
                <div class="twin-rank ${getRankClass(rank)}" role="cell">${rank}</div>
                <div class="twin-identity" role="cell">
                    <div class="twin-avatar" aria-hidden="true">${t.avatar || '🤖'}</div>
                    <div>
                        <div class="twin-name">${t.name}</div>
                        <div class="twin-bio">${t.bio || ''}</div>
                    </div>
                </div>
                <div class="twin-accuracy ${getAccuracyClass(t.accuracy_pct)}" role="cell">${t.accuracy_pct}%</div>
                <div class="twin-record" role="cell">${t.hits}W / ${t.misses}L</div>
                <div class="twin-bias ${getBiasClass(t.bias)}" role="cell">${t.bias || '—'}</div>
                <div class="twin-risk ${getRiskClass(t.risk_rating)}" role="cell">${t.risk_rating || '—'}</div>
                <div class="twin-action" role="cell">
                    <a href="/twin/${t.twin_id}" class="btn-view" aria-label="View ${t.name}">View →</a>
                </div>
            </div>`;
        });

        html += '</div>';
        container.innerHTML = html;

    } catch (err) {
        console.error('Leaderboard error:', err);
        container.innerHTML = '<div class="loading"><div class="loading-text">Failed to load. Is the server running?</div></div>';
    }
};

// ── Twin Detail ──────────────────────────────────────────────

const loadTwinDetail = async () => {
    const loadEl = document.getElementById('twin-loading');
    const contentEl = document.getElementById('twin-content');
    if (!loadEl || !contentEl) return;

    const twinId = window.location.pathname.split('/').pop();
    if (!twinId) { loadEl.innerHTML = '<div class="loading-text">Invalid twin ID</div>'; return; }

    try {
        const res = await fetch(`/api/twin/${twinId}`);
        if (!res.ok) throw new Error('Not found');
        const data = await res.json();

        const { twin, accuracy, ai_analysis: analysis } = data;

        document.getElementById('twin-avatar').textContent = twin.avatar || '🤖';
        document.getElementById('twin-name').textContent = twin.name;
        document.getElementById('twin-bio').textContent = twin.bio || 'No bio.';
        document.title = `${twin.name} — SentientMarket`;

        document.getElementById('detail-accuracy').textContent = accuracy.accuracy_pct + '%';
        document.getElementById('detail-record').textContent = `${accuracy.hits}W / ${accuracy.misses}L`;

        const biasEl = document.getElementById('detail-bias');
        biasEl.textContent = analysis.bias || '—';
        biasEl.style.color = analysis.bias === 'bullish' ? 'var(--green)' : analysis.bias === 'bearish' ? 'var(--red)' : '';

        const riskEl = document.getElementById('detail-risk');
        riskEl.textContent = analysis.risk_rating || '—';
        riskEl.style.color = analysis.risk_rating === 'low' ? 'var(--green)' : analysis.risk_rating === 'high' ? 'var(--red)' : 'var(--yellow)';

        document.getElementById('detail-narrative').textContent = analysis.narrative || 'No analysis available.';

        const strengthsEl = document.getElementById('detail-strengths');
        if (analysis.strengths?.length) {
            strengthsEl.innerHTML = `<div style="font-size:0.7rem;font-weight:700;color:var(--green);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">Strengths</div>
                <div class="chip-list">${analysis.strengths.map(s => `<span class="chip chip-green">✓ ${s}</span>`).join('')}</div>`;
        }

        const weakEl = document.getElementById('detail-weaknesses');
        if (analysis.weaknesses?.length) {
            weakEl.innerHTML = `<div style="font-size:0.7rem;font-weight:700;color:var(--red);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">Weaknesses</div>
                <div class="chip-list">${analysis.weaknesses.map(w => `<span class="chip chip-red">✗ ${w}</span>`).join('')}</div>`;
        }

        const proofEl = document.getElementById('proof-link');
        if (data.explorer_url && data.explorer_url.startsWith('https://')) {
            // On-chain tx — link to explorer
            proofEl.href = data.explorer_url;
            proofEl.textContent = '🔗 Verify: ' + truncateHash(data.payment_hash) + ' →';
            proofEl.style.cursor = 'pointer';
            proofEl.style.opacity = '1';
        } else if (data.payment_hash && !data.payment_hash.startsWith('0xDEMO_') && !data.payment_hash.startsWith('0xTEE_')) {
            // TEE verified proof (no explorer link but real proof)
            proofEl.removeAttribute('href');
            proofEl.textContent = '✅ TEE Verified — proof: ' + truncateHash(data.payment_hash);
            proofEl.style.cursor = 'default';
            proofEl.style.opacity = '1';
            proofEl.style.color = 'var(--green)';
        } else {
            proofEl.textContent = '🔒 Demo mode — set OG_PRIVATE_KEY for live proofs';
            proofEl.removeAttribute('href');
            proofEl.style.cursor = 'default';
            proofEl.style.opacity = '0.6';
        }

        const barsEl = document.getElementById('accuracy-bars');
        let barsHtml = buildBar('Overall', accuracy.accuracy_pct, accuracy.total);
        if (accuracy.by_asset) {
            Object.entries(accuracy.by_asset).forEach(([k, v]) => { barsHtml += buildBar(k, v.accuracy_pct, v.total); });
        }
        if (accuracy.by_direction) {
            Object.entries(accuracy.by_direction).forEach(([k, v]) => {
                if (v.total > 0) barsHtml += buildBar(k.charAt(0).toUpperCase() + k.slice(1), v.accuracy_pct, v.total);
            });
        }
        barsEl.innerHTML = barsHtml;

        const predEl = document.getElementById('prediction-list');
        if (twin.predictions?.length) {
            const sorted = [...twin.predictions].sort((a, b) => b.timestamp - a.timestamp);
            predEl.innerHTML = sorted.map(p => {
                const icon = p.outcome === 'hit' ? '✓' : p.outcome === 'miss' ? '✗' : '⏳';
                const cls = p.outcome || 'pending';
                const dir = p.direction === 'long' ? '↗ Long' : '↘ Short';
                const result = p.outcome === 'hit'
                    ? `Hit — reached ${fmtPrice(p.actual_price)}`
                    : p.outcome === 'miss'
                        ? `Missed — went to ${fmtPrice(p.actual_price)}`
                        : 'Pending...';
                return `<div class="prediction-item" role="listitem">
                    <div class="prediction-icon ${cls}" aria-hidden="true">${icon}</div>
                    <div class="prediction-details">
                        <div class="prediction-call">${p.asset} ${dir} at ${fmtPrice(p.price_at_call)} → ${fmtPrice(p.target)}</div>
                        <div class="prediction-result">${result} · ${timeAgo(p.timestamp)}</div>
                    </div>
                </div>`;
            }).join('');
        } else {
            predEl.innerHTML = '<div class="loading-text" style="padding:20px;">No predictions yet.</div>';
        }

        loadEl.style.display = 'none';
        contentEl.style.display = 'block';

    } catch (err) {
        console.error('Twin detail error:', err);
        loadEl.innerHTML = '<div class="loading-text">Twin not found.</div>';
    }
};

const buildBar = (label, pct, total) => `
    <div class="accuracy-bar-container">
        <div class="accuracy-bar-label">
            <span>${label}</span>
            <span>${pct}% (${total})</span>
        </div>
        <div class="accuracy-bar">
            <div class="accuracy-bar-fill ${getBarColor(pct)}" style="width: ${pct}%"></div>
        </div>
    </div>`;

// ── Init ─────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
    WalletManager.init();

    const path = window.location.pathname;
    if (path === '/' || path === '/index.html') loadLeaderboard();
    else if (path.startsWith('/twin/')) loadTwinDetail();
});
