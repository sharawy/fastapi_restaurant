from fastapi import FastAPI, Request, Response, APIRouter
from sqlalchemy.orm import Session

from fastapi.middleware.cors import CORSMiddleware
from fastapi_redis_cache import FastApiRedisCache

from app.core.config import settings
from users.api.v1 import router as user_router
from restaurant_management.api.v1 import router as restaurant_router
from reservation.api.v1 import router as reservation_router


def get_application():
    _app = FastAPI(title=settings.PROJECT_NAME)

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


app = get_application()


@app.on_event("startup")
def startup():
    redis_cache = FastApiRedisCache()
    redis_cache.init(
        host_url=settings.REDIS_URL,
        prefix="myapi-cache",
        response_header="X-MyAPI-Cache",
        ignore_arg_types=[Request, Response, Session]
    )


router = APIRouter()
router.include_router(user_router)
router.include_router(restaurant_router)
router.include_router(reservation_router)

app.include_router(router)


