
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getDashboardSummary } from "../../api/dashboard";
import Button from "../../components/ui/Button";
import Card from "../../components/ui/Card";
import { useAuth } from "../../context/useAuth";

const ROLE_LABELS = {
  ADMIN: "Administrator",
  PROPERTY_MANAGER: "Property Manager",
  TENANT: "Tenant",
};

const STAT_CONFIG = {
  ADMIN: [
    {
      key: "properties",
      label: "Total Properties",
      description: "Properties across the platform",
      href: "/properties",
    },
    {
      key: "units",
      label: "Total Units",
      description: "Rental units across the platform",
      href: "/units",
    },
    {
      key: "total_users",
      label: "Total Users",
      description: "Registered platform accounts",
      href: "/users",
    },
    {
      key: "active_tenancies",
      label: "Active Tenancies",
      description: "Currently active rental agreements",
      href: "/tenancies",
    },
    {
      key: "pending_payments",
      label: "Pending Payments",
      description: "Payments awaiting completion",
      href: "/payments",
    },
    {
      key: "open_maintenance_requests",
      label: "Open Maintenance",
      description: "Requests awaiting completion",
      href: "/maintenance",
    },
    {
      key: "total_payments",
      label: "All Payments",
      description: "Payment records across the platform",
      href: "/payments",
    },
    {
      key: "total_maintenance_requests",
      label: "All Maintenance",
      description: "All recorded maintenance requests",
      href: "/maintenance",
    },
  ],
  PROPERTY_MANAGER: [
    {
      key: "properties",
      label: "My Properties",
      description: "Properties assigned to you",
      href: "/properties",
    },
    {
      key: "units",
      label: "My Units",
      description: "Units in your managed properties",
      href: "/units",
    },
    {
      key: "active_tenancies",
      label: "Active Tenancies",
      description: "Active rentals in your properties",
      href: "/tenancies",
    },
    {
      key: "pending_payments",
      label: "Pending Payments",
      description: "Payments awaiting completion",
      href: "/payments",
    },
    {
      key: "open_maintenance_requests",
      label: "Open Maintenance",
      description: "Requests awaiting completion",
      href: "/maintenance",
    },
    {
      key: "unread_notifications",
      label: "Unread Notifications",
      description: "Notifications for your account",
      href: "/notifications",
    },
  ],
  TENANT: [
    {
      key: "active_tenancies",
      label: "Active Rentals",
      description: "Your active rental agreements",
      href: "/my-rental",
    },
    {
      key: "pending_payments",
      label: "Pending Payments",
      description: "Your payments awaiting completion",
      href: "/payments",
    },
    {
      key: "open_maintenance_requests",
      label: "Open Maintenance",
      description: "Your requests awaiting completion",
      href: "/maintenance",
    },
    {
      key: "unread_notifications",
      label: "Unread Notifications",
      description: "Unread updates for your account",
      href: "/notifications",
    },
  ],
};

function getErrorMessage(error) {
  const detail =
    error?.response?.data?.detail ||
    error?.response?.data?.message;

  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  if (!error?.response) {
    return "Unable to connect to RentNest. Check your connection and try again.";
  }

  if (error.response.status === 401) {
    return "Your session may have expired. Please sign in again.";
  }

  return "We couldn't load your dashboard. Please try again.";
}

function formatName(user) {
  const fullName = [user?.first_name, user?.last_name]
    .filter(Boolean)
    .join(" ")
    .trim();

  return fullName || user?.email || "there";
}

function formatNotificationDate(value) {
  if (!value) {
    return "Date unavailable";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Date unavailable";
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function LoadingState() {
  return (
    <div
      className="space-y-6"
      aria-live="polite"
      aria-busy="true"
    >
      <div className="h-8 w-56 animate-pulse rounded-lg bg-slate-200" />
      <div className="h-24 animate-pulse rounded-2xl bg-slate-100" />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }, (_, index) => (
          <div
            key={index}
            className="h-32 animate-pulse rounded-2xl bg-slate-100"
          />
        ))}
      </div>

      <p className="text-sm text-slate-500">
        Loading your dashboard…
      </p>
    </div>
  );
}

function ErrorState({ message, onRetry, isRefreshing }) {
  return (
    <Card className="border border-red-200 bg-white p-6">
      <div className="space-y-3">
        <h2 className="text-lg font-semibold text-slate-900">
          Dashboard unavailable
        </h2>

        <p role="alert" className="text-sm leading-6 text-slate-600">
          {message}
        </p>

        <Button
          type="button"
          variant="primary"
          onClick={onRetry}
          disabled={isRefreshing}
        >
          {isRefreshing ? "Retrying…" : "Try again"}
        </Button>
      </div>
    </Card>
  );
}

function StatCard({ label, value, description, href }) {
  return (
    <Card className="flex h-full flex-col justify-between gap-4 border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      <div>
        <p className="text-sm font-medium text-slate-500">
          {label}
        </p>

        <p className="mt-3 text-3xl font-bold tracking-tight text-slate-900">
          {value ?? 0}
        </p>

        <p className="mt-2 text-sm leading-5 text-slate-500">
          {description}
        </p>
      </div>

      <Link
        to={href}
        className="inline-flex w-fit items-center gap-2 text-sm font-semibold text-blue-600 transition hover:text-blue-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
      >
        View details
        <span aria-hidden="true">→</span>
      </Link>
    </Card>
  );
}

