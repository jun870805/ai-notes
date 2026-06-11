from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import settings
from app.database import engine
from app.routers.ai import router as ai_router
from app.routers.notes import router as notes_router
from app.schemas.common import error_envelope, success_envelope
from app.services.embedding_service import EmbeddingServiceError


def create_app() -> FastAPI:
    app = FastAPI(title="AI 工程筆記 API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_request, exc: RequestValidationError) -> JSONResponse:
        message = exc.errors()[0]["msg"] if exc.errors() else "Validation error."
        return JSONResponse(status_code=422, content=error_envelope("validation_error", message))

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request, exc: HTTPException) -> JSONResponse:
        if exc.status_code == 404:
            code = "note_not_found"
        elif exc.status_code == 400:
            code = "bad_request"
        else:
            code = "internal_error"
        return JSONResponse(status_code=exc.status_code, content=error_envelope(code, str(exc.detail)))

    @app.exception_handler(EmbeddingServiceError)
    async def embedding_service_error_handler(_request, exc: EmbeddingServiceError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=error_envelope(exc.code, exc.message))

    @app.get("/health")
    def healthcheck() -> JSONResponse:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return JSONResponse(status_code=200, content=success_envelope("ok"))

    app.include_router(notes_router, prefix="/api/v1")
    app.include_router(ai_router, prefix="/api/v1")
    return app


app = create_app()
