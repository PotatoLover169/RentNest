import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { getProperties } from "../../api/properties";
import {
  createUnit,
  getUnit,
  updateUnit,
} from "../../api/units";
import {
  Button,
  Card,
  ErrorState,
  LoadingState,
  PageHeader,
} from "../../components/ui";
import { getResults } from "../../utils/api";

const UNIT_TYPES = [
  { value: "STUDIO", label: "Studio" },
  { value: "ONE_BEDROOM", label: "One Bedroom" },
  { value: "TWO_BEDROOM", label: "Two Bedroom" },
  { value: "THREE_BEDROOM", label: "Three Bedroom" },
  { value: "FOUR_PLUS_BEDROOM", label: "Four Plus Bedroom" },
  { value: "COMMERCIAL", label: "Commercial" },
  { value: "OTHER", label: "Other" },
];

const INITIAL_FORM_DATA = {
  property: "",
  unit_number: "",
  unit_type: "",
  bedrooms: "0",
  bathrooms: "1",
  monthly_rent: "",
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

  if (data && typeof data === "object") {
    const messages = Object.values(data)
      .flatMap((value) =>
        Array.isArray(value) ? value : [value],
      )
      .filter((value) => typeof value === "string");

    if (messages.length > 0) {
      return messages.join(" ");
    }
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

  if (data.non_field_errors) {
    errors.unit_number = Array.isArray(
      data.non_field_errors,
    )
      ? data.non_field_errors.join(" ")
      : data.non_field_errors;
  }

  return errors;
}

function UnitForm() {
  const navigate = useNavigate();
  const { id } = useParams();

  const isEditMode = Boolean(id);

  const [formData, setFormData] = useState(
    INITIAL_FORM_DATA,
  );
  const [properties, setProperties] = useState([]);
  const [isLoading, setIsLoading] = useState(isEditMode);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [submitError, setSubmitError] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});

  const loadFormData = useCallback(async () => {
    try {
      setIsLoading(true);
      setLoadError("");

      const propertiesData = await getProperties();

      setProperties(getResults(propertiesData));

      if (id) {
        const unit = await getUnit(id);

        setFormData({
          property: unit.property ?? "",
          unit_number: unit.unit_number ?? "",
          unit_type: unit.unit_type ?? "",
          bedrooms: String(unit.bedrooms ?? 0),
          bathrooms: String(unit.bathrooms ?? 1),
          monthly_rent: String(unit.monthly_rent ?? ""),
          description: unit.description ?? "",
        });
      }
    } catch (requestError) {
      setLoadError(getErrorMessage(requestError));
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    // Data fetching is intentionally triggered when the form loads.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadFormData();
  }, [loadFormData]);

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

    if (!formData.property) {
      errors.property =
        "Property is required.";
    }

    if (!formData.unit_number.trim()) {
      errors.unit_number =
        "Unit number is required.";
    }

    if (!formData.unit_type) {
      errors.unit_type =
        "Unit type is required.";
    }

    if (
      formData.bedrooms === "" ||
      Number(formData.bedrooms) < 0
    ) {
      errors.bedrooms =
        "Bedrooms must be zero or greater.";
    }

    if (
      formData.bathrooms === "" ||
      Number(formData.bathrooms) < 0
    ) {
      errors.bathrooms =
        "Bathrooms must be zero or greater.";
    }

    if (
      formData.monthly_rent === "" ||
      Number(formData.monthly_rent) < 0
    ) {
      errors.monthly_rent =
        "Monthly rent must be zero or greater.";
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
      property: Number(formData.property),
      unit_number: formData.unit_number.trim(),
      unit_type: formData.unit_type,
      bedrooms: Number(formData.bedrooms),
      bathrooms: Number(formData.bathrooms),
      monthly_rent: formData.monthly_rent,
      description: formData.description.trim(),
    };

    try {
      if (isEditMode) {
        const updatedUnit = await updateUnit(
          id,
          {
            unit_number: payload.unit_number,
            unit_type: payload.unit_type,
            bedrooms: payload.bedrooms,
            bathrooms: payload.bathrooms,
            monthly_rent: payload.monthly_rent,
            description: payload.description,
          },
        );

        navigate(`/units/${updatedUnit.id || id}`);
        return;
      }

      const unit = await createUnit(payload);

      navigate(`/units/${unit.id}`);
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
      navigate(`/units/${id}`);
      return;
    }

    navigate("/units");
  };

  if (isLoading) {
    return (
      <div className="mx-auto max-w-4xl space-y-8">
        <PageHeader
          eyebrow="Management"
          title={
            isEditMode
              ? "Edit Unit"
              : "Add Unit"
          }
          description="Loading unit information..."
        />

        <LoadingState message="Loading unit..." />
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="mx-auto max-w-4xl space-y-8">
        <PageHeader
          eyebrow="Management"
          title={
            isEditMode
              ? "Edit Unit"
              : "Add Unit"
          }
          description="Unable to load unit information."
        />

        <ErrorState
          title="Unable to load unit"
          message={loadError}
          action={
            <div className="flex gap-3">
              <Button
                variant="secondary"
                onClick={loadFormData}
              >
                Try Again
              </Button>

              <Button
                variant="ghost"
                onClick={() => navigate("/units")}
              >
                Back to Units
              </Button>
            </div>
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
            ? "Edit Unit"
            : "Add Unit"
        }
        description={
          isEditMode
            ? "Update the unit information below."
            : "Add a new rental unit to one of your properties."
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
              Unit Information
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Enter the basic information for this rental unit.
            </p>

            <div className="mt-5 grid gap-5 sm:grid-cols-2">
              <div className="sm:col-span-2">
                <label
                  htmlFor="property"
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  Property
                </label>

                <select
                  id="property"
                  name="property"
                  value={formData.property}
                  onChange={handleChange}
                  disabled={isEditMode}
                  required
                  className={[
                    "w-full rounded-lg border bg-white px-4 py-3 text-sm text-slate-900 outline-none transition",
                    "focus:border-slate-900 focus:ring-2 focus:ring-slate-900/10",
                    "disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-500",
                    fieldErrors.property
                      ? "border-red-400"
                      : "border-slate-300",
                  ].join(" ")}
                >
                  <option value="">
                    Select a property
                  </option>

                  {properties.map((property) => (
                    <option
                      key={property.id}
                      value={property.id}
                    >
                      {property.name}
                    </option>
                  ))}
                </select>

                {isEditMode && (
                  <p className="mt-1.5 text-xs text-slate-400">
                    A unit cannot be moved to another property after creation.
                  </p>
                )}

                {fieldErrors.property && (
                  <p className="mt-1.5 text-sm text-red-600">
                    {fieldErrors.property}
                  </p>
                )}
              </div>

              <div>
                <label
                  htmlFor="unit_number"
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  Unit number
                </label>

                <input
                  id="unit_number"
                  name="unit_number"
                  type="text"
                  value={formData.unit_number}
                  onChange={handleChange}
                  placeholder="e.g. 101"
                  maxLength={50}
                  required
                  className={[
                    "w-full rounded-lg border bg-white px-4 py-3 text-sm text-slate-900 outline-none transition",
                    "placeholder:text-slate-400 focus:border-slate-900 focus:ring-2 focus:ring-slate-900/10",
                    fieldErrors.unit_number
                      ? "border-red-400"
                      : "border-slate-300",
                  ].join(" ")}
                />

                {fieldErrors.unit_number && (
                  <p className="mt-1.5 text-sm text-red-600">
                    {fieldErrors.unit_number}
                  </p>
                )}
              </div>

              <div>
                <label
                  htmlFor="unit_type"
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  Unit type
                </label>

                <select
                  id="unit_type"
                  name="unit_type"
                  value={formData.unit_type}
                  onChange={handleChange}
                  required
                  className={[
                    "w-full rounded-lg border bg-white px-4 py-3 text-sm text-slate-900 outline-none transition",
                    "focus:border-slate-900 focus:ring-2 focus:ring-slate-900/10",
                    fieldErrors.unit_type
                      ? "border-red-400"
                      : "border-slate-300",
                  ].join(" ")}
                >
                  <option value="">
                    Select a unit type
                  </option>

                  {UNIT_TYPES.map((type) => (
                    <option
                      key={type.value}
                      value={type.value}
                    >
                      {type.label}
                    </option>
                  ))}
                </select>

                {fieldErrors.unit_type && (
                  <p className="mt-1.5 text-sm text-red-600">
                    {fieldErrors.unit_type}
                  </p>
                )}
              </div>
            </div>
          </section>

          <section className="border-t border-slate-200 pt-8">
            <h2 className="text-lg font-semibold text-slate-950">
              Unit Specifications
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Define the size and rental price for this unit.
            </p>

            <div className="mt-5 grid gap-5 sm:grid-cols-3">
              <div>
                <label
                  htmlFor="bedrooms"
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  Bedrooms
                </label>

                <input
                  id="bedrooms"
                  name="bedrooms"
                  type="number"
                  min="0"
                  step="1"
                  value={formData.bedrooms}
                  onChange={handleChange}
                  required
                  className={[
                    "w-full rounded-lg border bg-white px-4 py-3 text-sm text-slate-900 outline-none transition",
                    "focus:border-slate-900 focus:ring-2 focus:ring-slate-900/10",
                    fieldErrors.bedrooms
                      ? "border-red-400"
                      : "border-slate-300",
                  ].join(" ")}
                />

                {fieldErrors.bedrooms && (
                  <p className="mt-1.5 text-sm text-red-600">
                    {fieldErrors.bedrooms}
                  </p>
                )}
              </div>

              <div>
                <label
                  htmlFor="bathrooms"
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  Bathrooms
                </label>

                <input
                  id="bathrooms"
                  name="bathrooms"
                  type="number"
                  min="0"
                  step="0.5"
                  value={formData.bathrooms}
                  onChange={handleChange}
                  required
                  className={[
                    "w-full rounded-lg border bg-white px-4 py-3 text-sm text-slate-900 outline-none transition",
                    "focus:border-slate-900 focus:ring-2 focus:ring-slate-900/10",
                    fieldErrors.bathrooms
                      ? "border-red-400"
                      : "border-slate-300",
                  ].join(" ")}
                />

                {fieldErrors.bathrooms && (
                  <p className="mt-1.5 text-sm text-red-600">
                    {fieldErrors.bathrooms}
                  </p>
                )}
              </div>

              <div>
                <label
                  htmlFor="monthly_rent"
                  className="mb-2 block text-sm font-medium text-slate-700"
                >
                  Monthly rent
                </label>

                <div className="relative">
                  <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-sm text-slate-400">
                    ₱
                  </span>

                  <input
                    id="monthly_rent"
                    name="monthly_rent"
                    type="number"
                    min="0"
                    step="0.01"
                    value={formData.monthly_rent}
                    onChange={handleChange}
                    placeholder="15000.00"
                    required
                    className={[
                      "w-full rounded-lg border bg-white py-3 pl-9 pr-4 text-sm text-slate-900 outline-none transition",
                      "placeholder:text-slate-400 focus:border-slate-900 focus:ring-2 focus:ring-slate-900/10",
                      fieldErrors.monthly_rent
                        ? "border-red-400"
                        : "border-slate-300",
                    ].join(" ")}
                  />
                </div>

                {fieldErrors.monthly_rent && (
                  <p className="mt-1.5 text-sm text-red-600">
                    {fieldErrors.monthly_rent}
                  </p>
                )}
              </div>
            </div>
          </section>

          <section className="border-t border-slate-200 pt-8">
            <h2 className="text-lg font-semibold text-slate-950">
              Description
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Add any additional information about this unit.
            </p>

            <div className="mt-5">
              <label
                htmlFor="description"
                className="mb-2 block text-sm font-medium text-slate-700"
              >
                Unit description
              </label>

              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={5}
                placeholder="Describe the unit..."
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
                  : "Create Unit"}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}

export default UnitForm;