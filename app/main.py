from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.responses import StreamingResponse
import io
from fastapi import FastAPI, HTTPException
import yfinance as yf
import pandas as pd
from datetime import datetime

app = FastAPI(
    title="Financial Data API",
    description="Simple API to download stock market data using yfinance",
    version="1.0.0",
)
templates = Jinja2Templates(directory="templates")

@app.get("/")
def home():
    return {
        "message": "Financial Data API is running",
        "usage": "/download?ticker=AAPL&start=2020-01-01&end=2023-01-01"
    }

@app.get("/error", response_class=HTMLResponse)
def error_page(request: Request):
    return templates.TemplateResponse(
        "error.html",
        {"request": request}
    )


@app.get("/ui", response_class=HTMLResponse)
def ui(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/error/date-format", response_class=HTMLResponse)
def date_format_error(request: Request):
    return templates.TemplateResponse(
        "error_date_format.html",
        {"request": request}
    )

@app.get("/error/date-order", response_class=HTMLResponse)
def date_order_error(request: Request):
    return templates.TemplateResponse(
        "error_date_order.html",
        {"request": request}
    )


@app.get("/download")
def download_data(
    ticker: str,
    start: str,
    end: str
):
    # Validate dates
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return RedirectResponse(url="/error/date-format", status_code=302)

    if start_date >= end_date:
        return RedirectResponse(url="/error/date-order", status_code=302)
    # Download data
    data = yf.download(ticker, start=start, end=end)

    if data.empty:
        return RedirectResponse(url="/error", status_code=302)

    # Flatten columns if MultiIndex
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Convert DataFrame to CSV in memory
    stream = io.StringIO()
    data.to_csv(stream)
    stream.seek(0)

    filename = f"{ticker.upper()}_{start}_to_{end}.csv"

    return StreamingResponse(
        stream,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
