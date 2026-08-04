# app/main.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.config import settings
from app.api.routes import router


# ── Create the FastAPI application ────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION
)


# ── Mount Static Files ─────────────────────────────────────────
# This tells FastAPI: "Serve files from the 'static' folder
# when someone visits a URL starting with '/static'"
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# ── Set up HTML Templates ──────────────────────────────────────
# Jinja2Templates tells FastAPI where our HTML files are
templates = Jinja2Templates(directory="templates")


# ── Global Exception Handlers ──────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException
):
    """Handles all HTTPExceptions with consistent JSON format."""
    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error_code": exc.detail.get("error_code", "ERROR"),
                "message": exc.detail.get("message", str(exc.detail)),
                "hint": exc.detail.get("hint", None)
            }
        )
    else:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "error_code": f"HTTP_{exc.status_code}",
                "message": str(exc.detail),
                "hint": None
            }
        )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    """Handles Pydantic validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "error_code": "VALIDATION_ERROR",
            "message": "Request validation failed.",
            "hint": "Make sure you are uploading a file using "
                    "multipart/form-data format.",
            "details": str(exc.errors())
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception
):
    """Catches any unexpected errors."""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
            "hint": "Please try again."
        }
    )


# ── Connect API Router ─────────────────────────────────────────
app.include_router(router, prefix="/api/v1")


# ── Frontend Route ─────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def frontend(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "model_name": settings.MODEL_NAME
        }
    )