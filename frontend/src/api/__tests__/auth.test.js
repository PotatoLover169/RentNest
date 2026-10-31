import { beforeEach, describe, expect, it, vi } from "vitest";
import apiClient from "../client";
import {
  loginUser,
  registerUser,
  getCurrentUser,
  updateCurrentUser,
  logoutUser,
  refreshAccessToken,
} from "../auth";

vi.mock("../client", () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
  },
}));

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

    expect(apiClient.post).toHaveBeenCalledWith(
      "/auth/login/",
      credentials,
    );
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

    expect(apiClient.post).toHaveBeenCalledWith(
      "/auth/register/",
      payload,
    );
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

    expect(apiClient.patch).toHaveBeenCalledWith(
      "/auth/me/",
      profile,
    );
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
    const result = {
      access: "new-access-token",
    };

    apiClient.post.mockResolvedValue({ data: result });

    await expect(refreshAccessToken(refreshToken)).resolves.toEqual(
      result,
    );

    expect(apiClient.post).toHaveBeenCalledWith("/auth/refresh/", {
      refresh: refreshToken,
    });
  });

  it("propagates authentication API errors", async () => {
    apiClient.post.mockRejectedValue(
      new Error("Invalid credentials"),
    );

    await expect(
      loginUser({
        email: "tenant@example.com",
        password: "wrong-password",
      }),
    ).rejects.toThrow("Invalid credentials");
  });
});