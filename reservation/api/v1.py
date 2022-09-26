from datetime import datetime, timedelta
from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_pagination import Page, add_pagination, paginate
from sqlalchemy.orm import Session
from starlette import status

from app.dependencies import get_db
from app.utils import get_model_or_404
from reservation import schemas, utils
from reservation.crud import get_reservations_by_restaurant_id
import reservation.crud as reservation_crud
from reservation.models import Reservation
from reservation.utils import get_table_available_slots, TimeSlot
from restaurant_management.models import Table
from users.roles import ADMIN_ROLE, EMPLOYEE_ROLE

router = APIRouter(prefix="/v1/reservations",
                   tags=["reservations"],
                   )


@router.get("{restaurant_id}/", response_model=Page[schemas.ReservationDetailsSchema],
            dependencies=[Depends(ADMIN_ROLE)])
def get_reservations(restaurant_id: int, start: Union[datetime, None] = Query(default=None),
                     end: Union[datetime, None] = Query(default=None),
                     table_id: Union[int, None] = Query(default=None),
                     db: Session = Depends(get_db)

                     ):
    return paginate(get_reservations_by_restaurant_id(restaurant_id, db, start, end, table_id))


@router.get("{restaurant_id}/today", response_model=Page[schemas.ReservationDetailsSchema],
            dependencies=[Depends(EMPLOYEE_ROLE)])
def get_today_reservations(restaurant_id: int, order: Union[str, None] = Query(default='asc'),
                           db: Session = Depends(get_db)):
    return paginate(get_reservations_by_restaurant_id(restaurant_id, db, datetime.today(),
                                                      datetime.now() + timedelta(days=1), order=order))


@router.post("/", response_model=schemas.ReservationDetailsSchema, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(EMPLOYEE_ROLE)])
def create_reservation(reservation_request: schemas.CreateReservationSchema, db: Session = Depends(get_db)):
    table = get_model_or_404(Table, reservation_request.table_id, db)

    better_allocations = reservation_crud.get_tables_with_better_allocation(table,
                                                                            reservation_request.start_time,
                                                                            reservation_request.end_time,
                                                                            reservation_request.number_of_customers, db)
    if better_allocations:
        tables_number = [str(table.id) + ',' for table in better_allocations]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"There are better allocation options for this reservation check tables: {tables_number}",
        )

    available_time_slots = get_table_available_slots(table.id, reservation_request.start_time, db)
    time_slot = TimeSlot(reservation_request.start_time.replace(tzinfo=None),
                         reservation_request.end_time.replace(tzinfo=None))
    if time_slot not in available_time_slots:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Time slot is not available.",
        )
    if table.number_of_seats < reservation_request.number_of_customers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Table seats are not enough.",
        )

    return reservation_crud.create_reservation(reservation_request, db)


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(ADMIN_ROLE)])
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = get_model_or_404(Reservation, reservation_id, db)
    if reservation.start_time < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete reservation in the past.",
        )
    reservation_crud.delete_reservation_by_id(reservation_id, db)


@router.post("{restaurant_id}/tables/{table_id}", response_model=List[schemas.TimeSlotSchema],
             dependencies=[Depends(EMPLOYEE_ROLE)])
def calculate_table_time_slots(restaurant_id: int, table_id: int,
                               calculate_time_slot_request: schemas.CalculateTimeSlot,
                               db: Session = Depends(get_db)):
    table = get_model_or_404(Table, table_id, db)
    time_slots = utils.get_table_available_slots(table.id, calculate_time_slot_request.date, db)
    return time_slots


add_pagination(router)
