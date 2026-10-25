
import apiClient from "../api/client";

/**
 * Fetch all pages from a Django REST Framework endpoint.
 * Supports unpaginated arrays and paginated results/next responses.
 */
export async function fetchAllPages(url, params = {}) {
  if (typeof url !== "string" || !url.trim()) {
    throw new TypeError("A valid API endpoint URL is required.");
  }

  const items = [];
  const visitedUrls = new Set();
  let nextUrl = url;
  let firstRequest = true;

  while (nextUrl) {
    if (visitedUrls.has(nextUrl)) {
      throw new Error("Pagination stopped because a page URL repeated.");
    }

    visitedUrls.add(nextUrl);

    const response = await apiClient.get(nextUrl, {
      ...(firstRequest ? { params } : {}),
    });

    const data = response.data;

    if (Array.isArray(data)) {
      return [...items, ...data];
    }

    if (!data || !Array.isArray(data.results)) {
      throw new Error(
        "Unexpected API response: expected an array or paginated results.",
      );
    }

    items.push(...data.results);

    if (data.next == null) {
      break;
    }

    if (typeof data.next !== "string" || !data.next.trim()) {
      throw new Error("Invalid pagination URL returned by the API.");
    }

    nextUrl = data.next;
    firstRequest = false;
  }

  return items;
}
