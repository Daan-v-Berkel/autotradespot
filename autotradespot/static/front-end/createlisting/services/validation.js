/**
 * Validation rules for each step of the listing form
 * Returns: { isValid: bool, error: string }
 */

export const validation = {
  licensePlate: (value) => {
    if (!value || !value.trim()) {
      return { isValid: false, error: "License plate cannot be empty" };
    }
    const cleaned = value.replace(/[-\s]/g, "").toUpperCase();
    if (cleaned.length !== 6) {
      return { isValid: false, error: "License plate must be 6 characters" };
    }
    if (!/^[A-Z0-9]{6}$/.test(cleaned)) {
      return { isValid: false, error: "License plate must contain only letters and numbers" };
    }
    return { isValid: true, error: "" };
  },

  listingType: (value) => {
    if (!value || !["S", "L"].includes(value)) {
      return { isValid: false, error: "Please select a valid listing type" };
    }
    return { isValid: true, error: "" };
  },

  title: (value) => {
    if (!value || value.trim().length < 5) {
      return { isValid: false, error: "Title must be at least 5 characters" };
    }
    if (value.length > 255) {
      return { isValid: false, error: "Title must be 255 characters or less" };
    }
    return { isValid: true, error: "" };
  },

  description: (value) => {
    if (value && value.length > 3000) {
      return { isValid: false, error: "Description must be 3000 characters or less" };
    }
    return { isValid: true, error: "" };
  },

  price: (value) => {
    if (!value || value === "") {
      return { isValid: false, error: "Price is required" };
    }
    const num = parseFloat(value);
    if (isNaN(num) || num < 0) {
      return { isValid: false, error: "Price must be a valid positive number" };
    }
    return { isValid: true, error: "" };
  },

  pricingType: (value) => {
    if (!value) {
      return { isValid: false, error: "Please select a pricing type" };
    }
    return { isValid: true, error: "" };
  },

  make: (value) => {
    if (!value) {
      return { isValid: false, error: "Please select a car make" };
    }
    return { isValid: true, error: "" };
  },

  model: (value) => {
    if (!value) {
      return { isValid: false, error: "Please select a car model" };
    }
    return { isValid: true, error: "" };
  },

  mileage: (value) => {
    if (value === "" || value === null) {
      return { isValid: false, error: "Mileage is required" };
    }
    const num = parseInt(value, 10);
    if (isNaN(num) || num < 0) {
      return { isValid: false, error: "Mileage must be a valid number" };
    }
    return { isValid: true, error: "" };
  },

  images: (files) => {
    if (!files || files.length === 0) {
      return { isValid: false, error: "At least one image is required" };
    }
    return { isValid: true, error: "" };
  },
};

/**
 * Validate a field by name
 */
export function validateField(fieldName, value) {
  const validator = validation[fieldName];
  if (!validator) {
    return { isValid: true, error: "" };
  }
  return validator(value);
}

/**
 * Validate multiple fields (for step validation)
 */
export function validateFields(fieldMap) {
  const errors = {};
  let isValid = true;

  for (const [fieldName, value] of Object.entries(fieldMap)) {
    const result = validateField(fieldName, value);
    if (!result.isValid) {
      errors[fieldName] = result.error;
      isValid = false;
    }
  }

  return { isValid, errors };
}
