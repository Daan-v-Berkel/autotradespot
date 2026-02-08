import React from "react";
import { FormProvider, useFormContext } from "./hooks/useFormContext";
import ProgressIndicator from "./components/ProgressIndicator";
import FormActions from "./components/FormActions";
import LicensePlateStep from "./steps/LicensePlateStep";
import TypeStep from "./steps/TypeStep";
import MakeModelStep from "./steps/MakeModelStep";
import DetailsStep from "./steps/DetailsStep";
import ImagesStep from "./steps/ImagesStep";

const steps = [LicensePlateStep, TypeStep, MakeModelStep, DetailsStep, ImagesStep];

function StepRenderer() {
  const { currentStep } = useFormContext();
  const Step = steps[currentStep] || (() => <div>Unknown step</div>);
  return <Step />;
}

function FormContent() {
  const { prevStep, currentStep } = useFormContext();

  return (
    <div className="join-item flex flex-col justify-between w-full bg-base-200 p-4 rounded-box border-2 border-l-0 border-base-300">
      <div id="tabcontent">
        <StepRenderer />
      </div>
      <div className="flex flex-row justify-between items-end mt-6">
        <div>
          {currentStep > 0 && (
            <button className="btn btn-outline" onClick={prevStep}>
              Back
            </button>
          )}
        </div>
        <FormActions />
      </div>
    </div>
  );
}

export default function ListingFormContainer() {
  return (
    <FormProvider>
      <div className="join flex flex-row my-4 mx-auto min-w-full">
        <ProgressIndicator />
        <FormContent />
      </div>
    </FormProvider>
  );
}
