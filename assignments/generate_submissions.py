"""
Script: Enroll Test Users and Submit Assignments on Canvas LMS
Description:
    Automates enrolling test users as students in multiple courses on Canvas LMS and submitting
    assignments on their behalf. It is designed to facilitate grading practice by targeting specific
    assignment types and using predefined submission details.

Prerequisites:
    - Access to Canvas LMS with an API URL and API key.
    - `canvasapi`, `pyyaml`, and `python-dotenv` packages installed in the Python environment.
    - `courses.yml` and `submissions.yml` files with course and submission details respectively.

Key Operations:
    - Validates environment variables for Canvas API access.
    - Loads course details from `courses.yml` and submission details from `submissions.yml`.
    - For each course, attempts to enroll specified test users and submit assignments of a defined type.

Usage:
    1. Install necessary Python packages.
    2. Set CANVAS_API_URL and CANVAS_API_KEY in environment variables.
    3. Prepare the `courses.yml` and `submissions.yml` files with relevant details.
    4. Run the script in a Python environment where prerequisites are met.

Safety and Permissions:
    - Use with caution as it modifies course enrollments and submissions.
    - Ensure the provided API key has permissions to perform these operations.
"""

import yaml
import os
from dotenv import load_dotenv
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException

# Constants for the script
ASSIGNMENT_TYPE = "online_text_entry"  # Specify the type of assignment to submit
COURSES_FILE = "courses.yml"  # Path to YAML file with course details
SUBMISSION_LIST = "submissions.yml"  # Path to YAML file with submission details

# Load environment variables for Canvas API access
load_dotenv()
CANVAS_API_KEY = os.environ.get("CANVAS_API_KEY")
CANVAS_API_URL = os.environ.get("CANVAS_API_URL")

# Validate environment variables
if not CANVAS_API_URL or not CANVAS_API_KEY:
    print("Error: Canvas API URL or API Key not set. Check your environment variables.")
    exit(1)

# Load courses and submissions from YAML files
try:
    with open(COURSES_FILE, "r") as file:
        course_list = yaml.load(file, Loader=yaml.FullLoader)
except Exception as e:
    print(f"Failed to load courses file: {e}")
    exit(1)

try:
    with open(SUBMISSION_LIST, "r") as file:
        submission_list = yaml.load(file, Loader=yaml.FullLoader)
except Exception as e:
    print(f"Failed to load submissions file: {e}")
    exit(1)

# Initialize Canvas API instance
canvas = Canvas(CANVAS_API_URL, CANVAS_API_KEY)

# Main operation: Enroll test users and submit assignments
for course_info in course_list:
    try:
        # Retrieve the course by its Canvas ID
        course = canvas.get_course(course_info["canvas_id"])

        # Attempt to find or assert the existence of a specific section for test students
        test_student_section = next(
            (
                section
                for section in course.get_sections()
                if section.name == course_info.get("test_student_section_name")
            ),
            None,
        )
        if not test_student_section:
            print(f"No test student section found in course: {course_info['name']}.")
            continue

        # Enroll users and prepare for submission
        for submission_info in submission_list:
            try:
                # Get the user by SIS login ID and enroll in the test student section if not already enrolled
                user = canvas.get_user(
                    submission_info["sis_login_id"], id_type="sis_login_id"
                )
                enrollment = test_student_section.enroll_user(
                    user,
                    enrollment={
                        "type": "StudentEnrollment",
                        "enrollment_state": "active",
                    },
                )
                print(f"Enrolled {user} in section: {test_student_section.name}")

                # Update submission parameters with the user ID for assignment submission
                submission_info["submission_params"]["user_id"] = user.id
            except CanvasException as e:
                print(
                    f"Error processing user {submission_info['sis_login_id']} in {course_info['name']}: {e}"
                )
                continue

        # Submit assignments for enrolled test users
        for assignment in course.get_assignments():
            if ASSIGNMENT_TYPE in assignment.submission_types:
                for submission_info in submission_list:
                    try:
                        assignment.submit(
                            submission=submission_info["submission_params"]
                        )
                        print(
                            f"Submitted {assignment.name} for {submission_info['sis_login_id']} in {course_info['name']}"
                        )
                    except CanvasException as e:
                        print(
                            f"Error submitting assignment for {submission_info['sis_login_id']} in {course_info['name']}: {e}"
                        )

    except CanvasException as e:
        print(f"Error processing course {course_info['name']}: {e}")
