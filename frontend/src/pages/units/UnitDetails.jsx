
import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  deactivateUnit,
  getUnit,
  updateUnitStatus,
} from "../../api/units";
import {
  Badge,
  Button,
  Card,
  ErrorState,
  LoadingState,
  PageHeader,
} from "../../components/ui";

const STATUS_OPTIONS = [
  { value: "AVAILABLE", label: "Available" },
  { value: "OCCUPIED", label: "Occupied" },
  { value: "MAINTENANCE", label: "Maintenance" },
];

function formatLabel(value) {
  if (!value) return "Not specified";

  return String(value)
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatRent(value) {
  if (value === null || value === undefined || value === "") return "—";

  const amount = Number(value);
  if (!Number.isFinite(amount)) return "—";

  return `₱${amount.toLocaleString("en-PH", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function formatDate(value) {
  if (!value) return "Not available";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Not available";

  return new Intl.DateTimeFormat("en-PH", {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(date);
}

function getErrorMessage(error) {
  const data = error?.response?.data;

  if (data?.detail) {
    return Array.isArray(data.detail) ? data.detail.join(" ") : data.detail;
  }

  if (data?.message) return data.message;

  if (data && typeof data === "object") {
    const messages = Object.values(data)
      .flatMap((value) => Array.isArray(value) ? value : [value])
      .filter((value) => typeof value === "string");

    if (messages.length) return messages.join(" ");
  }

  return "Something went wrong. Please try again.";
}

function statusVariant(status) {
  switch (String(status || "").toUpperCase()) {
    case "AVAILABLE":
      return "success";
    case "OCCUPIED":
      return "info";
    case "MAINTENANCE":
      return "warning";
    case "INACTIVE":
      return "neutral";
    default:
      return "neutral";
  }
}

function DetailItem({ label, value }) {
  return (
    <div className="min-w-0">
      <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
        {label}
      </p>
      <p className="mt-2 break-words text-sm font-medium leading-6 text-slate-900">
        {value ?? "Not specified"}
      </p>
    </div>
  );
}

function UnitDetails() {
  const navigate = useNavigate();
  const { id } = useParams();

  const [unit, setUnit] = useState(null);
  const [selectedStatus, setSelectedStatus] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isActionLoading, setIsActionLoading] = useState(false);
  const [error, setError] = useState("");
  const [actionError, setActionError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [lastRefreshed, setLastRefreshed] = useState(null);

  const loadUnit = useCallback(async () => {
    try {
      setIsLoading(true);
      setError("");

      const data = await getUnit(id);
      setUnit(data);
      setSelectedStatus(data.status ?? "");
      setLastRefreshed(new Date());
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    // Load the selected unit when its route identifier changes.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadUnit();
  }, [loadUnit]);

  const handleStatusUpdate = async () => {
    if (!unit || !selectedStatus || isActionLoading) return;

    if (selectedStatus === unit.status) {
      setActionError("Choose a different status before updating.");
      return;
    }

    const confirmed = window.confirm(
      `Change Unit ${unit.unit_number} to ${formatLabel(selectedStatus)}?`,
    );

    if (!confirmed) return;

    try {
      setIsActionLoading(true);
      setActionError("");
      setSuccessMessage("");

      const updatedUnit = await updateUnitStatus(id, {
        status: selectedStatus,
      });

      setUnit(updatedUnit);
      setSelectedStatus(updatedUnit.status ?? "");
      setSuccessMessage("Unit status updated successfully.");
      setLastRefreshed(new Date());
    } catch (requestError) {
      setActionError(getErrorMessage(requestError));
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleDeactivate = async () => {
    if (!unit || isActionLoading) return;

    const confirmed = window.confirm(
      `Deactivate Unit ${unit.unit_number}? This will mark the unit as inactive.`,
    );

    if (!confirmed) return;

    try {
      setIsActionLoading(true);
      setActionError("");
      setSuccessMessage("");

      const updatedUnit = await deactivateUnit(id);

      setUnit(updatedUnit);
      setSelectedStatus(updatedUnit.status ?? "INACTIVE");
      setSuccessMessage("Unit deactivated successfully.");
      setLastRefreshed(new Date());
    } catch (requestError) {
      setActionError(getErrorMessage(requestError));
    } finally {
      setIsActionLoading(false);
    }
  };

  if (isLoading && !unit) {
    return (
      <div className="mx-auto max-w-6xl space-y-8">
        <PageHeader
          eyebrow="Unit Management"
          title="Unit Details"
          description="Loading unit information..."
        />
        <LoadingState message="Loading unit..." />
      </div>
    );
  }

  if (error && !unit) {
    return (
      <div className="mx-auto max-w-6xl space-y-8">
        <PageHeader
          eyebrow="Unit Management"
          title="Unit Details"
          description="Unable to load this unit."
        />
        <ErrorState
          title="Unable to load unit"
          message={error}
          action={
            <div className="flex flex-wrap gap-3">
              <Button variant="secondary" onClick={loadUnit}>
                Try Again
              </Button>
              <Button variant="ghost" onClick={() => navigate("/units")}>
                Back to Units
              </Button>
            </div>
          }
        />
      </div>
    );
  }

  if (!unit) return null;

  const isInactive = String(unit.status || "").toUpperCase() === "INACTIVE";

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <PageHeader
        eyebrow={`Unit Management${unit.id ? ` · #${unit.id}` : ""}`}
        title={`Unit ${unit.unit_number ?? unit.id}`}
        description="Review rental information and manage the unit's operational status."
        action={
          <div className="flex flex-wrap gap-3">
            <Button variant="secondary" onClick={() => navigate("/units")}>
              Back to Units
            </Button>
            <Button
              variant="secondary"
              onClick={loadUnit}
              disabled={isLoading || isActionLoading}
            >
              {isLoading ? "Refreshing..." : "Refresh"}
            </Button>
            {!isInactive && (
              <Button
                onClick={() => navigate(`/units/${id}/edit`)}
                disabled={isActionLoading}
              >
                Edit Unit
              </Button>
            )}
          </div>
        }
      />

      {lastRefreshed && (
        <p className="-mt-5 text-xs text-slate-400">
          Last updated at {lastRefreshed.toLocaleTimeString([], {
            hour: "numeric",
            minute: "2-digit",
          })}
        </p>
      )}

      {error && (
        <div role="alert" className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Refresh failed. The last loaded unit information is still displayed. {error}
        </div>
      )}

      {actionError && (
        <div role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {actionError}
        </div>
      )}

      {successMessage && (
        <div role="status" className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800">
          {successMessage}
        </div>
      )}

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Card className="p-5">
          <p className="text-sm font-medium text-slate-500">Monthly rent</p>
          <p className="mt-2 text-2xl font-bold tracking-tight text-slate-950">
            {formatRent(unit.monthly_rent)}
          </p>
        </Card>
        <Card className="p-5">
          <p className="text-sm font-medium text-slate-500">Unit status</p>
          <div className="mt-3">
            <Badge variant={statusVariant(unit.status)}>
              {formatLabel(unit.status)}
            </Badge>
          </div>
        </Card>
        <Card className="p-5">
          <p className="text-sm font-medium text-slate-500">Bedrooms</p>
          <p className="mt-2 text-2xl font-bold tracking-tight text-slate-950">
            {unit.bedrooms ?? 0}
          </p>
        </Card>
        <Card className="p-5">
          <p className="text-sm font-medium text-slate-500">Bathrooms</p>
          <p className="mt-2 text-2xl font-bold tracking-tight text-slate-950">
            {unit.bathrooms ?? 0}
          </p>
        </Card>
      </section>

      <div className="grid items-start gap-6 lg:grid-cols-3">
        <Card className="overflow-hidden lg:col-span-2">
          <div className="border-b border-slate-100 bg-slate-50/70 px-6 py-5">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="text-sm font-medium text-slate-500">
                  Rental unit
                </p>
                <h2 className="mt-1 text-xl font-bold text-slate-950">
                  Unit {unit.unit_number ?? unit.id}
                </h2>
                <p className="mt-1 text-sm text-slate-500">
                  {formatLabel(unit.unit_type)}
                </p>
              </div>
              <Badge variant={statusVariant(unit.status)}>
                {formatLabel(unit.status)}
              </Badge>
            </div>
          </div>

          <div className="grid gap-x-8 gap-y-7 p-6 sm:grid-cols-2">
            <DetailItem label="Unit ID" value={unit.id ? `#${unit.id}` : "—"} />
            <DetailItem label="Unit number" value={unit.unit_number} />
            <DetailItem label="Unit type" value={formatLabel(unit.unit_type)} />
            <DetailItem label="Property ID" value={unit.property ? `#${unit.property}` : "Not available"} />
            <DetailItem label="Bedrooms" value={unit.bedrooms ?? 0} />
            <DetailItem label="Bathrooms" value={unit.bathrooms ?? 0} />
            <DetailItem label="Monthly rent" value={formatRent(unit.monthly_rent)} />
            <DetailItem label="Current status" value={formatLabel(unit.status)} />
            <DetailItem label="Created" value={formatDate(unit.created_at)} />
            <DetailItem label="Last updated" value={formatDate(unit.updated_at)} />
          </div>

          <div className="border-t border-slate-100 px-6 py-5">
            <h3 className="text-base font-semibold text-slate-950">
              Description
            </h3>
            <p className="mt-2 whitespace-pre-wrap break-words text-sm leading-7 text-slate-600">
              {unit.description?.trim() || "No description has been added for this unit."}
            </p>
          </div>
        </Card>

        <div className="space-y-6">
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-slate-950">
              Manage status
            </h2>
            <p className="mt-1 text-sm leading-6 text-slate-500">
              Update the unit's availability or mark it for maintenance.
            </p>

            <div className="mt-5">
              <label htmlFor="unit-status" className="mb-2 block text-sm font-semibold text-slate-700">
                New status
              </label>
              <select
                id="unit-status"
                value={selectedStatus}
                onChange={(event) => {
                  setSelectedStatus(event.target.value);
                  setActionError("");
                  setSuccessMessage("");
                }}
                disabled={isActionLoading || isInactive}
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 disabled:cursor-not-allowed disabled:bg-slate-100"
              >
                {STATUS_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <Button
              className="mt-4 w-full"
              onClick={handleStatusUpdate}
              disabled={isActionLoading || isInactive || selectedStatus === unit.status}
            >
              {isActionLoading ? "Updating..." : "Update Status"}
            </Button>

            {isInactive && (
              <p className="mt-4 rounded-lg bg-slate-50 p-3 text-sm leading-6 text-slate-600">
                This unit is inactive. Status changes and editing are disabled.
              </p>
            )}
          </Card>

          {!isInactive && (
            <Card className="p-6">
              <h2 className="text-base font-semibold text-slate-950">
                Deactivate unit
              </h2>
              <p className="mt-2 text-sm leading-6 text-slate-500">
                Use this when the unit should no longer be available for normal management.
              </p>
              <Button
                variant="danger"
                className="mt-5 w-full"
                onClick={handleDeactivate}
                disabled={isActionLoading}
              >
                {isActionLoading ? "Processing..." : "Deactivate Unit"}
              </Button>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

export default UnitDetails;
