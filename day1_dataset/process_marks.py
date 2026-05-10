"""
Read student marks from marks.csv, add average and grade,
find who failed, sort everyone by average, save two new CSV files.
"""

import csv
from pathlib import Path

# Minimum marks to pass (one subject below this = fail)
PASS_MARK = 40

RESULT_COLUMNS = [
    "student_id",
    "student_name",
    "science",
    "maths",
    "social_science",
    "tamil",
    "english",
    "average",
    "grade",
    "status",
    "fail_reason",
]

FAILED_COLUMNS = [
    "student_id",
    "student_name",
    "average",
    "grade",
    "fail_reason",
]


def get_grade(average):
    """Letter grade from the average mark (out of 100)."""
    if average >= 90:
        return "A+"
    if average >= 80:
        return "A"
    if average >= 70:
        return "B"
    if average >= 60:
        return "C"
    if average >= 50:
        return "D"
    return "F"


def build_record_from_marks(student_id, student_name, science, maths, social_science, tamil, english):
    """
    One student with valid integer marks -> result row dict.
    Shared by process_marks.py and task3_process_marks.py.
    """
    total = science + maths + social_science + tamil + english
    average_raw = total / 5
    average = round(average_raw, 2)

    failed_subjects = []
    if science < PASS_MARK:
        failed_subjects.append("science")
    if maths < PASS_MARK:
        failed_subjects.append("maths")
    if social_science < PASS_MARK:
        failed_subjects.append("social_science")
    if tamil < PASS_MARK:
        failed_subjects.append("tamil")
    if english < PASS_MARK:
        failed_subjects.append("english")

    if len(failed_subjects) > 0:
        status = "Fail"
        fail_reason = ";".join(failed_subjects)
    elif average_raw < PASS_MARK:
        status = "Fail"
        fail_reason = "average_below_threshold"
    else:
        status = "Pass"
        fail_reason = ""

    return {
        "student_id": student_id,
        "student_name": student_name,
        "science": science,
        "maths": maths,
        "social_science": social_science,
        "tamil": tamil,
        "english": english,
        "average": average,
        "grade": get_grade(average_raw),
        "status": status,
        "fail_reason": fail_reason,
    }


def average_for_sort(student):
    return student["average"]


def sort_students_by_average(students):
    """Sort the list in place: highest average first."""
    students.sort(key=average_for_sort, reverse=True)


def write_results_and_failed(results_file, failed_file, all_students):
    """Write marks_results.csv and failed_students.csv."""
    with open(results_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        for student in all_students:
            writer.writerow(student)

    failed_only = []
    for student in all_students:
        if student["status"] == "Fail":
            failed_only.append(student)

    with open(failed_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FAILED_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for student in failed_only:
            writer.writerow(student)


def main():
    # This script lives next to marks.csv — use that folder for all paths
    folder = Path(__file__).resolve().parent
    input_file = folder / "marks.csv"
    results_file = folder / "marks_results.csv"
    failed_file = folder / "failed_students.csv"

    all_students = []

    with open(input_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            science = int(row["science"])
            maths = int(row["maths"])
            social = int(row["social_science"])
            tamil = int(row["tamil"])
            english = int(row["english"])

            record = build_record_from_marks(
                row["student_id"],
                row["student_name"],
                science,
                maths,
                social,
                tamil,
                english,
            )
            all_students.append(record)

    sort_students_by_average(all_students)
    write_results_and_failed(results_file, failed_file, all_students)

    failed_only = [s for s in all_students if s["status"] == "Fail"]

    print("Done.")
    print("Saved sorted results with grades:", results_file)
    print("Saved failed students only:", failed_file)
    print("Number of students:", len(all_students))
    print("Number who failed:", len(failed_only))


if __name__ == "__main__":
    main()
