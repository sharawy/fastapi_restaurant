from pydantic import BaseModel, Field


class RestaurantBaseSchema(BaseModel):
    name: str
    open_hour: int
    close_hour: int


class CreateRestaurant(RestaurantBaseSchema):
    pass


class RestaurantDetailsSchema(RestaurantBaseSchema):
    id: int

    class Config:
        orm_mode = True


class TableBaseSchema(BaseModel):
    restaurant_id: int
    number_of_seats: int = Field(
        title='The Snap',
        description='this is the value of snap',
        gt=0,
        le=12,
    )
    number: int


class CreateTableSchema(TableBaseSchema):
    pass


class TableDetailsSchema(TableBaseSchema):
    id: int

    class Config:
        orm_mode = True
