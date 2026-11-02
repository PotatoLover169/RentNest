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
  getProperties,
  getProperty,
  createProperty,
  updateProperty,
  deactivateProperty,
} from "../properties";

describe("Properties API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("getProperties", () => {
    it("fetches all property pages", async () => {
      const properties = [{ id: 1 }, { id: 2 }];

      fetchAllPages.mockResolvedValue(properties);

      await expect(getProperties()).resolves.toEqual(properties);

      expect(fetchAllPages).toHaveBeenCalledWith("/properties/");
      expect(fetchAllPages).toHaveBeenCalledTimes(1);
    });
  });

  describe("getProperty", () => {
    it("fetches a property by ID", async () => {
      const property = { id: 1, name: "Sample Property" };

      apiClient.get.mockResolvedValue({ data: property });

      await expect(getProperty(1)).resolves.toEqual(property);

      expect(apiClient.get).toHaveBeenCalledWith("/properties/1/");
    });

    it("propagates API errors", async () => {
      const error = new Error("Property not found");

      apiClient.get.mockRejectedValue(error);

      await expect(getProperty(999)).rejects.toThrow("Property not found");
    });
  });

  describe("createProperty", () => {
    it("creates a property with the supplied data", async () => {
      const propertyData = {
        name: "Sample Property",
        address: "Cebu City",
      };

      const createdProperty = { id: 1, ...propertyData };

      apiClient.post.mockResolvedValue({ data: createdProperty });

      await expect(createProperty(propertyData)).resolves.toEqual(
        createdProperty,
      );

      expect(apiClient.post).toHaveBeenCalledWith(
        "/properties/",
        propertyData,
      );
    });

    it("propagates API errors", async () => {
      apiClient.post.mockRejectedValue(new Error("Creation failed"));

      await expect(createProperty({ name: "Sample Property" })).rejects.toThrow(
        "Creation failed",
      );
    });
  });

  describe("updateProperty", () => {
    it("updates a property using PATCH", async () => {
      const updateData = { name: "Updated Property" };
      const updatedProperty = { id: 1, ...updateData };

      apiClient.patch.mockResolvedValue({ data: updatedProperty });

      await expect(updateProperty(1, updateData)).resolves.toEqual(
        updatedProperty,
      );

      expect(apiClient.patch).toHaveBeenCalledWith(
        "/properties/1/",
        updateData,
      );
    });

    it("propagates API errors", async () => {
      apiClient.patch.mockRejectedValue(new Error("Update failed"));

      await expect(updateProperty(1, { name: "Updated" })).rejects.toThrow(
        "Update failed",
      );
    });
  });

  describe("deactivateProperty", () => {
    it("deactivates a property", async () => {
      const responseData = { message: "Property deactivated successfully." };

      apiClient.post.mockResolvedValue({ data: responseData });

      await expect(deactivateProperty(1)).resolves.toEqual(responseData);

      expect(apiClient.post).toHaveBeenCalledWith(
        "/properties/1/deactivate/",
      );
    });

    it("propagates API errors", async () => {
      apiClient.post.mockRejectedValue(new Error("Deactivation failed"));

      await expect(deactivateProperty(1)).rejects.toThrow(
        "Deactivation failed",
      );
    });
  });
});