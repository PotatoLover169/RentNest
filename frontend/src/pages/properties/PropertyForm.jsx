
import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  createProperty,
  getProperty,
  updateProperty,
} from "../../api/properties";
import {
  Button,
  Card,
  ErrorState,
  LoadingState,
  PageHeader,
} from "../../components/ui";

const PROPERTY_TYPES = [
  { value: "APARTMENT", label: "Apartment" },
  { value: "CONDOMINIUM", label: "Condominium" },
  { value: "HOUSE", label: "House" },
  { value: "BOARDING_HOUSE", label: "Boarding House" },
  { value: "DORMITORY", label: "Dormitory" },
  { value: "COMMERCIAL", label: "Commercial" },
  { value: "OTHER", label: "Other" },
];

const INITIAL_FORM_DATA = {
  name: "",
  property_type: "",
  address_line: "",
  city: "",
  province: "",
  postal_code: "",
  description: "",
};

function getErrorMessage(error) {
  const data = error?.response?.data;

  if (data?.detail) {
    return Array.isArray(data.detail)
      ? data.detail.join(" ")
      : data.detail;
  }

  if (data?.message) return data.message;

  return "Unable to save the property. Please review the form and try again.";
}

function getFieldErrors(error) {
  const data = error?.response?.data;

  if (!data || typeof data !== "object") return {};

  return Object.fromEntries(
    Object.entries(data)
      .filter(([key]) => !["detail", "message"].includes(key))
      .map(([key, value]) => [
        key,
        Array.isArray(value) ? value.join(" ") : String(value),
      ])
      .filter(([, value]) => value),
  );
}

const inputClass =
  "w-full rounded-xl border bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 disabled:cursor-not-allowed disabled:bg-slate-100";

function Field({
  label,
  name,
  value,
  onChange,
  error,
  required = false,
  ...props
}) {
  return (
    <div className="min-w-0">
      <label
        htmlFor={name}
        className="mb-2 block text-sm font-semibold text-slate-700"
      >
        {label}
        {required && <span className="ml-1 text-red-500">*</span>}
      </label>
      <input
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        required={required}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? `${name}-error` : undefined}
        className={`${inputClass} ${error ? "border-red-400" : "border-slate-300"}`}
        {...props}
      />
      {error && (
        <p id={`${name}-error`} className="mt-2 text-sm text-red-600">
          {error}
        </p>
      )}
    </div>
  );
}

