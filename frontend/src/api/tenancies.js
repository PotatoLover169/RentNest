import apiClient from "./client";

export async function getTenancies() {
  const response = await apiClient.get("/tenancies/");

  return response.data;
}