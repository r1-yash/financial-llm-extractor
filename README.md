# Financial LLM Extractor (Practice Project)

This is a backend-focused practice project where I built a small FastAPI service that extracts structured financial metrics from PDF annual reports using Google Gemini.

The goal of this project was to understand:

- How to handle PDF file uploads in FastAPI  
- How to extract raw text from PDFs  
- How to call an LLM using a REST API  
- How to enforce structured JSON output from an LLM  
- How to manage API keys securely  

There is no custom frontend. The API is tested using FastAPI's default Swagger UI (`/docs`). The UI is intentionally raw — this project focuses on backend + LLM integration.

---

## What It Does

Upload a financial report PDF →

1. Extract text using PyPDF  
2. Send the extracted text to Gemini  
3. Force structured JSON output  
4. Return standardized financial fields  

Example response:

```json
{
  "Revenue": "383.29 billion",
  "Net_Income": "96.99 billion",
  "Total_Debt": "106.13 billion",
  "Total_Assets": "352.58 billion",
  "EPS": "6.16"
}
```

---

## Tech Stack

- FastAPI
- Uvicorn
- Google Gemini API
- PyPDF
- python-dotenv

---

## Setup

### 1. Create Virtual Environment

```bash
cd financial_llm_extractor
python3 -m venv venv
source venv/bin/activate

### 2. Install dependencies
pip install -r requirements.txt

### 3. Add Gemini API Key
GEMINI_API_KEY=your_actual_key_here

### 4. Run the Server
uvicorn main:app --reload --port 8000

### Project Structure 

financial_llm_extractor/
├── main.py
├── extractor.py
├── download_sample_pdf.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
└── README.md

---

## Demo Screenshot

Below is the API working via Swagger UI:


<p align="center">
  <img src="https://raw.githubusercontent.com/r1-yash/financial-llm-extractor/main/assets/screenshot.png" width="900">
</p>