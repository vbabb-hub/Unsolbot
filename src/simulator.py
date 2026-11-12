import json
import os
from datetime import datetime
from bot_logic import get_sol_market_data, analyze_market

PORTFOLIO_FILE = "src/portfolio.json"
README_FILE = "README.md"
HTML_FILE = "index.html"

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)
    return {
        "cash": 30.00, 
        "initial_capital": 30.00, 
        "positions": [],
        "prev_rsi": None
    }

def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=4)

def format_pct_badge(val):
    color = "text-emerald-400 bg-emerald-500/10 border-emerald-500/20" if val >= 0 else "text-rose-400 bg-rose-500/10 border-rose-500/20"
    return f'<span class="px-2 py-1 rounded-md text-xs font-mono font-semibold border {color}">{val:+.2f}%</span>'

def update_dashboards(timestamp, price, changes, sma, rsi, signal, portfolio, total_value, pnl, action_msg):
    invested_capital = sum(p['cost'] for p in portfolio['positions'])
    total_sol = sum(p['amount'] for p in portfolio['positions'])
    
    exposure_pct = (invested_capital / total_value * 100) if total_value > 0 else 0.0
    num_pos = len(portfolio['positions'])
    pnl_pct = (pnl / portfolio['initial_capital']) * 100

    # --- 1. GENERAZIONE INDEX.HTML ---
    pos_rows_html = ""
    if num_pos > 0:
        for i, pos in enumerate(portfolio['positions'], 1):
            pos_pnl_pct = ((price - pos['entry']) / pos['entry']) * 100
            pos_color = "text-emerald-400" if pos_pnl_pct >= 0 else "text-rose-400"
            pos_rows_html += f"""
            <tr class="border-b border-slate-800 hover:bg-slate-800/40 transition">
                <td class="py-3 px-3 font-medium text-slate-200">#{i}</td>
                <td class="py-3 px-3 font-mono text-slate-300">{pos['amount']:.4f} SOL <span class="text-xs text-slate-500">(${pos['cost']:.2f})</span></td>
                <td class="py-3 px-3 font-mono text-slate-300">${pos['entry']:.2f}</td>
                <td class="py-3 px-3 font-mono text-amber-400 font-semibold">${pos['tp']:.2f}</td>
                <td class="py-3 px-3 font-mono {pos_color} text-right">{pos_pnl_pct:+.2f}%</td>
            </tr>"""
    else:
        pos_rows_html = """
        <tr>
            <td colspan="5" class="py-8 text-center text-slate-500 italic">Nessuna posizione attiva. In attesa di segnale di rimbalzo (SMA + RSI).</td>
        </tr>"""

    pnl_text_color = "text-emerald-400" if pnl >= 0 else "text-rose-400"
    signal_badge = "bg-emerald-500/20 text-emerald-300 border-emerald-500/30" if "BUY" in signal else "bg-slate-700/50 text-slate-300 border-slate-600"

    html_content = f"""<!DOCTYPE html>
<html lang="it" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="300">
    <title>Unsolbot | Solana Algorithmic Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-200 font-sans antialiased min-h-screen p-4 md:p-8">
    <div class="max-w-6xl mx-auto space-y-6">
        
        <!-- HEADER -->
        <header class="flex flex-col md:flex-row md:items-center justify-between bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
            <div class="flex items-center space-x-3">
                <div class="h-10 w-10 rounded-xl bg-gradient-to-tr from-purple-600 to-emerald-400 flex items-center justify-center text-slate-950 font-bold text-xl">S</div>
                <div>
                    <h1 class="text-xl md:text-2xl font-bold text-white tracking-tight">Unsolbot <span class="text-xs font-normal uppercase tracking-wider px-2 py-0.5 ml-2 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">Paper Trading</span></h1>
                    <p class="text-xs text-slate-400 mt-0.5">Strategia Combinata (SMA 20 + RSI Rebound > 35) • Max Cap 80% • No Stop-Loss</p>
                </div>
            </div>
            <div class="mt-4 md:mt-0 text-left md:text-right">
                <div class="text-2xl font-mono font-bold text-white">${price:.2f} <span class="text-xs font-sans font-normal text-slate-400">SOL/USD</span></div>
                <div class="text-xs text-slate-500 font-mono">Aggiornato: {timestamp} UTC</div>
            </div>
        </header>

        <!-- GRIGLIA 4 QUADRANTI -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            <!-- 1. PORTAFOGLIO & CAPITALE -->
            <section class="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between shadow-lg">
                <div>
                    <div class="flex items-center justify-between mb-4">
                        <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-400">1. Portafoglio & Capitale</h2>
                        <span class="text-xs font-mono px-2.5 py-1 rounded-full bg-slate-800 text-slate-300">Esposizione: {exposure_pct:.0f}% / 80%</span>
                    </div>
                    <div class="grid grid-cols-2 gap-4 my-2">
                        <div class="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
                            <div class="text-xs text-slate-400">Valore Totale (Corrente)</div>
                            <div class="text-2xl font-mono font-bold text-white mt-1">${total_value:.2f}</div>
                            <div class="text-xs text-slate-500 mt-1">Iniziale: ${portfolio['initial_capital']:.2f}</div>
                        </div>
                        <div class="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
                            <div class="text-xs text-slate-400">Profitto / Perdita (P&L)</div>
                            <div class="text-2xl font-mono font-bold {pnl_text_color} mt-1">${pnl:+.2f}</div>
                            <div class="text-xs font-mono {pnl_text_color} mt-1">{pnl_pct:+.2f}%</div>
                        </div>
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-4 pt-4 border-t border-slate-800/80 text-sm">
                    <div>
                        <span class="text-slate-400 block text-xs">Liquidità Residua (Cash)</span>
                        <span class="font-mono font-semibold text-slate-200">${portfolio['cash']:.2f}</span>
                    </div>
                    <div>
                        <span class="text-slate-400 block text-xs">Solana Detenuti</span>
                        <span class="font-mono font-semibold text-purple-300">{total_sol:.4f} SOL</span>
                    </div>
                </div>
            </section>

            <!-- 2. TREND SOLANA -->
            <section class="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between shadow-lg">
                <div>
                    <div class="flex items-center justify-between mb-4">
                        <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-400">2. Andamento Solana (Timeframe)</h2>
                        <span class="text-xs font-mono text-slate-400">ATH: <strong class="text-slate-200">${changes['ath']:.2f}</strong></span>
                    </div>
                    <div class="grid grid-cols-3 sm:grid-cols-5 gap-3 my-4">
                        <div class="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 text-center">
                            <div class="text-xs text-slate-400 mb-2">1 Ora</div>
                            {format_pct_badge(changes['1h'])}
                        </div>
                        <div class="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 text-center">
                            <div class="text-xs text-slate-400 mb-2">24 Ore</div>
                            {format_pct_badge(changes['1d'])}
                        </div>
                        <div class="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 text-center">
                            <div class="text-xs text-slate-400 mb-2">7 Giorni</div>
                            {format_pct_badge(changes['1w'])}
                        </div>
                        <div class="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 text-center">
                            <div class="text-xs text-slate-400 mb-2">30 Giorni</div>
                            {format_pct_badge(changes['1m'])}
                        </div>
                        <div class="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 text-center col-span-3 sm:col-span-1">
                            <div class="text-xs text-slate-400 mb-2">1 Anno</div>
                            {format_pct_badge(changes['1y'])}
                        </div>
                    </div>
                </div>
                <div class="pt-4 border-t border-slate-800/80 flex justify-between items-center text-xs text-slate-400">
                    <span>Distanza dall'ATH: <strong class="font-mono text-slate-300">{((price - changes['ath'])/changes['ath'])*100:.1f}%</strong></span>
                    <span>Fonte: CoinGecko / CoinCap</span>
                </div>
            </section>

            <!-- 3. POSIZIONI APERTE -->
            <section class="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 shadow-lg">
                <div class="flex items-center justify-between mb-4">
                    <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-400">3. Posizioni Aperte ({num_pos} Tranches)</h2>
                    <span class="text-xs px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20">TP +5% • No Stop-Loss</span>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-sm">
                        <thead>
                            <tr class="border-b border-slate-800 text-xs uppercase text-slate-500">
                                <th class="py-2 px-3">Slot</th>
                                <th class="py-2 px-3">Quantità / Investito</th>
                                <th class="py-2 px-3">Ingresso</th>
                                <th class="py-2 px-3">Target TP</th>
                                <th class="py-2 px-3 text-right">Stato</th>
                            </tr>
                        </thead>
                        <tbody>
                            {pos_rows_html}
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- 4. DIAGNOSTICA TECNICA -->
            <section class="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between shadow-lg">
                <div>
                    <div class="flex items-center justify-between mb-4">
                        <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-400">4. Diagnostica & Motore</h2>
                        <span class="text-xs px-2.5 py-1 rounded-md border font-mono {signal_badge}">{signal}</span>
                    </div>
                    <div class="grid grid-cols-2 gap-4 mb-4">
                        <div class="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800/80 flex justify-between items-center">
                            <span class="text-xs text-slate-400">SMA (20)</span>
                            <span class="font-mono font-semibold text-slate-200">${sma:.2f}</span>
                        </div>
                        <div class="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800/80 flex justify-between items-center">
                            <span class="text-xs text-slate-400">RSI (14)</span>
                            <span class="font-mono font-semibold text-slate-200">{rsi:.1f}</span>
                        </div>
                    </div>
                </div>
                <div class="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 text-xs font-mono text-slate-300">
                    <span class="text-slate-500 block mb-1 uppercase font-sans text-[10px] tracking-wider">Ultimo Evento Registrato:</span>
                    {action_msg}
                </div>
            </section>

        </div>
    </div>
</body>
</html>"""

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    # --- 2. GENERAZIONE README.MD ---
    md_positions = ""
    if num_pos > 0:
        for i, pos in enumerate(portfolio['positions'], 1):
            md_positions += f"| Tranche #{i} | {pos['amount']:.4f} SOL (${pos['cost']:.2f}) | ${pos['entry']:.2f} | ${pos['tp']:.2f} (+5%) |\n"
    else:
        md_positions = "| Nessuna posizione attiva | --- | --- | --- |\n"

    readme_content = f"""# 🤖 Unsolbot - Solana Paper Trading ($30)

🌐 **Dashboard Web Live:** [https://vbabb-hub.github.io/Unsolbot/](https://vbabb-hub.github.io/Unsolbot/)  
*Ultimo aggiornamento:* `{timestamp} UTC`

---

### 📦 1. Portafoglio & Capitale

| Metrica | Valore |
| :--- | :--- |
| **Capitale Iniziale** | `$30.00` |
| **Cash Disponibile** | `${portfolio['cash']:.2f}` |
| **Asset in SOL** | `{total_sol:.4f} SOL` |
| **Valore Totale** | **${total_value:.2f}** |
| **Performance (P&L)** | **${pnl:+.2f}** ({pnl_pct:+.2f}%) |

---

### 📊 2. Trend Solana (`${price:.2f}`)

| 1h | 1d | 1w | 1m | 1y | ATH |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `{changes['1h']:+.2f}%` | `{changes['1d']:+.2f}%` | `{changes['1w']:+.2f}%` | `{changes['1m']:+.2f}%` | `{changes['1y']:+.2f}%` | **`${changes['ath']:.2f}`** |

---

### 🎯 3. Posizioni Aperte ({num_pos} Tranches - No Stop-Loss)

| Tranche | Quantità / Investito | Ingresso | Target TP (+5%) |
| :--- | :--- | :--- | :--- |
{md_positions}
---

### ⚙️ 4. Diagnostica & Ultima Azione

| Parametro | Valore |
| :--- | :--- |
| **SMA (20)** | `${sma:.2f}` |
| **RSI (14)** | `{rsi:.1f}` |
| **Segnale** | `{signal}` |
| **Evento** | `{action_msg}` |
"""
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(readme_content)

