
from fastapi import FastAPI

from backend.api.routes import router
from backend.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Assistant intelligent pour les services universitaires.",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

app.include_router(router)
