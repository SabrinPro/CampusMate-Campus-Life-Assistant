# CampusMate — Smart Campus Life Management Platform

This package is the complete website implementation based on the submitted **A Smart Campus Life Management Platform** proposal. The proposal specifies an HTML/CSS/JavaScript frontend, Python Flask backend and MySQL database. fileciteturn0file0L10-L15

## Tech stack — kept simple

- **Frontend:** HTML + CSS + vanilla JavaScript
- **Backend:** Python + Flask
- **Database:** MySQL
- **No React, Bootstrap, Tailwind, Vue or other frontend framework**
- MySQL is accessed directly from Flask with `mysql-connector-python`.

The proposal's requested core services are covered: authentication/dashboard, events, notices, study groups, clubs, resources, lost & found, campus issues and notifications. fileciteturn0file0L50-L73 fileciteturn0file0L75-L95

## Design direction

The UI follows the supplied reference image: deep green/black surfaces, bright lime-green accents, large condensed headings, rounded dashboard cards, strong whitespace, compact navigation and modern responsive layouts. The Dribbble reference you supplied is also a dashboard-style visual reference with a clean, structured interface and published color palette. citeturn0search0turn0search5

The design is an original CampusMate implementation rather than a copy of the reference site.

## 1. Requirements

Install:

- Python 3.11+
- MySQL 8+
- VS Code recommended

## 2. Create the MySQL database

Open MySQL Workbench and run:

1. `schema.sql`
2. `seed.sql`

The schema includes the proposal's main data areas and adds small supporting tables for resources and notifications so those UI features can work. The proposal describes MySQL as the database storing users, events, notices, study groups, clubs and issues. fileciteturn0file0L132-L143

### Demo admin

- Email: `admin@campusmate.local`
- Password: `admin123`

## 3. Install Python packages

Windows PowerShell:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 4. Configure MySQL

If your local MySQL root account has a password, set it before starting Flask:

```powershell
$env:DB_HOST="localhost"
$env:DB_PORT="3306"
$env:DB_USER="root"
$env:DB_PASSWORD="YOUR_MYSQL_PASSWORD"
$env:DB_NAME="campusmate"
$env:SECRET_KEY="change-this-secret"
```

If your MySQL root account has no password, the default configuration in `app.py` works without changing `DB_PASSWORD`.

## 5. Run the website

```powershell
python app.py
```

Open:

`http://127.0.0.1:5000`

## Main pages

- `/` — public home
- `/register` — student registration
- `/login` — login/logout
- `/dashboard` — personalized student dashboard
- `/events` — search/filter/register for events
- `/notices` — notice search
- `/clubs` — club directory
- `/study-groups` — browse/request membership
- `/resources` — study resources
- `/lost-found` — post/browse lost & found
- `/issues` — report and track campus issues
- `/notifications` — notification list
- `/profile` — update personal profile
- `/admin` — administrator management center

## Folder structure

```text
CampusMate_HTML_CSS_JS_Flask_MySQL/
├── app.py
├── config.py
├── requirements.txt
├── schema.sql
├── seed.sql
├── README.md
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── events.html
│   ├── notices.html
│   ├── clubs.html
│   ├── study_groups.html
│   ├── resources.html
│   ├── lost_found.html
│   ├── issues.html
│   ├── notifications.html
│   ├── profile.html
│   └── admin.html
└── static/
    ├── css/style.css
    ├── js/app.js
    └── images/
```

## Proposal architecture

The implementation follows the simple flow in the proposal: browser HTML/CSS/JS → Flask → MySQL → Flask/Jinja2 → HTML back to the browser. fileciteturn0file0L114-L131

## Important note

The project is intentionally built without a separate REST API layer or frontend framework, matching the proposal's simplified architecture. The proposal itself describes the project as HTML/CSS/JS → Flask → MySQL with no separate API layer. fileciteturn0file0L170-L175
