import { Navigate, Route, Routes } from "react-router-dom";

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
import MaintenanceForm from "../pages/maintenance/MaintenanceForm";

import Notifications from "../pages/notifications/Notifications";

import MyRental from "../pages/tenant/MyRental";

import ProtectedRoute from "./ProtectedRoute";
import RoleRoute from "./RoleRoute";

function AppRoutes() {
  return (
    <Routes>
      {/* ======================================================
          AUTHENTICATED APPLICATION
      ====================================================== */}

      <Route element={<ProtectedRoute />}>
        <Route element={<DashboardLayout />}>

          {/* ==================================================
              ALL AUTHENTICATED USERS
          ================================================== */}

          <Route
            path="/dashboard"
            element={<Dashboard />}
          />

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
            path="/maintenance/new"
            element={<MaintenanceForm />}
          />

          <Route
            path="/notifications"
            element={<Notifications />}
          />

          {/* ==================================================
              ADMIN + PROPERTY MANAGER
          ================================================== */}

          <Route
            element={
              <RoleRoute
                allowedRoles={[
                  "ADMIN",
                  "PROPERTY_MANAGER",
                ]}
              />
            }
          >
            <Route
              path="/properties"
              element={<Properties />}
            />

            <Route
              path="/properties/:id"
              element={<PropertyDetails />}
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
              path="/units"
              element={<Units />}
            />

            <Route
              path="/units/new"
              element={<UnitForm />}
            />

            <Route
              path="/units/:id"
              element={<UnitDetails />}
            />

            <Route
              path="/units/:id/edit"
              element={<UnitForm />}
            />

            <Route
              path="/tenancies"
              element={<Tenancies />}
            />
          </Route>

          {/* ==================================================
              TENANT
          ================================================== */}

          <Route
            element={
              <RoleRoute
                allowedRoles={["TENANT"]}
              />
            }
          >
            <Route
              path="/my-rental"
              element={<MyRental />}
            />
          </Route>
        </Route>
      </Route>

      {/* ======================================================
          PUBLIC AUTH ROUTES
      ====================================================== */}

      <Route
        path="/login"
        element={<Login />}
      />

      <Route
        path="/register"
        element={<Register />}
      />

      {/* ======================================================
          FALLBACK
      ====================================================== */}

      <Route
        path="*"
        element={
          <Navigate
            to="/dashboard"
            replace
          />
        }
      />
    </Routes>
  );
}

export default AppRoutes;