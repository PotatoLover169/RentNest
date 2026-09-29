import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getProperties } from "../../api/properties";
import { getUnits } from "../../api/units";
import {
  Button,
  Card,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from "../../components/ui";
import { getPagination, getResults } from "../../utils/api";

function formatStatus(status) {
  if (!status) {
    return "Available";
  }

  return status
    .toLowerCase()
    .split("_")
    .map(
      (word) =>
        word.charAt(0).toUpperCase() + word.slice(1),
    )
    .join(" ");
}

function formatUnitType(unitType) {
  if (!unitType) {
    return "—";
  }

  return unitType
    .toLowerCase()
    .split("_")
    .map(
      (word) =>
        word.charAt(0).toUpperCase() + word.slice(1),
    )
    .join(" ");
}

function formatRent(rent) {
  if (rent == null) {
    return "—";
  }

  return `₱${Number(rent).toLocaleString("en-PH", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

function getStatusVariant(status) {
  switch (status?.toLowerCase()) {
    case "available":
      return "bg-emerald-100 text-emerald-700";

    case "occupied":
      return "bg-blue-100 text-blue-700";

    case "maintenance":
      return "bg-amber-100 text-amber-700";

    case "inactive":
      return "bg-slate-100 text-slate-600";

    default:
      return "bg-slate-100 text-slate-700";
  }
}

function Units() {
  const navigate = useNavigate();

  const [units, setUnits] = useState([]);
  const [properties, setProperties] = useState([]);
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const loadUnits = useCallback(async () => {
    try {
      setIsLoading(true);
      setError("");

      const [unitsData, propertiesData] =
        await Promise.all([
          getUnits(),
          getProperties(),
        ]);

      setUnits(getResults(unitsData));
      setProperties(getResults(propertiesData));
      setPagination(getPagination(unitsData));
    } catch (requestError) {
      setError(
        requestError?.response?.data?.message ||
          requestError?.response?.data?.detail ||
          "Unable to load units.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // Data fetching is intentionally triggered on mount.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadUnits();
  }, [loadUnits]);

  const getPropertyName = (propertyId) => {
    const property = properties.find(
      (item) => item.id === propertyId,
    );

    return property?.name || `Property #${propertyId}`;
  };

  return (
    <div className="mx-auto max-w-7xl space-y-8">
      <PageHeader
        eyebrow="Management"
        title="Units"
        description="Manage rental units across your properties."
        action={
          <Button
            onClick={() => navigate("/units/new")}
          >
            Add Unit
          </Button>
        }
      />

      {isLoading && (
        <LoadingState message="Loading units..." />
      )}

      {!isLoading && error && (
        <ErrorState
          title="Unable to load units"
          message={error}
          action={
            <Button
              variant="secondary"
              onClick={loadUnits}
            >
              Try Again
            </Button>
          }
        />
      )}

      {!isLoading && !error && units.length === 0 && (
        <EmptyState
          title="No units yet"
          description="Create your first rental unit to start managing units within your properties."
          action={
            <Button
              onClick={() => navigate("/units/new")}
            >
              Add Unit
            </Button>
          }
        />
      )}

      {!isLoading && !error && units.length > 0 && (
        <Card className="overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
            <div>
              <h2 className="font-semibold text-slate-950">
                Unit List
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                {pagination.count}{" "}
                {pagination.count === 1
                  ? "unit"
                  : "units"}
              </p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Unit
                  </th>

                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Property
                  </th>

                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Type
                  </th>

                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Rent
                  </th>

                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Status
                  </th>

                  <th className="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Actions
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-200 bg-white">
                {units.map((unit) => (
                  <tr
                    key={unit.id}
                    className="transition hover:bg-slate-50"
                  >
                    <td className="whitespace-nowrap px-6 py-4">
                      <p className="font-medium text-slate-900">
                        Unit {unit.unit_number}
                      </p>

                      <p className="mt-1 text-xs text-slate-400">
                        {unit.bedrooms ?? 0}{" "}
                        {unit.bedrooms === 1
                          ? "bedroom"
                          : "bedrooms"}
                        {" · "}
                        {unit.bathrooms ?? 0}{" "}
                        {Number(unit.bathrooms) === 1
                          ? "bathroom"
                          : "bathrooms"}
                      </p>
                    </td>

                    <td className="px-6 py-4 text-sm text-slate-600">
                      {getPropertyName(unit.property)}
                    </td>

                    <td className="px-6 py-4 text-sm text-slate-600">
                      {formatUnitType(unit.unit_type)}
                    </td>

                    <td className="whitespace-nowrap px-6 py-4 text-sm font-medium text-slate-900">
                      {formatRent(unit.monthly_rent)}
                    </td>

                    <td className="px-6 py-4">
                      <span
                        className={[
                          "inline-flex rounded-full px-3 py-1 text-xs font-semibold",
                          getStatusVariant(unit.status),
                        ].join(" ")}
                      >
                        {formatStatus(unit.status)}
                      </span>
                    </td>

                    <td className="px-6 py-4 text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() =>
                          navigate(`/units/${unit.id}`)
                        }
                      >
                        View
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}

export default Units;