import { useEffect, useState } from "react";

import { getMaintenanceRequests } from "../../api/maintenance";

function formatStatus(status) {
  if (!status) {
    return "Pending";
  }

  return status
    .toLowerCase()
    .split("_")
    .map(
      (word) =>
        word.charAt(0).toUpperCase() + word.slice(1),
    )
    .join(" ");
}

function Maintenance() {
  const [requests, setRequests] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadRequests = async () => {
      try {
        setIsLoading(true);
        setError("");

        const data = await getMaintenanceRequests();

        setRequests(data.results ?? data);
      } catch (requestError) {
        setError(
          requestError?.response?.data?.message ||
            requestError?.response?.data?.detail ||
            "Unable to load maintenance requests.",
        );
      } finally {
        setIsLoading(false);
      }
    };

    loadRequests();
  }, []);

  return (
    <div className="mx-auto max-w-7xl space-y-8">
      <section>
        <p className="text-sm font-semibold uppercase tracking-wider text-slate-500">
          Management
        </p>

        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
          Maintenance
        </h1>

        <p className="mt-2 max-w-2xl text-slate-500">
          Track maintenance requests and monitor their current
          status.
        </p>
      </section>

      {isLoading && (
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm text-slate-500">
            Loading maintenance requests...
          </p>
        </section>
      )}

      {!isLoading && error && (
        <section className="rounded-xl border border-red-200 bg-red-50 p-6">
          <h2 className="text-lg font-semibold text-red-900">
            Unable to load maintenance requests
          </h2>

          <p className="mt-2 text-sm text-red-700">
            {error}
          </p>
        </section>
      )}

      {!isLoading && !error && requests.length === 0 && (
        <section className="rounded-xl border border-slate-200 bg-white p-10 text-center shadow-sm">
          <h2 className="text-lg font-semibold text-slate-950">
            No maintenance requests yet
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            Maintenance requests associated with your account
            will appear here.
          </p>
        </section>
      )}

      {!isLoading && !error && requests.length > 0 && (
        <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Request
                  </th>

                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Unit
                  </th>

                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Priority
                  </th>

                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Status
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-200 bg-white">
                {requests.map((request) => (
                  <tr
                    key={request.id}
                    className="transition hover:bg-slate-50"
                  >
                    <td className="px-6 py-4">
                      <p className="font-medium text-slate-900">
                        {request.title ||
                          request.description ||
                          `Request #${request.id}`}
                      </p>
                    </td>

                    <td className="px-6 py-4 text-sm text-slate-500">
                      {request.unit_number ||
                        request.unit?.unit_number ||
                        request.unit?.name ||
                        "—"}
                    </td>

                    <td className="px-6 py-4 text-sm text-slate-500">
                      {formatStatus(request.priority)}
                    </td>

                    <td className="px-6 py-4">
                      <span className="inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                        {formatStatus(request.status)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}

export default Maintenance;