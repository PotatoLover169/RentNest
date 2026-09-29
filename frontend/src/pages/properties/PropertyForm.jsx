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
  {
    value: "APARTMENT",
    label: "Apartment",
  },
  {
    value: "CONDOMINIUM",
    label: "Condominium",
  },
  {
    value: "HOUSE",
    label: "House",
  },
  {
    value: "BOARDING_HOUSE",
    label: "Boarding House",
  },
  {
    value: "DORMITORY",
    label: "Dormitory",
  },
  {
    value: "COMMERCIAL",
    label: "Commercial",
  },
  {
    value: "OTHER",
    label: "Other",
  },
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

  if (data?.message) {
    return data.message;
  }

  return "Something went wrong. Please try again.";
}

function getFieldErrors(error) {
  const data = error?.response?.data;

  if (!data || typeof data !== "object") {
    return {};
  }

  const errors = {};

  Object.entries(data).forEach(([field, value]) => {
    if (field === "detail" || field === "message") {
      return;
    }

    if (Array.isArray(value)) {
      errors[field] = value.join(" ");
      return;
    }

    if (typeof value === "string") {
      errors[field] = value;
    }
  });

  return errors;
}

function PropertyForm() {
  const navigate = useNavigate();
  const { id } = useParams();

  const isEditMode = Boolean(id);

  const [formData, setFormData] = useState(
    INITIAL_FORM_DATA,
  );

  const [isLoading, setIsLoading] = useState(
    isEditMode,
  );

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [submitError, setSubmitError] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});

  const loadProperty = useCallback(async () => {
    if (!id) {
      return;
    }

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
    } catch (requestError) {
      setLoadError(
        getErrorMessage(requestError),
      );
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    // Data fetching is intentionally triggered when edit mode loads.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadProperty();
  }, [loadProperty]);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((current) => ({
      ...current,
      [name]: value,
    }));

    setSubmitError("");

    setFieldErrors((current) => {
      if (!current[name]) {
        return current;
      }

      const next = {
        ...current,
      };

      delete next[name];

      return next;
    });
  };

  const validateForm = () => {
    const errors = {};

    if (!formData.name.trim()) {
      errors.name = "Property name is required.";
    }

    if (!formData.property_type) {
      errors.property_type =
        "Property type is required.";
    }

    if (!formData.address_line.trim()) {
      errors.address_line =
        "Address is required.";
    }

    if (!formData.city.trim()) {
      errors.city = "City is required.";
    }

    if (!formData.province.trim()) {
      errors.province =
        "Province is required.";
    }

    return errors;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setSubmitError("");
    setFieldErrors({});

    const validationErrors = validateForm();

    if (Object.keys(validationErrors).length > 0) {
      setFieldErrors(validationErrors);
      return;
    }

    setIsSubmitting(true);

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
      if (isEditMode) {
        await updateProperty(id, payload);
        navigate(`/properties/${id}`);
        return;
      }

      const property = await createProperty(payload);

      navigate(`/properties/${property.id}`);
    } catch (requestError) {
      setSubmitError(
        getErrorMessage(requestError),
      );

      setFieldErrors(
        getFieldErrors(requestError),
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    if (isEditMode) {
      navigate(`/properties/${id}`);
      return;
    }

    navigate("/properties");
  };

  if (isLoading) {
    return (
      <div className="mx-auto max-w-4xl space-y-8">
        <PageHeader
          eyebrow="Management"
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
          eyebrow="Management"
          title="Edit Property"
          description="Unable to load this property."
        />

        <ErrorState
          title="Unable to load property"
          message={loadError}
          action={
            <Button
              variant="secondary"
              onClick={loadProperty}
            >
              Try Again
            </Button>
          }
        />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <PageHeader
        eyebrow="Management"
        title={
          isEditMode
            ? "Edit Property"
            : "Add Property"
        }
        description={
          isEditMode
            ? "Update the property information below."
            : "Add a new rental property to your portfolio."
        }
      />

      <Card className="p-6 sm:p-8">
        {submitError && (
          <div
            role="alert"
            className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
          >
            {submitError}
          </div>
        )}

        <form
          onSubmit={handleSubmit}
          className="space-y-8"
        >
          <section>
            <h2 className="text-lg font-semibold text-slate-950">
              Property Information
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Enter the basic information for this property.
            </p>

            <div className="mt-5 grid gap-5 sm:grid-cols-2">
              <div className="sm:col-span-2">
                <label
                  htmlFor="name"
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  Property name
                </label>

                <input
                  id="name"
                  name="name"
                  type="text"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="e.g. Sunrise Apartments"
                  maxLength={150}
                  required
                  className={[
                    "w-full rounded-lg border bg-white px-4 py-3 text-sm text-slate-900 outline-none transition",
                    "placeholder:text-slate-400 focus:border-slate-900 focus:ring-2 focus:ring-slate-900/10",
                    fieldErrors.name
                      ? "border-red-400"
                      : "border-slate-300",
                  ].join(" ")}
                />

                {fieldErrors.name && (
                  <p className="mt-1.5 text-sm text-red-600">
                    {fieldErrors.name}
                  </p>
                )}
              </div>

              <div className="sm:col-span-2">
                <label
                  htmlFor="property_type"
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  Property type
                </label>

                <select
                  id="property_type"
                  name="property_type"
                  value={formData.property_type}
                  onChange={handleChange}
                  required
                  className={[
                    "w-full rounded-lg border bg-white px-4 py-3 text-sm text-slate-900 outline-none transition",
                    "focus:border-slate-900 focus:ring-2 focus:ring-slate-900/10",
                    fieldErrors.property_type
                      ? "border-red-400"
                      : "border-slate-300",
                  ].join(" ")}
                >
                  <option value="">
                    Select a property type
                  </option>

                  {PROPERTY_TYPES.map((type) => (
                    <option
                      key={type.value}
                      value={type.value}
                    >
                      {type.label}
                    </option>
                  ))}
                </select>

                {fieldErrors.property_type && (
                  <p className="mt-1.5 text-sm text-red-600">
                    {fieldErrors.property_type}
                  </p>
                )}
              </div>

              <div className="sm:col-span-2">
                <label
                  htmlFor="description"
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  Description
                </label>

                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  rows={4}
                  placeholder="Describe the property..."
                  className={[
                    "w-full resize-y rounded-lg border bg-white px-4 py-3 text-sm text-slate-900 outline-none transition",
                    "placeholder:text-slate-400 focus:border-slate-900 focus:ring-2 focus:ring-slate-900/10",
                    fieldErrors.description
                      ? "border-red-400"
                      : "border-slate-300",
                  ].join(" ")}
                />

                {fieldErrors.description && (
                  <p className="mt-1.5 text-sm text-red-600">
                    {fieldErrors.description}
                  </p>
                )}
              </div>
            </div>
          </section>

          <section className="border-t border-slate-200 pt-8">
            <h2 className="text-lg font-semibold text-slate-950">
              Property Address
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Enter the property's complete location.
            </p>

            <div className="mt-5 grid gap-5 sm:grid-cols-2">
              <div className="sm:col-span-2">
                <label
                  htmlFor="address_line"
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  Address
                </label>

                <input
                  id="address_line"
                  name="address_line"
                  type="text"
                  value={formData.address_line}
                  onChange={handleChange}
                  placeholder="e.g. 123 Main Street"
                  maxLength={255}
                  required
                  className={[
                    "w-full rounded-lg border bg-white px-4 py-3 text-sm text-slate-900 outline-none transition",
                    "placeholder:text-slate-400 focus:border-slate-900 focus:ring-2 focus:ring-slate-900/10",
                    fieldErrors.address_line
                      ? "border-red-400"
                      : "border-slate-300",
                  ].join(" ")}
                />

                {fieldErrors.address_line && (
                  <p className="mt-1.5 text-sm text-red-600">
                    {fieldErrors.address_line}
                  </p>
                )}
              </div>

              <div>
                <label
                  htmlFor="city"
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  City
                </label>

                <input
                  id="city"
                  name="city"
                  type="text"
                  value={formData.city}
                  onChange={handleChange}
                  placeholder="e.g. Cebu City"
                  maxLength={100}
                  required
                  className={[
                    "w-full rounded-lg border bg-white px-4 py-3 text-sm text-slate-900 outline-none transition",
                    "placeholder:text-slate-400 focus:border-slate-900 focus:ring-2 focus:ring-slate-900/10",
                    fieldErrors.city
                      ? "border-red-400"
                      : "border-slate-300",
                  ].join(" ")}
                />

                {fieldErrors.city && (
                  <p className="mt-1.5 text-sm text-red-600">
                    {fieldErrors.city}
                  </p>
                )}
              </div>

              <div>
                <label
                  htmlFor="province"
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  Province
                </label>

                <input
                  id="province"
                  name="province"
                  type="text"
                  value={formData.province}
                  onChange={handleChange}
                  placeholder="e.g. Cebu"
                  maxLength={100}
                  required
                  className={[
                    "w-full rounded-lg border bg-white px-4 py-3 text-sm text-slate-900 outline-none transition",
                    "placeholder:text-slate-400 focus:border-slate-900 focus:ring-2 focus:ring-slate-900/10",
                    fieldErrors.province
                      ? "border-red-400"
                      : "border-slate-300",
                  ].join(" ")}
                />

                {fieldErrors.province && (
                  <p className="mt-1.5 text-sm text-red-600">
                    {fieldErrors.province}
                  </p>
                )}
              </div>

              <div>
                <label
                  htmlFor="postal_code"
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  Postal code
                </label>

                <input
                  id="postal_code"
                  name="postal_code"
                  type="text"
                  value={formData.postal_code}
                  onChange={handleChange}
                  placeholder="e.g. 6000"
                  maxLength={20}
                  className={[
                    "w-full rounded-lg border bg-white px-4 py-3 text-sm text-slate-900 outline-none transition",
                    "placeholder:text-slate-400 focus:border-slate-900 focus:ring-2 focus:ring-slate-900/10",
                    fieldErrors.postal_code
                      ? "border-red-400"
                      : "border-slate-300",
                  ].join(" ")}
                />

                {fieldErrors.postal_code && (
                  <p className="mt-1.5 text-sm text-red-600">
                    {fieldErrors.postal_code}
                  </p>
                )}
              </div>
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

            <Button
              type="submit"
              disabled={isSubmitting}
            >
              {isSubmitting
                ? isEditMode
                  ? "Saving..."
                  : "Creating..."
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