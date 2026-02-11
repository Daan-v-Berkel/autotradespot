import React, { useState } from "react";
import { useFormContext } from "../hooks/useFormContext";
import FormInput from "../components/FormInput";
import FormSelect from "../components/FormSelect";
import ErrorAlert from "../components/ErrorAlert";
import { validateField } from "../services/validation";

export default function DetailsStep() {
  const { formData, updateField, nextStep, prevStep, updateErrors, errors } = useFormContext();
  const [mileage, setMileage] = useState(formData.carDetails?.mileage || "");
  const [condition, setCondition] = useState(formData.carDetails?.condition || "good");
  const [transmission, setTransmission] = useState(formData.carDetails?.transmission || "manual");
  const [fuelType, setFuelType] = useState(formData.carDetails?.fuel_type || "petrol");
  const [numDoors, setNumDoors] = useState(formData.carDetails?.num_doors || "4");
  const [colorExterior, setColorExterior] = useState(formData.carDetails?.color_exterior || "");
  const [colorInterior, setColorInterior] = useState(formData.carDetails?.color_interior || "");
  const [engine, setEngine] = useState(formData.carDetails?.engine || "");
  const [apiError, setApiError] = useState("");

  const conditionChoices = [
    { value: "excellent", label: "Excellent" },
    { value: "good", label: "Good" },
    { value: "fair", label: "Fair" },
    { value: "poor", label: "Poor" },
  ];

  const transmissionChoices = [
    { value: "manual", label: "Manual" },
    { value: "automatic", label: "Automatic" },
    { value: "cvt", label: "CVT" },
  ];

  const fuelTypeChoices = [
    { value: "petrol", label: "Petrol" },
    { value: "diesel", label: "Diesel" },
    { value: "hybrid", label: "Hybrid" },
    { value: "electric", label: "Electric" },
    { value: "lpg", label: "LPG" },
  ];

  const doorsChoices = [
    { value: "2", label: "2 Doors" },
    { value: "3", label: "3 Doors" },
    { value: "4", label: "4 Doors" },
    { value: "5", label: "5 Doors" },
  ];

  const handleSubmit = (e) => {
    e.preventDefault();

    // Validate mileage
    const mileageValidation = validateField("mileage", mileage);
    if (!mileageValidation.isValid) {
      updateErrors({ mileage: mileageValidation.error });
      return;
    }

    updateErrors({});
    updateField("carDetails", {
      mileage,
      condition,
      transmission,
      fuel_type: fuelType,
      num_doors: numDoors,
      color_exterior: colorExterior,
      color_interior: colorInterior,
      engine,
    });
    nextStep();
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      {apiError && <ErrorAlert message={apiError} onClose={() => setApiError("")} />}

      <FormInput
        label="Mileage (km)"
        name="mileage"
        type="number"
        value={mileage}
        onChange={(e) => setMileage(e.target.value)}
        placeholder="e.g. 150000"
        error={errors.mileage || ""}
        required
      />

      <FormSelect
        label="Condition"
        name="condition"
        value={condition}
        onChange={(e) => setCondition(e.target.value)}
        options={conditionChoices}
      />

      <FormSelect
        label="Transmission"
        name="transmission"
        value={transmission}
        onChange={(e) => setTransmission(e.target.value)}
        options={transmissionChoices}
      />

      <FormSelect
        label="Fuel Type"
        name="fuelType"
        value={fuelType}
        onChange={(e) => setFuelType(e.target.value)}
        options={fuelTypeChoices}
      />

      <FormSelect
        label="Number of Doors"
        name="numDoors"
        value={numDoors}
        onChange={(e) => setNumDoors(e.target.value)}
        options={doorsChoices}
      />

      <FormInput
        label="Exterior Color"
        name="colorExterior"
        value={colorExterior}
        onChange={(e) => setColorExterior(e.target.value)}
        placeholder="e.g. Silver, Black, White"
      />

      <FormInput
        label="Interior Color"
        name="colorInterior"
        value={colorInterior}
        onChange={(e) => setColorInterior(e.target.value)}
        placeholder="e.g. Black, Leather, Cloth"
      />

      <FormInput
        label="Engine (Optional)"
        name="engine"
        value={engine}
        onChange={(e) => setEngine(e.target.value)}
        placeholder="e.g. 2.0L Turbo"
      />

      <div className="flex flex-row space-x-2 pt-4">
        <button type="button" className="btn btn-outline btn-sm" onClick={prevStep}>
          Back
        </button>
        <button className="btn btn-primary btn-sm" type="submit">
          Continue
        </button>
      </div>
    </form>
  );
}
