import { beforeEach, describe, expect, it, vi } from "vitest";
import apiClient from "../client";
import { fetchAllPages } from "../../utils/paginatedRequest";
import {
  getPayments,
  getPayment,
  createPayment,
  updatePayment,
  markPaymentPaid,
  markPaymentFailed,
  refundPayment,
  cancelPayment,
} from "../payments";

vi.mock("../client", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}));

vi.mock("../../utils/paginatedRequest", () => ({
  fetchAllPages: vi.fn(),
}));

describe("Payment API services", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("gets all payments using pagination", async () => {
    const payments = [{ id: 1 }, { id: 2 }];
    fetchAllPages.mockResolvedValue(payments);

    await expect(getPayments()).resolves.toEqual(payments);

    expect(fetchAllPages).toHaveBeenCalledWith("/payments/");
  });

  it("gets a payment by ID", async () => {
    const payment = { id: 5, amount: "1500.00" };
    apiClient.get.mockResolvedValue({ data: payment });

    await expect(getPayment(5)).resolves.toEqual(payment);

    expect(apiClient.get).toHaveBeenCalledWith("/payments/5/");
  });

  it("creates a payment", async () => {
    const payload = {
      tenancy: 3,
      amount: "1500.00",
      payment_method: "CASH",
    };
    const createdPayment = { id: 10, ...payload };

    apiClient.post.mockResolvedValue({ data: createdPayment });

    await expect(createPayment(payload)).resolves.toEqual(createdPayment);

    expect(apiClient.post).toHaveBeenCalledWith("/payments/", payload);
  });

  it("updates a payment", async () => {
    const payload = { amount: "2000.00" };
    const updatedPayment = { id: 5, amount: "2000.00" };

    apiClient.patch.mockResolvedValue({ data: updatedPayment });

    await expect(updatePayment(5, payload)).resolves.toEqual(updatedPayment);

    expect(apiClient.patch).toHaveBeenCalledWith("/payments/5/", payload);
  });

  it("marks a payment as paid", async () => {
    const result = { id: 5, status: "PAID" };
    apiClient.post.mockResolvedValue({ data: result });

    await expect(markPaymentPaid(5)).resolves.toEqual(result);

    expect(apiClient.post).toHaveBeenCalledWith(
      "/payments/5/mark-paid/",
    );
  });

  it("marks a payment as failed", async () => {
    const result = { id: 5, status: "FAILED" };
    apiClient.post.mockResolvedValue({ data: result });

    await expect(markPaymentFailed(5)).resolves.toEqual(result);

    expect(apiClient.post).toHaveBeenCalledWith(
      "/payments/5/mark-failed/",
    );
  });

  it("refunds a payment", async () => {
    const result = { id: 5, status: "REFUNDED" };
    apiClient.post.mockResolvedValue({ data: result });

    await expect(refundPayment(5)).resolves.toEqual(result);

    expect(apiClient.post).toHaveBeenCalledWith(
      "/payments/5/refund/",
    );
  });

  it("cancels a payment", async () => {
    const result = { id: 5, status: "CANCELLED" };
    apiClient.post.mockResolvedValue({ data: result });

    await expect(cancelPayment(5)).resolves.toEqual(result);

    expect(apiClient.post).toHaveBeenCalledWith(
      "/payments/5/cancel/",
    );
  });

  it("propagates payment API errors", async () => {
    apiClient.get.mockRejectedValue(new Error("Payment request failed"));

    await expect(getPayment(5)).rejects.toThrow(
      "Payment request failed",
    );
  });
});