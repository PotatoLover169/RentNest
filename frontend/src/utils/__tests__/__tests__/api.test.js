
import { describe, expect, it } from "vitest";
import { getPagination, getResults } from "../api";

describe("getResults", () => {
  it("returns an array unchanged", () => {
    const data = [{ id: 1 }, { id: 2 }];

    expect(getResults(data)).toEqual(data);
  });

  it("returns results from a paginated response", () => {
    expect(getResults({ count: 2, results: [{ id: 1 }, { id: 2 }] }))
      .toEqual([{ id: 1 }, { id: 2 }]);
  });

  it("returns an empty array for missing or unsupported results", () => {
    expect(getResults(null)).toEqual([]);
    expect(getResults(undefined)).toEqual([]);
    expect(getResults({ count: 0 })).toEqual([]);
  });
});

describe("getPagination", () => {
  it("returns pagination metadata from a paginated response", () => {
    expect(
      getPagination({
        count: 25,
        next: "https://example.test/api/items/?page=2",
        previous: null,
      }),
    ).toEqual({
      count: 25,
      next: "https://example.test/api/items/?page=2",
      previous: null,
    });
  });

  it("handles an unpaginated array", () => {
    expect(getPagination([{ id: 1 }, { id: 2 }])).toEqual({
      count: 2,
      next: null,
      previous: null,
    });
  });

  it("uses safe defaults for missing metadata", () => {
    expect(getPagination({ results: [] })).toEqual({
      count: 0,
      next: null,
      previous: null,
    });

    expect(getPagination(null)).toEqual({
      count: 0,
      next: null,
      previous: null,
    });
  });
});
