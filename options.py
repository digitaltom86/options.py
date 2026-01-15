"""
🎓 AKADEMIA OPCJI - Kompletna Platforma Edukacyjna
Zoptymalizowany kod do nauki wszystkich strategii opcyjnych
"""
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from dataclasses import dataclass
from typing import Callable

# ══════════════════════════════════════════════════════════════════════════════
# KONFIGURACJA I STAŁE
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="🎓 Akademia Opcji", 
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stałe finansowe
R = 0.045  # Stopa wolna od ryzyka

# ══════════════════════════════════════════════════════════════════════════════
# MODEL BLACKA-SCHOLESA - Serce wyceny opcji
# ══════════════════════════════════════════════════════════════════════════════
def bs(S: float, K: float, T: float, r: float, σ: float, typ: str = "call") -> dict:
    """
    Model Blacka-Scholesa - wycena opcji i współczynniki greckie.
    
    Parametry:
        S: Cena spot aktywa bazowego
        K: Strike (cena wykonania)
        T: Czas do wygaśnięcia (w latach)
        r: Stopa wolna od ryzyka
        σ: Zmienność implikowana (sigma)
        typ: "call" lub "put"
    
    Zwraca słownik z: cena, delta, gamma, theta, vega
    """
    T = max(T, 1e-6)  # Zabezpieczenie przed dzieleniem przez zero
    sqrt_T = np.sqrt(T)
    
    d1 = (np.log(S / K) + (r + 0.5 * σ**2) * T) / (σ * sqrt_T)
    d2 = d1 - σ * sqrt_T
    
    # Wartości pomocnicze
    Nd1, Nd2 = norm.cdf(d1), norm.cdf(d2)
    nd1 = norm.pdf(d1)
    exp_rT = np.exp(-r * T)
    
    if typ == "call":
        cena = S * Nd1 - K * exp_rT * Nd2
        delta = Nd1
        theta_dir = norm.cdf(d2)
    else:
        cena = K * exp_rT * (1 - Nd2) - S * (1 - Nd1)
        delta = Nd1 - 1
        theta_dir = norm.cdf(-d2)
    
    # Współczynniki greckie (wspólne dla call i put)
    gamma = nd1 / (S * σ * sqrt_T)
    vega = S * nd1 * sqrt_T / 100  # Na 1% zmianę IV
    theta = (-(S * nd1 * σ) / (2 * sqrt_T) - r * K * exp_rT * theta_dir) / 365
    
    return {"cena": cena, "delta": delta, "gamma": gamma, "theta": theta, "vega": vega}

# ══════════════════════════════════════════════════════════════════════════════
# DEFINICJE STRATEGII - Biblioteka wiedzy
# ══════════════════════════════════════════════════════════════════════════════
@dataclass
class Strategia:
    """Struktura danych opisująca strategię opcyjną"""
    nazwa: str
    kategoria: str
    opis: str
    kiedy: str
    konstrukcja: str
    max_zysk: str
    max_strata: str
    breakeven: str
    greeks: str
    poziom: str  # "🟢 Podstawowy", "🟡 Średni", "🔴 Zaawansowany"
    
