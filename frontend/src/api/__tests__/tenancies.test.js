import { beforeEach, describe, expect, it, vi } from "vitest";
import apiClient from "../client";
import { fetchAllPages } from "../../utils/paginatedRequest";
import {
  getTenancies,
  getTenancy,
  createTenancy,
  updateTenancy,
  activateTenancy,
  endTenancy,
} from "../tenancies";

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

describe("Tenancy API services", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("gets all tenancies using pagination", async () => {
    const tenancies = [{ id: 1 }, { id: 2 }];
    fetchAllPages.mockResolvedValue(tenancies);

    await expect(getTenancies()).resolves.toEqual(tenancies);

    expect(fetchAllPages).toHaveBeenCalledWith("/tenancies/");
  });

  it("gets a tenancy by ID", async () => {
    const tenancy = { id: 5, status: "ACTIVE" };
    apiClient.get.mockResolvedValue({ data: tenancy });

    await expect(getTenancy(5)).resolves.toEqual(tenancy);

    expect(apiClient.get).toHaveBeenCalledWith("/tenancies/5/");
  });

  it("creates a tenancy", async () => {
    const payload = {
      property: 2,
      tenant: 8,
      monthly_rent: "12000.00",
    };
    const createdTenancy = { id: 10, ...payload };

    apiClient.post.mockResolvedValue({ data: createdTenancy });

    await expect(createTenancy(payload)).resolves.toEqual(createdTenancy);

    expect(apiClient.post).toHaveBeenCalledWith("/tenancies/", payload);
  });

  it("updates a tenancy", async () => {
    const payload = { monthly_rent: "15000.00" };
    const updatedTenancy = { id: 5, monthly_rent: "15000.00" };

    apiClient.patch.mockResolvedValue({ data: updatedTenancy });

    await expect(updateTenancy(5, payload)).resolves.toEqual(updatedTenancy);

    expect(apiClient.patch).toHaveBeenCalledWith("/tenancies/5/", payload);
  });

  it("activates a tenancy", async () => {
    const result = { id: 5, status: "ACTIVE" };
    apiClient.post.mockResolvedValue({ data: result });

    await expect(activateTenancy(5)).resolves.toEqual(result);

    expect(apiClient.post).toHaveBeenCalledWith(
      "/tenancies/5/activate/",
    );
  });

  it("ends a tenancy with the supplied data", async () => {
    const payload = {
      end_date: "2026-10-31",
      reason: "Lease completed",
    };
    const result = { id: 5, status: "ENDED" };

    apiClient.post.mockResolvedValue({ data: result });

    await expect(endTenancy(5, payload)).resolves.toEqual(result);

    expect(apiClient.post).toHaveBeenCalledWith(
      "/tenancies/5/end/",
      payload,
    );
  });

  it("propagates tenancy API errors", async () => {
    apiClient.get.mockRejectedValue(new Error("Tenancy request failed"));

    await expect(getTenancy(5)).rejects.toThrow(
      "Tenancy request failed",
    );
  });
});