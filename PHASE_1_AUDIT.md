# Phase 1: Audit & Discovery - Current Implementation Analysis

**Date:** February 7, 2026
**Branch:** react_form

---

## 1.1 Current Implementation Audit

### Overview
The listing creation form is currently a fragmented implementation mix:
- **7 Django templates** for multi-step form traversal
- **HTMX** for form submission and step navigation
- **Hyperscript** (`_="..."`) for DOM manipulation (adding step-success classes)
- **Session-based state management** using `request.session`
- **Partially-implemented React components** (not integrated into flow)
- **Multiple Django views** handling each step

### File Structure

#### Templates (7 files in `autotradespot/templates/listings/create/`)
```
├── base.html                           # Main form container with progress indicator
├── createlisting.html                  # Index/entry point (NOT USED - redirects)
├── createlistingLP.html                # Step 1: License Plate
├── createlistingtype.html              # Step 2: Listing Type + Pricing
├── createlistingmake.html              # Step 3: Make/Model/Variant
├── createlistingdetails.html           # Step 4: Car Details + Options
└── uploadlistingimages.html            # Step 5: Image Upload
```

#### React Components (5 files in `autotradespot/static/front-end/createlisting/`)
```
├── ListingTypeForm.jsx                 # Partially implemented, NOT integrated
├── ListingMakeForm.jsx                 # Exists but NOT integrated
├── LicencePlateForm.jsx                # Exists but NOT integrated
├── LoadIcon.jsx                        # Loading spinner component
└── baseCreateForm.jsx                  # Base form wrapper (NOT integrated)
```

#### Backend Views (`autotradespot/listings/views.py` lines 52-290+)
```python
- ListingCreateNew()              # Main/index view, handles PUT/DELETE for save/clear
- ListingLicenceplate()           # Step 1: License plate validation + API lookup
- ListingType()                   # Step 2: Type selection + pricing form
- ListingMake()                   # Step 3: Make/model selection
- ListingDetails()                # Step 4: Car details form
- ListingImages()                 # Step 5: Image upload (not fully reviewed)
```

#### Models (`autotradespot/listings/models.py`)
```
Listing
├── type (AdTypes: "S"=Sale, "L"=Lease)
├── title (str)
├── description (text)
├── owner (FK to User)
├── status (Status choices: DRAFT, ACTIVE, etc.)
├── created/modified dates
└── Relations:
    ├── CarDetails (1-to-1)
    ├── PricingModelBuy (1-to-1) - for type="S"
    ├── PricingModelLease (1-to-1) - for type="L"
    └── ImageModel (1-to-many)

CarDetails (car-specific fields)
├── make (FK to CarMake)
├── model (FK to CarModel)
├── variant (str - optional)
├── mileage
├── condition
├── transmission
├── fuel_type
├── num_doors
├── etc.

PricingModelBuy
├── listing (FK to Listing)
├── pricetype ("F"=fixed, "N"=negotiable, "O"=open for bidding)
├── price

PricingModelLease
├── listing (FK to Listing)
├── pricetype ("P"=private, "O"=operational, "NO"=netto operational, "F"=financial, "S"=short)
├── price (monthly)
├── lease_period (DateField)
├── annual_kms

CarMake
├── name

CarModel
├── name
├── make (FK to CarMake)

CarOption (M-to-M with cardetails)
├── name
```

---

### Current Form Flow (Step-by-Step)

#### Step 1: License Plate (createlistingLP.html)
**URL:** `POST /listings/create-licence-plate/`

**Request:**
- POST field: `licenceplate` (text input)

