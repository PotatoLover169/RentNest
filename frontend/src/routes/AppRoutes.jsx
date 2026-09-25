import { Navigate, Route, Routes } from "react-router-dom";

import DashboardLayout from "../layouts/DashboardLayout";
import Dashboard from "../pages/dashboard/Dashboard";
import Login from "../pages/auth/Login";
import Register from "../pages/auth/Register";
import Properties from "../pages/properties/Properties";
import ProtectedRoute from "./ProtectedRoute";
import Units from "../pages/units/Units";
import Tenancies from "../pages/tenancies/Tenancies";
import Payments from "../pages/payments/Payments";

function AppRoutes() {
  return (
    <Routes>
      <Route element={<ProtectedRoute />}>
        <Route element={<DashboardLayout />}>
          <Route
            path="/dashboard"
            element={<Dashboard />}
          />

          <Route
            path="/properties"
            element={<Properties />}
          />

          <Route
            path="/units"
            element={<Units />}
          />

          <Route
            path="/tenancies"
            element={<Tenancies />}
          />

          <Route
            path="/payments"
            element={<Payments />}
          />
        </Route>
      </Route>

      <Route
        path="/login"
        element={<Login />}
      />

      <Route
        path="/register"
        element={<Register />}
      />

      <Route
        path="*"
        element={<Navigate to="/dashboard" replace />}
      />
    </Routes>
  );
}

export default AppRoutes;