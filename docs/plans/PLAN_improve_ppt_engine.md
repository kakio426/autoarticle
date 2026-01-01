
# Implementation Plan: Improve PPT Engine & AI Integration

**Status**: 🔄 In Progress
**Started**: 2026-01-01
**Last Updated**: 2026-01-01
**Estimated Completion**: 2026-01-02

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
Upgrade the existing `PPTEngine` to produce professional, visually appealing PowerPoint slides (16:9) with theme support. Integrate Gemini AI to automatically summarize long article content into concise bullet points, or provide a manual prompt copy feature for users who prefer manual AI interaction.

### Success Criteria
- [ ] PPT output uses a consistent, professional 2-column layout.
- [ ] Slides include proper headers, footers, and theme colors.
- [ ] Users can optionally use AI to auto-summarize articles into bullet points.
- [ ] Users can copy the AI prompt to use manually if desired.
- [ ] `add_newspaper_page` logic is not broken by changes.

### User Impact
Significantly improves the usability of the PPT export feature, making it "presentation-ready" without manual editing.

---

## 🏗️ Architecture Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| **Gemini for Summarization** | Existing integration in `app.py`, efficient and good at text processing. | API cost/quota usage (mitigated by opt-in toggle). |
| **Python-pptx Custom Layouts** | Programmatic layout control allows dynamic content fitting. | Harder to "see" the design while coding compared to template files. |
| **Manual Prompt Copy** | Provides an alternative for users wary of API costs/limits. | Slightly more friction for the user than auto-generation. |

---

## 📦 Dependencies

### Required Before Starting
- [x] `python-pptx` library (already installed)
- [x] `google-generativeai` library (already installed)

---

## 🧪 Test Strategy

### Testing Approach
**TDD Principle**: Write tests FIRST, then implement to make them pass.

### Test Pyramid for This Feature
| Test Type | Coverage Target | Purpose |
|-----------|-----------------|---------|
| **Unit Tests** | ≥80% | `PPTEngine` layout logic, summary function behavior |
| **Integration Tests** | Critical paths | `app.py` -> `PPTEngine` data flow |
| **Manual Tests** | UX | Verify PPT visual quality and UI toggles |

---

## 🚀 Implementation Phases

### Phase 1: PPT Engine Core Upgrade
**Goal**: Create a professional slide layout engine without AI first.
**Estimated Time**: 2 hours
**Status**: 🔄 In Progress

#### Tasks

**🔴 RED: Write Failing Tests First**
- [ ] **Test 1.1**: Update `tests/unit/test_ppt_engine.py` to check for specific internal structures (title, body placeholders availability, theme color application).
  - Expected: Fail because current engine is too basic.

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 1.2**: Rewrite `engines/ppt_engine.py`
  - Implement `_create_master_slide` or similar setup logic.
  - Create `add_content_slide` with 2-column layout (Text Left, Image Right).
  - Apply theme colors to Shapes and Text.

**🔵 REFACTOR: Clean Up Code**
- [ ] **Task 1.3**: Refactor layout constants into a config dictionary or class constants.

#### Quality Gate ✋
- [ ] **Build**: Project runs without errors `python -m streamlit run app.py`
- [ ] **Tests**: `pytest tests/unit/test_ppt_engine.py` passes
- [ ] **Manual**: Generate a PPT and visually verify the layout is not broken.

---

### Phase 2: AI Summarization Integration
**Goal**: Connect Gemini API to generate bullet points for PPT.
**Estimated Time**: 2 hours
**Status**: ⏳ Pending

#### Tasks

**🔴 RED: Write Failing Tests First**
- [ ] **Test 2.1**: Create `tests/unit/test_ai_summary.py` (mocked).
  - Verify `summarize_for_ppt(text)` returns a list of strings (bullet points).

**🟢 GREEN: Implement to Make Tests Pass**
- [ ] **Task 2.2**: Implement `summarize_for_ppt` in `app.py` (or new service file).
  - Use existing `genai` model.
  - Prompt: "Summarize this for a PPT slide, 3-5 bullet points."

**🔵 REFACTOR: Clean Up Code**
- [ ] **Task 2.3**: Move AI logic to `engines/ai_service.py` if `app.py` gets too crowded.

#### Quality Gate ✋
- [ ] **Tests**: `pytest` passes.
- [ ] **Manual**: Verify AI generates reasonable summaries (mock or real).

---

### Phase 3: UI & Integration
**Goal**: Expose new features to the user in Streamlit.
**Estimated Time**: 1 hour
**Status**: ⏳ Pending

#### Tasks

- [ ] **Task 3.1**: Add "Use AI Summarization" checkbox in `app.py`.
- [ ] **Task 3.2**: Add "Copy Prompt" expander in `app.py`.
- [ ] **Task 3.3**: Connect `PPTEngine` to receive AI summaries instead of raw content when enabled.

#### Quality Gate ✋
- [ ] **Manual**: Click checkboxes, generate PPT, verify differnce between AI-on and AI-off.
- [ ] **Manual**: Click "Copy Prompt", paste text, verify content.

---

## ⚠️ Risk Assessment

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| AI Quota Limit | Medium | Medium | Implement error handling fallback (use raw text if AI fails). |
| Layout Overflow | High | High | Auto-shrink font size if text > box size. |

---

## 📝 Notes & Learnings
- PPTX text fitting is tricky; `text_frame.fit_text()` is not standard, might need custom font sizing logic.
