import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { createMaintenanceRequest } from "../../api/maintenance";
import { getTenancies } from "../../api/tenancies";

function MaintenanceForm() {
  const navigate = useNavigate();

  const [tenancies, setTenancies] = useState([]);
  const [selectedTenancyId, setSelectedTenancyId] =
    useState("");

  const [title, setTitle] = useState("");
  const [description, setDescription] =
    useState("");
  const [priority, setPriority] =
    useState("MEDIUM");

  const [isLoading, setIsLoading] =
    useState(true);
  const [isSubmitting, setIsSubmitting] =
    useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let isActive = true;

    const loadTenancies = async () => {
      try {
        setIsLoading(true);
        setError("");

        const data = await getTenancies();

        const results = Array.isArray(data)
          ? data
          : Array.isArray(data?.results)
            ? data.results
            : [];

        const activeTenancies =
          results.filter(
            (tenancy) =>
              tenancy.status === "ACTIVE",
          );

        if (isActive) {
          setTenancies(activeTenancies);

          if (activeTenancies.length === 1) {
            setSelectedTenancyId(
              String(activeTenancies[0].id),
            );
          }
        }
      } catch (requestError) {
        if (isActive) {
          setError(
            requestError?.response?.data?.detail ||
              requestError?.response?.data?.message ||
              "Unable to load your rental information.",
          );
        }
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    };

    loadTenancies();

    return () => {
      isActive = false;
    };
  }, []);

  const selectedTenancy =
    tenancies.find(
      (tenancy) =>
        String(tenancy.id) ===
        String(selectedTenancyId),
    ) || null;

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!selectedTenancy) {
      setError(
        "Please select your rental unit.",
      );
      return;
    }

    if (!title.trim()) {
      setError("Please enter an issue title.");
      return;
    }

    if (!description.trim()) {
      setError(
        "Please describe the maintenance issue.",
      );
      return;
    }

    try {
      setIsSubmitting(true);
      setError("");

      const request =
        await createMaintenanceRequest({
          unit: selectedTenancy.unit,
          title: title.trim(),
          description: description.trim(),
          priority,
        });

      navigate(
        `/maintenance/${request.id}`,
      );
    } catch (requestError) {
      const responseData =
        requestError?.response?.data;

      setError(
        responseData?.detail ||
          responseData?.unit?.[0] ||
          responseData?.title?.[0] ||
          responseData?.description?.[0] ||
          "Unable to submit your maintenance request.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600" />

          <p className="mt-4 text-sm text-slate-500">
            Loading your rental information...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <section>
        <Link
          to="/maintenance"
          className="text-sm font-semibold text-blue-600 transition hover:text-blue-700"
        >
          ← Back to Maintenance
        </Link>

        <p className="mt-6 text-sm font-semibold uppercase tracking-wider text-slate-500">
          Tenant Support
        </p>

        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
          Report a Maintenance Issue
        </h1>

        <p className="mt-2 text-sm leading-6 text-slate-500">
          Tell your property manager what needs attention
          in your rental.
        </p>
      </section>

      {tenancies.length === 0 ? (
        <section className="rounded-2xl border border-amber-200 bg-amber-50 p-6">
          <h2 className="text-lg font-bold text-amber-900">
            No Active Rental
          </h2>

          <p className="mt-2 text-sm leading-6 text-amber-800">
            You need an active tenancy before you can
            submit a maintenance request.
          </p>
        </section>
      ) : (
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          {error && (
            <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm font-medium text-red-700">
              {error}
            </div>
          )}

          <form
            onSubmit={handleSubmit}
            className="space-y-6"
          >
            <div>
              <label
                htmlFor="tenancy"
                className="block text-sm font-semibold text-slate-800"
              >
                Rental Unit
              </label>

              <select
                id="tenancy"
                value={selectedTenancyId}
                onChange={(event) =>
                  setSelectedTenancyId(
                    event.target.value,
                  )
                }
                className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                required
              >
                <option value="">
                  Select your rental
                </option>

                {tenancies.map(
                  (tenancy) => (
                    <option
                      key={tenancy.id}
                      value={tenancy.id}
                    >
                      {tenancy.property_name ||
                        "Property"}{" "}
                      — Unit{" "}
                      {tenancy.unit_number ||
                        tenancy.unit}
                    </option>
                  ),
                )}
              </select>

              {selectedTenancy && (
                <p className="mt-2 text-xs text-slate-500">
                  Managed by{" "}
                  {selectedTenancy.manager_name ||
                    selectedTenancy.manager_email ||
                    "your property manager"}
                </p>
              )}
            </div>

            <div>
              <label
                htmlFor="title"
                className="block text-sm font-semibold text-slate-800"
              >
                Issue Title
              </label>

              <input
                id="title"
                type="text"
                value={title}
                onChange={(event) =>
                  setTitle(event.target.value)
                }
                placeholder="e.g. Air conditioner not working"
                className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                required
              />
            </div>

            <div>
              <label
                htmlFor="priority"
                className="block text-sm font-semibold text-slate-800"
              >
                Priority
              </label>

              <select
                id="priority"
                value={priority}
                onChange={(event) =>
                  setPriority(event.target.value)
                }
                className="mt-2 w-full rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              >
                <option value="LOW">
                  Low
                </option>

                <option value="MEDIUM">
                  Medium
                </option>

                <option value="HIGH">
                  High
                </option>

                <option value="URGENT">
                  Urgent
                </option>
              </select>
            </div>

            <div>
              <label
                htmlFor="description"
                className="block text-sm font-semibold text-slate-800"
              >
                Description
              </label>

              <textarea
                id="description"
                rows={6}
                value={description}
                onChange={(event) =>
                  setDescription(
                    event.target.value,
                  )
                }
                placeholder="Describe what is wrong..."
                className="mt-2 w-full resize-y rounded-xl border border-slate-200 bg-white px-3 py-3 text-sm leading-6 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                required
              />
            </div>

            <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
              <Link
                to="/maintenance"
                className="inline-flex items-center justify-center rounded-xl border border-slate-200 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
              >
                Cancel
              </Link>

              <button
                type="submit"
                disabled={isSubmitting}
                className="inline-flex items-center justify-center rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isSubmitting
                  ? "Submitting..."
                  : "Submit Request"}
              </button>
            </div>
          </form>
        </section>
      )}
    </div>
  );
}

export default MaintenanceForm;