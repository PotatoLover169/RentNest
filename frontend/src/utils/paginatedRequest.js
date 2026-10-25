
import apiClient from "../api/client";

/**
 * Fetch all pages from a Django REST Framework paginated endpoint.
 * Supports plain arrays and responses containing results/next.
 */
export async function fetchAllPages(url, params = {}) {
  const items = [];
  let nextUrl = url;
  let firstRequest = true;

  while (nextUrl) {
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
    nextUrl = data.next;
    firstRequest = false;
  }

  return items;
}
