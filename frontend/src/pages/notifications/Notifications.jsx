import { useCallback, useEffect, useState } from "react";

import {
  deleteNotification,
  getNotifications,
  markAllNotificationsRead,
  markNotificationRead,
  markNotificationUnread,
} from "../../api/notifications";
import {
  Badge,
  Button,
  Card,
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeader,
} from "../../components/ui";
import { getPagination, getResults } from "../../utils/api";

function formatNotificationType(type) {
  if (!type) {
    return "General";
  }

  return type
    .toLowerCase()
    .split("_")
    .map(
      (word) =>
        word.charAt(0).toUpperCase() + word.slice(1),
    )
    .join(" ");
}

function formatDate(date) {
  if (!date) {
    return "—";
  }

  const parsedDate = new Date(date);

  if (Number.isNaN(parsedDate.getTime())) {
    return date;
  }

  return parsedDate.toLocaleString("en-PH", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function getErrorMessage(error) {
  const data = error?.response?.data;

  if (data?.detail) {
    return Array.isArray(data.detail)
      ? data.detail.join(" ")
      : data.detail;
  }

  if (data?.message) {
    return data.message;
  }

  return "Something went wrong. Please try again.";
}

function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null,
  });

  const [isLoading, setIsLoading] = useState(true);
  const [isActionLoading, setIsActionLoading] = useState(false);
  const [error, setError] = useState("");
  const [actionError, setActionError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const loadNotifications = useCallback(async () => {
    try {
      setIsLoading(true);
      setError("");

      const data = await getNotifications();

      setNotifications(getResults(data));
      setPagination(getPagination(data));
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // Fetch notifications when the page loads.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadNotifications();
  }, [loadNotifications]);

  const unreadCount = notifications.filter(
    (notification) => !notification.is_read,
  ).length;

  const handleMarkRead = async (id) => {
    try {
      setIsActionLoading(true);
      setActionError("");
      setSuccessMessage("");

      const updatedNotification =
        await markNotificationRead(id);

      setNotifications((current) =>
        current.map((notification) =>
          notification.id === id
            ? updatedNotification
            : notification,
        ),
      );

      setSuccessMessage("Notification marked as read.");
    } catch (requestError) {
      setActionError(getErrorMessage(requestError));
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleMarkUnread = async (id) => {
    try {
      setIsActionLoading(true);
      setActionError("");
      setSuccessMessage("");

      const updatedNotification =
        await markNotificationUnread(id);

      setNotifications((current) =>
        current.map((notification) =>
          notification.id === id
            ? updatedNotification
            : notification,
        ),
      );

      setSuccessMessage("Notification marked as unread.");
    } catch (requestError) {
      setActionError(getErrorMessage(requestError));
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleMarkAllRead = async () => {
    if (unreadCount === 0) {
      return;
    }

    try {
      setIsActionLoading(true);
      setActionError("");
      setSuccessMessage("");

      await markAllNotificationsRead();

      setNotifications((current) =>
        current.map((notification) => ({
          ...notification,
          is_read: true,
        })),
      );

      setSuccessMessage(
        "All notifications marked as read.",
      );
    } catch (requestError) {
      setActionError(getErrorMessage(requestError));
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleDelete = async (notification) => {
    const confirmed = window.confirm(
      `Delete "${notification.title}"? This action cannot be undone.`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setIsActionLoading(true);
      setActionError("");
      setSuccessMessage("");

      await deleteNotification(notification.id);

      setNotifications((current) =>
        current.filter(
          (item) => item.id !== notification.id,
        ),
      );

      setPagination((current) => ({
        ...current,
        count: Math.max(0, current.count - 1),
      }));

      setSuccessMessage("Notification deleted.");
    } catch (requestError) {
      setActionError(getErrorMessage(requestError));
    } finally {
      setIsActionLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <PageHeader
        eyebrow="Activity"
        title="Notifications"
        description="Stay up to date with important activity and updates from your RentNest account."
        action={
          <div className="flex flex-wrap gap-3">
            <Button
              variant="secondary"
              onClick={loadNotifications}
              disabled={isLoading || isActionLoading}
            >
              Refresh
            </Button>

            <Button
              onClick={handleMarkAllRead}
              disabled={
                isLoading ||
                isActionLoading ||
                unreadCount === 0
              }
            >
              Mark All Read
            </Button>
          </div>
        }
      />

      <div className="grid gap-4 sm:grid-cols-3">
        <Card className="p-5">
          <p className="text-sm font-medium text-slate-500">
            Total Notifications
          </p>

          <p className="mt-2 text-3xl font-bold text-slate-950">
            {pagination.count}
          </p>
        </Card>

        <Card className="p-5">
          <p className="text-sm font-medium text-slate-500">
            Unread
          </p>

          <p className="mt-2 text-3xl font-bold text-slate-950">
            {unreadCount}
          </p>
        </Card>

        <Card className="p-5">
          <p className="text-sm font-medium text-slate-500">
            Read
          </p>

          <p className="mt-2 text-3xl font-bold text-slate-950">
            {Math.max(0, notifications.length - unreadCount)}
          </p>
        </Card>
      </div>

      {actionError && (
        <div
          role="alert"
          className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          {actionError}
        </div>
      )}

      {successMessage && (
        <div
          role="status"
          className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700"
        >
          {successMessage}
        </div>
      )}

      {isLoading && (
        <LoadingState message="Loading notifications..." />
      )}

      {!isLoading && error && (
        <ErrorState
          title="Unable to load notifications"
          message={error}
          action={
            <Button
              variant="secondary"
              onClick={loadNotifications}
            >
              Try Again
            </Button>
          }
        />
      )}

      {!isLoading &&
        !error &&
        notifications.length === 0 && (
          <EmptyState
            title="You're all caught up"
            description="New notifications about your RentNest account will appear here."
          />
        )}

      {!isLoading &&
        !error &&
        notifications.length > 0 && (
          <Card className="overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
              <div>
                <h2 className="font-semibold text-slate-950">
                  Recent Activity
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  {notifications.length} displayed
                </p>
              </div>

              {unreadCount > 0 && (
                <Badge variant="info">
                  {unreadCount} unread
                </Badge>
              )}
            </div>

            <div className="divide-y divide-slate-200">
              {notifications.map((notification) => {
                const isRead = notification.is_read;

                return (
                  <article
                    key={notification.id}
                    className={[
                      "p-5 transition sm:p-6",
                      isRead ? "bg-white" : "bg-slate-50",
                    ].join(" ")}
                  >
                    <div className="flex gap-4">
                      <div
                        className={[
                          "mt-2 h-2.5 w-2.5 shrink-0 rounded-full",
                          isRead
                            ? "bg-slate-300"
                            : "bg-blue-600",
                        ].join(" ")}
                        aria-hidden="true"
                      />

                      <div className="min-w-0 flex-1">
                        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                          <div className="min-w-0">
                            <div className="flex flex-wrap items-center gap-2">
                              <Badge variant="default">
                                {formatNotificationType(
                                  notification.notification_type,
                                )}
                              </Badge>

                              {!isRead && (
                                <Badge variant="info">
                                  Unread
                                </Badge>
                              )}
                            </div>

                            <h3 className="mt-2 font-semibold text-slate-950">
                              {notification.title}
                            </h3>
                          </div>

                          <time
                            dateTime={notification.created_at}
                            className="shrink-0 text-xs text-slate-400"
                          >
                            {formatDate(notification.created_at)}
                          </time>
                        </div>

                        <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-600">
                          {notification.message}
                        </p>

                        {notification.read_at && (
                          <p className="mt-2 text-xs text-slate-400">
                            Read {formatDate(notification.read_at)}
                          </p>
                        )}

                        <div className="mt-4 flex flex-wrap gap-2">
                          {isRead ? (
                            <Button
                              variant="secondary"
                              size="sm"
                              disabled={isActionLoading}
                              onClick={() =>
                                handleMarkUnread(notification.id)
                              }
                            >
                              Mark Unread
                            </Button>
                          ) : (
                            <Button
                              variant="secondary"
                              size="sm"
                              disabled={isActionLoading}
                              onClick={() =>
                                handleMarkRead(notification.id)
                              }
                            >
                              Mark as Read
                            </Button>
                          )}

                          <Button
                            variant="ghost"
                            size="sm"
                            disabled={isActionLoading}
                            onClick={() =>
                              handleDelete(notification)
                            }
                          >
                            Delete
                          </Button>
                        </div>
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
          </Card>
        )}
    </div>
  );
}

export default Notifications;