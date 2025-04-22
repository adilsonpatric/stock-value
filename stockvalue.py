import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Valuation App", layout="centered")
st.title("📊 Stock Valuation Calculator")

# Input do usuário
ticker = st.text_input("Enter the Ticker Symbol (e.g., QFIN, PDD, JD)").upper()
methods = st.multiselect(
    "Select Valuation Methods:",
    ["Graham Formula", "Discounted Cash Flow (DCF)", "Multiples"]
)

if ticker and methods:
    stock = yf.Ticker(ticker)
    info = stock.info

    try:
        eps = info.get("trailingEps")
        price = info.get("regularMarketPrice")
        shares_outstanding = info.get("sharesOutstanding")
        net_income = info.get("netIncomeToCommon")
        sector_pe = info.get("forwardPE")  # Rough estimate

        st.write(f"### Current Price: ${price:.2f}")
        st.write(f"EPS: {eps}")

        if "Graham Formula" in methods:
            growth = st.number_input("Estimated Growth Rate (%) for Graham", value=10)
            graham_value = eps * (8.5 + 2 * growth)
            st.subheader("🔹 Graham Formula")
            st.write(f"Intrinsic Value: **${graham_value:.2f}**")

        if "Discounted Cash Flow (DCF)" in methods:
            st.subheader("🔹 Discounted Cash Flow (DCF)")
            fcf = st.number_input("Free Cash Flow (or Net Income, in billions)", value=net_income / 1e9 if net_income else 1.0)
            growth_rate = st.number_input("Growth Rate (%)", value=15.0)
            discount_rate = st.number_input("Discount Rate (%)", value=10.0)
            years = 5

            fcf_values = [fcf * ((1 + growth_rate / 100) ** i) for i in range(1, years + 1)]
            fcf_pv = sum([v / ((1 + discount_rate / 100) ** i) for i, v in enumerate(fcf_values, start=1)])
            terminal_value = fcf_values[-1] * (1 + growth_rate / 100) / ((discount_rate - growth_rate) / 100)
            terminal_pv = terminal_value / ((1 + discount_rate / 100) ** years)
            total_value = (fcf_pv + terminal_pv) * 1e9  # Convert back to full value

            if shares_outstanding:
                intrinsic_value_dcf = total_value / shares_outstanding
                st.write(f"Intrinsic Value per Share: **${intrinsic_value_dcf:.2f}**")
            else:
                st.warning("Could not fetch shares outstanding to calculate per-share value.")

        if "Multiples" in methods:
            st.subheader("🔹 Valuation by Multiples")
            custom_pe = st.number_input("Enter Sector or Expected P/E Ratio", value=sector_pe or 15.0)
            if eps:
                value_by_multiples = eps * custom_pe
                st.write(f"Intrinsic Value: **${value_by_multiples:.2f}**")
            else:
                st.warning("EPS not available to calculate multiples valuation.")

    except Exception as e:
        st.error(f"Error fetching data or computing values: {e}")
