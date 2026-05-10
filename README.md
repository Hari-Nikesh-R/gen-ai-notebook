# Agentic AI Learning progress

## Task 1: Create a marks dataset

We keep a small CSV of **20 students** with marks for **science**, **maths**, **social_science**, **Tamil**, and **english**.

- **Source file:** `day1_dataset/marks.csv`  
- Columns: `student_id`, `student_name`, plus the five subject columns.

## Task 2: Process marks (grades, failures, sort, export)

A small script reads `marks.csv`, adds analytics, and writes new CSVs.

- **Script:** `day1_dataset/process_marks.py`
- **Run:** from the repo root, `python3 day1_dataset/process_marks.py` (or run it from inside `day1_dataset/`).

**What it does**

1. **Grade** — from **average** of all five subjects: A+ (≥90), A (≥80), B (≥70), C (≥60), D (≥50), F (under 50).
2. **Failed students** — anyone with **any subject under 40** or **average under 40** (threshold is `PASS_MARK` in the script).
3. **Sort** — all rows sorted by **average**, highest first.
4. **Outputs**
   - `day1_dataset/marks_results.csv` — full table with `average`, `grade`, `status` (Pass/Fail), `fail_reason`.
   - `day1_dataset/failed_students.csv` — only rows that failed (header only if nobody fails).

Edit `PASS_MARK` or the grade bands in `process_marks.py` if your institution uses different rules.
