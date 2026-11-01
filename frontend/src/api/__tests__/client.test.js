import { afterEach, describe, expect, it, vi } from "vitest";
import axios from "axios";

const { createMock, requestUseMock } = vi.hoisted(() => ({
  createMock: vi.fn(),
  requestUseMock: vi.fn(),
}));

vi.mock("axios", () => ({
  default: {
    create: createMock,
  },
}));

describe("API client configuration", () => {
  afterEach(() => {
    vi.resetModules();
    vi.unstubAllEnvs();
    localStorage.clear();
    createMock.mockReset();
    requestUseMock.mockReset();
  });

  async function loadClient(baseURL) {
    vi.stubEnv("VITE_API_BASE_URL", baseURL);

    const client = {
      interceptors: {
        request: {
          use: requestUseMock,
        },
      },
    };

    createMock.mockReturnValue(client);

    const module = await import("../client");

    return {
      client: module.default,
      config: createMock.mock.calls[0][0],
      interceptor: requestUseMock.mock.calls[0][0],
      errorInterceptor: requestUseMock.mock.calls[0][1],
    };
  }

  it("creates the client with the default API URL", async () => {
    const { config } = await loadClient("");

    expect(config.baseURL).toBe("http://127.0.0.1:8000/api");
  });

  it("uses the configured API base URL", async () => {
    const { config } = await loadClient(
      "https://api.example.com/api",
    );

    expect(config.baseURL).toBe("https://api.example.com/api");
  });

  it("removes trailing slashes from the configured URL", async () => {
    const { config } = await loadClient(
      "https://api.example.com/api///",
    );

    expect(config.baseURL).toBe("https://api.example.com/api");
  });

  it("uses a 15-second request timeout", async () => {
    const { config } = await loadClient("");

    expect(config.timeout).toBe(15000);
  });

  it("sets the JSON content-type header", async () => {
    const { config } = await loadClient("");

    expect(config.headers).toEqual({
      "Content-Type": "application/json",
    });
  });

  it("adds the bearer token when an access token exists", async () => {
    localStorage.setItem(
      "rentnest_access_token",
      "test-access-token",
    );

    const { interceptor } = await loadClient("");

    const requestConfig = {
      headers: {},
    };

    const result = interceptor(requestConfig);

    expect(result.headers.Authorization).toBe(
      "Bearer test-access-token",
    );
  });

  it("does not add authorization when no access token exists", async () => {
    const { interceptor } = await loadClient("");

    const requestConfig = {
      headers: {},
    };

    const result = interceptor(requestConfig);

    expect(result.headers).not.toHaveProperty("Authorization");
  });

  it("preserves other request configuration values", async () => {
    localStorage.setItem(
      "rentnest_access_token",
      "test-access-token",
    );

    const { interceptor } = await loadClient("");

    const requestConfig = {
      url: "/properties/",
      method: "get",
      headers: {
        Accept: "application/json",
      },
    };

    const result = interceptor(requestConfig);

    expect(result.url).toBe("/properties/");
    expect(result.method).toBe("get");
    expect(result.headers.Accept).toBe("application/json");
    expect(result.headers.Authorization).toBe(
      "Bearer test-access-token",
    );
  });

  it("rejects request interceptor errors", async () => {
    const { errorInterceptor } = await loadClient("");

    const error = new Error("Request configuration failed");

    await expect(errorInterceptor(error)).rejects.toBe(error);
  });

  it("creates an Axios instance", async () => {
    const { client } = await loadClient("");

    expect(axios.create).toHaveBeenCalledTimes(1);
    expect(client).toBeDefined();
  });
});