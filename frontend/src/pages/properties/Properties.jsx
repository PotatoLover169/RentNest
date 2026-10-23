
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
  const normalizedStatus = (status || "active").trim().toLowerCase();

  switch (normalizedStatus) {
    case "active":
      return "active";
    case "available":
      return "available";
    case "inactive":
    case "deactivated":
      return "inactive";
    default:
      return "default";
  }
}

function formatStatus(status) {
  const normalizedStatus = (status || "active").trim().toLowerCase();

  return normalizedStatus
    ? normalizedStatus.charAt(0).toUpperCase() + normalizedStatus.slice(1)
    : "Active";
}

function formatAddress(property) {
  const parts = [
    property.address_line,
    property.city,
    property.province,
    property.postal_code,
  ].filter(Boolean);

  return parts.length ? parts.join(", ") : "Address not provided";
}

function formatPropertyId(id) {
  return id === null || id === undefined ? "—" : `#${id}`;
}

const statusClasses = {
  active: "bg-emerald-50 text-emerald-700 ring-1 ring-inset ring-emerald-600/20",
  available: "bg-blue-50 text-blue-700 ring-1 ring-inset ring-blue-600/20",
  inactive: "bg-red-50 text-red-700 ring-1 ring-inset ring-red-600/20",
  default: "bg-slate-100 text-slate-700 ring-1 ring-inset ring-slate-500/20",
};

