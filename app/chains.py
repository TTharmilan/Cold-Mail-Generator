import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv
import re

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="deepseek-r1-distill-qwen-32b")

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
        """
        ### SCRAPED TEXT FROM WEBSITE:
        {page_data}
        ### INSTRUCTION:
        The scraped text is from the career's page of a website.
        Your job is to extract the job postings and return them in JSON format containing the
        following keys: `role`, `experience`, `skills` and `description`.
        Only return the valid JSON.
        ### VALID JSON (NO PREAMBLE):
        """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, links):
        prompt_email = PromptTemplate.from_template(
        """
        ### JOB DESCRIPTION:
        {job_description}

        ### INSTRUCTION:
        You are Raam, a business development executive at WeMake. WeMake is an AI & Software Consulting company dedicated to facilitating
        the seamless integration of business processes through automated tools.
        Over our experience, we have empowered numerous enterprises with tailored solutions, fostering scalability,
        process optimization, cost reduction, and heightened overall efficiency.
        Your job is to write a cold EMAIL to the client regarding the job mentioned above describing the capability of WeMake
        in fulfilling their needs.
        Mail SUBJECT is MUST.
        HIGHLIGHT how you found about their job posting.
        Address the EMAIL to the client in a professional manner, only using the JOB ROLE. Example: Dear Hiring Manager.
        Also add the most relevant links from the following list to showcase WeMake's portfolio: {link_list},**ONLY include Relevant  URLs ONLY once, no additional text or descriptions**.
        Include only the URLs, no descriptions or titles.
        Remember you are Raam, BDE at WeMake.
        **Do not provide a preamble or any additional explanation.**
        **Do not include CONTACT details in the Mail ending.**
        ### VALID EMAIL (NO PREAMBLE):
        ### EMAIL (NO PREAMBLE):
        """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link_list": links})
        cleaned_res = re.sub(r"<think>.*?</think>", "", res.content, flags=re.DOTALL).strip()
        return cleaned_res

if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))
