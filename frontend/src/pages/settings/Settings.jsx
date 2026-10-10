
import { useState } from "react";
import { useAuth } from "../../context/useAuth";
import Button from "../../components/ui/Button";
import Card from "../../components/ui/Card";

function SettingsForm({ user, updateProfile }) {
  const [form, setForm] = useState(() => ({
    first_name: user?.first_name ?? "",
    last_name: user?.last_name ?? "",
  }));

  const [isSaving, setIsSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const handleChange = (event) => {
    const { name, value } = event.target;

    setForm((currentForm) => ({
      ...currentForm,
      [name]: value,
    }));

    setErrorMessage("");
    setSuccessMessage("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setIsSaving(true);
    setErrorMessage("");
    setSuccessMessage("");

    try {
      await updateProfile({
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
      });

      setSuccessMessage("Your profile has been updated successfully.");
    } catch (error) {
      const data = error.response?.data;

      if (typeof data?.detail === "string") {
        setErrorMessage(data.detail);
      } else if (typeof data?.first_name?.[0] === "string") {
        setErrorMessage(data.first_name[0]);
      } else if (typeof data?.last_name?.[0] === "string") {
        setErrorMessage(data.last_name[0]);
      } else if (typeof data?.non_field_errors?.[0] === "string") {
        setErrorMessage(data.non_field_errors[0]);
      } else {
        setErrorMessage(
          "Unable to update your profile. Please check your information and try again."
        );
      }
    } finally {
      setIsSaving(false);
    }
  };

  const roleLabel = (user?.role ?? "")
    .toString()
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (character) => character.toUpperCase());

  return (
    <div className="mx-auto w-full max-w-4xl space-y-6">
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-600">
          Account
        </p>
        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
          Settings
        </h1>
        <p className="mt-2 text-sm leading-6 text-slate-500">
          Manage your personal information and review your account details.
        </p>
      </div>

      <Card className="p-6 sm:p-8">
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-slate-900">
            Personal information
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            Update the name associated with your RentNest account.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <div>
              <label
                htmlFor="first_name"
                className="mb-2 block text-sm font-medium text-slate-700"
              >
                First name
              </label>
              <input
                id="first_name"
                name="first_name"
                type="text"
                autoComplete="given-name"
                value={form.first_name}
                onChange={handleChange}
                required
                maxLength={100}
                disabled={isSaving}
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 disabled:cursor-not-allowed disabled:bg-slate-100"
                placeholder="Enter your first name"
              />
            </div>

            <div>
              <label
                htmlFor="last_name"
                className="mb-2 block text-sm font-medium text-slate-700"
              >
                Last name
              </label>
              <input
                id="last_name"
                name="last_name"
                type="text"
                autoComplete="family-name"
                value={form.last_name}
                onChange={handleChange}
                required
                maxLength={100}
                disabled={isSaving}
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 disabled:cursor-not-allowed disabled:bg-slate-100"
                placeholder="Enter your last name"
              />
            </div>
          </div>

          <div className="border-t border-slate-200 pt-5">
            <h3 className="text-base font-semibold text-slate-900">
              Account details
            </h3>
            <p className="mt-1 text-sm text-slate-500">
              These details are managed by your account settings and cannot be
              edited here.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <div>
              <label
                htmlFor="email"
                className="mb-2 block text-sm font-medium text-slate-700"
              >
                Email address
              </label>
              <input
                id="email"
                type="email"
                value={user?.email ?? ""}
                readOnly
                className="w-full cursor-not-allowed rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500"
              />
            </div>

            <div>
              <label
                htmlFor="role"
                className="mb-2 block text-sm font-medium text-slate-700"
              >
                Account role
              </label>
              <input
                id="role"
                type="text"
                value={roleLabel}
                readOnly
                className="w-full cursor-not-allowed rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500"
              />
            </div>
          </div>

          {errorMessage && (
            <div
              role="alert"
              className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
            >
              {errorMessage}
            </div>
          )}

          {successMessage && (
            <div
              role="status"
              className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700"
            >
              {successMessage}
            </div>
          )}

          <div className="flex justify-end border-t border-slate-200 pt-5">
            <Button
              type="submit"
              disabled={isSaving}
              className="min-w-36"
            >
              {isSaving ? "Saving..." : "Save changes"}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}

export default function Settings() {
  const { user, isLoading, updateProfile } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-64 items-center justify-center">
        <p className="text-sm text-slate-500">
          Loading your account settings...
        </p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-6">
        <h1 className="text-lg font-semibold text-slate-900">
          Account unavailable
        </h1>
        <p className="mt-2 text-sm text-slate-500">
          Please sign in again to access your account settings.
        </p>
      </div>
    );
  }

  return (
    <SettingsForm
      key={user.id}
      user={user}
      updateProfile={updateProfile}
    />
  );
}
