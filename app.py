import datetime
import os
import pickle

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

import ai


load_dotenv()

st.set_page_config(page_title="Booking check", page_icon="✦", layout="wide")
st.markdown(
    """
    <style>
        :root { --ink: #18211d; --muted: #68736d; --paper: #f7f7f2; --line: #dde2d9; --green: #236344; --amber: #a44e25; }
        .stApp { background: linear-gradient(135deg, #f8f8f3 0%, #f3f6f0 100%); color: var(--ink); }
        [data-testid="stSidebar"] { background: #c8d9c9; border-right: 1px solid #abc1ae; min-width: 340px; }
        [data-testid="stSidebar"] > div:first-child { min-width: 340px; }
        [data-testid="stSidebar"] > div:first-child { padding-top: 2rem; }
        h1 { font-size: 2.25rem !important; letter-spacing: -.055em; margin-bottom: .15rem !important; }
        h2, h3 { letter-spacing: -.025em; }
        .eyebrow { color: var(--green); font-size: .72rem; font-weight: 700; letter-spacing: .11em; text-transform: uppercase; }
        .subtitle { color: var(--muted); font-size: 1rem; margin-bottom: 1.8rem; }
        .card { background: #fffefb; border: 1px solid var(--line); border-radius: 12px; padding: 1.35rem; min-height: 148px; box-shadow: 0 8px 22px rgba(30, 62, 42, .055); }
        .card-label { color: var(--muted); font-size: .75rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
        .score { font-size: 2.3rem; font-weight: 700; letter-spacing: -.06em; line-height: 1.15; margin: .35rem 0; }
        .note { color: var(--muted); font-size: .9rem; }
        .stButton > button { background: #236344; border: 1px solid #236344; border-radius: 7px; color: white; font-weight: 650; padding: .55rem 1rem; box-shadow: 0 4px 10px rgba(35, 99, 68, .18); }
        .stButton > button:hover { background: var(--green); border-color: var(--green); color: white; }
        [data-testid="stMetric"] { background: #fffefb; border: 1px solid var(--line); border-radius: 10px; padding: .8rem; box-shadow: 0 5px 14px rgba(30, 62, 42, .04); }
        [data-testid="stMetricValue"] { color: var(--green); }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: #397354; font-weight: 750; letter-spacing: .08em; }
        [data-testid="stSidebar"] [data-testid="stTextInput"], [data-testid="stSidebar"] [data-testid="stSelectbox"], [data-testid="stSidebar"] [data-testid="stNumberInput"] { background: rgba(255, 255, 255, .35); border-radius: 7px; }
        hr { border-color: var(--line); }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_resources():
    try:
        with open("rf_model.pkl", "rb") as file:
            model = pickle.load(file)
        with open("encoders.pkl", "rb") as file:
            encoders = pickle.load(file)
        return model, encoders
    except FileNotFoundError:
        return None, None


model, encoders = load_resources()
if model is None:
    st.error("The prediction model could not be found.")
    st.stop()

with st.sidebar:
    st.markdown("<p class='eyebrow'>Booking desk</p>", unsafe_allow_html=True)
    st.title("Guest details")
    customer_name = st.text_input("Guest name", placeholder="e.g. Maya Shah")
    customer_email = st.text_input("Email", placeholder="maya@example.com")

    st.markdown("---")
    st.caption("STAY")
    booking_date = st.date_input("Booked on", datetime.date.today())
    arrival_date = st.date_input("Arrival", min_value=booking_date)
    hotel = st.selectbox("Property", encoders["hotel"].classes_)
    total_stay = st.number_input("Nights", min_value=1, value=3)
    adr = st.number_input("Nightly rate (₹)", min_value=0.0, value=100.0)

    st.markdown("---")
    st.caption("CONTEXT")
    market_segment = st.selectbox("Market segment", encoders["market_segment"].classes_)
    country = st.selectbox("Country", encoders["country"].classes_)
    special_requests = st.number_input("Special requests", min_value=0, value=0)
    booking_changes = st.number_input("Booking changes", min_value=0, value=0)

    st.markdown("---")
    st.caption("HISTORY")
    prev_cancellations = st.number_input("Previous cancellations", min_value=0, value=0)
    prev_bookings = st.number_input("Previous completed stays", min_value=0, value=0)

    run_check = st.button("Check booking", use_container_width=True)

lead_time = (arrival_date - booking_date).days
arrival_day = arrival_date.day
arrival_month = arrival_date.strftime("%B")
name = customer_name.strip() or "Guest"

st.markdown("<p class='eyebrow'>Operations / cancellation likelihood</p>", unsafe_allow_html=True)
st.title("A quick read on this booking.")
st.markdown("<p class='subtitle'>Use the signal to decide whether the guest needs a thoughtful nudge.</p>", unsafe_allow_html=True)

overview = st.columns(3)
overview[0].metric("Arrival", arrival_date.strftime("%d %b %Y"))
overview[1].metric("Lead time", f"{lead_time} days")
overview[2].metric("Stay value", f"₹{adr * total_stay:,.0f}")

if run_check:
    input_df = pd.DataFrame({
        "hotel": [hotel], "lead_time": [lead_time], "arrival_date_month": [arrival_month],
        "arrival_date_day_of_month": [arrival_day], "total_stay": [total_stay],
        "market_segment": [market_segment], "country": [country],
        "previous_cancellations": [prev_cancellations], "booking_changes": [booking_changes],
        "total_of_special_requests": [special_requests], "adr": [adr],
    })
    for column, encoder in encoders.items():
        input_df[column] = encoder.transform(input_df[column].astype(str))

    cancellation_probability = model.predict_proba(input_df)[0][1]
    is_risky = model.predict(input_df)[0] == 1
    loyalty = "Returning guest" if prev_bookings else "First stay"
    if prev_cancellations:
        loyalty = f"{prev_cancellations} earlier cancellation{'s' if prev_cancellations != 1 else ''}"

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns((1.15, 1))
    with left:
        label = "Needs attention" if is_risky else "Looks steady"
        tone = "var(--amber)" if is_risky else "var(--green)"
        description = "A personal confirmation or flexible option may help secure this stay." if is_risky else "No immediate outreach is needed based on this booking profile."
        st.markdown(
            f"<div class='card'><div class='card-label'>Cancellation risk</div>"
            f"<div class='score' style='color:{tone}'>{cancellation_probability:.0%}</div>"
            f"<strong>{label}</strong><br><span class='note'>{description}</span></div>",
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            f"<div class='card'><div class='card-label'>Guest context</div>"
            f"<div class='score'>{loyalty}</div>"
            f"<span class='note'>{prev_bookings} completed stay{'s' if prev_bookings != 1 else ''} on record · {special_requests} special request{'s' if special_requests != 1 else ''}</span></div>",
            unsafe_allow_html=True,
        )

    if is_risky:
        details = {"market_segment": market_segment, "lead_time": lead_time, "country": country}
        with st.spinner("Preparing a retention idea…"):
            strategy = ai.get_retention_strategy(os.getenv("HF_TOKEN"), details)

        st.markdown("### Suggested next step")
        st.info(strategy)
        st.markdown("### Ready-to-send note")
        channel = st.radio("Channel", ["WhatsApp", "Email"], horizontal=True, label_visibility="collapsed")
        if channel == "WhatsApp":
            message = f"Hi {name}, we're looking forward to welcoming you to {hotel}. {strategy} Reply YES and we'll take care of the rest. — Guest Services"
        else:
            message = f"Dear {name},\n\nWe're looking forward to your stay at {hotel}. {strategy}\n\nReply to this email and our team will be happy to help.\n\nGuest Services"
        st.text_area("Message", message, height=140)
else:
    st.caption("Complete the details in the sidebar, then select **Check booking**.")
