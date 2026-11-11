from app.core.cache import redis_client


def test_create_ride(client):
    response = client.post(
        "/api/v1/rides",
        json={
            "passenger_name": "Test Passenger",
            "pickup_location": "Islamabad F-10",
            "dropoff_location": "Blue Area Islamabad",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["id"] is not None
    assert data["passenger_name"] == "Test Passenger"
    assert data["status"] == "requested"


def test_list_rides(client):
    client.post(
        "/api/v1/rides",
        json={
            "passenger_name": "Test Passenger",
            "pickup_location": "Islamabad F-10",
            "dropoff_location": "Blue Area Islamabad",
        },
    )

    response = client.get("/api/v1/rides")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["passenger_name"] == "Test Passenger"


def test_get_existing_ride(client):
    create_response = client.post(
        "/api/v1/rides",
        json={
            "passenger_name": "Test Passenger",
            "pickup_location": "Islamabad F-10",
            "dropoff_location": "Blue Area Islamabad",
        },
    )

    ride_id = create_response.json()["id"]

    response = client.get(f"/api/v1/rides/{ride_id}")

    assert response.status_code == 200
    assert response.json()["id"] == ride_id


def test_get_nonexistent_ride(client):
    response = client.get("/api/v1/rides/999999")

    assert response.status_code == 404


def test_create_ride_validation(client):
    response = client.post(
        "/api/v1/rides",
        json={
            "passenger_name": "A",
            "pickup_location": "Islamabad",
            "dropoff_location": "Blue Area",
        },
    )

    assert response.status_code == 422


def test_valid_status_transitions(client):
    create_response = client.post(
        "/api/v1/rides",
        json={
            "passenger_name": "Test Passenger",
            "pickup_location": "Islamabad F-10",
            "dropoff_location": "Blue Area Islamabad",
        },
    )

    ride_id = create_response.json()["id"]

    for new_status in ["accepted", "in_progress", "completed"]:
        response = client.patch(
            f"/api/v1/rides/{ride_id}/status",
            json={"status": new_status},
        )

        assert response.status_code == 200
        assert response.json()["status"] == new_status


def test_invalid_status_transition(client):
    create_response = client.post(
        "/api/v1/rides",
        json={
            "passenger_name": "Test Passenger",
            "pickup_location": "Islamabad F-10",
            "dropoff_location": "Blue Area Islamabad",
        },
    )

    ride_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/rides/{ride_id}/status",
        json={"status": "completed"},
    )

    assert response.status_code == 409
    assert "Invalid ride status transition" in response.json()["detail"]


def test_completed_ride_cannot_be_reopened(client):
    create_response = client.post(
        "/api/v1/rides",
        json={
            "passenger_name": "Test Passenger",
            "pickup_location": "Islamabad F-10",
            "dropoff_location": "Blue Area Islamabad",
        },
    )

    ride_id = create_response.json()["id"]

    for new_status in ["accepted", "in_progress", "completed"]:
        client.patch(
            f"/api/v1/rides/{ride_id}/status",
            json={"status": new_status},
        )

    response = client.patch(
        f"/api/v1/rides/{ride_id}/status",
        json={"status": "in_progress"},
    )

    assert response.status_code == 409


def test_get_ride_stores_cache(client):
    create_response = client.post(
        "/api/v1/rides",
        json={
            "passenger_name": "Cache Passenger",
            "pickup_location": "Islamabad F-10",
            "dropoff_location": "Blue Area Islamabad",
        },
    )

    ride_id = create_response.json()["id"]

    response = client.get(f"/api/v1/rides/{ride_id}")

    assert response.status_code == 200
    assert redis_client.exists(f"rideflow:ride:{ride_id}") == 1


def test_status_update_invalidates_ride_cache(client):
    create_response = client.post(
        "/api/v1/rides",
        json={
            "passenger_name": "Cache Passenger",
            "pickup_location": "Islamabad F-10",
            "dropoff_location": "Blue Area Islamabad",
        },
    )

    ride_id = create_response.json()["id"]

    client.get(f"/api/v1/rides/{ride_id}")

    cache_key = f"rideflow:ride:{ride_id}"
    assert redis_client.exists(cache_key) == 1

    update_response = client.patch(
        f"/api/v1/rides/{ride_id}/status",
        json={"status": "accepted"},
    )

    assert update_response.status_code == 200
    assert redis_client.exists(cache_key) == 0

    refreshed_response = client.get(f"/api/v1/rides/{ride_id}")
    assert refreshed_response.json()["status"] == "accepted"


def test_create_ride_invalidates_list_cache(client):
    client.post(
        "/api/v1/rides",
        json={
            "passenger_name": "First Passenger",
            "pickup_location": "Islamabad F-10",
            "dropoff_location": "Blue Area Islamabad",
        },
    )

    client.get("/api/v1/rides")

    cache_key = "rideflow:rides:list:0:20"
    assert redis_client.exists(cache_key) == 1

    create_response = client.post(
        "/api/v1/rides",
        json={
            "passenger_name": "Second Passenger",
            "pickup_location": "Islamabad G-10",
            "dropoff_location": "F-7 Islamabad",
        },
    )

    assert create_response.status_code == 201
    assert redis_client.exists(cache_key) == 0

    refreshed_response = client.get("/api/v1/rides")
    assert len(refreshed_response.json()) == 2
