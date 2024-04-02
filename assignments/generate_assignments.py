"""
This script automates the process of creating and setting up example assignments for grading practice in multiple courses on Canvas LMS (Learning Management System). 
It reads course and assignment configurations from YAML files and uses the Canvas API to create assignments with specified parameters
and associate them with rubrics if provided.

Prerequisites:
- A Canvas API URL and API key are required for authentication and must be set as environment variables (`CANVAS_API_URL` and `CANVAS_API_KEY`).
- The `canvasapi` Python package must be installed to interact with the Canvas API.
- Two YAML configuration files are needed:
  - `courses.yml`: Specifies the list of courses with their Canvas IDs and the number of assignments to create for each course. Each entry should include `canvas_id`, `name`, and optionally `num_create_assignments` which defaults to 1 if not specified.
  - `assignment.yml`: Contains the assignment parameters for creation. Each assignment can include a name, parameters for the assignment (`params`), and an optional `rubric_id` for rubric association. The `params` key should include assignment details like description, submission types, grading type, points possible, and published status.

Operations performed by the script:
1. Validates the presence of required environment variables.
2. Loads course and assignment configurations from the `courses.yml` and `assignment.yml` files.
3. Iterates over each course listed in `courses.yml`:
   a. Retrieves the course from Canvas using its Canvas ID.
   b. Fetches existing assignments to prevent duplicate creations.
   c. For each assignment configuration in `assignment.yml`, creates a specified number of assignments based on `num_create_assignments` and associates them with a rubric if `rubric_id` is provided.
   d. Logs the creation of assignments and any errors encountered during the process, such as issues fetching courses, creating assignments, or associating rubrics.

Usage:
1. Ensure that `canvasapi`, `pyyaml`, and `python-dotenv` packages are installed.
2. Set the `CANVAS_API_URL` and `CANVAS_API_KEY` environment variables.
3. Prepare the `courses.yml` and `assignment.yml` configuration files according to the specified format.
4. Run the script in an environment where Python 3 and the required packages are installed.

Note: This script assumes that the Canvas API URL and key provided have sufficient permissions to create assignments and enroll users in the specified courses.
"""

import yaml
import os
from dotenv import load_dotenv
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException

ASSIGNMENT_PARAMS_FILE = "assignment.yml"
COURSES_FILE = "courses.yml"

# Load environment variables for API access
load_dotenv()
CANVAS_API_KEY = os.environ.get("CANVAS_API_KEY")
CANVAS_API_URL = os.environ.get("CANVAS_API_URL")

if not CANVAS_API_URL or not CANVAS_API_KEY:
    print(
        "Required environment variables (CANVAS_API_URL or CANVAS_API_KEY) are not set."
    )
    exit(1)

try:
    with open(COURSES_FILE, "r") as file:
        course_list = yaml.load(file, Loader=yaml.FullLoader)
except FileNotFoundError:
    print(f"File {COURSES_FILE} not found.")
    exit(1)
except yaml.YAMLError as e:
    print(f"Error parsing the YAML file: {e}")
    exit(1)

try:
    with open(ASSIGNMENT_PARAMS_FILE, "r") as file:
        assignment_list = yaml.load(file, Loader=yaml.FullLoader)
except FileNotFoundError:
    print(f"File {ASSIGNMENT_PARAMS_FILE} not found.")
    exit(1)
except yaml.YAMLError as e:
    print(f"Error parsing the YAML file: {e}")
    exit(1)

canvas = Canvas(CANVAS_API_URL, CANVAS_API_KEY)

for course_info in course_list:
    course_canvas_id = course_info["canvas_id"]
    course_name = course_info["name"]
    num_create_assignments = course_info.get("num_create_assignments", 1)

    try:
        course = canvas.get_course(course_canvas_id)
    except CanvasException as e:
        print(f"Error getting course {course_name} (ID: {course_canvas_id}): {e}")
        continue

    existing_assignments = [assignment.name for assignment in course.get_assignments()]

    for assignment in assignment_list:
        assignment_base_name = assignment.get("name", "Assignment")
        assignment_rubric_id = assignment.get("rubric_id", None)
        for i in range(1, num_create_assignments + 1):
            assignment_name = f"{assignment_base_name}{i}"
            if assignment_name in existing_assignments:
                print(
                    f"Assignment {assignment_name} already exists in {course_name}, skipping creation."
                )
                continue

            assignment_params = assignment.get("params", {}).copy()
            assignment_params["name"] = assignment_name

            try:
                new_assignment = course.create_assignment(assignment=assignment_params)
                if assignment_rubric_id:
                    course.create_rubric_association(
                        rubric_association={
                            "rubric_id": assignment_rubric_id,
                            "association_id": new_assignment.id,
                            "use_for_grading": True,
                            "association_type": "Assignment",
                            "purpose": "grading",
                            "bookmarked": False,
                        }
                    )
                print(
                    f"Created and associated rubric for assignment: {assignment_name} in {course_name}"
                )
            except CanvasException as e:
                print(
                    f"Error creating assignment {assignment_name} in {course_name} or associating rubric: {e}"
                )
