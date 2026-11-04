
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../client", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}));

import apiClient from "../client";
import {
  loginUser,
  registerUser,
  getCurrentUser,
  updateCurrentUser,
  logoutUser,
  refreshAccessToken,
} from "../auth";

describe("Authentication API services", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("logs in a user with credentials", async () => {
    const credentials = {
      email: "tenant@example.com",
      password: "SecurePassword123!",
    };
    const result = {
      access: "access-token",
      refresh: "refresh-token",
    };

    apiClient.post.mockResolvedValue({ data: result });

    await expect(loginUser(credentials)).resolves.toEqual(result);
    expect(apiClient.post).toHaveBeenCalledWith("/auth/login/", credentials);
  });

  it("registers a user", async () => {
    const payload = {
      email: "newtenant@example.com",
      password: "SecurePassword123!",
      first_name: "New",
      last_name: "Tenant",
    };
    const result = {
      id: 1,
      email: payload.email,
      role: "TENANT",
    };

    apiClient.post.mockResolvedValue({ data: result });

    await expect(registerUser(payload)).resolves.toEqual(result);
    expect(apiClient.post).toHaveBeenCalledWith("/auth/register/", payload);
  });

  it("gets the current authenticated user", async () => {
    const user = {
      id: 1,
      email: "tenant@example.com",
      role: "TENANT",
    };

    apiClient.get.mockResolvedValue({ data: user });

    await expect(getCurrentUser()).resolves.toEqual(user);
    expect(apiClient.get).toHaveBeenCalledWith("/auth/me/");
  });

  it("updates the current user's profile", async () => {
    const profile = {
      first_name: "Updated",
      last_name: "Tenant",
    };
    const result = {
      id: 1,
      email: "tenant@example.com",
      ...profile,
    };

    apiClient.patch.mockResolvedValue({ data: result });

    await expect(updateCurrentUser(profile)).resolves.toEqual(result);
    expect(apiClient.patch).toHaveBeenCalledWith("/auth/me/", profile);
  });

  it("logs out using the supplied refresh token", async () => {
    const refreshToken = "refresh-token";
    const result = { message: "Successfully logged out." };

    apiClient.post.mockResolvedValue({ data: result });

    await expect(logoutUser(refreshToken)).resolves.toEqual(result);
    expect(apiClient.post).toHaveBeenCalledWith("/auth/logout/", {
      refresh: refreshToken,
    });
  });

  it("refreshes the access token", async () => {
    const refreshToken = "refresh-token";
    const result = { access: "new-access-token" };

    apiClient.post.mockResolvedValue({ data: result });

    await expect(refreshAccessToken(refreshToken)).resolves.toEqual(result);
    expect(apiClient.post).toHaveBeenCalledWith("/auth/refresh/", {
      refresh: refreshToken,
    });
  });

  it.each([
    ["loginUser", () => loginUser({ email: "tenant@example.com", password: "wrong" })],
    ["registerUser", () => registerUser({ email: "tenant@example.com" })],
    ["getCurrentUser", () => getCurrentUser()],
    ["updateCurrentUser", () => updateCurrentUser({ first_name: "Updated" })],
    ["logoutUser", () => logoutUser("refresh-token")],
    ["refreshAccessToken", () => refreshAccessToken("refresh-token")],
  ])("propagates API errors from %s", async (_name, request) => {
    const error = new Error("Authentication request failed");

    apiClient.get.mockRejectedValue(error);
    apiClient.post.mockRejectedValue(error);
    apiClient.patch.mockRejectedValue(error);

    await expect(request()).rejects.toBe(error);
  });

  it("sends the refresh token only in the logout request body", async () => {
    apiClient.post.mockResolvedValue({
      data: { message: "Successfully logged out." },
    });

    await logoutUser("sample-refresh-token");

    expect(apiClient.post).toHaveBeenCalledTimes(1);
    expect(apiClient.post.mock.calls[0]).toEqual([
      "/auth/logout/",
      { refresh: "sample-refresh-token" },
    ]);
  });

  it("sends the refresh token only in the refresh request body", async () => {
    apiClient.post.mockResolvedValue({
      data: { access: "new-access-token" },
    });

    await refreshAccessToken("sample-refresh-token");

    expect(apiClient.post).toHaveBeenCalledTimes(1);
    expect(apiClient.post.mock.calls[0]).toEqual([
      "/auth/refresh/",
      { refresh: "sample-refresh-token" },
    ]);
  });
});
