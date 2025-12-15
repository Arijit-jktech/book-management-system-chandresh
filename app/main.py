from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.include_router(api_router, prefix=settings.API_V1_STR)

from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def root():
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
