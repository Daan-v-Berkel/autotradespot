import React, { useEffect, useState } from "react";
import { useFormContext } from "../hooks/useFormContext";
import FormSelect from "../components/FormSelect";
import FormInput from "../components/FormInput";
import ErrorAlert from "../components/ErrorAlert";
import { fetchCarMakes, fetchCarModels } from "../services/listingAPI";
import { validateFields } from "../services/validation";

export default function MakeModelStep() {
  const { formData, updateField, nextStep, prevStep, updateErrors, errors } = useFormContext();
  const [makes, setMakes] = useState([]);
  const [models, setModels] = useState([]);
  const [loadingMakes, setLoadingMakes] = useState(true);
  const [loadingModels, setLoadingModels] = useState(false);
  const [selectedMake, setSelectedMake] = useState(formData.make || "");
  const [selectedModel, setSelectedModel] = useState(formData.model || "");
  const [variant, setVariant] = useState(formData.variant || "");
  const [apiError, setApiError] = useState("");

  // Fetch car makes on mount
  useEffect(() => {
    let mounted = true;
    setLoadingMakes(true);
    fetchCarMakes()
      .then((data) => {
        if (!mounted) return;
        // Handle array of { id, name } objects
        const makesList = Array.isArray(data)
          ? data.map((m) => ({ value: m.id || m.pk, label: m.name }))
          : [];
        setMakes(makesList);
      })
      .catch((err) => {
        if (!mounted) return;
        console.error("Failed to fetch makes:", err);
        setApiError("Failed to load car makes. Please try again.");
      })
      .finally(() => {
        if (mounted) setLoadingMakes(false);
      });

    return () => (mounted = false);
  }, []);

  // Fetch models when make changes
  useEffect(() => {
    if (!selectedMake) {
      setModels([]);
      setSelectedModel("");
      return;
    }

    let mounted = true;
    setLoadingModels(true);
    fetchCarModels(selectedMake)
      .then((data) => {
        if (!mounted) return;
        const modelsList = Array.isArray(data)
          ? data.map((m) => ({ value: m.id || m.pk, label: m.name }))
          : [];
        setModels(modelsList);
        setSelectedModel("");
      })
      .catch((err) => {
        if (!mounted) return;
        console.error("Failed to fetch models:", err);
        setApiError("Failed to load car models. Please try again.");
      })
      .finally(() => {
        if (mounted) setLoadingModels(false);
      });

    return () => (mounted = false);
  }, [selectedMake]);

  const handleSubmit = (e) => {
    e.preventDefault();

    const { isValid, errors: validationErrors } = validateFields({
      make: selectedMake,
      model: selectedModel,
    });

    if (!isValid) {
      updateErrors(validationErrors);
      return;
    }

    updateErrors({});
    updateField("make", selectedMake);
    updateField("model", selectedModel);
    updateField("variant", variant);
    nextStep();
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      {apiError && <ErrorAlert message={apiError} onClose={() => setApiError("")} />}

      <FormSelect
        label="Car Make"
        name="make"
        value={selectedMake}
        onChange={(e) => setSelectedMake(e.target.value)}
        options={makes}
        error={errors.make || ""}
        required
        disabled={loadingMakes}
        placeholder={loadingMakes ? "Loading..." : "Select car make"}
      />

      <FormSelect
        label="Car Model"
        name="model"
        value={selectedModel}
        onChange={(e) => setSelectedModel(e.target.value)}
        options={models}
        error={errors.model || ""}
        required
        disabled={loadingModels || !selectedMake}
        placeholder={loadingModels ? "Loading..." : !selectedMake ? "Select a make first" : "Select model"}
      />

      <FormInput
        label="Variant (Optional)"
        name="variant"
        value={variant}
        onChange={(e) => setVariant(e.target.value)}
        placeholder="e.g. PHEV, GT, Sport"
      />

      <div className="flex flex-row space-x-2 pt-4">
        <button type="button" className="btn btn-outline" onClick={prevStep}>
          Back
        </button>
        <button className="btn btn-primary" type="submit">
          Continue
        </button>
      </div>
    </form>
  );
}
