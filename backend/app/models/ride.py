from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Ride(Base):
    __tablename__ = "rides"

    __table_args__ = (
        CheckConstraint(
            "status IN ('requested', 'accepted', 'in_progress', 'completed', 'cancelled')",
            name="ck_ride_status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    passenger_name: Mapped[str] = mapped_column(String(120), nullable=False)
    pickup_location: Mapped[str] = mapped_column(String(255), nullable=False)
    dropoff_location: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="requested"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
