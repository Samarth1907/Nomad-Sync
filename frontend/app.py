import streamlit as st
import requests

st.title("Nomad-Sync Travel Planner")

start = st.text_input("Start City")
dest = st.text_input("Destination")
days = st.number_input("Days",1,10,2)
budget = st.number_input("Budget",1000,20000,5000)

if st.button("Generate Trip"):
    payload = {
        "start_city": start,
        "destination": dest,
        "days": days,
        "budget": budget,
        "people": 5
    }

    with st.spinner("Generating trip plan..."):
        try:
            r = requests.post("http://backend:8000/plan_trip", json=payload)
            r.raise_for_status()
            st.success("Trip plan generated!")
            st.write(r.json())
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to the backend: {e}")
