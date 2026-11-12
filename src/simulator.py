def update_readme_dashboard(timestamp, price, changes, sma, rsi, signal, portfolio, total_value, pnl, action_msg):
    """Scrive la dashboard in 4 blocchi visivi sul README.md"""
    
    pos_status = "🟢 POSIZIONE APERTA (In attesa di TP)" if portfolio["position_active"] else "⚪ FLAT (Liquidità disponibile)"
    entry = f"${portfolio['entry_price']:.2f}" if portfolio["position_active"] else "---"
    tp = f"${portfolio['take_profit_price']:.2f} (+5%)" if portfolio["position_active"] else "---"
    pnl_color = "🟢" if pnl >= 0 else "🔴"

    dashboard_content = f"""# 🤖 Solana Algorithmic Trading Bot ($30 Paper Portfolio)

*Ultimo aggiornamento:* `{timestamp} UTC`

---

### 📦 1. PORTAFOGLIO & CAPITALE
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

### 🎯 3. POSIZIONE ATTIVA & REGOLE
| Stato | Prezzo Ingresso | Target Take Profit | Stop Loss |
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
