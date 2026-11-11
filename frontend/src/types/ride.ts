export type RideStatus =
  | "requested"
  | "accepted"
  | "in_progress"
  | "completed"
  | "cancelled";

export interface Ride {
  id: number;
  passenger_name: string;
  pickup_location: string;
  dropoff_location: string;
  status: RideStatus;
  created_at: string;
  updated_at: string;
}

export interface RideCreate {
  passenger_name: string;
  pickup_location: string;
  dropoff_location: string;
}

export interface RideStatusUpdate {
  status: RideStatus;
}
