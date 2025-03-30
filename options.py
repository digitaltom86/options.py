import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.figure import Figure
import scipy.stats as si

# Set page configuration
st.set_page_config(
    page_title="Options Trading Simulator",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to improve the app's appearance
st.markdown("""
<style>
    .main .block-container {padding-top: 2rem;}
    h1, h2, h3 {margin-top: 0;}
    .stTabs [data-baseweb="tab-panel"] {padding-top: 1rem;}
    .stExpander {border: 1px solid #ddd; border-radius: 5px; margin-bottom: 1rem;}
    .streamlit-expanderHeader {font-weight: bold;}
    div[data-testid="stSidebar"] .block-container {padding-top: 2rem;}
</style>
""", unsafe_allow_html=True)

# Title and introduction
st.title("Options Trading Interactive Simulator")
st.markdown("""
This app helps you understand the mechanics of basic options strategies:
- **Long Call**: Right to buy at strike price
- **Short Call**: Obligation to sell at strike price
- **Long Put**: Right to sell at strike price 
- **Short Put**: Obligation to buy at strike price

Adjust the parameters to see how different factors affect option profitability!
""")

# Sidebar for global parameters
with st.sidebar:
    st.header("Market Settings")
    
    # Asset type selection
    asset_type = st.selectbox(
        "Select Asset Class",
        ["Stock", "Currency", "Commodity", "Index"],
        index=0
    )
    
    # Asset examples based on selection
    asset_examples = {
        "Stock": ["AAPL", "MSFT", "AMZN", "GOOGL", "TSLA"],
        "Currency": ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CNY", "USD/CAD"],
        "Commodity": ["Gold", "Silver", "Crude Oil", "Natural Gas", "Wheat"],
        "Index": ["S&P 500", "Nasdaq", "Dow Jones", "Russell 2000", "VIX"]
    }
    
    asset = st.selectbox(
        f"Select {asset_type}",
        asset_examples[asset_type],
        index=0
    )
    
    # Set default prices based on asset type
    default_prices = {
        "Stock": 150.0,
        "Currency": 1.2,
        "Commodity": 1800.0,
        "Index": 4500.0
    }
    
    # Current price
    current_price = st.number_input(
        "Current Price",
        min_value=0.01,
        max_value=10000.0,
        value=default_prices[asset_type],
        step=0.01,
        format="%.2f"
    )
    
    # Price range to display
    price_range_percent = st.slider(
        "Price Range to Display (%)",
        min_value=5,
        max_value=50,
        value=20,
        step=5
    )
    
    # Days until expiration
    days_to_expiration = st.slider(
        "Days Until Expiration",
        min_value=1,
        max_value=365,
        value=30,
        step=1
    )
    
    # Volatility
    volatility = st.slider(
        "Implied Volatility (%)",
        min_value=5,
        max_value=100,
        value=25,
        step=5
    ) / 100.0
    
    # Risk-free rate
    risk_free_rate = st.slider(
        "Risk-Free Rate (%)",
        min_value=0.0,
        max_value=10.0,
        value=4.0,
        step=0.1
    ) / 100.0

# Function to calculate option price using Black-Scholes
def black_scholes(S, K, T, r, sigma, option_type="call"):
    if T <= 0:
        # At expiration, option is worth intrinsic value only
        if option_type == "call":
            return max(0, S - K)
        else:  # put
            return max(0, K - S)
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == "call":
        price = S * si.norm.cdf(d1) - K * np.exp(-r * T) * si.norm.cdf(d2)
    else:  # put
        price = K * np.exp(-r * T) * si.norm.cdf(-d2) - S * si.norm.cdf(-d1)
    
    return price

# Helper function to create profit/loss chart
def create_option_chart(strategy, strike_price, premium, current_price, price_range_percent, contract_size=100):
    # Calculate price range
    min_price = current_price * (1 - price_range_percent / 100)
    max_price = current_price * (1 + price_range_percent / 100)
    
    # Create price array
    prices = np.linspace(min_price, max_price, 1000)
    
    # Calculate profit/loss based on strategy
    if strategy == "Long Call":
        profits = np.maximum(prices - strike_price, 0) * contract_size - premium * contract_size
    elif strategy == "Short Call":
        profits = -np.maximum(prices - strike_price, 0) * contract_size + premium * contract_size
    elif strategy == "Long Put":
        profits = np.maximum(strike_price - prices, 0) * contract_size - premium * contract_size
    elif strategy == "Short Put":
        profits = -np.maximum(strike_price - prices, 0) * contract_size + premium * contract_size
    
    # Create the figure
    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    
    # Plot the profit/loss line
    ax.plot(prices, profits, linewidth=2.5, color='blue')
    
    # Add a horizontal line at y=0
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=1)
    
    # Add a vertical line at strike price
    ax.axvline(x=strike_price, color='red', linestyle='--', alpha=0.8, linewidth=1)
    
    # Add a vertical line at current price
    ax.axvline(x=current_price, color='green', linestyle='--', alpha=0.8, linewidth=1)
    
    # Fill the area above/below 0
    ax.fill_between(prices, profits, 0, where=(profits > 0), color='green', alpha=0.3)
    ax.fill_between(prices, profits, 0, where=(profits <= 0), color='red', alpha=0.3)
    
    # Set labels
    ax.set_xlabel(f"{asset_type} Price at Expiration", fontsize=12)
    ax.set_ylabel("Profit/Loss ($)", fontsize=12)
    ax.set_title(f"{strategy} P&L at Expiration", fontsize=14, fontweight='bold')
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f"${x:,.0f}"))
    
    # Mark important points
    # Breakeven point(s)
    if strategy == "Long Call":
        breakeven = strike_price + premium
        if min_price <= breakeven <= max_price:
            ax.scatter([breakeven], [0], color='purple', s=100, zorder=5)
            ax.annotate(f"Breakeven: {breakeven:.2f}", 
                        (breakeven, 0), 
                        textcoords="offset points", 
                        xytext=(0, 10), 
                        ha='center',
                        fontweight='bold')
    
    elif strategy == "Short Call":
        breakeven = strike_price + premium
        if min_price <= breakeven <= max_price:
            ax.scatter([breakeven], [0], color='purple', s=100, zorder=5)
            ax.annotate(f"Breakeven: {breakeven:.2f}", 
                        (breakeven, 0), 
                        textcoords="offset points", 
                        xytext=(0, 10), 
                        ha='center',
                        fontweight='bold')
    
    elif strategy == "Long Put":
        breakeven = strike_price - premium
        if min_price <= breakeven <= max_price:
            ax.scatter([breakeven], [0], color='purple', s=100, zorder=5)
            ax.annotate(f"Breakeven: {breakeven:.2f}", 
                        (breakeven, 0), 
                        textcoords="offset points", 
                        xytext=(0, 10), 
                        ha='center',
                        fontweight='bold')
    
    elif strategy == "Short Put":
        breakeven = strike_price - premium
        if min_price <= breakeven <= max_price:
            ax.scatter([breakeven], [0], color='purple', s=100, zorder=5)
            ax.annotate(f"Breakeven: {breakeven:.2f}", 
                        (breakeven, 0), 
                        textcoords="offset points", 
                        xytext=(0, 10), 
                        ha='center',
                        fontweight='bold')
    
    # Annotate strike price and current price
    ax.annotate(f"Strike: {strike_price:.2f}", 
                (strike_price, 0), 
                textcoords="offset points", 
                xytext=(5, -15), 
                color='red',
                fontweight='bold')
    
    ax.annotate(f"Current: {current_price:.2f}", 
                (current_price, 0), 
                textcoords="offset points", 
                xytext=(5, -30), 
                color='green',
                fontweight='bold')
    
    # Show min and max profit/loss
    max_profit = max(profits)
    min_profit = min(profits)
    
    if np.isfinite(max_profit):
        if strategy in ["Short Call", "Short Put"]:
            ax.annotate(f"Max Profit: ${premium * contract_size:.2f}", 
                        (min_price, premium * contract_size),
                        textcoords="offset points", 
                        xytext=(5, 0))
        elif max_profit > 0:
            max_profit_price = prices[np.argmax(profits)]
            ax.annotate(f"Max Profit: ${max_profit:.2f}", 
                        (max_profit_price, max_profit),
                        textcoords="offset points", 
                        xytext=(0, 5),
                        ha='center')
    
    if np.isfinite(min_profit):
        if strategy in ["Long Call", "Long Put"]:
            ax.annotate(f"Max Loss: -${premium * contract_size:.2f}", 
                        (strike_price, -premium * contract_size),
                        textcoords="offset points", 
                        xytext=(0, -20),
                        ha='center')
        elif min_profit < 0:
            min_profit_price = prices[np.argmin(profits)]
            ax.annotate(f"Max Loss: ${min_profit:.2f}", 
                        (min_profit_price, min_profit),
                        textcoords="offset points", 
                        xytext=(0, -15),
                        ha='center')
    
    # Set grid
    ax.grid(True, alpha=0.3)
    
    # Tight layout
    fig.tight_layout()
    
    return fig

