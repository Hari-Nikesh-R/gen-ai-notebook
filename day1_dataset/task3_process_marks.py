"""
Task 3 builds on process_marks.py:

  - Reuses the same grading record (build_record_from_marks), sort, and CSV writes.
  - Adds safe parsing so missing or invalid cells do not crash the program.
  - Writes extra file marks_skipped.csv for rows that could not be graded.
"""

import csv
from pathlib import Path

from process_marks import (
    build_record_from_marks,
    sort_students_by_average,
    write_results_and_failed,
)

SUBJECTS = ["science", "maths", "social_science", "tamil", "english"]


def parse_mark(cell):
    """
    Read one mark from the CSV cell.
    Returns (mark or None, error tag or None).
    """
    if cell is None:
        return None, "missing"

    text = str(cell).strip()
    if text == "":
        return None, "missing"

    try:
        value = int(text)
    except ValueError:
        return None, "not_an_integer"

    if value < 0 or value > 100:
        return None, "outside_0_to_100"

    return value, None


def read_scores_from_row(row):
    """
    Try to read all five subject marks from one CSV row.
    Returns (scores dict, list of issue strings like "science:missing").
    """
    scores = {}
    problems = []

    for subject in SUBJECTS:
        raw = row.get(subject, "")
        mark, err = parse_mark(raw)
        scores[subject] = mark
        if err is not None:
            problems.append(f"{subject}:{err}")

    return scores, problems


def all_marks_present(scores):
    for subject in SUBJECTS:
        if scores[subject] is None:
            return False
    return True


def write_skipped_csv(path, skipped_rows):
    columns = ["student_id", "student_name", "issues"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in skipped_rows:
            writer.writerow(row)


def process_marks_file(input_path, results_path, failed_path, skipped_path):
    """
    Same outputs as process_marks.py, plus marks_skipped.csv.
    Returns (graded_count, failed_count, skipped_count).
    """
    graded = []
    skipped = []

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = (row.get("student_id") or "").strip()
            sname = (row.get("student_name") or "").strip()

            scores, problems = read_scores_from_row(row)

            if not all_marks_present(scores):
                skipped.append(
                    {
                        "student_id": sid,
                        "student_name": sname,
                        "issues": "; ".join(problems),
                    }
                )
                continue

            record = build_record_from_marks(
                sid,
                sname,
                scores["science"],
                scores["maths"],
                scores["social_science"],
                scores["tamil"],
                scores["english"],
            )
            graded.append(record)

    sort_students_by_average(graded)
    write_results_and_failed(results_path, failed_path, graded)
    write_skipped_csv(skipped_path, skipped)

    failed_only = [s for s in graded if s["status"] == "Fail"]
    return len(graded), len(failed_only), len(skipped)


def main():
    folder = Path(__file__).resolve().parent
    input_file = folder / "marks.csv"
    results_file = folder / "marks_results.csv"
    failed_file = folder / "failed_students.csv"
    skipped_file = folder / "marks_skipped.csv"

    n_ok, n_fail, n_skip = process_marks_file(
        input_file,
        results_file,
        failed_file,
        skipped_file,
    )

    print("Done (Task 3 on top of process_marks).")
    print("Graded students:", n_ok, "->", results_file)
    print("Failed (among graded):", n_fail, "->", failed_file)
    print("Skipped (bad or missing marks):", n_skip, "->", skipped_file)


if __name__ == "__main__":
    main()
