
import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getPayment } from "../../api/payments";

const formatCurrency = (value) => {
  const amount = Number(value);

  if (!Number.isFinite(amount)) {
    return "₱0.00";
  }

  return new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
  }).format(amount);
};

const formatDate = (value) => {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleDateString("en-PH", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
};

const formatDateTime = (value) => {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return date.toLocaleString("en-PH", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
};

const formatLabel = (value) => {
  if (!value) return "—";

  return String(value)
    .toLowerCase()
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
};

const getStatusStyle = (status) => {
  const styles = {
    PAID: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
    PENDING: "bg-amber-50 text-amber-700 ring-amber-600/20",
    FAILED: "bg-red-50 text-red-700 ring-red-600/20",
    REFUNDED: "bg-purple-50 text-purple-700 ring-purple-600/20",
    CANCELLED: "bg-gray-100 text-gray-600 ring-gray-500/20",
  };

  return (
    styles[status] ||
    "bg-gray-100 text-gray-600 ring-gray-500/20"
  );
};

function DetailItem({ label, value }) {
  return (
    <div className="border-b border-gray-100 py-4 last:border-b-0">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="mt-1 break-words text-sm font-medium text-gray-900">
        {value ?? "—"}
      </p>
    </div>
  );
}

function PaymentDetail() {
  const { id } = useParams();

  const [payment, setPayment] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const loadPayment = useCallback(async () => {
    setIsLoading(true);
    setError("");

    try {
      const data = await getPayment(id);
      setPayment(data);
    } catch (err) {
      setPayment(null);

      if (err.response?.status === 404) {
        setError("Payment not found.");
      } else {
        setError(
          err.response?.data?.detail ||
            "Unable to load payment details. Please try again."
        );
      }
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    let isActive = true;

    const fetchPayment = async () => {
      setIsLoading(true);
      setError("");

      try {
        const data = await getPayment(id);

        if (isActive) {
          setPayment(data);
        }
      } catch (err) {
        if (isActive) {
          setPayment(null);

          setError(
            err.response?.status === 404
              ? "Payment not found."
              : err.response?.data?.detail ||
                  "Unable to load payment details. Please try again."
          );
        }
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    };

    fetchPayment();

    return () => {
      isActive = false;
    };
  }, [id]);

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600" />
          <p className="mt-4 text-sm text-gray-500">
            Loading payment details...
          </p>
        </div>
      </div>
    );
  }

  if (error || !payment) {
    return (
      <div className="mx-auto max-w-3xl">
        <Link
          to="/payments"
          className="text-sm font-medium text-blue-600 hover:text-blue-700"
        >
          ← Back to Payments
        </Link>

        <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-6">
          <h2 className="text-lg font-semibold text-red-800">
            Unable to Load Payment
          </h2>

          <p className="mt-2 text-sm text-red-700">
            {error || "The requested payment could not be found."}
          </p>

          <button
            type="button"
            onClick={loadPayment}
            className="mt-5 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <Link
            to="/payments"
            className="text-sm font-medium text-blue-600 hover:text-blue-700"
          >
            ← Back to Payments
          </Link>

          <h1 className="mt-3 text-2xl font-bold tracking-tight text-gray-900">
            Payment Details
          </h1>

          <p className="mt-1 text-sm text-gray-500">
            Review the payment information and transaction record.
          </p>
        </div>

        <span
          className={`inline-flex w-fit items-center rounded-full px-3 py-1.5 text-sm font-medium ring-1 ring-inset ${getStatusStyle(
            payment.status
          )}`}
        >
          {formatLabel(payment.status)}
        </span>
      </div>

      <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
        <div className="border-b border-gray-100 bg-gray-50/70 px-6 py-6 sm:px-8">
          <p className="text-sm font-medium text-gray-500">
            Payment Amount
          </p>

          <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900">
            {formatCurrency(payment.amount)}
          </p>

          <p className="mt-2 text-sm text-gray-500">
            Transaction #{payment.id}
          </p>
        </div>

        <div className="grid gap-x-12 px-6 sm:grid-cols-2 sm:px-8">
          <div>
            <DetailItem
              label="Payment Reference"
              value={payment.reference_number || "No reference provided"}
            />

            <DetailItem
              label="Payment Method"
              value={formatLabel(payment.payment_method)}
            />

            <DetailItem
              label="Payment Date"
              value={formatDate(payment.payment_date)}
            />

            <DetailItem
              label="Payment Status"
              value={formatLabel(payment.status)}
            />
          </div>

          <div>
            <DetailItem
              label="Payment ID"
              value={payment.id}
            />

            <DetailItem
              label="Tenancy ID"
              value={payment.tenancy}
            />

            <DetailItem
              label="Tenant ID"
              value={payment.tenant}
            />

            <DetailItem
              label="Created At"
              value={formatDateTime(payment.created_at)}
            />

            <DetailItem
              label="Last Updated"
              value={formatDateTime(payment.updated_at)}
            />
          </div>
        </div>

        <div className="border-t border-gray-100 px-6 py-6 sm:px-8">
          <h2 className="text-sm font-semibold text-gray-900">
            Payment Notes
          </h2>

          <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-gray-600">
            {payment.notes || "No notes available for this payment."}
          </p>
        </div>
      </div>
    </div>
  );
}

export default PaymentDetail;