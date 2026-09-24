import { useEffect, useState } from "react";

import { getProperties } from "../../api/properties";

function Properties() {
  const [properties, setProperties] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadProperties = async () => {
      try {
        setIsLoading(true);
        setError("");

        const data = await getProperties();

        setProperties(data.results ?? data);
      } catch (requestError) {
        setError(
          requestError?.response?.data?.message ||
            "Unable to load properties.",
        );
      } finally {
        setIsLoading(false);
      }
    };

    loadProperties();
  }, []);

  return (
    <div className="mx-auto max-w-7xl space-y-8">
      <section>
        <p className="text-sm font-semibold uppercase tracking-wider text-slate-500">
          Management
        </p>

        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
          Properties
        </h1>

        <p className="mt-2 max-w-2xl text-slate-500">
          Manage your rental properties and view their current
          information.
        </p>
      </section>

      {isLoading && (
        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm text-slate-500">
            Loading properties...
          </p>
        </section>
      )}

      {!isLoading && error && (
        <section className="rounded-xl border border-red-200 bg-red-50 p-6">
          <h2 className="text-lg font-semibold text-red-900">
            Unable to load properties
          </h2>

          <p className="mt-2 text-sm text-red-700">
            {error}
          </p>
        </section>
      )}

      {!isLoading && !error && properties.length === 0 && (
        <section className="rounded-xl border border-slate-200 bg-white p-10 text-center shadow-sm">
          <h2 className="text-lg font-semibold text-slate-950">
            No properties yet
          </h2>

          <p className="mt-2 text-sm text-slate-500">
            Properties assigned to your account will appear here.
          </p>
        </section>
      )}

      {!isLoading && !error && properties.length > 0 && (
        <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Property
                  </th>

                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Address
                  </th>

                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                    Status
                  </th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-200 bg-white">
                {properties.map((property) => (
                  <tr
                    key={property.id}
                    className="transition hover:bg-slate-50"
                  >
                    <td className="whitespace-nowrap px-6 py-4">
                      <p className="font-medium text-slate-900">
                        {property.name}
                      </p>
                    </td>

                    <td className="px-6 py-4 text-sm text-slate-500">
                      {property.address || "—"}
                    </td>

                    <td className="px-6 py-4">
                      <span className="inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                        {property.status || "Active"}
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

export default Properties;