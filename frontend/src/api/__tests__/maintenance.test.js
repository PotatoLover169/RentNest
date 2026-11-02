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
  getMaintenanceRequests,
  getMaintenanceRequest,
  createMaintenanceRequest,
  updateMaintenanceRequest,
  startMaintenanceRequest,
  completeMaintenanceRequest,
  cancelMaintenanceRequest,
} from "../maintenance";

describe("Maintenance API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("getMaintenanceRequests", () => {
    it("fetches all maintenance request pages", async () => {
      const requests = [
        { id: 1, title: "Leaking faucet" },
        { id: 2, title: "Electrical issue" },
      ];

      fetchAllPages.mockResolvedValue(requests);

      await expect(getMaintenanceRequests()).resolves.toEqual(requests);

      expect(fetchAllPages).toHaveBeenCalledWith("/maintenance/");
      expect(fetchAllPages).toHaveBeenCalledTimes(1);
    });

    it("propagates pagination errors", async () => {
      fetchAllPages.mockRejectedValue(
        new Error("Unable to fetch maintenance requests"),
      );

      await expect(getMaintenanceRequests()).rejects.toThrow(
        "Unable to fetch maintenance requests",
      );
    });
  });

  describe("getMaintenanceRequest", () => {
    it("fetches a maintenance request by ID", async () => {
      const request = { id: 1, title: "Leaking faucet" };

      apiClient.get.mockResolvedValue({ data: request });

      await expect(getMaintenanceRequest(1)).resolves.toEqual(request);

      expect(apiClient.get).toHaveBeenCalledWith("/maintenance/1/");
    });

    it("propagates API errors", async () => {
      apiClient.get.mockRejectedValue(
        new Error("Maintenance request not found"),
      );

      await expect(getMaintenanceRequest(999)).rejects.toThrow(
        "Maintenance request not found",
      );
    });
  });

  describe("createMaintenanceRequest", () => {
    it("creates a maintenance request", async () => {
      const requestData = {
        title: "Leaking faucet",
        description: "The kitchen faucet is leaking.",
      };

      const createdRequest = { id: 1, ...requestData };

      apiClient.post.mockResolvedValue({ data: createdRequest });

      await expect(
        createMaintenanceRequest(requestData),
      ).resolves.toEqual(createdRequest);

      expect(apiClient.post).toHaveBeenCalledWith(
        "/maintenance/",
        requestData,
      );
    });

    it("propagates API errors", async () => {
      apiClient.post.mockRejectedValue(
        new Error("Maintenance request creation failed"),
      );

      await expect(
        createMaintenanceRequest({ title: "Leaking faucet" }),
      ).rejects.toThrow("Maintenance request creation failed");
    });
  });

  describe("updateMaintenanceRequest", () => {
    it("updates a maintenance request using PATCH", async () => {
      const updateData = { title: "Updated maintenance request" };
      const updatedRequest = { id: 1, ...updateData };

      apiClient.patch.mockResolvedValue({ data: updatedRequest });

      await expect(
        updateMaintenanceRequest(1, updateData),
      ).resolves.toEqual(updatedRequest);

      expect(apiClient.patch).toHaveBeenCalledWith(
        "/maintenance/1/",
        updateData,
      );
    });

    it("propagates API errors", async () => {
      apiClient.patch.mockRejectedValue(
        new Error("Maintenance request update failed"),
      );

      await expect(
        updateMaintenanceRequest(1, { title: "Updated" }),
      ).rejects.toThrow("Maintenance request update failed");
    });
  });

  describe("startMaintenanceRequest", () => {
    it("starts a maintenance request", async () => {
      const responseData = { id: 1, status: "IN_PROGRESS" };

      apiClient.post.mockResolvedValue({ data: responseData });

      await expect(startMaintenanceRequest(1)).resolves.toEqual(
        responseData,
      );

      expect(apiClient.post).toHaveBeenCalledWith(
        "/maintenance/1/start/",
      );
    });

    it("propagates API errors", async () => {
      apiClient.post.mockRejectedValue(
        new Error("Unable to start maintenance request"),
      );

      await expect(startMaintenanceRequest(1)).rejects.toThrow(
        "Unable to start maintenance request",
      );
    });
  });

  describe("completeMaintenanceRequest", () => {
    it("completes a maintenance request with supplied data", async () => {
      const completionData = {
        completion_notes: "The faucet has been repaired.",
      };

      const responseData = {
        id: 1,
        status: "COMPLETED",
        ...completionData,
      };

      apiClient.post.mockResolvedValue({ data: responseData });

      await expect(
        completeMaintenanceRequest(1, completionData),
      ).resolves.toEqual(responseData);

      expect(apiClient.post).toHaveBeenCalledWith(
        "/maintenance/1/complete/",
        completionData,
      );
    });

    it("propagates API errors", async () => {
      apiClient.post.mockRejectedValue(
        new Error("Unable to complete maintenance request"),
      );

      await expect(
        completeMaintenanceRequest(1, {
          completion_notes: "Completed",
        }),
      ).rejects.toThrow("Unable to complete maintenance request");
    });
  });

  describe("cancelMaintenanceRequest", () => {
    it("cancels a maintenance request", async () => {
      const responseData = {
        id: 1,
        status: "CANCELLED",
      };

      apiClient.post.mockResolvedValue({ data: responseData });

      await expect(cancelMaintenanceRequest(1)).resolves.toEqual(
        responseData,
      );

      expect(apiClient.post).toHaveBeenCalledWith(
        "/maintenance/1/cancel/",
      );
    });

    it("propagates API errors", async () => {
      apiClient.post.mockRejectedValue(
        new Error("Unable to cancel maintenance request"),
      );

      await expect(cancelMaintenanceRequest(1)).rejects.toThrow(
        "Unable to cancel maintenance request",
      );
    });
  });
});