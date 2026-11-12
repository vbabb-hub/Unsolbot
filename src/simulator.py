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
        "sol": 0.0, 
        "initial_capital": 30.00, 
        "position_active": False, 
        "entry_price": 0.0, 
        "take_profit_price": 0.0,
        "invested_slots": 0
    }

def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=4)

def update_readme_dashboard(timestamp, price, changes, sma, rsi, signal, portfolio, total_value, pnl, action_msg):
    """Scrive la dashboard aggiornata con la regola del 20% sul README.md"""
    
    invested_capital = portfolio['initial_capital'] - portfolio['cash']
    exposure_pct = (invested_capital / portfolio['initial_capital']) * 100
    
    pos_status = f"🟢 ATTIVO ({exposure_pct:.0f}% capitale esposto - Slot: {portfolio['invested_slots']}/4)" if portfolio["invested_slots"] > 0 else "⚪ FLAT (Liquidità disponibile)"
    entry = f"${portfolio['entry_price']:.2f}" if portfolio["position_active"] else "---"
    tp = f"${portfolio['take_profit_price']:.2f} (+5%)" if portfolio["position_active"] else "---"
    pnl_color = "🟢" if pnl >= 0 else "🔴"

    dashboard_content = f"""# 🤖 Solana Algorithmic Trading Bot ($30 Paper Portfolio)

*Ultimo aggiornamento:* `{timestamp} UTC`

---

### 📦 1. PORTAFOGLIO & CAPITALE (Max 80% Esposizione)
| Metrica | Valore |
| :--- | :--- |
| **Capitale Iniziale** | `$30.00` |
| **Cash Disponibile** | `${portfolio['cash']:.2f}` |
| **Asset in SOL** | `{portfolio['sol']:.4f} SOL` |
| **Valore Totale** | **${total_value:.2f}** |
| **Performance (P&L)** | {pnl_color} **${pnl:+.2f}** ({ (pnl/30)*100:+.2f}% ) |

---

### 📊 2. TREND SOLANA (TIMEFRAME)
| 1h | 1d | 1w | 1m | 1y | ATH |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `{changes['1h']:+.2f}%` | `{changes['1d']:+.2f}%` | `{changes['1w']:+.2f}%` | `{changes['1m']:+.2f}%` | `{changes['1y']:+.2f}%` | **`${changes['ath']:.2f}`** |

*(Prezzo spot attuale: **${price:.2f}**)*

---

### 🎯 3. POSIZIONE ATTIVA & REGOLE (Frazionata 20%)
| Stato Esposizione | Prezzo Ingresso | Target Take Profit | Stop Loss |
| :--- | :--- | :--- | :--- |
| `{pos_status}` | `{entry}` | `{tp}` | **DISABILITATO (HODL)** |

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
    print(f"[{timestamp}] === Avvio Ciclo Bot Trading (Frazionato 20%) ===")
    
    price, changes = get_sol_market_data()
    if not price:
        print("Impossibile recuperare il prezzo di Solana.")
        return

    portfolio = load_portfolio()
    signal, sma, rsi = analyze_market()
    
    total_value = portfolio["cash"] + (portfolio["sol"] * price)
    pnl = total_value - portfolio['initial_capital']
    
    action_msg = "Nessuna operazione effettuata."

    # 1. Controllo Take Profit se c'è una posizione aperta (sul prezzo di carico attuale)
    if portfolio["position_active"] and price >= portfolio["take_profit_price"]:
        cash_earned = portfolio["sol"] * price
        portfolio["cash"] += cash_earned
        action_msg = f"🎯 Take Profit raggiunto a ${price:.2f}! Liquidati tutti i SOL per ${cash_earned:.2f}"
        print(f">>> {action_msg}")
        
        # Reset completo della posizione
        portfolio["sol"] = 0.0
        portfolio["position_active"] = False
        portfolio["entry_price"] = 0.0
        portfolio["take_profit_price"] = 0.0
        portfolio["invested_slots"] = 0

    else:
        # 2. Controllo Segnale d'Acquisto con limite massimo all'80% (max 4 slot da 20%)
        max_investment_allowed = portfolio['initial_capital'] * 0.80  # 80% di 30$ = 24$
        current_invested = portfolio['initial_capital'] - portfolio['cash']
        amount_per_tranche = portfolio['initial_capital'] * 0.20       # 20% di 30$ = 6$

        if "BUY" in signal:
            if current_invested < max_investment_allowed and portfolio["cash"] >= amount_per_tranche:
                # Esegue l'acquisto del 20%
                sol_bought = amount_per_tranche / price
                portfolio["sol"] += sol_bought
                portfolio["cash"] -= amount_per_tranche
                
                # Aggiorna i dati della posizione
                portfolio["position_active"] = True
                portfolio["invested_slots"] += 1
                portfolio["entry_price"] = price  # Aggiorna al prezzo dell'ultimo acquisto (o media)
                portfolio["take_profit_price"] = price * 1.05  # Target +5% sul nuovo carico
                
                action_msg = f"🛒 Tranche #{portfolio['invested_slots']} (20%): Acquistati {sol_bought:.4f} SOL a ${price:.2f}. TP: ${portfolio['take_profit_price']:.2f}"
                print(f">>> [ACQUISTO FRAZIONATO] {action_msg}")
            else:
                action_msg = "Segnale BUY ricevuto, ma limite massimo di esposizione (80%) raggiunto o cash insufficiente."
                print(f">>> [CAP RAGGIUNTO] Nessun nuovo acquisto effettuato.")
        else:
            if portfolio["position_active"]:
                action_msg = f"Posizione attiva ({portfolio['invested_slots']} slot). In attesa del TP o nuovi segnali."
            else:
                action_msg = "In attesa di condizioni di ingresso (RSI/SMA)."

    # Ricalcolo finale
    total_value = portfolio["cash"] + (portfolio["sol"] * price)
    pnl = total_value - portfolio['initial_capital']

    save_portfolio(portfolio)
    update_readme_dashboard(timestamp, price, changes, sma, rsi, signal, portfolio, total_value, pnl, action_msg)
    
    print("=== Ciclo completato con successo ===")

if __name__ == "__main__":
    run_paper_trade()
