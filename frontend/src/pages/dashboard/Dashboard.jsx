const stats = [
  {
    label: "Properties",
    value: "0",
    description: "Managed properties",
  },
  {
    label: "Units",
    value: "0",
    description: "Total rental units",
  },
  {
    label: "Active Tenancies",
    value: "0",
    description: "Current tenants",
  },
  {
    label: "Pending Payments",
    value: "0",
    description: "Payments requiring attention",
  },
];

function Dashboard() {
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
          Getting started
        </h2>

        <p className="mt-2 text-sm leading-6 text-slate-500">
          Your RentNest workspace is ready. Once authentication and
          API integration are connected, this dashboard will display
          live property management data.
        </p>
      </section>
    </div>
  );
}

export default Dashboard;