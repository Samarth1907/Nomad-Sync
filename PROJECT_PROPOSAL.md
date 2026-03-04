# Nomad-Sync: The Collaborative Multi-Agent Travel Engine

## The Team
**Name of your Institute:** Indian Institute of Technology, Madras  
**Your Team Name:** MysteryMolecules  
**Challenge Area:** Track 4: Agent Teamwork  
**Registered Email ID of your Team Lead:** cs24b051@smail.iitm.ac.in  

Our team is a blend of competitive programmers and systems enthusiasts who share a passion for optimizing complex workflows. Having previously worked on low-latency C++ guides and game-theory bot strategies, we realized that the ‘travel planning’ problem is essentially a multi-constraint optimization puzzle. We decided to join AI Unlocked to apply agentic architecture to the chaos of group travel, moving away from static spreadsheets to dynamic, autonomous execution.

## The Concept
Planning a trip with a ‘normal trip gang’ usually results in 100+ disjointed messages and ‘planning fatigue’. Nomad-Sync solves this by deploying a trio of specialized AI agents that work in harmony to build, validate, and book a trip. 

Unlike traditional LLM wrappers, our system uses a Planner to draft the route, a Retriever to pull live regional data (like spots in Mahabalipuram or traffic patterns in Chennai), and an Executor to handle the logistics like calendar syncing and expense splitting. We solve the "hallucination" problem by forcing the agents to cross-verify every suggestion against real-world APIs before presenting it to the user.

## Target Audience or Market
*   **Primary Audience:** Gen Z and Millennial ‘trip gangs’ in India who prefer experience-based travel but lack the time for manual itinerary building.
*   **Geography:** Initially focusing on the Indian domestic travel market (e.g., weekend getaways from Tier-1 tech hubs like Chennai or Bangalore).
*   **Market Size:** With India’s domestic travel market projected to reach $150B+ by 2027, even a 1% penetration into the digital-first student/professional demographic represents a massive user base.

## Personas
1.  **Arjun, the ‘Overwhelmed Organizer’:** A 21-year-old CS student who wants to take 5 friends to Mahabalipuram but is tired of manually checking bus timings and entry fees. 
2.  **Sanya, the ‘Budget-Conscious Explorer’:** A young professional who wants a high-density 2-day itinerary that maximizes "sight-seeing per Rupee" without the stress of logistics.

## How it Works
We built Nomad-Sync using Microsoft AutoGen to manage the ‘agent-to-agent’ dialogue.
*   **Azure OpenAI Service** provides the reasoning backbone (GPT-4o) for our Planner Agent.
*   **Azure Maps API** allows the Retriever Agent to cluster locations geographically to minimize travel time.
*   **Azure Container Apps** ensures our Executor Agent can run Python scripts to generate PDF itineraries and .ics files in a scalable, isolated environment.

## Core Technologies
*   **Microsoft AutoGen:** For agent orchestration and state management.
*   **Azure OpenAI (GPT-4o):** For multimodal intent processing.
*   **Azure Maps:** For distance-matrix calculations and local POI data.
*   **Python/C++ Hybrid:** Using C++ for low-latency route-optimization algorithms where necessary.

## The Business Plan
We envision a B2B2C model. While the base planner is free for students, we can partner with local travel aggregators to provide "One-Click Booking" for the entire generated itinerary, earning a lead-generation commission for every hotel or transport booking made through the agents.
