const API_BASE = "/api/listings";

export async function saveDraft(data) {
  const res = await fetch(`${API_BASE}/draft/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to save draft");
  return res.json();
}

export async function resumeDraft() {
  const res = await fetch(`${API_BASE}/draft/`, { method: "GET" });
  if (!res.ok) throw new Error("Failed to fetch draft");
  return res.json();
}

export async function fetchListingTypes() {
  const res = await fetch(`${API_BASE}/types/`);
  if (!res.ok) throw new Error("Failed to fetch listing types");
  return res.json();
}

export async function fetchCarMakes() {
  const res = await fetch(`${API_BASE}/car-makes/`);
  if (!res.ok) throw new Error("Failed to fetch car makes");
  return res.json();
}

export async function fetchCarModels(makeId) {
  const res = await fetch(`${API_BASE}/car-models/?make=${encodeURIComponent(makeId)}`);
  if (!res.ok) throw new Error("Failed to fetch car models");
  return res.json();
}

export async function uploadImages(images) {
  // images is an array of objects with { id, file, preview, name }
  // Create FormData for multipart file upload
  const formData = new FormData();
  for (const image of images) {
    formData.append("images", image.file, image.name);
  }

  const res = await fetch(`${API_BASE}/images/upload/`, {
    method: "POST",
    body: formData,
    // Note: do NOT set Content-Type header; browser will set it with boundary
  });
  if (!res.ok) throw new Error("Failed to upload images");
  return res.json();
}
