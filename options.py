"""
🎓 AKADEMIA OPCJI v2.0 - KOMPLETNA PLATFORMA EDUKACYJNA
Wszystkie strategie opcyjne z pełnym kontekstem "kiedy używać"
"""
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from dataclasses import dataclass

# ══════════════════════════════════════════════════════════════════════════════
# KONFIGURACJA
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="🎓 Akademia Opcji v2.0", page_icon="📈", layout="wide")
R = 0.045  # Stopa wolna od ryzyka

# ══════════════════════════════════════════════════════════════════════════════
# MODEL BLACKA-SCHOLESA
# ══════════════════════════════════════════════════════════════════════════════
def bs(S, K, T, r, σ, typ="call"):
    """Model Blacka-Scholesa - wycena i Greeks"""
    T = max(T, 1e-6)
    sqrt_T = np.sqrt(T)
    d1 = (np.log(S / K) + (r + 0.5 * σ**2) * T) / (σ * sqrt_T)
    d2 = d1 - σ * sqrt_T
    Nd1, Nd2, nd1 = norm.cdf(d1), norm.cdf(d2), norm.pdf(d1)
    exp_rT = np.exp(-r * T)
    
    if typ == "call":
        cena = S * Nd1 - K * exp_rT * Nd2
        delta = Nd1
        theta_cdf = Nd2
    else:
        cena = K * exp_rT * (1 - Nd2) - S * (1 - Nd1)
        delta = Nd1 - 1
        theta_cdf = norm.cdf(-d2)
    
    gamma = nd1 / (S * σ * sqrt_T)
    vega = S * nd1 * sqrt_T / 100
    theta = (-(S * nd1 * σ) / (2 * sqrt_T) - r * K * exp_rT * theta_cdf) / 365
    
    return {"cena": cena, "delta": delta, "gamma": gamma, "theta": theta, "vega": vega}

# ══════════════════════════════════════════════════════════════════════════════
# DEFINICJE WSZYSTKICH STRATEGII
# ══════════════════════════════════════════════════════════════════════════════
@dataclass
class Strategia:
    nazwa: str
    kategoria: str
    opis: str
    kiedy: str
    konstrukcja: str
    max_zysk: str
    max_strata: str
    breakeven: str
    greeks: str
    poziom: str
    uwagi: str = ""

