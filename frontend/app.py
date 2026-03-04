import streamlit as st
import requests

st.title("Nomad-Sync Travel Planner")
st.markdown("Collaborative Multi-Agent Travel Engine powered by Azure AI & AutoGen")

start = st.text_input("Origin City", value="Chennai")
dest = st.text_input("Destination", value="Mahabalipuram")
days = st.number_input("Days", 1, 10, 2)
budget = st.number_input("Budget (INR)", 500, 50000, 5000)
people = st.number_input("Number of Travelers", 1, 20, 2)
interests_str = st.text_input("Interests (comma separated)", value="temples, beaches, food")

if st.button("Generate Trip"):
    interests = [i.strip() for i in interests_str.split(",") if i.strip()]
    payload = {
        "origin": start,
        "destination": dest,
        "num_days": days,
        "budget": budget,
        "num_travelers": people,
        "interests": interests
    }

    with st.spinner("Agents are collaborating to build your itinerary..."):
        try:
            # Change URL to match the backend's exposed endpoint
            r = requests.post("http://localhost:8000/api/plan-trip", json=payload)
            r.raise_for_status()
            data = r.json()
            st.success("Trip plan generated successfully!")

            trip_id = data.get("trip_id")
            if trip_id:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**[📄 Download PDF Itinerary](http://localhost:8000/api/download/{trip_id}/pdf)**")
                with col2:
                    st.markdown(f"**[📅 Download ICS Calendar](http://localhost:8000/api/download/{trip_id}/ics)**")

            st.json(data)
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to the backend: {e}")
