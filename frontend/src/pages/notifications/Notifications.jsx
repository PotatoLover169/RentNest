import { useEffect, useState } from "react";

import { getNotifications } from "../../api/notifications";

function formatNotificationType(type) {
  if (!type) {
    return "Notification";
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

  return parsedDate.toLocaleString();
}

function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadNotifications = async () => {
      try {
        setIsLoading(true);
        setError("");

        const data = await getNotifications();

        setNotifications(data.results ?? data);
      } catch (requestError) {
        setError(
          requestError?.response?.data?.message ||
            requestError?.response?.data?.detail ||
            "Unable to load notifications.",
        );
      } finally {
        setIsLoading(false);
      }
    };

    loadNotifications();
  }, []);

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <section>
        <p className="text-sm font-semibold uppercase tracking-wider text-slate-500">
          Activity
        </p>

        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
          Notifications
        </h1>

        <p className="mt-2 max-w-2xl text-slate-500">
          Stay up to date with important activity and updates
          from your RentNest account.
        </p>
      </section>

      {isLoading && (
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm text-slate-500">
            Loading notifications...
          </p>
        </section>
      )}

      {!isLoading && error && (
        <section className="rounded-xl border border-red-200 bg-red-50 p-6">
          <h2 className="text-lg font-semibold text-red-900">
            Unable to load notifications
          </h2>

          <p className="mt-2 text-sm text-red-700">
            {error}
          </p>
        </section>
      )}

      {!isLoading &&
        !error &&
        notifications.length === 0 && (
          <section className="rounded-xl border border-slate-200 bg-white p-10 text-center shadow-sm">
            <h2 className="text-lg font-semibold text-slate-950">
              No notifications
            </h2>

            <p className="mt-2 text-sm text-slate-500">
              You're all caught up. New notifications will
              appear here.
            </p>
          </section>
        )}

      {!isLoading &&
        !error &&
        notifications.length > 0 && (
          <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
            <div className="divide-y divide-slate-200">
              {notifications.map((notification) => {
                const isRead =
                  notification.is_read ??
                  notification.read ??
                  false;

                return (
                  <article
                    key={notification.id}
                    className={[
                      "p-5 transition",
                      isRead
                        ? "bg-white"
                        : "bg-slate-50",
                    ].join(" ")}
                  >
                    <div className="flex gap-4">
                      <div
                        className={[
                          "mt-1 h-2.5 w-2.5 shrink-0 rounded-full",
                          isRead
                            ? "bg-slate-300"
                            : "bg-slate-900",
                        ].join(" ")}
                        aria-hidden="true"
                      />

                      <div className="min-w-0 flex-1">
                        <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                          <div>
                            <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                              {formatNotificationType(
                                notification.notification_type ||
                                  notification.type,
                              )}
                            </p>

                            <h2 className="mt-1 font-semibold text-slate-950">
                              {notification.title ||
                                "RentNest Notification"}
                            </h2>
                          </div>

                          <time className="shrink-0 text-xs text-slate-400">
                            {formatDate(
                              notification.created_at ||
                                notification.timestamp,
                            )}
                          </time>
                        </div>

                        <p className="mt-2 text-sm leading-6 text-slate-600">
                          {notification.message ||
                            notification.body ||
                            "You have a new RentNest notification."}
                        </p>

                        {!isRead && (
                          <span className="mt-3 inline-flex rounded-full bg-slate-900 px-2.5 py-1 text-xs font-semibold text-white">
                            Unread
                          </span>
                        )}
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
          </section>
        )}
    </div>
  );
}

export default Notifications;