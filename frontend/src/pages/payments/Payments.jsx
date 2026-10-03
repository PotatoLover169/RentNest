import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getPayments } from "../../api/payments";

const STATUS_OPTIONS = [
  "ALL",
  "PENDING",
  "PAID",
  "FAILED",
  "REFUNDED",
  "CANCELLED",
];

function normalizeStatus(status) {
  return String(status || "PENDING").toUpperCase();
}

function formatStatus(status) {
  return normalizeStatus(status)
    .toLowerCase()
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function getStatusStyles(status) {
  const styles = {
    PAID: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
    PENDING: "bg-amber-50 text-amber-700 ring-amber-600/20",
    FAILED: "bg-red-50 text-red-700 ring-red-600/20",
    REFUNDED: "bg-blue-50 text-blue-700 ring-blue-600/20",
    CANCELLED: "bg-slate-100 text-slate-600 ring-slate-500/20",
  };

  return (
    styles[normalizeStatus(status)] ||
    "bg-slate-100 text-slate-600 ring-slate-500/20"
  );
}

function formatCurrency(amount) {
  if (amount == null || amount === "") {
    return "—";
  }

  const numericAmount = Number(amount);

  if (!Number.isFinite(numericAmount)) {
    return "—";
  }

  return new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
    maximumFractionDigits: 2,
  }).format(numericAmount);
}

