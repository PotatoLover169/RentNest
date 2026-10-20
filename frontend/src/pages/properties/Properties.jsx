
import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
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
          "Unable to load properties.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // Fetch properties when the page is mounted.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadProperties();
  }, [loadProperties]);

  const formatAddress = (property) => {
    const parts = [
      property.address_line,
      property.city,
      property.province,
      property.postal_code,
    ].filter(Boolean);

    return parts.length ? parts.join(", ") : "—";
  };

  const getStatusVariant = (status) => {
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
  };

  const filteredProperties = useMemo(() => {
    const query = searchTerm.trim().toLowerCase();

    return properties.filter((property) => {
      const normalizedStatus =
        property.status?.toLowerCase() || "active";

      const matchesSearch =
        !query ||
        [
          property.name,
          property.address_line,
          property.city,
          property.province,
          property.postal_code,
        ].some(
          (value) =>
            typeof value === "string" &&
            value.toLowerCase().includes(query),
        );

      const matchesStatus =
        statusFilter === "all" ||
        (statusFilter === "active" &&
          ["active", "available"].includes(normalizedStatus)) ||
        (statusFilter === "inactive" &&
          ["inactive", "deactivated"].includes(normalizedStatus));

      return matchesSearch && matchesStatus;
    });
  }, [properties, searchTerm, statusFilter]);

  const resetFilters = () => {
    setSearchTerm("");
    setStatusFilter("all");
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
          <div className="flex flex-col gap-4 border-b border-slate-200 px-6 py-5">
            <div>
              <h2 className="font-semibold text-slate-950">
                Property List
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Showing {filteredProperties.length} of{" "}
                {properties.length} loaded properties
                {pagination.count > properties.length
                  ? ` (${pagination.count} total)`
                  : ""}
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <label
                  htmlFor="property-search"
                  className="mb-2 block text-sm font-medium text-slate-700"
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
                  className="mb-2 block text-sm font-medium text-slate-700"
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
                </select>
              </div>
            </div>
          </div>

          {filteredProperties.length === 0 ? (
            <div className="px-6 py-12 text-center">
              <h3 className="font-semibold text-slate-900">
                No matching properties
              </h3>

              <p className="mt-2 text-sm text-slate-500">
                Try changing your search or status filter.
              </p>

              <Button
                variant="secondary"
                className="mt-4"
                onClick={resetFilters}
              >
                Clear Filters
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
