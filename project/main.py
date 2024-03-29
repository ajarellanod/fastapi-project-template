from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.api.routes.v1 import router as v1_router
from project.core.config import settings


def get_application():
    _app = FastAPI(
        title=settings.PROJECT_NAME,
        default_response_class=ORJSONResponse,
    )

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


app = get_application()

#
# Healthcheck
#


@app.get("/healthcheck", status_code=200)
def status():
    return {"status": "success"}


#
# Routers
#

app.include_router(v1_router)
