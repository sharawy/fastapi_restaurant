from sqlalchemy import Integer, Column, String, ForeignKey, DateTime

from app.database import Base


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    main_guest_name = Column(String)
    number_of_customers = Column(Integer, default=1)
    table_id = Column(Integer, ForeignKey("tables.id"))
    start_time = Column(DateTime())
    end_time = Column(DateTime())

    @property
    def duration(self):
        return self.end_time - self.end_time
