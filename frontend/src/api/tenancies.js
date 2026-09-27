import apiClient from "./client";

export async function getTenancies() {
  const response = await apiClient.get(
    "/tenancies/",
  );

  return response.data;
}

export async function getTenancy(id) {
  const response = await apiClient.get(
    `/tenancies/${id}/`,
  );

  return response.data;
}

export async function createTenancy(data) {
  const response = await apiClient.post(
    "/tenancies/",
    data,
  );

  return response.data;
}

export async function updateTenancy(id, data) {
  const response = await apiClient.patch(
    `/tenancies/${id}/`,
    data,
  );

  return response.data;
}

export async function activateTenancy(id) {
  const response = await apiClient.post(
    `/tenancies/${id}/activate/`,
  );

  return response.data;
}

export async function endTenancy(id) {
  const response = await apiClient.post(
    `/tenancies/${id}/end/`,
  );

  return response.data;
}