
import { useCallback, useEffect, useMemo, useState } from "react";
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

function normalize(value) {
  return String(value ?? "").trim().toLowerCase();
}

function formatLabel(value) {
  if (!value) return "Unknown";
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

function statusClass(status) {
  switch (normalize(status)) {
    case "available":
      return "bg-emerald-50 text-emerald-700 ring-1 ring-inset ring-emerald-600/20";
    case "occupied":
      return "bg-blue-50 text-blue-700 ring-1 ring-inset ring-blue-600/20";
    case "maintenance":
      return "bg-amber-50 text-amber-800 ring-1 ring-inset ring-amber-600/20";
    case "inactive":
      return "bg-slate-100 text-slate-600 ring-1 ring-inset ring-slate-500/20";
    default:
      return "bg-slate-100 text-slate-700 ring-1 ring-inset ring-slate-500/20";
  }
}

function UnitStatus({ status }) {
  return (
    <span className={`inline-flex whitespace-nowrap items-center rounded-full px-3 py-1 text-xs font-semibold ${statusClass(status)}`}>
      <span className="mr-2 h-1.5 w-1.5 rounded-full bg-current" aria-hidden="true" />
      {formatLabel(status || "AVAILABLE")}
    </span>
  );
}

function UnitCard({ unit, propertyName, onView }) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-blue-200 hover:shadow-md">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Unit {unit.unit_number ?? unit.id}
          </p>
          <h3 className="mt-1 break-words text-lg font-bold text-slate-950">
            {propertyName}
          </h3>
          <p className="mt-1 text-sm text-slate-500">
            {formatLabel(unit.unit_type)}
          </p>
        </div>
        <UnitStatus status={unit.status} />
      </div>

      <div className="mt-5 grid grid-cols-2 gap-4 border-t border-slate-100 pt-4">
        <div>
          <p className="text-xs font-medium text-slate-400">Monthly rent</p>
          <p className="mt-1 font-semibold text-slate-900">
            {formatRent(unit.monthly_rent)}
          </p>
        </div>
        <div>
          <p className="text-xs font-medium text-slate-400">Bedrooms / Baths</p>
          <p className="mt-1 font-semibold text-slate-900">
            {unit.bedrooms ?? 0} / {unit.bathrooms ?? 0}
          </p>
        </div>
      </div>

      <div className="mt-5 flex justify-end">
        <Button variant="secondary" size="sm" onClick={() => onView(unit.id)}>
          View Unit
        </Button>
      </div>
    </article>
  );
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
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortBy, setSortBy] = useState("unit-asc");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastRefreshed, setLastRefreshed] = useState(null);

  const loadUnits = useCallback(async () => {
    try {
      setIsLoading(true);
      setError("");

      const [unitsData, propertiesData] = await Promise.all([
        getUnits(),
        getProperties(),
      ]);

      setUnits(getResults(unitsData));
      setProperties(getResults(propertiesData));
      setPagination(getPagination(unitsData));
      setLastRefreshed(new Date());
    } catch (requestError) {
      setError(
        requestError?.response?.data?.detail ||
          requestError?.response?.data?.message ||
          "Unable to load units. Please try again.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // Fetch units and their property names on page mount.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadUnits();
  }, [loadUnits]);

  const propertyNames = useMemo(() => {
    return new Map(
      properties.map((property) => [String(property.id), property.name]),
    );
  }, [properties]);

  const getPropertyName = useCallback(
    (propertyId) =>
      propertyNames.get(String(propertyId)) || `Property #${propertyId ?? "—"}`,
    [propertyNames],
  );

  const filteredUnits = useMemo(() => {
    const query = normalize(search);

    const result = units.filter((unit) => {
      const propertyName = getPropertyName(unit.property);
      const matchesSearch = !query || [
        unit.unit_number,
        unit.unit_type,
        unit.id,
        propertyName,
      ].some((value) => normalize(value).includes(query));

      const status = normalize(unit.status || "available");
      const matchesStatus = statusFilter === "all" || status === statusFilter;

      return matchesSearch && matchesStatus;
    });

    return [...result].sort((a, b) => {
      const unitA = normalize(a.unit_number);
      const unitB = normalize(b.unit_number);

      switch (sortBy) {
        case "unit-desc":
          return unitB.localeCompare(unitA, undefined, { numeric: true });
        case "rent-asc":
          return Number(a.monthly_rent || 0) - Number(b.monthly_rent || 0);
        case "rent-desc":
          return Number(b.monthly_rent || 0) - Number(a.monthly_rent || 0);
        case "status-asc":
          return normalize(a.status).localeCompare(normalize(b.status));
        default:
          return unitA.localeCompare(unitB, undefined, { numeric: true });
      }
    });
  }, [units, search, statusFilter, sortBy, getPropertyName]);

  const summary = useMemo(() => ({
    total: pagination.count || units.length,
    available: units.filter((unit) => normalize(unit.status || "available") === "available").length,
    occupied: units.filter((unit) => normalize(unit.status) === "occupied").length,
    maintenance: units.filter((unit) => normalize(unit.status) === "maintenance").length,
  }), [units, pagination.count]);

  const hasFilters =
    Boolean(search.trim()) || statusFilter !== "all" || sortBy !== "unit-asc";

  const clearFilters = () => {
    setSearch("");
    setStatusFilter("all");
    setSortBy("unit-asc");
  };

  const showUnits = !isLoading || units.length > 0;

  return (
    <div className="mx-auto max-w-7xl space-y-8">
      <PageHeader
        eyebrow="Management"
        title="Rental Units"
        description="Review unit availability, rental prices, and unit information across your properties."
        action={
          <div className="flex flex-wrap gap-3">
            <Button variant="secondary" onClick={loadUnits} disabled={isLoading}>
              {isLoading ? "Refreshing..." : "Refresh"}
            </Button>
            <Button onClick={() => navigate("/units/new")}>Add Unit</Button>
          </div>
        }
      />

      {lastRefreshed && (
        <p className="-mt-5 text-xs text-slate-400">
          Last refreshed at {lastRefreshed.toLocaleTimeString([], {
            hour: "numeric",
            minute: "2-digit",
          })}
        </p>
      )}

      {isLoading && units.length === 0 && (
        <LoadingState message="Loading rental units..." />
      )}

      {!isLoading && error && units.length === 0 && (
        <ErrorState
          title="Unable to load units"
          message={String(error)}
          action={
            <Button variant="secondary" onClick={loadUnits}>
              Try Again
            </Button>
          }
        />
      )}

      {error && units.length > 0 && (
        <div role="alert" className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          Refresh failed. Showing the previously loaded units. {String(error)}
        </div>
      )}

      {showUnits && !error && units.length === 0 && (
        <EmptyState
          title="No units yet"
          description="Add a rental unit to begin tracking availability and monthly rent."
          action={<Button onClick={() => navigate("/units/new")}>Add Unit</Button>}
        />
      )}

      {showUnits && units.length > 0 && (
        <>
          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {[
              ["Total units", summary.total, "text-slate-950"],
              ["Available", summary.available, "text-emerald-700"],
              ["Occupied", summary.occupied, "text-blue-700"],
              ["Maintenance", summary.maintenance, "text-amber-700"],
            ].map(([label, value, color]) => (
              <Card key={label} className="p-5">
                <p className="text-sm font-medium text-slate-500">{label}</p>
                <p className={`mt-2 text-3xl font-bold tracking-tight ${color}`}>{value}</p>
              </Card>
            ))}
          </section>

          <Card className="p-5 sm:p-6">
            <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_190px_190px_auto] lg:items-end">
              <div>
                <label htmlFor="unit-search" className="mb-2 block text-sm font-semibold text-slate-700">
                  Search units
                </label>
                <input
                  id="unit-search"
                  type="search"
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                  placeholder="Unit number or property..."
                  className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10"
                />
              </div>

              <div>
                <label htmlFor="unit-status" className="mb-2 block text-sm font-semibold text-slate-700">
                  Status
                </label>
                <select
                  id="unit-status"
                  value={statusFilter}
                  onChange={(event) => setStatusFilter(event.target.value)}
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10"
                >
                  <option value="all">All statuses</option>
                  <option value="available">Available</option>
                  <option value="occupied">Occupied</option>
                  <option value="maintenance">Maintenance</option>
                  <option value="inactive">Inactive</option>
                </select>
              </div>

              <div>
                <label htmlFor="unit-sort" className="mb-2 block text-sm font-semibold text-slate-700">
                  Sort by
                </label>
                <select
                  id="unit-sort"
                  value={sortBy}
                  onChange={(event) => setSortBy(event.target.value)}
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10"
                >
                  <option value="unit-asc">Unit number A–Z</option>
                  <option value="unit-desc">Unit number Z–A</option>
                  <option value="rent-asc">Rent: low to high</option>
                  <option value="rent-desc">Rent: high to low</option>
                  <option value="status-asc">Status</option>
                </select>
              </div>

              <Button variant="secondary" onClick={clearFilters} disabled={!hasFilters}>
                Clear
              </Button>
            </div>

            <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-4">
              <p className="text-sm text-slate-500">
                Showing <span className="font-semibold text-slate-900">{filteredUnits.length}</span> of{" "}
                <span className="font-semibold text-slate-900">{units.length}</span> loaded units
              </p>
              {isLoading && <span className="text-xs font-medium text-blue-700">Refreshing data…</span>}
            </div>
          </Card>

          {filteredUnits.length === 0 ? (
            <EmptyState
              title="No matching units"
              description="Try changing your search or filters."
              action={<Button variant="secondary" onClick={clearFilters}>Clear filters</Button>}
            />
          ) : (
            <>
              <section className="grid gap-4 sm:grid-cols-2 lg:hidden">
                {filteredUnits.map((unit) => (
                  <UnitCard
                    key={unit.id}
                    unit={unit}
                    propertyName={getPropertyName(unit.property)}
                    onView={(unitId) => navigate(`/units/${unitId}`)}
                  />
                ))}
              </section>

              <Card className="hidden overflow-hidden lg:block">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-slate-200">
                    <thead className="bg-slate-50">
                      <tr>
                        {["Unit", "Property", "Type", "Monthly rent", "Status", "Actions"].map((heading) => (
                          <th
                            key={heading}
                            scope="col"
                            className={`px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-500 ${heading === "Actions" ? "text-right" : "text-left"}`}
                          >
                            {heading}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 bg-white">
                      {filteredUnits.map((unit) => (
                        <tr key={unit.id} className="transition hover:bg-slate-50">
                          <td className="whitespace-nowrap px-6 py-4">
                            <p className="font-semibold text-slate-900">
                              Unit {unit.unit_number ?? unit.id}
                            </p>
                            <p className="mt-1 text-xs text-slate-400">
                              {unit.bedrooms ?? 0} bed · {unit.bathrooms ?? 0} bath
                            </p>
                          </td>
                          <td className="px-6 py-4 text-sm text-slate-600">
                            {getPropertyName(unit.property)}
                          </td>
                          <td className="px-6 py-4 text-sm text-slate-600">
                            {formatLabel(unit.unit_type)}
                          </td>
                          <td className="whitespace-nowrap px-6 py-4 text-sm font-semibold text-slate-900">
                            {formatRent(unit.monthly_rent)}
                          </td>
                          <td className="px-6 py-4">
                            <UnitStatus status={unit.status} />
                          </td>
                          <td className="px-6 py-4 text-right">
                            <Button variant="ghost" size="sm" onClick={() => navigate(`/units/${unit.id}`)}>
                              View details
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            </>
          )}
        </>
      )}
    </div>
  );
}

export default Units;
