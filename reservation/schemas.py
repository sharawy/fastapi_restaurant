from datetime import datetime

import pytz
from pydantic import BaseModel, validator

from app.core.config import settings


class ReservationBaseSchema(BaseModel):
    main_guest_name: str
    number_of_customers: int
    table_id: int
    end_time: datetime
    start_time: datetime


class CreateReservationSchema(ReservationBaseSchema):

    @validator('start_time', pre=False)
    def time_slot_validation(cls, start_time, values, **kwargs):

        end_time = values.get('end_time', None)
        now_date = datetime.now(tz=pytz.UTC)
        if start_time >= end_time:
            raise ValueError('start time should be before end time')
        if start_time < now_date or now_date > end_time:
            raise ValueError('Selected dates should be only in future')

        if (end_time - start_time).seconds // 60 != settings.TIME_SLOT_MINUTES:
            raise ValueError(F'Duration between start and end time not equal to {settings.TIME_SLOT_MINUTES}')
        if not end_time or not start_time:
            raise ValueError('start and end time are mandatory fields')

        return start_time

    class Config:
        orm_mode = True


class ReservationDetailsSchema(ReservationBaseSchema):
    id: int

    class Config:
        orm_mode = True


class CalculateTimeSlot(BaseModel):
    date: datetime


class TimeSlotSchema(BaseModel):
    start: datetime
    end: datetime

    class Config:
        orm_mode = True
