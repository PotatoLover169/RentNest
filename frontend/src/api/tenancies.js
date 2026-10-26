
import apiClient from "./client";
import { fetchAllPages } from "../utils/paginatedRequest";

export async function getTenancies() {
  return fetchAllPages("/tenancies/");
}

export async function getTenancy(id) {
  const response = await apiClient.get(`/tenancies/${id}/`);
  return response.data;
}

export async function createTenancy(data) {
  const response = await apiClient.post("/tenancies/", data);
  return response.data;
}

export async function updateTenancy(id, data) {
  const response = await apiClient.patch(`/tenancies/${id}/`, data);
  return response.data;
}

export async function activateTenancy(id) {
  const response = await apiClient.post(`/tenancies/${id}/activate/`);
  return response.data;
}

export async function endTenancy(id, data) {
  const response = await apiClient.post(`/tenancies/${id}/end/`, data);
  return response.data;
}
