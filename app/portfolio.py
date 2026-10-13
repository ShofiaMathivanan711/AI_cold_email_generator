
import os
import uuid
import re
import chromadb
import pandas as pd


class Portfolio:
    def __init__(self, file_path=None):
        # Find the project root directory
        base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        # Locate the portfolio CSV file
        if file_path is None:
            file_path = os.path.join(
                base_dir, "app", "resource", "my_portfolio.csv"
            )

        self.file_path = file_path

        if not os.path.exists(self.file_path):
            raise FileNotFoundError(
                f"Portfolio CSV not found: {self.file_path}"
            )

        self.data = pd.read_csv(self.file_path)

        # Create persistent ChromaDB storage
        self.chroma_client = chromadb.PersistentClient(
            path=os.path.join(base_dir, "vectorstore")
        )

        self.collection = self.chroma_client.get_or_create_collection(
            name="portfolio"
        )

    def load_portfolio(self):
        # Load entries only when the collection is empty
        if self.collection.count() == 0:
            for _, row in self.data.iterrows():
                self.collection.add(
                    documents=[str(row["Techstack"])],
                    metadatas=[{"links": str(row["Links"])}],
                    ids=[str(uuid.uuid4())],
                )

    
    def query_links(self, job):
        """Return only CSV portfolio links matching the job's technologies."""

        if isinstance(job, dict):
            job_text = " ".join(
                str(job.get(field, ""))
                for field in ("role", "experience", "skills", "description")
            )
        elif isinstance(job, str):
            job_text = job
        elif isinstance(job, list):
            job_text = " ".join(map(str, job))
        else:
            return []

        if not job_text.strip():
            return []

        matching_links = []

        for _, row in self.data.iterrows():
            techstack = str(row.get("Techstack", ""))
            link = str(row.get("Links", "")).strip()

            if not link or link.lower() == "nan":
                continue

            technologies = [
                tech.strip()
                for tech in techstack.split(",")
                if tech.strip()
            ]

            for tech in technologies:
                pattern = (
                    r"(?<![A-Za-z0-9])"
                    + re.escape(tech)
                    + r"(?![A-Za-z0-9])"
                )

                if re.search(pattern, job_text, re.IGNORECASE):
                    matching_links.append(link)
                    break

        # Remove duplicate links while preserving their order.
        return list(dict.fromkeys(matching_links))