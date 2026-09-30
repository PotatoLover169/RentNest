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

function formatUnitType(value) {
  if (!value) {
    return "—";
  }

  return value
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatStatus(value) {
  if (!value) {
    return "Unknown";
  }

  return value
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function getStatusVariant(status) {
  switch (status) {
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

function formatRent(value) {
  if (value === null || value === undefined || value === "") {
    return "—";
  }

  return `₱${Number(value).toLocaleString("en-PH", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function formatDate(value) {
  if (!value) {
    return "—";
  }

  return new Date(value).toLocaleDateString("en-PH", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function getErrorMessage(error) {
  const data = error?.response?.data;

  if (data?.detail) {
    return Array.isArray(data.detail)
      ? data.detail.join(" ")
      : data.detail;
  }

  if (data?.message) {
    return data.message;
  }

  if (data && typeof data === "object") {
    const messages = Object.values(data)
      .flatMap((value) =>
        Array.isArray(value) ? value : [value],
      )
      .filter((value) => typeof value === "string");

    if (messages.length > 0) {
      return messages.join(" ");
    }
  }

  return "Something went wrong. Please try again.";
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

  const loadUnit = useCallback(async () => {
    try {
      setIsLoading(true);
      setError("");

      const data = await getUnit(id);

      setUnit(data);
      setSelectedStatus(data.status ?? "");
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    // Data fetching is intentionally triggered on mount.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadUnit();
    }, [loadUnit]);

  const handleStatusUpdate = async () => {
    if (!unit || !selectedStatus) {
      return;
    }

    if (selectedStatus === unit.status) {
      setSuccessMessage("");
      setActionError("The unit is already using this status.");
      return;
    }

    const confirmed = window.confirm(
      `Change the status of Unit ${unit.unit_number} to ${formatStatus(selectedStatus)}?`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setIsActionLoading(true);
      setActionError("");
      setSuccessMessage("");

      const updatedUnit = await updateUnitStatus(id, {
        status: selectedStatus,
      });

      setUnit(updatedUnit);
      setSelectedStatus(updatedUnit.status);
      setSuccessMessage("Unit status updated successfully.");
    } catch (requestError) {
      setActionError(getErrorMessage(requestError));
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleDeactivate = async () => {
    if (!unit) {
      return;
    }

    const confirmed = window.confirm(
      `Deactivate Unit ${unit.unit_number}? This action will mark the unit as inactive.`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setIsActionLoading(true);
      setActionError("");
      setSuccessMessage("");

      const updatedUnit = await deactivateUnit(id);

      setUnit(updatedUnit);
      setSelectedStatus(updatedUnit.status);
      setSuccessMessage("Unit deactivated successfully.");
    } catch (requestError) {
      setActionError(getErrorMessage(requestError));
    } finally {
      setIsActionLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="mx-auto max-w-5xl space-y-8">
        <PageHeader
          eyebrow="Management"
          title="Unit Details"
          description="Loading unit information..."
        />

        <LoadingState message="Loading unit..." />
      </div>
    );
  }

  if (error || !unit) {
    return (
      <div className="mx-auto max-w-5xl space-y-8">
        <PageHeader
          eyebrow="Management"
          title="Unit Details"
          description="Unable to load unit information."
        />

        <ErrorState
          title="Unable to load unit"
          message={error || "The requested unit could not be found."}
          action={
            <div className="flex gap-3">
              <Button
                variant="secondary"
                onClick={loadUnit}
              >
                Try Again
              </Button>

              <Button
                variant="ghost"
                onClick={() => navigate("/units")}
              >
                Back to Units
              </Button>
            </div>
          }
        />
      </div>
    );
  }

  const isInactive = unit.status === "INACTIVE";

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <PageHeader
        eyebrow="Unit Management"
        title={`Unit ${unit.unit_number}`}
        description="View unit information and manage its current status."
        action={
          <div className="flex flex-wrap gap-3">
            <Button
              variant="secondary"
              onClick={() => navigate("/units")}
            >
              Back to Units
            </Button>

            {!isInactive && (
              <Button
                onClick={() =>
                  navigate(`/units/${id}/edit`)
                }
              >
                Edit Unit
              </Button>
            )}
          </div>
        }
      />

      {actionError && (
        <div
          role="alert"
          className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          {actionError}
        </div>
      )}

      {successMessage && (
        <div
          role="status"
          className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700"
        >
          {successMessage}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="p-6 lg:col-span-2">
          <div className="flex flex-col gap-4 border-b border-slate-200 pb-6 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="text-sm font-medium text-slate-500">
                Unit
              </p>

              <h2 className="mt-1 text-2xl font-semibold text-slate-950">
                {unit.unit_number}
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                {formatUnitType(unit.unit_type)}
              </p>
            </div>

            <Badge variant={getStatusVariant(unit.status)}>
              {formatStatus(unit.status)}
            </Badge>
          </div>

          <div className="grid gap-6 py-6 sm:grid-cols-2 lg:grid-cols-3">
            <div>
              <p className="text-sm text-slate-500">
                Monthly Rent
              </p>

              <p className="mt-1 text-lg font-semibold text-slate-950">
                {formatRent(unit.monthly_rent)}
              </p>
            </div>

            <div>
              <p className="text-sm text-slate-500">
                Bedrooms
              </p>

              <p className="mt-1 text-lg font-semibold text-slate-950">
                {unit.bedrooms ?? 0}
              </p>
            </div>

            <div>
              <p className="text-sm text-slate-500">
                Bathrooms
              </p>

              <p className="mt-1 text-lg font-semibold text-slate-950">
                {unit.bathrooms ?? 0}
              </p>
            </div>
          </div>

          <div className="border-t border-slate-200 pt-6">
            <h3 className="text-base font-semibold text-slate-950">
              Description
            </h3>

            <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-600">
              {unit.description?.trim()
                ? unit.description
                : "No description has been added for this unit."}
            </p>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-lg font-semibold text-slate-950">
            Unit Status
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Update the current operational status of this unit.
          </p>

          <div className="mt-5">
            <label
              htmlFor="status"
              className="mb-2 block text-sm font-medium text-slate-700"
            >
              Status
            </label>

            <select
              id="status"
              value={selectedStatus}
              onChange={(event) => {
                setSelectedStatus(event.target.value);
                setActionError("");
                setSuccessMessage("");
              }}
              disabled={
                isActionLoading || isInactive
              }
              className="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-slate-900 focus:ring-2 focus:ring-slate-900/10 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-500"
            >
              {STATUS_OPTIONS.map((status) => (
                <option
                  key={status.value}
                  value={status.value}
                >
                  {status.label}
                </option>
              ))}
            </select>
          </div>

          <Button
            className="mt-4 w-full"
            onClick={handleStatusUpdate}
            disabled={
              isActionLoading ||
              isInactive ||
              selectedStatus === unit.status
            }
          >
            {isActionLoading
              ? "Updating..."
              : "Update Status"}
          </Button>

          {!isInactive && (
            <div className="mt-6 border-t border-slate-200 pt-6">
              <h3 className="text-sm font-semibold text-slate-950">
                Deactivate Unit
              </h3>

              <p className="mt-1 text-sm leading-5 text-slate-500">
                Deactivate this unit when it should no longer
                be available for normal management.
              </p>

              <Button
                variant="danger"
                className="mt-4 w-full"
                onClick={handleDeactivate}
                disabled={isActionLoading}
              >
                {isActionLoading
                  ? "Processing..."
                  : "Deactivate Unit"}
              </Button>
            </div>
          )}

          {isInactive && (
            <div className="mt-6 rounded-lg border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm font-medium text-slate-700">
                This unit is inactive.
              </p>

              <p className="mt-1 text-xs leading-5 text-slate-500">
                Inactive units cannot be edited or have their
                operational status changed.
              </p>
            </div>
          )}
        </Card>
      </div>

      <Card className="p-6">
        <h2 className="text-lg font-semibold text-slate-950">
          Record Information
        </h2>

        <div className="mt-5 grid gap-5 sm:grid-cols-2">
          <div>
            <p className="text-sm text-slate-500">
              Created
            </p>

            <p className="mt-1 text-sm font-medium text-slate-900">
              {formatDate(unit.created_at)}
            </p>
          </div>

          <div>
            <p className="text-sm text-slate-500">
              Last Updated
            </p>

            <p className="mt-1 text-sm font-medium text-slate-900">
              {formatDate(unit.updated_at)}
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}

export default UnitDetails;