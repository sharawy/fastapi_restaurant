from datetime import datetime, timedelta
from typing import Union, Optional

from fastapi import Depends
from sqlalchemy import Date, cast
from sqlalchemy.orm import Session

from app.dependencies import get_db
from reservation.models import Reservation
import restaurant_management.crud as restaurant_crud


class TimeSlot():

    # https://github.com/ErikBjare/timeslot/blob/master/src/timeslot/timeslot.py
    # Inspired by: http://www.codeproject.com/Articles/168662/Time-Period-Library-for-NET
    def __init__(self, start: datetime, end: datetime) -> None:
        # TODO: Introduce once tested in production (where negative duration events might occur)
        # if start > end:
        #     raise ValueError("Timeslot cannot have negative duration, start '{}' came after end '{}'".format(start,
        #     end))
        self.start = start
        self.end = end

    def __repr__(self) -> str:
        return "<Timeslot(start={}, end={})>".format(self.start, self.end)

    @property
    def duration(self) -> timedelta:
        return self.end - self.start

    def overlaps(self, other: "TimeSlot") -> bool:
        """Checks if this time slot is overlapping partially or entirely with another timeslot"""
        return (
                self.start <= other.start < self.end
                or self.start < other.end <= self.end
                or self in other
        )

    def intersects(self, other: "TimeSlot") -> bool:
        """Alias for overlaps"""
        return self.overlaps(other)

    def contains(self, other: Union[datetime, "TimeSlot"]) -> bool:
        """Checks if this time slot contains the entirety of another timeslot or a datetime"""
        if isinstance(other, TimeSlot):
            return self.start <= other.start and other.end <= self.end
        elif isinstance(other, datetime):
            return self.start <= other <= self.end
        else:
            raise TypeError("argument of invalid type '{}'".format(type(other)))

    def __contains__(self, other: Union[datetime, "TimeSlot"]) -> bool:
        return self.contains(other)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TimeSlot):
            return self.start == other.start and self.end == other.end
        else:
            return False

    def __lt__(self, other: object) -> bool:
        # implemented to easily allow sorting of a list of timeslots
        if isinstance(other, TimeSlot):
            return self.start < other.start
        else:
            raise TypeError(
                "operator not supported between instaces of '{}' and '{}'".format(
                    type(self), type(other)
                )
            )

    def intersection(self, other: "TimeSlot") -> Optional["TimeSlot"]:
        """Returns the timeslot contained in both slots"""
        # https://stackoverflow.com/posts/3721426/revisions
        if self.contains(other):
            # Entirety of other is within self
            return other
        elif self.start <= other.start < self.end:
            # End part of self intersects
            return TimeSlot(other.start, self.end)
        elif self.start < other.end <= self.end:
            # Start part of self intersects
            return TimeSlot(self.start, other.end)
        elif other.contains(self):
            # Entirety of self is within other
            return self
        return None

    def adjacent(self, other: "TimeSlot") -> bool:
        """Iff timeslots are exactly next to each other, return True."""
        return self.start == other.end or self.end == other.start

    def gap(self, other: "TimeSlot") -> Optional["TimeSlot"]:
        """If slots are separated by a non-zero gap, return the gap as a new timeslot, else None"""
        if self.end < other.start:
            return TimeSlot(self.end, other.start)
        elif other.end < self.start:
            return TimeSlot(other.end, self.start)
        else:
            return None

    def union(self, other: "TimeSlot") -> "TimeSlot":
        if not self.gap(other):
            return TimeSlot(min(self.start, other.start), max(self.end, other.end))
        else:
            raise Exception("Time slots must not have a gap if they are to be unioned")

    def __hash__(self):
        return hash(str(self.start.timestamp()) + str(self.end.timestamp()))


def get_daily_slots(start, end, slot, date):
    # combine start time to respective day
    dt = datetime.combine(date.date(), start.time())
    slots = set([TimeSlot(dt, dt + timedelta(minutes=slot))])
    # increment current time by slot till the end time
    while dt.time() < end.time():
        dt = dt + timedelta(minutes=slot)
        time_slot = TimeSlot(dt, dt + timedelta(minutes=slot))
        slots.add(time_slot)
    return slots


def get_table_available_slots(table_id, reservation_time: datetime, db: Session):
    table = restaurant_crud.get_table_by_id(table_id, db)
    restaurant = restaurant_crud.get_restaurant_by_id(table.restaurant_id, db)
    assert restaurant.open_hour <= reservation_time.hour < restaurant.close_hour, "Reservation should be be in open " \
                                                                                  "hours only"
    start_time = reservation_time.replace(hour=restaurant.open_hour, minute=0)
    end_time = reservation_time.replace(hour=restaurant.close_hour, minute=0)
    slot = 15
    available_slots = set()
    reserved_slots = set()
    all_daily_slots = get_daily_slots(start_time, end_time, slot, reservation_time)
    reservations = db.query(Reservation).filter(
        Reservation.table_id == table.id,
        cast(Reservation.start_time, Date) == reservation_time.date()
    )
    print(len(all_daily_slots))

    for reservation in reservations:
        reserved_slots.add(
            TimeSlot(reservation.start_time.replace(tzinfo=None), reservation.end_time.replace(tzinfo=None)))
    available_slots = all_daily_slots - reserved_slots
    print(len(available_slots))
    return available_slots


