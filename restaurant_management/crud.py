from typing import List

from sqlalchemy.orm import Session

from restaurant_management import models
from restaurant_management.schemas import CreateRestaurant, RestaurantDetailsSchema, CreateTableSchema, \
    TableDetailsSchema


def create_restaurant(restaurant_request: CreateRestaurant, db: Session) -> RestaurantDetailsSchema:
    db_item = models.Restaurant(name=restaurant_request.name, open_hour=restaurant_request.open_hour,
                                close_hour=restaurant_request.close_hour)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_restaurants(db: Session) -> List[RestaurantDetailsSchema]:
    return db.query(models.Restaurant).all()


def get_restaurant_by_id(restaurant_id: int, db: Session) -> RestaurantDetailsSchema:
    return db.query(models.Restaurant).get(restaurant_id)


def update_restaurant(restaurant_request: RestaurantDetailsSchema, db: Session):
    restaurant = get_restaurant_by_id(restaurant_request.id, db)
    restaurant_data = restaurant_request.dict(exclude_unset=True)
    for key, value in restaurant_data.items():
        setattr(restaurant, key, value)
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)
    return restaurant


def create_table(table_request: CreateTableSchema, db: Session) -> TableDetailsSchema:
    db_item = models.Table(**table_request.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_tables_by_restaurant_id(restaurant_id: int, db: Session) -> List[TableDetailsSchema]:
    return db.query(models.Table).filter_by(restaurant_id=restaurant_id).all()


def get_table_by_id(table_id: int, db: Session) -> TableDetailsSchema:
    return db.query(models.Table).get(table_id)


def delete_table_by_id(table_id: int, db: Session):
    return db.query(models.Table).filter_by(id=table_id).delete()
