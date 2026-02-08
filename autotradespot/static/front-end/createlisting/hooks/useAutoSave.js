import { useEffect } from "react";
import { saveDraft } from "../services/listingAPI";

/**
 * Hook to auto-save form data to backend on step change
 */
export function useAutoSave(formData, currentStep) {
  useEffect(() => {
    let timeoutId;

    const performSave = async () => {
      try {
        await saveDraft(formData);
        console.log("Draft saved at step", currentStep);
      } catch (error) {
        console.error("Failed to auto-save draft:", error);
        // Silently fail; user can manually save if needed
      }
    };

    // Debounce save by 1 second to avoid excessive API calls
    timeoutId = setTimeout(performSave, 1000);

    return () => clearTimeout(timeoutId);
  }, [formData, currentStep]);
}

export default useAutoSave;
