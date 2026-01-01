# Job Portal Project (B4)

## Overview
A comprehensive Job Portal application built with Django 5.x. This platform connects Job Seekers with Recruiters, allowing for job posting, searching, applying, and profile management.

### Key Features
- **User Roles**: Separate dashboards for Job Seekers and Recruiters.
- **Job Management**: Recruiters can post, edit, delete, and view applicants for jobs.
- **Job Search**: Seekers can search and filter jobs by category, location, etc.
- **Applications**: Seekers can apply for jobs with resumes and cover letters.
- **Profile Management**: Detailed profiles with Experience, Education, Skills, and Languages.
- **Messaging**: Integrated messaging system between applicants and recruiters.

### Tech Stack
- **Backend**: Python 3.x, Django 5.2.5
- **Database**: SQLite (Default) / Customizable
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap (inferred)
- **Authentication**: Django Auth, Django AllAuth

---

## Installation & Setup

Follow these steps to set up the project locally on your machine.

### Prerequisites
- **Python 3.10+** installed.
- **pip** (Python package manager).
- **Git** installed.

### 1. Clone the Repository
Open your terminal or command prompt and run:
```bash
git clone <repository-url>
cd "rajeshdiu Job-Portal-Project-B4 main myProject"
```

### 2. Create a Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
Install the required Python packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
Set up the database tables:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a Superuser (Admin)
Create an admin account to access the Django Admin Panel:
```bash
python manage.py createsuperuser
```
Follow the prompts to set a username, email, and password.

### 6. Run the Development Server
Start the Django local server:

**Windows:**
```bash
python manage.py runserver
```

**macOS / Linux:**
```bash
python3 manage.py runserver
```

### 7. Access the Application
- **Main Site**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Admin Panel**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## Usage Guide

### For Recruiters
1.  Sign up as a **Recruiter**.
2.  Go to your Dashboard to **Post a Job**.
3.  Manage your posted jobs and view the **Applicant List**.
4.  Schedule interviews or reject applications directly from the dashboard.

### For Job Seekers
1.  Sign up as a **Job Seeker**.
2.  Complete your **Profile** (Basic Info, Skills, Education, Language).
    *   *Note: Languages must be added to the Admin Panel first.*
3.  Browse the **Job Feed** or search for specific roles.
4.  **Apply** to jobs and track your application status.

### Admin Configuration
- To add **Languages** or **Skills** to the master list:
    1.  Log in to `/admin`.
    2.  Navigate to **Intermediate Language Models** or **Intermediate Skill Models**.
    3.  Add new entries (e.g., "English", "Python") there.

## Management & Maintenance

### Default Admin Credentials
If you are using the pre-configured database (or after following the setup below), try these default credentials:
- **Username**: `admin`
- **Password**: `admin`

*(If these do not work, see "Create a Superuser" below)*

### How to Create a Superuser
To create a new admin account with full permissions:
1.  Open your terminal in the project folder.
2.  Run the command:
    ```bash
    python manage.py createsuperuser
    ```
3.  Enter a **Username** (e.g., `admin`).
4.  Enter an **Email** (can be left blank).
5.  Enter a **Password** and confirm it (it won't show while typing).

### How to Clean the Database
If you want to delete all data and start fresh (wipe the database):

**Option 1: Flush (Keeps tables, deletes data)**
This deletes all data but keeps the database structure intact.
```bash
python manage.py flush
```
*You will be asked to confirm with 'yes'.*

**Option 2: Hard Reset (Deletes everything)**
1.  Delete the `db.sqlite3` file in your project folder.
2.  Delete all migration files inside `myApp/migrations/` **EXCEPT** `__init__.py`.
3.  Run migrations again:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser
    ```

## Troubleshooting

- **`TemplateSyntaxError`**: Ensure you have pulled the latest code updates, as recent fixes for template syntax have been applied.
- **Static Files**: If images or styles are missing, verify the `static` and `media` directories are correctly configured in `settings.py`.
# Job-Portal-Batch-01
# Job-Portal-Batch-01
