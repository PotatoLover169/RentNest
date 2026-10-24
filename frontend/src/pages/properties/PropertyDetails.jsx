
import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  deactivateProperty,
  getProperty,
} from "../../api/properties";
import {
  Badge,
  Button,
  Card,
  ErrorState,
  LoadingState,
  PageHeader,
} from "../../components/ui";

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

  return "Something went wrong. Please try again.";
}

function getStatusVariant(status) {
  switch (String(status || "ACTIVE").toUpperCase()) {
    case "ACTIVE":
    case "AVAILABLE":
      return "success";
    case "INACTIVE":
    case "DEACTIVATED":
      return "danger";
    default:
      return "default";
  }
}

function formatLabel(value) {
  if (!value) return "Not specified";

  return String(value)
    .toLowerCase()
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function formatAddress(property) {
  return [
    property.address_line,
    property.city,
    property.province,
    property.postal_code,
  ]
    .filter(Boolean)
    .join(", ");
}

function formatDate(value) {
  if (!value) return "Not available";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Not available";
  }

  return new Intl.DateTimeFormat(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(date);
}

function DetailItem({ label, value }) {
  return (
    <div className="min-w-0">
      <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
        {label}
      </p>
      <p className="mt-2 break-words text-sm font-medium leading-6 text-slate-900">
        {value || "Not specified"}
      </p>
    </div>
  );
}

function PropertyDetails() {
  const navigate = useNavigate();
  const { id } = useParams();

  const [property, setProperty] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDeactivating, setIsDeactivating] = useState(false);
  const [error, setError] = useState("");
  const [actionError, setActionError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [copyMessage, setCopyMessage] = useState("");

  const loadProperty = useCallback(async () => {
    try {
      setIsLoading(true);
      setError("");

      const data = await getProperty(id);
      setProperty(data);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    // Load the selected property when the route changes.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadProperty();
  }, [loadProperty]);

  const handleCopyAddress = async () => {
    const address = property ? formatAddress(property) : "";

    if (!address) {
      setCopyMessage("No property address is available to copy.");
      return;
    }

    try {
      if (!navigator.clipboard?.writeText) {
        setCopyMessage(
          "Clipboard access is unavailable. Copy the address manually.",
        );
        return;
      }

      await navigator.clipboard.writeText(address);
      setCopyMessage("Address copied to clipboard.");
    } catch {
      setCopyMessage(
        "Unable to copy the address. Please copy it manually.",
      );
    }
  };

  const handleDeactivate = async () => {
    const confirmed = window.confirm(
      "Are you sure you want to deactivate this property?",
    );

    if (!confirmed) return;

    try {
      setIsDeactivating(true);
      setActionError("");
      setSuccessMessage("");

      const updatedProperty = await deactivateProperty(id);

      setProperty((current) => ({
        ...current,
        ...updatedProperty,
      }));

      setSuccessMessage("Property deactivated successfully.");
    } catch (requestError) {
      setActionError(getErrorMessage(requestError));
    } finally {
      setIsDeactivating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="mx-auto max-w-6xl space-y-8">
        <PageHeader
          eyebrow="Property Management"
          title="Property Details"
          description="Loading property information..."
        />
        <LoadingState message="Loading property..." />
      </div>
    );
  }

  if (error || !property) {
    return (
      <div className="mx-auto max-w-6xl space-y-8">
        <PageHeader
          eyebrow="Property Management"
          title="Property Details"
          description="Unable to load this property."
        />
        <ErrorState
          title="Unable to load property"
          message={error || "Property not found."}
          action={
            <div className="flex flex-wrap gap-3">
              <Button variant="secondary" onClick={loadProperty}>
                Try Again
              </Button>
              <Button
                variant="ghost"
                onClick={() => navigate("/properties")}
              >
                Back to Properties
              </Button>
            </div>
          }
        />
      </div>
    );
  }

  const address = formatAddress(property);
  const status = String(property.status || "ACTIVE").toUpperCase();
  const isInactive = ["INACTIVE", "DEACTIVATED"].includes(status);
  const units = Array.isArray(property.units) ? property.units : [];

  const availableUnits = units.filter(
    (unit) => String(unit.status || "").toUpperCase() === "AVAILABLE",
  ).length;

  const occupiedUnits = units.filter(
    (unit) => String(unit.status || "").toUpperCase() === "OCCUPIED",
  ).length;

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <PageHeader
        eyebrow={`Property ${property.id ? `#${property.id}` : "Overview"}`}
        title={property.name || "Untitled Property"}
        description="Review the property's information, operational status, and rental units."
        action={
          <div className="flex flex-wrap gap-3">
            <Button
              variant="secondary"
              onClick={() => navigate("/properties")}
            >
              Back
            </Button>
            <Button
              onClick={() => navigate(`/properties/${id}/edit`)}
              disabled={isInactive}
            >
              Edit Property
            </Button>
          </div>
        }
      />

      {successMessage && (
        <div
          role="status"
          className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800"
        >
          {successMessage}
        </div>
      )}

      {actionError && (
        <div
          role="alert"
          className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          {actionError}
        </div>
      )}

      {copyMessage && (
        <div
          role="status"
          className={[
            "rounded-xl border px-4 py-3 text-sm",
            copyMessage === "Address copied to clipboard."
              ? "border-emerald-200 bg-emerald-50 text-emerald-800"
              : "border-amber-200 bg-amber-50 text-amber-800",
          ].join(" ")}
        >
          {copyMessage}
        </div>
      )}

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Card className="p-5">
          <p className="text-sm font-medium text-slate-500">
            Property Status
          </p>
          <div className="mt-3">
            <Badge variant={getStatusVariant(status)}>
              {formatLabel(status)}
            </Badge>
          </div>
        </Card>

        <Card className="p-5">
          <p className="text-sm font-medium text-slate-500">
            Total Units
          </p>
          <p className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
            {units.length}
          </p>
          <p className="mt-1 text-xs text-slate-500">
            Units returned by the property API
          </p>
        </Card>

        <Card className="p-5">
          <p className="text-sm font-medium text-slate-500">
            Available Units
          </p>
          <p className="mt-2 text-3xl font-bold tracking-tight text-emerald-700">
            {availableUnits}
          </p>
          <p className="mt-1 text-xs text-slate-500">
            Currently marked available
          </p>
        </Card>

        <Card className="p-5">
          <p className="text-sm font-medium text-slate-500">
            Occupied Units
          </p>
          <p className="mt-2 text-3xl font-bold tracking-tight text-blue-700">
            {occupiedUnits}
          </p>
          <p className="mt-1 text-xs text-slate-500">
            Currently marked occupied
          </p>
        </Card>
      </section>

      <div className="grid items-start gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card className="overflow-hidden">
            <div className="border-b border-slate-100 bg-slate-50/70 px-6 py-5">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-medium text-slate-500">
                    Property Overview
                  </p>
                  <h2 className="mt-1 text-xl font-bold text-slate-950">
                    {property.name || "Untitled Property"}
                  </h2>
                </div>
                <Badge variant={getStatusVariant(status)}>
                  {formatLabel(status)}
                </Badge>
              </div>
            </div>

            <div className="grid gap-x-8 gap-y-7 p-6 sm:grid-cols-2">
              <DetailItem
                label="Property ID"
                value={property.id ? `#${property.id}` : "Not available"}
              />
              <DetailItem
                label="Property Type"
                value={formatLabel(property.property_type)}
              />
              <DetailItem
                label="City"
                value={property.city}
              />
              <DetailItem
                label="Province"
                value={property.province}
              />
              <DetailItem
                label="Postal Code"
                value={property.postal_code}
              />
              <DetailItem
                label="Date Created"
                value={formatDate(property.created_at)}
              />
              <DetailItem
                label="Last Updated"
                value={formatDate(property.updated_at)}
              />
              <DetailItem
                label="Current Status"
                value={formatLabel(status)}
              />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold text-slate-950">
                  Property Address
                </h2>
                <p className="mt-1 text-sm text-slate-500">
                  Registered location for this property.
                </p>
              </div>
              <Button
                variant="secondary"
                size="sm"
                onClick={handleCopyAddress}
                disabled={!address}
              >
                Copy Address
              </Button>
            </div>

            <div className="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="break-words text-sm leading-7 text-slate-800">
                {address || "No address has been added."}
              </p>
            </div>
          </Card>

          <Card className="p-6">
            <h2 className="text-lg font-semibold text-slate-950">
              Property Description
            </h2>
            <p className="mt-3 whitespace-pre-wrap break-words text-sm leading-7 text-slate-600">
              {property.description?.trim() ||
                "No description has been added for this property."}
            </p>
          </Card>
        </div>

        <div className="space-y-6">
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-slate-950">
              Property Actions
            </h2>
            <p className="mt-2 text-sm leading-6 text-slate-500">
              Manage this property using the available actions.
            </p>

            <div className="mt-6 space-y-3">
              <Button
                className="w-full"
                onClick={() => navigate(`/properties/${id}/edit`)}
                disabled={isInactive}
              >
                Edit Property
              </Button>

              <Button
                className="w-full"
                variant="secondary"
                onClick={() => navigate("/units")}
              >
                Browse All Units
              </Button>

              <Button
                className="w-full"
                variant="danger"
                onClick={handleDeactivate}
                disabled={isDeactivating || isInactive}
              >
                {isDeactivating
                  ? "Deactivating..."
                  : isInactive
                    ? "Property Inactive"
                    : "Deactivate Property"}
              </Button>
            </div>

            {isInactive && (
              <p className="mt-4 rounded-lg bg-slate-50 p-3 text-xs leading-5 text-slate-500">
                This property is inactive. Editing and deactivation
                actions are disabled.
              </p>
            )}
          </Card>

          <Card className="p-6">
            <h2 className="text-lg font-semibold text-slate-950">
              Unit Summary
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              Overview of the units associated with this property.
            </p>

            <div className="mt-5 space-y-4">
              <div className="flex items-center justify-between gap-4">
                <span className="text-sm text-slate-600">
                  Total units
                </span>
                <span className="font-semibold text-slate-950">
                  {units.length}
                </span>
              </div>

              <div className="flex items-center justify-between gap-4">
                <span className="text-sm text-slate-600">
                  Available
                </span>
                <span className="font-semibold text-emerald-700">
                  {availableUnits}
                </span>
              </div>

              <div className="flex items-center justify-between gap-4">
                <span className="text-sm text-slate-600">
                  Occupied
                </span>
                <span className="font-semibold text-blue-700">
                  {occupiedUnits}
                </span>
              </div>
            </div>

            <Button
              variant="secondary"
              className="mt-6 w-full"
              onClick={() => navigate("/units")}
            >
              View Units
            </Button>
          </Card>
        </div>
      </div>
    </div>
  );
}

export default PropertyDetails;
