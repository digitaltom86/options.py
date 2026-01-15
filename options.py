import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
import pandas as pd

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="Options Master Pro - Simulator",
    page_icon="📈",
    layout="wide"
)

# --- SILNIK MATEMATYCZNY (BLACK-SCHOLES) ---
def black_scholes(S, K, T, r, sigma, option_type="call"):
    """Oblicza teoretyczną cenę opcji oraz Greki."""
    if T <= 0: T = 1e-6 # Zabezpieczenie przed dzieleniem przez zero
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        delta = norm.cdf(d1)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = norm.cdf(d1) - 1
    
    # Vega i Theta (dzienna)
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100
    theta = (-(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2 if option_type=="call" else -d2)) / 365
    
    return price, delta, theta, vega

# --- INTERFEJS UŻYTKOWNIKA ---
st.title("📈 Options Strategy Master Simulator")
st.markdown("---")

# Sidebar - Parametry rynkowe
st.sidebar.header("⚙️ Ustawienia Rynku / Market Settings")
lang = st.sidebar.radio("Język / Language", ["PL", "EN"])

# Słownik tłumaczeń
t = {
    "price": {"PL": "Cena instrumentu (S)", "EN": "Asset Price (S)"},
    "strike": {"PL": "Cena wykonania (K)", "EN": "Strike Price (K)"},
    "vol": {"PL": "Zmienność Implikowana (%)", "EN": "Implied Volatility (%)"},
    "days": {"PL": "Dni do wygaśnięcia", "EN": "Days to Expiration"},
    "strategy": {"PL": "Wybierz Strategię", "EN": "Select Strategy"},
    "results": {"PL": "Analiza Wyników", "EN": "Results Analysis"},
}

with st.sidebar:
    S = st.number_input(t["price"][lang], value=100.0, step=1.0)
    K = st.number_input(t["strike"][lang], value=105.0, step=1.0)
    vol = st.slider(t["vol"][lang], 5, 150, 30) / 100
    days = st.slider(t["days"][lang], 1, 365, 30)
    r = st.sidebar.slider("Risk-Free Rate (%)", 0.0, 10.0, 4.5) / 100
    contract_size = st.sidebar.number_input("Contract Size", value=100)

# Wybór strategii
st.subheader(f"🛠️ {t['strategy'][lang]}")
strategies = ["Long Call", "Short Call", "Long Put", "Short Put", "Covered Call"]
strategy = st.selectbox("", strategies)

# Obliczenia bazowe
T = days / 365
opt_type = "call" if "Call" in strategy else "put"
prem_theo, delta, theta, vega = black_scholes(S, K, T, r, vol, opt_type)

# --- GENEROWANIE WYKRESU P&L ---
x_range = np.linspace(S * 0.6, S * 1.4, 200)

if strategy == "Long Call":
    y_range = (np.maximum(x_range - K, 0) - prem_theo) * contract_size
    be = K + prem_theo
elif strategy == "Short Call":
    y_range = (prem_theo - np.maximum(x_range - K, 0)) * contract_size
    be = K + prem_theo
elif strategy == "Long Put":
    y_range = (np.maximum(K - x_range, 0) - prem_theo) * contract_size
    be = K - prem_theo
elif strategy == "Short Put":
    y_range = (prem_theo - np.maximum(K - x_range, 0)) * contract_size
    be = K - prem_theo
elif strategy == "Covered Call":
    y_range = ((x_range - S) + prem_theo - np.maximum(x_range - K, 0)) * contract_size
    be = S - prem_theo

# Wykres Plotly
fig = go.Figure()
# Obszar zysku i straty (kolorowanie)
fig.add_trace(go.Scatter(x=x_range, y=y_range, fill='tozeroy', name='P&L', line=dict(color='cyan', width=4)))
fig.add_hline(y=0, line_dash="dash", line_color="white")
fig.add_vline(x=S, line_dash="dot", line_color="orange", annotation_text="ENTRY PRICE")

fig.update_layout(
    title=f"{strategy} - Profit & Loss at Expiration",
    xaxis_title="Price at Expiration",
    yaxis_title="Profit / Loss ($)",
    template="plotly_dark",
    hovermode="x unified",
    height=500
)
st.plotly_chart(fig, use_container_width=True)

# --- DASHBOARD STATYSTYCZNY ---
st.subheader(f"📊 {t['results'][lang]}")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Total Premium", f"${prem_theo * contract_size:.2f}")
    st.caption("Całkowita premia za kontrakt")

with c2:
    st.metric("Breakeven", f"${be:.2f}")
    st.caption("Punkt wyjścia na zero")

with c3:
    st.metric("Delta (Δ)", f"{delta:.2f}")
    st.caption("Wrażliwość na zmianę ceny")

with c4:
    st.metric("Theta (Θ)", f"${theta * contract_size:.2f}")
    st.caption("Dzienny spadek wartości (Time Decay)")

# --- DODATKOWE NARZĘDZIE: IV CRUSH ---
st.markdown("---")
with st.expander("⚡ IV Crush & Probability Analysis"):
    st.write("Symulacja spadku zmienności po wynikach (Earnings)")
    drop = st.slider("IV Drop (%)", 0, 80, 20)
    new_vol = max(0.01, vol - (drop/100))
    new_prem, _, _, _ = black_scholes(S, K, T, r, new_vol, opt_type)
    impact = (new_prem - prem_theo) * contract_size
    
    st.warning(f"Efekt spadku zmienności: Twoja premia zmieni się o ok. {impact:.2f} USD")
    
    # Prosta statystyka
    prob_itm = norm.cdf((np.log(S/K) + (r - 0.5*vol**2)*T) / (vol*np.sqrt(T)))
    if opt_type == "put": prob_itm = 1 - prob_itm
    st.write(f"Teoretyczne szanse, że opcja wygaśnie 'w pieniądzu' (ITM): **{prob_itm*100:.1f}%**")

# Stopka
st.markdown("---")
st.caption("Options Master Pro v2.0 | Wykorzystano model Blacka-Scholesa | 2026")