# Main app tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Long Call", 
    "Short Call", 
    "Long Put", 
    "Short Put"
])

# Contract size explanation
contract_size = 100
contract_multiplier_note = f"""
**Note:** For simplicity, we're using a standard contract size of {contract_size} units.
- For stocks, each option contract typically represents {contract_size} shares
- For currencies, it varies by exchange but often represents {contract_size},000 units
- For commodities, it depends on the specific commodity (e.g., 100 troy ounces for Gold)
- For indices, it's typically ${contract_size} times the index value
"""

####################
# LONG CALL TAB
####################
with tab1:
    st.header("Long Call Strategy")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### 📈 Strategy Overview
        A **Long Call** gives you the right (but not obligation) to buy the underlying asset at the strike price before expiration.
        
        * **Maximum Profit:** Unlimited (as price rises)
        * **Maximum Loss:** Limited to premium paid
        * **Breakeven Point:** Strike Price + Premium
        * **When to Use:** Bullish outlook - expecting price to rise significantly
        """)
        
        with st.expander("When to use Long Calls"):
            st.markdown("""
            **Ideal scenarios for Long Calls:**
            * When you expect a significant upward movement in price
            * When you want leverage (control more shares with less capital)
            * Before anticipated positive announcements (earnings, product launches)
            * When you want to limit your risk to just the premium paid
            
            **Real-world example:**
            Imagine you believe AAPL stock will rise significantly after their upcoming product announcement.
            Instead of buying 100 shares at $150 each ($15,000 investment), you could buy a call option for $5 per share ($500 total).
            If the stock rises to $170, your call option might be worth $20+ per share, giving you a 300%+ return instead of just 13%.
            """)
    
    with col2:
        # Long Call parameters
        lc_strike = st.number_input(
            "Strike Price (Long Call)",
            min_value=0.01,
            max_value=current_price * 2,
            value=current_price,
            step=0.01,
            format="%.2f",
            key="lc_strike"
        )
        
        # Calculate theoretical premium
        time_to_expiry = days_to_expiration / 365
        lc_premium_calc = black_scholes(current_price, lc_strike, time_to_expiry, risk_free_rate, volatility, "call")
        
        lc_premium = st.number_input(
            "Option Premium (Long Call)",
            min_value=0.01,
            max_value=current_price * 0.5,
            value=float(lc_premium_calc),
            step=0.01,
            format="%.2f",
            key="lc_premium"
        )
        
        # Display calculated values
        st.markdown(f"""
        * **Total Cost:** ${lc_premium * contract_size:.2f} ({contract_size} × ${lc_premium:.2f})
        * **Breakeven Price:** ${lc_strike + lc_premium:.2f}
        * **Profit at Current Price:** ${max(0, current_price - lc_strike) * contract_size - lc_premium * contract_size:.2f}
        """)
        
        # Show the profit/loss chart
        lc_chart = create_option_chart("Long Call", lc_strike, lc_premium, current_price, price_range_percent)
        st.pyplot(lc_chart)
        
        st.markdown(contract_multiplier_note)

####################
# SHORT CALL TAB
####################
with tab2:
    st.header("Short Call Strategy")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### 📉 Strategy Overview
        A **Short Call** obligates you to sell the underlying asset at the strike price if the option is exercised.
        
        * **Maximum Profit:** Limited to premium received
        * **Maximum Loss:** Unlimited (as price rises)
        * **Breakeven Point:** Strike Price + Premium
        * **When to Use:** Bearish or neutral outlook - expecting price to stay below strike
        """)
        
        with st.expander("When to use Short Calls"):
            st.markdown("""
            **Ideal scenarios for Short Calls:**
            * When you expect the price to fall or remain stable
            * When you want to generate income from existing holdings (covered call)
            * When implied volatility is high and you expect it to decrease
            * When you want to effectively sell at a higher price than the current market
            
            **Real-world example:**
            You own 100 shares of XYZ trading at $50, but you don't expect much movement in the coming month.
            You sell a call with a strike price of $55 for a premium of $2 per share ($200 total).
            If the stock stays below $55, you keep the premium as extra income.
            If it rises above $55, you still profit from the stock appreciation up to $55 plus the premium.
            """)
    
    with col2:
        # Short Call parameters
        sc_strike = st.number_input(
            "Strike Price (Short Call)",
            min_value=0.01,
            max_value=current_price * 2,
            value=current_price * 1.1,
            step=0.01,
            format="%.2f",
            key="sc_strike"
        )
        
        # Calculate theoretical premium
        time_to_expiry = days_to_expiration / 365
        sc_premium_calc = black_scholes(current_price, sc_strike, time_to_expiry, risk_free_rate, volatility, "call")
        
        sc_premium = st.number_input(
            "Option Premium (Short Call)",
            min_value=0.01,
            max_value=current_price * 0.5,
            value=float(sc_premium_calc),
            step=0.01,
            format="%.2f",
            key="sc_premium"
        )
        
        # Display calculated values
        st.markdown(f"""
        * **Total Income:** ${sc_premium * contract_size:.2f} ({contract_size} × ${sc_premium:.2f})
        * **Breakeven Price:** ${sc_strike + sc_premium:.2f}
        * **Profit at Current Price:** ${-max(0, current_price - sc_strike) * contract_size + sc_premium * contract_size:.2f}
        """)
        
        # Show the profit/loss chart
        sc_chart = create_option_chart("Short Call", sc_strike, sc_premium, current_price, price_range_percent)
        st.pyplot(sc_chart)
        
        st.markdown(contract_multiplier_note)

