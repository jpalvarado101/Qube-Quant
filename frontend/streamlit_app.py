import os
import requests
import streamlit as st

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Buy / Sell / Hold", page_icon="📈", layout="centered")
st.title("📈 Simple Buy / Sell / Hold")

symbol = st.text_input("Ticker symbol", value="AAPL").upper()

if st.button("Get Signal"):
    try:
        resp = requests.post(f"{API_URL}/predict", json={"symbol": symbol}, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            action = data["action"]
            conf = data["confidence"]
            st.metric(label=f"{symbol} as of {data['as_of']}", value=action, delta=f"confidence {conf:.2%}")
            if action == "BUY":
                st.success("BUY ✅")
            elif action == "SELL":
                st.error("SELL ❌")
            else:
                st.info("HOLD ⏸️")
        else:
            st.warning(resp.text)
    except Exception as e:
        st.warning(str(e))

st.caption("Signals are for educational purposes only and not financial advice.")
