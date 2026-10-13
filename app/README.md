# AI-Powered Cold Email Generator

## 1. Project Overview

The Cold Email Generator is a Python-based application that helps a software development company identify potential business opportunities and draft personalized B2B cold emails.

When a company publishes a software engineering job vacancy, it may indicate a need for additional technical expertise. The application extracts job information, identifies relevant technologies, matches them against the company's portfolio, and generates a professional email offering software development services.

The application generates email drafts for human review. It does not automatically send emails.

## 2. Business Scenario

Bug Treat Technologies is a software development company. Shofia, its Business Development Executive, wants to contact companies that publish relevant software engineering vacancies.

For example, if a company advertises a role requiring Python and machine learning, the application searches the company's portfolio CSV for matching technologies and selects relevant portfolio links.

It then generates a personalized email introducing Bug Treat Technologies' services.

## 3. Project Workflow

1. The user enters a company's careers-page URL.
2. The application downloads the webpage.
3. HTML elements such as scripts, navigation, and footers are removed.
4. The remaining webpage text is cleaned.
5. An LLM extracts job roles, experience, skills, and descriptions.
6. The application matches job technologies against the portfolio CSV.
7. Relevant portfolio links are identified.
8. The LLM generates a personalized B2B cold email.
9. The email and relevant portfolio links are displayed in the Streamlit interface.

If no suitable portfolio links are found, the current application skips email generation for that job.

## 4. Technology Stack

| Technology          | Purpose                                                           |
| ------------------- | ----------------------------------------------------------------- |
| Python              | Core application logic                                            |
| Streamlit           | Web user interface                                                |
| Requests            | Downloads webpages using HTTP                                     |
| Beautiful Soup      | Parses HTML and extracts readable text                            |
| LangChain           | Connects prompts to the language model and processes responses    |
| Groq API            | Provides hosted access to the configured language model           |
| GPT-OSS 120B        | Language model configured for job extraction and email generation |
| Pandas              | Reads and processes the portfolio CSV                             |
| ChromaDB            | Provides persistent vector storage                                |
| python-dotenv       | Loads the API key from the `.env` file                            |
| Regular expressions | Cleans text and matches technology names                          |

**Implementation note:** The current portfolio matching function uses Python regular expressions to match technologies against the CSV. Although ChromaDB is initialized, the current matching function does not use vector similarity search to select links.

## 5. Project Structure

```text
cold_email_generator/
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── app/
│   ├── main.py
│   ├── chains.py
│   ├── portfolio.py
│   ├── utils.py
│   └── resource/
│       └── my_portfolio.csv
├── vectorstore/
└── .venv/
```

Some folders, such as `vectorstore`, may be created when the application runs. The `.venv` folder contains the project's virtual environment.

### File Responsibilities

* `main.py`: Defines the Streamlit interface and coordinates the workflow.
* `chains.py`: Configures the language model, extracts job information, and generates cold emails.
* `portfolio.py`: Loads the portfolio CSV, initializes ChromaDB, and matches portfolio links.
* `utils.py`: Contains helper functions for cleaning webpage text.
* `my_portfolio.csv`: Stores technology stacks and corresponding portfolio URLs.
* `.env`: Stores the Groq API key.
* `requirements.txt`: Lists the required Python packages.
* `README.md`: Documents the project.

## 6. Portfolio CSV

The portfolio CSV contains two important columns:

* `Techstack`: Technologies associated with the company's portfolio work.
* `Links`: URLs pointing to the corresponding portfolio entries.

Example:

| Techstack                            | Links                                   |
| ------------------------------------ | --------------------------------------- |
| Python, Django, MySQL                | https://example.com/python-portfolio    |
| Machine Learning, Python, TensorFlow | https://example.com/ml-python-portfolio |

These example URLs are placeholders. Replace them with genuine portfolio URLs before using the application for real business outreach.

## 7. Installation and Setup

### Prerequisites

* Python installed on the system.
* Visual Studio Code or another code editor.
* A Groq API key.
* Internet access for webpage requests and model API calls.

### Step 1: Open the project directory

```powershell
cd "C:\My Documents\Study Materials\cold_email_generator"
```

### Step 2: Create a virtual environment if one does not exist

```powershell
python -m venv .venv
```

### Step 3: Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 4: Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### Step 5: Configure the API key

Create a `.env` file in the project root and add:

```text
GROQ_API_KEY=your_actual_api_key
```

Replace the placeholder with your own API key. Never publish the real key or commit it to Git.

### Step 6: Run the application

```powershell
python -m streamlit run app/main.py
```

Streamlit will display a local URL in the terminal. Open that URL in a browser to use the application.

## 8. How the AI Integration Works

The application uses LangChain to build prompt-and-model workflows.

### Job Extraction

The careers-page text is passed to a language model with instructions to extract:

* Job role
* Experience requirements
* Technical skills
* Job description

The model is instructed to return JSON so the application can process the information as structured data.

### Email Generation

The extracted job information and matching portfolio links are provided to the language model. A prompt instructs it to create a professional B2B cold email from Shofia at Bug Treat Technologies.

The prompt also instructs the model not to invent clients, achievements, or contact details.

Model responses must still be reviewed because prompt instructions alone cannot guarantee factual accuracy.

## 9. ChromaDB and Vector Databases

ChromaDB is a vector database that can store document embeddings and metadata and retrieve semantically similar information.

In the current implementation, ChromaDB is initialized with persistent local storage, and portfolio entries can be loaded into a collection.

However, the current `query_links()` method uses regular-expression keyword matching against the CSV. It does not perform semantic similarity search through ChromaDB.

Semantic retrieval could be added in a future version to identify relevant portfolio entries when job descriptions use different wording from the stored technology descriptions.

## 10. Current Limitations

* Some careers websites block automated requests.
* Pages that load jobs dynamically with JavaScript may not expose listings in the downloaded HTML.
* LLM extraction may miss jobs or produce incorrect fields.
* Keyword matching may miss synonyms or return links based on a single matching technology.
* The current portfolio URLs may be placeholders.
* A job vacancy does not necessarily mean the company is interested in outsourcing.
* ChromaDB is initialized, but semantic portfolio search is not currently implemented.
* Generated emails require human review before sending.

## 11. Future Improvements

* Add Playwright support for JavaScript-rendered careers pages.
* Improve technology matching with weighted keyword matching or semantic search.
* Filter irrelevant or weakly matched portfolio links.
* Add validation for extracted job data and generated emails.
* Add automated tests for matching and email generation.
* Improve error handling, logging, and monitoring.
* Store genuine portfolio project descriptions and URLs.
* Add an option to download or copy the generated email.
* Consider integrating a CRM or email platform in a future version.

## 12. Security Considerations

* Keep API keys in environment variables or a protected secrets manager.
* Never commit `.env` or virtual-environment folders to a public repository.
* Use real, authorized portfolio links.
* Review generated content before sending business emails.
* Respect website terms of use, access restrictions, and applicable privacy and email regulations.

## 13. Summary

This project demonstrates a practical Generative AI application combining web scraping, structured information extraction, portfolio matching, and personalized B2B email generation.

It uses Python for the application logic, Streamlit for the interface, LangChain for model integration, Groq for hosted inference, and Pandas for portfolio data processing. ChromaDB is configured for persistent vector storage, while portfolio selection currently uses keyword matching.

The project can be extended with semantic search, more robust webpage extraction, automated testing, and improved data validation.
