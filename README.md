# RubricLab

RubricLab is designed to streamline the process of setting up practice grading environments within Canvas LMS. It facilitates the automatic enrollment of test students, creation of test assignments, and generation of test submissions. RubricLab is useful for educators and developers who are looking to create a controlled environment for testing grading schemas, rubric implementations, or simply to enhance their understanding of the Canvas LMS grading functionalities.

## Features

- **Test Student Enrollment:** Automates the enrollment of test students into specified Canvas courses, allowing for a realistic grading environment.
- **Test Assignment Generation:** Dynamically creates test assignments with customizable parameters to suit various testing needs.
- **Test Submissions Creation:** Generates test submissions for the created assignments, simulating student activity and submissions for grading practice.

## Getting Started

### Prerequisites

- A Canvas LMS account with API access.
- Python 3.x installed on your machine.
- Installation of required Python packages: `canvasapi`, `pyyaml`, and `python-dotenv`.

### Setup

1. **Clone the Repository**

    ```
    git clone https://github.com/yourusername/rubriclab.git
    cd rubriclab
    ```

2. **Environment Configuration**

    Create a new file named `.env` and fill in your Canvas API URL and API Key:

    ```
    CANVAS_API_URL='https://yourinstitution.instructure.com'
    CANVAS_API_KEY='your_api_key_here'
    ```

3. **Install Dependencies**

    ```
    pip install -r requirements.txt
    ```

### Usage

1. **Prepare Configuration Files**

    - `courses.yml`: Define the courses where test students will be enrolled, assignments created, and submissions made.
    - `submissions.yml`: Specify the test students (by their SIS login ID) and the submission details for each test assignment.
    - `assignment.yml`: Outline the test assignments to be created, including their names, optional rubric IDs, and other parameters.

2. **Run the Scripts**

    - To enroll test students, generate assignments, and create submissions:

    ```
    python generate_assignments.py
    python generate_submissions.py
    ```

    This script will process the configurations defined in your YAML files and interact with the Canvas API to set up your test environment.