####################
# LONG PUT TAB
####################
with tab3:
    st.header("Long Put Strategy")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### 📉 Strategy Overview
        A **Long Put** gives you the right (but not obligation) to sell the underlying asset at the strike price before expiration.
        
        * **Maximum Profit:** Limited to strike price (minus premium) if asset goes to zero
        * **Maximum Loss:** Limited to premium paid
        * **Breakeven Point:** Strike Price - Premium
        * **When to Use:** Bearish outlook - expecting price to fall significantly
        """)
        
        with st.expander("When to use Long Puts"):
            st.markdown("""
            **Ideal scenarios for Long Puts:**
            * When you expect a significant downward movement in price
            * As insurance for existing holdings (protective put)
            * Before anticipated negative events (poor earnings, market corrections)
            * When you want to profit from a decline without selling short
            
            **Real-world example:**
            You own 100 shares of ABC corporation worth $10,000 ($100 per share) and are worried about an upcoming earnings report.
            Rather than selling your shares, you buy a protective put with a strike price of $95 for $3 per share ($300 total).
            If the stock drops to $80 after poor earnings, your put option allows you to effectively sell at $95,
            limiting your loss to $5 per share plus the $3 premium, instead of a $20 per share loss.
            """)
    
    with col2:
        # Long Put parameters
        lp_strike = st.number_input(
            "Strike Price (Long Put)",
            min_value=0.01,
            max_value=current_price * 2,
            value=current_price,
            step=0.01,
            format="%.2f",
            key="lp_strike"
        )
        
        # Calculate theoretical premium
        time_to_expiry = days_to_expiration / 365
        lp_premium_calc = black_scholes(current_price, lp_strike, time_to_expiry, risk_free_rate, volatility, "put")
        
        lp_premium = st.number_input(
            "Option Premium (Long Put)",
            min_value=0.01,
            max_value=current_price * 0.5,
            value=float(lp_premium_calc),
            step=0.01,
            format="%.2f",
            key="lp_premium"
        )
        
        # Display calculated values
        st.markdown(f"""
        * **Total Cost:** ${lp_premium * contract_size:.2f} ({contract_size} × ${lp_premium:.2f})
        * **Breakeven Price:** ${lp_strike - lp_premium:.2f}
        * **Profit at Current Price:** ${max(0, lp_strike - current_price) * contract_size - lp_premium * contract_size:.2f}
        """)
        
        # Show the profit/loss chart
        lp_chart = create_option_chart("Long Put", lp_strike, lp_premium, current_price, price_range_percent)
        st.pyplot(lp_chart)
        
        st.markdown(contract_multiplier_note)

####################
# SHORT PUT TAB
####################
with tab4:
    st.header("Short Put Strategy")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### 📈 Strategy Overview
        A **Short Put** obligates you to buy the underlying asset at the strike price if the option is exercised.
        
        * **Maximum Profit:** Limited to premium received
        * **Maximum Loss:** Up to strike price (minus premium) if asset goes to zero
        * **Breakeven Point:** Strike Price - Premium
        * **When to Use:** Bullish or neutral outlook - expecting price to stay above strike
        """)
        
        with st.expander("When to use Short Puts"):
            st.markdown("""
            **Ideal scenarios for Short Puts:**
            * When you expect the price to rise or remain stable
            * When you're willing to buy the asset at a lower price than current (cash-secured put)
            * When implied volatility is high and you expect it to decrease
            * When you want to generate income in a flat or slightly bullish market
            
            **Real-world example:**
            You want to buy DEF stock currently trading at $75, but you think it's a bit overpriced and would prefer to pay $70.
            You sell a put with a strike price of $70 for a premium of $2 per share ($200 total).
            If the stock stays above $70, you keep the premium as profit.
            If it falls below $70, you'll be assigned the shares at an effective cost of $68 ($70 strike minus $2 premium).
            """)
    
    with col2:
        # Short Put parameters
        sp_strike = st.number_input(
            "Strike Price (Short Put)",
            min_value=0.01,
            max_value=current_price * 2,
            value=current_price * 0.9,
            step=0.01,
            format="%.2f",
            key="sp_strike"
        )
        
        # Calculate theoretical premium
        time_to_expiry = days_to_expiration / 365
        sp_premium_calc = black_scholes(current_price, sp_strike, time_to_expiry, risk_free_rate, volatility, "put")
        
        sp_premium = st.number_input(
            "Option Premium (Short Put)",
            min_value=0.01,
            max_value=current_price * 0.5,
            value=float(sp_premium_calc),
            step=0.01,
            format="%.2f",
            key="sp_premium"
        )
        
        # Display calculated values
        st.markdown(f"""
        * **Total Income:** ${sp_premium * contract_size:.2f} ({contract_size} × ${sp_premium:.2f})
        * **Breakeven Price:** ${sp_strike - sp_premium:.2f}
        * **Profit at Current Price:** ${-max(0, sp_strike - current_price) * contract_size + sp_premium * contract_size:.2f}
        """)
        
        # Show the profit/loss chart
        sp_chart = create_option_chart("Short Put", sp_strike, sp_premium, current_price, price_range_percent)
        st.pyplot(sp_chart)
        
        st.markdown(contract_multiplier_note)

