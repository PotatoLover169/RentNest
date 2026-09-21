import { NavLink, Outlet } from "react-router-dom";

const navigationItems = [
  {
    label: "Dashboard",
    path: "/dashboard",
  },
  {
    label: "Properties",
    path: "/properties",
  },
  {
    label: "Units",
    path: "/units",
  },
  {
    label: "Tenancies",
    path: "/tenancies",
  },
  {
    label: "Payments",
    path: "/payments",
  },
  {
    label: "Maintenance",
    path: "/maintenance",
  },
  {
    label: "Notifications",
    path: "/notifications",
  },
];

function DashboardLayout() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-slate-200 bg-white lg:block">
        <div className="flex h-16 items-center border-b border-slate-200 px-6">
          <div>
            <p className="text-xl font-bold tracking-tight text-slate-900">
              RentNest
            </p>
            <p className="text-xs text-slate-500">
              Property Management
            </p>
          </div>
        </div>

        <nav className="space-y-1 p-4">
          {navigationItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                [
                  "block rounded-lg px-4 py-2.5 text-sm font-medium transition",
                  isActive
                    ? "bg-slate-900 text-white"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
                ].join(" ")
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 border-t border-slate-200 p-4">
          <button
            type="button"
            className="w-full rounded-lg px-4 py-2.5 text-left text-sm font-medium text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
          >
            Logout
          </button>
        </div>
      </aside>

      <div className="lg:pl-64">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur sm:px-6">
          <div>
            <p className="text-sm font-medium text-slate-500">
              Welcome back
            </p>
            <p className="text-sm font-semibold text-slate-900">
              RentNest Dashboard
            </p>
          </div>

          <button
            type="button"
            className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-100 text-sm font-semibold text-slate-700"
            aria-label="User profile"
          >
            U
          </button>
        </header>

        <main className="p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default DashboardLayout;