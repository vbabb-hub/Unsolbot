import json
import os
from datetime import datetime
from bot_logic import get_sol_market_data, analyze_market

PORTFOLIO_FILE = "src/portfolio.json"
README_FILE = "README.md"

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)
    return {
        "cash": 30.00, 
        "initial_capital": 30.00, 
        "positions": []
    }

def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=4)

def update_readme_dashboard(timestamp, price, changes, sma, rsi, signal, portfolio, total_value, pnl, action_msg):
    """Scrive la dashboard aggiornata con posizioni indipendenti sul README.md"""
    
    invested_capital = sum(p['cost'] for p in portfolio['positions'])
    total_sol = sum(p['amount'] for p in portfolio['positions'])
    exposure_pct = (invested_capital / portfolio['initial_capital']) * 100
    
    num_pos = len(portfolio['positions'])
    pos_status = f"🟢 ATTIVO ({num_pos} posizioni aperte - {exposure_pct:.0f}% capitale)" if num_pos > 0 else "⚪ FLAT (Liquidità disponibile)"
    
    pnl_color = "🟢" if pnl >= 0 else "🔴"

    # Tabella delle posizioni aperte dettagliate
    positions_rows = ""
    if num_pos > 0:
        for i, pos in enumerate(portfolio['positions'], 1):
            positions_rows += f"| Tranche #{i} | {pos['amount']:.4f} SOL | ${pos['entry']:.2f} | ${pos['tp']:.2f} (+5%) |\n"
    else:
        positions_rows = "| Nessuna posizione attiva | --- | --- | --- |\n"

    dashboard_content = f"""# 🤖 Solana Algorithmic Trading Bot ($30 Paper Portfolio)

*Ultimo aggiornamento:* `{timestamp} UTC`

---

### 📦 1. PORTAFOGLIO & CAPITALE (Max 4 Tranches da 20%)
| Metrica | Valore |
| :--- | :--- |
| **Capitale Iniziale** | `$30.00` |
| **Cash Disponibile** | `${portfolio['cash']:.2f}` |
| **Asset Totali in SOL** | `{total_sol:.4f} SOL` |
| **Valore Totale** | **${total_value:.2f}** |
| **Performance (P&L)** | {pnl_color} **${pnl:+.2f}** ({ (pnl/30)*100:+.2f}% ) |

---

### 📊 2. TREND SOLANA (TIMEFRAME)
| 1h | 1d | 1w | 1m | 1y | ATH |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `{changes['1h']:+.2f}%` | `{changes['1d']:+.2f}%` | `{changes['1w']:+.2f}%` | `{changes['1m']:+.2f}%` | `{changes['1y']:+.2f}%` | **`${changes['ath']:.2f}`** |

*(Prezzo spot attuale: **${price:.2f}**)*

---

### 🎯 3. POSIZIONI APERTE INDIPENDENTI (No Stop-Loss)
| Tranche | Quantità SOL | Prezzo Ingresso | Target Take Profit (TP) |
| :--- | :--- | :--- | :--- |
{positions_rows}

*Stato generale:* `{pos_status}`

---

### ⚙️ 4. DIAGNOSTICA TECNICA & ULTIMO EVENTO
| Indicatore / Log | Stato Corrente |
| :--- | :--- |
| **Media Mobile (SMA 20)** | `${sma:.2f}` |
| **RSI (14 periodi)** | `{rsi:.1f}` |
| **Segnale Modello** | `{signal}` |
| **Ultima Azione** | `{action_msg}` |

---
*Esecuzione automatica tramite GitHub Actions.*
"""
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(dashboard_content)

def run_paper_trade():
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] === Avvio Ciclo Bot Trading (Posizioni Indipendenti) ===")
    
    price, changes = get_sol_market_data()
    if not price:
        print("Impossibile recuperare il prezzo di Solana.")
        return

    portfolio = load_portfolio()
    signal, sma, rsi = analyze_market()
    
    action_logs = []

    # 1. CONTROLLO TAKE PROFIT INDIPENDENTE PER CIASCUNA POSIZIONE
    remaining_positions = []
    freed_cash = 0.0

    for pos in portfolio['positions']:
        if price >= pos['tp']:
            # Questa singola posizione ha raggiunto il suo TP del +5%!
            sale_value = pos['amount'] * price
            freed_cash += sale_value
            action_logs.append(f"🎯 TP raggiunto! Venduti {pos['amount']:.4f} SOL (Entrata: ${pos['entry']:.2f}) a ${price:.2f} per ${sale_value:.2f}")
        else:
            # Questa posizione non ha ancora raggiunto il target, resta aperta
            remaining_positions.append(pos)

    portfolio['positions'] = remaining_positions
    portfolio['cash'] += freed_cash

    if freed_cash > 0:
        print(f">>> [TAKE PROFIT SINGOLO] Chiusa/e tranche in utile. Cash recuperato: ${freed_cash:.2f}")

    # 2. CONTROLLO SEGNALE D'ACQUISTO (Se c'è segnale BUY, spazio e cash)
    max_investment_allowed = portfolio['initial_capital'] * 0.80  # Max 80% (24$)
    current_invested = sum(p['cost'] for p in portfolio['positions'])
    amount_per_tranche = portfolio['initial_capital'] * 0.20       # 20% (6$)

    if "BUY" in signal:
        if current_invested < max_investment_allowed and portfolio["cash"] >= amount_per_tranche:
            # Apri una nuova tranche indipendente
            sol_bought = amount_per_tranche / price
            new_position = {
                "amount": sol_bought,
                "cost": amount_per_tranche,
                "entry": price,
                "tp": price * 1.05  # TP fissato al +5% per questa specifica tranche
            }
            portfolio['positions'].append(new_position)
            portfolio["cash"] -= amount_per_tranche
            
            msg = f"🛒 Nuova Tranche (20%): Acquistati {sol_bought:.4f} SOL a ${price:.2f}. TP mirato a ${new_position['tp']:.2f}"
            action_logs.append(msg)
            print(f">>> [ACQUISTO FRAZIONATO] {msg}")
        else:
            msg = "Segnale BUY ricevuto, ma cap 80% raggiunto o cash insufficiente per una nuova tranche."
            if not action_logs: action_logs.append(msg)
    else:
        if not action_logs:
            num_active = len(portfolio['positions'])
            action_logs.append(f"In attesa (posizioni attive: {num_active}). Nessun target TP toccato.")

    action_msg = " | ".join(action_logs)

    # Ricalcolo totale portafoglio e P&L
    total_sol_held = sum(p['amount'] for p in portfolio['positions'])
    total_value = portfolio["cash"] + (total_sol_held * price)
    pnl = total_value - portfolio['initial_capital']

    save_portfolio(portfolio)
    update_readme_dashboard(timestamp, price, changes, sma, rsi, signal, portfolio, total_value, pnl, action_msg)
    
    print("=== Ciclo completato con successo ===")

if __name__ == "__main__":
    run_paper_trade()
