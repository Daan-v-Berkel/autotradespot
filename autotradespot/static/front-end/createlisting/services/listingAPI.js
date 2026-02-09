const API_BASE = "/api/";

function getCookie(name) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
  if (match) return decodeURIComponent(match[2]);
  return null;
}

const defaultFetchOpts = { credentials: 'same-origin' };

export async function saveDraft(data) {
  const csrfToken = getCookie('csrftoken');

  const res = await fetch(`${API_BASE}listings/draft/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken || ""
    },
    body: JSON.stringify(data),
    ...defaultFetchOpts,
  });

  if (!res.ok) {
    const errText = await res.text();
    console.error("[saveDraft] Error response:", errText);
    throw new Error(`Failed to save draft: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export async function resumeDraft() {
  const csrfToken = getCookie('csrftoken');

  const res = await fetch(`${API_BASE}listings/draft/`, {
    method: "GET",
    headers: { "X-CSRFToken": csrfToken || "" },
    ...defaultFetchOpts
  });

  if (!res.ok && res.status !== 204) {
    const errText = await res.text();
    console.error("[resumeDraft] Error response:", errText);
    throw new Error(`Failed to fetch draft: ${res.status}`);
  }
  if (res.status === 204) return {};
  return res.json();
}

export async function fetchListingTypes() {
  const res = await fetch(`${API_BASE}listings/types/`);
  if (!res.ok) throw new Error("Failed to fetch listing types");
  return res.json();
}

export async function fetchCarMakes() {
  const res = await fetch(`${API_BASE}car/makes/`, { ...defaultFetchOpts });
  if (!res.ok) throw new Error("Failed to fetch car makes");
  return res.json();
}

export async function fetchCarModels(makeId) {
  const res = await fetch(`${API_BASE}car/models/?make=${encodeURIComponent(makeId)}`, { ...defaultFetchOpts });
  if (!res.ok) throw new Error("Failed to fetch car models");
  return res.json();
}

export async function uploadImages(images, listing_pk = null) {
  // images is an array of objects with { id, file, preview, name }
  const formData = new FormData();
  for (const image of images) {
    formData.append("image", image.file, image.name);
  }
  if (listing_pk) formData.append("listing_pk", listing_pk);

  const res = await fetch(`${API_BASE}listings/images/upload/`, {
    method: "POST",
    body: formData,
    headers: { "X-CSRFToken": getCookie('csrftoken') },
    ...defaultFetchOpts,
  });
  if (!res.ok) throw new Error("Failed to upload images");
  return res.json();
}