# Interactive Scenario Builder
st.header("Interactive Scenario Builder")

with st.expander("Build Your Own Market Scenario"):
    st.markdown("""
    ### Create a Market Scenario
    
    Test how different options strategies would perform under various market conditions.
    Adjust the expected price movement and see how each strategy would perform.
    """)
    
    # Scenario parameters
    scenario_days = st.slider(
        "Days to Pass Before Checking Performance",
        min_value=1,
        max_value=days_to_expiration,
        value=int(days_to_expiration/2),
        step=1
    )
    
    # Expected price movement
    expected_move = st.slider(
        f"Expected {asset_type} Price Movement",
        min_value=float(-price_range_percent),
        max_value=float(price_range_percent),
        value=0.0,
        step=1.0
    )
    
    # Calculate expected price
    expected_price = current_price * (1 + expected_move/100)
    
    # Expected volatility change
    vol_change = st.slider(
        "Expected Volatility Change (percentage points)",
        min_value=-20,
        max_value=20,
        value=0,
        step=5
    )
    
    expected_vol = max(5, volatility * 100 + vol_change)
    
    st.markdown(f"""
    ### Scenario Summary
    
    * Current {asset_type} Price: **${current_price:.2f}**
    * Expected {asset_type} Price: **${expected_price:.2f}** ({expected_move:+.1f}%)
    * Days Passed: **{scenario_days}** (of {days_to_expiration} days until expiration)
    * Current Volatility: **{volatility*100:.1f}%**
    * Expected Volatility: **{expected_vol:.1f}%** ({vol_change:+d} points)
    """)
    
    if st.button("Calculate Scenario Results"):
        # Calculate remaining time to expiration
        remaining_time = (days_to_expiration - scenario_days) / 365
        
        # Check if scenario takes us to expiration
        if remaining_time <= 0:
            remaining_time = 0.001  # Small non-zero value to avoid division by zero
            
        # New volatility for calculations
        new_volatility = expected_vol / 100
        
        # Function to estimate new option prices
        def estimate_option_value(is_call, strike, original_premium, orig_price, new_price, time_passed, time_remaining, orig_vol, new_vol):
            # For expired options, just calculate intrinsic value
            if time_remaining <= 0.001:
                if is_call:
                    return max(0, new_price - strike)
                else:
                    return max(0, strike - new_price)
            
            # For non-expired options, estimate using Black-Scholes with new parameters
            if is_call:
                new_premium = black_scholes(new_price, strike, time_remaining, risk_free_rate, new_vol, "call")
            else:
                new_premium = black_scholes(new_price, strike, time_remaining, risk_free_rate, new_vol, "put")
                
            return new_premium
        
        # Calculate new premiums for all options
        new_lc_premium = estimate_option_value(True, lc_strike, lc_premium, current_price, expected_price, 
                                              scenario_days/365, remaining_time, volatility, new_volatility)
        new_sc_premium = estimate_option_value(True, sc_strike, sc_premium, current_price, expected_price, 
                                              scenario_days/365, remaining_time, volatility, new_volatility)
        new_lp_premium = estimate_option_value(False, lp_strike, lp_premium, current_price, expected_price, 
                                              scenario_days/365, remaining_time, volatility, new_volatility)
        new_sp_premium = estimate_option_value(False, sp_strike, sp_premium, current_price, expected_price, 
                                              scenario_days/365, remaining_time, volatility, new_volatility)
        
        # Calculate P&L for each strategy
        lc_pl = (new_lc_premium - lc_premium) * contract_size
        sc_pl = (sc_premium - new_sc_premium) * contract_size
        lp_pl = (new_lp_premium - lp_premium) * contract_size
        sp_pl = (sp_premium - new_sp_premium) * contract_size
        
        # Results for each strategy
        results = {
            "Strategy": ["Long Call", "Short Call", "Long Put", "Short Put"],
            "Initial Investment": [
                f"${lc_premium * contract_size:.2f}",
                f"${sc_premium * contract_size:.2f} (received)",
                f"${lp_premium * contract_size:.2f}",
                f"${sp_premium * contract_size:.2f} (received)"
            ],
            "New Value": [
                f"${new_lc_premium * contract_size:.2f}",
                f"${new_sc_premium * contract_size:.2f} (owe)",
                f"${new_lp_premium * contract_size:.2f}",
                f"${new_sp_premium * contract_size:.2f} (owe)"
            ],
            "Profit/Loss": [
                f"${lc_pl:.2f} ({lc_pl/(lc_premium*contract_size)*100:.1f}%)" if lc_premium > 0 else "N/A",
                f"${sc_pl:.2f} ({sc_pl/(sc_premium*contract_size)*100:.1f}%)" if sc_premium > 0 else "N/A",
                f"${lp_pl:.2f} ({lp_pl/(lp_premium*contract_size)*100:.1f}%)" if lp_premium > 0 else "N/A",
                f"${sp_pl:.2f} ({sp_pl/(sp_premium*contract_size)*100:.1f}%)" if sp_premium > 0 else "N/A"
            ]
        }
        
        # Create a DataFrame and display it
        results_df = pd.DataFrame(results)
        st.dataframe(results_df, hide_index=True)
        
        # Visual comparison of P&L
        fig, ax = plt.subplots(figsize=(10, 6))
        strategies = results["Strategy"]
        pl_values = [lc_pl, sc_pl, lp_pl, sp_pl]
        
        # Create bars with colors based on profit/loss
        colors = ['green' if pl >= 0 else 'red' for pl in pl_values]
        ax.bar(strategies, pl_values, color=colors, alpha=0.7)
        
        # Add horizontal line at y=0
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # Formatting
        ax.set_title('Projected Profit/Loss by Strategy', fontweight='bold')
        ax.set_ylabel('Profit/Loss ($)')
        ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f"${x:,.0f}"))
        
        # Add values on top of bars
        for i, v in enumerate(pl_values):
            ax.text(i, v + (5 if v >= 0 else -20), f"${v:.2f}", 
                    ha='center', fontweight='bold', fontsize=9)
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Recommendation based on scenario
        st.subheader("Strategy Analysis")
        
        best_strategy_idx = pl_values.index(max(pl_values))
        best_strategy = strategies[best_strategy_idx]
        
        st.markdown(f"""
        ### Based on your scenario:
        
        The **{best_strategy}** strategy would perform best with a projected profit of **${max(pl_values):.2f}**.
        
        #### Key Takeaways:
        
        * **Price Movement**: {'Upward' if expected_move > 0 else 'Downward' if expected_move < 0 else 'Sideways'} movement 
          generally favors {'bullish strategies (Long Call, Short Put)' if expected_move > 0 else 'bearish strategies (Long Put, Short Call)' if expected_move < 0 else 'neutral strategies with premium collection'}.
          
        * **Time Decay**: As time passes, strategies that involve selling options (Short Call, Short Put) 
          benefit from time decay, while buying options (Long Call, Long Put) work against it.
          
        * **Volatility Changes**: {'Higher' if vol_change > 0 else 'Lower' if vol_change < 0 else 'Stable'} volatility 
          tends to {'increase' if vol_change > 0 else 'decrease' if vol_change < 0 else 'maintain'} option premiums, 
          benefiting {'option buyers' if vol_change > 0 else 'option sellers' if vol_change < 0 else 'neither buyers nor sellers significantly'}.
        """)

