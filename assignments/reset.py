"""
Script: Reset Course
Description:
    This script is designed to clean up a Canvas course by performing several actions:
    1. Removes all generated assignments specified in the assignment.yml file.
    2. Removes all test student enrollments from the specified test student section.
    3. Removes all enrollments from the specified grader section.
    4. Deletes the test student section.
    5. Deletes the grader section.

    The script requires course details to be specified in a courses.yml file and uses assignment names
    from an assignment.yml file to identify which assignments to delete.

Prerequisites:
    - A Canvas LMS account with API access.
    - Python 3.x and the 'canvasapi', 'pyyaml', 'python-dotenv' packages installed.
    - COURSES_FILE (courses.yml) and ASSIGNMENT_PARAMS_FILE (assignment.yml) properly configured.

Usage:
    Ensure that the .env file is set up with CANVAS_API_URL and CANVAS_API_KEY, and run the script.
    python reset_course.py
"""

import yaml
import os
from dotenv import load_dotenv
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException

# Configuration file paths
ASSIGNMENT_PARAMS_FILE = "assignment.yml"
COURSES_FILE = "courses.yml"

# Load environment variables for API access
load_dotenv()
CANVAS_API_KEY = os.environ.get("CANVAS_API_KEY")
CANVAS_API_URL = os.environ.get("CANVAS_API_URL")

# Check for required environment variables
if not CANVAS_API_URL or not CANVAS_API_KEY:
    print(
        "Error: Required environment variables (CANVAS_API_URL, CANVAS_API_KEY) are not set."
    )
    exit(1)

# Load course list from courses.yml
try:
    with open(COURSES_FILE, "r") as file:
        course_list = yaml.load(file, Loader=yaml.FullLoader)
except Exception as e:
    print(f"Error loading {COURSES_FILE}: {e}")
    exit(1)

# Initialize Canvas API
canvas = Canvas(CANVAS_API_URL, CANVAS_API_KEY)

# Iterate through courses for cleanup
for course_info in course_list:
    course_canvas_id = course_info["canvas_id"]
    course_name = course_info["name"]

    # Attempt to fetch the course from Canvas
    try:
        course = canvas.get_course(course_canvas_id)
    except CanvasException as e:
        print(f"Skipping {course_name} due to error: {e}")
        continue

    # Load assignments to be deleted
    try:
        with open(ASSIGNMENT_PARAMS_FILE, "r") as file:
            assignment_list = yaml.load(file, Loader=yaml.FullLoader)
    except Exception as e:
        print(f"Error loading {ASSIGNMENT_PARAMS_FILE}: {e}")
        exit(1)

    # Compile a list of assignment names to delete
    assignments_to_delete = [
        f"{a.get('name', 'Assignment')}{i}"
        for a in assignment_list
        for i in range(1, course_info.get("num_create_assignments", 1) + 1)
    ]

    # Delete specified assignments
    for assignment in course.get_assignments():
        if assignment.name in assignments_to_delete:
            try:
                assignment.delete()
                print(f"Deleted assignment: {assignment.name} from {course_name}")
            except CanvasException as e:
                print(f"Error deleting assignment {assignment.name}: {e}")

    # Delete specified sections and their enrollments
    for section in course.get_sections():
        if section.name in [
            course_info.get("test_student_section_name", "Test Students"),
            course_info.get("grader_section_name", "Graders"),
        ]:
            try:
                # Deactivate section enrollments
                for enrollment in section.get_enrollments():
                    enrollment.deactivate(task="delete")
                # Delete the section
                section.delete()
                print(f"Deleted section: {section.name} from {course_name}")
            except CanvasException as e:
                print(f"Error processing section {section.name}: {e}")
