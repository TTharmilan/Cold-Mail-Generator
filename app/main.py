import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
import os
from dotenv import load_dotenv

from chains import Chain
from portfolio import Portfolio
from utils import clean_text

load_dotenv()  # Load environment variables
os.environ["USER_AGENT"] = os.getenv("USER_AGENT", "Mozilla/5.0")

def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Cold Email Generator")
    url_input = st.text_input("Enter the URL:", value="https://careers.nike.com/senior-principal-ai-ml-engineer/job/R-43372")
    submit_button = st.button("Submit")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}



    if submit_button:
        try:
            loader = WebBaseLoader([url_input], header_template=headers)
            data = clean_text(loader.load().pop().page_content)
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)
            for job in jobs:
                skills = job.get('skills', [])
                links = portfolio.query_links(skills)
                email = llm.write_mail(job, links)
                st.code(email, language='markdown')
        except Exception as e:
            st.error(f"An Error Occurred: {e}")

if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)