# Strategy comparison section
st.header("Compare All Strategies")

if st.button("Generate Strategy Comparison"):
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()
    
    # Generate charts for each strategy
    strategies = ["Long Call", "Short Call", "Long Put", "Short Put"]
    strikes = [lc_strike, sc_strike, lp_strike, sp_strike]
    premiums = [lc_premium, sc_premium, lp_premium, sp_premium]
    
    # Price range for x-axis
    min_price = current_price * (1 - price_range_percent / 100)
    max_price = current_price * (1 + price_range_percent / 100)
    prices = np.linspace(min_price, max_price, 1000)
    
    for i, (strategy, strike, premium) in enumerate(zip(strategies, strikes, premiums)):
        # Calculate profits for each strategy
        if strategy == "Long Call":
            profits = np.maximum(prices - strike, 0) * contract_size - premium * contract_size
        elif strategy == "Short Call":
            profits = -np.maximum(prices - strike, 0) * contract_size + premium * contract_size
        elif strategy == "Long Put":
            profits = np.maximum(strike - prices, 0) * contract_size - premium * contract_size
        elif strategy == "Short Put":
            profits = -np.maximum(strike - prices, 0) * contract_size + premium * contract_size
        
        # Plot 
        axes[i].plot(prices, profits, linewidth=2, color='blue')
        
        # Add horizontal and vertical lines
        axes[i].axhline(y=0, color='black', linestyle='-', alpha=0.3, linewidth=1)
        axes[i].axvline(x=strike, color='red', linestyle='--', alpha=0.7, linewidth=1)
        axes[i].axvline(x=current_price, color='green', linestyle='--', alpha=0.7, linewidth=1)
        
        # Fill above/below 0
        axes[i].fill_between(prices, profits, 0, where=(profits > 0), color='green', alpha=0.3)
        axes[i].fill_between(prices, profits, 0, where=(profits <= 0), color='red', alpha=0.3)
        
        # Set labels and title
        axes[i].set_xlabel("Price at Expiration", fontsize=10)
        axes[i].set_ylabel("Profit/Loss ($)", fontsize=10)
        axes[i].set_title(f"{strategy} P&L at Expiration", fontsize=12, fontweight='bold')
        
        # Format y-axis as currency
        axes[i].yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f"${x:,.0f}"))
        
        # Add grid
        axes[i].grid(True, alpha=0.3)
        
        # Annotate strike and current price
        axes[i].annotate(f"S={strike:.2f}", (strike, 0), xytext=(5, -15), textcoords="offset points", color='red', fontsize=8)
        axes[i].annotate(f"C={current_price:.2f}", (current_price, 0), xytext=(5, -30), textcoords="offset points", color='green', fontsize=8)
    
    # Adjust layout and spacing
    plt.tight_layout()
    st.pyplot(fig)
    
    # Strategy summary table
    strategy_data = {
        "Strategy": strategies,
        "Strike Price": [f"${strike:.2f}" for strike in strikes],
        "Premium": [f"${premium:.2f}" for premium in premiums],
        "Max Profit": [
            "Unlimited",
            f"${sc_premium * contract_size:.2f}",
            f"${(lp_strike - lp_premium) * contract_size:.2f}",
            f"${sp_premium * contract_size:.2f}"
        ],
        "Max Loss": [
            f"${lc_premium * contract_size:.2f}",
            "Unlimited",
            f"${lp_premium * contract_size:.2f}",
            f"${(sp_strike - sp_premium) * contract_size:.2f}"
        ],
        "Breakeven": [
            f"${lc_strike + lc_premium:.2f}",
            f"${sc_strike + sc_premium:.2f}",
            f"${lp_strike - lp_premium:.2f}",
            f"${sp_strike - sp_premium:.2f}"
        ],
        "Outlook": ["Bullish", "Bearish/Neutral", "Bearish", "Bullish/Neutral"]
    }
    
    df = pd.DataFrame(strategy_data)
    st.dataframe(df, hide_index=True)