function RecentNotifications({ notifications }) {
  if (!notifications.length) {
    return (
      <div className="rounded-xl border border-dashed border-slate-200 px-5 py-8 text-center">
        <p className="font-medium text-slate-700">
          You're all caught up
        </p>

        <p className="mt-1 text-sm text-slate-500">
          Your recent notifications will appear here.
        </p>
      </div>
    );
  }

  return (
    <ul className="divide-y divide-slate-100">
      {notifications.map((notification) => (
        <li
          key={notification.id}
          className="flex gap-3 py-4 first:pt-0 last:pb-0"
        >
          <span
            className={`mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full ${
              notification.is_read
                ? "bg-slate-300"
                : "bg-blue-500"
            }`}
            aria-hidden="true"
          />

          <div className="min-w-0 flex-1">
            <p className="font-medium text-slate-900">
              {notification.title}
            </p>

            <p className="mt-1 whitespace-pre-line break-words text-sm leading-6 text-slate-600">
              {notification.message}
            </p>

            <p className="mt-2 text-xs text-slate-400">
              {formatNotificationDate(notification.created_at)}
            </p>

            <span className="sr-only">
              {notification.is_read ? "Read" : "Unread"}
            </span>
          </div>
        </li>
      ))}
    </ul>
  );
}

export default function Dashboard() {
  const { user } = useAuth();

  const [dashboard, setDashboard] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState(null);

  const loadDashboard = useCallback(async ({ initial = false } = {}) => {
    if (initial) {
      setIsLoading(true);
    } else {
      setIsRefreshing(true);
    }

    setError("");

    try {
      const data = await getDashboardSummary();

      setDashboard(data);
      setLastUpdated(new Date());
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;

    async function fetchInitialDashboard() {
      try {
        const data = await getDashboardSummary();

        if (isMounted) {
          setDashboard(data);
          setLastUpdated(new Date());
          setError("");
        }
      } catch (requestError) {
        if (isMounted) {
          setError(getErrorMessage(requestError));
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    fetchInitialDashboard();

    return () => {
      isMounted = false;
    };
  }, []);

  if (isLoading) {
    return <LoadingState />;
  }

  if (error && !dashboard) {
    return (
      <ErrorState
        message={error}
        onRetry={() => loadDashboard()}
        isRefreshing={isRefreshing}
      />
    );
  }

  const role = dashboard?.role || user?.role || "";
  const summary = dashboard?.summary || {};
  const notifications = dashboard?.recent_notifications || [];
  const statCards = STAT_CONFIG[role] || [];

  return (
    <div className="space-y-8">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-blue-600">
            {ROLE_LABELS[role] || "Dashboard"}
          </p>

          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
            Welcome back, {formatName(user)}
          </h1>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
            Here is an overview of your rental activity and the latest
            updates for your account.
          </p>

          {lastUpdated && (
            <p className="mt-2 text-xs text-slate-400">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </p>
          )}
        </div>

        <Button
          type="button"
          variant="secondary"
          onClick={() => loadDashboard()}
          disabled={isRefreshing}
        >
          {isRefreshing ? "Refreshing…" : "Refresh dashboard"}
        </Button>
      </header>

      {error && (
        <div
          role="alert"
          className="flex flex-col gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 sm:flex-row sm:items-center sm:justify-between"
        >
          <p className="text-sm text-amber-900">{error}</p>

          <Button
            type="button"
            variant="secondary"
            onClick={() => loadDashboard()}
            disabled={isRefreshing}
          >
            {isRefreshing ? "Retrying…" : "Retry"}
          </Button>
        </div>
      )}

      <section aria-labelledby="dashboard-stats-heading">
        <div className="mb-4">
          <h2
            id="dashboard-stats-heading"
            className="text-lg font-semibold text-slate-900"
          >
            Overview
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Statistics based on the latest records in RentNest.
          </p>
        </div>

        {statCards.length === 0 ? (
          <Card className="border border-slate-200 bg-white p-5">
            <p className="text-sm text-slate-600">
              Dashboard statistics are not configured for this account role.
            </p>
          </Card>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {statCards.map((stat) => (
              <StatCard
                key={stat.key}
                label={stat.label}
                value={summary[stat.key]}
                description={stat.description}
                href={stat.href}
              />
            ))}
          </div>
        )}
      </section>

      <section aria-labelledby="dashboard-notifications-heading">
        <Card className="border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2
                id="dashboard-notifications-heading"
                className="text-lg font-semibold text-slate-900"
              >
                Recent Notifications
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                The latest updates sent to your account.
              </p>
            </div>

            <Link
              to="/notifications"
              className="inline-flex w-fit items-center gap-2 text-sm font-semibold text-blue-600 hover:text-blue-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
            >
              View all
              <span aria-hidden="true">→</span>
            </Link>
          </div>

          <RecentNotifications notifications={notifications} />
        </Card>
      </section>
    </div>
  );
}
