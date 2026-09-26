import apiClient from "./client";

export async function getNotifications() {
  const response = await apiClient.get("/notifications/");

  return response.data;
}