# Educational tabs
st.header("Educational Resources")
ed_tab1, ed_tab2, ed_tab3 = st.tabs(["Advanced Concepts", "Case Studies", "Risk Management"])

# Advanced concepts tab
with ed_tab1:
    st.markdown("""
    ### The Greeks: Factors Affecting Option Prices
    
    Options prices are influenced by several factors, often referred to as "The Greeks":
    
    * **Delta (Δ)** - How much the option price changes when the underlying asset price changes by $1
    * **Gamma (Γ)** - Rate of change of Delta (the "acceleration" of the option price)
    * **Theta (Θ)** - Time decay; how much the option loses value each day
    * **Vega (V)** - How much the option price changes when implied volatility changes
    * **Rho (ρ)** - How much the option price changes when interest rates change
    
    ### Options Pricing: Black-Scholes Model
    
    The Black-Scholes model is the foundational mathematical model for options pricing. It calculates a theoretical price for European-style options based on these inputs:
    
    * **Current price** of the underlying asset
    * **Strike price** of the option
    * **Time until expiration** (in years)
    * **Risk-free interest rate** (usually Treasury bill rate)
    * **Implied volatility** of the underlying asset
    
    This app uses Black-Scholes to calculate theoretical option premiums, but remember that real market prices often deviate from theoretical values due to supply and demand dynamics.
    
    ### Options Strategies Beyond the Basics
    
    While this app focuses on the four basic option positions, traders often combine these into more complex strategies:
    
    * **Vertical Spreads**:
      * **Bull Call Spread**: Buy a call + sell a higher strike call (bullish, defined risk/reward)
      * **Bear Put Spread**: Buy a put + sell a lower strike put (bearish, defined risk/reward)
      * **Credit Spreads**: Sell options spreads to collect premium (bull put/bear call spreads)
    
    * **Neutral Strategies**:
      * **Straddle**: Buy a call + buy a put at the same strike (profit from big moves either direction)
      * **Strangle**: Buy a call + buy a put at different strikes (cheaper than straddle, needs bigger move)
      * **Iron Condor**: Sell an OTM call spread + sell an OTM put spread (profit if price stays in range)
      * **Butterfly**: Buy one option + sell two at middle strike + buy one at far strike (profit if price hits middle)
    
    * **Stock + Options Strategies**:
      * **Covered Call**: Own 100 shares + sell a call (generate income, willing to sell shares)
      * **Cash-Secured Put**: Cash to buy 100 shares + sell a put (generate income, willing to buy shares)
      * **Protective Put**: Own 100 shares + buy a put (insurance against big drops)
      * **Collar**: Own 100 shares + buy a put + sell a call (protected position with limited upside)
    
    ### Intrinsic vs. Extrinsic Value
    
    Every option's premium consists of:
    
    * **Intrinsic Value** - The amount the option is "in-the-money" (if any)
    * **Extrinsic Value** (Time Value) - The remaining premium based on time and volatility
    
    As expiration approaches, extrinsic value decreases (theta decay), while intrinsic value remains based on the difference between market price and strike price.
    """)

