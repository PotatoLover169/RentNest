import apiClient from "./client";

export async function getNotifications() {
  const response = await apiClient.get(
    "/notifications/",
  );

  return response.data;
}

export async function getNotification(id) {
  const response = await apiClient.get(
    `/notifications/${id}/`,
  );

  return response.data;
}

export async function markNotificationRead(id) {
  const response = await apiClient.post(
    `/notifications/${id}/mark-read/`,
  );

  return response.data;
}

export async function markNotificationUnread(id) {
  const response = await apiClient.post(
    `/notifications/${id}/mark-unread/`,
  );

  return response.data;
}

export async function markAllNotificationsRead() {
  const response = await apiClient.post(
    "/notifications/mark-all-read/",
  );

  return response.data;
}

export async function deleteNotification(id) {
  const response = await apiClient.delete(
    `/notifications/${id}/delete/`,
  );

  return response.data;
}