import apiClient from "./client";

export async function getMaintenanceRequests() {
  const response = await apiClient.get("/maintenance/");

  return response.data;
}