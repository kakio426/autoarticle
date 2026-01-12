# Implementation Plan: UI Refactor & Critical Bug Fix

**Status**: 🔄 In Progress
**Started**: 2026-01-12
**Last Updated**: 2026-01-12
**Estimated Completion**: 2026-01-12

---

**⚠️ CRITICAL INSTRUCTIONS**: After completing each phase:
1. ✅ Check off completed task checkboxes
2. 🧪 Run all quality gate validation commands
3. ⚠️ Verify ALL quality gate items pass
4. 📅 Update "Last Updated" date above
5. 📝 Document learnings in Notes section
6. ➡️ Only then proceed to next phase

⛔ **DO NOT skip quality gates or proceed with failing checks**

---

## 📋 Overview

### Feature Description
Refactor `app.py` to address a critical start-up crash related to Gemini API configuration and improve the overall User Experience by separating "Article Writing" and "Newsletter Publishing" into distinct modes.

### Success Criteria
- [ ] Users can navigate to "Newsletter Production" immediately after launch without crashing (API Key error fixed).
- [ ] Sidebar is simplified, acting as a navigation menu.
- [ ] "Write Mode" and "Publish Mode" are clearly separated.
- [ ] Publishing interface (Archive/Batch) uses the full main area width.

### User Impact
- **Reliability**: Eliminates the `DefaultCredentialsError` when skipping the writing step.
- **Usability**: Cleaner interface, easier to manage large lists of archived articles.

---

## 🏗️ Architecture Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| Global `genai.configure` in `main` | Ensures API is ready regardless of which tab/function is accessed first. | API Key must be provided immediately for any AI feature. |
| `st.radio` for Mode Switch | Simple, persistent navigation state in sidebar. | Adds one click to switch contexts (but clarifies context). |
| Dataframe for Archive | `st.dataframe` provides better sorting/viewing for many items than a simple list. | Slightly improved complexity in handling selection. |

---

## 📦 Dependencies

### Required Before Starting
- [x] Existing `app.py`
- [x] `NanumGothic` font (Verified existence)

### External Dependencies
- Streamlit (Already installed)
- Google GenAI (Already installed)

---

## 🧪 Test Strategy

### Testing Approach
Since this modifies the Streamlit UI and main entry point, verification will primarily be **Manual Interactive Testing**.

### Test Pyramid for This Feature
| Test Type | Coverage Target | Purpose |
|-----------|-----------------|---------|
| **Manual UI Test** | 100% | Critical user flows (Write -> Publish, Direct Publish) |
| **Unit Tests** | N/A | Existing business logic tests should pass. |

---

## 🚀 Implementation Phases

### Phase 1: Critical Bug Fix (API Configuration)
**Goal**: Ensure `genai.configure` is called globally so "Letter Generation" doesn't crash on fresh start.
**Estimated Time**: 0.5 hours
**Status**: ⏳ Pending

#### Tasks

**🔴 RED: Write Failing Tests First**
- *Note: Hard to unit test Streamlit global state. We will simulate this by checking code structure or manual fail first.*
- [ ] **Manual Test**: Run app, enter key, go straight to "Newsletter Generation" tab (in current UI), click generate. Expect: Crash.

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 1.1**: specific `main()` update
  - File(s): `app.py`
  - Action: Move `genai.configure(api_key=api_key)` to be immediately after API key input in the sidebar, or at start of `main` if key is stored in session.
  - Detail:
    ```python
    if api_key:
        try:
            genai.configure(api_key=api_key)
        except Exception as e:
            st.error(f"API Key Error: {e}")
    ```

**🔵 REFACTOR: Clean Up Code**
- [ ] **Task 1.2**: Remove redundant `genai.configure` calls inside `generate_article_gemini` if they are no longer needed (or keep as safety).

#### Quality Gate ✋

**⚠️ STOP: Do NOT proceed to Phase 2 until ALL checks pass**

- [ ] **Manual Verify**: App starts, Key entered, "Newsletter Generation" works without visiting other tabs.

---

### Phase 2: UI Structure Refactoring
**Goal**: Split UI into "Write Mode" and "Publish Mode" to declutter sidebar and improve workflow.
**Estimated Time**: 1.5 hours
**Status**: ⏳ Pending

#### Tasks

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 2.1**: Implement Sidebar Navigation
  - File(s): `app.py`
  - details: Add `page_mode = st.radio(...)` in sidebar. Hide other sidebar items depending on mode if necessary, or just keep Navigation/Settings there.

- [ ] **Task 2.2**: Refactor "Write Mode"
  - File(s): `app.py`
  - details: Wrap existing Article Generation UI code in `if page_mode == "📝 기사 작성":`.

- [ ] **Task 2.3**: Refactor "Publish Mode"
  - File(s): `app.py`
  - details: Move `tab_search` and `tab_batch` logic (Archive viewing, Newspaper creation) into `if page_mode == "🗂️ 기록 관리 및 발행":`.
  - details: Replace `st.selectbox` for list with `st.dataframe` or improved grid layout if possible (as per user suggestion).

**🔵 REFACTOR: Clean Up Code**
- [ ] **Task 2.4**: Clean up styling
  - Ensure `apply_custom_style()` still works for new layout.
  - Verify "Wide Mode" (`layout="wide"`) is set.

#### Quality Gate ✋

**⚠️ STOP: Do NOT proceed until ALL checks pass**

- [ ] **Functionality**: "Write Mode" creates articles correctly.
- [ ] **Functionality**: "Publish Mode" lists history and generates PDFs.
- [ ] **Visual**: Sidebar is clean.

---

## 📊 Progress Tracking

### Completion Status
- **Phase 1**: ⏳ 0%
- **Phase 2**: ⏳ 0%

---
