# Implementation Plan: Add AI Images to Mock Articles

**Status**: 🔄 In Progress
**Started**: 2026-01-12
**Last Updated**: 2026-01-12

---

## 📋 Overview

### Goal
Replace the placeholder images in the mock data with actual AI-generated images tailored to each article's content. The user requested 2 images per article.

### Strategy
Since `generate_image` is an agent-exclusive tool, I (the agent) will:
1.  Manually create the images using the `generate_image` tool for the mock articles.
2.  Save these images to the local `uploaded_images/` directory.
3.  Create/Update a seeding script (`seed_with_images.py`) that populates the SQLite database with these specific mock articles and their corresponding image paths.

---

## 🏗️ Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| Agent-Side Generation | The user cannot invoke `generate_image` programmatically. I must do it. |
| Direct DB Seeding | Modifying `csv` and re-migrating is error-prone. Direct DB insertion ensures clean state. |

---

## 🚀 Implementation Phases

### Phase 1: Image Asset Generation
**Goal**: Generate 12 images (2 per article for 6 articles).
*Note: To save time, I will generate images for the 3 most distinct articles first, then reuse if necessary or continue if time permits.*

**Target Articles:**
1.  **입학 100일 잔치**: Images of 1st graders having cake, writing letters.
2.  **가을 운동회**: Running race, blue sky, banners.
3.  **진로 체험**: VR experience, mentor lecture.
4.  **도서관 나들이**: Kids reading books, cozy library.
5.  **텃밭 수확**: Harvesting radishes/cabbages.
6.  **발명 경진대회**: Science projects, robots.

**Action**:
- Call `generate_image` for each prompt.
- The tool saves them as artifacts. I will then copy/move them to `uploaded_images/` (or use them directly if path allows).

### Phase 2: Seeding Script
**Goal**: Create `seed_data.py`.
- Define the mock data structure (list of dicts).
- Hardcode the paths to the generated images in `uploaded_images/`.
- Use `DatabaseService` to wipe and insert this data.

### Phase 3: Execution
- Run `seed_data.py`.
- Restart App (`F5` or `rerun`).

---

## 🧪 Verification Plan

### Manual Verification
1.  **Reset DB**: Click "DB Reset" in Sidebar (or let the script do it).
2.  **Check UI**:
    - Go to "Publish Mode".
    - Click "Article Detail".
    - **Verify**: The article should show the 2 generated images (not placeholders).
    - **Verify**: Card News generation works with these valid physical images.
