import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  getCurrentUser,
  loginUser,
  logoutUser,
} from "../api/auth";

import { AuthContext } from "./authContextDefinition";

const ACCESS_TOKEN_KEY = "rentnest_access_token";
const REFRESH_TOKEN_KEY = "rentnest_refresh_token";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = Boolean(user);

  const clearAuthentication = useCallback(() => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    setUser(null);
  }, []);

  useEffect(() => {
    let isMounted = true;

    const initializeAuthentication = async () => {
      const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);

      if (!accessToken) {
        if (isMounted) {
          setIsLoading(false);
        }
        return;
      }

      try {
        const currentUser = await getCurrentUser();

        if (isMounted) {
          setUser(currentUser);
        }
      } catch {
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);

        if (isMounted) {
          setUser(null);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    initializeAuthentication();

    return () => {
      isMounted = false;
    };
  }, []);

  const login = async (credentials) => {
    const data = await loginUser(credentials);

    localStorage.setItem(
      ACCESS_TOKEN_KEY,
      data.access,
    );

    localStorage.setItem(
      REFRESH_TOKEN_KEY,
      data.refresh,
    );

    const currentUser = await getCurrentUser();

    setUser(currentUser);

    return currentUser;
  };

  const logout = async () => {
    const refreshToken = localStorage.getItem(
      REFRESH_TOKEN_KEY,
    );

    try {
      if (refreshToken) {
        await logoutUser(refreshToken);
      }
    } finally {
      clearAuthentication();
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}