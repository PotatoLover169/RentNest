import { beforeEach, describe, expect, it, vi } from "vitest";
import apiClient from "../../api/client";
import { fetchAllPages } from "../paginatedRequest";

vi.mock("../../api/client", () => ({
  default: {
    get: vi.fn(),
  },
}));

describe("fetchAllPages", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("rejects an invalid endpoint", async () => {
    await expect(fetchAllPages("")).rejects.toThrow(
      "A valid API endpoint URL is required.",
    );

    expect(apiClient.get).not.toHaveBeenCalled();
  });

  it("returns an unpaginated array response", async () => {
    apiClient.get.mockResolvedValueOnce({
      data: [{ id: 1 }, { id: 2 }],
    });

    await expect(fetchAllPages("/properties/")).resolves.toEqual([
      { id: 1 },
      { id: 2 },
    ]);

    expect(apiClient.get).toHaveBeenCalledTimes(1);
  });

  it("returns an empty array when the first paginated page is empty", async () => {
    apiClient.get.mockResolvedValueOnce({
      data: {
        count: 0,
        next: null,
        previous: null,
        results: [],
      },
    });

    await expect(fetchAllPages("/properties/")).resolves.toEqual([]);

    expect(apiClient.get).toHaveBeenCalledTimes(1);
  });

  it("fetches all pages and combines their results", async () => {
    apiClient.get
      .mockResolvedValueOnce({
        data: {
          next: "/properties/?page=2",
          results: [{ id: 1 }, { id: 2 }],
        },
      })
      .mockResolvedValueOnce({
        data: {
          next: null,
          results: [{ id: 3 }],
        },
      });

    const result = await fetchAllPages("/properties/", {
      page_size: 2,
    });

    expect(result).toEqual([{ id: 1 }, { id: 2 }, { id: 3 }]);

    expect(apiClient.get).toHaveBeenNthCalledWith(1, "/properties/", {
      params: { page_size: 2 },
    });

    expect(apiClient.get).toHaveBeenNthCalledWith(
      2,
      "/properties/?page=2",
      {},
    );
  });

  it("continues when a page has no results but has a next page", async () => {
    apiClient.get
      .mockResolvedValueOnce({
        data: {
          next: "/properties/?page=2",
          results: [],
        },
      })
      .mockResolvedValueOnce({
        data: {
          next: null,
          results: [{ id: 1 }],
        },
      });

    await expect(fetchAllPages("/properties/")).resolves.toEqual([
      { id: 1 },
    ]);

    expect(apiClient.get).toHaveBeenCalledTimes(2);
  });

  it("stops when next is null", async () => {
    apiClient.get.mockResolvedValueOnce({
      data: {
        next: null,
        results: [{ id: 1 }],
      },
    });

    await expect(fetchAllPages("/properties/")).resolves.toEqual([
      { id: 1 },
    ]);

    expect(apiClient.get).toHaveBeenCalledTimes(1);
  });

  it("rejects an unexpected response format", async () => {
    apiClient.get.mockResolvedValueOnce({
      data: { items: [{ id: 1 }] },
    });

    await expect(fetchAllPages("/properties/")).rejects.toThrow(
      "Unexpected API response: expected an array or paginated results.",
    );
  });

  it("rejects an invalid pagination URL", async () => {
    apiClient.get.mockResolvedValueOnce({
      data: {
        next: " ",
        results: [{ id: 1 }],
      },
    });

    await expect(fetchAllPages("/properties/")).rejects.toThrow(
      "Invalid pagination URL returned by the API.",
    );
  });

  it("rejects a repeated page URL", async () => {
    apiClient.get.mockResolvedValueOnce({
      data: {
        next: "/properties/",
        results: [{ id: 1 }],
      },
    });

    await expect(fetchAllPages("/properties/")).rejects.toThrow(
      "Pagination stopped because a page URL repeated.",
    );

    expect(apiClient.get).toHaveBeenCalledTimes(1);
  });

  it("propagates API request errors", async () => {
    const error = new Error("Network error");
    apiClient.get.mockRejectedValueOnce(error);

    await expect(fetchAllPages("/properties/")).rejects.toThrow(
      "Network error",
    );
  });
});