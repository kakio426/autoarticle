# Implementation Plan: Fix PPT Summary Generation

**Status**: 🔄 In Progress
**Started**: 2026-01-12
**Last Updated**: 2026-01-12

---

## 📋 Overview

### Feature Description
The current PPT summary generation relies on experimental/preview models (`gemini-3.0-flash-preview`, etc.) which may be failing due to availability or API limits, causing the system to fallback to a hard-truncated string ("...요약에 실패했습니다").
This plan aims to make the summary robust by:
1. Prioritizing stable models (`gemini-1.5-flash`).
2. Ensuring API key is explicitly configured in the summary function scope if needed.
3. Providing clear error feedback instead of silent failure.

### Success Criteria
- [ ] PPT generation produces actual bullet points, not the fallback truncation message.
- [ ] If Generation fails, the error message gives a hint (e.g., "Quota exceeded") rather than generic failure.

---

## 🏗️ Architecture Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| Prioritize `gemini-1.5-flash` | Most stable and widely available model for free tier users. | Might be slightly less "smart" than 2.0/3.0 preview (negligible for simple summarization). |
| Pass `api_key` to summary function | Ensures `genai` is configured even if called from different context. | Requires signature update in `ai_service` and `ui_logic`. |

---

## 🚀 Implementation Phases

### Phase 1: Robustness Fix
**Goal**: Update `ai_service.py` and `ui_logic.py` to use stable models and pass API credentials.

#### Tasks

**1. Update `engines/ai_service.py`**
- [ ] Function `summarize_article_for_ppt`:
    - Add `api_key` parameter (optional/required).
    - If `api_key` provided, call `genai.configure`.
    - Change `models_to_try` order: `['gemini-1.5-flash', 'gemini-2.0-flash-exp']`.
    - Improve error catching: Capture the specific error message to display if all fail.

**2. Update `ui_logic.py`**
- [ ] Function `_generate_newsletters`:
    - Retrieve `api_key` from session state (or pass it in).
    - Pass `api_key` to `summarize_article_for_ppt`.

#### Quality Gate ✋
- [ ] Manual Test: Generate a PPT with a long article. Confirm summary appears.

---

## 🧪 Verification Plan

### Manual Verification
1.  **Setup**: Ensure valid API Key in Sidebar.
2.  **Action**: 
    -   Go to "Write Mode", create a dummy long article (or use existing).
    -   Save it.
    -   Go to "Publish Mode", select that article.
    -   Check "PPT Summary" option.
    -   Click "Generate".
3.  **Check**: Open generated PPT (or check logs/UI success message). The content should be bullet points, not the fallback text.

---
