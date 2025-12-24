from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import os
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.api.v1.api import api_router
from app.core.database import engine, Base

# Initialize logging
log_level = os.getenv("LOG_LEVEL", "INFO")
use_json_logs = os.getenv("JSON_LOGS", "false").lower() == "true"
setup_logging(log_level=log_level, use_json=use_json_logs)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info(f"Starting {settings.PROJECT_NAME}")
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages."""
    logger.warning(f"Validation error on {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": [str(err) for err in exc.errors()]},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred"},
    )

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests."""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} - Status: {response.status_code}")
    return response

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with welcome page."""
    return """
    <html>
        <head>
            <title>Book Management System</title>
            <style>
                body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f2f5; }
                .container { text-align: center; padding: 2rem; background: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                h1 { color: #1a73e8; }
                a { display: inline-block; margin-top: 1rem; padding: 0.5rem 1rem; background: #1a73e8; color: white; text-decoration: none; border-radius: 4px; }
                a:hover { background: #1557b0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Intelligent Book Management System</h1>
                <p>The API is running successfully.</p>
                <a href="/docs">Go to API Documentation (Swagger UI)</a>
            </div>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.PROJECT_NAME}
