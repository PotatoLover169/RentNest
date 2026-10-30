
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../../api/client", () => ({
  default: {
    get: vi.fn(),
  },
}));

import apiClient from "../../api/client";
import { fetchAllPages } from "../paginatedRequest";

describe("fetchAllPages", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("rejects an invalid endpoint", async () => {
    await expect(fetchAllPages("")).rejects.toThrow(
      "A valid API endpoint URL is required.",
    );

    await expect(fetchAllPages(null)).rejects.toThrow(TypeError);

    expect(apiClient.get).not.toHaveBeenCalled();
  });

  it("returns an unpaginated array", async () => {
    apiClient.get.mockResolvedValueOnce({
      data: [{ id: 1 }, { id: 2 }],
    });

    await expect(fetchAllPages("/properties/")).resolves.toEqual([
      { id: 1 },
      { id: 2 },
    ]);

    expect(apiClient.get).toHaveBeenCalledTimes(1);
  });

  it("combines results from every page", async () => {
    apiClient.get
      .mockResolvedValueOnce({
        data: {
          count: 3,
          next: "/properties/?page=2",
          previous: null,
          results: [{ id: 1 }, { id: 2 }],
        },
      })
      .mockResolvedValueOnce({
        data: {
          count: 3,
          next: null,
          previous: "/properties/",
          results: [{ id: 3 }],
        },
      });

    await expect(
      fetchAllPages("/properties/", { search: "apartment" }),
    ).resolves.toEqual([{ id: 1 }, { id: 2 }, { id: 3 }]);

    expect(apiClient.get).toHaveBeenNthCalledWith(
      1,
      "/properties/",
      { params: { search: "apartment" } },
    );

    expect(apiClient.get).toHaveBeenNthCalledWith(
      2,
      "/properties/?page=2",
      {},
    );
  });

  it("rejects an unexpected response format", async () => {
    apiClient.get.mockResolvedValueOnce({
      data: { count: 10, items: [] },
    });

    await expect(fetchAllPages("/properties/")).rejects.toThrow(
      "Unexpected API response: expected an array or paginated results.",
    );
  });

  it("rejects an invalid next-page URL", async () => {
    apiClient.get.mockResolvedValueOnce({
      data: {
        results: [{ id: 1 }],
        next: 123,
      },
    });

    await expect(fetchAllPages("/properties/")).rejects.toThrow(
      "Invalid pagination URL returned by the API.",
    );
  });

  it("stops if the API repeats a page URL", async () => {
    apiClient.get
      .mockResolvedValueOnce({
        data: {
          results: [{ id: 1 }],
          next: "/properties/",
        },
      });

    await expect(fetchAllPages("/properties/")).rejects.toThrow(
      "Pagination stopped because a page URL repeated.",
    );
  });
});
