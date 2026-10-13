
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException


# Find the project root and load the API key from .env
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Chain:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY was not found. "
                "Check your project-root .env file."
            )

        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=api_key,
            model_name="openai/gpt-oss-120b",
        )

    def extract_jobs(self, cleaned_text):
        """Extract job postings from careers-page text."""

        prompt_extract = PromptTemplate.from_template(
            """
            ### CAREERS PAGE TEXT:
            {page_data}

            ### INSTRUCTIONS:
            Extract genuine job postings from the text.

            Return a JSON array. Each job must contain:
            - role: string
            - experience: string
            - skills: list of strings
            - description: string

            Use an empty string or empty list when information
            is missing.

            Ignore navigation, icons, SVG text, and unrelated content.
            Do not invent job postings or requirements.
            Return only valid JSON without Markdown fences.
            """
        )

        chain_extract = prompt_extract | self.llm
        response = chain_extract.invoke({"page_data": cleaned_text})

        try:
            parser = JsonOutputParser()
            jobs = parser.parse(response.content)
        except OutputParserException as exc:
            raise OutputParserException(
                "Unable to parse extracted jobs as JSON."
            ) from exc

        if isinstance(jobs, dict):
            jobs = [jobs]

        if not isinstance(jobs, list):
            return []

        return [
            job
            for job in jobs
            if isinstance(job, dict) and job.get("role")
        ]

    def write_mail(self, job, links):
        """
        Generate a B2B sales email using the job posting
        and relevant portfolio links.
        """

        prompt_email = PromptTemplate.from_template(
            """
            ### JOB POSTING:
            {job_description}

            ### RELEVANT PORTFOLIO LINKS FROM OUR CSV:
            {link_list}

            ### YOUR IDENTITY:
            You are Shofia, Business Development Executive at
            Bug Treat Technologies, a software development company.

            ### BUSINESS SCENARIO:
            A company has advertised a software engineering vacancy.
            Bug Treat Technologies offers software development services
            that may help the company extend its engineering capacity.

            Your goal is to introduce our services and explore whether
            the company would consider working with an external
            software development partner.

            You are NOT applying for the advertised job.
            You are NOT writing a job application.

            ### EMAIL WRITING RULES:
            1. Write a professional, concise, personalized B2B cold email.
            2. Mention the advertised role and relevant technical needs.
            3. Explain how our software development services may help.
            4. Do not assume the company definitely needs a vendor.
            5. Do not claim we have dedicated engineers available unless
               that information is explicitly provided.
            6. Do not invent clients, projects, achievements, statistics,
               years of experience, or customer results.
            7. Use only the supplied job details and portfolio links.
            8. Include only portfolio URLs supplied in the CSV links.
            9. Include each supplied URL exactly as given.
            10. Do not include unrelated portfolio links.
            11. If no portfolio links are supplied, do not invent links.
            12. Include a clear subject line.
            13. End with a polite call to action.
            14. Sign off exactly as:

                Best regards,
                Shofia
                Business Development Executive
                Bug Treat Technologies

            Return only the completed email, including its subject.

            ### EMAIL:
            """
        )

        link_list = (
            "\n".join(str(link) for link in links)
            if links
            else "No relevant portfolio links were found."
        )

        chain_email = prompt_email | self.llm

        response = chain_email.invoke(
            {
                "job_description": str(job),
                "link_list": link_list,
            }
        )

        email = str(response.content).strip()

        # Ensure every supplied portfolio URL appears in the email.
        missing_links = [
            str(link)
            for link in links
            if str(link) not in email
        ]

        if missing_links:
            email += "\n\nRelevant Portfolio Links:\n"
            email += "\n".join(missing_links)

        # Correct the sender identity if the model uses another name
        # or company in its sign-off.
        unwanted_signatures = [
            "\nMohan\n",
            "\nAtliQ\n",
            "\nAtliq\n",
        ]

        for signature in unwanted_signatures:
            email = email.replace(signature, "\n")

        return email


if __name__ == "__main__":
    print(
        "GROQ_API_KEY loaded:",
        bool(os.getenv("GROQ_API_KEY"))
    )

    print("Chain configuration loaded successfully.")