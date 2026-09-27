import apiClient from "./client";

export async function getPayments() {
  const response = await apiClient.get(
    "/payments/",
  );

  return response.data;
}

export async function getPayment(id) {
  const response = await apiClient.get(
    `/payments/${id}/`,
  );

  return response.data;
}

export async function createPayment(data) {
  const response = await apiClient.post(
    "/payments/",
    data,
  );

  return response.data;
}

export async function updatePayment(id, data) {
  const response = await apiClient.patch(
    `/payments/${id}/`,
    data,
  );

  return response.data;
}

export async function markPaymentPaid(id) {
  const response = await apiClient.post(
    `/payments/${id}/mark-paid/`,
  );

  return response.data;
}

export async function markPaymentFailed(id) {
  const response = await apiClient.post(
    `/payments/${id}/mark-failed/`,
  );

  return response.data;
}

export async function refundPayment(id) {
  const response = await apiClient.post(
    `/payments/${id}/refund/`,
  );

  return response.data;
}

export async function cancelPayment(id) {
  const response = await apiClient.post(
    `/payments/${id}/cancel/`,
  );

  return response.data;
}