import apiClient from "./client";

export async function getMaintenanceRequests() {
  const response = await apiClient.get("/maintenance/");
  return response.data;
}

export async function getMaintenanceRequest(id) {
  const response = await apiClient.get(`/maintenance/${id}/`);
  return response.data;
}

export async function createMaintenanceRequest(data) {
  const response = await apiClient.post("/maintenance/", data);
  return response.data;
}

export async function updateMaintenanceRequest(id, data) {
  const response = await apiClient.patch(`/maintenance/${id}/`, data);
  return response.data;
}

export async function startMaintenanceRequest(id) {
  const response = await apiClient.post(`/maintenance/${id}/start/`);
  return response.data;
}

export async function completeMaintenanceRequest(id, data) {
  const response = await apiClient.post(
    `/maintenance/${id}/complete/`,
    data,
  );
  return response.data;
}

export async function cancelMaintenanceRequest(id) {
  const response = await apiClient.post(
    `/maintenance/${id}/cancel/`,
  );
  return response.data;
}