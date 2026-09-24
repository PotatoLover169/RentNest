import apiClient from "./client";

export async function getProperties() {
  const response = await apiClient.get("/properties/");

  return response.data;
}