# Case studies tab
with ed_tab2:
    st.markdown("""
    ## Real-World Options Trading Case Studies
    
    ### Case Study 1: Earnings Anticipation (Long Straddle)
    
    **Scenario**: A technology company is about to announce quarterly earnings. The market expects significant movement, but the direction is uncertain.
    
    **Strategy**: A trader buys both a call option and a put option at the same strike price (at-the-money), creating a **Long Straddle**.
    
    **Example**:
    - XYZ Tech trades at $100/share
    - Trader buys $100 strike call for $5
    - Trader buys $100 strike put for $5
    - Total investment: $10 per share ($1,000 for one contract)
    
    **Outcomes**:
    - If stock jumps to $120: Call worth $20, put worth $0, profit = $10
    - If stock drops to $80: Call worth $0, put worth $20, profit = $10
    - If stock stays at $100: Both options expire worthless, loss = $10
    
    **Key Lesson**: When you expect a big move but are uncertain of direction, a straddle can be effective, but the stock needs to move enough to overcome the combined premium costs.
    
    ---
    
    ### Case Study 2: Income Generation (Covered Call)
    
    **Scenario**: An investor owns 100 shares of a stable blue-chip stock and wants to generate additional income.
    
    **Strategy**: The investor sells a call option against their shares, creating a **Covered Call**.
    
    **Example**:
    - Investor owns 100 shares of ABC Corp at $50/share ($5,000 investment)
    - Sells a $55 strike call expiring in 45 days for $2/share ($200 premium)
    
    **Outcomes**:
    - If stock stays below $55: Option expires worthless, investor keeps $200 premium (4% return in 45 days)
    - If stock rises above $55: Shares get called away at $55, investor profits from share appreciation ($500) plus premium ($200)
    
    **Key Lesson**: Covered calls can enhance portfolio returns but limit upside potential. They're most effective in sideways or slightly bullish markets.
    
    ---
    
    ### Case Study 3: Protective Strategy (Protective Put)
    
    **Scenario**: A portfolio manager has a large position in an index fund but is concerned about short-term market turbulence.
    
    **Strategy**: The manager buys put options to protect the position, creating a **Protective Put** (or "portfolio insurance").
    
    **Example**:
    - Fund holds $1 million in S&P 500 index fund at $450/share
    - Buys 10-month $425 put options (5% OTM) for $15/share ($33,333 total cost)
    
    **Outcomes**:
    - If market drops 20%: Fund loses $200,000 in value, but puts gain approximately $167,000, limiting net loss
    - If market remains flat or rises: Insurance "expires worthless" like home insurance when your house doesn't burn down
    
    **Key Lesson**: Protective puts act as insurance policies. They have a cost that reduces returns in good times but provide valuable protection during market downturns.
    
    ---
    
    ### Case Study 4: Stock Replacement (Long Call)
    
    **Scenario**: An investor is bullish on a high-priced stock but doesn't want to commit the full capital required to buy shares.
    
    **Strategy**: Instead of buying shares, the investor purchases deep in-the-money **Long Calls** as a stock replacement strategy.
    
    **Example**:
    - DEF Inc. trades at $800/share
    - Instead of buying 100 shares ($80,000), investor buys $700 strike calls for $120/share ($12,000)
    
    **Outcomes**:
    - If stock rises to $900: Calls worth $200/share, 67% gain vs. 12.5% gain owning shares
    - If stock drops to $700: Calls retain some value, loss is capped at premium paid
    
    **Key Lesson**: Using deep ITM calls as stock replacements provides leverage with defined risk, but theta decay works against the position as expiration approaches.
    """)

