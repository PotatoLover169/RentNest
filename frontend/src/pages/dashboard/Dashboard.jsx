import { useAuth } from "../../context/AuthContext";

function getDisplayName(user) {
  if (!user) {
    return "User";
  }

  const fullName = [user.first_name, user.last_name]
    .filter(Boolean)
    .join(" ")
    .trim();

  return fullName || user.email || "User";
}

function formatRole(role) {
  if (!role) {
    return "User";
  }

  return role
    .toLowerCase()
    .split("_")
    .map(
      (word) =>
        word.charAt(0).toUpperCase() + word.slice(1),
    )
    .join(" ");
}

const stats = [
  {
    label: "Properties",
    value: "—",
    description: "Managed properties",
  },
  {
    label: "Units",
    value: "—",
    description: "Total rental units",
  },
  {
    label: "Active Tenancies",
    value: "—",
    description: "Current tenants",
  },
  {
    label: "Pending Payments",
    value: "—",
    description: "Payments requiring attention",
  },
];

function Dashboard() {
  const { user } = useAuth();

  const displayName = getDisplayName(user);
  const role = formatRole(user?.role);

  return (
    <div className="mx-auto max-w-7xl space-y-8">
      <section>
        <p className="text-sm font-semibold uppercase tracking-wider text-slate-500">
          Overview
        </p>

        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
          Dashboard
        </h1>

        <p className="mt-2 max-w-2xl text-slate-500">
          Manage your properties, units, tenants, payments, and
          maintenance activities from one place.
        </p>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-medium text-slate-500">
              Signed in as
            </p>

            <h2 className="mt-1 text-2xl font-bold tracking-tight text-slate-950">
              {displayName}
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              {user?.email}
            </p>
          </div>

          <div className="inline-flex w-fit rounded-full bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-700">
            {role}
          </div>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
          >
            <p className="text-sm font-medium text-slate-500">
              {stat.label}
            </p>

            <p className="mt-3 text-3xl font-bold text-slate-950">
              {stat.value}
            </p>

            <p className="mt-1 text-sm text-slate-500">
              {stat.description}
            </p>
          </div>
        ))}
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-950">
          Your workspace
        </h2>

        <p className="mt-2 text-sm leading-6 text-slate-500">
          Your account information is being loaded from the
          authenticated RentNest API. Dashboard statistics will be
          connected to the corresponding property management
          resources as those modules are integrated.
        </p>
      </section>
    </div>
  );
}

export default Dashboard;