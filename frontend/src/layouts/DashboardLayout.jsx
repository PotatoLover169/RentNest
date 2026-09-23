import { NavLink, Outlet } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

const navigationItems = [
  { label: "Dashboard", path: "/dashboard" },
  { label: "Properties", path: "/properties" },
  { label: "Units", path: "/units" },
  { label: "Tenancies", path: "/tenancies" },
  { label: "Payments", path: "/payments" },
  { label: "Maintenance", path: "/maintenance" },
  { label: "Notifications", path: "/notifications" },
];

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

function getInitials(user) {
  const displayName = getDisplayName(user);

  const words = displayName.split(/\s+/).filter(Boolean);

  if (words.length >= 2) {
    return `${words[0][0]}${words[words.length - 1][0]}`.toUpperCase();
  }

  return displayName.slice(0, 2).toUpperCase();
}

function DashboardLayout() {
  const { user, logout } = useAuth();

  const displayName = getDisplayName(user);
  const initials = getInitials(user);

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
            onClick={logout}
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
              {displayName}
            </p>
          </div>

          <div
            className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-900 text-sm font-semibold text-white"
            aria-label={`Signed in as ${displayName}`}
            title={user?.email}
          >
            {initials}
          </div>
        </header>

        <main className="p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default DashboardLayout;