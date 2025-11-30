import streamlit as st
import pandas as pd
import pickle
import urllib.parse
import os
from dotenv import load_dotenv
import ai
import datetime

load_dotenv()

st.set_page_config(page_title="Hotel Booking", layout="wide")

@st.cache_resource
def load_resources():
    try:
        with open('rf_model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('encoders.pkl', 'rb') as f:
            encoders = pickle.load(f)
        return model, encoders
    except FileNotFoundError:
        return None, None

model, encoders = load_resources()

st.sidebar.title("Customer Details")

if not model:
    st.error("Model files not found.")
    st.stop()
customer_name = st.sidebar.text_input("Customer Name")
name = customer_name if customer_name else "Guest"
customer_email = st.sidebar.text_input("Customer Email")
booking_date = st.sidebar.date_input("Booking Date", datetime.date.today())

arrival_date = st.sidebar.date_input("Arrival Date")

lead_time = (arrival_date - booking_date).days
arrival_day = arrival_date.day
arrival_month = arrival_date.strftime("%B")

st.sidebar.write(f"Lead Time: **{lead_time} days**")
st.sidebar.write(f"Arrival Day: **{arrival_day}**")
st.sidebar.write(f"Arrival Month: **{arrival_month}**")
hotel = st.sidebar.selectbox("Hotel Type", encoders['hotel'].classes_)
market_segment = st.sidebar.selectbox("Market Segment", encoders['market_segment'].classes_)
country = st.sidebar.selectbox("Country", encoders['country'].classes_, index=0)

total_stay = st.sidebar.number_input("Total Stay (nights)", value=3)
adr = st.sidebar.number_input("Price per Night (ADR)", value=100.0)
special_requests = st.sidebar.number_input("Special Requests", value=0)
booking_changes = st.sidebar.number_input("Booking Changes", value=0)

st.sidebar.markdown("---")
st.sidebar.subheader("History (For Loyalty)")
prev_cancellations = st.sidebar.number_input("Past Cancellations", value=0)
prev_bookings = st.sidebar.number_input("Past Successful Bookings", value=0)

hf_token = os.getenv("HF_TOKEN")

st.title("Hotel Booking Cancellation Risk Analyzer")

if "show_results" not in st.session_state:
    st.session_state.show_results = False

if st.button("Analyze Booking Risk"):
    st.session_state.show_results = True

if st.session_state.show_results:

    input_df = pd.DataFrame({
        'hotel': [hotel], 'lead_time': [lead_time], 'arrival_date_month': [arrival_month],
        'arrival_date_day_of_month': [arrival_day], 'total_stay': [total_stay],
        'market_segment': [market_segment], 'country': [country],
        'previous_cancellations': [prev_cancellations], 'booking_changes': [booking_changes],
        'total_of_special_requests': [special_requests], 'adr': [adr]
    })

    for col, enc in encoders.items():
        input_df[col] = enc.transform(input_df[col].astype(str))

    pred = model.predict(input_df)[0]
    prob = model.predict_proba(input_df)[0][1]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Prediction")
        if pred == 1:
            st.error(f" High Cancellation Risk ({prob:.0%} chance)")
            is_risky = True
        else:
            st.success(f"Safe Booking ({1-prob:.0%} chance)")
            is_risky = False

    with col2:
        st.subheader("Loyalty Check")
        if prev_bookings > 0 and prev_cancellations == 0:
            st.balloons()
            st.info(f"Loyal Customer! ({prev_bookings} past stays). Award 500 Points.")
        elif prev_cancellations > 0:
            st.warning("High Risk History. No points.")
        else:
            st.write("New Customer.")

    if is_risky:
        st.markdown("---")
        st.subheader("Customer Retention Plan")

        with st.spinner("AI is generating a custom offer..."):
            details = {"market_segment": market_segment, "lead_time": lead_time, "country": country}
            strategy_text = ai.get_retention_strategy(hf_token, details)
            st.info(f"**Insight:** {strategy_text}")
        st.markdown("---")
        st.subheader("Booking Summary")

        st.write(f"**Guest Name:** {name}")
        st.write(f"**Hotel:** {hotel}")
        st.write(f"**Arrival Date:** {arrival_date}")
        st.write(f"**Total Stay:** {total_stay} nights")
        st.write(f"**ADR:** ₹{adr}")
        st.write(f"**Lead Time:** {lead_time} days")

        st.markdown("---")
        st.subheader("Customer Outreach")

        if "msg_format" not in st.session_state:
            st.session_state.msg_format = "WhatsApp Format"

        format_type = st.radio(
            "Choose Message Format",
            ["WhatsApp Format", "Email Format"],
            index=0 if st.session_state.msg_format == "WhatsApp Format" else 1,
            horizontal=True,
            key="msg_format"
        )

        whatsapp_msg = (
            f"Hi {name}, We noticed your upcoming stay at {hotel} may need confirmation.\n\n"
            f"Special Offer: {strategy_text}\n\n"
            f"Reply 'YES' to claim this offer!\n\n"
            f"Best regards,\nGuest Services"
        )
        email_msg = (
            f"Dear {name},\n\n"
            f"We noticed that your booking at {hotel} may not be fully confirmed yet.\n"
            f"To help you finalize, we are pleased to offer:\n\n"
            f"{strategy_text}\n\n"
            f"Please reply to this email to claim the offer.\n\n"
            f"Warm regards,\nGuest Services Team"
        )

        st.write("### Message Preview")
        if st.session_state.msg_format == "WhatsApp Format":
            final_msg = st.text_area("WhatsApp Message", whatsapp_msg, height=200, key="wa_msg")
        else:
            final_msg = st.text_area("Email Message", email_msg, height=250, key="email_msg")
        