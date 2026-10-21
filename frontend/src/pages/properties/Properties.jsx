
import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getProperties } from "../../api/properties";
import {
  Button,
  Card,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from "../../components/ui";
import { getPagination, getResults } from "../../utils/api";

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

function Properties() {
  const navigate = useNavigate();

  const [properties, setProperties] = useState([]);
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null,
  });
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortBy, setSortBy] = useState("name-asc");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const loadProperties = useCallback(async () => {
    try {
      setIsLoading(true);
      setError("");

      const data = await getProperties();

      setProperties(getResults(data));
      setPagination(getPagination(data));
    } catch (requestError) {
      setError(
        requestError?.response?.data?.message ||
          requestError?.response?.data?.detail ||
          "Unable to load properties.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // Fetch the property list when the page mounts.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadProperties();
  }, [loadProperties]);

  const filteredProperties = useMemo(() => {
    const query = searchTerm.trim().toLowerCase();

    const filtered = properties.filter((property) => {
      const searchableValues = [
        property.name,
        property.address_line,
        property.city,
        property.province,
        property.postal_code,
      ];

      const matchesSearch =
        !query ||
        searchableValues.some(
          (value) =>
            typeof value === "string" &&
            value.toLowerCase().includes(query),
        );

      const normalizedStatus = (
        property.status || "active"
      ).toLowerCase();

      const matchesStatus =
        statusFilter === "all" ||
        normalizedStatus === statusFilter;

      return matchesSearch && matchesStatus;
    });

    return [...filtered].sort((a, b) => {
      const nameA = (a.name || "").toLowerCase();
      const nameB = (b.name || "").toLowerCase();
      const statusA = (a.status || "active").toLowerCase();
      const statusB = (b.status || "active").toLowerCase();

      switch (sortBy) {
        case "name-desc":
          return nameB.localeCompare(nameA);

        case "status-asc":
          return (
            statusA.localeCompare(statusB) ||
            nameA.localeCompare(nameB)
          );

        case "status-desc":
          return (
            statusB.localeCompare(statusA) ||
            nameA.localeCompare(nameB)
          );

        case "name-asc":
        default:
          return nameA.localeCompare(nameB);
      }
    });
  }, [properties, searchTerm, statusFilter, sortBy]);

  const clearFilters = () => {
    setSearchTerm("");
    setStatusFilter("all");
    setSortBy("name-asc");
  };

  return (
    <div className="mx-auto max-w-7xl space-y-8">
      <PageHeader
        eyebrow="Management"
        title="Properties"
        description="Manage your rental properties and view their current information."
        action={
          <Button onClick={() => navigate("/properties/new")}>
            Add Property
          </Button>
        }
      />

      {isLoading && (
        <LoadingState message="Loading properties..." />
      )}

      {!isLoading && error && (
        <ErrorState
          title="Unable to load properties"
          message={error}
          action={
            <Button
              variant="secondary"
              onClick={loadProperties}
            >
              Try Again
            </Button>
          }
        />
      )}

      {!isLoading && !error && properties.length === 0 && (
        <EmptyState
          title="No properties yet"
          description="Create your first rental property to start managing your portfolio."
          action={
            <Button onClick={() => navigate("/properties/new")}>
              Add Property
            </Button>
          }
        />
      )}

      {!isLoading && !error && properties.length > 0 && (
        <Card className="overflow-hidden">
          <div className="space-y-4 border-b border-slate-200 px-6 py-5">
            <div>
              <h2 className="font-semibold text-slate-950">
                Property List
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Showing {filteredProperties.length} of{" "}
                {properties.length} loaded{" "}
                {properties.length === 1
                  ? "property"
                  : "properties"}
                {pagination.count > properties.length
                  ? ` (${pagination.count} total on the server)`
                  : ""}
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <label
                  htmlFor="property-search"
                  className="mb-1.5 block text-sm font-medium text-slate-700"
                >
                  Search properties
                </label>

                <input
                  id="property-search"
                  type="search"
                  value={searchTerm}
                  onChange={(event) =>
                    setSearchTerm(event.target.value)
                  }
                  placeholder="Name, city, or address..."
                  className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />
              </div>

              <div>
                <label
                  htmlFor="property-status-filter"
                  className="mb-1.5 block text-sm font-medium text-slate-700"
                >
                  Filter by status
                </label>

                <select
                  id="property-status-filter"
                  value={statusFilter}
                  onChange={(event) =>
                    setStatusFilter(event.target.value)
                  }
                  className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                >
                  <option value="all">All statuses</option>
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                  <option value="deactivated">Deactivated</option>
                </select>
              </div>

              <div>
                <label
                  htmlFor="property-sort"
                  className="mb-1.5 block text-sm font-medium text-slate-700"
                >
                  Sort properties
                </label>

                <select
                  id="property-sort"
                  value={sortBy}
                  onChange={(event) =>
                    setSortBy(event.target.value)
                  }
                  className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                >
                  <option value="name-asc">
                    Name: A to Z
                  </option>
                  <option value="name-desc">
                    Name: Z to A
                  </option>
                  <option value="status-asc">
                    Status: A to Z
                  </option>
                  <option value="status-desc">
                    Status: Z to A
                  </option>
                </select>
              </div>
            </div>

            {(searchTerm || statusFilter !== "all" || sortBy !== "name-asc") && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearFilters}
              >
                Reset search, filters, and sorting
              </Button>
            )}
          </div>

          {filteredProperties.length === 0 ? (
            <div className="px-6 py-12 text-center">
              <h3 className="font-semibold text-slate-900">
                No matching properties
              </h3>

              <p className="mt-2 text-sm text-slate-500">
                Try a different search term or status.
              </p>

              <Button
                variant="secondary"
                className="mt-4"
                onClick={clearFilters}
              >
                Reset
              </Button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Property
                    </th>

                    <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                      Address
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
                  {filteredProperties.map((property) => {
                    const statusVariant = getStatusVariant(
                      property.status,
                    );

                    return (
                      <tr
                        key={property.id}
                        className="transition hover:bg-slate-50"
                      >
                        <td className="whitespace-nowrap px-6 py-4">
                          <p className="font-medium text-slate-900">
                            {property.name}
                          </p>
                        </td>

                        <td className="px-6 py-4 text-sm text-slate-500">
                          {formatAddress(property)}
                        </td>

                        <td className="px-6 py-4">
                          <span
                            className={[
                              "inline-flex rounded-full px-3 py-1 text-xs font-semibold",
                              statusVariant === "success"
                                ? "bg-emerald-100 text-emerald-700"
                                : statusVariant === "danger"
                                  ? "bg-red-100 text-red-700"
                                  : "bg-slate-100 text-slate-700",
                            ].join(" ")}
                          >
                            {property.status || "Active"}
                          </span>
                        </td>

                        <td className="px-6 py-4 text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() =>
                              navigate(
                                `/properties/${property.id}`,
                              )
                            }
                          >
                            View
                          </Button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </Card>
      )}
    </div>
  );
}

export default Properties;
