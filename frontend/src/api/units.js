import apiClient from "./client";

export async function getUnits() {
  const response = await apiClient.get(
    "/properties/units/",
  );

  return response.data;
}

export async function getUnit(id) {
  const response = await apiClient.get(
    `/properties/units/${id}/`,
  );

  return response.data;
}

export async function createUnit(data) {
  const response = await apiClient.post(
    "/properties/units/",
    data,
  );

  return response.data;
}

export async function updateUnit(id, data) {
  const response = await apiClient.patch(
    `/properties/units/${id}/`,
    data,
  );

  return response.data;
}

export async function updateUnitStatus(id, data) {
  const response = await apiClient.post(
    `/properties/units/${id}/status/`,
    data,
  );

  return response.data;
}

export async function deactivateUnit(id) {
  const response = await apiClient.post(
    `/properties/units/${id}/deactivate/`,
  );

  return response.data;
}