
import apiClient from "./client";
import { fetchAllPages } from "../utils/paginatedRequest";

export async function getProperties() {
  return fetchAllPages("/properties/");
}

export async function getProperty(id) {
  const response = await apiClient.get(`/properties/${id}/`);
  return response.data;
}

export async function createProperty(data) {
  const response = await apiClient.post("/properties/", data);
  return response.data;
}

export async function updateProperty(id, data) {
  const response = await apiClient.patch(`/properties/${id}/`, data);
  return response.data;
}

export async function deactivateProperty(id) {
  const response = await apiClient.post(`/properties/${id}/deactivate/`);
  return response.data;
}
