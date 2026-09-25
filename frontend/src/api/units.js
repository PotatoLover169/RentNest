import apiClient from "./client";

export async function getUnits() {
  const response = await apiClient.get("/properties/units/");

  return response.data;
}