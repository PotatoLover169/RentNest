import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getTenancies } from "../../api/tenancies";

function formatDate(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleDateString("en-PH", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function formatCurrency(value) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "—";
  }

  const amount = Number(value);

  if (Number.isNaN(amount)) {
    return "—";
  }

  return new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
  }).format(amount);
}

function formatLabel(value) {
  if (!value) {
    return "—";
  }

  return String(value)
    .toLowerCase()
    .split("_")
    .map(
      (word) =>
        word.charAt(0).toUpperCase() +
        word.slice(1),
    )
    .join(" ");
}

function InfoItem({ label, value }) {
  return (
    <div className="border-b border-slate-100 py-4 last:border-b-0">
      <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
        {label}
      </p>

      <p className="mt-1 text-sm font-semibold text-slate-900">
        {value}
      </p>
    </div>
  );
}

function MyRental() {
  const [tenancy, setTenancy] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let isActive = true;

    const loadRental = async () => {
      try {
        setIsLoading(true);
        setError("");

        const data = await getTenancies();

        const results = Array.isArray(data)
          ? data
          : Array.isArray(data?.results)
            ? data.results
            : [];

        const activeTenancy =
          results.find(
            (item) => item.status === "ACTIVE",
          ) || null;

        if (isActive) {
          setTenancy(activeTenancy);
        }
      } catch (requestError) {
        if (isActive) {
          setError(
            requestError?.response?.data?.detail ||
              requestError?.response?.data?.message ||
              "Unable to load your rental information.",
          );
        }
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    };

    loadRental();

    return () => {
      isActive = false;
    };
  }, []);

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600" />

          <p className="mt-4 text-sm text-slate-500">
            Loading your rental...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-5xl">
        <div className="rounded-2xl border border-red-200 bg-red-50 p-6">
          <h1 className="text-lg font-bold text-red-900">
            Unable to Load Rental
          </h1>

          <p className="mt-2 text-sm text-red-700">
            {error}
          </p>
        </div>
      </div>
    );
  }

  if (!tenancy) {
    return (
      <div className="mx-auto max-w-5xl space-y-8">
        <section>
          <p className="text-sm font-semibold uppercase tracking-wider text-slate-500">
            Tenant Portal
          </p>

          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
            My Rental
          </h1>

          <p className="mt-2 text-sm leading-6 text-slate-500">
            View your current rental information.
          </p>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-10 text-center shadow-sm">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-slate-100 text-2xl">
            🏠
          </div>

          <h2 className="mt-5 text-xl font-bold text-slate-950">
            No Active Rental
          </h2>

          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
            You don't currently have an active tenancy
            associated with your account.
          </p>

          <Link
            to="/notifications"
            className="mt-6 inline-flex items-center justify-center rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
          >
            View Notifications
          </Link>
        </section>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <section>
        <p className="text-sm font-semibold uppercase tracking-wider text-slate-500">
          Tenant Portal
        </p>

        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
          My Rental
        </h1>

        <p className="mt-2 text-sm leading-6 text-slate-500">
          Your current rental, tenancy, and property manager
          information.
        </p>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm font-medium text-slate-500">
              Current Property
            </p>

            <h2 className="mt-1 text-2xl font-bold tracking-tight text-slate-950">
              {tenancy.property_name || "Your Rental Property"}
            </h2>

            <p className="mt-2 text-sm text-slate-500">
              {[
                tenancy.address_line,
                tenancy.city,
                tenancy.province,
              ]
                .filter(Boolean)
                .join(", ") || "Address unavailable"}
            </p>
          </div>

          <span className="inline-flex w-fit rounded-full bg-emerald-50 px-3 py-1.5 text-sm font-semibold text-emerald-700 ring-1 ring-inset ring-emerald-600/20">
            {formatLabel(tenancy.status)}
          </span>
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-bold text-slate-950">
            Rental Details
          </h2>

          <div className="mt-4">
            <InfoItem
              label="Unit"
              value={
                tenancy.unit_number
                  ? `Unit ${tenancy.unit_number}`
                  : "—"
              }
            />

            <InfoItem
              label="Unit Type"
              value={formatLabel(tenancy.unit_type)}
            />

            <InfoItem
              label="Monthly Rent"
              value={formatCurrency(
                tenancy.monthly_rent,
              )}
            />

            <InfoItem
              label="Security Deposit"
              value={formatCurrency(
                tenancy.security_deposit,
              )}
            />
          </div>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-bold text-slate-950">
            Tenancy Information
          </h2>

          <div className="mt-4">
            <InfoItem
              label="Start Date"
              value={formatDate(
                tenancy.start_date,
              )}
            />

            <InfoItem
              label="End Date"
              value={formatDate(
                tenancy.end_date,
              )}
            />

            <InfoItem
              label="Property Manager"
              value={
                tenancy.manager_name ||
                tenancy.manager_email ||
                "—"
              }
            />

            <InfoItem
              label="Manager Email"
              value={
                tenancy.manager_email || "—"
              }
            />
          </div>
        </section>
      </div>

      <section className="rounded-2xl border border-blue-100 bg-blue-50 p-6">
        <h2 className="text-lg font-bold text-blue-950">
          Need help with your rental?
        </h2>

        <p className="mt-2 max-w-2xl text-sm leading-6 text-blue-800">
          Submit a maintenance request when something in
          your rental needs attention.
        </p>

        <Link
          to="/maintenance"
          className="mt-5 inline-flex items-center justify-center rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-700"
        >
          Go to Maintenance
        </Link>
      </section>
    </div>
  );
}

export default MyRental;