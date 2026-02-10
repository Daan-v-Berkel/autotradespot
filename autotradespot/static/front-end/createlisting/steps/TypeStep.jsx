import React, { useEffect, useState } from "react";
import { useFormContext } from "../hooks/useFormContext";
import FormInput from "../components/FormInput";
import FormSelect from "../components/FormSelect";
import ErrorAlert from "../components/ErrorAlert";
import { fetchListingTypes } from "../services/listingAPI";
import { validateFields } from "../services/validation";

export default function TypeStep() {
  const { formData, updateField, nextStep, prevStep, updateErrors, errors } = useFormContext();
  const [choices, setChoices] = useState([]);
  const [type, setType] = useState(formData.listingType || "S");
  const [title, setTitle] = useState(formData.title || "");
  const [description, setDescription] = useState(formData.description || "");
  const [priceType, setPriceType] = useState(formData.pricing?.priceType || "");
  const [price, setPrice] = useState(formData.pricing?.price || "");
  const [apiError, setApiError] = useState("");

  useEffect(() => {
    let mounted = true;
    fetchListingTypes()
      .then((data) => {
        if (!mounted) return;
        setChoices(
          Array.isArray(data) && data.length
            ? data
            : [
                { value: "S", label: "Sale" },
                { value: "L", label: "Lease" },
              ]
        );
      })
      .catch(() => {
        if (!mounted) return;
        setChoices([
          { value: "S", label: "Sale" },
          { value: "L", label: "Lease" },
        ]);
      });
    return () => (mounted = false);
  }, []);

  const getPriceTypeChoices = () => {
    if (type === "S") {
      return [
        { value: "F", label: "Fixed Price" },
        { value: "N", label: "Negotiable" },
        { value: "O", label: "Open for Bidding" },
      ];
    } else {
      return [
        { value: "P", label: "Private" },
        { value: "O", label: "Operational" },
        { value: "NO", label: "Netto Operational" },
        { value: "F", label: "Financial" },
        { value: "S", label: "Short Term" },
      ];
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const fieldsToValidate = {
      title,
      description,
      listingType: type,
      pricingType: priceType,
      price,
    };

    const { isValid, errors: validationErrors } = validateFields(fieldsToValidate);

    if (!isValid) {
      updateErrors(validationErrors);
      return;
    }

    updateErrors({});
    updateField("title", title);
    updateField("description", description);
    updateField("listingType", type);
    updateField("pricing", { priceType, price });
    nextStep();
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      {apiError && <ErrorAlert message={apiError} onClose={() => setApiError("")} />}

      <FormInput
        label="Listing Title"
        name="title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="e.g. Honda Civic 2020"
        error={errors.title || ""}
        required
      />

      <FormInput
        label="Description"
        name="description"
        type="textarea"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Additional details about the vehicle (optional)"
        error={errors.description || ""}
      />

      <FormSelect
        label="Listing Type"
        name="type"
        value={type}
        onChange={(e) => {
          setType(e.target.value);
          setPriceType("");
        }}
        options={choices}
        error={errors.listingType || ""}
        required
        placeholder="Select listing type"
      />

      <FormSelect
        label="Pricing Type"
        name="priceType"
        value={priceType}
        onChange={(e) => setPriceType(e.target.value)}
        options={getPriceTypeChoices()}
        error={errors.pricingType || ""}
        required
        placeholder="Select pricing type"
      />

      <FormInput
        label="Price"
        name="price"
        type="number"
        value={price}
        onChange={(e) => setPrice(e.target.value)}
        placeholder="0.00"
        error={errors.price || ""}
        required
      />

      <div className="flex flex-row space-x-2 pt-4">
        <button className="btn btn-sm btn-primary" type="button" onClick={prevStep}>
          Back
        </button>
        <button className="btn btn-sm btn-primary" type="submit">
          Continue
        </button>
      </div>
    </form>
  );
}
