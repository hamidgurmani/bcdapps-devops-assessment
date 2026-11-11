from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.cache import (
    get_cached,
    invalidate_ride_cache,
    set_cached,
)
from app.db.session import get_db
from app.models.ride import Ride
from app.schemas.ride import RideCreate, RideResponse, RideStatusUpdate


router = APIRouter(prefix="/rides", tags=["Rides"])


@router.post(
    "",
    response_model=RideResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ride(payload: RideCreate, db: Session = Depends(get_db)):
    ride = Ride(**payload.model_dump())
    db.add(ride)
    db.commit()
    db.refresh(ride)

    invalidate_ride_cache(ride.id)

    return ride


@router.get("", response_model=list[RideResponse])
def list_rides(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    cache_key = f"rides:list:{skip}:{limit}"
    cached_rides = get_cached(cache_key)

    if cached_rides is not None:
        return cached_rides

    statement = (
        select(Ride)
        .order_by(Ride.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    rides = db.scalars(statement).all()

    response = [
        RideResponse.model_validate(ride).model_dump(mode="json")
        for ride in rides
    ]

    set_cached(cache_key, response)

    return response


@router.get("/{ride_id}", response_model=RideResponse)
def get_ride(ride_id: int, db: Session = Depends(get_db)):
    cache_key = f"ride:{ride_id}"
    cached_ride = get_cached(cache_key)

    if cached_ride is not None:
        return cached_ride

    ride = db.get(Ride, ride_id)

    if ride is None:
        raise HTTPException(status_code=404, detail="Ride not found")

    response = RideResponse.model_validate(ride).model_dump(mode="json")
    set_cached(cache_key, response)

    return response


@router.patch("/{ride_id}/status", response_model=RideResponse)
def update_ride_status(
    ride_id: int,
    payload: RideStatusUpdate,
    db: Session = Depends(get_db),
):
    ride = db.get(Ride, ride_id)

    if ride is None:
        raise HTTPException(status_code=404, detail="Ride not found")

    allowed_transitions = {
        "requested": {"accepted", "cancelled"},
        "accepted": {"in_progress", "cancelled"},
        "in_progress": {"completed"},
        "completed": set(),
        "cancelled": set(),
    }

    new_status = payload.status.value

    if new_status not in allowed_transitions[ride.status]:
        raise HTTPException(
            status_code=409,
            detail=f"Invalid ride status transition: {ride.status} -> {new_status}",
        )

    ride.status = new_status
    db.commit()
    db.refresh(ride)

    invalidate_ride_cache(ride_id)

    return ride
