import { beforeEach, describe, expect, it, vi } from "vitest";

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

import apiClient from "../client";
import { fetchAllPages } from "../../utils/paginatedRequest";
import {
  getUnits,
  getUnit,
  createUnit,
  updateUnit,
  updateUnitStatus,
  deactivateUnit,
} from "../units";

describe("Units API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("getUnits", () => {
    it("fetches all unit pages", async () => {
      const units = [
        { id: 1, unit_number: "101" },
        { id: 2, unit_number: "102" },
      ];

      fetchAllPages.mockResolvedValue(units);

      await expect(getUnits()).resolves.toEqual(units);

      expect(fetchAllPages).toHaveBeenCalledWith("/properties/units/");
      expect(fetchAllPages).toHaveBeenCalledTimes(1);
    });

    it("propagates pagination errors", async () => {
      fetchAllPages.mockRejectedValue(new Error("Unable to fetch units"));

      await expect(getUnits()).rejects.toThrow("Unable to fetch units");
    });
  });

  describe("getUnit", () => {
    it("fetches a unit by ID", async () => {
      const unit = { id: 1, unit_number: "101" };

      apiClient.get.mockResolvedValue({ data: unit });

      await expect(getUnit(1)).resolves.toEqual(unit);

      expect(apiClient.get).toHaveBeenCalledWith("/properties/units/1/");
    });

    it("propagates API errors", async () => {
      apiClient.get.mockRejectedValue(new Error("Unit not found"));

      await expect(getUnit(999)).rejects.toThrow("Unit not found");
    });
  });

  describe("createUnit", () => {
    it("creates a unit with the supplied data", async () => {
      const unitData = {
        property: 1,
        unit_number: "101",
      };

      const createdUnit = { id: 1, ...unitData };

      apiClient.post.mockResolvedValue({ data: createdUnit });

      await expect(createUnit(unitData)).resolves.toEqual(createdUnit);

      expect(apiClient.post).toHaveBeenCalledWith(
        "/properties/units/",
        unitData,
      );
    });

    it("propagates API errors", async () => {
      apiClient.post.mockRejectedValue(new Error("Unit creation failed"));

      await expect(createUnit({ unit_number: "101" })).rejects.toThrow(
        "Unit creation failed",
      );
    });
  });

  describe("updateUnit", () => {
    it("updates a unit using PATCH", async () => {
      const updateData = { unit_number: "102" };
      const updatedUnit = { id: 1, ...updateData };

      apiClient.patch.mockResolvedValue({ data: updatedUnit });

      await expect(updateUnit(1, updateData)).resolves.toEqual(updatedUnit);

      expect(apiClient.patch).toHaveBeenCalledWith(
        "/properties/units/1/",
        updateData,
      );
    });

    it("propagates API errors", async () => {
      apiClient.patch.mockRejectedValue(new Error("Unit update failed"));

      await expect(updateUnit(1, { unit_number: "102" })).rejects.toThrow(
        "Unit update failed",
      );
    });
  });

  describe("updateUnitStatus", () => {
    it("updates a unit status", async () => {
      const statusData = { status: "MAINTENANCE" };
      const responseData = { id: 1, ...statusData };

      apiClient.post.mockResolvedValue({ data: responseData });

      await expect(updateUnitStatus(1, statusData)).resolves.toEqual(
        responseData,
      );

      expect(apiClient.post).toHaveBeenCalledWith(
        "/properties/units/1/status/",
        statusData,
      );
    });

    it("propagates API errors", async () => {
      apiClient.post.mockRejectedValue(new Error("Status update failed"));

      await expect(
        updateUnitStatus(1, { status: "MAINTENANCE" }),
      ).rejects.toThrow("Status update failed");
    });
  });

  describe("deactivateUnit", () => {
    it("deactivates a unit", async () => {
      const responseData = {
        message: "Unit deactivated successfully.",
      };

      apiClient.post.mockResolvedValue({ data: responseData });

      await expect(deactivateUnit(1)).resolves.toEqual(responseData);

      expect(apiClient.post).toHaveBeenCalledWith(
        "/properties/units/1/deactivate/",
      );
    });

    it("propagates API errors", async () => {
      apiClient.post.mockRejectedValue(new Error("Deactivation failed"));

      await expect(deactivateUnit(1)).rejects.toThrow(
        "Deactivation failed",
      );
    });
  });
});