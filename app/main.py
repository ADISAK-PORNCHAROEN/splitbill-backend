from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.api.controllers.balances import router as balances_router
from app.api.controllers.expenses import router as expenses_router
from app.api.controllers.groups import router as groups_router
from app.api.routes.health import router as health_router
from app.core.config import settings
from app.domain.types import DomainError

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "X-User", "Idempotency-Key"],
)
app.include_router(health_router, prefix="/api")
app.include_router(groups_router)
app.include_router(expenses_router)
app.include_router(balances_router)


def openapi_schema():
    if app.openapi_schema is None:
        schema = get_openapi(title=app.title, version=app.version, routes=app.routes)
        for path in schema["paths"].values():
            for operation in path.values():
                responses = operation.get("responses", {})
                if "422" in responses:
                    responses.pop("422")
                    responses.setdefault("400", {"description": "Invalid request"})
        app.openapi_schema = schema
    return app.openapi_schema


app.openapi = openapi_schema


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(
        status_code=exc.status, content={"error": {"code": exc.code, "message": exc.message}}
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400, content={"error": {"code": "bad_request", "message": "Invalid request"}}
    )


@app.exception_handler(HTTPException)
async def http_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "http_error", "message": str(exc.detail)}},
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "internal_error", "message": "Internal server error"}},
    )