function PropertyForm() {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEditMode = Boolean(id);

  const [formData, setFormData] = useState(INITIAL_FORM_DATA);
  const [isLoading, setIsLoading] = useState(isEditMode);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [submitError, setSubmitError] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});
  const [hasChanges, setHasChanges] = useState(false);

  const loadProperty = useCallback(async () => {
    if (!id) return;

    try {
      setIsLoading(true);
      setLoadError("");

      const property = await getProperty(id);

      setFormData({
        name: property.name ?? "",
        property_type: property.property_type ?? "",
        address_line: property.address_line ?? "",
        city: property.city ?? "",
        province: property.province ?? "",
        postal_code: property.postal_code ?? "",
        description: property.description ?? "",
      });
      setHasChanges(false);
    } catch (error) {
      setLoadError(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    // Load existing values only when editing a property.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadProperty();
  }, [loadProperty]);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((current) => ({ ...current, [name]: value }));
    setHasChanges(true);
    setSubmitError("");

    setFieldErrors((current) => {
      if (!current[name]) return current;
      const next = { ...current };
      delete next[name];
      return next;
    });
  };

  const validateForm = () => {
    const errors = {};

    if (!formData.name.trim()) {
      errors.name = "Enter a property name.";
    } else if (formData.name.trim().length > 150) {
      errors.name = "Property name must be 150 characters or fewer.";
    }

    if (!formData.property_type) {
      errors.property_type = "Select a property type.";
    }

    if (!formData.address_line.trim()) {
      errors.address_line = "Enter the street address.";
    }

    if (!formData.city.trim()) {
      errors.city = "Enter the city.";
    }

    if (!formData.province.trim()) {
      errors.province = "Enter the province.";
    }

    if (formData.postal_code.trim().length > 20) {
      errors.postal_code = "Postal code must be 20 characters or fewer.";
    }

    return errors;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (isSubmitting) return;

    setSubmitError("");
    const errors = validateForm();
    setFieldErrors(errors);

    if (Object.keys(errors).length) {
      document.getElementById(Object.keys(errors)[0])?.focus();
      return;
    }

    const payload = {
      name: formData.name.trim(),
      property_type: formData.property_type,
      address_line: formData.address_line.trim(),
      city: formData.city.trim(),
      province: formData.province.trim(),
      postal_code: formData.postal_code.trim(),
      description: formData.description.trim(),
    };

    try {
      setIsSubmitting(true);

      if (isEditMode) {
        await updateProperty(id, payload);
        navigate(`/properties/${id}`);
      } else {
        const property = await createProperty(payload);
        navigate(`/properties/${property.id}`);
      }
    } catch (error) {
      setSubmitError(getErrorMessage(error));
      setFieldErrors(getFieldErrors(error));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    if (
      hasChanges &&
      !window.confirm("Discard your unsaved changes?")
    ) {
      return;
    }

    navigate(isEditMode ? `/properties/${id}` : "/properties");
  };

  if (isLoading) {
    return (
      <div className="mx-auto max-w-4xl space-y-8">
        <PageHeader
          eyebrow="Property Management"
          title="Edit Property"
          description="Loading property information..."
        />
        <LoadingState message="Loading property..." />
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="mx-auto max-w-4xl space-y-8">
        <PageHeader
          eyebrow="Property Management"
          title="Edit Property"
          description="Unable to load this property."
        />
        <ErrorState
          title="Unable to load property"
          message={loadError}
          action={
            <div className="flex flex-wrap gap-3">
              <Button variant="secondary" onClick={loadProperty}>
                Try Again
              </Button>
              <Button variant="ghost" onClick={() => navigate("/properties")}>
                Back to Properties
              </Button>
            </div>
          }
        />
      </div>
    );
  }

  const fieldsComplete = [
    formData.name.trim(),
    formData.property_type,
    formData.address_line.trim(),
    formData.city.trim(),
    formData.province.trim(),
  ].filter(Boolean).length;

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <PageHeader
        eyebrow="Property Management"
        title={isEditMode ? "Edit Property" : "Add Property"}
        description={
          isEditMode
            ? "Keep your property information accurate and up to date."
            : "Register a rental property in your RentNest portfolio."
        }
        action={
          <Button variant="secondary" onClick={handleCancel}>
            Cancel
          </Button>
        }
      />

      <Card className="overflow-hidden">
        <div className="border-b border-slate-200 bg-slate-50 px-6 py-5 sm:px-8">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h2 className="font-semibold text-slate-950">
                Property information
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                Fields marked with <span className="text-red-500">*</span> are required.
              </p>
            </div>
            <span className="whitespace-nowrap rounded-full bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-700">
              {fieldsComplete}/5 required
            </span>
          </div>
          <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-slate-200">
            <div
              className="h-full rounded-full bg-blue-600 transition-all"
              style={{ width: `${(fieldsComplete / 5) * 100}%` }}
            />
          </div>
        </div>

        <form onSubmit={handleSubmit} noValidate className="space-y-8 p-6 sm:p-8">
          {submitError && (
            <div
              role="alert"
              className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm leading-6 text-red-700"
            >
              {submitError}
            </div>
          )}

          <section>
            <h3 className="text-base font-semibold text-slate-950">
              Basic details
            </h3>
            <p className="mt-1 text-sm text-slate-500">
              Identify the property and choose its category.
            </p>

            <div className="mt-5 grid gap-5 sm:grid-cols-2">
              <div className="sm:col-span-2">
                <Field
                  label="Property name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  error={fieldErrors.name}
                  required
                  maxLength={150}
                  placeholder="e.g. Sunrise Apartments"
                  autoComplete="organization"
                />
                <p className="mt-1 text-right text-xs text-slate-400">
                  {formData.name.length}/150
                </p>
              </div>

              <div className="sm:col-span-2">
                <label htmlFor="property_type" className="mb-2 block text-sm font-semibold text-slate-700">
                  Property type <span className="text-red-500">*</span>
                </label>
                <select
                  id="property_type"
                  name="property_type"
                  value={formData.property_type}
                  onChange={handleChange}
                  required
                  aria-invalid={Boolean(fieldErrors.property_type)}
                  aria-describedby={fieldErrors.property_type ? "property_type-error" : undefined}
                  className={`${inputClass} ${fieldErrors.property_type ? "border-red-400" : "border-slate-300"}`}
                >
                  <option value="">Select a property type</option>
                  {PROPERTY_TYPES.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
                {fieldErrors.property_type && (
                  <p id="property_type-error" className="mt-2 text-sm text-red-600">
                    {fieldErrors.property_type}
                  </p>
                )}
              </div>
            </div>
          </section>

          <section className="border-t border-slate-200 pt-8">
            <h3 className="text-base font-semibold text-slate-950">
              Location
            </h3>
            <p className="mt-1 text-sm text-slate-500">
              Enter the property's registered address.
            </p>

            <div className="mt-5 grid gap-5 sm:grid-cols-2">
              <div className="sm:col-span-2">
                <Field
                  label="Street address"
                  name="address_line"
                  value={formData.address_line}
                  onChange={handleChange}
                  error={fieldErrors.address_line}
                  required
                  maxLength={255}
                  placeholder="Building, street, barangay"
                  autoComplete="street-address"
                />
              </div>
              <Field
                label="City"
                name="city"
                value={formData.city}
                onChange={handleChange}
                error={fieldErrors.city}
                required
                maxLength={100}
                placeholder="e.g. Cebu City"
                autoComplete="address-level2"
              />
              <Field
                label="Province"
                name="province"
                value={formData.province}
                onChange={handleChange}
                error={fieldErrors.province}
                required
                maxLength={100}
                placeholder="e.g. Cebu"
                autoComplete="address-level1"
              />
              <Field
                label="Postal code"
                name="postal_code"
                value={formData.postal_code}
                onChange={handleChange}
                error={fieldErrors.postal_code}
                maxLength={20}
                placeholder="Optional"
                autoComplete="postal-code"
              />
            </div>
          </section>

          <section className="border-t border-slate-200 pt-8">
            <h3 className="text-base font-semibold text-slate-950">
              Additional information
            </h3>
            <p className="mt-1 text-sm text-slate-500">
              Add useful context for your team.
            </p>
            <div className="mt-5">
              <label htmlFor="description" className="mb-2 block text-sm font-semibold text-slate-700">
                Description
              </label>
              <textarea
                id="description"
                name="description"
                rows={5}
                value={formData.description}
                onChange={handleChange}
                maxLength={2000}
                placeholder="Describe the property, amenities, or other useful details..."
                className={`${inputClass} resize-y border-slate-300`}
              />
              <p className="mt-1 text-right text-xs text-slate-400">
                {formData.description.length}/2000
              </p>
              {fieldErrors.description && (
                <p className="mt-2 text-sm text-red-600">
                  {fieldErrors.description}
                </p>
              )}
            </div>
          </section>

          <div className="flex flex-col-reverse gap-3 border-t border-slate-200 pt-6 sm:flex-row sm:justify-end">
            <Button
              type="button"
              variant="secondary"
              onClick={handleCancel}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting
                ? "Saving property..."
                : isEditMode
                  ? "Save Changes"
                  : "Create Property"}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}

export default PropertyForm;
