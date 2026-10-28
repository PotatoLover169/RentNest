
import { useCallback, useEffect, useMemo, useState } from "react";

import { getTenancies } from "../../api/tenancies";

const STATUS_OPTIONS = [
  "ALL",
  "PENDING",
  "ACTIVE",
  "ENDED",
  "CANCELLED",
];

function normalizeStatus(status) {
  return String(status || "PENDING").toUpperCase();
}

function formatStatus(status) {
  return normalizeStatus(status)
    .toLowerCase()
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function getStatusStyles(status) {
  const styles = {
    ACTIVE: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
    PENDING: "bg-amber-50 text-amber-700 ring-amber-600/20",
    ENDED: "bg-slate-100 text-slate-600 ring-slate-500/20",
    CANCELLED: "bg-red-50 text-red-700 ring-red-600/20",
  };

  return (
    styles[normalizeStatus(status)] ||
    "bg-slate-100 text-slate-600 ring-slate-500/20"
  );
}

function formatCurrency(amount) {
  if (amount == null || amount === "") {
    return "—";
  }

  const numericAmount = Number(amount);

  if (!Number.isFinite(numericAmount)) {
    return "—";
  }

  return new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
    maximumFractionDigits: 2,
  }).format(numericAmount);
}

function formatDate(value) {
  if (!value) {
    return "No end date";
  }

  const date = new Date(`${value}T00:00:00`);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return new Intl.DateTimeFormat("en-PH", {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(date);
}

function getTenantLabel(tenancy) {
  if (tenancy.tenant_name) {
    return tenancy.tenant_name;
  }

  if (tenancy.tenant && typeof tenancy.tenant === "object") {
    const fullName = [
      tenancy.tenant.first_name,
      tenancy.tenant.last_name,
    ]
      .filter(Boolean)
      .join(" ")
      .trim();

    return fullName || tenancy.tenant.email || "Tenant";
  }

  return tenancy.tenant ? `Tenant #${tenancy.tenant}` : "—";
}

function SummaryCard({ label, value, description, accent }) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-slate-500">{label}</p>
          <p className="mt-3 text-2xl font-bold tracking-tight text-slate-950">
            {value}
          </p>
          <p className="mt-1 text-xs text-slate-500">{description}</p>
        </div>

        <span
          className={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full ${accent}`}
          aria-hidden="true"
        />
      </div>
    </article>
  );
}

export default function Tenancies() {
  const [tenancies, setTenancies] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [lastUpdated, setLastUpdated] = useState(null);

  const loadTenancies = useCallback(async ({ initial = false } = {}) => {
    if (initial) {
      setIsLoading(true);
    } else {
      setIsRefreshing(true);
    }

    setError("");

    try {
      const data = await getTenancies();

      const results = Array.isArray(data)
        ? data
        : Array.isArray(data?.results)
          ? data.results
          : [];

      setTenancies(results);
      setLastUpdated(new Date());
    } catch (requestError) {
      const detail =
        requestError?.response?.data?.detail ||
        requestError?.response?.data?.message;

      const message =
        typeof detail === "string" && detail.trim()
          ? detail
          : !requestError?.response
            ? "Unable to connect to RentNest. Check your connection and try again."
            : requestError.response.status === 401
              ? "Your session may have expired. Please sign in again."
              : "Unable to load tenancies. Please try again.";

      setError(message);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;

    async function fetchInitialTenancies() {
      try {
        const data = await getTenancies();

        if (!isMounted) {
          return;
        }

        const results = Array.isArray(data)
          ? data
          : Array.isArray(data?.results)
            ? data.results
            : [];

        setTenancies(results);
        setLastUpdated(new Date());
        setError("");
      } catch (requestError) {
        if (!isMounted) {
          return;
        }

        const detail =
          requestError?.response?.data?.detail ||
          requestError?.response?.data?.message;

        const message =
          typeof detail === "string" && detail.trim()
            ? detail
            : !requestError?.response
              ? "Unable to connect to RentNest. Check your connection and try again."
              : requestError.response.status === 401
                ? "Your session may have expired. Please sign in again."
                : "Unable to load tenancies. Please try again.";

        setError(message);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    fetchInitialTenancies();

    return () => {
      isMounted = false;
    };
  }, []);

  const summary = useMemo(() => {
    return tenancies.reduce(
      (totals, tenancy) => {
        totals.total += 1;

        const status = normalizeStatus(tenancy.status);

        if (status === "ACTIVE") {
          totals.active += 1;
        } else if (status === "PENDING") {
          totals.pending += 1;
        } else if (status === "ENDED") {
          totals.ended += 1;
        } else if (status === "CANCELLED") {
          totals.cancelled += 1;
        }

        return totals;
      },
      {
        total: 0,
        active: 0,
        pending: 0,
        ended: 0,
        cancelled: 0,
      },
    );
  }, [tenancies]);

  const filteredTenancies = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase();

    return tenancies.filter((tenancy) => {
      const matchesStatus =
        statusFilter === "ALL" ||
        normalizeStatus(tenancy.status) === statusFilter;

      const searchableText = [
        tenancy.id,
        getTenantLabel(tenancy),
        tenancy.property_name,
        tenancy.unit_number,
        tenancy.unit_type,
        tenancy.city,
        tenancy.province,
        tenancy.status,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return (
        matchesStatus &&
        (!normalizedSearch || searchableText.includes(normalizedSearch))
      );
    });
  }, [tenancies, search, statusFilter]);

  const clearFilters = () => {
    setSearch("");
    setStatusFilter("ALL");
  };

  return (
    <div className="mx-auto max-w-7xl space-y-8 pb-10">
      <section className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-blue-600">
            Rental Management
          </p>

          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
            Tenancies
          </h1>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
            Review rental agreements, track tenancy statuses, and search
            tenancy records available to your account.
          </p>

          {lastUpdated && (
            <p className="mt-2 text-xs text-slate-400">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </p>
          )}
        </div>

        <button
          type="button"
          onClick={() => loadTenancies()}
          disabled={isLoading || isRefreshing}
          className="inline-flex items-center justify-center rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isLoading || isRefreshing ? "Refreshing…" : "Refresh tenancies"}
        </button>
      </section>

      {error && (
        <section
          role="alert"
          className="rounded-xl border border-red-200 bg-red-50 p-5"
        >
          <h2 className="font-semibold text-red-900">
            Unable to load tenancies
          </h2>

          <p className="mt-2 text-sm leading-6 text-red-700">{error}</p>

          <button
            type="button"
            onClick={() => loadTenancies()}
            disabled={isRefreshing}
            className="mt-4 rounded-lg bg-red-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-red-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:ring-offset-2 disabled:opacity-60"
          >
            {isRefreshing ? "Retrying…" : "Try again"}
          </button>
        </section>
      )}

      {isLoading ? (
        <section
          className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
          aria-label="Loading tenancy summary"
          aria-busy="true"
        >
          {Array.from({ length: 4 }, (_, index) => (
            <div
              key={index}
              className="h-28 animate-pulse rounded-2xl bg-slate-100"
            />
          ))}
        </section>
      ) : !error ? (
        <>
          <section
            className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
            aria-label="Tenancy summary"
          >
            <SummaryCard
              label="Total Tenancies"
              value={summary.total.toLocaleString("en-PH")}
              description="All loaded agreements"
              accent="bg-blue-500"
            />

            <SummaryCard
              label="Active"
              value={summary.active.toLocaleString("en-PH")}
              description="Currently active agreements"
              accent="bg-emerald-500"
            />

            <SummaryCard
              label="Pending"
              value={summary.pending.toLocaleString("en-PH")}
              description="Awaiting activation"
              accent="bg-amber-500"
            />

            <SummaryCard
              label="Ended"
              value={summary.ended.toLocaleString("en-PH")}
              description="Completed rental agreements"
              accent="bg-slate-400"
            />
          </section>

          {summary.cancelled > 0 && (
            <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <SummaryCard
                label="Cancelled"
                value={summary.cancelled.toLocaleString("en-PH")}
                description="Cancelled agreements"
                accent="bg-red-500"
              />
            </section>
          )}

          <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            <div className="flex flex-col gap-4 border-b border-slate-200 p-5 sm:p-6">
              <div>
                <h2 className="text-lg font-semibold text-slate-950">
                  Rental Agreements
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Search by tenant, property, unit, or tenancy ID.
                </p>
              </div>

              <div className="flex flex-col gap-3 md:flex-row">
                <div className="min-w-0 flex-1">
                  <label htmlFor="tenancy-search" className="sr-only">
                    Search tenancies
                  </label>

                  <input
                    id="tenancy-search"
                    type="search"
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                    placeholder="Search tenant, property, unit, or ID…"
                    className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10"
                  />
                </div>

                <div className="w-full md:w-52">
                  <label htmlFor="tenancy-status" className="sr-only">
                    Filter by tenancy status
                  </label>

                  <select
                    id="tenancy-status"
                    value={statusFilter}
                    onChange={(event) => setStatusFilter(event.target.value)}
                    className="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10"
                  >
                    {STATUS_OPTIONS.map((status) => (
                      <option key={status} value={status}>
                        {status === "ALL"
                          ? "All statuses"
                          : formatStatus(status)}
                      </option>
                    ))}
                  </select>
                </div>

                {(search || statusFilter !== "ALL") && (
                  <button
                    type="button"
                    onClick={clearFilters}
                    className="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-600 transition hover:bg-slate-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
                  >
                    Clear filters
                  </button>
                )}
              </div>
            </div>

            {filteredTenancies.length === 0 ? (
              <div className="p-10 text-center sm:p-14">
                <h3 className="text-base font-semibold text-slate-900">
                  {tenancies.length === 0
                    ? "No tenancies yet"
                    : "No matching tenancies"}
                </h3>

                <p className="mx-auto mt-2 max-w-sm text-sm leading-6 text-slate-500">
                  {tenancies.length === 0
                    ? "Rental agreements available to your account will appear here."
                    : "Try another search term or choose a different status."}
                </p>

                {(search || statusFilter !== "ALL") && (
                  <button
                    type="button"
                    onClick={clearFilters}
                    className="mt-4 text-sm font-semibold text-blue-600 hover:text-blue-700"
                  >
                    Clear filters
                  </button>
                )}
              </div>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-slate-200">
                    <thead className="bg-slate-50">
                      <tr>
                        {[
                          "Tenant",
                          "Property",
                          "Unit",
                          "Monthly Rent",
                          "Start Date",
                          "End Date",
                          "Status",
                        ].map((heading) => (
                          <th
                            key={heading}
                            scope="col"
                            className="whitespace-nowrap px-5 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-slate-500 sm:px-6"
                          >
                            {heading}
                          </th>
                        ))}
                      </tr>
                    </thead>

                    <tbody className="divide-y divide-slate-100">
                      {filteredTenancies.map((tenancy) => (
                        <tr
                          key={tenancy.id}
                          className="transition hover:bg-slate-50"
                        >
                          <td className="whitespace-nowrap px-5 py-4 sm:px-6">
                            <p className="text-sm font-semibold text-slate-900">
                              {getTenantLabel(tenancy)}
                            </p>

                            <p className="mt-1 text-xs text-slate-500">
                              Tenancy #{tenancy.id}
                            </p>
                          </td>

                          <td className="px-5 py-4 sm:px-6">
                            <p className="text-sm font-medium text-slate-800">
                              {tenancy.property_name || "—"}
                            </p>

                            {(tenancy.city || tenancy.province) && (
                              <p className="mt-1 text-xs text-slate-500">
                                {[tenancy.city, tenancy.province]
                                  .filter(Boolean)
                                  .join(", ")}
                              </p>
                            )}
                          </td>

                          <td className="whitespace-nowrap px-5 py-4 sm:px-6">
                            <p className="text-sm text-slate-700">
                              {tenancy.unit_number
                                ? `Unit ${tenancy.unit_number}`
                                : tenancy.unit
                                  ? `Unit #${tenancy.unit}`
                                  : "—"}
                            </p>

                            {tenancy.unit_type && (
                              <p className="mt-1 text-xs text-slate-500">
                                {formatStatus(tenancy.unit_type)}
                              </p>
                            )}
                          </td>

                          <td className="whitespace-nowrap px-5 py-4 text-sm font-semibold text-slate-900 sm:px-6">
                            {formatCurrency(tenancy.monthly_rent)}
                          </td>

                          <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-600 sm:px-6">
                            {formatDate(tenancy.start_date)}
                          </td>

                          <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-600 sm:px-6">
                            {formatDate(tenancy.end_date)}
                          </td>

                          <td className="whitespace-nowrap px-5 py-4 sm:px-6">
                            <span
                              className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset ${getStatusStyles(tenancy.status)}`}
                            >
                              {formatStatus(tenancy.status)}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="flex flex-col gap-2 border-t border-slate-200 px-5 py-4 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between sm:px-6">
                  <p role="status" aria-live="polite">
                    Showing {filteredTenancies.length.toLocaleString("en-PH")}{" "}
                    of {tenancies.length.toLocaleString("en-PH")} loaded
                    tenancies
                  </p>

                  <p>
                    {summary.active.toLocaleString("en-PH")} active agreement
                    {summary.active === 1 ? "" : "s"}
                  </p>
                </div>
              </>
            )}
          </section>
        </>
      ) : null}
    </div>
  );
}
