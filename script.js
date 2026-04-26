const API_URL = 'http://localhost:5000/api';

let allocChart = null;
let sentChart = null;

async function fetchDashboard() {
    try {
        const res = await fetch(`${API_URL}/dashboard`);
        const data = await res.json();
        renderDashboard(data);
    } catch (e) {
        console.error("Failed to fetch dashboard", e);
        document.getElementById('tableBody').innerHTML = '<tr><td colspan="7" style="text-align:center;color:red;">Error fetching data. Is backend running?</td></tr>';
    }
}

function renderDashboard(data) {
    // 1. Summary
    const formatter = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });
    document.getElementById('totalValue').textContent = formatter.format(data.total_value);
    
    const gainEl = document.getElementById('totalGain');
    gainEl.textContent = (data.total_gain_loss >= 0 ? '+' : '') + formatter.format(data.total_gain_loss) + ` (${data.total_gain_loss_pct.toFixed(2)}%)`;
    gainEl.style.color = data.total_gain_loss >= 0 ? 'var(--success)' : 'var(--danger)';

    // 2. Table
    const tbody = document.getElementById('tableBody');
    if (!data.holdings || data.holdings.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">No holdings yet.</td></tr>';
    } else {
        tbody.innerHTML = data.holdings.map(h => {
            let actionBadge = 'bg-hold';
            if (h.suggested_action.includes('BUY')) actionBadge = 'bg-buy';
            if (h.suggested_action.includes('SELL')) actionBadge = 'bg-sell';
            
            return `
            <tr>
                <td><strong>${h.symbol}</strong><br><small>${h.name}</small></td>
                <td>${h.shares} sh<br><small>Avg: $${h.avg_price.toFixed(2)} | Cur: $${h.current_price.toFixed(2)}</small></td>
                <td style="color: ${h.profit_loss_pct >= 0 ? 'var(--success)' : 'var(--danger)'}">
                    ${h.profit_loss_pct >= 0 ? '+' : ''}${h.profit_loss_pct.toFixed(2)}%
                </td>
                <td>${h.volatility.toFixed(2)}%<br><small>Thresh: ${h.volatility_threshold}%</small></td>
                <td>${h.sentiment_score.toFixed(2)}</td>
                <td>
                    <span class="badge ${actionBadge}">${h.suggested_action}</span><br>
                    <small style="color: var(--text-light); display:block; max-width: 250px; margin-top: 4px;">${h.action_reason}</small>
                </td>
                <td><button onclick="removeHolding('${h.symbol}')" style="background:var(--danger); padding:0.4rem;">Del</button></td>
            </tr>
            `;
        }).join('');
    }

    // 3. Charts
    renderCharts(data.holdings);
}

function renderCharts(holdings) {
    if (!holdings) return;
    
    // Allocation Chart (Pie)
    const allocCtx = document.getElementById('allocationChart').getContext('2d');
    const labels = holdings.map(h => h.symbol);
    const values = holdings.map(h => h.current_value);
    
    if (allocChart) allocChart.destroy();
    allocChart = new Chart(allocCtx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6']
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    // Sentiment vs Profit Chart (Scatter or Bar)
    const sentCtx = document.getElementById('sentimentChart').getContext('2d');
    
    if (sentChart) sentChart.destroy();
    sentChart = new Chart(sentCtx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Sentiment Score',
                    data: holdings.map(h => h.sentiment_score),
                    backgroundColor: holdings.map(h => h.sentiment_score > 0 ? 'rgba(16, 185, 129, 0.7)' : 'rgba(239, 68, 68, 0.7)'),
                    yAxisID: 'y'
                },
                {
                    label: 'P&L %',
                    data: holdings.map(h => h.profit_loss_pct),
                    type: 'line',
                    borderColor: '#4f46e5',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { type: 'linear', display: true, position: 'left', title: {display: true, text: 'Sentiment (-1 to 1)'}},
                y1: { type: 'linear', display: true, position: 'right', grid: {drawOnChartArea: false}, title: {display: true, text: 'P&L %'}}
            }
        }
    });
}

async function removeHolding(symbol) {
    if(!confirm(`Remove ${symbol}?`)) return;
    await fetch(`${API_URL}/portfolio/remove`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol })
    });
    fetchDashboard();
}

document.getElementById('addForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('button');
    btn.textContent = 'Saving...';
    btn.disabled = true;

    const payload = {
        symbol: document.getElementById('symbol').value,
        shares: document.getElementById('shares').value,
        avg_price: document.getElementById('avg_price').value,
        target_profit_pct: document.getElementById('target_profit').value || 15.0,
        volatility_threshold: document.getElementById('vol_threshold').value || 5.0,
        target_entry: document.getElementById('target_entry').value || null
    };

    try {
        await fetch(`${API_URL}/portfolio/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        e.target.reset();
        fetchDashboard();
    } finally {
        btn.textContent = 'Save Holding';
        btn.disabled = false;
    }
});

// Init
fetchDashboard();
setInterval(fetchDashboard, 30000); // Refresh every 30s
