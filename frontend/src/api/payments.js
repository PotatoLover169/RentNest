import apiClient from "./client";

export async function getPayments() {
  const response = await apiClient.get("/payments/");

  return response.data;
}