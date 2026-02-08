import React, { createContext, useContext, useState } from "react";
import useAutoSave from "./useAutoSave";

const FormContext = createContext(null);

export function FormProvider({ children }) {
  const [formData, setFormData] = useState({
    licensePlate: "",
    listingType: "S",
    title: "",
    description: "",
    pricing: {},
    make: null,
    model: null,
    variant: "",
    carDetails: {},
    carOptions: [],
    images: [],
  });

  const [currentStep, setCurrentStep] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

  // Auto-save on form data or step changes
  // useAutoSave(formData, currentStep);

  const updateField = (key, value) => {
    setFormData((prev) => ({ ...prev, [key]: value }));
    // Clear error for this field when user starts typing
    if (errors[key]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[key];
        return next;
      });
    }
  };

  const updateErrors = (newErrors) => {
    setErrors(newErrors);
  };

  const clearErrors = () => {
    setErrors({});
  };

  const nextStep = () => setCurrentStep((s) => Math.min(s + 1, 4));
  const prevStep = () => setCurrentStep((s) => Math.max(s - 1, 0));
  const goToStep = (i) => setCurrentStep(() => Math.max(0, Math.min(i, 4)));

  const saveDraft = async () => {
    setIsLoading(true);
    try {
      // TODO: call listingAPI.saveDraft(formData)
    } finally {
      setIsLoading(false);
    }
  };

  const clearForm = () => {
    setFormData({
      licensePlate: "",
      listingType: "S",
      title: "",
      description: "",
      pricing: {},
      make: null,
      model: null,
      variant: "",
      carDetails: {},
      carOptions: [],
      images: [],
    });
    setErrors({});
    setCurrentStep(0);
  };

  return (
    <FormContext.Provider
      value={{
        formData,
        updateField,
        updateErrors,
        clearErrors,
        currentStep,
        nextStep,
        prevStep,
        goToStep,
        saveDraft,
        clearForm,
        isLoading,
        errors,
      }}
    >
      {children}
    </FormContext.Provider>
  );
}

export function useFormContext() {
  const ctx = useContext(FormContext);
  if (!ctx) throw new Error("useFormContext must be used within FormProvider");
  return ctx;
}

export default FormContext;
