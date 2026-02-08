import React, { useState } from "react";
import { useFormContext } from "../hooks/useFormContext";
import FormInput from "../components/FormInput";
import ErrorAlert from "../components/ErrorAlert";
import { validateField } from "../services/validation";

export default function LicensePlateStep() {
  const { formData, updateField, nextStep, updateErrors } = useFormContext();
  const [value, setValue] = useState(formData.licensePlate || "");
  const [fieldError, setFieldError] = useState("");

  const handleValidation = () => {
    const result = validateField("licensePlate", value.trim());
    if (!result.isValid) {
      setFieldError(result.error);
      return false;
    }
    setFieldError("");
    return true;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (handleValidation()) {
      updateField("licensePlate", value.trim());
      nextStep();
    }
  };

  const handleSkip = () => {
    updateField("licensePlate", "");
    nextStep();
  };

  return (
    <div>
      {fieldError && <ErrorAlert message={fieldError} onClose={() => setFieldError("")} />}
      <form onSubmit={handleSubmit} className="flex flex-col space-y-4">
        <FormInput
          label="License Plate Number"
          name="licensePlate"
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
            setFieldError("");
          }}
          onBlur={handleValidation}
          placeholder="A-000-BB"
          error={fieldError}
          required
        />
        <div className="flex flex-row space-x-2">
          <button className="btn btn-primary btn-sm" type="submit">
            Continue
          </button>
          <button type="button" className="btn btn-secondary btn-sm" onClick={handleSkip}>
            Skip
          </button>
        </div>
      </form>
    </div>
  );
}
