import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import {
  cancelMaintenanceRequest,
  completeMaintenanceRequest,
  getMaintenanceRequest,
  startMaintenanceRequest,
} from "../../api/maintenance";

import { useAuth } from "../../context/useAuth";

function formatLabel(value, fallback = "—") {
  if (!value) return fallback;

  return String(value)
    .toLowerCase()
    .split("_")
    .map(
      (word) =>
        word.charAt(0).toUpperCase() + word.slice(1)
    )
    .join(" ");
}

function formatCurrency(value) {
  if (value === null || value === undefined || value === "") {
    return "—";
  }

  const amount = Number(value);

  if (!Number.isFinite(amount)) {
    return "—";
  }

  return new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
  }).format(amount);
}

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleDateString("en-PH", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function formatDateTime(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleString("en-PH", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function getStatusStyle(status) {
  const styles = {
    PENDING:
      "bg-amber-50 text-amber-700 ring-amber-600/20",
    IN_PROGRESS:
      "bg-blue-50 text-blue-700 ring-blue-600/20",
    COMPLETED:
      "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
    CANCELLED:
      "bg-slate-100 text-slate-600 ring-slate-500/20",
  };

  return (
    styles[status] ||
    "bg-slate-100 text-slate-600 ring-slate-500/20"
  );
}

function getPriorityStyle(priority) {
  const styles = {
    LOW: "bg-slate-100 text-slate-600",
    MEDIUM: "bg-blue-50 text-blue-700",
    HIGH: "bg-orange-50 text-orange-700",
    URGENT: "bg-red-50 text-red-700",
  };

  return (
    styles[priority] ||
    "bg-slate-100 text-slate-600"
  );
}

function getUnitLabel(request) {
  return (
    request.unit_number ||
    request.unit?.unit_number ||
    request.unit?.name ||
    request.unit?.id ||
    request.unit ||
    "—"
  );
}

function DetailItem({ label, value }) {
  return (
    <div className="border-b border-slate-100 py-4 last:border-b-0">
      <p className="text-sm text-slate-500">
        {label}
      </p>

      <p className="mt-1 break-words text-sm font-semibold text-slate-900">
        {value ?? "—"}
      </p>
    </div>
  );
}

function MaintenanceDetail() {
  const { id } = useParams();
  const { user } = useAuth();

  const [request, setRequest] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionError, setActionError] = useState("");
  const [actionSuccess, setActionSuccess] = useState("");
  const [activeAction, setActiveAction] = useState("");
  const [actualCost, setActualCost] = useState("");

  const loadRequest = async () => {
    setIsLoading(true);
    setError("");

    try {
      const data = await getMaintenanceRequest(id);
      setRequest(data);
    } catch (requestError) {
      setRequest(null);

      if (requestError?.response?.status === 404) {
        setError("Maintenance request not found.");
      } else {
        setError(
          requestError?.response?.data?.detail ||
            "Unable to load maintenance request. Please try again."
        );
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    let isActive = true;

    const fetchRequest = async () => {
      setIsLoading(true);
      setError("");

      try {
        const data = await getMaintenanceRequest(id);

        if (isActive) {
          setRequest(data);
        }
      } catch (requestError) {
        if (isActive) {
          setRequest(null);

          setError(
            requestError?.response?.status === 404
              ? "Maintenance request not found."
              : requestError?.response?.data?.detail ||
                  "Unable to load maintenance request. Please try again."
          );
        }
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    };

    fetchRequest();

    return () => {
      isActive = false;
    };
  }, [id]);

  const runAction = async (action, callback) => {
    setActiveAction(action);
    setActionError("");
    setActionSuccess("");

    try {
      const updatedRequest = await callback();

      setRequest(updatedRequest);

      if (action === "start") {
        setActionSuccess(
          "Maintenance work has been started successfully."
        );
      }

      if (action === "complete") {
        setActionSuccess(
          "Maintenance request has been completed successfully."
        );
      }

      if (action === "cancel") {
        setActionSuccess(
          "Maintenance request has been cancelled successfully."
        );
      }

      setActualCost("");
    } catch (requestError) {
      setActionError(
        requestError?.response?.data?.detail ||
          requestError?.response?.data?.message ||
          "The requested action could not be completed."
      );
    } finally {
      setActiveAction("");
    }
  };

  const handleStart = () => {
    runAction("start", () =>
      startMaintenanceRequest(id)
    );
  };

  const handleComplete = () => {
    const payload = {};

    if (actualCost.trim()) {
      payload.actual_cost = actualCost.trim();
    }

    runAction("complete", () =>
      completeMaintenanceRequest(id, payload)
    );
  };

  const handleCancel = () => {
    const confirmed = window.confirm(
      "Are you sure you want to cancel this maintenance request?"
    );

    if (!confirmed) {
      return;
    }

    runAction("cancel", () =>
      cancelMaintenanceRequest(id)
    );
  };

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600" />

          <p className="mt-4 text-sm text-slate-500">
            Loading maintenance request...
          </p>
        </div>
      </div>
    );
  }

  if (error || !request) {
    return (
      <div className="mx-auto max-w-4xl">
        <Link
          to="/maintenance"
          className="text-sm font-semibold text-blue-600 transition hover:text-blue-700"
        >
          ← Back to Maintenance
        </Link>

        <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-6">
          <h2 className="text-lg font-bold text-red-900">
            Unable to Load Maintenance Request
          </h2>

          <p className="mt-2 text-sm leading-6 text-red-700">
            {error ||
              "The requested maintenance request could not be found."}
          </p>

          <button
            type="button"
            onClick={loadRequest}
            className="mt-5 rounded-xl bg-red-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const isAdminOrManager =
    user?.role === "ADMIN" ||
    user?.role === "PROPERTY_MANAGER";

  const isTenant =
    user?.role === "TENANT";

  const canStart =
    isAdminOrManager &&
    request.status === "PENDING";

  const canComplete =
    isAdminOrManager &&
    request.status === "IN_PROGRESS";

  const canCancel =
    isTenant &&
    request.status === "PENDING";

  const isActionRunning = Boolean(activeAction);

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <section className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link
            to="/maintenance"
            className="text-sm font-semibold text-blue-600 transition hover:text-blue-700"
          >
            ← Back to Maintenance
          </Link>

          <p className="mt-5 text-sm font-semibold uppercase tracking-wider text-slate-500">
            Maintenance Request
          </p>

          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
            {request.title || `Request #${request.id}`}
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            Request #{request.id} · Submitted{" "}
            {formatDate(request.created_at)}
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <span
            className={`inline-flex items-center rounded-full px-3 py-1.5 text-sm font-semibold ring-1 ring-inset ${getStatusStyle(
              request.status
            )}`}
          >
            {formatLabel(request.status)}
          </span>

          <span
            className={`inline-flex items-center rounded-full px-3 py-1.5 text-sm font-semibold ${getPriorityStyle(
              request.priority
            )}`}
          >
            {formatLabel(request.priority)}
          </span>
        </div>
      </section>

      {actionSuccess && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm font-medium text-emerald-700">
          {actionSuccess}
        </div>
      )}

      {actionError && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm font-medium text-red-700">
          {actionError}
        </div>
      )}

      <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-100 bg-slate-50/70 px-6 py-6 sm:px-8">
          <p className="text-sm font-medium text-slate-500">
            Description
          </p>

          <p className="mt-2 whitespace-pre-wrap text-sm leading-7 text-slate-700">
            {request.description || "No description provided."}
          </p>
        </div>

        <div className="grid gap-x-12 px-6 sm:grid-cols-2 sm:px-8">
          <div>
            <DetailItem
              label="Property"
              value={
                request.property?.name ||
                request.property_name ||
                request.property ||
                "—"
              }
            />

            <DetailItem
              label="Unit"
              value={getUnitLabel(request)}
            />

            <DetailItem
              label="Priority"
              value={formatLabel(request.priority)}
            />

            <DetailItem
              label="Submitted"
              value={formatDateTime(request.created_at)}
            />
          </div>

          <div>
            <DetailItem
              label="Assigned Manager"
              value={
                request.assigned_to?.name ||
                request.assigned_to?.email ||
                request.assigned_to ||
                "Not assigned"
              }
            />

            <DetailItem
              label="Estimated Cost"
              value={formatCurrency(request.estimated_cost)}
            />

            <DetailItem
              label="Actual Cost"
              value={formatCurrency(request.actual_cost)}
            />

            <DetailItem
              label="Completed At"
              value={formatDateTime(request.completed_at)}
            />
          </div>
        </div>
      </section>

      {(canStart || canComplete || canCancel) && (
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <div>
            <h2 className="text-lg font-bold text-slate-950">
              Request Actions
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Available workflow actions for your account.
            </p>
          </div>

          <div className="mt-6 space-y-5">
            {canComplete && (
              <div className="max-w-md">
                <label
                  htmlFor="actual-cost"
                  className="block text-sm font-semibold text-slate-700"
                >
                  Actual Cost
                  <span className="ml-1 font-normal text-slate-400">
                    (optional)
                  </span>
                </label>

                <input
                  id="actual-cost"
                  type="number"
                  min="0"
                  step="0.01"
                  value={actualCost}
                  onChange={(event) =>
                    setActualCost(event.target.value)
                  }
                  placeholder="0.00"
                  disabled={isActionRunning}
                  className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:cursor-not-allowed disabled:bg-slate-50"
                />
              </div>
            )}

            <div className="flex flex-wrap gap-3">
              {canStart && (
                <button
                  type="button"
                  onClick={handleStart}
                  disabled={isActionRunning}
                  className="rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {activeAction === "start"
                    ? "Starting..."
                    : "Start Work"}
                </button>
              )}

              {canComplete && (
                <button
                  type="button"
                  onClick={handleComplete}
                  disabled={isActionRunning}
                  className="rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {activeAction === "complete"
                    ? "Completing..."
                    : "Mark Completed"}
                </button>
              )}

              {canCancel && (
                <button
                  type="button"
                  onClick={handleCancel}
                  disabled={isActionRunning}
                  className="rounded-xl border border-red-200 bg-white px-5 py-2.5 text-sm font-semibold text-red-600 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {activeAction === "cancel"
                    ? "Cancelling..."
                    : "Cancel Request"}
                </button>
              )}
            </div>
          </div>
        </section>
      )}

      {!canStart && !canComplete && !canCancel && (
        <section className="rounded-2xl border border-slate-200 bg-slate-50 p-6">
          <p className="text-sm text-slate-500">
            No workflow actions are currently available for
            this request.
          </p>
        </section>
      )}
    </div>
  );
}

export default MaintenanceDetail;