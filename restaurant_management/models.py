from datetime import timezone

from sqlalchemy import Column, Integer, String, ForeignKey, SmallInteger

from app.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    open_hour = Column(Integer)
    close_hour = Column(Integer)

    @property
    def is_open(self):
        return self.open_hour <= timezone.now() > self.close_hour


class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    number_of_seats = Column(SmallInteger)
    number = Column(Integer, unique=True)

    def __repr__(self):
        return F"Table number: {self.id} restaurant id: {self.restaurant_id}"