STRATEGIE = {
    # ═══════════════════════════════════════════════════════════════════════════
    # STRATEGIE PODSTAWOWE
    # ═══════════════════════════════════════════════════════════════════════════
    "Long Call": Strategia(
        nazwa="Long Call",
        kategoria="📗 Podstawowa",
        opis="Najprostsza strategia byka - kupno opcji call z oczekiwaniem wzrostu ceny.",
        kiedy="✅ Oczekujesz SILNEGO wzrostu ceny\n✅ Chcesz ograniczyć ryzyko do premii\n✅ Masz określony horyzont czasowy\n❌ NIE używaj przy wysokiej IV (drogo!)",
        konstrukcja="Kupno 1 opcji CALL",
        max_zysk="♾️ Nieograniczony",
        max_strata="Ograniczona do zapłaconej premii",
        breakeven="Strike + Premia",
        greeks="Delta ⬆️ | Gamma ⬆️ | Theta ⬇️ | Vega ⬆️",
        poziom="🟢 Podstawowy"
    ),
    "Long Put": Strategia(
        nazwa="Long Put",
        kategoria="📗 Podstawowa",
        opis="Najprostsza strategia niedźwiedzia - kupno opcji put z oczekiwaniem spadku.",
        kiedy="✅ Oczekujesz SILNEGO spadku ceny\n✅ Chcesz zabezpieczyć długą pozycję\n✅ Przed negatywnymi wydarzeniami\n❌ NIE używaj przy wysokiej IV",
        konstrukcja="Kupno 1 opcji PUT",
        max_zysk="Ograniczony (cena może spaść do 0)",
        max_strata="Ograniczona do zapłaconej premii",
        breakeven="Strike - Premia",
        greeks="Delta ⬇️ | Gamma ⬆️ | Theta ⬇️ | Vega ⬆️",
        poziom="🟢 Podstawowy"
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STRATEGIE DOCHODOWE
    # ═══════════════════════════════════════════════════════════════════════════
    "Covered Call": Strategia(
        nazwa="Covered Call",
        kategoria="💰 Dochodowa",
        opis="Posiadanie akcji + sprzedaż call. Generujesz dochód w zamian za ograniczenie wzrostu.",
        kiedy="✅ Posiadasz akcje długoterminowo\n✅ Oczekujesz ruchu bocznego/lekkiego wzrostu\n✅ Chcesz generować miesięczny dochód\n✅ Przy wysokiej IV (wyższe premie!)\n❌ NIE przy oczekiwaniu silnego wzrostu",
        konstrukcja="100 akcji + Sprzedaż 1 CALL OTM",
        max_zysk="(Strike - Cena akcji) + Premia",
        max_strata="Duża (cena może spaść do 0), zmniejszona o premię",
        breakeven="Cena zakupu akcji - Premia",
        greeks="Delta ⬆️ mała | Theta ⬆️ (korzystna!)",
        poziom="🟢 Podstawowy"
    ),
    "Protective Put": Strategia(
        nazwa="Protective Put",
        kategoria="🛡️ Zabezpieczająca",
        opis="Ubezpieczenie akcji - kupno put jako ochrona przed spadkiem.",
        kiedy="✅ Posiadasz akcje i boisz się spadku\n✅ Przed ważnymi wydarzeniami (wyniki)\n✅ Chcesz zachować potencjał wzrostu\n❌ Kosztowne przy wysokiej IV",
        konstrukcja="100 akcji + Kupno 1 PUT",
        max_zysk="♾️ Nieograniczony (wzrost akcji)",
        max_strata="(Cena akcji - Strike) + Premia",
        breakeven="Cena zakupu + Premia",
        greeks="Delta ⬆️ z ograniczeniem strat",
        poziom="🟢 Podstawowy"
    ),
    "Collar": Strategia(
        nazwa="Collar",
        kategoria="🛡️ Zabezpieczająca",
        opis="Ochrona za darmo - kupno put + sprzedaż call. Ograniczasz zysk i stratę.",
        kiedy="✅ Chcesz zabezpieczyć zyski BEZ KOSZTU\n✅ Przed niepewnymi wydarzeniami\n✅ Gdy masz duży niezrealizowany zysk\n❌ Ogranicza dalszy wzrost",
        konstrukcja="100 akcji + Kupno PUT OTM + Sprzedaż CALL OTM",
        max_zysk="Strike call - Cena akcji ± Premia netto",
        max_strata="Cena akcji - Strike put ± Premia netto",
        breakeven="Zależy od premii (często zero-cost)",
        greeks="Delta ⬆️ ograniczona | Theta/Vega minimalne",
        poziom="🟡 Średni"
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SPREADY
    # ═══════════════════════════════════════════════════════════════════════════
    "Bull Call Spread": Strategia(
        nazwa="Bull Call Spread",
        kategoria="📊 Spread",
        opis="Tańszy wzrost - kupno call + sprzedaż wyższego call. Ogranicza koszt i zysk.",
        kiedy="✅ Oczekujesz UMIARKOWANEGO wzrostu\n✅ Chcesz tańszą alternatywę dla long call\n✅ Przy wysokiej IV (sprzedaż offset'uje koszt)\n❌ NIE przy oczekiwaniu silnego wzrostu",
        konstrukcja="Kupno CALL niższy strike + Sprzedaż CALL wyższy strike",
        max_zysk="Różnica strike'ów - Premia netto",
        max_strata="Zapłacona premia netto",
        breakeven="Niższy strike + Premia",
        greeks="Delta ⬆️ | Theta ≈ neutralna",
        poziom="🟡 Średni"
    ),
    "Bear Put Spread": Strategia(
        nazwa="Bear Put Spread",
        kategoria="📊 Spread",
        opis="Tańszy spadek - kupno put + sprzedaż niższego put. Ogranicza koszt i zysk.",
        kiedy="✅ Oczekujesz UMIARKOWANEGO spadku\n✅ Chcesz tańszą alternatywę dla long put\n✅ Przy wysokiej IV\n❌ NIE przy oczekiwaniu silnego spadku",
        konstrukcja="Kupno PUT wyższy strike + Sprzedaż PUT niższy strike",
        max_zysk="Różnica strike'ów - Premia netto",
        max_strata="Zapłacona premia netto",
        breakeven="Wyższy strike - Premia",
        greeks="Delta ⬇️ | Theta ≈ neutralna",
        poziom="🟡 Średni"
    ),
    "Bull Put Spread": Strategia(
        nazwa="Bull Put Spread",
        kategoria="📊 Spread",
        opis="Kredytowy byczy - sprzedaż put + kupno niższego put. Zarabiasz jeśli cena nie spada.",
        kiedy="✅ Oczekujesz, że cena NIE SPADNIE\n✅ Chcesz natychmiastową premię\n✅ Przy wysokiej IV (wyższe premie)\n✅ Rynek boczny lub lekko wzrostowy",
        konstrukcja="Sprzedaż PUT wyższy strike + Kupno PUT niższy strike",
        max_zysk="Otrzymana premia netto",
        max_strata="Różnica strike'ów - Premia",
        breakeven="Wyższy strike - Premia",
        greeks="Delta ⬆️ | Theta ⬆️ (korzystna!)",
        poziom="🟡 Średni"
    ),
    "Bear Call Spread": Strategia(
        nazwa="Bear Call Spread",
        kategoria="📊 Spread",
        opis="Kredytowy niedźwiedzi - sprzedaż call + kupno wyższego call. Zarabiasz jeśli cena nie rośnie.",
        kiedy="✅ Oczekujesz, że cena NIE WZROŚNIE\n✅ Chcesz natychmiastową premię\n✅ Przy wysokiej IV\n✅ Rynek boczny lub spadkowy",
        konstrukcja="Sprzedaż CALL niższy strike + Kupno CALL wyższy strike",
        max_zysk="Otrzymana premia netto",
        max_strata="Różnica strike'ów - Premia",
        breakeven="Niższy strike + Premia",
        greeks="Delta ⬇️ | Theta ⬆️ (korzystna!)",
        poziom="🟡 Średni"
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STRATEGIE NA ZMIENNOŚĆ
    # ═══════════════════════════════════════════════════════════════════════════
    "Long Straddle": Strategia(
        nazwa="Long Straddle",
        kategoria="🌪️ Zmienność",
        opis="Gra na duży ruch - kupno call + put z tym samym strike. Kierunek nieważny!",
        kiedy="✅ Przed WAŻNYMI wydarzeniami (wyniki, FDA)\n✅ Oczekujesz DUŻEGO ruchu w dowolnym kierunku\n✅ Przy NISKIEJ IV (tanie opcje)\n❌ NIE przy wysokiej IV (za drogo!)\n❌ NIE przy stabilnym rynku",
        konstrukcja="Kupno CALL ATM + Kupno PUT ATM (ten sam strike)",
        max_zysk="♾️ Nieograniczony",
        max_strata="Suma obu premii",
        breakeven="Strike ± Suma premii (dwa punkty!)",
        greeks="Delta ≈ 0 | Gamma ⬆️⬆️ | Theta ⬇️⬇️ | Vega ⬆️⬆️",
        poziom="🟡 Średni"
    ),
    "Long Strangle": Strategia(
        nazwa="Long Strangle",
        kategoria="🌪️ Zmienność",
        opis="Tańszy straddle - kupno OTM call + OTM put. Wymaga większego ruchu.",
        kiedy="✅ Oczekujesz BARDZO DUŻEGO ruchu\n✅ Chcesz tańszą alternatywę dla straddle\n✅ Przy niskiej IV\n❌ Wymaga jeszcze większego ruchu niż straddle",
        konstrukcja="Kupno CALL OTM + Kupno PUT OTM",
        max_zysk="♾️ Nieograniczony",
        max_strata="Suma obu premii (niższa niż straddle)",
        breakeven="Put strike - Premia put | Call strike + Premia call",
        greeks="Delta ≈ 0 | Gamma ⬆️ | Theta ⬇️ | Vega ⬆️",
        poziom="🟡 Średni"
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # STRATEGIE NEUTRALNE
    # ═══════════════════════════════════════════════════════════════════════════
    "Iron Condor": Strategia(
        nazwa="Iron Condor",
        kategoria="😴 Neutralna",
        opis="Król strategii dochodowych - zarabiasz na BRAKU ruchu. Cztery opcje tworzą tunel zysku.",
        kiedy="✅ Oczekujesz NISKIEJ zmienności\n✅ Rynek boczny, konsolidacja\n✅ Przy WYSOKIEJ IV (wyższe premie!)\n✅ Po dużych ruchach (powrót do średniej)\n❌ NIE przed ważnymi wydarzeniami",
        konstrukcja="Sprzedaż PUT + Kupno niższego PUT + Sprzedaż CALL + Kupno wyższego CALL",
        max_zysk="Otrzymana premia netto",
        max_strata="Szerokość spreadu - Premia",
        breakeven="Wewnętrzne strike'i ± Premia",
        greeks="Delta ≈ 0 | Gamma ⬇️ | Theta ⬆️⬆️ (super!) | Vega ⬇️",
        poziom="🟡 Średni"
    ),
    "Iron Butterfly": Strategia(
        nazwa="Iron Butterfly",
        kategoria="😴 Neutralna",
        opis="Precyzyjny neutralny - wszystkie sprzedane opcje mają ten sam strike. Maksymalny zysk przy dokładnej cenie.",
        kiedy="✅ Oczekujesz, że cena pozostanie DOKŁADNIE przy strike\n✅ Przy bardzo wysokiej IV\n✅ Węższy zakres zysku niż Iron Condor\n❌ Wymaga większej precyzji",
        konstrukcja="Sprzedaż PUT ATM + Kupno PUT OTM + Sprzedaż CALL ATM + Kupno CALL OTM",
        max_zysk="Otrzymana premia netto",
        max_strata="Szerokość skrzydła - Premia",
        breakeven="Środkowy strike ± Premia",
        greeks="Delta ≈ 0 | Gamma ⬇️⬇️ | Theta ⬆️ | Vega ⬇️",
        poziom="🔴 Zaawansowany"
    ),
    "Long Butterfly": Strategia(
        nazwa="Long Butterfly",
        kategoria="😴 Neutralna",
        opis="Tani zakład na konkretną cenę - maksymalny zysk gdy cena = środkowy strike.",
        kiedy="✅ Oczekujesz, że cena będzie przy KONKRETNYM poziomie\n✅ Niski koszt wejścia\n✅ Przed wygaśnięciem, gdy znasz cel\n❌ Wąski zakres zysku",
        konstrukcja="Kupno CALL ITM + Sprzedaż 2× CALL ATM + Kupno CALL OTM",
        max_zysk="(Szerokość skrzydła - Premia) przy środkowym strike",
        max_strata="Zapłacona premia netto (niska!)",
        breakeven="Środkowy strike ± Szerokość - Premia",
        greeks="Delta ≈ 0 | Gamma ujemna przy środku | Theta ⬆️",
        poziom="🔴 Zaawansowany"
    ),
}

# ══════════════════════════════════════════════════════════════════════════════
# FUNKCJE PAYOFF DLA STRATEGII
# ══════════════════════════════════════════════════════════════════════════════
def payoff_long_call(x, S, K, T, σ):
    """Payoff dla Long Call"""
    premia = bs(S, K, T, R, σ, "call")["cena"]
    return np.maximum(x - K, 0) - premia, premia, {"delta": bs(S, K, T, R, σ, "call")["delta"], 
                                                    "theta": bs(S, K, T, R, σ, "call")["theta"],
                                                    "vega": bs(S, K, T, R, σ, "call")["vega"]}

def payoff_long_put(x, S, K, T, σ):
    """Payoff dla Long Put"""
    premia = bs(S, K, T, R, σ, "put")["cena"]
    return np.maximum(K - x, 0) - premia, premia, {"delta": bs(S, K, T, R, σ, "put")["delta"],
                                                    "theta": bs(S, K, T, R, σ, "put")["theta"],
                                                    "vega": bs(S, K, T, R, σ, "put")["vega"]}

def payoff_covered_call(x, S, K, T, σ):
    """Payoff dla Covered Call"""
    premia = bs(S, K, T, R, σ, "call")["cena"]
    pozycja_akcji = x - S
    krotka_call = premia - np.maximum(x - K, 0)
    g = bs(S, K, T, R, σ, "call")
    return pozycja_akcji + krotka_call, premia, {"delta": 1 - g["delta"], "theta": -g["theta"], "vega": -g["vega"]}

def payoff_protective_put(x, S, K, T, σ):
    """Payoff dla Protective Put"""
    premia = bs(S, K, T, R, σ, "put")["cena"]
    pozycja_akcji = x - S
    dluga_put = np.maximum(K - x, 0) - premia
    g = bs(S, K, T, R, σ, "put")
    return pozycja_akcji + dluga_put, premia, {"delta": 1 + g["delta"], "theta": g["theta"], "vega": g["vega"]}

def payoff_collar(x, S, K_put, K_call, T, σ):
    """Payoff dla Collar"""
    premia_put = bs(S, K_put, T, R, σ, "put")["cena"]
    premia_call = bs(S, K_call, T, R, σ, "call")["cena"]
    koszt = premia_put - premia_call
    pozycja = (x - S) + np.maximum(K_put - x, 0) - np.maximum(x - K_call, 0)
    return pozycja - koszt, koszt, {"delta": 0.5, "theta": 0, "vega": 0}

def payoff_bull_call_spread(x, S, K1, K2, T, σ):
    """Payoff dla Bull Call Spread"""
    c1 = bs(S, K1, T, R, σ, "call")["cena"]
    c2 = bs(S, K2, T, R, σ, "call")["cena"]
    koszt = c1 - c2
    g1, g2 = bs(S, K1, T, R, σ, "call"), bs(S, K2, T, R, σ, "call")
    return np.maximum(x - K1, 0) - np.maximum(x - K2, 0) - koszt, koszt, {
        "delta": g1["delta"] - g2["delta"], 
        "theta": g1["theta"] - g2["theta"],
        "vega": g1["vega"] - g2["vega"]
    }

def payoff_bear_put_spread(x, S, K1, K2, T, σ):
    """Payoff dla Bear Put Spread (K1 niższy, K2 wyższy)"""
    p1 = bs(S, K1, T, R, σ, "put")["cena"]
    p2 = bs(S, K2, T, R, σ, "put")["cena"]
    koszt = p2 - p1
    g1, g2 = bs(S, K1, T, R, σ, "put"), bs(S, K2, T, R, σ, "put")
    return np.maximum(K2 - x, 0) - np.maximum(K1 - x, 0) - koszt, koszt, {
        "delta": g2["delta"] - g1["delta"],
        "theta": g2["theta"] - g1["theta"],
        "vega": g2["vega"] - g1["vega"]
    }

def payoff_bull_put_spread(x, S, K1, K2, T, σ):
    """Payoff dla Bull Put Spread (kredytowy) - K1 niższy, K2 wyższy"""
    p1 = bs(S, K1, T, R, σ, "put")["cena"]
    p2 = bs(S, K2, T, R, σ, "put")["cena"]
    kredyt = p2 - p1
    g1, g2 = bs(S, K1, T, R, σ, "put"), bs(S, K2, T, R, σ, "put")
    return kredyt - np.maximum(K2 - x, 0) + np.maximum(K1 - x, 0), -kredyt, {
        "delta": -(g2["delta"] - g1["delta"]),
        "theta": -(g2["theta"] - g1["theta"]),
        "vega": -(g2["vega"] - g1["vega"])
    }

def payoff_bear_call_spread(x, S, K1, K2, T, σ):
    """Payoff dla Bear Call Spread (kredytowy) - K1 niższy, K2 wyższy"""
    c1 = bs(S, K1, T, R, σ, "call")["cena"]
    c2 = bs(S, K2, T, R, σ, "call")["cena"]
    kredyt = c1 - c2
    g1, g2 = bs(S, K1, T, R, σ, "call"), bs(S, K2, T, R, σ, "call")
    return kredyt - np.maximum(x - K1, 0) + np.maximum(x - K2, 0), -kredyt, {
        "delta": -(g1["delta"] - g2["delta"]),
        "theta": -(g1["theta"] - g2["theta"]),
        "vega": -(g1["vega"] - g2["vega"])
    }

def payoff_long_straddle(x, S, K, T, σ):
    """Payoff dla Long Straddle"""
    c = bs(S, K, T, R, σ, "call")
    p = bs(S, K, T, R, σ, "put")
    koszt = c["cena"] + p["cena"]
    return np.maximum(x - K, 0) + np.maximum(K - x, 0) - koszt, koszt, {
        "delta": c["delta"] + p["delta"],
        "theta": c["theta"] + p["theta"],
        "vega": c["vega"] + p["vega"]
    }

def payoff_long_strangle(x, S, K_put, K_call, T, σ):
    """Payoff dla Long Strangle"""
    c = bs(S, K_call, T, R, σ, "call")
    p = bs(S, K_put, T, R, σ, "put")
    koszt = c["cena"] + p["cena"]
    return np.maximum(x - K_call, 0) + np.maximum(K_put - x, 0) - koszt, koszt, {
        "delta": c["delta"] + p["delta"],
        "theta": c["theta"] + p["theta"],
        "vega": c["vega"] + p["vega"]
    }

def payoff_iron_condor(x, S, K1, K2, K3, K4, T, σ):
    """Payoff dla Short Iron Condor (K1<K2<K3<K4)"""
    # Kupno put K1, sprzedaż put K2, sprzedaż call K3, kupno call K4
    p1 = bs(S, K1, T, R, σ, "put")["cena"]
    p2 = bs(S, K2, T, R, σ, "put")["cena"]
    c3 = bs(S, K3, T, R, σ, "call")["cena"]
    c4 = bs(S, K4, T, R, σ, "call")["cena"]
    kredyt = (p2 - p1) + (c3 - c4)
    
    payoff = (kredyt 
              - np.maximum(K2 - x, 0) + np.maximum(K1 - x, 0)  # Put spread
              - np.maximum(x - K3, 0) + np.maximum(x - K4, 0))  # Call spread
    return payoff, -kredyt, {"delta": 0, "theta": 0.05, "vega": -0.1}

def payoff_iron_butterfly(x, S, K_wing_low, K_mid, K_wing_high, T, σ):
    """Payoff dla Short Iron Butterfly"""
    p_low = bs(S, K_wing_low, T, R, σ, "put")["cena"]
    p_mid = bs(S, K_mid, T, R, σ, "put")["cena"]
    c_mid = bs(S, K_mid, T, R, σ, "call")["cena"]
    c_high = bs(S, K_wing_high, T, R, σ, "call")["cena"]
    
    kredyt = (p_mid - p_low) + (c_mid - c_high)
    
    payoff = (kredyt
              - np.maximum(K_mid - x, 0) + np.maximum(K_wing_low - x, 0)
              - np.maximum(x - K_mid, 0) + np.maximum(x - K_wing_high, 0))
    return payoff, -kredyt, {"delta": 0, "theta": 0.08, "vega": -0.15}

def payoff_long_butterfly(x, S, K1, K2, K3, T, σ):
    """Payoff dla Long Call Butterfly (K1 < K2 < K3)"""
    c1 = bs(S, K1, T, R, σ, "call")["cena"]
    c2 = bs(S, K2, T, R, σ, "call")["cena"]
    c3 = bs(S, K3, T, R, σ, "call")["cena"]
    koszt = c1 - 2*c2 + c3
    
    payoff = (np.maximum(x - K1, 0) 
              - 2 * np.maximum(x - K2, 0) 
              + np.maximum(x - K3, 0) 
              - koszt)
    return payoff, koszt, {"delta": 0, "theta": 0.02, "vega": -0.05}

# ══════════════════════════════════════════════════════════════════════════════
# KOMPONENTY UI
# ══════════════════════════════════════════════════════════════════════════════
def rysuj_wykres(x, y, tytul, S, breakevens=None):
    """Uniwersalna funkcja do rysowania wykresu payoff"""
    fig = go.Figure()
    
    # Obszary zysku/straty
    zysk = np.where(y > 0, y, 0)
    strata = np.where(y < 0, y, 0)
    
    fig.add_trace(go.Scatter(x=x, y=zysk, fill='tozeroy', name='Zysk', 
                              line=dict(color='#00FF88', width=0), fillcolor='rgba(0,255,136,0.3)'))
    fig.add_trace(go.Scatter(x=x, y=strata, fill='tozeroy', name='Strata',
                              line=dict(color='#FF4444', width=0), fillcolor='rgba(255,68,68,0.3)'))
    
    # Linia payoff
    fig.add_trace(go.Scatter(x=x, y=y, name='Payoff', 
                              line=dict(color='#FFFFFF', width=3)))
    
    # Linia zerowa
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Aktualna cena
    fig.add_vline(x=S, line_dash="dot", line_color="#FFD700", opacity=0.7,
                  annotation_text=f"Cena: {S:.0f}", annotation_position="top")
    
    # Breakeven points
    if breakevens:
        for be in breakevens:
            fig.add_vline(x=be, line_dash="dash", line_color="#00BFFF", opacity=0.5,
                          annotation_text=f"BE: {be:.2f}", annotation_position="bottom")
    
    fig.update_layout(
        template="plotly_dark",
        title=dict(text=tytul, font=dict(size=20)),
        xaxis_title="Cena aktywa w dniu wygaśnięcia",
        yaxis_title="Zysk / Strata (na kontrakt)",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=500,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def panel_edukacyjny(strategia: Strategia, greeks: dict, koszt: float):
    """Wyświetla panel z informacjami edukacyjnymi"""
    
    st.markdown("---")
    st.subheader("📚 Panel Edukacyjny")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Kiedy używać tej strategii?")
        st.markdown(strategia.kiedy)
        
        st.markdown("### 🏗️ Konstrukcja")
        st.info(strategia.konstrukcja)
    
    with col2:
        st.markdown("### 📊 Profil Zysku/Straty")
        st.success(f"**Max Zysk:** {strategia.max_zysk}")
        st.error(f"**Max Strata:** {strategia.max_strata}")
        st.warning(f"**Breakeven:** {strategia.breakeven}")
    
    st.markdown("---")
    st.markdown("### 🇬🇷 Współczynniki Greckie - Twoje Czujniki Ryzyka")
    
    g1, g2, g3, g4 = st.columns(4)
    
    with g1:
        delta_color = "🟢" if greeks.get("delta", 0) > 0 else "🔴" if greeks.get("delta", 0) < 0 else "⚪"
        st.metric("Delta Δ", f"{greeks.get('delta', 0):.3f}", 
                  help="Ile zyskujesz/tracisz gdy cena zmieni się o 1 PLN")
        st.caption(f"{delta_color} {'Zarabiasz na wzroście' if greeks.get('delta', 0) > 0 else 'Zarabiasz na spadku' if greeks.get('delta', 0) < 0 else 'Neutralny'}")
    
    with g2:
        theta_val = greeks.get('theta', 0) * 100
        theta_color = "🟢" if theta_val > 0 else "🔴"
        st.metric("Theta Θ", f"{theta_val:.2f} PLN/dzień",
                  help="Ile tracisz/zyskujesz każdego dnia przez upływ czasu")
        st.caption(f"{theta_color} {'Czas pracuje DLA ciebie' if theta_val > 0 else 'Czas pracuje PRZECIW tobie'}")
    
    with g3:
        vega_val = greeks.get('vega', 0) * 100
        vega_color = "🟢" if vega_val > 0 else "🔴"
        st.metric("Vega V", f"{vega_val:.2f} PLN/%IV",
                  help="Ile zyskujesz/tracisz gdy zmienność wzrośnie o 1%")
        st.caption(f"{vega_color} {'Korzystasz ze wzrostu strachu' if vega_val > 0 else 'Korzystasz ze spokoju'}")
    
    with g4:
        if koszt > 0:
            st.metric("💰 Koszt wejścia", f"{koszt:.2f} PLN", help="Ile płacisz za otwarcie pozycji")
            st.caption("Debet - płacisz z góry")
        else:
            st.metric("💰 Kredyt", f"{-koszt:.2f} PLN", help="Ile otrzymujesz za otwarcie pozycji")
            st.caption("Kredyt - dostajesz pieniądze!")

# ══════════════════════════════════════════════════════════════════════════════
# GŁÓWNA APLIKACJA
# ══════════════════════════════════════════════════════════════════════════════
def main():
    # Nagłówek
    st.title("🎓 Akademia Opcji")
    st.markdown("*Interaktywna platforma do nauki strategii opcyjnych*")
    
    # Sidebar - parametry
    st.sidebar.header("⚙️ Parametry Rynkowe")
    S = st.sidebar.number_input("📈 Cena aktywa (S)", value=100.0, min_value=1.0, step=1.0)
    vol = st.sidebar.slider("🌪️ Zmienność IV (%)", 5, 150, 30) / 100
    dni = st.sidebar.slider("📅 Dni do wygaśnięcia", 1, 365, 30)
    T = dni / 365
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📖 Legenda IV")
    st.sidebar.markdown("""
    - **< 20%**: Niska (spokojny rynek)
    - **20-40%**: Normalna
    - **40-60%**: Podwyższona
    - **> 60%**: Wysoka (strach/panika)
    """)
    
    # Wybór strategii
    st.markdown("---")
    
    # Grupowanie strategii według kategorii
    kategorie = {}
    for nazwa, strat in STRATEGIE.items():
        kat = strat.kategoria
        if kat not in kategorie:
            kategorie[kat] = []
        kategorie[kat].append(nazwa)
    
    col_wybor1, col_wybor2 = st.columns([2, 3])
    
    with col_wybor1:
        wybrana_kategoria = st.selectbox("📂 Kategoria", list(kategorie.keys()))
    
    with col_wybor2:
        wybrana_strategia = st.selectbox("📋 Strategia", kategorie[wybrana_kategoria])
    
    strategia = STRATEGIE[wybrana_strategia]
    
    # Nagłówek strategii
    st.markdown(f"## {strategia.poziom} {strategia.nazwa}")
    st.markdown(f"*{strategia.opis}*")
    
    # Parametry specyficzne dla strategii
    st.markdown("### ⚙️ Parametry Strategii")
    
    x = np.linspace(S * 0.6, S * 1.4, 200)
    
    # Dynamiczne UI w zależności od strategii
    if wybrana_strategia == "Long Call":
        K = st.slider("Strike (K)", float(S * 0.8), float(S * 1.2), float(S * 1.05))
        y, koszt, greeks = payoff_long_call(x, S, K, T, vol)
        be = [K + koszt]
        
    elif wybrana_strategia == "Long Put":
        K = st.slider("Strike (K)", float(S * 0.8), float(S * 1.2), float(S * 0.95))
        y, koszt, greeks = payoff_long_put(x, S, K, T, vol)
        be = [K - koszt]
        
    elif wybrana_strategia == "Covered Call":
        K = st.slider("Strike sprzedawanego Call", float(S), float(S * 1.3), float(S * 1.1))
        y, koszt, greeks = payoff_covered_call(x, S, K, T, vol)
        be = [S - koszt]
        
    elif wybrana_strategia == "Protective Put":
        K = st.slider("Strike kupowanego Put", float(S * 0.7), float(S), float(S * 0.95))
        y, koszt, greeks = payoff_protective_put(x, S, K, T, vol)
        be = [S + koszt]
        
    elif wybrana_strategia == "Collar":
        col1, col2 = st.columns(2)
        with col1:
            K_put = st.slider("Strike Put (ochrona)", float(S * 0.7), float(S), float(S * 0.95))
        with col2:
            K_call = st.slider("Strike Call (limit)", float(S), float(S * 1.3), float(S * 1.10))
        y, koszt, greeks = payoff_collar(x, S, K_put, K_call, T, vol)
        be = [S - koszt] if koszt != 0 else [S]
        
    elif wybrana_strategia == "Bull Call Spread":
        col1, col2 = st.columns(2)
        with col1:
            K1 = st.slider("Strike kupowanego Call", float(S * 0.8), float(S * 1.1), float(S))
        with col2:
            K2 = st.slider("Strike sprzedawanego Call", float(K1), float(S * 1.3), float(S * 1.1))
        y, koszt, greeks = payoff_bull_call_spread(x, S, K1, K2, T, vol)
        be = [K1 + koszt]
        
    elif wybrana_strategia == "Bear Put Spread":
        col1, col2 = st.columns(2)
        with col1:
            K1 = st.slider("Strike sprzedawanego Put", float(S * 0.7), float(S), float(S * 0.9))
        with col2:
            K2 = st.slider("Strike kupowanego Put", float(K1), float(S * 1.2), float(S))
        y, koszt, greeks = payoff_bear_put_spread(x, S, K1, K2, T, vol)
        be = [K2 - koszt]
        
    elif wybrana_strategia == "Bull Put Spread":
        col1, col2 = st.columns(2)
        with col1:
            K1 = st.slider("Strike kupowanego Put (niższy)", float(S * 0.7), float(S * 0.95), float(S * 0.9))
        with col2:
            K2 = st.slider("Strike sprzedawanego Put (wyższy)", float(K1), float(S * 1.1), float(S))
        y, koszt, greeks = payoff_bull_put_spread(x, S, K1, K2, T, vol)
        be = [K2 + koszt]  # koszt jest ujemny (kredyt)
        
    elif wybrana_strategia == "Bear Call Spread":
        col1, col2 = st.columns(2)
        with col1:
            K1 = st.slider("Strike sprzedawanego Call (niższy)", float(S * 0.9), float(S * 1.1), float(S))
        with col2:
            K2 = st.slider("Strike kupowanego Call (wyższy)", float(K1), float(S * 1.3), float(S * 1.1))
        y, koszt, greeks = payoff_bear_call_spread(x, S, K1, K2, T, vol)
        be = [K1 - koszt]  # koszt jest ujemny (kredyt)
        
    elif wybrana_strategia == "Long Straddle":
        K = st.slider("Strike (ATM)", float(S * 0.9), float(S * 1.1), float(S))
        y, koszt, greeks = payoff_long_straddle(x, S, K, T, vol)
        be = [K - koszt, K + koszt]
        
    elif wybrana_strategia == "Long Strangle":
        col1, col2 = st.columns(2)
        with col1:
            K_put = st.slider("Strike Put (OTM)", float(S * 0.7), float(S * 0.95), float(S * 0.9))
        with col2:
            K_call = st.slider("Strike Call (OTM)", float(S * 1.05), float(S * 1.3), float(S * 1.1))
        y, koszt, greeks = payoff_long_strangle(x, S, K_put, K_call, T, vol)
        p_prem = bs(S, K_put, T, R, vol, "put")["cena"]
        c_prem = bs(S, K_call, T, R, vol, "call")["cena"]
        be = [K_put - koszt, K_call + koszt]
        
    elif wybrana_strategia == "Iron Condor":
        st.markdown("*Ustaw 4 strike'i: K1 < K2 < K3 < K4*")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            K1 = st.number_input("K1 (kupno put)", value=float(S * 0.85))
        with col2:
            K2 = st.number_input("K2 (sprzedaż put)", value=float(S * 0.95))
        with col3:
            K3 = st.number_input("K3 (sprzedaż call)", value=float(S * 1.05))
        with col4:
            K4 = st.number_input("K4 (kupno call)", value=float(S * 1.15))
        y, koszt, greeks = payoff_iron_condor(x, S, K1, K2, K3, K4, T, vol)
        be = [K2 + koszt, K3 - koszt]  # koszt jest ujemny
        
    elif wybrana_strategia == "Iron Butterfly":
        col1, col2, col3 = st.columns(3)
        with col1:
            K_low = st.number_input("K niskie (kupno put)", value=float(S * 0.9))
        with col2:
            K_mid = st.number_input("K środkowe (sprzedaż)", value=float(S))
        with col3:
            K_high = st.number_input("K wysokie (kupno call)", value=float(S * 1.1))
        y, koszt, greeks = payoff_iron_butterfly(x, S, K_low, K_mid, K_high, T, vol)
        be = [K_mid + koszt, K_mid - koszt]
        
    elif wybrana_strategia == "Long Butterfly":
        col1, col2, col3 = st.columns(3)
        with col1:
            K1 = st.number_input("K1 (kupno call ITM)", value=float(S * 0.95))
        with col2:
            K2 = st.number_input("K2 (sprzedaż 2x call ATM)", value=float(S))
        with col3:
            K3 = st.number_input("K3 (kupno call OTM)", value=float(S * 1.05))
        y, koszt, greeks = payoff_long_butterfly(x, S, K1, K2, K3, T, vol)
        be = [K1 + koszt, K3 - koszt]
    
    # Wykres
    st.markdown("### 📈 Wykres Payoff")
    fig = rysuj_wykres(x, y * 100, f"Profil Zysku/Straty: {wybrana_strategia}", S, be)
    st.plotly_chart(fig, use_container_width=True)
    
    # Panel edukacyjny
    panel_edukacyjny(strategia, greeks, koszt)
    
    # Scenariusze
    st.markdown("---")
    st.markdown("### 🎭 Analiza Scenariuszy")
    
    scenariusze = {
        "📉 Silny spadek (-20%)": S * 0.8,
        "📉 Umiarkowany spadek (-10%)": S * 0.9,
        "➡️ Bez zmian": S,
        "📈 Umiarkowany wzrost (+10%)": S * 1.1,
        "📈 Silny wzrost (+20%)": S * 1.2
    }
    
    cols = st.columns(5)
    for i, (nazwa, cena) in enumerate(scenariusze.items()):
        idx = np.argmin(np.abs(x - cena))
        wynik = y[idx] * 100
        with cols[i]:
            if wynik > 0:
                st.success(f"**{nazwa}**\n\n💰 +{wynik:.0f} PLN")
            elif wynik < 0:
                st.error(f"**{nazwa}**\n\n💸 {wynik:.0f} PLN")
            else:
                st.info(f"**{nazwa}**\n\n⚖️ {wynik:.0f} PLN")
    
    # Stopka
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
        <p>⚠️ <strong>Ostrzeżenie o ryzyku:</strong> Handel opcjami wiąże się ze znacznym ryzykiem straty. 
        Niektóre strategie mogą generować straty przekraczające początkową inwestycję.</p>
        <p>🎓 Akademia Opcji - Edukacyjne narzędzie do nauki strategii opcyjnych</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
