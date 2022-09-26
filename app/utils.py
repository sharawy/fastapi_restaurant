from fastapi import HTTPException
from fastapi_redis_cache import FastApiRedisCache
from fastapi_redis_cache.util import deserialize_json
from starlette import status


def get_model_or_404(klass, id: int, db):
    model_object = db.query(klass).get(id)
    if not model_object:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Object with id: {id} does not exist.",
        )
    return model_object


redis_cache = FastApiRedisCache()


def add_to_cache(key: str, values: dict, ttl=3600):
    return redis_cache.add_to_cache(key, values, ttl)


def get_from_cache(key: str):
    _, in_cache = redis_cache.check_cache(key)
    if in_cache:
        return deserialize_json(in_cache)


