# AutoTradeSpot - Issues & TODOs for MVP Launch

**Last Updated:** February 6, 2026
**Status:** MVP Final Sprint

---

## 🔴 CRITICAL / BLOCKING FOR MVP

### 11. **Email Configuration** - 🔴 CRITICAL - TODO before MVP launch
- **File:** [config/settings/production.py](config/settings/production.py#L72-L89)
- **Issue:** `ANYMAIL` config is empty; real email service not configured
- **Impact:** BLOCKS signup flow - users cannot confirm email or reset passwords
- **Required for:**
  - Email confirmation (signup flow)
  - Password resets
  - Listing notifications
  - Admin alerts
- **Fix:** Configure actual email provider (SendGrid, Mailgun, AWS SES, etc.)
- **Severity:** CRITICAL (will break core user flow)
- **Effort:** 1-2 hours (depends on provider choice)
- **Timing:** Must be completed before MVP launch

---

## 🟠 HIGH PRIORITY / PRE-MVP IMPROVEMENTS

### 5. **Hardcoded Lease Price Choices** - HIGH - Part of React form implementation (PR #16)
- **File:** [autotradespot/static/front-end/createlisting/ListingTypeForm.jsx](autotradespot/static/front-end/createlisting/ListingTypeForm.jsx#L5-L8)
- **Issue:** TODO comment: `// TODO: get from backend` - choices are hardcoded in frontend
- **Impact:** Inconsistency between frontend and backend; requires manual sync
- **Fix:** Create API endpoint to fetch pricing choices dynamically
- **Severity:** High (related to larger form refactor in #16)
- **Effort:** 2 hours
- **Timing:** Part of React form implementation initiative (can be batched with #16)
- **Note:** Grouped with issue #16 - multi-step form refactor

### 16. **Multi-Step Listing Creation Form is Brittle & Unmaintainable** - HIGH - Part of React form implementation
- **Primary Files:**
  - Templates: [autotradespot/templates/listings/create/](autotradespot/templates/listings/create/) (7 Django templates)
  - Views: [autotradespot/listings/views.py](autotradespot/listings/views.py#L52-L290) (multiple handling functions)
  - Components: [autotradespot/static/front-end/createlisting/](autotradespot/static/front-end/createlisting/) (React components, partially integrated)
  - Base template: [autotradespot/templates/base/main_navbar.html](autotradespot/templates/base.html#L25) uses hyperscript navigation
- **Issue:** The listing creation flow is a fragmented mix of:
  - HTMX for form submission and step navigation
  - Hyperscript (`_="..."`) for DOM manipulation (marking completed steps)
  - Partially-implemented React components that aren't integrated
  - Django template rendering for each step
  - Session-based state management for multi-step flow
- **Current Implementation Complexity:**
  1. User navigates between steps via HTMX calls to separate endpoints
  2. Each step (license plate, type, make/model, details, images) has its own template
  3. Progress indicator uses hyperscript to add `.step-success` classes
  4. Form data stored in Django session (`request.session["listing_in_progress"]`)
  5. React components exist but are not integrated into the flow
  6. State management across steps is implicit; unclear form validity rules
- **Problems:**
  - Hard to understand overall flow; logic scattered across multiple files
  - Difficult to maintain: changes in one step may break others
  - Poor UX: step navigation feels disjointed; no client-side validation until submission
  - Hyperscript is fragile and difficult to debug
  - Partially-written React components indicate previous attempt at modernization
  - Session-based approach makes it hard to handle concurrent edits or browser back/forward navigation
  - No proper error boundary or loading state management
- **Recommended Solution:** Consolidate into a single **React-based multi-step form component** with:
  - Centralized state management (React Context or local useState)
  - Client-side validation for each step
  - Clear step navigation with visual progress
  - Single form submission endpoint or separate API calls per step
  - Proper loading/error states
  - Session fallback for server-side persistence
- **Impact:**
  - High code clarity improvement
  - Easier to add features (e.g., save draft, resume later)
  - Better user experience
- **Severity:** High (core user feature)
- **Effort:** 6-8 hours (design component structure, integrate React, migrate session logic, test)
- **Timing:** Pre-MVP if timeline allows; post-MVP otherwise as high-value delivery
- **Block Status:** Functional but poor UX - does NOT block MVP launch
- **Bundled with:** Issue #5 (hardcoded pricing choices)

---

## 🟡 MEDIUM PRIORITY / POST-LAUNCH IMPROVEMENTS

### 9. **HSTS Configuration** - MEDIUM - TODO after launch
- **File:** [config/settings/production.py](config/settings/production.py#L49-L50)
- **Issue:** SECURE_HSTS_SECONDS temporarily set to 60 (recommended 518400)
- **Status:** Intentional; will be increased after verification
- **Fix:** After first week in production, increase to 518400 (6 months)
- **Severity:** Medium (security hardening, not blocking)
- **Effort:** 5 minutes
- **Timing:** First week in production post-launch

### 10. **Dutch Translation Incomplete** - MEDIUM - TODO after feature complete
- **Status:** WIP (Work in Progress)
- **Files:**
  - [locale/nl_NL/LC_MESSAGES/](locale/nl_NL/LC_MESSAGES/)
- **Issue:** Dutch translations not finalized
- **MVP Decision:** Disable Dutch language temporarily or complete before launch
- **Options:**
  - Option A: Remove Dutch from available languages temporarily
  - Option B: Complete Dutch translation before launch
  - Option C: Set as post-launch initiative
- **Severity:** Medium (feature impact depends on target market)
- **Effort:** 4-6 hours (translation work)
- **Timing:** Before MVP launch OR post-launch depending on market requirements

### 12. **Inline Media Serving** - MEDIUM - Part of S3 integration (post-MVP scaling)
- **File:** [autotradespot/listings/models.py](autotradespot/listings/models.py#L189)
- **Issue:** `upload_for_user` uses callable path, serving via Django directly
- **Current Status:** OK for MVP at small scale
- **Recommendation:**
  - Keep as-is for MVP launch
  - Monitor if user base grows rapidly
  - Consider S3/cloud storage migration when needed
- **Scaling Trigger:** When user uploads exceed server capacity
- **Severity:** Medium (depends on usage/scaling)
- **Effort:** 4-8 hours (if S3 migration needed)
- **Timing:** Post-MVP when performance requires it

---

## 🟢 LOW PRIORITY / OPTIONAL FOR MVP

### 7. **Improve Test Coverage** - LOW - Create valuable tests (post-MVP)
- **File:** [autotradespot/users/tests/test_views.py](autotradespot/users/tests/test_views.py#L16-L25)
- **Issue:** TODO comment about pytest-django limitations; fixture setup could be improved
- **Impact:** Test maintainability improvement (not a blocker)
- **Fix:** Extract common test setup into reusable fixtures
- **Severity:** Low (test framework limitation)
- **Effort:** 2 hours (not required for MVP)
- **Timing:** Post-MVP - first sprint of maintenance/improvement phase

### 17. **Incomplete Documentation** - LOW - Post-launch documentation
- **Status:** README.md recently improved
- **Current State:** Basic documentation in place
- **Missing:**
  - `.env.example` template for required environment variables
  - Deployment guide for Traefik + Docker production
  - Database backup/recovery procedures
  - API documentation for custom endpoints
- **Recommendation:** Add within first week of launch
- **Severity:** Low (doesn't affect functionality)
- **Effort:** 2-3 hours
- **Timing:** Post-MVP launch
- **Optional:** Can be completed post-launch based on team bandwidth

### 18. **Admin Interface Hardening** - LOW - Post-MVP enhancement
- **Recommendation:** Add custom admin actions, filters, and permissions
- **Status:** Not required for MVP but helpful for operations
- **Effort:** 3-4 hours
- **Timing:** Post-MVP after core functionality proven

### 19. **Performance Optimization** - LOW - Post-MVP scaling
- **Recommendations:**
  - Database query optimization (prefetch_related, select_related)
  - Implement caching for car makes/models
  - Add Redis caching for frequently accessed listings
  - Cache invalidation strategy for updated listings
- **Status:** Optional for MVP - add if performance issues arise
- **Trigger:** When response times exceed acceptable thresholds
- **Effort:** 6-8 hours (depends on scope)
- **Timing:** Post-MVP when monitoring data available

### 20. **Error Pages Customization** - LOW - Post-MVP polish
- **Status:** 403, 404, 500 error pages exist but may need styling improvements
- **Effort:** 1-2 hours
- **Timing:** Post-MVP visual polish phase

### 21. **Testing Coverage Expansion** - LOW - Post-MVP assurance
- **Current State:** Test coverage unknown; need baseline measurement
- **Recommendation:** Expand tests for critical user paths (signup, listing creation, payment)
- **Effort:** 4-6 hours
- **Timing:** Post-MVP first-sprint after baseline measurement

### 22. **Listing URL Configuration** - LOW - Post-MVP email fix
- **Issue:** Listing.get_absolute_url might be incomplete (related to emails containing only /listing/:id part)
- **Effort:** 30 minutes
- **Timing:** Post-MVP email verification phase

---

## SUMMARY TABLE

| Timing | Count | Est. Hours | Status | Required for MVP |
|--------|-------|-----------|--------|------------------|
| 🔴 **Critical (Pre-MVP)** | 1 | 1-2 | Email config needed | **YES** |
| 🟠 **High (Pre-MVP)** | 2 | 8 | React form refactor (bundled) | **OPTIONAL** |
| 🟡 **Medium (Post-Launch)** | 3 | 10 | After deployment | NO |
| 🟢 **Low (Post-MVP)** | 6 | 15+ | Maintenance phase | NO |

**Critical Path to MVP:** 1-2 hours (Email configuration)
**High Priority (if timeline allows):** +8 hours (React form work) - can slip to post-MVP
**Total Medium Priority:** ~10 hours distributed over first month post-launch
**Completed (Current Sprint):** 1.5 hours (Issues #13, #14 - API validation & error handling)

---

## MVP LAUNCH CHECKLIST

### 🔴 BLOCKING - Must Complete Before MVP

- [ ] **Configure Email Service** (Issue #11) - Choose provider and implement ANYMAIL config
- [ ] **Test Complete Signup Flow** - Email confirmation working end-to-end
- [ ] **Disable or Complete Dutch Translation** (Issue #10) - Decision on language support

### 🟢 COMPLETED BEFORE MVP

- [x] Fix CORS misconfiguration
- [x] Move API token to environment variable
- [x] Remove all debug print() and console.log() statements
- [x] Verify DEBUG=False in production
- [x] Test license plate API with error handling (Issues #13, #14)

### ⏱️ POST-LAUNCH (First Week)

- [ ] Increase HSTS max-age (Issue #9) - After 1 week in production verification
- [ ] Monitor error logs and fix any issues
- [ ] Verify Sentry integration if enabled
- [ ] Monitor performance metrics

### 📋 POST-LAUNCH (First Month)

- [ ] Complete documentation (Issue #17) - `.env.example`, deployment guides
- [ ] Consider React form refactor (Issue #16) - If UX issues reported or bandwidth available
- [ ] Monitor media serving performance (Issue #12) - Plan S3 migration if needed
- [ ] Measure test coverage baseline (Issue #21)

### 🚀 POST-MVP INITIATIVES (Sprint 2+)

- [ ] React Multi-Step Form Refactor (Issues #5 + #16) - High impact on code maintainability
- [ ] S3 Migration (Issue #12) - If media serving becomes bottleneck
- [ ] Performance Optimization (Issue #19) - If scaling needed
- [ ] Admin Interface Hardening (Issue #18)
- [ ] Expanded Test Coverage (Issues #7, #21)

---

## NOTES & CONTEXT

- **Database:** Appears well-designed with proper constraints
- **Authentication:** django-allauth well-integrated; email service is critical dependency
- **Task Queue:** Celery configured; verify broker in production
- **Frontend:** React + HTMX approach is good; code organization needs improvement (Issue #16)
- **API Validation:** Robust license plate validation and error handling in place (Issues #13, #14) ✅
- **Webhooks/Signals:** Properly used for user preferences creation
- **Critical Dependencies:** Email service MUST be configured before MVP launch to enable signup flow