STRATEGIE = {
    # ═══════════════════════════════════════════════════════════════════════════
    # 📗 STRATEGIE PODSTAWOWE - SINGLE LEG
    # ═══════════════════════════════════════════════════════════════════════════
    "Long Call": Strategia(
        nazwa="Long Call",
        kategoria="📗 Podstawowe",
        opis="Kupno opcji call - najprostsza gra na wzrost ceny.",
        kiedy="""✅ Oczekujesz SILNEGO wzrostu ceny
✅ Chcesz ograniczyć ryzyko do premii
✅ Przed pozytywnymi wydarzeniami (wyniki, FDA)
✅ Przy NISKIEJ IV (tanie opcje!)
❌ NIE używaj przy wysokiej IV - przepłacasz
❌ NIE przy oczekiwaniu małego ruchu""",
        konstrukcja="Kupno 1 CALL",
        max_zysk="♾️ Nieograniczony",
        max_strata="Zapłacona premia",
        breakeven="Strike + Premia",
        greeks="Delta ⬆️ dodatnia | Theta ⬇️ ujemna | Vega ⬆️ dodatnia",
        poziom="🟢",
        uwagi="Najprostsza strategia byka. Czas pracuje przeciwko Tobie!"
    ),
    
    "Long Put": Strategia(
        nazwa="Long Put",
        kategoria="📗 Podstawowe",
        opis="Kupno opcji put - najprostsza gra na spadek ceny.",
        kiedy="""✅ Oczekujesz SILNEGO spadku ceny
✅ Chcesz zabezpieczyć portfel akcji
✅ Przed negatywnymi wydarzeniami
✅ Przy NISKIEJ IV
❌ NIE przy wysokiej IV
❌ NIE jako długoterminowe zabezpieczenie (drogo!)""",
        konstrukcja="Kupno 1 PUT",
        max_zysk="Strike - Premia (cena może spaść do 0)",
        max_strata="Zapłacona premia",
        breakeven="Strike - Premia",
        greeks="Delta ⬇️ ujemna | Theta ⬇️ ujemna | Vega ⬆️ dodatnia",
        poziom="🟢",
        uwagi="Ubezpieczenie portfela. Drożeje gdy rynek panikuje."
    ),
    
    "Short Call (Naked)": Strategia(
        nazwa="Short Call (Naked)",
        kategoria="📗 Podstawowe",
        opis="Sprzedaż opcji call bez posiadania akcji - bardzo ryzykowne!",
        kiedy="""✅ Oczekujesz spadku lub stagnacji
✅ Przy WYSOKIEJ IV (wysoka premia)
✅ Masz duży kapitał na depozyt
⚠️ TYLKO dla doświadczonych!
❌ NIGDY przed ważnymi wydarzeniami
❌ NIE bez zrozumienia ryzyka!""",
        konstrukcja="Sprzedaż 1 CALL (bez akcji)",
        max_zysk="Otrzymana premia",
        max_strata="♾️ NIEOGRANICZONA! (cena może rosnąć w nieskończoność)",
        breakeven="Strike + Premia",
        greeks="Delta ⬇️ ujemna | Theta ⬆️ dodatnia | Vega ⬇️ ujemna",
        poziom="🔴",
        uwagi="⚠️ EKSTREMALNE RYZYKO! Możesz stracić więcej niż masz na koncie!"
    ),
    
    "Short Put (Cash-Secured)": Strategia(
        nazwa="Short Put (Cash-Secured)",
        kategoria="📗 Podstawowe",
        opis="Sprzedaż opcji put z gotówką na koncie - 'kupowanie akcji z rabatem'.",
        kiedy="""✅ CHCESZ kupić akcje, ale taniej
✅ Lubisz spółkę i chcesz ją posiadać
✅ Przy WYSOKIEJ IV (wysoka premia)
✅ Rynek boczny lub lekko wzrostowy
✅ Masz gotówkę na kupno 100 akcji
❌ NIE jeśli nie chcesz posiadać akcji!
❌ NIE przed spadkowym rynkiem""",
        konstrukcja="Sprzedaż 1 PUT + Gotówka = Strike × 100",
        max_zysk="Otrzymana premia",
        max_strata="Strike - Premia (jeśli akcja spadnie do 0)",
        breakeven="Strike - Premia",
        greeks="Delta ⬆️ dodatnia | Theta ⬆️ dodatnia | Vega ⬇️ ujemna",
        poziom="🟢",
        uwagi="""💡 STRATEGIA WARRENA BUFFETTA!
Scenariusz 1: Cena > Strike → zatrzymujesz premię (dochód!)
Scenariusz 2: Cena < Strike → kupujesz akcje po Strike-Premia (rabat!)
WIN-WIN jeśli lubisz spółkę!"""
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 💰 STRATEGIE DOCHODOWE
    # ═══════════════════════════════════════════════════════════════════════════
    "Covered Call": Strategia(
        nazwa="Covered Call",
        kategoria="💰 Dochodowe",
        opis="Posiadasz akcje + sprzedajesz call. Generujesz dochód w zamian za limit wzrostu.",
        kiedy="""✅ Posiadasz akcje długoterminowo
✅ Oczekujesz ruchu bocznego/małego wzrostu
✅ Chcesz generować miesięczny dochód
✅ Przy WYSOKIEJ IV (wyższa premia!)
✅ Na akcjach które nie chcesz sprzedać
❌ NIE przy oczekiwaniu silnego wzrostu
❌ NIE tuż przed dywidendą (ryzyko assignment)""",
        konstrukcja="100 akcji + Sprzedaż 1 CALL OTM",
        max_zysk="(Strike - Cena akcji) + Premia",
        max_strata="Cena akcji - Premia (spadek do 0)",
        breakeven="Cena zakupu akcji - Premia",
        greeks="Delta ⬆️ mała | Theta ⬆️ dodatnia | Vega ⬇️ ujemna",
        poziom="🟢",
        uwagi="Najpopularniejsza strategia dochodowa. 'Wynajem' akcji co miesiąc."
    ),
    
    "Covered Put": Strategia(
        nazwa="Covered Put",
        kategoria="💰 Dochodowe",
        opis="Masz krótką pozycję w akcjach + sprzedajesz put. Dochód przy spadku.",
        kiedy="""✅ Masz SHORT na akcjach
✅ Oczekujesz spadku lub stagnacji
✅ Przy WYSOKIEJ IV
❌ NIE przy oczekiwaniu silnego spadku
❌ Mniej popularna strategia""",
        konstrukcja="Short 100 akcji + Sprzedaż 1 PUT OTM",
        max_zysk="(Cena sprzedaży - Strike) + Premia",
        max_strata="♾️ Nieograniczona (cena może rosnąć)",
        breakeven="Cena sprzedaży akcji + Premia",
        greeks="Delta ⬇️ ujemna | Theta ⬆️ dodatnia",
        poziom="🟡",
        uwagi="Lustrzane odbicie covered call. Dla shortujących."
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 🛡️ STRATEGIE ZABEZPIECZAJĄCE
    # ═══════════════════════════════════════════════════════════════════════════
    "Protective Put": Strategia(
        nazwa="Protective Put",
        kategoria="🛡️ Zabezpieczające",
        opis="Masz akcje + kupujesz put jako ubezpieczenie od spadku.",
        kiedy="""✅ Masz zysk na akcjach i chcesz go chronić
✅ Przed niepewnymi wydarzeniami (wybory, wyniki)
✅ Chcesz zachować potencjał wzrostu
✅ Przy NISKIEJ IV (tańsze ubezpieczenie)
❌ Kosztowne przy wysokiej IV
❌ Nie na długi termin (theta zjada)""",
        konstrukcja="100 akcji + Kupno 1 PUT",
        max_zysk="♾️ Nieograniczony",
        max_strata="(Cena akcji - Strike) + Premia",
        breakeven="Cena akcji + Premia",
        greeks="Delta ⬆️ z limitem strat | Theta ⬇️",
        poziom="🟢",
        uwagi="Polisa ubezpieczeniowa na akcje. Spokojny sen."
    ),
    
    "Protective Call": Strategia(
        nazwa="Protective Call",
        kategoria="🛡️ Zabezpieczające",
        opis="Masz SHORT + kupujesz call jako ochrona przed wzrostem.",
        kiedy="""✅ Masz krótką pozycję w akcjach
✅ Chcesz ograniczyć ryzyko short squeeze
✅ Przed wydarzeniami mogącymi wywołać wzrost
❌ Kosztowne przy wysokiej IV""",
        konstrukcja="Short 100 akcji + Kupno 1 CALL",
        max_zysk="Cena sprzedaży - Premia (spadek do 0)",
        max_strata="(Strike - Cena sprzedaży) + Premia",
        breakeven="Cena sprzedaży - Premia",
        greeks="Delta ⬇️ z limitem strat | Theta ⬇️",
        poziom="🟡",
        uwagi="Ubezpieczenie dla shortujących."
    ),
    
    "Collar (Zero-Cost)": Strategia(
        nazwa="Collar (Zero-Cost)",
        kategoria="🛡️ Zabezpieczające",
        opis="Akcje + kupno put + sprzedaż call. Ochrona za darmo, ale z limitem wzrostu.",
        kiedy="""✅ Chcesz zabezpieczyć zyski BEZ KOSZTU
✅ Masz duży niezrealizowany zysk na akcjach
✅ Przed niepewnymi wydarzeniami
✅ Akceptujesz ograniczenie dalszych zysków
❌ NIE gdy oczekujesz silnego wzrostu""",
        konstrukcja="100 akcji + Kupno PUT OTM + Sprzedaż CALL OTM",
        max_zysk="Strike call - Cena akcji",
        max_strata="Cena akcji - Strike put",
        breakeven="Cena akcji (przy zero-cost)",
        greeks="Delta ⬆️ ograniczona | Theta ≈ 0 | Vega ≈ 0",
        poziom="🟡",
        uwagi="Darmowe ubezpieczenie! Popularny przy dużych zyskach."
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 📊 SPREADY PIONOWE (VERTICAL SPREADS)
    # ═══════════════════════════════════════════════════════════════════════════
    "Bull Call Spread": Strategia(
        nazwa="Bull Call Spread",
        kategoria="📊 Spready",
        opis="Kupno call + sprzedaż wyższego call. Tańszy zakład na wzrost.",
        kiedy="""✅ Oczekujesz UMIARKOWANEGO wzrostu
✅ Chcesz tańszą alternatywę dla long call
✅ Znasz poziom docelowy (target)
✅ Przy WYSOKIEJ IV (sprzedaż offset)
❌ NIE przy oczekiwaniu silnego wzrostu""",
        konstrukcja="Kupno CALL niższy K + Sprzedaż CALL wyższy K",
        max_zysk="Różnica strike'ów - Koszt netto",
        max_strata="Zapłacona premia netto",
        breakeven="Niższy strike + Koszt",
        greeks="Delta ⬆️ umiarkowana | Theta ≈ neutralna",
        poziom="🟡",
        uwagi="Spread debetowy. Płacisz z góry, ograniczony zysk."
    ),
    
    "Bear Put Spread": Strategia(
        nazwa="Bear Put Spread",
        kategoria="📊 Spready",
        opis="Kupno put + sprzedaż niższego put. Tańszy zakład na spadek.",
        kiedy="""✅ Oczekujesz UMIARKOWANEGO spadku
✅ Chcesz tańszą alternatywę dla long put
✅ Znasz poziom docelowy
✅ Przy WYSOKIEJ IV
❌ NIE przy oczekiwaniu silnego spadku""",
        konstrukcja="Kupno PUT wyższy K + Sprzedaż PUT niższy K",
        max_zysk="Różnica strike'ów - Koszt netto",
        max_strata="Zapłacona premia netto",
        breakeven="Wyższy strike - Koszt",
        greeks="Delta ⬇️ umiarkowana | Theta ≈ neutralna",
        poziom="🟡",
        uwagi="Spread debetowy niedźwiedzi."
    ),
    
    "Bull Put Spread (Credit)": Strategia(
        nazwa="Bull Put Spread (Credit)",
        kategoria="📊 Spready",
        opis="Sprzedaż put + kupno niższego put. Dostajesz premię, zarabiasz gdy NIE spada.",
        kiedy="""✅ Oczekujesz, że cena NIE SPADNIE
✅ Chcesz otrzymać premię z góry
✅ Przy WYSOKIEJ IV (wyższe premie!)
✅ Rynek boczny lub wzrostowy
❌ NIE przed negatywnymi wydarzeniami""",
        konstrukcja="Sprzedaż PUT wyższy K + Kupno PUT niższy K",
        max_zysk="Otrzymana premia netto",
        max_strata="Różnica strike'ów - Premia",
        breakeven="Wyższy strike - Premia",
        greeks="Delta ⬆️ | Theta ⬆️ KORZYSTNA!",
        poziom="🟡",
        uwagi="Spread kredytowy - dostajesz pieniądze na start!"
    ),
    
    "Bear Call Spread (Credit)": Strategia(
        nazwa="Bear Call Spread (Credit)",
        kategoria="📊 Spready",
        opis="Sprzedaż call + kupno wyższego call. Dostajesz premię, zarabiasz gdy NIE rośnie.",
        kiedy="""✅ Oczekujesz, że cena NIE WZROŚNIE
✅ Chcesz otrzymać premię z góry
✅ Przy WYSOKIEJ IV
✅ Rynek boczny lub spadkowy
❌ NIE przed pozytywnymi wydarzeniami""",
        konstrukcja="Sprzedaż CALL niższy K + Kupno CALL wyższy K",
        max_zysk="Otrzymana premia netto",
        max_strata="Różnica strike'ów - Premia",
        breakeven="Niższy strike + Premia",
        greeks="Delta ⬇️ | Theta ⬆️ KORZYSTNA!",
        poziom="🟡",
        uwagi="Spread kredytowy niedźwiedzi."
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 🌪️ STRATEGIE NA ZMIENNOŚĆ - KUPOWANIE
    # ═══════════════════════════════════════════════════════════════════════════
    "Long Straddle": Strategia(
        nazwa="Long Straddle",
        kategoria="🌪️ Zmienność",
        opis="Kupno call + put z tym samym strike. Zarabiasz na DUŻYM ruchu w dowolnym kierunku.",
        kiedy="""✅ Przed WAŻNYMI wydarzeniami (wyniki, FDA, wybory)
✅ Oczekujesz DUŻEGO ruchu, nie wiesz w którą stronę
✅ Przy NISKIEJ IV (tanie opcje!)
✅ Gdy IV jest nienormalnie niska
❌ NIE przy wysokiej IV - przepłacasz!
❌ NIE przy stabilnym rynku""",
        konstrukcja="Kupno CALL ATM + Kupno PUT ATM (ten sam strike)",
        max_zysk="♾️ Nieograniczony",
        max_strata="Suma obu premii",
        breakeven="Strike ± Suma premii (DWA punkty!)",
        greeks="Delta ≈ 0 | Gamma ⬆️⬆️ | Theta ⬇️⬇️ | Vega ⬆️⬆️",
        poziom="🟡",
        uwagi="Gra na 'eksplozję'. Kierunek nieważny, ważna siła ruchu!"
    ),
    
    "Long Strangle": Strategia(
        nazwa="Long Strangle",
        kategoria="🌪️ Zmienność",
        opis="Kupno OTM call + OTM put. Tańszy straddle, ale wymaga większego ruchu.",
        kiedy="""✅ Oczekujesz BARDZO DUŻEGO ruchu
✅ Chcesz tańszą alternatywę dla straddle
✅ Przy NISKIEJ IV
❌ Wymaga jeszcze większego ruchu niż straddle""",
        konstrukcja="Kupno CALL OTM + Kupno PUT OTM",
        max_zysk="♾️ Nieograniczony",
        max_strata="Suma obu premii (niższa niż straddle)",
        breakeven="Put strike - Premia | Call strike + Premia",
        greeks="Delta ≈ 0 | Gamma ⬆️ | Theta ⬇️ | Vega ⬆️",
        poziom="🟡",
        uwagi="Tańszy zakład na 'eksplozję' w dowolnym kierunku."
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 😴 STRATEGIE NA NISKĄ ZMIENNOŚĆ - SPRZEDAWANIE
    # ═══════════════════════════════════════════════════════════════════════════
    "Short Straddle": Strategia(
        nazwa="Short Straddle",
        kategoria="😴 Neutralne",
        opis="Sprzedaż call + put z tym samym strike. Zarabiasz gdy cena NIE rusza się.",
        kiedy="""✅ Oczekujesz NISKIEJ zmienności
✅ Cena pozostanie blisko strike
✅ Przy WYSOKIEJ IV (wysokie premie!)
✅ Po dużych ruchach (powrót do średniej)
⚠️ RYZYKOWNE - nieograniczona strata!
❌ NIE przed ważnymi wydarzeniami""",
        konstrukcja="Sprzedaż CALL ATM + Sprzedaż PUT ATM",
        max_zysk="Suma obu premii",
        max_strata="♾️ NIEOGRANICZONA!",
        breakeven="Strike ± Suma premii",
        greeks="Delta ≈ 0 | Gamma ⬇️⬇️ | Theta ⬆️⬆️ | Vega ⬇️⬇️",
        poziom="🔴",
        uwagi="⚠️ BARDZO RYZYKOWNE! Wymaga aktywnego zarządzania."
    ),
    
    "Short Strangle": Strategia(
        nazwa="Short Strangle",
        kategoria="😴 Neutralne",
        opis="Sprzedaż OTM call + OTM put. Szerszy zakres zysku niż straddle.",
        kiedy="""✅ Oczekujesz ruchu bocznego
✅ Przy WYSOKIEJ IV
✅ Cena pozostanie w zakresie między strike'ami
⚠️ RYZYKOWNE - nieograniczona strata!
❌ NIE przed ważnymi wydarzeniami""",
        konstrukcja="Sprzedaż CALL OTM + Sprzedaż PUT OTM",
        max_zysk="Suma obu premii",
        max_strata="♾️ NIEOGRANICZONA!",
        breakeven="Put strike - Premia | Call strike + Premia",
        greeks="Delta ≈ 0 | Gamma ⬇️ | Theta ⬆️ | Vega ⬇️",
        poziom="🔴",
        uwagi="⚠️ RYZYKOWNE! Szerszy zakres niż straddle, ale wciąż niebezpieczne."
    ),
    
    "Iron Condor": Strategia(
        nazwa="Iron Condor",
        kategoria="😴 Neutralne",
        opis="KRÓL strategii dochodowych! 4 opcje tworzące tunel zysku. Zarabiasz na BRAKU ruchu.",
        kiedy="""✅ Oczekujesz NISKIEJ zmienności
✅ Rynek boczny, konsolidacja
✅ Przy WYSOKIEJ IV (wyższe premie!)
✅ Po dużych ruchach
✅ Regularny dochód co miesiąc
❌ NIE przed ważnymi wydarzeniami""",
        konstrukcja="Sprzedaż PUT + Kupno niższego PUT + Sprzedaż CALL + Kupno wyższego CALL",
        max_zysk="Otrzymana premia netto",
        max_strata="Szerokość spreadu - Premia (OGRANICZONA!)",
        breakeven="Wewnętrzne strike'i ± Premia",
        greeks="Delta ≈ 0 | Gamma ⬇️ | Theta ⬆️⬆️ SUPER! | Vega ⬇️",
        poziom="🟡",
        uwagi="""💰 Najpopularniejsza strategia dochodowa profesjonalistów!
Ograniczone ryzyko w obie strony. Czas pracuje DLA Ciebie."""
    ),
    
    "Iron Butterfly": Strategia(
        nazwa="Iron Butterfly",
        kategoria="😴 Neutralne",
        opis="Jak Iron Condor, ale wszystkie sprzedane opcje mają TEN SAM strike. Precyzyjny zakład.",
        kiedy="""✅ Oczekujesz, że cena będzie DOKŁADNIE przy strike
✅ Przy bardzo wysokiej IV
✅ Wyższa premia niż Iron Condor
❌ Węższy zakres zysku - wymaga precyzji""",
        konstrukcja="Kupno PUT OTM + Sprzedaż PUT ATM + Sprzedaż CALL ATM + Kupno CALL OTM",
        max_zysk="Otrzymana premia netto",
        max_strata="Szerokość skrzydła - Premia",
        breakeven="Środkowy strike ± Premia",
        greeks="Delta ≈ 0 | Gamma ⬇️⬇️ | Theta ⬆️ | Vega ⬇️",
        poziom="🔴",
        uwagi="Wyższa premia, ale wymaga większej precyzji."
    ),
    
    "Long Call Butterfly": Strategia(
        nazwa="Long Call Butterfly",
        kategoria="😴 Neutralne",
        opis="Kupno 1 call ITM + sprzedaż 2 call ATM + kupno 1 call OTM. Niski koszt, precyzyjny zakład.",
        kiedy="""✅ Oczekujesz, że cena będzie przy KONKRETNYM poziomie
✅ Niski koszt wejścia
✅ Blisko wygaśnięcia gdy znasz cel
❌ Wąski zakres zysku""",
        konstrukcja="Kupno CALL ITM + Sprzedaż 2× CALL ATM + Kupno CALL OTM",
        max_zysk="Szerokość - Koszt (przy środkowym strike)",
        max_strata="Zapłacona premia (niska!)",
        breakeven="Środkowy strike ± (Szerokość - Koszt)",
        greeks="Delta ≈ 0 | Gamma ⬇️ przy środku | Theta ⬆️",
        poziom="🔴",
        uwagi="Tani zakład na konkretną cenę w dniu wygaśnięcia."
    ),
    
    "Long Put Butterfly": Strategia(
        nazwa="Long Put Butterfly",
        kategoria="😴 Neutralne",
        opis="To samo co call butterfly, ale z opcjami put. Ten sam profil zysku.",
        kiedy="""✅ Oczekujesz konkretnej ceny
✅ Czasem lepsze ceny przy put
✅ Niski koszt""",
        konstrukcja="Kupno PUT OTM + Sprzedaż 2× PUT ATM + Kupno PUT ITM",
        max_zysk="Szerokość - Koszt",
        max_strata="Zapłacona premia",
        breakeven="Środkowy strike ± (Szerokość - Koszt)",
        greeks="Delta ≈ 0 | Theta ⬆️",
        poziom="🔴",
        uwagi="Alternatywa dla call butterfly - porównaj ceny."
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 📅 STRATEGIE KALENDARZOWE (CALENDAR SPREADS)
    # ═══════════════════════════════════════════════════════════════════════════
    "Calendar Call Spread": Strategia(
        nazwa="Calendar Call Spread",
        kategoria="📅 Kalendarzowe",
        opis="Sprzedaż call bliski termin + kupno call daleki termin. Zarabiasz na różnicy theta.",
        kiedy="""✅ Oczekujesz stabilnej ceny w krótkim terminie
✅ Chcesz wykorzystać szybszy rozpad czasu bliskiej opcji
✅ Przy niskiej IV (spodziewasz się wzrostu)
❌ Nie przy bardzo wysokiej IV""",
        konstrukcja="Sprzedaż CALL (bliski termin) + Kupno CALL (daleki termin) - TEN SAM strike",
        max_zysk="Różnica premii gdy cena = strike przy bliskim wygaśnięciu",
        max_strata="Zapłacona premia netto",
        breakeven="Złożony - zależy od IV",
        greeks="Delta ≈ 0 | Theta ⬆️ | Vega ⬆️ (zyskujesz na wzroście IV!)",
        poziom="🔴",
        uwagi="Gra na różnicę w rozpadzie czasowym. Zyskujesz też na wzroście IV!"
    ),
    
    "Calendar Put Spread": Strategia(
        nazwa="Calendar Put Spread",
        kategoria="📅 Kalendarzowe",
        opis="Sprzedaż put bliski termin + kupno put daleki termin.",
        kiedy="""✅ Oczekujesz stabilnej ceny
✅ Chcesz wykorzystać theta
✅ Alternatywa dla calendar call""",
        konstrukcja="Sprzedaż PUT (bliski termin) + Kupno PUT (daleki termin) - TEN SAM strike",
        max_zysk="Różnica premii przy strike",
        max_strata="Zapłacona premia netto",
        breakeven="Złożony",
        greeks="Delta ≈ 0 | Theta ⬆️ | Vega ⬆️",
        poziom="🔴",
        uwagi="Porównaj z calendar call - czasem lepsza cena."
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 📐 STRATEGIE DIAGONALNE
    # ═══════════════════════════════════════════════════════════════════════════
    "Diagonal Call Spread": Strategia(
        nazwa="Diagonal Call Spread",
        kategoria="📐 Diagonalne",
        opis="Calendar spread + vertical spread. Kupno dalekiego call ITM + sprzedaż bliskiego call OTM.",
        kiedy="""✅ Lekko byczy pogląd
✅ Chcesz generować dochód przez sprzedaż call
✅ Posiadasz LEAPS (długoterminowe opcje)
❌ Złożona strategia""",
        konstrukcja="Kupno CALL (daleki, niższy K) + Sprzedaż CALL (bliski, wyższy K)",
        max_zysk="Złożony - zależy od wielu czynników",
        max_strata="Ograniczona do debetu",
        breakeven="Złożony",
        greeks="Delta ⬆️ mała | Theta ⬆️ | Vega zmienna",
        poziom="🔴",
        uwagi="Poor Man's Covered Call - tańsza alternatywa dla covered call."
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ⚖️ RATIO SPREADS
    # ═══════════════════════════════════════════════════════════════════════════
    "Call Ratio Spread": Strategia(
        nazwa="Call Ratio Spread",
        kategoria="⚖️ Ratio",
        opis="Kupno 1 call + sprzedaż 2 call wyższych. Darmowy lub kredytowy zakład na umiarkowany wzrost.",
        kiedy="""✅ Oczekujesz UMIARKOWANEGO wzrostu do konkretnego poziomu
✅ Chcesz wejść za darmo lub z kredytem
⚠️ Ryzyko przy silnym wzroście!
❌ NIE gdy oczekujesz silnego wzrostu""",
        konstrukcja="Kupno 1 CALL + Sprzedaż 2 CALL (wyższy strike)",
        max_zysk="(Wyższy K - Niższy K) + Kredyt przy wyższym strike",
        max_strata="♾️ Nieograniczona powyżej górnego BE!",
        breakeven="Dwa punkty - dolny i górny",
        greeks="Delta zmienna | Gamma ujemna przy górze",
        poziom="🔴",
        uwagi="⚠️ Uwaga na nieograniczone ryzyko przy silnym wzroście!"
    ),
    
    "Put Ratio Spread": Strategia(
        nazwa="Put Ratio Spread",
        kategoria="⚖️ Ratio",
        opis="Kupno 1 put + sprzedaż 2 put niższych. Zakład na umiarkowany spadek.",
        kiedy="""✅ Oczekujesz UMIARKOWANEGO spadku
✅ Chcesz wejść tanio/za darmo
⚠️ Ryzyko przy silnym spadku!
❌ NIE przy oczekiwaniu krachu""",
        konstrukcja="Kupno 1 PUT + Sprzedaż 2 PUT (niższy strike)",
        max_zysk="(Wyższy K - Niższy K) + Kredyt przy niższym strike",
        max_strata="Może być duża przy silnym spadku",
        breakeven="Dwa punkty",
        greeks="Delta zmienna",
        poziom="🔴",
        uwagi="⚠️ Ryzyko przy krachu rynku!"
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 🎯 STRATEGIE SYNTETYCZNE
    # ═══════════════════════════════════════════════════════════════════════════
    "Synthetic Long Stock": Strategia(
        nazwa="Synthetic Long Stock",
        kategoria="🎯 Syntetyczne",
        opis="Kupno call + sprzedaż put (ten sam strike). Zachowuje się jak posiadanie akcji.",
        kiedy="""✅ Chcesz ekspozycję na akcje bez ich kupowania
✅ Niższy wymóg kapitałowy
✅ Przy opcjach europejskich
❌ Ryzyko przydziału przy amerykańskich""",
        konstrukcja="Kupno CALL ATM + Sprzedaż PUT ATM (ten sam strike)",
        max_zysk="♾️ Nieograniczony",
        max_strata="Strike (jak przy akcjach)",
        breakeven="Strike + Koszt netto",
        greeks="Delta ≈ 1 (jak akcje!)",
        poziom="🟡",
        uwagi="Tańszy sposób na ekspozycję na akcje. Put-Call Parity w praktyce."
    ),
    
    "Synthetic Short Stock": Strategia(
        nazwa="Synthetic Short Stock",
        kategoria="🎯 Syntetyczne",
        opis="Kupno put + sprzedaż call (ten sam strike). Zachowuje się jak short na akcjach.",
        kiedy="""✅ Chcesz shortować bez pożyczania akcji
✅ Gdy akcje są trudne do pożyczenia
✅ Bez ryzyka short squeeze""",
        konstrukcja="Kupno PUT ATM + Sprzedaż CALL ATM (ten sam strike)",
        max_zysk="Strike - Koszt netto",
        max_strata="♾️ Nieograniczona",
        breakeven="Strike - Kredyt netto",
        greeks="Delta ≈ -1 (jak short akcje!)",
        poziom="🟡",
        uwagi="Syntetyczny short bez pożyczania akcji."
    ),
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 🏦 STRATEGIE ARBITRAŻOWE
    # ═══════════════════════════════════════════════════════════════════════════
    "Box Spread": Strategia(
        nazwa="Box Spread",
        kategoria="🏦 Arbitraż",
        opis="Bull call spread + bear put spread. Syntetyczna pożyczka/lokata o znanym zwrocie.",
        kiedy="""✅ Arbitraż cenowy (instytucje)
✅ Syntetyczne pożyczanie środków
✅ Różnica powinna = stopa wolna od ryzyka
❌ Mało praktyczne dla indywidualnych""",
        konstrukcja="Kupno CALL K1 + Sprzedaż CALL K2 + Kupno PUT K2 + Sprzedaż PUT K1",
        max_zysk="Różnica strike'ów - Koszt (= stopa %)",
        max_strata="Brak (jeśli prawidłowo wycenione)",
        breakeven="Nie dotyczy",
        greeks="Wszystkie ≈ 0",
        poziom="🔴",
        uwagi="Używane przez instytucje do syntetycznego pożyczania."
    ),
    
    "Conversion": Strategia(
        nazwa="Conversion",
        kategoria="🏦 Arbitraż",
        opis="Long stock + long put + short call. Arbitraż na put-call parity.",
        kiedy="""✅ Wykorzystanie błędnej wyceny
✅ Gdy opcje są źle wycenione względem siebie
❌ Wymaga bardzo niskich kosztów transakcji""",
        konstrukcja="100 akcji + Kupno PUT + Sprzedaż CALL (ten sam strike)",
        max_zysk="Różnica w błędnej wycenie",
        max_strata="Brak (pozycja bez ryzyka)",
        breakeven="Nie dotyczy",
        greeks="Delta = 0 | Wszystkie ≈ 0",
        poziom="🔴",
        uwagi="Czysta strategia arbitrażowa dla profesjonalistów."
    ),
    
    "Reversal": Strategia(
        nazwa="Reversal",
        kategoria="🏦 Arbitraż",
        opis="Short stock + short put + long call. Odwrotność conversion.",
        kiedy="""✅ Wykorzystanie błędnej wyceny w drugą stronę
❌ Wymaga możliwości shortowania""",
        konstrukcja="Short 100 akcji + Sprzedaż PUT + Kupno CALL (ten sam strike)",
        max_zysk="Różnica w błędnej wycenie",
        max_strata="Brak",
        breakeven="Nie dotyczy",
        greeks="Delta = 0",
        poziom="🔴",
        uwagi="Odwrotność conversion. Dla market makerów."
    ),
}

# ══════════════════════════════════════════════════════════════════════════════
# FUNKCJE PAYOFF
# ══════════════════════════════════════════════════════════════════════════════
def get_payoff(strategia_nazwa, x, S, params, T, σ):
    """Uniwersalna funkcja zwracająca payoff dla dowolnej strategii"""
    
    # === PODSTAWOWE ===
    if strategia_nazwa == "Long Call":
        K = params["K"]
        g = bs(S, K, T, R, σ, "call")
        return np.maximum(x - K, 0) - g["cena"], g["cena"], g
    
    elif strategia_nazwa == "Long Put":
        K = params["K"]
        g = bs(S, K, T, R, σ, "put")
        return np.maximum(K - x, 0) - g["cena"], g["cena"], g
    
    elif strategia_nazwa == "Short Call (Naked)":
        K = params["K"]
        g = bs(S, K, T, R, σ, "call")
        return g["cena"] - np.maximum(x - K, 0), -g["cena"], {k: -v for k, v in g.items()}
    
    elif strategia_nazwa == "Short Put (Cash-Secured)":
        K = params["K"]
        g = bs(S, K, T, R, σ, "put")
        return g["cena"] - np.maximum(K - x, 0), -g["cena"], {k: -v for k, v in g.items()}
    
    # === DOCHODOWE ===
    elif strategia_nazwa == "Covered Call":
        K = params["K"]
        g = bs(S, K, T, R, σ, "call")
        akcje = x - S
        short_call = g["cena"] - np.maximum(x - K, 0)
        return akcje + short_call, g["cena"], {"delta": 1 - g["delta"], "theta": -g["theta"], "vega": -g["vega"], "cena": g["cena"]}
    
    elif strategia_nazwa == "Covered Put":
        K = params["K"]
        g = bs(S, K, T, R, σ, "put")
        short_akcje = S - x
        short_put = g["cena"] - np.maximum(K - x, 0)
        return short_akcje + short_put, g["cena"], {"delta": -1 - g["delta"], "theta": -g["theta"], "vega": -g["vega"], "cena": g["cena"]}
    
    # === ZABEZPIECZAJĄCE ===
    elif strategia_nazwa == "Protective Put":
        K = params["K"]
        g = bs(S, K, T, R, σ, "put")
        akcje = x - S
        long_put = np.maximum(K - x, 0) - g["cena"]
        return akcje + long_put, g["cena"], {"delta": 1 + g["delta"], "theta": g["theta"], "vega": g["vega"], "cena": g["cena"]}
    
    elif strategia_nazwa == "Protective Call":
        K = params["K"]
        g = bs(S, K, T, R, σ, "call")
        short_akcje = S - x
        long_call = np.maximum(x - K, 0) - g["cena"]
        return short_akcje + long_call, g["cena"], {"delta": -1 + g["delta"], "theta": g["theta"], "vega": g["vega"], "cena": g["cena"]}
    
    elif strategia_nazwa == "Collar (Zero-Cost)":
        K_put, K_call = params["K_put"], params["K_call"]
        gp, gc = bs(S, K_put, T, R, σ, "put"), bs(S, K_call, T, R, σ, "call")
        koszt = gp["cena"] - gc["cena"]
        akcje = x - S
        long_put = np.maximum(K_put - x, 0) - gp["cena"]
        short_call = gc["cena"] - np.maximum(x - K_call, 0)
        return akcje + long_put + short_call, koszt, {"delta": 1 + gp["delta"] - gc["delta"], "theta": gp["theta"] - gc["theta"], "vega": gp["vega"] - gc["vega"], "cena": koszt}
    
    # === SPREADY ===
    elif strategia_nazwa == "Bull Call Spread":
        K1, K2 = params["K1"], params["K2"]
        g1, g2 = bs(S, K1, T, R, σ, "call"), bs(S, K2, T, R, σ, "call")
        koszt = g1["cena"] - g2["cena"]
        return np.maximum(x - K1, 0) - np.maximum(x - K2, 0) - koszt, koszt, {"delta": g1["delta"] - g2["delta"], "theta": g1["theta"] - g2["theta"], "vega": g1["vega"] - g2["vega"], "cena": koszt}
    
    elif strategia_nazwa == "Bear Put Spread":
        K1, K2 = params["K1"], params["K2"]  # K1 niższy, K2 wyższy
        g1, g2 = bs(S, K1, T, R, σ, "put"), bs(S, K2, T, R, σ, "put")
        koszt = g2["cena"] - g1["cena"]
        return np.maximum(K2 - x, 0) - np.maximum(K1 - x, 0) - koszt, koszt, {"delta": g2["delta"] - g1["delta"], "theta": g2["theta"] - g1["theta"], "vega": g2["vega"] - g1["vega"], "cena": koszt}
    
    elif strategia_nazwa == "Bull Put Spread (Credit)":
        K1, K2 = params["K1"], params["K2"]  # K1 niższy, K2 wyższy
        g1, g2 = bs(S, K1, T, R, σ, "put"), bs(S, K2, T, R, σ, "put")
        kredyt = g2["cena"] - g1["cena"]
        return kredyt - np.maximum(K2 - x, 0) + np.maximum(K1 - x, 0), -kredyt, {"delta": -(g2["delta"] - g1["delta"]), "theta": -(g2["theta"] - g1["theta"]), "vega": -(g2["vega"] - g1["vega"]), "cena": -kredyt}
    
    elif strategia_nazwa == "Bear Call Spread (Credit)":
        K1, K2 = params["K1"], params["K2"]  # K1 niższy, K2 wyższy
        g1, g2 = bs(S, K1, T, R, σ, "call"), bs(S, K2, T, R, σ, "call")
        kredyt = g1["cena"] - g2["cena"]
        return kredyt - np.maximum(x - K1, 0) + np.maximum(x - K2, 0), -kredyt, {"delta": -(g1["delta"] - g2["delta"]), "theta": -(g1["theta"] - g2["theta"]), "vega": -(g1["vega"] - g2["vega"]), "cena": -kredyt}
    
    # === ZMIENNOŚĆ ===
    elif strategia_nazwa == "Long Straddle":
        K = params["K"]
        gc, gp = bs(S, K, T, R, σ, "call"), bs(S, K, T, R, σ, "put")
        koszt = gc["cena"] + gp["cena"]
        return np.maximum(x - K, 0) + np.maximum(K - x, 0) - koszt, koszt, {"delta": gc["delta"] + gp["delta"], "theta": gc["theta"] + gp["theta"], "vega": gc["vega"] + gp["vega"], "cena": koszt}
    
    elif strategia_nazwa == "Long Strangle":
        K_put, K_call = params["K_put"], params["K_call"]
        gc, gp = bs(S, K_call, T, R, σ, "call"), bs(S, K_put, T, R, σ, "put")
        koszt = gc["cena"] + gp["cena"]
        return np.maximum(x - K_call, 0) + np.maximum(K_put - x, 0) - koszt, koszt, {"delta": gc["delta"] + gp["delta"], "theta": gc["theta"] + gp["theta"], "vega": gc["vega"] + gp["vega"], "cena": koszt}
    
    elif strategia_nazwa == "Short Straddle":
        K = params["K"]
        gc, gp = bs(S, K, T, R, σ, "call"), bs(S, K, T, R, σ, "put")
        kredyt = gc["cena"] + gp["cena"]
        return kredyt - np.maximum(x - K, 0) - np.maximum(K - x, 0), -kredyt, {"delta": -(gc["delta"] + gp["delta"]), "theta": -(gc["theta"] + gp["theta"]), "vega": -(gc["vega"] + gp["vega"]), "cena": -kredyt}
    
    elif strategia_nazwa == "Short Strangle":
        K_put, K_call = params["K_put"], params["K_call"]
        gc, gp = bs(S, K_call, T, R, σ, "call"), bs(S, K_put, T, R, σ, "put")
        kredyt = gc["cena"] + gp["cena"]
        return kredyt - np.maximum(x - K_call, 0) - np.maximum(K_put - x, 0), -kredyt, {"delta": -(gc["delta"] + gp["delta"]), "theta": -(gc["theta"] + gp["theta"]), "vega": -(gc["vega"] + gp["vega"]), "cena": -kredyt}
    
    # === NEUTRALNE ===
    elif strategia_nazwa == "Iron Condor":
        K1, K2, K3, K4 = params["K1"], params["K2"], params["K3"], params["K4"]
        gp1, gp2 = bs(S, K1, T, R, σ, "put"), bs(S, K2, T, R, σ, "put")
        gc3, gc4 = bs(S, K3, T, R, σ, "call"), bs(S, K4, T, R, σ, "call")
        kredyt = (gp2["cena"] - gp1["cena"]) + (gc3["cena"] - gc4["cena"])
        payoff = kredyt - np.maximum(K2 - x, 0) + np.maximum(K1 - x, 0) - np.maximum(x - K3, 0) + np.maximum(x - K4, 0)
        return payoff, -kredyt, {"delta": 0, "theta": 0.05, "vega": -0.1, "cena": -kredyt}
    
    elif strategia_nazwa == "Iron Butterfly":
        K_low, K_mid, K_high = params["K_low"], params["K_mid"], params["K_high"]
        gp_low, gp_mid = bs(S, K_low, T, R, σ, "put"), bs(S, K_mid, T, R, σ, "put")
        gc_mid, gc_high = bs(S, K_mid, T, R, σ, "call"), bs(S, K_high, T, R, σ, "call")
        kredyt = (gp_mid["cena"] - gp_low["cena"]) + (gc_mid["cena"] - gc_high["cena"])
        payoff = kredyt - np.maximum(K_mid - x, 0) + np.maximum(K_low - x, 0) - np.maximum(x - K_mid, 0) + np.maximum(x - K_high, 0)
        return payoff, -kredyt, {"delta": 0, "theta": 0.08, "vega": -0.15, "cena": -kredyt}
    
    elif strategia_nazwa in ["Long Call Butterfly", "Long Put Butterfly"]:
        K1, K2, K3 = params["K1"], params["K2"], params["K3"]
        if "Call" in strategia_nazwa:
            g1, g2, g3 = bs(S, K1, T, R, σ, "call"), bs(S, K2, T, R, σ, "call"), bs(S, K3, T, R, σ, "call")
            koszt = g1["cena"] - 2*g2["cena"] + g3["cena"]
            payoff = np.maximum(x - K1, 0) - 2*np.maximum(x - K2, 0) + np.maximum(x - K3, 0) - koszt
        else:
            g1, g2, g3 = bs(S, K1, T, R, σ, "put"), bs(S, K2, T, R, σ, "put"), bs(S, K3, T, R, σ, "put")
            koszt = g3["cena"] - 2*g2["cena"] + g1["cena"]
            payoff = np.maximum(K3 - x, 0) - 2*np.maximum(K2 - x, 0) + np.maximum(K1 - x, 0) - koszt
        return payoff, koszt, {"delta": 0, "theta": 0.02, "vega": -0.05, "cena": koszt}
    
    # === KALENDARZOWE ===
    elif strategia_nazwa in ["Calendar Call Spread", "Calendar Put Spread"]:
        K = params["K"]
        T_near, T_far = params.get("T_near", T*0.5), params.get("T_far", T)
        typ = "call" if "Call" in strategia_nazwa else "put"
        g_near = bs(S, K, T_near, R, σ, typ)
        g_far = bs(S, K, T_far, R, σ, typ)
        koszt = g_far["cena"] - g_near["cena"]
        # Uproszczony payoff przy wygaśnięciu bliższej opcji
        if typ == "call":
            payoff = g_far["cena"] - koszt - np.maximum(x - K, 0) + g_near["cena"]
        else:
            payoff = g_far["cena"] - koszt - np.maximum(K - x, 0) + g_near["cena"]
        # Maksymalny zysk przy strike
        max_at_strike = g_far["cena"] - koszt
        payoff = np.where(np.abs(x - K) < S*0.1, max_at_strike, payoff * 0.3)
        return payoff, koszt, {"delta": 0, "theta": 0.03, "vega": 0.1, "cena": koszt}
    
    # === SYNTETYCZNE ===
    elif strategia_nazwa == "Synthetic Long Stock":
        K = params["K"]
        gc, gp = bs(S, K, T, R, σ, "call"), bs(S, K, T, R, σ, "put")
        koszt = gc["cena"] - gp["cena"]
        return (x - K) - koszt, koszt, {"delta": 1, "theta": gc["theta"] - gp["theta"], "vega": gc["vega"] - gp["vega"], "cena": koszt}
    
    elif strategia_nazwa == "Synthetic Short Stock":
        K = params["K"]
        gc, gp = bs(S, K, T, R, σ, "call"), bs(S, K, T, R, σ, "put")
        kredyt = gc["cena"] - gp["cena"]
        return (K - x) + kredyt, -kredyt, {"delta": -1, "theta": -(gc["theta"] - gp["theta"]), "vega": -(gc["vega"] - gp["vega"]), "cena": -kredyt}
    
    # === RATIO ===
    elif strategia_nazwa == "Call Ratio Spread":
        K1, K2 = params["K1"], params["K2"]
        g1, g2 = bs(S, K1, T, R, σ, "call"), bs(S, K2, T, R, σ, "call")
        koszt = g1["cena"] - 2*g2["cena"]
        payoff = np.maximum(x - K1, 0) - 2*np.maximum(x - K2, 0) - koszt
        return payoff, koszt, {"delta": g1["delta"] - 2*g2["delta"], "theta": g1["theta"] - 2*g2["theta"], "vega": g1["vega"] - 2*g2["vega"], "cena": koszt}
    
    elif strategia_nazwa == "Put Ratio Spread":
        K1, K2 = params["K1"], params["K2"]  # K1 niższy, K2 wyższy
        g1, g2 = bs(S, K1, T, R, σ, "put"), bs(S, K2, T, R, σ, "put")
        koszt = g2["cena"] - 2*g1["cena"]
        payoff = np.maximum(K2 - x, 0) - 2*np.maximum(K1 - x, 0) - koszt
        return payoff, koszt, {"delta": g2["delta"] - 2*g1["delta"], "theta": g2["theta"] - 2*g1["theta"], "vega": g2["vega"] - 2*g1["vega"], "cena": koszt}
    
    # === ARBITRAŻ ===
    elif strategia_nazwa in ["Box Spread", "Conversion", "Reversal"]:
        # Te strategie mają płaski profil - zysk = stopa %
        K = params.get("K", S)
        zysk = K * R * T / 365 * 100
        return np.full_like(x, zysk), 0, {"delta": 0, "theta": 0, "vega": 0, "cena": 0}
    
    # === DIAGONALNE (uproszczone) ===
    elif strategia_nazwa == "Diagonal Call Spread":
        K1, K2 = params["K1"], params["K2"]
        g1 = bs(S, K1, T * 2, R, σ, "call")  # daleki termin
        g2 = bs(S, K2, T, R, σ, "call")  # bliski termin
        koszt = g1["cena"] - g2["cena"]
        # Uproszczony payoff
        payoff = np.minimum(np.maximum(x - K1, 0), K2 - K1) + g2["cena"] - koszt
        return payoff, koszt, {"delta": 0.5, "theta": 0.02, "vega": 0.05, "cena": koszt}
    
    # Default
    return np.zeros_like(x), 0, {"delta": 0, "theta": 0, "vega": 0, "cena": 0}

# ══════════════════════════════════════════════════════════════════════════════
# UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def rysuj_wykres(x, y, tytul, S, breakevens=None):
    """Rysuj wykres payoff"""
    fig = go.Figure()
    
    zysk = np.where(y > 0, y, np.nan)
    strata = np.where(y <= 0, y, np.nan)
    
    fig.add_trace(go.Scatter(x=x, y=zysk, fill='tozeroy', name='Zysk', 
                              line=dict(color='#00FF88', width=0), fillcolor='rgba(0,255,136,0.3)'))
    fig.add_trace(go.Scatter(x=x, y=strata, fill='tozeroy', name='Strata',
                              line=dict(color='#FF4444', width=0), fillcolor='rgba(255,68,68,0.3)'))
    fig.add_trace(go.Scatter(x=x, y=y, name='Payoff', line=dict(color='#FFFFFF', width=3)))
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=S, line_dash="dot", line_color="#FFD700", opacity=0.7,
                  annotation_text=f"Spot: {S:.0f}", annotation_position="top")
    
    if breakevens:
        for be in breakevens:
            if 0.5*S < be < 1.5*S:
                fig.add_vline(x=be, line_dash="dash", line_color="#00BFFF", opacity=0.5,
                              annotation_text=f"BE: {be:.1f}", annotation_position="bottom")
    
    fig.update_layout(
        template="plotly_dark",
        title=dict(text=tytul, font=dict(size=18)),
        xaxis_title="Cena przy wygaśnięciu",
        yaxis_title="Zysk / Strata (PLN)",
        height=450,
        margin=dict(l=50, r=50, t=60, b=50),
        showlegend=False
    )
    return fig

def panel_edukacyjny(strategia, greeks, koszt):
    """Panel edukacyjny z informacjami o strategii"""
    st.markdown("---")
    
    # Kiedy używać
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🎯 KIEDY UŻYWAĆ?")
        st.markdown(strategia.kiedy)
    
    with col2:
        st.markdown("### 📊 PROFIL ZYSKU/STRATY")
        st.success(f"**Max Zysk:** {strategia.max_zysk}")
        st.error(f"**Max Strata:** {strategia.max_strata}")
        st.info(f"**Breakeven:** {strategia.breakeven}")
        st.warning(f"**Konstrukcja:** {strategia.konstrukcja}")
    
    # Greeks
    st.markdown("---")
    st.markdown("### 🇬🇷 GREEKS - Czujniki Ryzyka")
    
    g1, g2, g3, g4 = st.columns(4)
    
    delta = greeks.get("delta", 0)
    theta = greeks.get("theta", 0) * 100
    vega = greeks.get("vega", 0) * 100
    
    with g1:
        kolor = "🟢" if delta > 0.1 else "🔴" if delta < -0.1 else "⚪"
        st.metric("Delta Δ", f"{delta:.3f}")
        if delta > 0.1:
            st.caption(f"{kolor} Zarabiasz na WZROŚCIE")
        elif delta < -0.1:
            st.caption(f"{kolor} Zarabiasz na SPADKU")
        else:
            st.caption(f"{kolor} NEUTRALNY kierunkowo")
    
    with g2:
        kolor = "🟢" if theta > 0.5 else "🔴" if theta < -0.5 else "⚪"
        st.metric("Theta Θ", f"{theta:.2f} PLN/dzień")
        if theta > 0.5:
            st.caption(f"{kolor} Czas pracuje DLA Ciebie! 💰")
        elif theta < -0.5:
            st.caption(f"{kolor} Czas pracuje PRZECIW Tobie! ⏰")
        else:
            st.caption(f"{kolor} Neutralny czasowo")
    
    with g3:
        kolor = "🟢" if vega > 1 else "🔴" if vega < -1 else "⚪"
        st.metric("Vega V", f"{vega:.2f} PLN/%IV")
        if vega > 1:
            st.caption(f"{kolor} Zyskujesz gdy IV ROŚNIE 🌪️")
        elif vega < -1:
            st.caption(f"{kolor} Zyskujesz gdy IV SPADA 😴")
        else:
            st.caption(f"{kolor} Neutralny na zmienność")
    
    with g4:
        if koszt > 0:
            st.metric("💰 Koszt", f"{koszt:.2f} PLN")
            st.caption("DEBET - płacisz z góry")
        elif koszt < 0:
            st.metric("💰 Kredyt", f"{-koszt:.2f} PLN")
            st.caption("KREDYT - dostajesz pieniądze! 🎉")
        else:
            st.metric("💰 Koszt", "0 PLN")
            st.caption("Zero-cost!")
    
    # Uwagi
    if strategia.uwagi:
        st.markdown("---")
        st.markdown("### 💡 WAŻNE UWAGI")
        st.info(strategia.uwagi)

def get_params_ui(strategia_nazwa, S):
    """Dynamiczne UI dla parametrów strategii"""
    params = {}
    
    single_strike = ["Long Call", "Long Put", "Short Call (Naked)", "Short Put (Cash-Secured)",
                     "Covered Call", "Covered Put", "Protective Put", "Protective Call",
                     "Long Straddle", "Short Straddle", "Synthetic Long Stock", "Synthetic Short Stock",
                     "Calendar Call Spread", "Calendar Put Spread"]
    
    two_strikes_same = ["Bull Call Spread", "Bear Put Spread", "Bull Put Spread (Credit)", 
                        "Bear Call Spread (Credit)", "Call Ratio Spread", "Put Ratio Spread",
                        "Diagonal Call Spread"]
    
    strangle = ["Long Strangle", "Short Strangle", "Collar (Zero-Cost)"]
    
    condor = ["Iron Condor"]
    butterfly = ["Iron Butterfly"]
    butterfly3 = ["Long Call Butterfly", "Long Put Butterfly"]
    
    if strategia_nazwa in single_strike:
        default = S if "ATM" in STRATEGIE[strategia_nazwa].konstrukcja or "Straddle" in strategia_nazwa else S * 1.05 if "Call" in strategia_nazwa and "Put" not in strategia_nazwa else S * 0.95
        params["K"] = st.slider("Strike (K)", float(S * 0.7), float(S * 1.3), float(default), step=1.0)
    
    elif strategia_nazwa in two_strikes_same:
        col1, col2 = st.columns(2)
        if "Bull" in strategia_nazwa or "Ratio" in strategia_nazwa:
            with col1:
                params["K1"] = st.slider("K1 (niższy)", float(S * 0.8), float(S * 1.1), float(S * 0.95), step=1.0)
            with col2:
                params["K2"] = st.slider("K2 (wyższy)", float(params["K1"]), float(S * 1.3), float(S * 1.1), step=1.0)
        else:  # Bear
            with col1:
                params["K1"] = st.slider("K1 (niższy)", float(S * 0.7), float(S), float(S * 0.9), step=1.0)
            with col2:
                params["K2"] = st.slider("K2 (wyższy)", float(params["K1"]), float(S * 1.2), float(S * 1.05), step=1.0)
    
    elif strategia_nazwa in strangle:
        col1, col2 = st.columns(2)
        with col1:
            params["K_put"] = st.slider("Strike PUT", float(S * 0.7), float(S), float(S * 0.9), step=1.0)
        with col2:
            params["K_call"] = st.slider("Strike CALL", float(S), float(S * 1.3), float(S * 1.1), step=1.0)
    
    elif strategia_nazwa in condor:
        st.markdown("*Strike'i: K1 < K2 < K3 < K4*")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            params["K1"] = st.number_input("K1 (Put buy)", value=float(S * 0.85), step=1.0)
        with col2:
            params["K2"] = st.number_input("K2 (Put sell)", value=float(S * 0.95), step=1.0)
        with col3:
            params["K3"] = st.number_input("K3 (Call sell)", value=float(S * 1.05), step=1.0)
        with col4:
            params["K4"] = st.number_input("K4 (Call buy)", value=float(S * 1.15), step=1.0)
    
    elif strategia_nazwa in butterfly:
        col1, col2, col3 = st.columns(3)
        with col1:
            params["K_low"] = st.number_input("K niskie", value=float(S * 0.9), step=1.0)
        with col2:
            params["K_mid"] = st.number_input("K środkowe", value=float(S), step=1.0)
        with col3:
            params["K_high"] = st.number_input("K wysokie", value=float(S * 1.1), step=1.0)
    
    elif strategia_nazwa in butterfly3:
        col1, col2, col3 = st.columns(3)
        with col1:
            params["K1"] = st.number_input("K1 (ITM)", value=float(S * 0.95), step=1.0)
        with col2:
            params["K2"] = st.number_input("K2 (ATM)", value=float(S), step=1.0)
        with col3:
            params["K3"] = st.number_input("K3 (OTM)", value=float(S * 1.05), step=1.0)
    
    else:
        params["K"] = S
    
    return params

# ══════════════════════════════════════════════════════════════════════════════
# GŁÓWNA APLIKACJA
# ══════════════════════════════════════════════════════════════════════════════
def main():
    st.title("🎓 Akademia Opcji v2.0")
    st.markdown("*Kompletna platforma edukacyjna - wszystkie strategie opcyjne*")
    
    # Sidebar
    st.sidebar.header("⚙️ Parametry Rynkowe")
    S = st.sidebar.number_input("📈 Cena aktywa (S)", value=100.0, min_value=1.0, step=1.0)
    vol = st.sidebar.slider("🌪️ Zmienność IV (%)", 5, 150, 30) / 100
    dni = st.sidebar.slider("📅 Dni do wygaśnięcia", 1, 365, 30)
    T = dni / 365
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Interpretacja IV")
    iv_level = "🟢 NISKA" if vol < 0.2 else "🟡 NORMALNA" if vol < 0.4 else "🟠 WYSOKA" if vol < 0.6 else "🔴 EKSTREMALNA"
    st.sidebar.markdown(f"**{iv_level}** ({vol*100:.0f}%)")
    
    if vol < 0.2:
        st.sidebar.info("💡 Kupuj opcje (long straddle)")
    elif vol > 0.5:
        st.sidebar.info("💡 Sprzedawaj premię (iron condor)")
    
    # Grupowanie strategii
    kategorie = {}
    for nazwa, strat in STRATEGIE.items():
        kat = strat.kategoria
        if kat not in kategorie:
            kategorie[kat] = []
        kategorie[kat].append(nazwa)
    
    # Wybór strategii
    st.markdown("---")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        wybrana_kategoria = st.selectbox("📂 Kategoria", list(kategorie.keys()))
    with col2:
        wybrana_strategia = st.selectbox("📋 Strategia", kategorie[wybrana_kategoria])
    
    strategia = STRATEGIE[wybrana_strategia]
    
    # Nagłówek strategii
    st.markdown(f"## {strategia.poziom} {strategia.nazwa}")
    st.markdown(f"*{strategia.opis}*")
    
    # Parametry
    st.markdown("### ⚙️ Parametry Strategii")
    params = get_params_ui(wybrana_strategia, S)
    
    # Obliczenia
    x = np.linspace(S * 0.5, S * 1.5, 300)
    y, koszt, greeks = get_payoff(wybrana_strategia, x, S, params, T, vol)
    
    # Breakeven
    breakevens = []
    zero_crossings = np.where(np.diff(np.sign(y)))[0]
    for idx in zero_crossings:
        breakevens.append(x[idx])
    
    # Wykres
    st.markdown("### 📈 Wykres Payoff (przy wygaśnięciu)")
    fig = rysuj_wykres(x, y * 100, f"{wybrana_strategia}", S, breakevens)
    st.plotly_chart(fig, use_container_width=True)
    
    # Panel edukacyjny
    panel_edukacyjny(strategia, greeks, koszt)
    
    # Scenariusze
    st.markdown("---")
    st.markdown("### 🎭 Analiza Scenariuszy")
    
    scenariusze = [
        ("📉 -20%", S * 0.8),
        ("📉 -10%", S * 0.9),
        ("➡️ 0%", S),
        ("📈 +10%", S * 1.1),
        ("📈 +20%", S * 1.2)
    ]
    
    cols = st.columns(5)
    for i, (nazwa, cena) in enumerate(scenariusze):
        idx = np.argmin(np.abs(x - cena))
        wynik = y[idx] * 100
        with cols[i]:
            if wynik > 10:
                st.success(f"**{nazwa}**\n\n💰 **+{wynik:.0f}** PLN")
            elif wynik < -10:
                st.error(f"**{nazwa}**\n\n💸 **{wynik:.0f}** PLN")
            else:
                st.info(f"**{nazwa}**\n\n⚖️ **{wynik:.0f}** PLN")
    
    # Statystyki
    st.markdown("---")
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        max_zysk = np.max(y) * 100
        st.metric("📈 Max Zysk", f"{max_zysk:.0f} PLN" if max_zysk < 10000 else "♾️")
    
    with col_stat2:
        max_strata = np.min(y) * 100
        st.metric("📉 Max Strata", f"{max_strata:.0f} PLN" if max_strata > -10000 else "♾️")
    
    with col_stat3:
        if breakevens:
            be_str = " | ".join([f"{be:.1f}" for be in breakevens[:2]])
            st.metric("⚖️ Breakeven", be_str)
        else:
            st.metric("⚖️ Breakeven", "N/A")
    
    with col_stat4:
        if max_strata != 0 and max_zysk > 0 and max_strata > -10000:
            ratio = max_zysk / abs(max_strata)
            st.metric("📊 Zysk/Ryzyko", f"{ratio:.2f}x")
        else:
            st.metric("📊 Zysk/Ryzyko", "N/A")
    
    # Stopka
    st.markdown("---")
    st.caption("⚠️ **Ostrzeżenie:** Handel opcjami wiąże się ze znacznym ryzykiem. Niektóre strategie mogą generować straty przekraczające początkową inwestycję. To narzędzie służy wyłącznie celom edukacyjnym.")

if __name__ == "__main__":
    main()
