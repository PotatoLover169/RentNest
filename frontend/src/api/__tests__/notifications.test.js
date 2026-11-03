import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../client", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn(),
  },
}));

vi.mock("../../utils/paginatedRequest", () => ({
  fetchAllPages: vi.fn(),
}));

import apiClient from "../client";
import { fetchAllPages } from "../../utils/paginatedRequest";
import {
  getNotifications,
  getNotification,
  markNotificationRead,
  markNotificationUnread,
  markAllNotificationsRead,
  deleteNotification,
} from "../notifications";

describe("Notifications API", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("getNotifications", () => {
    it("fetches all notification pages", async () => {
      const notifications = [
        { id: 1, message: "Payment received" },
        { id: 2, message: "Maintenance request updated" },
      ];

      fetchAllPages.mockResolvedValue(notifications);

      await expect(getNotifications()).resolves.toEqual(notifications);

      expect(fetchAllPages).toHaveBeenCalledWith("/notifications/");
      expect(fetchAllPages).toHaveBeenCalledTimes(1);
    });

    it("propagates pagination errors", async () => {
      fetchAllPages.mockRejectedValue(
        new Error("Unable to fetch notifications"),
      );

      await expect(getNotifications()).rejects.toThrow(
        "Unable to fetch notifications",
      );
    });
  });

  describe("getNotification", () => {
    it("fetches a notification by ID", async () => {
      const notification = {
        id: 1,
        message: "Payment received",
        is_read: false,
      };

      apiClient.get.mockResolvedValue({ data: notification });

      await expect(getNotification(1)).resolves.toEqual(notification);

      expect(apiClient.get).toHaveBeenCalledWith("/notifications/1/");
    });

    it("propagates API errors", async () => {
      apiClient.get.mockRejectedValue(
        new Error("Notification not found"),
      );

      await expect(getNotification(999)).rejects.toThrow(
        "Notification not found",
      );
    });
  });

  describe("markNotificationRead", () => {
    it("marks a notification as read", async () => {
      const responseData = {
        id: 1,
        is_read: true,
      };

      apiClient.post.mockResolvedValue({ data: responseData });

      await expect(markNotificationRead(1)).resolves.toEqual(responseData);

      expect(apiClient.post).toHaveBeenCalledWith(
        "/notifications/1/mark-read/",
      );
    });

    it("propagates API errors", async () => {
      apiClient.post.mockRejectedValue(
        new Error("Unable to mark notification as read"),
      );

      await expect(markNotificationRead(1)).rejects.toThrow(
        "Unable to mark notification as read",
      );
    });
  });

  describe("markNotificationUnread", () => {
    it("marks a notification as unread", async () => {
      const responseData = {
        id: 1,
        is_read: false,
      };

      apiClient.post.mockResolvedValue({ data: responseData });

      await expect(markNotificationUnread(1)).resolves.toEqual(
        responseData,
      );

      expect(apiClient.post).toHaveBeenCalledWith(
        "/notifications/1/mark-unread/",
      );
    });

    it("propagates API errors", async () => {
      apiClient.post.mockRejectedValue(
        new Error("Unable to mark notification as unread"),
      );

      await expect(markNotificationUnread(1)).rejects.toThrow(
        "Unable to mark notification as unread",
      );
    });
  });

  describe("markAllNotificationsRead", () => {
    it("marks all notifications as read", async () => {
      const responseData = {
        message: "All notifications marked as read.",
      };

      apiClient.post.mockResolvedValue({ data: responseData });

      await expect(markAllNotificationsRead()).resolves.toEqual(
        responseData,
      );

      expect(apiClient.post).toHaveBeenCalledWith(
        "/notifications/mark-all-read/",
      );
    });

    it("propagates API errors", async () => {
      apiClient.post.mockRejectedValue(
        new Error("Unable to mark all notifications as read"),
      );

      await expect(markAllNotificationsRead()).rejects.toThrow(
        "Unable to mark all notifications as read",
      );
    });
  });

  describe("deleteNotification", () => {
    it("deletes a notification by ID", async () => {
      const responseData = {
        message: "Notification deleted successfully.",
      };

      apiClient.delete.mockResolvedValue({ data: responseData });

      await expect(deleteNotification(1)).resolves.toEqual(responseData);

      expect(apiClient.delete).toHaveBeenCalledWith(
        "/notifications/1/delete/",
      );
    });

    it("propagates API errors", async () => {
      apiClient.delete.mockRejectedValue(
        new Error("Unable to delete notification"),
      );

      await expect(deleteNotification(1)).rejects.toThrow(
        "Unable to delete notification",
      );
    });
  });
});