**Backend Logic:**
1. Validate license plate format (Issue #13) - Dutch plate pattern validation
2. Fetch car data from RDW API (2 endpoints)
3. Extract relevant fields into `LP_data` session dict
4. Redirect to Step 2

**Session Data Stored:**
```python
request.session["LP_data"] = {
    "licence": "XX00XX",  # Clean license plate
    "make": "Honda",
    "model": "Civic",
    "year": "2020",
    # ... other fields from API
}
```

**DOM Manipulation:**
```html
_="on click add .step-success to #lp_tab"
```

**Skip Path:** User can skip license plate lookup and go directly to Step 2

#### Step 2: Listing Type + Pricing (createlistingtype.html)
**URL:** `POST /listings/create-type/`

**Request:**
- `type` (choice: "S" or "L")
- If type="S": `PricingSaleForm` fields (pricetype, price)
- If type="L": `PricingLeaseForm` fields (pricetype, price, lease_period, annual_kms)
- `title` (from ListingForm)
- `description` (from ListingForm)

**Backend Logic:**
1. Validate ListingForm (title, description, type)
2. Validate PricingForm (depends on type)
3. Create/update Listing model with form data
4. Create/update PricingModelBuy or PricingModelLease
5. Store `listing.pk` in `request.session["listing_in_progress"]`
6. Redirect to Step 3

**Notes:**
- Initial form values populated from `LP_data` if available
- Form title pre-filled with "Make Model" from license plate lookup

#### Step 3: Make/Model Variant (createlistingmake.html)
**URL:** `POST /listings/create-make/`

**Request:**
- `make` (FK to CarMake)
- `model` (FK to CarModel, filtered by make)
- `variant` (optional text)

**Backend Logic:**
1. Validate CarMakeForm, CarModelForm, VariantForm
2. Store in `LP_data` session dict:
   ```python
   request.session["LP_data"]["makeId"] = selected_make_id
   request.session["LP_data"]["modelId"] = selected_model_id
   request.session["LP_data"]["variant"] = variant_text
   ```
3. Redirect to Step 4

**HTMX Behavior:**
```html
hx-get="{% url 'listings:getmodels' %}"
hx-target="#id_model"
hx-swap="outerHTML"
```
Fetches model options dynamically when make changes

#### Step 4: Car Details + Options (createlistingdetails.html)
**URL:** `POST /listings/create-details/`

**Request:**
- CardetailForm fields (mileage, condition, transmission, fuel_type, etc.)
- CarOptionsForm (multi-checkbox for car features)

**Backend Logic:**
1. Validate both forms
2. Create/update CarDetails model linked to Listing
3. Update CarDetails with make/model/variant from session
4. Create M-to-M relations with selected CarOptions
5. Redirect to Step 5

#### Step 5: Image Upload (uploadlistingimages.html)
**URL:** `POST /listings/upload-images/`

**Request:**
- `image` (MultipleFileField - drag & drop or file input)

**Backend Logic:**
1. Validate image form
2. Process uploaded images (compression via `img_compression.py`)
3. Create ImageModel instances linked to Listing
4. Final confirmation - list can be saved as draft or activated

---

### Session State Management

#### Session Keys Used
```python
request.session["listing_in_progress"]  # Listing.pk (primary key)
request.session["LP_data"]              # Dict with license plate + car data
```

#### Flow Assumptions
- User starts: No session keys set
- After Step 1 (LP): `LP_data` set, `listing_in_progress` not yet
- After Step 2 (Type): `listing_in_progress` created, Listing object in DB
- After Step 3 (Make): LP_data updated with make/model ids
- After Step 4 (Details): CarDetails created, linked to Listing
- After Step 5 (Images): ImageModels created
- Final: User clicks "Save Draft" (PUT) or "Continue" → activates listing

#### Draft/Resume Feature
```python
def ListingCreateNew(request):
    # PUT request with save_method
    if request.method == "PUT" and listing_pk:
        listing.status = listing.Status.DRAFT  # or ACTIVE
        listing.save()

    # DELETE request clears session
    elif request.method == "DELETE":
        clearListingInProgress(request)
```

---

### Current Integration Points

#### Navigation
Main container: `base.html`
```html
<ul class="steps steps-vertical">
  <li class="step" id="lp_tab" hx-get="...licenceplate..." />
  <li class="step" id="title_tab" hx-get="...type..." />
  <li class="step" id="make_tab" hx-get="...make..." />
  <li class="step" id="detail_tab" hx-get="...details..." />
  <li class="step" id="image_tab" hx-get="...images..." />
</ul>
```

#### Style Classes
- `step` - daisyUI progress step
- `step-success` - indicates completed step (added via Hyperscript)

#### Theme
- daisyUI components used: `steps`, `input`, `select`, `btn`, `form-control`, `label`
- TailwindCSS for layout

---

### Existing React Component Analysis

#### ListingTypeForm.jsx
**Status:** Partially implemented, NOT integrated
- Has local state for form data
- Hardcoded pricing type choices (Issue #5)
- Client-side validation
- NOT hooked into existing flow
- Would need to be integrated with backend

**Code Issues:**
```jsx
const typeChoices = [
    {"value": "S", "label": "Sale"},
    {"value": "L", "label": "Lease"}
]
const LeasePriceChoices = [ ... ]  // Hardcoded - TODO: get from backend
```

#### Other React Components
- Exist but are even less complete
- LoadIcon.jsx - reusable loading spinner
- baseCreateForm.jsx - wrapper component (stub)

---

### Known Issues & TODOs

#### Issue #5: Hardcoded Lease Price Choices
**File:** `ListingTypeForm.jsx` line 5-8
**Problem:** Pricing type choices are hardcoded in React component
**Impact:** Inconsistency if backend changes
**Solution:** Fetch from backend API endpoint

#### Issue #13: License Plate Validation
**Status:** ✅ Implemented
- Validates Dutch license plate format
- Provides error messages

#### Issue #14: Error Handling
**Status:** ✅ Implemented
- Comprehensive error handling for API timeouts/failures
- User-friendly error messages

---

## 1.2 Proposed React Component Structure

### Component Hierarchy

```
ListingFormContainer
├── ProgressIndicator
├── FormContent (current step component)
│   ├── LicensePlateStep
│   ├── TypeStep
│   │   ├── FormInput
│   │   └── PriceForm (dynamic based on type)
│   ├── MakeModelStep
│   │   ├── FormSelect (dependent dropdowns)
│   │   └── LoadingSpinner
│   ├── DetailsStep
│   │   ├── CheckboxGroup
│   │   ├── FormInput
│   │   └── FormSelect
│   └── ImagesStep
│       ├── ImageUpload (drag & drop + file input)
│       ├── ImagePreview
│       └── ImageGallery
├── StepNavigation
│   ├── PrevButton
│   └── NextButton
├── FormActions
│   ├── SaveDraftButton
│   ├── ClearButton
│   └── SubmitButton
└── ErrorBoundary
    └── ErrorAlert
```

### State Management

**Using React Context + useState:**

```javascript
const FormContext = createContext({
  // Form data
  formData: {
    licensePlate: "",
    listingType: "S",
    title: "",
    description: "",
    pricing: {},
    make: null,
    model: null,
    variant: "",
    carDetails: {},
    carOptions: [],
    images: []
  },

  // UI state
  currentStep: 0,
  isLoading: false,
  isDirty: false,

  // Validation
  errors: {},

  // Actions
  updateField: (path, value) => {},
  nextStep: () => {},
  prevStep: () => {},
  goToStep: (stepIndex) => {},
  saveDraft: () => {},
  submitForm: () => {},
  clearForm: () => {},
})
```

### Data Flow

**Step Sequence:**
```
Step 0: License Plate
├── Input: license plate string
├── API Call: Fetch car data
├── Store: LP_data in formData
└── Persist: Save draft to backend

Step 1: Listing Type
├── Input: type (S/L), pricing details
├── Store: type, pricing in formData
└── Persist: Save draft, create/update Listing

Step 2: Make/Model/Variant
├── Input: make, model, variant
├── API Call: Fetch models based on make
├── Store: make, model, variant in formData
└── Persist: Save draft

Step 3: Car Details
├── Input: mileage, condition, features
├── Store: carDetails, carOptions in formData
└── Persist: Save draft, create/update CarDetails

Step 4: Images
├── Input: multiple image files
├── Process: Upload to backend
├── Store: images in formData
└── Persist: Save draft, create ImageModels

SUBMIT
└── Create/update all models
└── Set listing status to ACTIVE or DRAFT
└── Redirect to listing detail page
```

### API Service Layer

**New endpoints needed (or adapt existing):**

```javascript
// listingAPI.js
export const listingAPI = {
  // License plate lookup
  fetchCarData: (licensePlate) => POST /api/listings/car-data/,

  // Get pricing type choices
  fetchListingTypes: () => GET /api/listings/types/,
  fetchPricingChoices: (type) => GET /api/listings/pricing-choices/?type=,

  // Get make/model options
  fetchCarMakes: () => GET /api/listings/car-makes/,
  fetchCarModels: (makeId) => GET /api/listings/car-models/?make=,

  // Get car detail options
  fetchCarOptions: () => GET /api/listings/car-options/,

  // Form persistence
  saveDraft: (formData) => POST /api/listings/draft/,
  resumeDraft: (listingId?) => GET /api/listings/draft/,

  // Image operations
  uploadImages: (listingId, files) => POST /api/listings/:id/images/upload/,
  deleteImage: (imageId) => DELETE /api/listings/images/:id/,

  // Final submission
  submitListing: (formData) => POST /api/listings/,
  updateListing: (listingId, formData) => PUT /api/listings/:id/,
}
```

### Validation Rules

**validation.js - Step-by-step validation:**

```javascript
export const validation = {
  // Step 0
  licensePlate: (value) => {
    // Dutch plate format check
    // Return: { isValid: bool, error: string }
  },

  // Step 1
  nameTitle: (value) => { /* required, min 5 chars */ },
  description: (value) => { /* max 3000 chars, optional */ },
  listingType: (value) => { /* required, S or L */ },
  pricingType: (value) => { /* required */ },
  price: (value) => { /* required, numeric, > 0 */ },
  leaseDetails: (data) => { /* lease-specific validation */ },

  // Step 2
  make: (value) => { /* required */ },
  model: (value) => { /* required */ },
  variant: (value) => { /* optional */ },

  // Step 3
  carDetails: (data) => { /* mileage, condition, transmission, etc. */ },

  // Step 4
  images: (files) => { /* at least 1 image, format/size validation */ },
}
```

---

## Summary Table

| Aspect | Current | New Plan |
|--------|---------|----------|
| **Navigation** | HTMX + Hyperscript | React state |
| **State Management** | Django session | React Context |
| **Step Components** | Django templates | React components |
| **Forms** | Django forms | React forms |
| **Validation** | Server-side | Client + Server |
| **Styling** | daisyUI via Django | daisyUI via React |
| **Draft Persistence** | Backend session | Backend API + local state |

---

## Output Files

- ✅ Current implementation understood and documented
- ✅ Component hierarchy designed
- ✅ State shape proposed
- ✅ API service endpoints identified
- ✅ Validation rules outlined

**Next Step:** Phase 2 - Foundation Setup
