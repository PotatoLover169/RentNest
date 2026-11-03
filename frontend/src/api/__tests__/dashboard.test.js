import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../client", () => ({
  default: {
    get: vi.fn(),
  },
}));

import apiClient from "../client";
import { getDashboardSummary } from "../dashboard";

describe("Dashboard API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("getDashboardSummary", () => {
    it("fetches the dashboard summary", async () => {
      const summary = {
        total_properties: 10,
        total_units: 50,
        occupied_units: 35,
        vacant_units: 15,
      };

      apiClient.get.mockResolvedValue({ data: summary });

      await expect(getDashboardSummary()).resolves.toEqual(summary);

      expect(apiClient.get).toHaveBeenCalledWith("/dashboard/");
      expect(apiClient.get).toHaveBeenCalledTimes(1);
    });

    it("returns an empty summary when the API returns an empty object", async () => {
      apiClient.get.mockResolvedValue({ data: {} });

      await expect(getDashboardSummary()).resolves.toEqual({});
    });

    it("propagates API errors", async () => {
      apiClient.get.mockRejectedValue(
        new Error("Unable to fetch dashboard summary"),
      );

      await expect(getDashboardSummary()).rejects.toThrow(
        "Unable to fetch dashboard summary",
      );
    });
  });
});