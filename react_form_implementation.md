# React Form Implementation Plan - Issue #16

**Created:** February 6, 2026
**Branch:** react_form
**Status:** In Planning

## Overview
Convert the multi-step listing creation form from a brittle mix of HTMX, Hyperscript, and partial React components into a cohesive, maintainable React-based form with centralized state management.

---

## Phase 1: Discovery & Architecture (1-1.5 hours)

### 1.1 Audit Current Implementation
- **Templates:** Review all 7 Django templates in `autotradespot/templates/listings/create/`
- **Views:** Map view logic in `autotradespot/listings/views.py` (lines 52-290)
- **React Components:** Examine existing partial components in `autotradespot/static/front-end/createlisting/`
- **State Management:** Understand session-based multi-step state in `request.session["listing_in_progress"]`
- **Output:** Document current flow, identify data transformations, list all form fields

### 1.2 Design React Component Structure
- Create `ListingFormContainer.jsx` - main wrapper with centralized state management
- Plan sub-components:
  - `LicensePlateStep` - License plate input and validation
  - `TypeStep` - Listing type selection (dropdown)
  - `MakeModelStep` - Car make/model dependent dropdowns
  - `DetailsStep` - Vehicle details (checkboxes, text inputs, optional fields)
  - `ImagesStep` - Multi-file upload with preview and delete
- **State Shape:** Form data, current step, validation errors, loading states
- **Output:** Component hierarchy diagram, state tree structure

---

## Phase 2: Foundation Setup (1.5 hours)

### 2.1 Set Up Component Scaffold
- Create `ListingFormContainer.jsx` with React Context for state
- Stub out all step components with basic structure
- Implement step navigation logic (next/previous/jump to step)
- Set up progress indicator component
- **Output:** Scaffold directory structure, working navigation between empty steps

### 2.2 daisyUI Theme Integration
- Ensure progress indicator uses daisyUI `steps` component
- Create reusable input wrapper component with daisyUI styling
- Set up consistent button styles (daisyUI `btn` classes)
- Design form grid layout using daisyUI's grid system
- **Output:** Styled component library for form fields

