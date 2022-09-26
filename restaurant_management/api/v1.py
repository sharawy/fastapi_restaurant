from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.dependencies import get_db
from app.utils import get_model_or_404
from restaurant_management import schemas
import restaurant_management.crud as restaurant_crud
from restaurant_management.models import Restaurant
from users.roles import ADMIN_ROLE

router = APIRouter(prefix="/v1/restaurants",
                   tags=["restaurants"],
                   )


@router.get("/", response_model=List[schemas.RestaurantDetailsSchema], dependencies=[Depends(ADMIN_ROLE)])
def list_restaurant(db: Session = Depends(get_db)):
    return restaurant_crud.get_restaurants(db)


@router.post("/", response_model=schemas.RestaurantDetailsSchema, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(ADMIN_ROLE)])
def create_restaurant(restaurant_request: schemas.CreateRestaurant, db: Session = Depends(get_db)):
    return restaurant_crud.create_restaurant(restaurant_request, db)


@router.get("{restaurant_id}/tables", response_model=List[schemas.TableDetailsSchema],
            dependencies=[Depends(ADMIN_ROLE)])
def get_restaurant_tables(restaurant_id: int, db: Session = Depends(get_db)):
    return restaurant_crud.get_tables_by_restaurant_id(restaurant_id, db)


@router.post("/tables", response_model=schemas.TableDetailsSchema, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(ADMIN_ROLE)])
def create_restaurant_table(restaurant_request: schemas.CreateTableSchema, db: Session = Depends(get_db)):
    _ = get_model_or_404(Restaurant, restaurant_request.restaurant_id, db)
    table = restaurant_crud.create_table(restaurant_request, db)
    return table


@router.delete("/tables/{table_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(ADMIN_ROLE)])
def delete_restaurant_table(table_id: int, db: Session = Depends(get_db)):
    restaurant_crud.delete_table_by_id(table_id, db)
