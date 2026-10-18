
import { useState } from "react";
import { useAuth } from "../../context/useAuth";
import Button from "../../components/ui/Button";
import Card from "../../components/ui/Card";

function getInitials(user) {
  const firstName = user?.first_name?.trim() ?? "";
  const lastName = user?.last_name?.trim() ?? "";

  const initials = `${firstName.charAt(0)}${lastName.charAt(0)}`;

  return initials.trim().toUpperCase() || user?.email?.charAt(0)?.toUpperCase() || "U";
}

function formatRole(role) {
  return String(role ?? "")
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function SettingsForm({ user, updateProfile }) {
  const [form, setForm] = useState(() => ({
    first_name: user?.first_name ?? "",
    last_name: user?.last_name ?? "",
  }));

  const [isSaving, setIsSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const fullName =
    [user?.first_name, user?.last_name].filter(Boolean).join(" ") ||
    "Your account";

  const roleLabel = formatRole(user?.role);
  const initials = getInitials(user);

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

  return (
    <div className="mx-auto w-full max-w-6xl space-y-8">
      {/* Page heading */}
      <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-blue-700">
            <span className="h-1.5 w-1.5 rounded-full bg-blue-600" />
            Account preferences
          </div>

          <h1 className="text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
            Settings
          </h1>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500 sm:text-base">
            Manage your profile and keep your RentNest account information up
            to date.
          </p>
        </div>

        <div className="flex items-center gap-2 text-sm text-slate-500">
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-50 text-emerald-600">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="h-4 w-4"
              aria-hidden="true"
            >
              <path d="m5 12 4 4L19 6" />
            </svg>
          </span>
          Account overview
        </div>
      </header>

      {/* Account identity banner */}
      <Card className="overflow-hidden">
        <div className="h-2 bg-gradient-to-r from-blue-700 via-blue-500 to-sky-300" />

        <div className="flex flex-col gap-5 p-6 sm:flex-row sm:items-center sm:p-8">
          <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-2xl bg-blue-50 text-2xl font-bold text-blue-700 ring-1 ring-blue-100">
            {initials}
          </div>

          <div className="min-w-0 flex-1">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">
              Your profile
            </p>

            <h2 className="mt-1 truncate text-xl font-bold text-slate-950 sm:text-2xl">
              {fullName}
            </h2>

            <p className="mt-1 break-all text-sm text-slate-500">
              {user?.email}
            </p>

            <div className="mt-3 flex flex-wrap items-center gap-2">
              <span className="inline-flex items-center gap-1.5 rounded-full border border-blue-100 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                <span className="h-1.5 w-1.5 rounded-full bg-blue-600" />
                {roleLabel || "Account"}
              </span>

              <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-100 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                Signed in
              </span>
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 sm:min-w-40">
            <p className="text-xs font-medium text-slate-500">
              Account type
            </p>
            <p className="mt-1 text-sm font-semibold text-slate-900">
              {roleLabel || "Standard account"}
            </p>
            <p className="mt-1 text-xs text-slate-400">
              RentNest member
            </p>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-[minmax(0,1.6fr)_minmax(280px,0.9fr)]">
        {/* Profile form */}
        <Card className="overflow-hidden">
          <div className="border-b border-slate-100 px-6 py-5 sm:px-8">
            <div className="flex items-start gap-3">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-700">
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  className="h-5 w-5"
                  aria-hidden="true"
                >
                  <path d="M20 21a8 8 0 0 0-16 0" />
                  <circle cx="12" cy="8" r="4" />
                </svg>
              </div>

              <div>
                <h2 className="text-base font-bold text-slate-950">
                  Personal information
                </h2>
                <p className="mt-1 text-sm leading-5 text-slate-500">
                  Update the name associated with your account.
                </p>
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6 p-6 sm:p-8">
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
              <div>
                <label
                  htmlFor="first_name"
                  className="mb-2 block text-sm font-semibold text-slate-700"
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
                  placeholder="Enter first name"
                  className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 hover:border-slate-300 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 disabled:cursor-not-allowed disabled:bg-slate-50"
                />
              </div>

              <div>
                <label
                  htmlFor="last_name"
                  className="mb-2 block text-sm font-semibold text-slate-700"
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
                  placeholder="Enter last name"
                  className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 hover:border-slate-300 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 disabled:cursor-not-allowed disabled:bg-slate-50"
                />
              </div>
            </div>

            <div className="border-t border-slate-100 pt-6">
              <div className="mb-5">
                <h3 className="text-sm font-bold text-slate-900">
                  Account details
                </h3>
                <p className="mt-1 text-sm text-slate-500">
                  These details are managed by your account and cannot be
                  edited here.
                </p>
              </div>

              <div className="space-y-4">
                <div>
                  <label
                    htmlFor="email"
                    className="mb-2 block text-sm font-semibold text-slate-700"
                  >
                    Email address
                  </label>
                  <div className="relative">
                    <input
                      id="email"
                      type="email"
                      value={user?.email ?? ""}
                      readOnly
                      className="w-full cursor-not-allowed rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 pr-11 text-sm text-slate-500"
                    />
                    <span className="absolute inset-y-0 right-4 flex items-center text-slate-400">
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        className="h-4 w-4"
                        aria-hidden="true"
                      >
                        <rect x="3" y="5" width="18" height="14" rx="2" />
                        <path d="m3 7 9 6 9-6" />
                      </svg>
                    </span>
                  </div>
                </div>

                <div>
                  <label
                    htmlFor="role"
                    className="mb-2 block text-sm font-semibold text-slate-700"
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
            </div>

            {errorMessage && (
              <div
                role="alert"
                className="flex gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm leading-5 text-red-700"
              >
                <span className="font-bold" aria-hidden="true">!</span>
                <p>{errorMessage}</p>
              </div>
            )}

            {successMessage && (
              <div
                role="status"
                className="flex gap-3 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm leading-5 text-emerald-700"
              >
                <span className="font-bold" aria-hidden="true">✓</span>
                <p>{successMessage}</p>
              </div>
            )}

            <div className="flex flex-col-reverse gap-3 border-t border-slate-100 pt-5 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-xs leading-5 text-slate-400">
                Changes apply to your RentNest profile.
              </p>

              <Button
                type="submit"
                disabled={isSaving}
                className="w-full sm:w-auto"
              >
                {isSaving ? (
                  <span className="inline-flex items-center gap-2">
                    <svg
                      className="h-4 w-4 animate-spin"
                      viewBox="0 0 24 24"
                      fill="none"
                      aria-hidden="true"
                    >
                      <circle
                        cx="12"
                        cy="12"
                        r="9"
                        stroke="currentColor"
                        strokeWidth="3"
                        opacity=".25"
                      />
                      <path
                        d="M21 12a9 9 0 0 0-9-9"
                        stroke="currentColor"
                        strokeWidth="3"
                        strokeLinecap="round"
                      />
                    </svg>
                    Saving changes...
                  </span>
                ) : (
                  "Save changes"
                )}
              </Button>
            </div>
          </form>
        </Card>

        {/* Supporting information */}
        <div className="space-y-6">
          <Card className="p-6 sm:p-7">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-sky-50 text-sky-700">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
                className="h-5 w-5"
                aria-hidden="true"
              >
                <path d="M12 3 4.5 6v5.5c0 4.5 3.2 7.8 7.5 9.5 4.3-1.7 7.5-5 7.5-9.5V6L12 3Z" />
                <path d="m9 12 2 2 4-4" />
              </svg>
            </div>

            <h2 className="mt-4 text-base font-bold text-slate-950">
              Your account, your access
            </h2>

            <p className="mt-2 text-sm leading-6 text-slate-500">
              RentNest uses your account role to determine which areas of the
              platform are available to you.
            </p>

            <div className="mt-5 rounded-xl border border-slate-100 bg-slate-50 p-4">
              <p className="text-xs font-medium uppercase tracking-wider text-slate-400">
                Current role
              </p>
              <p className="mt-1.5 text-sm font-semibold text-slate-800">
                {roleLabel || "Not specified"}
              </p>
            </div>
          </Card>

          <Card className="overflow-hidden">
            <div className="border-b border-slate-100 px-6 py-5">
              <h2 className="text-base font-bold text-slate-950">
                Profile checklist
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                Keep your account information current.
              </p>
            </div>

            <div className="space-y-4 p-6">
              <div className="flex items-start gap-3">
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-50 text-xs font-bold text-emerald-600">
                  ✓
                </span>
                <div>
                  <p className="text-sm font-semibold text-slate-800">
                    Account email
                  </p>
                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    Your account email is available for identification.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <span
                  className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                    user?.first_name?.trim() && user?.last_name?.trim()
                      ? "bg-emerald-50 text-emerald-600"
                      : "bg-amber-50 text-amber-600"
                  }`}
                >
                  {user?.first_name?.trim() && user?.last_name?.trim()
                    ? "✓"
                    : "!"}
                </span>
                <div>
                  <p className="text-sm font-semibold text-slate-800">
                    Full name
                  </p>
                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    {user?.first_name?.trim() && user?.last_name?.trim()
                      ? "Your profile includes your first and last name."
                      : "Add your first and last name to complete your profile."}
                  </p>
                </div>
              </div>
            </div>
          </Card>

          <div className="rounded-xl border border-blue-100 bg-blue-50/70 p-5">
            <p className="text-sm font-semibold text-blue-950">
              Need to change your email or password?
            </p>
            <p className="mt-2 text-sm leading-6 text-blue-800/80">
              Those actions are not available in this form yet. We can add
              them after implementing the appropriate secure backend flows.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Settings() {
  const { user, isLoading, updateProfile } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-64 items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-slate-200 border-t-blue-600" />
          <p className="mt-4 text-sm font-medium text-slate-500">
            Loading your account settings...
          </p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="mx-auto max-w-xl rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-amber-50 text-amber-600">
          !
        </div>
        <h1 className="mt-4 text-lg font-bold text-slate-900">
          Account unavailable
        </h1>
        <p className="mt-2 text-sm leading-6 text-slate-500">
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
