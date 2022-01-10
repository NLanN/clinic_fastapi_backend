from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.api import api_router as router_v1
from core.configs import settings


def create_app():
    tags_metadata = []
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        description="RIGHT SHIP API.",
        openapi_tags=tags_metadata,
    )
    configure_app(app=app)
    return app


def configure_app(app=None):
    config_extensions(app=app)
    config_error_handlers(app=app)
    configure_middlewares(app=app)
    configure_routers(app=app)


def config_extensions(app):
    ...


def config_error_handlers(app):
    ...


def configure_middlewares(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def configure_routers(app):
    app.include_router(router_v1, prefix=settings.API_V1_STR)


app = create_app()
