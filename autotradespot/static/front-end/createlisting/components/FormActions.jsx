import React from "react";
import { useFormContext } from "../hooks/useFormContext";

export default function FormActions() {
  const { saveDraft, isLoading, removeDraft } = useFormContext();

  const handleSaveDraft = async () => {
    await saveDraft();
    alert("Draft saved successfully");
  };

  const handleRemoveDraft = async () => {
    if (window.confirm("Are you sure you want to remove the draft?")) {
      await removeDraft();
      alert("Draft removed successfully");
    }
  };

  const handleClear = () => {
    if (window.confirm("Are you sure you want to clear all data?")) {
			// TODO: Optionally send API request to delete draft on backend before clearing form
      removeDraft();
    }
  };

  return (
    <div id="adform_actions" className="flex flex-row space-x-4 mt-4">
      <button
        className="btn btn-sm btn-outline btn-error"
        onClick={handleClear}
        disabled={isLoading}
      >
        <span className="ti-eraser"></span> Clear Draft
      </button>
      <button
        className="btn btn-sm btn-outline btn-secondary"
        onClick={handleSaveDraft}
        disabled={isLoading}
      >
        {isLoading ? "Saving..." : "Continue later"}
      </button>
    </div>
  );
}
