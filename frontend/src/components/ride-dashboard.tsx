
"use client";

import { useCallback, useEffect, useState } from "react";
import type { FormEvent } from "react";

import {
  createRide,
  getRides,
  updateRideStatus,
} from "@/lib/api";

import type {
  Ride,
  RideCreate,
  RideStatus,
} from "@/types/ride";

const statusStyles: Record<RideStatus, string> = {
  requested: "bg-amber-50 text-amber-700 ring-amber-200",
  accepted: "bg-blue-50 text-blue-700 ring-blue-200",
  in_progress: "bg-violet-50 text-violet-700 ring-violet-200",
  completed: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  cancelled: "bg-slate-100 text-slate-600 ring-slate-200",
};

const statusLabels: Record<RideStatus, string> = {
  requested: "Requested",
  accepted: "Accepted",
  in_progress: "In progress",
  completed: "Completed",
  cancelled: "Cancelled",
};

const nextActions: Partial<
  Record<RideStatus, { status: RideStatus; label: string }[]>
> = {
  requested: [
    { status: "accepted", label: "Accept ride" },
    { status: "cancelled", label: "Cancel" },
  ],
  accepted: [
    { status: "in_progress", label: "Start ride" },
    { status: "cancelled", label: "Cancel" },
  ],
  in_progress: [
    { status: "completed", label: "Complete ride" },
  ],
};

const initialForm: RideCreate = {
  passenger_name: "",
  pickup_location: "",
  dropoff_location: "",
};

