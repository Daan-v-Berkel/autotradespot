import React from "react";
import { useFormContext } from "../hooks/useFormContext";

export default function FormActions() {
  const { saveDraft, isLoading } = useFormContext();

  const handleSaveDraft = async () => {
    await saveDraft();
    alert("Draft saved successfully");
  };

  const handleClear = () => {
    if (window.confirm("Are you sure you want to clear all data?")) {
      // TODO: call clearForm action
      window.location.reload();
    }
  };

  return (
    <div id="adform_actions" className="flex flex-row space-x-4 mt-4">
      <button
        className="btn btn-secondary"
        onClick={handleClear}
        disabled={isLoading}
      >
        <span className="ti-eraser"></span> Clear
      </button>
      <button
        className="btn btn-outline btn-secondary"
        onClick={handleSaveDraft}
        disabled={isLoading}
      >
        {isLoading ? "Saving..." : "Continue later"}
      </button>
    </div>
  );
}
