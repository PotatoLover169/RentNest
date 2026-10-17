import { Navigate, Outlet, Route, Routes } from "react-router-dom";

import { useAuth } from "../context/useAuth";
import DashboardLayout from "../layouts/DashboardLayout";

import Dashboard from "../pages/dashboard/Dashboard";

import Login from "../pages/auth/Login";
import Register from "../pages/auth/Register";

import Properties from "../pages/properties/Properties";
import PropertyDetails from "../pages/properties/PropertyDetails";
import PropertyForm from "../pages/properties/PropertyForm";

import Units from "../pages/units/Units";
import UnitForm from "../pages/units/UnitForm";
import UnitDetails from "../pages/units/UnitDetails";

import Tenancies from "../pages/tenancies/Tenancies";

import Payments from "../pages/payments/Payments";
import PaymentDetail from "../pages/payments/PaymentDetail";

import Maintenance from "../pages/maintenance/Maintenance";
import MaintenanceDetail from "../pages/maintenance/MaintenanceDetail";

import Notifications from "../pages/notifications/Notifications";
import Settings from "../pages/settings/Settings";

import MyRental from "../pages/tenant/MyRental";

import ProtectedRoute from "./ProtectedRoute";

function RoleRoute({ allowedRoles }) {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <p className="text-sm font-medium text-slate-500">
          Loading RentNest...
        </p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const role = String(user.role || "").toUpperCase();

  if (!allowedRoles.includes(role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}

function AppRoutes() {
  return (
    <Routes>
      {/* Authentication-protected application routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<DashboardLayout />}>
          {/* All authenticated roles */}
          <Route
            path="/dashboard"
            element={<Dashboard />}
          />

          {/* Admin and property manager only */}
          <Route
            element={
              <RoleRoute
                allowedRoles={["ADMIN", "PROPERTY_MANAGER"]}
              />
            }
          >
            <Route
              path="/properties"
              element={<Properties />}
            />

            <Route
              path="/properties/new"
              element={<PropertyForm />}
            />

            <Route
              path="/properties/:id/edit"
              element={<PropertyForm />}
            />

            <Route
              path="/properties/:id"
              element={<PropertyDetails />}
            />

            <Route
              path="/units"
              element={<Units />}
            />

            <Route
              path="/units/new"
              element={<UnitForm />}
            />

            <Route
              path="/units/:id/edit"
              element={<UnitForm />}
            />

            <Route
              path="/units/:id"
              element={<UnitDetails />}
            />

            <Route
              path="/tenancies"
              element={<Tenancies />}
            />
          </Route>

          {/* Tenant only */}
          <Route
            element={
              <RoleRoute allowedRoles={["TENANT"]} />
            }
          >
            <Route
              path="/my-rental"
              element={<MyRental />}
            />
          </Route>

          {/* Shared pages; backend permissions still apply */}
          <Route
            path="/payments"
            element={<Payments />}
          />

          <Route
            path="/payments/:id"
            element={<PaymentDetail />}
          />

          <Route
            path="/maintenance"
            element={<Maintenance />}
          />

          <Route
            path="/maintenance/:id"
            element={<MaintenanceDetail />}
          />

          <Route
            path="/notifications"
            element={<Notifications />}
          />

          <Route
            path="/settings"
            element={<Settings />}
          />
        </Route>
      </Route>

      {/* Public authentication routes */}
      <Route
        path="/login"
        element={<Login />}
      />

      <Route
        path="/register"
        element={<Register />}
      />

      {/* Unknown routes */}
      <Route
        path="*"
        element={<Navigate to="/dashboard" replace />}
      />
    </Routes>
  );
}

export default AppRoutes;