from datetime import datetime
from typing import List

from requests import Session
from sqlalchemy import cast, Date, desc, asc

from reservation.models import Reservation
from reservation.schemas import CreateReservationSchema, ReservationDetailsSchema
from restaurant_management.models import Table


def create_reservation(reservation_request: CreateReservationSchema, db: Session) -> ReservationDetailsSchema:
    data = reservation_request.dict()
    data['start_time'] = data['start_time'].replace(tzinfo=None)
    data['end_time'] = data['end_time'].replace(tzinfo=None)
    db_item = Reservation(**data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_tables_with_better_allocation(selected_table: Table, start_time: datetime,
                                      end_time: datetime,
                                      number_of_customers,
                                      db: Session):
    reservations = db.query(Reservation.table_id).filter(Reservation.start_time >= start_time,
                                                   Reservation.end_time <= end_time)
    return db.query(Table).filter(Table.id != selected_table.id, Table.restaurant_id == selected_table.restaurant_id,
                                  Table.number_of_seats >= number_of_customers,
                                  Table.number_of_seats < selected_table.number_of_seats) \
        .join(Reservation, isouter=True).filter(Reservation.id == None, Table.id.not_in(reservations)).order_by(
        asc(Table.number_of_seats)).all()


def get_reservations_by_restaurant_id(restaurant_id: int, db: Session, start_time: datetime = None,
                                      end_time: datetime = None, table_id: int = None, order: str = None) \
        -> List[ReservationDetailsSchema]:
    query = db.query(Reservation).join(Table).filter_by(restaurant_id=restaurant_id)
    if start_time:
        query = query.filter(cast(Reservation.start_time, Date) >= start_time.date())
    if end_time:
        query = query.filter(cast(Reservation.start_time, Date) < end_time.date())
    if table_id:
        query = query.filter(Reservation.table_id == table_id)
    if order == 'desc':
        query = query.order_by(
            desc(Reservation.start_time)
        )
    else:
        query = query.order_by(
            asc(Reservation.start_time)
        )

    return query.all()


def delete_reservation_by_id(reservation_id: int, db: Session):
    return db.query(Reservation).filter_by(id=reservation_id).delete()
