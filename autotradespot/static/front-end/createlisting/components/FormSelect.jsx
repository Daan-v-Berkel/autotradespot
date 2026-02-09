import React from "react";

/**
 * Reusable form select component with daisyUI styling and error display
 */
export default function FormSelect({
  label,
  name,
  value = "",
  onChange,
  onBlur,
  options = [],
  error = "",
  required = false,
  disabled = false,
  placeholder = "Select an option",
  className = "",
}) {
  return (
    <label className="form-control w-full">
      <div className="label">
        <span className="label-text text-base-content">
          {label}
          {required && <span className="text-error ml-1">*</span>}
        </span>
      </div>
      <select
        name={name}
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        disabled={disabled}
				key={"select" + name}
        className={`select select-bordered select-sm w-full ${
          error ? "select-error" : ""
        } ${className}`}
      >
        <option value="" disabled>{placeholder}</option>
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && <div className="label">
        <span className="label-text-alt text-error">{error}</span>
      </div>}
    </label>
  );
}