function StatusBadge({ status }) {
  const variant = getStatusVariant(status);

  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${statusClasses[variant]}`}
    >
      <span
        className="mr-2 h-1.5 w-1.5 rounded-full bg-current"
        aria-hidden="true"
      />
      {formatStatus(status)}
    </span>
  );
}

function PropertyCard({ property, onView }) {
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:border-blue-200 hover:shadow-md">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="break-words font-semibold text-slate-950">
            {property.name || "Untitled property"}
          </h3>
          <p className="mt-1 text-xs font-medium text-slate-500">
            Property ID: {formatPropertyId(property.id)}
          </p>
        </div>
        <div className="shrink-0">
          <StatusBadge status={property.status} />
        </div>
      </div>

      <div className="mt-4 border-t border-slate-100 pt-3">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
          Address
        </p>
        <p className="mt-1 break-words text-sm leading-6 text-slate-600">
          {formatAddress(property)}
        </p>
      </div>

      <div className="mt-4 flex justify-end">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => onView(property.id)}
          aria-label={`View ${property.name || "property"} details`}
        >
          View Details
        </Button>
      </div>
    </article>
  );
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

  const summary = useMemo(() => {
    const active = properties.filter((property) => {
      const status = (property.status || "active").trim().toLowerCase();
      return status === "active" || status === "available";
    }).length;

    const inactive = properties.filter((property) => {
      const status = (property.status || "active").trim().toLowerCase();
      return status === "inactive" || status === "deactivated";
    }).length;

    return {
      total: pagination.count || properties.length,
      active,
      inactive,
    };
  }, [properties, pagination.count]);

  const filteredProperties = useMemo(() => {
    const query = searchTerm.trim().toLowerCase();

    const filtered = properties.filter((property) => {
      const searchableValues = [
        property.name,
        property.address_line,
        property.city,
        property.province,
        property.postal_code,
        property.id === null || property.id === undefined
          ? ""
          : String(property.id),
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
      ).trim().toLowerCase();

      return (
        matchesSearch &&
        (statusFilter === "all" || normalizedStatus === statusFilter)
      );
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
          return statusA.localeCompare(statusB) || nameA.localeCompare(nameB);
        case "status-desc":
          return statusB.localeCompare(statusA) || nameA.localeCompare(nameB);
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

  const hasActiveFilters =
    searchTerm.trim() !== "" ||
    statusFilter !== "all" ||
    sortBy !== "name-asc";

  const viewProperty = (propertyId) => {
    navigate(`/properties/${propertyId}`);
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

      {isLoading && <LoadingState message="Loading properties..." />}

      {!isLoading && error && (
        <ErrorState
          title="Unable to load properties"
          message={error}
          action={
            <Button variant="secondary" onClick={loadProperties}>
              Try Again
            </Button>
          }
        />
      )}

      {!isLoading && !error && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <Card className="p-5">
              <p className="text-sm font-medium text-slate-500">
                Total Properties
              </p>
              <p className="mt-2 text-3xl font-bold text-slate-950">
                {summary.total}
              </p>
            </Card>
            <Card className="p-5">
              <p className="text-sm font-medium text-slate-500">
                Active Properties
              </p>
              <p className="mt-2 text-3xl font-bold text-emerald-600">
                {summary.active}
              </p>
            </Card>
            <Card className="p-5">
              <p className="text-sm font-medium text-slate-500">
                Inactive Properties
              </p>
              <p className="mt-2 text-3xl font-bold text-slate-600">
                {summary.inactive}
              </p>
            </Card>
          </div>

          {properties.length === 0 ? (
            <EmptyState
              title="Your property portfolio is empty"
              description="You haven't added any rental properties yet. Create your first property to start managing units, tenants, and rental activity."
              action={
                <Button onClick={() => navigate("/properties/new")}>
                  Add Your First Property
                </Button>
              }
            />
          ) : (
            <Card className="overflow-hidden">
              <div className="space-y-4 border-b border-slate-200 px-4 py-5 sm:px-6">
                <div>
                  <h2 className="font-semibold text-slate-950">Property List</h2>
                  <p className="mt-1 text-sm text-slate-500">
                    Showing {filteredProperties.length} of {properties.length}{" "}
                    loaded {properties.length === 1 ? "property" : "properties"}
                    {pagination.count > properties.length
                      ? ` (${pagination.count} total on the server)`
                      : ""}
                  </p>
                </div>

                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
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
                      onChange={(event) => setSearchTerm(event.target.value)}
                      placeholder="Name, ID, city, or address..."
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
                      onChange={(event) => setStatusFilter(event.target.value)}
                      className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                    >
                      <option value="all">All statuses</option>
                      <option value="active">Active</option>
                      <option value="available">Available</option>
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
                      onChange={(event) => setSortBy(event.target.value)}
                      className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                    >
                      <option value="name-asc">Name: A to Z</option>
                      <option value="name-desc">Name: Z to A</option>
                      <option value="status-asc">Status: A to Z</option>
                      <option value="status-desc">Status: Z to A</option>
                    </select>
                  </div>
                </div>

                {hasActiveFilters && (
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <p className="text-sm text-slate-500">
                      Search and filter settings are applied.
                    </p>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={clearFilters}
                    >
                      Clear Filters
                    </Button>
                  </div>
                )}
              </div>

              {filteredProperties.length === 0 ? (
                <div className="px-6 py-12 text-center">
                  <h3 className="font-semibold text-slate-900">
                    No matching properties found
                  </h3>
                  <p className="mx-auto mt-2 max-w-md text-sm text-slate-500">
                    {searchTerm.trim()
                      ? `No properties match "${searchTerm.trim()}". Try a different keyword or adjust your status filter.`
                      : "No properties match the selected status. Try choosing a different status."}
                  </p>
                  <Button
                    variant="secondary"
                    className="mt-4"
                    onClick={clearFilters}
                  >
                    Clear Search and Filters
                  </Button>
                </div>
              ) : (
                <>
                  <div className="grid gap-3 p-4 sm:grid-cols-2 lg:hidden">
                    {filteredProperties.map((property) => (
                      <PropertyCard
                        key={property.id}
                        property={property}
                        onView={viewProperty}
                      />
                    ))}
                  </div>

                  <div className="hidden overflow-x-auto lg:block">
                    <table className="min-w-full divide-y divide-slate-200 text-sm">
                      <thead className="bg-slate-50">
                        <tr>
                          <th scope="col" className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                            Property
                          </th>
                          <th scope="col" className="whitespace-nowrap px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                            Property ID
                          </th>
                          <th scope="col" className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                            Address
                          </th>
                          <th scope="col" className="whitespace-nowrap px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                            Status
                          </th>
                          <th scope="col" className="whitespace-nowrap px-6 py-4 text-right text-xs font-semibold uppercase tracking-wider text-slate-500">
                            Actions
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 bg-white">
                        {filteredProperties.map((property) => (
                          <tr
                            key={property.id}
                            className="transition-colors hover:bg-blue-50/40 focus-within:bg-blue-50/40"
                          >
                            <td className="min-w-48 px-6 py-5">
                              <p className="font-semibold text-slate-900">
                                {property.name || "Untitled property"}
                              </p>
                              <p className="mt-1 text-xs text-slate-400">
                                {formatPropertyId(property.id)}
                              </p>
                            </td>
                            <td className="whitespace-nowrap px-6 py-5 font-medium tabular-nums text-slate-500">
                              {formatPropertyId(property.id)}
                            </td>
                            <td className="min-w-64 px-6 py-5 leading-6 text-slate-600">
                              {formatAddress(property)}
                            </td>
                            <td className="whitespace-nowrap px-6 py-5">
                              <StatusBadge status={property.status} />
                            </td>
                            <td className="whitespace-nowrap px-6 py-5 text-right">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => viewProperty(property.id)}
                                aria-label={`View ${property.name || "property"} details`}
                              >
                                View Details
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </Card>
          )}
        </>
      )}
    </div>
  );
}

export default Properties;
