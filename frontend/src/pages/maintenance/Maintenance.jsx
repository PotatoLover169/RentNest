
import { useEffect, useMemo, useState } from "react";
import { getMaintenanceRequests } from "../../api/maintenance";

function formatLabel(value, fallback = "—") {
  if (!value) return fallback;

  return String(value)
    .toLowerCase()
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function getStatusStyle(status) {
  const styles = {
    PENDING: "bg-amber-50 text-amber-700 ring-amber-600/20",
    IN_PROGRESS: "bg-blue-50 text-blue-700 ring-blue-600/20",
    COMPLETED: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
    CANCELLED: "bg-slate-100 text-slate-600 ring-slate-500/20",
    OPEN: "bg-amber-50 text-amber-700 ring-amber-600/20",
    APPROVED: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
    REJECTED: "bg-red-50 text-red-700 ring-red-600/20",
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
    NORMAL: "bg-blue-50 text-blue-700",
    HIGH: "bg-orange-50 text-orange-700",
    URGENT: "bg-red-50 text-red-700",
    CRITICAL: "bg-red-100 text-red-800",
  };

  return styles[priority] || "bg-slate-100 text-slate-600";
}

function getUnitLabel(request) {
  return (
    request.unit_number ||
    request.unit?.unit_number ||
    request.unit?.name ||
    request.unit?.id ||
    "—"
  );
}

function getRequestTitle(request) {
  return (
    request.title ||
    request.description ||
    `Request #${request.id}`
  );
}

function getRequestDate(request) {
  const value =
    request.created_at ||
    request.requested_at ||
    request.date_created;

  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "—";

  return date.toLocaleDateString("en-PH", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function SummaryCard({ label, value, description }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-medium text-slate-500">
        {label}
      </p>

      <p className="mt-3 text-3xl font-bold tracking-tight text-slate-950">
        {value}
      </p>

      <p className="mt-1 text-xs text-slate-400">
        {description}
      </p>
    </div>
  );
}

function Maintenance() {
  const [requests, setRequests] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [priorityFilter, setPriorityFilter] = useState("ALL");
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    let isActive = true;

    const loadRequests = async () => {
      try {
        setIsLoading(true);
        setError("");

        const data = await getMaintenanceRequests();

        const results = Array.isArray(data)
          ? data
          : Array.isArray(data?.results)
            ? data.results
            : [];

        if (isActive) {
          setRequests(results);
        }
      } catch (requestError) {
        if (isActive) {
          setError(
            requestError?.response?.data?.message ||
              requestError?.response?.data?.detail ||
              "Unable to load maintenance requests. Please try again."
          );
        }
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    };

    loadRequests();

    return () => {
      isActive = false;
    };
  }, [refreshKey]);

  const summary = useMemo(() => {
    return {
      total: requests.length,
      pending: requests.filter(
        (request) => request.status === "PENDING"
      ).length,
      inProgress: requests.filter(
        (request) => request.status === "IN_PROGRESS"
      ).length,
      completed: requests.filter(
        (request) => request.status === "COMPLETED"
      ).length,
    };
  }, [requests]);

  const filteredRequests = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase();

    return requests.filter((request) => {
      const matchesSearch =
        !normalizedSearch ||
        [
          request.title,
          request.description,
          request.unit_number,
          request.unit?.unit_number,
          request.unit?.name,
          request.id,
        ].some((value) =>
          String(value ?? "")
            .toLowerCase()
            .includes(normalizedSearch)
        );

      const matchesStatus =
        statusFilter === "ALL" ||
        request.status === statusFilter;

      const matchesPriority =
        priorityFilter === "ALL" ||
        request.priority === priorityFilter;

      return (
        matchesSearch &&
        matchesStatus &&
        matchesPriority
      );
    });
  }, [requests, search, statusFilter, priorityFilter]);

  const priorities = useMemo(() => {
    return [
      ...new Set(
        requests
          .map((request) => request.priority)
          .filter(Boolean)
      ),
    ];
  }, [requests]);

  const handleRefresh = () => {
    setRefreshKey((current) => current + 1);
  };

  return (
    <div className="mx-auto max-w-7xl space-y-8">
      <section className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wider text-slate-500">
            Property Operations
          </p>

          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
            Maintenance
          </h1>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
            Monitor maintenance requests, review their priority,
            and track progress across your rental properties.
          </p>
        </div>

        <button
          type="button"
          onClick={handleRefresh}
          disabled={isLoading}
          className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`}
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M20 7v5h-5M4 17v-5h5"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M5.6 9a7 7 0 0 1 11.8-2L20 12M4 12l2.6 5a7 7 0 0 0 11.8-2"
            />
          </svg>
          Refresh
        </button>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <SummaryCard
          label="Total Requests"
          value={summary.total}
          description="Requests available to your account"
        />

        <SummaryCard
          label="Pending"
          value={summary.pending}
          description="Awaiting maintenance action"
        />

        <SummaryCard
          label="In Progress"
          value={summary.inProgress}
          description="Currently being addressed"
        />

        <SummaryCard
          label="Completed"
          value={summary.completed}
          description="Successfully resolved"
        />
      </section>

      <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="flex flex-col gap-4 border-b border-slate-100 p-5 sm:p-6">
          <div>
            <h2 className="text-lg font-semibold text-slate-950">
              Maintenance Requests
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Search and filter your maintenance records.
            </p>
          </div>

          <div className="grid gap-3 md:grid-cols-3">
            <div className="relative">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400"
                aria-hidden="true"
              >
                <circle cx="11" cy="11" r="7" />
                <path
                  strokeLinecap="round"
                  d="m20 20-4-4"
                />
              </svg>

              <input
                type="search"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search requests..."
                aria-label="Search maintenance requests"
                className="w-full rounded-xl border border-slate-200 bg-white py-2.5 pl-10 pr-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />
            </div>

            <select
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value)}
              aria-label="Filter by status"
              className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            >
              <option value="ALL">All statuses</option>
              <option value="PENDING">Pending</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="COMPLETED">Completed</option>
              <option value="CANCELLED">Cancelled</option>
            </select>

            <select
              value={priorityFilter}
              onChange={(event) => setPriorityFilter(event.target.value)}
              aria-label="Filter by priority"
              className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            >
              <option value="ALL">All priorities</option>
              {priorities.map((priority) => (
                <option key={priority} value={priority}>
                  {formatLabel(priority)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {isLoading && (
          <div className="flex items-center justify-center px-6 py-16">
            <div className="text-center">
              <div className="mx-auto h-9 w-9 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600" />

              <p className="mt-4 text-sm text-slate-500">
                Loading maintenance requests...
              </p>
            </div>
          </div>
        )}

        {!isLoading && error && (
          <div className="m-5 rounded-xl border border-red-200 bg-red-50 p-5 sm:m-6">
            <h3 className="font-semibold text-red-900">
              Unable to load maintenance requests
            </h3>

            <p className="mt-2 text-sm text-red-700">
              {error}
            </p>

            <button
              type="button"
              onClick={handleRefresh}
              className="mt-4 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-red-700"
            >
              Try Again
            </button>
          </div>
        )}

        {!isLoading && !error && requests.length === 0 && (
          <div className="px-6 py-16 text-center">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.6"
                className="h-7 w-7 text-slate-500"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M12 8v4m0 4h.01M4.9 19h14.2c1.2 0 1.9-1.3 1.3-2.3L13.3 4.4c-.6-1-2-.9-2.6 0L3.6 16.7C3 17.7 3.7 19 4.9 19Z"
                />
              </svg>
            </div>

            <h3 className="mt-4 text-base font-semibold text-slate-900">
              No maintenance requests yet
            </h3>

            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
              Maintenance requests associated with your account
              will appear here when available.
            </p>
          </div>
        )}

        {!isLoading &&
          !error &&
          requests.length > 0 &&
          filteredRequests.length === 0 && (
            <div className="px-6 py-14 text-center">
              <h3 className="font-semibold text-slate-900">
                No matching requests
              </h3>

              <p className="mt-2 text-sm text-slate-500">
                Try adjusting your search or filters.
              </p>

              <button
                type="button"
                onClick={() => {
                  setSearch("");
                  setStatusFilter("ALL");
                  setPriorityFilter("ALL");
                }}
                className="mt-4 text-sm font-semibold text-blue-600 hover:text-blue-700"
              >
                Clear filters
              </button>
            </div>
          )}

        {!isLoading &&
          !error &&
          filteredRequests.length > 0 && (
            <>
              <div className="flex items-center justify-between px-5 py-3 sm:px-6">
                <p className="text-xs text-slate-500">
                  Showing{" "}
                  <span className="font-semibold text-slate-700">
                    {filteredRequests.length}
                  </span>{" "}
                  of{" "}
                  <span className="font-semibold text-slate-700">
                    {requests.length}
                  </span>{" "}
                  requests
                </p>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-100">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="whitespace-nowrap px-5 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-slate-500 sm:px-6">
                        Request
                      </th>

                      <th className="whitespace-nowrap px-5 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                        Unit
                      </th>

                      <th className="whitespace-nowrap px-5 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                        Priority
                      </th>

                      <th className="whitespace-nowrap px-5 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                        Status
                      </th>

                      <th className="whitespace-nowrap px-5 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                        Date Submitted
                      </th>
                    </tr>
                  </thead>

                  <tbody className="divide-y divide-slate-100">
                    {filteredRequests.map((request) => (
                      <tr
                        key={request.id}
                        className="transition hover:bg-slate-50/80"
                      >
                        <td className="max-w-sm px-5 py-4 sm:px-6">
                          <p className="truncate text-sm font-semibold text-slate-900">
                            {getRequestTitle(request)}
                          </p>

                          {request.title && request.description && (
                            <p className="mt-1 line-clamp-2 text-xs leading-5 text-slate-500">
                              {request.description}
                            </p>
                          )}

                          <p className="mt-1 text-xs text-slate-400">
                            Request #{request.id}
                          </p>
                        </td>

                        <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-600">
                          {getUnitLabel(request)}
                        </td>

                        <td className="whitespace-nowrap px-5 py-4">
                          <span
                            className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${getPriorityStyle(
                              request.priority
                            )}`}
                          >
                            {formatLabel(request.priority, "Normal")}
                          </span>
                        </td>

                        <td className="whitespace-nowrap px-5 py-4">
                          <span
                            className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset ${getStatusStyle(
                              request.status
                            )}`}
                          >
                            {formatLabel(request.status, "Pending")}
                          </span>
                        </td>

                        <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-500">
                          {getRequestDate(request)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
      </section>
    </div>
  );
}

export default Maintenance;