function formatDate(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return new Intl.DateTimeFormat("en-PH", {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(date);
}

function getPaymentReference(payment) {
  return (
    payment.reference_number ||
    payment.payment_reference ||
    payment.reference ||
    `Payment #${payment.id}`
  );
}

function getPaymentDate(payment) {
  return payment.payment_date || payment.due_date || payment.created_at;
}

function SummaryCard({ label, value, description, accent }) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-slate-500">{label}</p>
          <p className="mt-3 text-2xl font-bold tracking-tight text-slate-950">
            {value}
          </p>
          <p className="mt-1 text-xs text-slate-500">{description}</p>
        </div>

        <span
          className={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full ${accent}`}
          aria-hidden="true"
        />
      </div>
    </article>
  );
}

function Payments() {
  const [payments, setPayments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null,
  });

  const loadPayments = useCallback(async () => {
    try {
      setIsLoading(true);
      setError("");

      const data = await getPayments();
      const results = Array.isArray(data) ? data : data?.results ?? [];

      setPayments(results);
      setPagination({
        count: data?.count ?? results.length,
        next: data?.next ?? null,
        previous: data?.previous ?? null,
      });
    } catch (requestError) {
      setError(
        requestError?.response?.data?.message ||
          requestError?.response?.data?.detail ||
          "Unable to load payments. Please try again.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // Load payment records when the page mounts.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadPayments();
  }, [loadPayments]);

  const summary = useMemo(() => {
    return payments.reduce(
      (totals, payment) => {
        const status = normalizeStatus(payment.status);
        const amount = Number(payment.amount) || 0;

        totals.total += 1;

        if (status === "PAID") {
          totals.paid += 1;
          totals.paidAmount += amount;
        } else if (status === "PENDING") {
          totals.pending += 1;
        } else if (status === "FAILED") {
          totals.failed += 1;
        }

        return totals;
      },
      {
        total: 0,
        paid: 0,
        pending: 0,
        failed: 0,
        paidAmount: 0,
      },
    );
  }, [payments]);

  const filteredPayments = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase();

    return payments.filter((payment) => {
      const matchesStatus =
        statusFilter === "ALL" ||
        normalizeStatus(payment.status) === statusFilter;

      const searchableText = [
        getPaymentReference(payment),
        payment.id,
        payment.payment_method,
        payment.reference_number,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      const matchesSearch =
        !normalizedSearch || searchableText.includes(normalizedSearch);

      return matchesStatus && matchesSearch;
    });
  }, [payments, search, statusFilter]);

  return (
    <div className="mx-auto max-w-7xl space-y-8 pb-10">
      <section className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-blue-600">
            Financial Management
          </p>

          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
            Payments
          </h1>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
            Monitor rental payment records, review payment statuses, and keep
            track of collected payments.
          </p>
        </div>

        <button
          type="button"
          onClick={loadPayments}
          disabled={isLoading}
          className="inline-flex items-center justify-center rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isLoading ? "Refreshing..." : "Refresh"}
        </button>
      </section>

      {!isLoading && !error && (
        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <SummaryCard
            label="Total Payments"
            value={pagination.count.toLocaleString("en-PH")}
            description="Records available in the API"
            accent="bg-blue-500"
          />

          <SummaryCard
            label="Paid"
            value={summary.paid.toLocaleString("en-PH")}
            description={formatCurrency(summary.paidAmount) + " on this page"}
            accent="bg-emerald-500"
          />

          <SummaryCard
            label="Pending"
            value={summary.pending.toLocaleString("en-PH")}
            description="Awaiting payment"
            accent="bg-amber-500"
          />

          <SummaryCard
            label="Failed"
            value={summary.failed.toLocaleString("en-PH")}
            description="Payment attempts marked failed"
            accent="bg-red-500"
          />
        </section>
      )}

      <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="flex flex-col gap-4 border-b border-slate-200 p-5 sm:p-6">
          <div>
            <h2 className="text-lg font-semibold text-slate-950">
              Payment Records
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              Search and filter the available payment records.
            </p>
          </div>

          <div className="flex flex-col gap-3 md:flex-row">
            <div className="relative min-w-0 flex-1">
              <label htmlFor="payment-search" className="sr-only">
                Search payments
              </label>

              <input
                id="payment-search"
                type="search"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search reference, ID, or method..."
                className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-500/10"
              />
            </div>

            <div className="w-full md:w-52">
              <label htmlFor="payment-status" className="sr-only">
                Filter by status
              </label>

              <select
                id="payment-status"
                value={statusFilter}
                onChange={(event) => setStatusFilter(event.target.value)}
                className="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10"
              >
                {STATUS_OPTIONS.map((status) => (
                  <option key={status} value={status}>
                    {status === "ALL" ? "All statuses" : formatStatus(status)}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {isLoading && (
          <div className="p-10 text-center">
            <div
              className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-slate-200 border-t-blue-600"
              role="status"
              aria-label="Loading payments"
            />
            <p className="mt-4 text-sm text-slate-500">
              Loading payment records...
            </p>
          </div>
        )}

        {!isLoading && error && (
          <div className="p-6 sm:p-8">
            <div className="rounded-xl border border-red-200 bg-red-50 p-5">
              <h3 className="font-semibold text-red-900">
                Unable to load payments
              </h3>
              <p className="mt-2 text-sm text-red-700">{error}</p>

              <button
                type="button"
                onClick={loadPayments}
                className="mt-4 rounded-lg bg-red-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-red-800"
              >
                Try again
              </button>
            </div>
          </div>
        )}

        {!isLoading && !error && filteredPayments.length === 0 && (
          <div className="p-10 text-center sm:p-14">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-500">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.7"
                className="h-6 w-6"
                aria-hidden="true"
              >
                <rect x="3" y="5" width="18" height="14" rx="2" />
                <path d="M3 10h18M7 15h3" />
              </svg>
            </div>

            <h3 className="mt-4 text-base font-semibold text-slate-900">
              {payments.length === 0
                ? "No payments yet"
                : "No matching payments"}
            </h3>

            <p className="mx-auto mt-2 max-w-sm text-sm leading-6 text-slate-500">
              {payments.length === 0
                ? "Payment records associated with your account will appear here."
                : "Try adjusting your search term or selecting a different payment status."}
            </p>

            {(search || statusFilter !== "ALL") && (
              <button
                type="button"
                onClick={() => {
                  setSearch("");
                  setStatusFilter("ALL");
                }}
                className="mt-4 text-sm font-semibold text-blue-600 hover:text-blue-700"
              >
                Clear filters
              </button>
            )}
          </div>
        )}

        {!isLoading && !error && filteredPayments.length > 0 && (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200">
                <thead className="bg-slate-50/80">
                  <tr>
                    {[
                      "Payment",
                      "Method",
                      "Amount",
                      "Payment Date",
                      "Status",
                    ].map((heading) => (
                      <th
                        key={heading}
                        scope="col"
                        className="whitespace-nowrap px-5 py-3.5 text-left text-xs font-semibold uppercase tracking-wider text-slate-500 sm:px-6"
                      >
                        {heading}
                      </th>
                    ))}
                  </tr>
                </thead>

                <tbody className="divide-y divide-slate-100">
                  {filteredPayments.map((payment) => (
                    <tr
                      key={payment.id}
                      className="transition hover:bg-slate-50/80"
                    >
                      <td className="whitespace-nowrap px-5 py-4 sm:px-6">
                        <Link
                          to={`/payments/${payment.id}`}
                          className="text-sm font-semibold text-blue-600 transition hover:text-blue-800 hover:underline"
                        >
                          {getPaymentReference(payment)}
                        </Link>
                        <p className="mt-1 text-xs text-slate-500">
                          ID: {payment.id}
                        </p>
                      </td>

                      <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-600 sm:px-6">
                        {payment.payment_method
                          ? formatStatus(payment.payment_method)
                          : "—"}
                      </td>

                      <td className="whitespace-nowrap px-5 py-4 text-sm font-semibold text-slate-900 sm:px-6">
                        {formatCurrency(payment.amount)}
                      </td>

                      <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-500 sm:px-6">
                        {formatDate(getPaymentDate(payment))}
                      </td>

                      <td className="whitespace-nowrap px-5 py-4 sm:px-6">
                        <span
                          className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset ${getStatusStyles(payment.status)}`}
                        >
                          {formatStatus(payment.status)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="flex flex-col gap-2 border-t border-slate-200 px-5 py-4 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between sm:px-6">
              <p>
                Showing {filteredPayments.length} matching record
                {filteredPayments.length === 1 ? "" : "s"} from the loaded page
              </p>

              <p className="text-xs text-slate-400">
                {pagination.count.toLocaleString("en-PH")} total records
              </p>
            </div>
          </>
        )}
      </section>
    </div>
  );
}

export default Payments;