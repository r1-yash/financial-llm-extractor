"""
FastAPI application for financial data extraction from PDFs using Gemini.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile

from extractor import extract_financial_data_from_pdf

# Configure logging: ensure we never log API keys or full request bodies
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Validate environment on startup (without exposing the key)."""
    try:
        from extractor import get_api_key
        get_api_key()
        logger.info("GEMINI_API_KEY is set and valid (key not logged).")
    except ValueError as e:
        logger.warning("Startup check: %s", str(e))
    yield


app = FastAPI(
    title="Financial LLM Extractor",
    description="Extract financial metrics from PDF reports using Google Gemini.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    """Health check (does not use API key)."""
    return {"status": "ok"}


@app.post("/upload")
async def upload(pdf: UploadFile = File(...)):
    """
    Accept a PDF file, extract text, send to Gemini, and return structured
    financial data (Revenue, Net Income, Total Debt, Total Assets, EPS).
    """
    if not pdf.filename or not pdf.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF (.pdf)")

    try:
        raw = await pdf.read()
    except Exception as e:
        logger.exception("Failed to read uploaded file")
        raise HTTPException(status_code=400, detail="Failed to read file") from e

    if not raw:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        result = extract_financial_data_from_pdf(raw)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail="Server configuration error") from e
    except Exception as e:
        logger.exception("Extraction failed")
        raise HTTPException(status_code=500, detail="Extraction failed") from e


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
