"""
Script: Create Example Assignments for Grading Practice
Description:
    Automates the setup of example assignments for grading practice across multiple Canvas LMS courses.
    It utilizes course and assignment configurations defined in YAML files to create assignments
    with specific parameters and associates them with rubrics when provided.

Prerequisites:
    - Canvas LMS API URL and API key set as environment variables (CANVAS_API_URL and CANVAS_API_KEY).
    - 'canvasapi', 'pyyaml', and 'python-dotenv' Python packages installed.
    - courses.yml: Lists courses with Canvas IDs and the number of assignments to create for each.
    - assignment.yml: Defines parameters for each assignment, including optional rubric IDs.

Operations:
    1. Validates the presence of necessary environment variables.
    2. Loads configurations from courses.yml and assignment.yml.
    3. For each course:
       a. Retrieves the course by Canvas ID.
       b. Checks for existing assignments to avoid duplicates.
       c. Creates assignments as defined, associating them with rubrics if specified.
       d. Reports on the creation process and handles any errors encountered.

Usage:
    Ensure all prerequisites are met, set the environment variables, prepare the configuration files,
    and run the script in an environment with Python 3 and the required packages.

Note:
    Assumes sufficient permissions for assignment creation and rubric association via the provided API key.
"""

import yaml
import os
from dotenv import load_dotenv
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException

# Configuration file paths
ASSIGNMENT_PARAMS_FILE = "assignment.yml"
COURSES_FILE = "courses.yml"

# Load and verify API access environment variables
load_dotenv()
CANVAS_API_KEY = os.environ.get("CANVAS_API_KEY")
CANVAS_API_URL = os.environ.get("CANVAS_API_URL")

if not CANVAS_API_URL or not CANVAS_API_KEY:
    print(
        "Error: Canvas API URL or API Key not set. Please check your environment variables."
    )
    exit(1)

# Load course and assignment configurations from YAML files
try:
    with open(COURSES_FILE, "r") as file:
        course_list = yaml.load(file, Loader=yaml.FullLoader)
except Exception as e:
    print(f"Failed to load courses configuration: {e}")
    exit(1)

try:
    with open(ASSIGNMENT_PARAMS_FILE, "r") as file:
        assignment_list = yaml.load(file, Loader=yaml.FullLoader)
except Exception as e:
    print(f"Failed to load assignment configuration: {e}")
    exit(1)

# Initialize Canvas API
canvas = Canvas(CANVAS_API_URL, CANVAS_API_KEY)

# Process each course for assignment creation
for course_info in course_list:
    try:
        course = canvas.get_course(course_info["canvas_id"])

        # Ensure necessary sections exist and create them if not
        # Enhances clarity on section handling before assignment creation
        required_sections = [
            course_info.get("test_student_section_name", "Test Students"),
            course_info.get("grader_section_name", "Graders"),
        ]
        existing_sections = {section.name: section for section in course.get_sections()}

        for section_name in required_sections:
            if section_name not in existing_sections:
                course.create_course_section(course_section={"name": section_name})
                print(f"Created section: {section_name} in {course_info['name']}")

        # Create assignments as specified, avoiding duplicates
        existing_assignments = [
            assignment.name for assignment in course.get_assignments()
        ]
        for assignment in assignment_list:
            for i in range(1, course_info.get("num_create_assignments", 1) + 1):
                assignment_name = f"{assignment.get('name', 'Assignment')}{i}"
                if assignment_name not in existing_assignments:
                    assignment_params = assignment.get("params", {}).copy()
                    assignment_params["name"] = assignment_name
                    new_assignment = course.create_assignment(
                        assignment=assignment_params
                    )
                    # Associate with a rubric if specified
                    if "rubric_id" in assignment:
                        course.create_rubric_association(
                            rubric_association={
                                "rubric_id": assignment["rubric_id"],
                                "association_id": new_assignment.id,
                                "use_for_grading": True,
                                "association_type": "Assignment",
                                "purpose": "grading",
                                "bookmarked": False,
                            }
                        )
                    print(f"Created: {assignment_name} in {course_info['name']}")
    except Exception as e:
        print(f"An error occurred with {course_info['name']}: {e}")
