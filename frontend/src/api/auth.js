import apiClient from "./client";

export async function loginUser(credentials) {
  const response = await apiClient.post(
    "/auth/login/",
    credentials,
  );

  return response.data;
}

export async function registerUser(data) {
  const response = await apiClient.post(
    "/auth/register/",
    data,
  );

  return response.data;
}

export async function getCurrentUser() {
  const response = await apiClient.get("/auth/me/");

  return response.data;
}

export async function logoutUser(refreshToken) {
  const response = await apiClient.post(
    "/auth/logout/",
    {
      refresh: refreshToken,
    },
  );

  return response.data;
}

export async function refreshAccessToken(refreshToken) {
  const response = await apiClient.post(
    "/auth/refresh/",
    {
      refresh: refreshToken,
    },
  );

  return response.data;
}