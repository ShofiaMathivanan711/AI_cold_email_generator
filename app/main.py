
import streamlit as st
import requests
from bs4 import BeautifulSoup

from chains import Chain
from portfolio import Portfolio
from utils import clean_text


def extract_website_text(url):
    """Download a webpage and extract its readable text."""
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(
        url,
        headers=headers,
        timeout=20,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove elements that do not contain useful job information.
    for tag in soup([
        "script",
        "style",
        "nav",
        "footer",
        "header",
        "svg",
        "noscript",
    ]):
        tag.decompose()

    return clean_text(soup.get_text(separator=" "))


def display_value(value):
    """Convert extracted job fields into readable text."""
    if value is None:
        return "Not specified"

    if isinstance(value, list):
        items = [
            str(item).strip()
            for item in value
            if item is not None and str(item).strip()
        ]
        return ", ".join(items) if items else "Not specified"

    if isinstance(value, dict):
        return str(value) if value else "Not specified"

    text = str(value).strip()

    if not text or text.lower() in {"none", "nan", "[]", "{}"}:
        return "Not specified"

    if text.lower() == "svg":
        return "Not specified"

    return text


st.set_page_config(
    page_title="Cold Email Generator",
    page_icon="📧",
    layout="wide",
)

st.title("📧 Cold Email Generator")

st.write(
    "Enter a company's careers-page URL to extract job postings "
    "and generate a tailored cold email using relevant portfolio links."
)

url = st.text_input(
    "Company careers-page URL",
    placeholder="https://example.com/careers",
)

generate_button = st.button(
    "Generate Cold Email",
    type="primary",
)

if generate_button:
    if not url.strip():
        st.warning("Please enter a careers-page URL.")

    elif not url.strip().startswith(("http://", "https://")):
        st.warning(
            "Please enter a valid URL starting with http:// or https://."
        )

    else:
        try:
            with st.spinner("Reading the careers page..."):
                page_text = extract_website_text(url)

            if not page_text:
                st.warning(
                    "No readable text was found on this webpage."
                )

            else:
                chain = Chain()
                portfolio = Portfolio()

                with st.spinner("Extracting job postings with AI..."):
                    jobs = chain.extract_jobs(page_text)

                if not jobs:
                    st.warning(
                        "No job postings were found. The website may "
                        "load listings dynamically or block automated access."
                    )

                else:
                    st.success(
                        f"Found {len(jobs)} job posting(s)."
                    )

                    for index, job in enumerate(jobs, start=1):
                        if not isinstance(job, dict):
                            continue

                        role = display_value(job.get("role"))

                        with st.expander(
                            f"Job {index}: {role}",
                            expanded=True,
                        ):
                            st.markdown("### Job Details")

                            st.write(
                                "**Experience:**",
                                display_value(job.get("experience")),
                            )

                            st.write(
                                "**Skills:**",
                                display_value(job.get("skills")),
                            )

                            st.write(
                                "**Description:**",
                                display_value(job.get("description")),
                            )

                            # Match the complete job against CSV technologies.
                            with st.spinner(
                                "Finding relevant portfolio links..."
                            ):
                                links = portfolio.query_links(job)

                            st.markdown("### Relevant Portfolio Links")

                            if not links:
                                st.warning(
                                    "No matching portfolio links were found "
                                    "in your CSV for this job. Email "
                                    "generation was skipped."
                                )
                                continue

                            for link in links:
                                st.markdown(f"- [{link}]({link})")

                            # Generate an email only when matching links exist.
                            with st.spinner("Generating your cold email..."):
                                email = chain.write_mail(job, links)

                            st.markdown("### Generated Cold Email")

                            # Streamlit's code block includes a copy icon.
                            st.code(
                                email,
                                language="text",
                            )

        except requests.exceptions.RequestException as exc:
            st.error(
                f"Could not access the careers webpage: {exc}"
            )

        except Exception as exc:
            st.error(
                f"Something went wrong: {exc}"
            )