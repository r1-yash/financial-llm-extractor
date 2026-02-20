# Financial LLM Extractor

Production-ready FastAPI service that extracts financial metrics (Revenue, Net Income, Total Debt, Total Assets, EPS) from PDF annual reports using the **Google Gemini 1.5 Flash** API.

## Security

- **Never hardcode API keys.** The app loads `GEMINI_API_KEY` from the environment via `python-dotenv`.
- The key is **never logged or printed**. Keep your `.env` file out of version control.

---

## Quick Start

### 1. Create a virtual environment

```bash
cd financial_llm_extractor
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get a Gemini API key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Sign in with your Google account.
3. Click **Create API key** and copy the key.

### 4. Configure the API key

- **Copy the example env file:**
  ```bash
  cp .env.example .env
  ```
- **Edit `.env`** and replace the placeholder with your key:
  ```
  GEMINI_API_KEY=your_actual_key_here
  ```
- **Where to paste:** In the project root, in the `.env` file, as the value of `GEMINI_API_KEY`. Do not commit `.env` to Git.

### 5. Run the server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or:

```bash
python main.py
```

- API docs: http://localhost:8000/docs  
- Health: http://localhost:8000/health  

---

## Download a sample PDF for testing

The helper script downloads a public annual report PDF (e.g. from investor relations) for testing:

```bash
python download_sample_pdf.py
```

This downloads a public 10-K PDF (e.g. Apple) into `sample_annual_report.pdf` in the project root.

---

## Example request

**Upload a PDF and get extracted financial data:**

```bash
curl -X POST http://localhost:8000/upload \
  -F "pdf=@sample_annual_report.pdf"
```

**Example response:**

```json
{
  "Revenue": "383.29 billion",
  "Net_Income": "96.99 billion",
  "Total_Debt": "106.13 billion",
  "Total_Assets": "352.58 billion",
  "EPS": "6.16"
}
```

Missing fields are returned as `null`.

---

## Pushing to GitHub without leaking secrets

1. **Never commit `.env`.** It is listed in `.gitignore`; confirm with:
   ```bash
   git status
   ```
   You should not see `.env` in the list.

2. **Commit `.env.example`** so others know which variables to set (with placeholder values only).

3. **Before the first push**, verify:
   ```bash
   git check-ignore .env && echo ".env is ignored"
   cat .gitignore
   ```
   Ensure `.env`, `venv/`, and `__pycache__/` are present.

4. If you ever committed `.env` by mistake:
   - Rotate the API key immediately in Google AI Studio.
   - Remove the file from history (e.g. `git filter-branch` or BFG Repo-Cleaner) and force-push, or create a new repo and push again without `.env`.

---

## Project structure

```
financial_llm_extractor/
├── main.py              # FastAPI app, /upload and /health
├── extractor.py         # PDF text extraction + Gemini call
├── requirements.txt
├── download_sample_pdf.py
├── .env                 # Your secrets (do not commit)
├── .env.example         # Template (safe to commit)
├── .gitignore
└── README.md
```

---

## License

Use and modify as needed for your project.
