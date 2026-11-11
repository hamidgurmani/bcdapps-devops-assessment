import type {
  Ride,
  RideCreate,
  RideStatus,
} from "@/types/ride";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  if (!API_BASE_URL) {
    throw new Error("NEXT_PUBLIC_API_BASE_URL is not configured.");
  }

  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");

  if (options.body) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    cache: "no-store",
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null) as
      | { detail?: unknown }
      | null;

    const message =
      typeof errorBody?.detail === "string"
        ? errorBody.detail
        : `API request failed with status ${response.status}.`;

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function getRides(
  skip = 0,
  limit = 20,
): Promise<Ride[]> {
  const params = new URLSearchParams({
    skip: String(skip),
    limit: String(limit),
  });

  return request<Ride[]>(`/rides?${params.toString()}`);
}

export function createRide(payload: RideCreate): Promise<Ride> {
  return request<Ride>("/rides", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateRideStatus(
  rideId: number,
  status: RideStatus,
): Promise<Ride> {
  return request<Ride>(`/rides/${rideId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}