# Risk management tab
with ed_tab3:
    st.markdown("""
    ## Options Risk Management Guidelines
    
    ### Position Sizing
    
    One of the most common mistakes options traders make is taking positions that are too large relative to their account size.
    
    **Guidelines**:
    - Limit single options positions to 1-5% of your portfolio value
    - For more complex strategies (spreads, iron condors), limit to 2-7% per strategy
    - Consider reducing position sizes for higher volatility underlyings
    
    **Example**: With a $100,000 account, a single long call position might be limited to $2,000-$5,000 in premium.
    
    ---
    
    ### Risk-to-Reward Ratios
    
    Before entering any options trade, calculate your potential profit and loss scenarios.
    
    **Guidelines**:
    - For directional trades (long calls/puts): Aim for at least 2:1 reward-to-risk ratio
    - For credit spreads: Aim for profit potential of at least 20-30% of the maximum risk
    - For iron condors: Look for potential profit of 15-25% of the maximum risk
    
    **Example**: If risking $500 on a long call, the target profit should be at least $1,000.
    
    ---
    
    ### Managing Winners and Losers
    
    Setting exit rules before entering trades helps remove emotion from decision-making.
    
    **Guidelines for Long Options**:
    - Consider taking profits at 50-100% gain
    - Consider cutting losses at 30-50% of premium paid
    - Create a time-based exit plan (e.g., exit if not profitable within 50% of time to expiration)
    
    **Guidelines for Short Options**:
    - Consider taking profits at 50-75% of maximum potential profit
    - Consider adjusting positions if losses approach 1.5-2x expected profit
    - Be cautious about holding short options into expiration week (gamma risk)
    
    ---
    
    ### Volatility Considerations
    
    Implied volatility significantly impacts options pricing and strategy selection.
    
    **Guidelines**:
    - Check implied volatility (IV) percentile before trading
    - In high IV environments: Consider selling options (credit spreads, iron condors)
    - In low IV environments: Consider buying options (long calls/puts, debit spreads)
    - Be aware of upcoming events that might cause volatility spikes (earnings, FDA decisions, etc.)
    
    ---
    
    ### Diversification Principles
    
    Even with prudent position sizing, diversification remains important.
    
    **Guidelines**:
    - Diversify across different underlyings (don't only trade tech stocks)
    - Diversify across strategies (some directional, some neutral)
    - Diversify across time frames (different expiration dates)
    - Balance positive and negative vega/theta exposures
    
    ---
    
    ### Managing Assignment Risk
    
    For short options positions, understanding and planning for potential assignment is crucial.
    
    **Guidelines**:
    - Maintain sufficient margin/cash for potential assignment
    - Be especially cautious with short options on dividend-paying stocks near ex-dividend dates
    - Consider closing short options that are deeply in-the-money before expiration
    - Understand how to handle assignment (conversion to stock position, delivery of futures, etc.)
    
    ---
    
    ### Warning Signs to Exit Trades Early
    
    Sometimes the prudent action is to exit a trade before your planned stop loss.
    
    **Warning Signs**:
    - Unexpected announcement affecting the underlying
    - Significant changes in the broader market conditions
    - Abnormal implied volatility changes
    - Technical breakouts/breakdowns beyond your planned price range
    """)

# Conclusion section
st.header("Conclusion: Next Steps in Your Options Journey")

st.markdown("""
### Continuing Your Options Education

This simulator provides a foundation for understanding basic options strategies, but options trading is a deep field with much to learn:

1. **Paper Trading**: Before risking real money, consider practicing in a paper trading account
2. **Start Simple**: Begin with covered calls or cash-secured puts if you already own or want to own the underlying asset
3. **Continuous Learning**: Options markets are dynamic - keep learning about advanced strategies and risk management

### Key Takeaways

* Options provide leverage, allowing control of more assets with less capital
* Every strategy has tradeoffs between risk, reward, and probability of profit
* Time decay (theta) benefits option sellers but works against option buyers
* Implied volatility significantly impacts options pricing and strategy selection
* Position sizing and risk management are critical to long-term success

### Feedback and Improvements

We value your feedback on this educational tool! Please help us improve by sharing your experience:
""")

feedback = st.text_area("Suggestions for Improvement:", height=100)
rating = st.slider("Rate this simulator (1-5 stars):", 1, 5, 3)

if st.button("Submit Feedback"):
    st.success("Thank you for your feedback! We'll use it to improve future versions of this educational tool.")

st.markdown("""
---
*Disclaimer: This app is for educational purposes only. Options trading involves significant risk of loss and is not suitable for all investors.*

*© 2025 Options Trading Simulator | Created with Streamlit*
""")