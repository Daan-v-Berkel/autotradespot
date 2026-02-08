import React from "react";
import { useFormContext } from "../hooks/useFormContext";

const labels = ["Licenceplate", "Type", "Make/Model", "Details", "Images"];

export default function ProgressIndicator() {
  const { currentStep, goToStep } = useFormContext();

  return (
    <ul className="join-item steps steps-vertical overflow-x-hidden bg-base-200 max-h-fit border-2 border-base-300 mb-auto md:w-full max-w-fit px-2 md:pr-8">
      {labels.map((label, i) => (
        <li
          key={i}
          role="tab"
          className={`step cursor-pointer ${i < currentStep ? "step-success" : i === currentStep ? "step-primary" : ""}`}
          onClick={() => goToStep(i)}
        >
          <span className="hidden md:block text-sm text-base-content">{label}</span>
        </li>
      ))}
    </ul>
  );
}
