---
name: pr-solve-review
description: Interactive Human-in-the-Loop workflow for addressing PR review feedback line-by-line or bullet-by-bullet. Reads PR review comments or artifacts, breaks down items into tasks, resolves them one-by-one, presents changes for user confirmation, and commits on approval.
---

# PR Solve Review Guidelines (Human-in-the-Loop)

## Overview & Principles

This skill automates and guides the process of fixing code issues identified during Pull Request code reviews. It adheres strictly to the **Human-in-the-Loop** paradigm to give developers complete control over code changes.

### Core Rules

1. **One Task at a Time**: Never fix all review comments in a single batch. Resolve **exactly one bullet/task per iteration**.
2. **Review Before Commit**: After implementing a fix for a task, present the diff and explanation to the user. **Wait for user confirmation** before committing.
3. **Incremental Progress**: Track completed vs remaining review items in a live checklist throughout the session.
4. **Clean Commits**: Create focused, individual git commits for each resolved feedback item (or grouped logically upon user request).

---

## Trigger Commands

- `/pr-solve-review <PR_LINK_OR_NUMBER>`
- `/pr-solve-review` (defaults to active branch's PR or latest review artifact in `~/.cursor/pr-code-review/`)
- `@[pr-solve-review] solve`
- Any user request to solve, fix, or address PR review comments (e.g. "ช่วยแก้ PR review หน่อย", "แก้ PR ตามที่ review")

---

## Step 1: Read & Parse Review Feedback

Gather review items from available sources:

1. **Local Review Artifacts (Highest priority if present)**:
   - Check `$HOME/.cursor/pr-code-review/{owner}__{repo}__pr-{number}.md`
2. **GitHub PR Comments & Reviews (Fallback)**:
   - Run `gh pr view <PR> --comments`
   - Run `gh api repos/{owner}/{repo}/pulls/{number}/reviews` and review comments if needed.

Extract and categorize all action items into 4 priority buckets:
- 🛑 **Blocker** (Bugs, security risks, critical defects)
- ⚠️ **Warning** (Spec drift, missing edge-case handling, potential runtime issues)
- 💡 **Suggestion** (Refactoring, cleaner patterns, performance improvements)
- 🔍 **Nitpick** (Formatting, minor naming, polish)

---

## Step 2: Present Initial Task Queue

Display the full task list to the user before making any code edits:

```markdown
### 📋 PR Review Task Queue (PR #<number>)

- [ ] **Task 1 [Blocker]**: <Summary of blocker 1>
- [ ] **Task 2 [Warning]**: <Summary of warning 1>
- [ ] **Task 3 [Suggestion]**: <Summary of suggestion 1>
- [ ] **Task 4 [Nitpick]**: <Summary of nitpick 1>

*กำลังจะเริ่มดำเนินการ **Task 1** ก่อน คุณต้องการให้ปรับเปลี่ยนลำดับหรือข้ามรายการไหนหรือไม่?*
```

---

## Step 3: Incremental Execution Loop (One Bullet at a Time)

For each task in the queue, execute the following sub-steps:

### 3.1 Implement Fix for Current Task
- Locate the relevant file(s) and line range.
- Make precise, targeted changes addressing **only** the current bullet item.
- Do not touch unrelated code.

### 3.2 Verification
- Check formatting / linter (`poetry run black --check` or equivalent).
- Run relevant unit tests if present (`pytest` or test script).

### 3.3 Present Diff & Seek User Approval
Display the code diff and ask the user to confirm:

```markdown
#### 🛠️ สรุปการแก้ไขสำหรับ Task <N>: <Task Title>

**ไฟล์ที่แก้ไข:** [`path/to/file.py`](file:///path/to/file.py#L12-L30)

```diff
- old code
+ new code
```

**คำอธิบาย:** <อธิบายเหตุผลและรายละเอียดการแก้ไขแบบสั้น>

---
คุณต้องการให้:
1. ✅ **อนุมัติและ Commit** (จะสร้าง commit: `fix(...)`)
2. ✏️ **ปรับแต่งเพิ่มเติม** (แจ้งรายละเอียดที่ต้องการแก้เพิ่ม)
3. ⏭️ **ข้าม Task นี้** (ไม่แก้และไปทำ Task ถัดไป)
```

### 3.4 Process User Response
- **If Approved (Option 1)**:
  - Stage changed file(s): `git add <files>`
  - Commit with descriptive message: `git commit -m "<conventional commit message>"`
  - Mark task as completed `[x]` in queue.
- **If Feedback Provided (Option 2)**:
  - Adjust code per user instructions, then repeat 3.2 - 3.3.
- **If Skipped (Option 3)**:
  - Revert changes for this task (`git checkout -- <files>`).
  - Mark task as skipped `[-]` in queue.

---

## Step 4: Final Summary & Push

Once all tasks in the queue are processed (completed or skipped):

1. Display final status summary of all tasks and generated commits:
   ```markdown
   ### 🎉 ดำเนินการ แก้ไข PR Review เรียบร้อยแล้ว!

   **สรุปผลการทำงาน:**
   - [x] Task 1: [Blocker] <Title> — *Committed (`a1b2c3d`)*
   - [x] Task 2: [Warning] <Title> — *Committed (`e4f5g6h`)*
   - [-] Task 3: [Suggestion] <Title> — *Skipped*

   คุณต้องการให้ push commits ทั้งหมดขึ้นไปยัง GitHub (`git push`) เลยหรือไม่?
   ```
2. On user confirmation, execute `git push`.
