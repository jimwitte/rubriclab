"""
This script is designed to automate the process of enrolling test users as students in multiple courses
and submitting assignments for grading practice on their behalf on the Canvas Learning Management System (LMS). 
It targets assignments of a specific type, specified by `ASSIGNMENT_TYPE`, and makes submissions based on details provided in a YAML file.

Prerequisites:
- Canvas LMS access with API URL and key available.
- Installation of the `canvasapi` Python package to interact with the Canvas API.
- Two YAML files:
  - `courses.yml`: Lists the courses by their Canvas ID where submissions need to be made. This file is crucial for identifying the courses to which the script will apply.
  - `submissions.yml`: Contains details for each submission, including the `sis_login_id` of the user making the submission and parameters specific to the submission (e.g., submission text, type).

Key Operations:
- The script initializes by validating the presence of necessary environment variables for Canvas API authentication (`CANVAS_API_URL` and `CANVAS_API_KEY`).
- It then loads the course and submission information from the respective YAML files.
- For each course listed in `courses.yml`, it:
  1. Fetches the course object from Canvas.
  2. Attempts to enroll each user specified in `submissions.yml` into the course, if not already enrolled.
  3. Submits assignments for these users if the assignment matches the `ASSIGNMENT_TYPE` specified.

Usage Notes:
- This script assumes that users are identified by their SIS login ID, which must be specified in `submissions.yml`.
- It requires that the submission parameters in `submissions.yml` are compatible with the assignment submission types in Canvas (e.g., text entry, file upload).
- Only assignments matching the `ASSIGNMENT_TYPE` will be targeted for submission. This is specified at the top of the script and can be adjusted as needed.

Running the Script:
1. Ensure the `canvasapi` Python package is installed in your environment.
2. Set the `CANVAS_API_URL` and `CANVAS_API_KEY` environment variables with your Canvas API credentials.
3. Prepare the `courses.yml` and `submissions.yml` files with the relevant course and submission information.
4. Execute the script in an environment where Python 3 and the necessary packages are available.

Safety and Permissions:
- The script makes changes to course enrollments and submissions and therefore should be used with caution.
- Ensure that the API key used has the necessary permissions for the operations the script performs.
"""

import yaml
import os
from dotenv import load_dotenv
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException

##### CONSTANTS #####
ASSIGNMENT_TYPE = "online_text_entry"  # Desired type of assignment for submissions
COURSES_FILE = "courses.yml"  # YAML file with course information
SUBMISSION_LIST = "submissions.yml"  # YAML file containing submission details
#####################

# Load environment variables
load_dotenv()
CANVAS_API_KEY = os.environ.get("CANVAS_API_KEY")
CANVAS_API_URL = os.environ.get("CANVAS_API_URL")

# Check if both CANVAS_API_URL and CANVAS_API_KEY are set
if not all([CANVAS_API_URL, CANVAS_API_KEY]):
    print(
        "Required environment variables (CANVAS_API_URL, CANVAS_API_KEY) are not set."
    )
    exit(1)

# Load courses list from YAML file
try:
    with open(COURSES_FILE, "r") as file:
        course_list = yaml.load(file, Loader=yaml.FullLoader)
except FileNotFoundError:
    print(f"File {COURSES_FILE} not found.")
    exit(1)
except yaml.YAMLError as e:
    print(f"Error parsing YAML file: {e}")
    exit(1)

# Load submissions list from YAML file
try:
    with open(SUBMISSION_LIST, "r") as file:
        submission_list = yaml.load(file, Loader=yaml.FullLoader)
except FileNotFoundError:
    print(f"File {SUBMISSION_LIST} not found.")
    exit(1)
except yaml.YAMLError as e:
    print(f"Error parsing YAML file: {e}")
    exit(1)

# Initialize Canvas object
canvas = Canvas(CANVAS_API_URL, CANVAS_API_KEY)

# Process each course
for course_info in course_list:
    course_canvas_id = course_info["canvas_id"]
    course_name = course_info["name"]

    # Fetch the course
    try:
        course = canvas.get_course(course_canvas_id)
    except CanvasException as e:
        print(f"Error getting course {course_name}: {e}")
        continue

    # Enroll users and prepare submissions
    for s in submission_list:
        try:
            canvas_user = canvas.get_user(s["sis_login_id"], id_type="sis_login_id")
            course.enroll_user(
                canvas_user.id, "StudentEnrollment", enrollment_state="active"
            )
            s["submission_params"]["user_id"] = canvas_user.id
        except CanvasException as e:
            print(f"Error processing user {s['sis_login_id']} in {course_name}: {e}")
            continue  # Skip this user and continue with the next

    # Submit assignments
    try:
        assignments = course.get_assignments()
        for a in assignments:
            if ASSIGNMENT_TYPE in a.submission_types:
                for s in submission_list:
                    try:
                        a.submit(submission=s["submission_params"])
                        print(
                            f"Submitted {a.name} for {s['sis_login_id']} in {course_name}"
                        )
                    except CanvasException as e:
                        print(
                            f"Error submitting assignment for {s['sis_login_id']} in {course_name}: {e}"
                        )
    except CanvasException as e:
        print(f"Error fetching assignments in {course_name}: {e}")