### 2.3 Create API Service Layer
- Create `listingAPI.js` with functions:
  - `saveDraft(formData)` - Save current progress to backend
  - `resumeDraft()` - Fetch last saved draft
  - `submitListing(formData)` - Final submission
  - `fetchListingTypes()` - Get available listing types (for #5)
  - `fetchCarMakes()` - Get car makes
  - `fetchCarModels(make)` - Get models for a make
- **Output:** Complete API service module ready for use

---

## Phase 3: Step Implementation (3-4 hours)

### 3.1 Step 1: License Plate
**Components:** `LicensePlateStep.jsx`
- Text input for license plate
- Format validation (EU plate format or custom)
- Client-side validation feedback
- daisyUI styling
- **Output:** Fully functional step

### 3.2 Step 2: Listing Type
**Components:** `TypeStep.jsx`
**Related Issue:** #5 (hardcoded pricing choices)
- Fetch listing types from API (solve #5)
- Dropdown selection
- Display price info if available
- Validation (required field)
- daisyUI styling
- **Output:** Functional step with dynamic data

### 3.3 Step 3: Make/Model
**Components:** `MakeModelStep.jsx`
- Dependent dropdowns (make → model)
- Fetch makes on component mount
- Fetch models when make changes
- Loading states during fetch
- Validation (both required)
- daisyUI styling
- **Output:** Working dependent dropdown step

### 3.4 Step 4: Details
**Components:** `DetailsStep.jsx`, `CheckboxGroup.jsx`, `TextInput.jsx`
- Vehicle details form (condition, mileage, transmission, fuel type, etc.)
- Checkbox groups for selectable features
- Text/number inputs for specs
- Optional vs required field handling
- Client-side validation rules
- daisyUI styling
- **Output:** Complex multi-field step

### 3.5 Step 5: Images
**Components:** `ImagesStep.jsx`, `ImageUpload.jsx`, `ImagePreview.jsx`
- Multi-file upload (drag & drop, file input)
- Image preview grid
- Delete individual images
- Upload progress indicators
- File validation (format, size)
- Loading states
- daisyUI styling
- **Output:** Complete image management step

---

## Phase 4: State & Persistence (1 hour)

### 4.1 Implement State Management
- React Context API with useState for centralized form data
- Context includes:
  - `formData` - All field values
  - `currentStep` - Index of active step (0-4)
  - `errors` - Validation errors by field
  - `isLoading` - API call in progress
  - `isDirty` - Form has unsaved changes
- Hooks: `useFormContext()` for component access
- **Output:** Working context providers and hooks

### 4.2 Form Validation
- Create `validation.js` with rules for each step
- Real-time validation on field change
- Step-level validation before allowing navigation
- Error message mapping
- **Output:** Validation service module

### 4.3 Auto-Save/Draft Persistence
- Save draft on step transition (prev/next)
- Save draft on component unmount
- Load draft on component mount
- Show draft recovery UI if recovering from previous session
- **Output:** Draft persistence logic integrated into context

### 4.4 Loading & Error States
- Show form spinner during API calls
- Display error toasts/alerts for failed operations
- Network error handling with retry capability
- User-friendly error messages
- **Output:** Error boundary component, loading UI patterns

---

## Phase 5: Form Submission & Flow (0.5-1 hour)

### 5.1 Final Submission Logic
- Validate all steps before allowing submission
- Show final confirmation step (optional)
- POST to backend endpoint
- Handle success response with redirect
- Handle error response with field-level feedback
- **Output:** Working form submission

### 5.2 User Flow Testing
- **Flow 1:** Fresh form creation (no existing draft)
  - User starts with Step 1
  - Navigates through all steps
  - Submits successfully
- **Flow 2:** Draft resumption
  - User had draft from previous session
  - Data pre-fills from draft
  - Can continue from last step or from beginning
- **Flow 3:** Step navigation
  - User can go forward and backward
  - User can jump to previous steps
  - Validation prevents incomplete steps
- **Flow 4:** Error recovery
  - Network error during save
  - Shows error message and retry option
  - Preserves form data
- **Output:** Test cases documented and passing

---

## Phase 6: Cleanup & Polish (0.5-1 hour)

### 6.1 Remove Old Implementation
- Delete Django templates from `autotradespot/templates/listings/create/`
- Remove HTMX form handling endpoints from views.py
- Remove Hyperscript DOM manipulation code
- Clean up session state logic
- Update URL routing (if needed) to point to single React component
- **Output:** Old code removed, views simplified

### 6.2 Final Polish
- Verify all daisyUI components match site design
- Test keyboard navigation throughout form
- Add ARIA labels for accessibility
- Test responsive design on mobile/tablet
- Verify button states (hover, active, disabled)
- Test form with slow network (simulated delays)
- **Output:** Polished, accessible component

### 6.3 Documentation
- Document component API (props) for each step component
- Document state shape and context usage
- Add comments for complex logic
- Create usage example in comments
- **Output:** Code comments and inline documentation

---

## 📁 File Structure (Target)

```
autotradespot/static/front-end/createlisting/
├── ListingFormContainer.jsx          (Main container with state)
├── hooks/
│   ├── useFormContext.js             (Context hook)
│   └── useValidation.js              (Validation hook)
├── steps/
│   ├── LicensePlateStep.jsx
│   ├── TypeStep.jsx
│   ├── MakeModelStep.jsx
│   ├── DetailsStep.jsx
│   └── ImagesStep.jsx
├── components/
│   ├── FormInput.jsx                 (Reusable input wrapper)
│   ├── CheckboxGroup.jsx
│   ├── ImageUpload.jsx
│   ├── ImagePreview.jsx
│   ├── ProgressIndicator.jsx
│   ├── StepNavigation.jsx
│   └── ErrorAlert.jsx
├── services/
│   ├── listingAPI.js                 (API calls)
│   └── validation.js                 (Form validation rules)
└── styles/
    └── listing-form.css              (Component-specific styles)
```

---

## 🎯 Implementation Order

```
Phase 1: Audit & Design
    ↓
Phase 2: Scaffold & Setup
    ↓
Phase 3: Implement Steps (1→2→3→4→5)
    ↓
Phase 4: State Management & Persistence
    ↓
Phase 5: Submission & Testing
    ↓
Phase 6: Cleanup & Polish
    ↓
COMPLETE
```

---

## 🔑 Key Technical Decisions

| Decision | Approach | Rationale |
|----------|----------|-----------|
| **State Management** | React Context + useState | Lightweight, no extra dependencies, sufficient for this scope |
| **API Calls** | Custom service module (`listingAPI.js`) | Centralized, easy to mock for testing |
| **Styling** | daisyUI components + custom CSS | Aligns with existing theme, consistent look |
| **Draft Persistence** | Backend session + optional localStorage | Leverage existing backend capability |
| **Validation** | Declarative rules object in `validation.js` | Reusable, testable, easy to maintain |
| **Component Split** | One component per step | Clear responsibility, easier to test and modify |

---

## 📋 Related Issues

- **Issue #5:** Hardcoded lease price choices - Solve in Phase 3.2 by fetching from API
- **Backend:** Existing draft/resume capability is ready - use immediately

---

## ⏱️ Time Estimate

| Phase | Hours | Status |
|-------|-------|--------|
| 1. Discovery & Architecture | 1-1.5 | Not Started |
| 2. Foundation Setup | 1.5 | Not Started |
| 3. Step Implementation | 3-4 | Not Started |
| 4. State & Persistence | 1 | Not Started |
| 5. Form Submission | 0.5-1 | Not Started |
| 6. Cleanup & Polish | 0.5-1 | Not Started |
| **TOTAL** | **7.5-10** | **Not Started** |

---

## ✅ Definition of Done

- [ ] All 5 steps fully implemented and functional
- [ ] Form data persists across sessions (draft/resume)
- [ ] Client-side validation working on all fields
- [ ] daisyUI theme fully applied
- [ ] Keyboard navigation working
- [ ] Mobile responsive design validated
- [ ] All old templates/code removed
- [ ] Error handling complete
- [ ] User flows tested (new form, draft, navigation, submission, errors)
- [ ] Code documented with comments
- [ ] Issue #5 resolved (dynamic pricing choices)
- [ ] All tests passing

---

## 🚀 Success Metrics

1. Form is easier to understand (single source of state, clear component hierarchy)
2. Maintenance is faster (changes isolated to specific step components)
3. User experience is better (client-side validation, smooth navigation, save draft)
4. Code is well-organized and documented
5. No test coverage regression after refactor
