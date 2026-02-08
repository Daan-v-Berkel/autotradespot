import React from "react";

/**
 * Reusable form input component with daisyUI styling and error display
 * Supports text, number, email, password, and textarea types
 */
export default function FormInput({
  label,
  name,
  type = "text",
  value = "",
  onChange,
  onBlur,
  placeholder = "",
  error = "",
  required = false,
  disabled = false,
  className = "",
  rows = 3,
}) {
  const isTextarea = type === "textarea";

  return (
    <label className="form-control w-full">
      <div className="label">
        <span className="label-text text-base-content">
          {label}
          {required && <span className="text-error ml-1">*</span>}
        </span>
      </div>
      {isTextarea ? (
        <textarea
          name={name}
          value={value}
          onChange={onChange}
          onBlur={onBlur}
          placeholder={placeholder}
          disabled={disabled}
          rows={rows}
          className={`textarea textarea-bordered textarea-sm w-full ${
            error ? "textarea-error" : ""
          } ${className}`}
        />
      ) : (
        <input
          type={type}
          name={name}
          value={value}
          onChange={onChange}
          onBlur={onBlur}
          placeholder={placeholder}
          disabled={disabled}
          className={`input input-bordered input-sm w-full ${
            error ? "input-error" : ""
          } ${className}`}
        />
      )}
      {error && <div className="label">
        <span className="label-text-alt text-error">{error}</span>
      </div>}
    </label>
  );
}
