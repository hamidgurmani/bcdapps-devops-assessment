from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class RideStatus(str, Enum):
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RideCreate(BaseModel):
    passenger_name: str = Field(min_length=2, max_length=120)
    pickup_location: str = Field(min_length=2, max_length=255)
    dropoff_location: str = Field(min_length=2, max_length=255)


class RideStatusUpdate(BaseModel):
    status: RideStatus


class RideResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    passenger_name: str
    pickup_location: str
    dropoff_location: str
    status: RideStatus
    created_at: datetime
    updated_at: datetime
