import React, { useRef, useState } from "react";
import { useFormContext } from "../hooks/useFormContext";
import ErrorAlert from "../components/ErrorAlert";
import { uploadImages } from "../services/listingAPI";

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"];

export default function ImagesStep() {
  const { formData, updateField, nextStep, prevStep, updateErrors, errors } = useFormContext();
  const [images, setImages] = useState(formData.images || []);
  const [dragActive, setDragActive] = useState(false);
  const [validationError, setValidationError] = useState("");
  const fileInputRef = useRef(null);

  const validateFile = (file) => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      return { ok: false, error: "Only JPEG, PNG, and WebP images are allowed" };
    }
    if (file.size > MAX_FILE_SIZE) {
      return { ok: false, error: "File size must be less than 5MB" };
    }
    return { ok: true };
  };

  const handleFiles = (fileList) => {
    setValidationError("");
    const newFiles = Array.from(fileList);
    const candidates = [];

    for (const file of newFiles) {
      const res = validateFile(file);
      if (!res.ok) {
        setValidationError(res.error);
        // skip invalid files but continue checking others
        continue;
      }
      candidates.push(file);
    }

    if (candidates.length === 0) return;
		console.log("Valid files to upload:", candidates);

    const loaded = [];
    let remaining = candidates.length;
    for (const file of candidates) {
			console.log(`Processing file: ${file.name} (${file.type}, ${file.size} bytes)`);
      const reader = new FileReader();
      reader.onload = (e) => {
        loaded.push({
          id: Math.random().toString(36).substr(2, 9),
          file,
          preview: e.target.result,
          name: file.name,
        });
        remaining -= 1;
				console.log(`Loaded preview for ${file.name}, ${remaining} remaining...`);
        if (remaining === 0) {
          // Once all file previews are ready, attempt upload but always show previews
          (async () => {
            try {
              console.log("Uploading images to API...", loaded.map((l) => l.name));
              const resp = await uploadImages(loaded);
              console.log("uploadImages response:", resp);
            } catch (err) {
              console.error("Failed to upload images:", err);
              setValidationError("Failed to upload images. Please try again.");
            } finally {
              // Always update UI with previews even if upload fails (server may be added later)
              setImages((prev) => [...prev, ...loaded]);
            }
          })();
        }
      };
      reader.readAsDataURL(file);
    }

    // Reset file input so same file can be selected again
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    handleFiles(e.dataTransfer.files);
		console.log("Dropped files:", e.dataTransfer.files);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = () => {
    setDragActive(false);
  };

  const deleteImage = (id) => {
    setImages((prev) => prev.filter((img) => img.id !== id));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (images.length === 0) {
      updateErrors({ images: "At least one image is required" });
      setValidationError("Please upload at least one image");
      return;
    }

    updateErrors({});
    updateField("images", images);
    nextStep();
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      {validationError && (
        <ErrorAlert message={validationError} onClose={() => setValidationError("")} />
      )}
      {errors.images && (
        <ErrorAlert message={errors.images} onClose={() => updateErrors({})} />
      )}

      <label
        htmlFor="file-input"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors block ${
          dragActive
            ? "border-primary bg-primary bg-opacity-10"
            : "border-base-300 bg-base-100 hover:border-primary"
        }`}
      >
        <input
          id="file-input"
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/jpeg,image/png,image/webp"
          onChange={(e) => handleFiles(e.target.files)}
          className="hidden"
        />
        <div className="flex flex-col items-center gap-2 pointer-events-none">
          <svg className="w-16 h-16 text-base-400" width="64" height="64" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p className="text-base font-semibold">Drag and drop images here</p>
          <p className="text-sm text-base-500">or click to select files</p>
          <p className="text-xs text-base-400 mt-2">Supported formats: JPEG, PNG, WebP (max 5MB per image)</p>
        </div>
      </label>

      {images.length > 0 && (
        <div>
          <label className="label">
            <span className="label-text font-semibold">Selected Images ({images.length})</span>
          </label>
          <div className="flex flex-row flex-wrap gap-4">
            {images.map((img) => (
              <div key={img.id} className="relative max-w-fit">
                <button type="button" onClick={() => deleteImage(img.id)} className="btn btn-circle btn-sm btn-error opacity-0 group-hover:opacity-100 transition-opacity absolute top-2 right-2">✕</button>
                <img src={img.preview} alt={img.name} className="w-32 h-32 object-cover rounded-lg border border-base-300" />
                <p className="text-xs text-base-500 mt-1 truncate">{img.name}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex flex-row space-x-2 pt-4">
        <button type="button" className="btn btn-outline" onClick={prevStep}>Back</button>
        <button className="btn btn-primary" type="submit">{images.length > 0 ? "Continue to Review" : "Continue"}</button>
      </div>
    </form>
  );
}