def run_paper_trade():
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] === Avvio Ciclo Bot Trading (SMA + RSI Rebound) ===")
    
    price, changes = get_sol_market_data()
    if not price:
        print("Impossibile recuperare il prezzo di Solana.")
        return

    portfolio = load_portfolio()
    signal, sma, rsi = analyze_market()
    
    prev_rsi = portfolio.get("prev_rsi", None)
    action_logs = []

    total_sol_held = sum(p['amount'] for p in portfolio['positions'])
    total_value = portfolio["cash"] + (total_sol_held * price)

    # 1. CONTROLLO TAKE PROFIT INDIPENDENTE
    remaining_positions = []
    freed_cash = 0.0

    for pos in portfolio['positions']:
        if price >= pos['tp']:
            sale_value = pos['amount'] * price
            freed_cash += sale_value
            action_logs.append(f"🎯 TP raggiunto! Venduti {pos['amount']:.4f} SOL a ${price:.2f} per ${sale_value:.2f}")
        else:
            remaining_positions.append(pos)

    portfolio['positions'] = remaining_positions
    portfolio['cash'] += freed_cash

    total_sol_held = sum(p['amount'] for p in portfolio['positions'])
    total_value = portfolio["cash"] + (total_sol_held * price)

    # 2. LOGICA COMBINATA: TREND SMA 20 + RSI REBOUND (> 35)
    max_investment_allowed = total_value * 0.80
    current_invested = sum(p['cost'] for p in portfolio['positions'])
    amount_per_tranche = total_value * 0.20

    # Filtro Trend: Il prezzo deve essere sopra la SMA 20
    trend_ok = price > sma

    # Trigger RSI: L'RSI era sotto 35 ed è risalito sopra 35 (oppure primo avvio sotto 35)
    if prev_rsi is None:
        rsi_trigger = (rsi < 35)  # Al primo avvio se è già in ipervenduto
    else:
        rsi_trigger = (prev_rsi < 35 and rsi >= 35)

    should_buy = trend_ok and rsi_trigger

    if should_buy:
        if current_invested < max_investment_allowed and portfolio["cash"] >= amount_per_tranche:
            sol_bought = amount_per_tranche / price
            new_position = {
                "amount": sol_bought,
                "cost": amount_per_tranche,
                "entry": price,
                "tp": price * 1.05
            }
            portfolio['positions'].append(new_position)
            portfolio["cash"] -= amount_per_tranche
            
            msg = f"🛒 BUY (SMA + RSI Rebound): Acquistati {sol_bought:.4f} SOL (${amount_per_tranche:.2f}) a ${price:.2f}. TP a ${new_position['tp']:.2f}"
            action_logs.append(msg)
            print(f">>> [ACQUISTO STRATEGICO] {msg}")
        else:
            msg = "Segnale di rimbalzo valido, ma cap 80% raggiunto o cash insufficiente."
            if not action_logs: action_logs.append(msg)
    else:
        if not action_logs:
            action_logs.append(f"In attesa (posizioni attive: {len(portfolio['positions'])}). Trend OK: {trend_ok}, RSI Corrente: {rsi:.1f}")

    # Aggiornamo la memoria del precedente RSI per il prossimo ciclo
    portfolio["prev_rsi"] = rsi

    action_msg = " | ".join(action_logs)

    total_sol_held = sum(p['amount'] for p in portfolio['positions'])
    total_value = portfolio["cash"] + (total_sol_held * price)
    pnl = total_value - portfolio['initial_capital']

    save_portfolio(portfolio)
    update_dashboards(timestamp, price, changes, sma, rsi, signal, portfolio, total_value, pnl, action_msg)
    
    print("=== Ciclo completato con successo ===")

if __name__ == "__main__":
    run_paper_trade()
