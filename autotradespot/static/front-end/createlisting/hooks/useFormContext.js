import React, { createContext, useContext, useState, useEffect } from "react";
import useAutoSave from "./useAutoSave";
import * as listingAPI from "../services/listingAPI";

const FormContext = createContext(null);

export function FormProvider({ children }) {
  const [formData, setFormData] = useState({
    listing_pk: null,
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
  useAutoSave(formData, currentStep);

  // Try to resume an existing draft when provider mounts
  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await listingAPI.resumeDraft();
        if (!mounted) return;
        if (res && res.listing_pk) {
          setFormData((prev) => ({ ...prev, ...res, listing_pk: res.listing_pk }));
        }
      } catch (e) {
        // ignore — no draft or unauthenticated
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

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
      // Normalize front-end formData into the API payload shape
      const pricePayload = (function() {
        const p = formData.pricing || {};
        if (!p) return {};
        // front-end uses { priceType, price } keys for sale; backend expects {pricetype, price}
        const common = {
          pricetype: p.priceType || p.pricetype || "F",
          price: p.price || p.price === 0 ? p.price : undefined,
        };
        // lease-specific keys
        if (formData.listingType === "L") {
          return {
            ...common,
            annual_kms: p.annual_kms || p.annualKms || p.annualKms || undefined,
            lease_company: p.lease_company || p.leaseCompany || undefined,
            lease_period: p.lease_period || p.leasePeriod || undefined,
          };
        }
        return common;
      })();

      const carDetailsPayload = (function() {
        const cd = formData.carDetails || {};
        return {
          make_id: formData.make || cd.make_id || cd.make || null,
          model_id: formData.model || cd.model_id || cd.model || null,
          mileage: cd.mileage || cd.mileage === 0 ? cd.mileage : undefined,
          manufacture_year: cd.manufacture_year || cd.manufactureYear || undefined,
        };
      })();

      const payload = {
        listing_pk: formData.listing_pk,
        title: formData.title,
        description: formData.description,
        type: formData.listingType,
        price: pricePayload,
        car_details: carDetailsPayload,
        // additional optional metadata
        car_options: formData.carOptions || [],
        images: (formData.images || []).map((img) => ({ name: img.name || img.filename || img.id })),
        license_plate: formData.licensePlate || null,
      };

      const res = await listingAPI.saveDraft(payload);
      if (res && res.listing_pk) {
        setFormData((prev) => ({ ...prev, listing_pk: res.listing_pk }));
      }
    } finally {
      setIsLoading(false);
    }
  };

  const clearForm = () => {
    setFormData((prev) => ({
			...prev,
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
    }));
    setErrors({});
    setCurrentStep(0);
  };

	const removeDraft = async () => {
		if (!formData.listing_pk) return;
		setIsLoading(true);
		try {
			await listingAPI.removeDraft(formData.listing_pk);
			clearForm();
		} finally {
			setIsLoading(false);
		}
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
				removeDraft,
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
