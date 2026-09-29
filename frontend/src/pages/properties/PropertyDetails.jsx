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
  const normalizedStatus = status?.toLowerCase();

  if (
    normalizedStatus === "active" ||
    normalizedStatus === "available"
  ) {
    return "success";
  }

  if (
    normalizedStatus === "inactive" ||
    normalizedStatus === "deactivated"
  ) {
    return "danger";
  }

  return "default";
}

function formatAddress(property) {
  const parts = [
    property.address_line,
    property.city,
    property.province,
    property.postal_code,
  ].filter(Boolean);

  return parts.length > 0 ? parts.join(", ") : "—";
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
    // Data fetching is intentionally triggered when the page loads.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadProperty();
  }, [loadProperty]);

  const handleDeactivate = async () => {
    const confirmed = window.confirm(
      "Are you sure you want to deactivate this property?",
    );

    if (!confirmed) {
      return;
    }

    try {
      setIsDeactivating(true);
      setActionError("");
      setSuccessMessage("");

      const updatedProperty = await deactivateProperty(id);

      setProperty((current) => ({
        ...current,
        ...updatedProperty,
      }));

      setSuccessMessage(
        "Property has been deactivated successfully.",
      );
    } catch (requestError) {
      setActionError(getErrorMessage(requestError));
    } finally {
      setIsDeactivating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="mx-auto max-w-5xl space-y-8">
        <PageHeader
          eyebrow="Management"
          title="Property Details"
          description="Loading property information..."
        />

        <LoadingState message="Loading property..." />
      </div>
    );
  }

  if (error || !property) {
    return (
      <div className="mx-auto max-w-5xl space-y-8">
        <PageHeader
          eyebrow="Management"
          title="Property Details"
          description="Unable to load this property."
        />

        <ErrorState
          title="Unable to load property"
          message={error || "Property not found."}
          action={
            <div className="flex gap-3">
              <Button
                variant="secondary"
                onClick={loadProperty}
              >
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

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <PageHeader
        eyebrow="Management"
        title={property.name}
        description="View and manage property information."
        action={
          <div className="flex flex-wrap gap-3">
            <Button
              variant="secondary"
              onClick={() => navigate("/properties")}
            >
              Back
            </Button>

            <Button
              onClick={() =>
                navigate(`/properties/${id}/edit`)
              }
            >
              Edit Property
            </Button>
          </div>
        }
      />

      {successMessage && (
        <div
          role="status"
          className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700"
        >
          {successMessage}
        </div>
      )}

      {actionError && (
        <div
          role="alert"
          className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          {actionError}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="p-6 lg:col-span-2">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm font-medium text-slate-500">
                Property
              </p>

              <h2 className="mt-1 text-2xl font-bold text-slate-950">
                {property.name}
              </h2>
            </div>

            <Badge
              variant={getStatusVariant(property.status)}
            >
              {property.status || "Active"}
            </Badge>
          </div>

          <div className="mt-8 grid gap-6 sm:grid-cols-2">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Property Type
              </p>

              <p className="mt-1 text-sm font-medium text-slate-900">
                {property.property_type || "—"}
              </p>
            </div>

            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Status
              </p>

              <p className="mt-1 text-sm font-medium text-slate-900">
                {property.status || "Active"}
              </p>
            </div>

            <div className="sm:col-span-2">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Address
              </p>

              <p className="mt-1 text-sm font-medium text-slate-900">
                {formatAddress(property)}
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-lg font-semibold text-slate-950">
            Property Actions
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            Manage the current property.
          </p>

          <div className="mt-6 space-y-3">
            <Button
              className="w-full"
              variant="secondary"
              onClick={() =>
                navigate(`/properties/${id}/edit`)
              }
            >
              Edit Property
            </Button>

            <Button
              className="w-full"
              variant="danger"
              onClick={handleDeactivate}
              disabled={
                isDeactivating ||
                property.status?.toLowerCase() ===
                  "inactive" ||
                property.status?.toLowerCase() ===
                  "deactivated"
              }
            >
              {isDeactivating
                ? "Deactivating..."
                : "Deactivate Property"}
            </Button>
          </div>
        </Card>

        <Card className="p-6 lg:col-span-3">
          <h2 className="text-lg font-semibold text-slate-950">
            Description
          </h2>

          <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-600">
            {property.description ||
              "No description has been added for this property."}
          </p>
        </Card>
      </div>
    </div>
  );
}

export default PropertyDetails;