export default function RideDashboard() {
  const [rides, setRides] = useState<Ride[]>([]);
  const [form, setForm] = useState<RideCreate>(initialForm);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [updatingRideId, setUpdatingRideId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const refreshRides = useCallback(async () => {
    setError("");

    try {
      const data = await getRides();
      setRides(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to load rides.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadInitialRides() {
      try {
        const data = await getRides();

        if (!cancelled) {
          setRides(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Unable to load rides.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadInitialRides();

    return () => {
      cancelled = true;
    };
  }, []);

  async function handleCreateRide(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");
    setSubmitting(true);

    try {
      await createRide(form);
      setForm({ ...initialForm });
      setSuccess("Your ride has been created successfully.");
      await refreshRides();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to create ride.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function handleStatusUpdate(
    rideId: number,
    status: RideStatus,
  ) {
    setError("");
    setSuccess("");
    setUpdatingRideId(rideId);

    try {
      await updateRideStatus(rideId, status);
      setSuccess("Ride status updated successfully.");
      await refreshRides();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unable to update ride.",
      );
    } finally {
      setUpdatingRideId(null);
    }
  }

  const statistics = [
    {
      label: "Total rides",
      value: rides.length,
      detail: "All recorded rides",
    },
    {
      label: "Requested",
      value: rides.filter((ride) => ride.status === "requested").length,
      detail: "Awaiting acceptance",
    },
    {
      label: "Active",
      value: rides.filter(
        (ride) =>
          ride.status === "accepted" || ride.status === "in_progress",
      ).length,
      detail: "Accepted or in progress",
    },
    {
      label: "Completed",
      value: rides.filter((ride) => ride.status === "completed").length,
      detail: "Successfully finished",
    },
  ];

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5 sm:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-lg font-bold text-white">
              R
            </div>

            <div>
              <p className="text-lg font-bold tracking-tight">RideFlow</p>
              <p className="text-xs text-slate-500">
                Ride management platform
              </p>
            </div>
          </div>

          <span className="hidden rounded-full bg-slate-100 px-3 py-2 text-xs font-medium text-slate-600 sm:block">
            Local assessment environment
          </span>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-5 py-8 sm:px-8">
        <section className="mb-8">
          <p className="mb-2 text-sm font-semibold uppercase tracking-wider text-indigo-600">
            Operations overview
          </p>

          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-slate-950">
                Ride dashboard
              </h1>
              <p className="mt-2 text-sm text-slate-500">
                Create, monitor and manage ride requests from one place.
              </p>
            </div>

            <button
              type="button"
              onClick={() => void refreshRides()}
              disabled={loading}
              className="rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:opacity-50"
            >
              {loading ? "Refreshing..." : "Refresh rides"}
            </button>
          </div>
        </section>

        {error && (
          <div
            role="alert"
            className="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
          >
            {error}
          </div>
        )}

        {success && (
          <div
            role="status"
            className="mb-6 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700"
          >
            {success}
          </div>
        )}

        <section className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {statistics.map((stat) => (
            <article
              key={stat.label}
              className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
            >
              <p className="text-sm font-medium text-slate-500">
                {stat.label}
              </p>
              <p className="mt-3 text-3xl font-bold tracking-tight">
                {loading ? "—" : stat.value}
              </p>
              <p className="mt-2 text-xs text-slate-400">
                {stat.detail}
              </p>
            </article>
          ))}
        </section>

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-[360px_minmax(0,1fr)]">
          <section className="h-fit rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-6">
              <h2 className="text-lg font-bold">Create a ride</h2>
              <p className="mt-1 text-sm text-slate-500">
                Enter the passenger and journey details.
              </p>
            </div>

            <form onSubmit={handleCreateRide} className="space-y-4">
              <div>
                <label
                  htmlFor="passenger_name"
                  className="mb-1.5 block text-sm font-medium text-slate-700"
                >
                  Passenger name
                </label>
                <input
                  id="passenger_name"
                  required
                  minLength={2}
                  maxLength={120}
                  value={form.passenger_name}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      passenger_name: event.target.value,
                    })
                  }
                  placeholder="Enter passenger name"
                  className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
                />
              </div>

              <div>
                <label
                  htmlFor="pickup_location"
                  className="mb-1.5 block text-sm font-medium text-slate-700"
                >
                  Pickup location
                </label>
                <input
                  id="pickup_location"
                  required
                  minLength={2}
                  maxLength={255}
                  value={form.pickup_location}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      pickup_location: event.target.value,
                    })
                  }
                  placeholder="Where should the ride start?"
                  className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
                />
              </div>

              <div>
                <label
                  htmlFor="dropoff_location"
                  className="mb-1.5 block text-sm font-medium text-slate-700"
                >
                  Drop-off location
                </label>
                <input
                  id="dropoff_location"
                  required
                  minLength={2}
                  maxLength={255}
                  value={form.dropoff_location}
                  onChange={(event) =>
                    setForm({
                      ...form,
                      dropoff_location: event.target.value,
                    })
                  }
                  placeholder="Where should the ride end?"
                  className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full rounded-lg bg-indigo-600 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {submitting ? "Creating ride..." : "Create ride"}
              </button>
            </form>
          </section>

          <section className="min-w-0 rounded-2xl border border-slate-200 bg-white shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-200 px-6 py-5">
              <div>
                <h2 className="text-lg font-bold">Recent rides</h2>
                <p className="mt-1 text-sm text-slate-500">
                  Latest ride requests and their current status.
                </p>
              </div>

              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                {rides.length} records
              </span>
            </div>

            <div className="divide-y divide-slate-100">
              {loading ? (
                <p className="px-6 py-12 text-center text-sm text-slate-500">
                  Loading rides...
                </p>
              ) : rides.length === 0 ? (
                <div className="px-6 py-14 text-center">
                  <p className="font-semibold text-slate-700">
                    No rides found
                  </p>
                  <p className="mt-1 text-sm text-slate-500">
                    Create your first ride using the form.
                  </p>
                </div>
              ) : (
                rides.map((ride) => (
                  <article key={ride.id} className="px-6 py-5">
                    <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="font-semibold text-slate-900">
                            {ride.passenger_name}
                          </h3>
                          <span className="text-xs text-slate-400">
                            Ride #{ride.id}
                          </span>
                        </div>

                        <div className="mt-3 space-y-2 text-sm">
                          <p className="text-slate-600">
                            <span className="mr-2 font-medium text-slate-400">
                              FROM
                            </span>
                            {ride.pickup_location}
                          </p>

                          <p className="text-slate-600">
                            <span className="mr-2 font-medium text-slate-400">
                              TO
                            </span>
                            {ride.dropoff_location}
                          </p>
                        </div>

                        <p className="mt-3 text-xs text-slate-400">
                          Created{" "}
                          {new Date(ride.created_at).toLocaleString()}
                        </p>
                      </div>

                      <span
                        className={`w-fit rounded-full px-3 py-1 text-xs font-semibold ring-1 ring-inset ${statusStyles[ride.status]}`}
                      >
                        {statusLabels[ride.status]}
                      </span>
                    </div>

                    <div className="mt-4 flex flex-wrap gap-2">
                      {(nextActions[ride.status] ?? []).map((action) => (
                        <button
                          key={action.status}
                          type="button"
                          disabled={updatingRideId === ride.id}
                          onClick={() =>
                            void handleStatusUpdate(
                              ride.id,
                              action.status,
                            )
                          }
                          className={
                            action.status === "cancelled"
                              ? "rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-600 transition hover:bg-slate-50 disabled:opacity-50"
                              : "rounded-lg bg-slate-900 px-3 py-2 text-xs font-semibold text-white transition hover:bg-slate-700 disabled:opacity-50"
                          }
                        >
                          {updatingRideId === ride.id
                            ? "Updating..."
                            : action.label}
                        </button>
                      ))}
                    </div>
                  </article>
                ))
              )}
            </div>
          </section>
        </div>

        <footer className="mt-8 border-t border-slate-200 py-5 text-center text-xs text-slate-400">
          RideFlow · Local assessment environment · FastAPI + Next.js
        </footer>
      </div>
    </main>
  );
}
