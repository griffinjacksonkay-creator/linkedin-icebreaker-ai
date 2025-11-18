import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")  # or st.secrets

st.set_page_config(page_title="LinkedIn Icebreaker AI", page_icon="💬")
st.title("LinkedIn Icebreaker AI")
st.caption("Never send another generic “I saw your profile” message again")

linkedin_url = st.text_input("LinkedIn Profile URL", placeholder="https://www.linkedin.com/in/johndoe")

if st.button("Generate 5 Personalized Icebreakers"):
    if not linkedin_url or "linkedin.com" not in linkedin_url:
        st.error("Please enter a valid LinkedIn URL")
    else:
        with st.spinner("Scraping profile..."):
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                r = requests.get(linkedin_url, headers=headers, timeout=10)
                soup = BeautifulSoup(r.text, 'html.parser')
                name = soup.find("h1") or "there"
                name = name.get_text(strip=True) if name else "there"
                title = soup.find("div", {"class": "text-body-medium"}) or ""
                title = title.get_text(strip=True) if title else ""
                about = soup.find("div", {"class": "pv-about__summary-text"}) or ""
                about = about.get_text(strip=True)[:500] if about else ""
                experience = [exp.get_text(strip=True) for exp in soup.find_all("span", {"class": "mr1 hoverable-link-text"})[:3]]
                context = f"Name: {name}\nCurrent Title: {title}\nAbout: {about}\nRecent roles: {', '.join(experience[:2])}"
            except:
                context = "Could not scrape full profile – using URL only"

        with st.spinner("Writing 5 human-sounding icebreakers..."):
            response = openai.chat.completions.create(
                model="gpt-4o-mini",   # cheap + fast
                messages=[
                    {"role": "system", "content": """You are a world-class B2B sales copywriter and networking expert. 
                    Write 5 short, personalized LinkedIn connection messages (max 120 chars each) that feel 100% human, never generic.
                    Reference specific details from the profile. Sound warm, curious, and valuable. Never start with “I noticed” or “Great profile”.
                    Format exactly like this:
                    1. [message]
                    2. [message]
                    etc."""},
                    {"role": "user", "content": context}
                ],
                temperature=0.8,
                max_tokens=600
            )
            result = response.choices[0].message.content
            st.success("Done!")
            st.markdown(result)
            st.download_button("Download as .txt", result, "icebreakers.txt")
