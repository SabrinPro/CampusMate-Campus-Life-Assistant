from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
from datetime import datetime
from functools import wraps

load_dotenv()

app = Flask(__name__)

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "campusmate-secret-key")
app.config["UPLOAD_FOLDER"] = os.path.join('static', 'uploads', 'notes')
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Railway injects DATABASE_URL for MySQL add-on (format: mysql://...)
# Fall back to individual vars for local development.
_database_url = os.getenv("DATABASE_URL")
if _database_url:
    # Railway sometimes provides mysql:// — ensure pymysql driver
    if _database_url.startswith("mysql://"):
        _database_url = _database_url.replace("mysql://", "mysql+pymysql://", 1)
    elif _database_url.startswith("mysql+mysqlconnector://"):
        _database_url = _database_url.replace("mysql+mysqlconnector://", "mysql+pymysql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = _database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}"
        f"/{os.getenv('DB_NAME')}"
    )

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ---------------------------------------------------------------------------
# AUTH DECORATORS
# ---------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.")
            return redirect(url_for("login"))
        if not session.get("is_admin"):
            flash("Admin access required.")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# MODELS
# ---------------------------------------------------------------------------

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class LoginLog(db.Model):
    __tablename__ = "login_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    action = db.Column(db.String(20), nullable=False)
    action_time = db.Column(db.DateTime, default=datetime.utcnow)


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False, default="General")
    max_seats = db.Column(db.Integer, nullable=False, default=50)
    created_by = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class EventRegistration(db.Model):
    __tablename__ = "event_registrations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    event_id = db.Column(db.Integer, nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)


class Notice(db.Model):
    __tablename__ = "notices"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    date_published = db.Column(db.DateTime, default=datetime.utcnow)
    priority = db.Column(db.String(20), default="Normal")


class StudyGroup(db.Model):
    __tablename__ = "study_groups"

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(120), nullable=False)
    group_name = db.Column(db.String(150), nullable=False)
    members_count = db.Column(db.Integer, default=0)
    meeting_time = db.Column(db.String(100), nullable=False)
    created_by = db.Column(db.Integer, nullable=True)


class GroupMembership(db.Model):
    __tablename__ = "group_memberships"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    group_id = db.Column(db.Integer, nullable=False)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    # Status values: Pending | Approved | Rejected
    status = db.Column(db.String(20), default="Pending")


class Club(db.Model):
    __tablename__ = "clubs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    members_count = db.Column(db.Integer, default=0)
    created_by = db.Column(db.Integer, nullable=True)


class LostFound(db.Model):
    __tablename__ = "lost_found"

    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    item_type = db.Column(db.String(20), nullable=False)
    # Status values: Active | Resolved
    status = db.Column(db.String(30), default="Active")
    posted_by = db.Column(db.Integer, nullable=False)
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)


class CampusIssue(db.Model):
    __tablename__ = "campus_issues"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    # Status values: Pending | In Progress | Resolved
    status = db.Column(db.String(30), default="Pending")
    created_by = db.Column(db.Integer, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(180), nullable=False)
    message = db.Column(db.Text, nullable=False)
    kind = db.Column(db.String(50), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Resource(db.Model):
    __tablename__ = "resources"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=False)
    resource_url = db.Column(db.String(500), nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    created_by = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------------------------------------------------------------------
# HOME
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# SIGNUP
# ---------------------------------------------------------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            flash("Email already registered.")
            return redirect(url_for("signup"))

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please login.")
        return redirect(url_for("login"))

    return render_template("signup.html")


# ---------------------------------------------------------------------------
# LOGIN
# ---------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_email"] = user.email
            session["is_admin"] = bool(user.is_admin)

            db.session.add(LoginLog(user_id=user.id, email=user.email, action="login"))
            db.session.commit()

            return redirect(url_for("admin_dashboard") if user.is_admin else url_for("dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")


# ---------------------------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------------------------

@app.route("/logout")
def logout():
    user_id = session.get("user_id")
    if user_id:
        user = db.session.get(User, user_id)
        if user:
            db.session.add(LoginLog(user_id=user.id, email=user.email, action="logout"))
            db.session.commit()

    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("home"))


# ---------------------------------------------------------------------------
# PROFILE
# ---------------------------------------------------------------------------

@app.route("/profile")
@login_required
def profile():
    user = db.session.get(User, session["user_id"])
    return render_template("profile.html", user=user)


@app.route("/profile/update", methods=["POST"])
@login_required
def update_profile():
    user = db.session.get(User, session["user_id"])

    name = request.form.get("name", "").strip()
    current_password = request.form.get("current_password", "").strip()
    new_password = request.form.get("password", "").strip()

    if not name:
        flash("Name cannot be empty.")
        return redirect(url_for("profile"))

    user.name = name

    if new_password:
        # Require current password verification before changing password
        if not current_password or not check_password_hash(user.password_hash, current_password):
            flash("Current password is incorrect.")
            return redirect(url_for("profile"))
        user.password_hash = generate_password_hash(new_password)

    db.session.commit()
    session["user_name"] = user.name
    flash("Profile updated successfully.")
    return redirect(url_for("profile"))


# ---------------------------------------------------------------------------
# STUDENT DASHBOARD
# ---------------------------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))

    registered_events = (
        db.session.query(Event)
        .join(EventRegistration, Event.id == EventRegistration.event_id)
        .filter(EventRegistration.user_id == session["user_id"])
        .order_by(Event.date.asc())
        .all()
    )

    notifications_list = (
        Notification.query
        .filter_by(user_id=session["user_id"])
        .order_by(Notification.id.desc())
        .limit(3)
        .all()
    )

    return render_template(
        "dashboard.html",
        registered_events=registered_events,
        notifications=notifications_list
    )


# ---------------------------------------------------------------------------
# STUDENT EVENTS
# ---------------------------------------------------------------------------

@app.route("/events")
@login_required
def events():
    events_list = Event.query.order_by(Event.date.asc()).all()

    registered_event_ids = {
        r.event_id
        for r in EventRegistration.query.filter_by(user_id=session["user_id"]).all()
    }

    available_seats = {}
    for event in events_list:
        count = EventRegistration.query.filter_by(event_id=event.id).count()
        available_seats[event.id] = max(event.max_seats - count, 0)

    return render_template(
        "events.html",
        events=events_list,
        registered_event_ids=registered_event_ids,
        available_seats=available_seats
    )


@app.route("/events/register/<int:event_id>", methods=["POST"])
@login_required
def register_event(event_id):
    event = Event.query.get_or_404(event_id)

    if EventRegistration.query.filter_by(user_id=session["user_id"], event_id=event.id).first():
        flash("You are already registered for this event.")
        return redirect(url_for("events"))

    if EventRegistration.query.filter_by(event_id=event.id).count() >= event.max_seats:
        flash("This event is already full.")
        return redirect(url_for("events"))

    db.session.add(EventRegistration(user_id=session["user_id"], event_id=event.id))
    db.session.add(Notification(
        user_id=session["user_id"],
        title="Event Registration",
        message=f"You successfully registered for {event.title}.",
        kind="Event",
        is_read=False
    ))
    db.session.commit()

    flash("Event registration successful.")
    return redirect(url_for("events"))


# ---------------------------------------------------------------------------
# NOTICES
# ---------------------------------------------------------------------------

@app.route("/notices")
@login_required
def notices():
    return render_template(
        "notices.html",
        notices=Notice.query.order_by(Notice.date_published.desc()).all()
    )


# ---------------------------------------------------------------------------
# STUDY GROUPS
# ---------------------------------------------------------------------------

@app.route("/groups")
@login_required
def groups():
    groups_list = StudyGroup.query.order_by(StudyGroup.id.desc()).all()
    group_status = {
        m.group_id: m.status
        for m in GroupMembership.query.filter_by(user_id=session["user_id"]).all()
    }
    return render_template("groups.html", groups=groups_list, group_status=group_status)


@app.route("/groups/join/<int:group_id>", methods=["POST"])
@login_required
def join_group(group_id):
    group = StudyGroup.query.get_or_404(group_id)

    if GroupMembership.query.filter_by(user_id=session["user_id"], group_id=group.id).first():
        flash("You have already requested to join this group.")
        return redirect(url_for("groups"))

    db.session.add(GroupMembership(user_id=session["user_id"], group_id=group.id, status="Pending"))
    db.session.commit()
    flash("Join request sent successfully.")
    return redirect(url_for("groups"))


# ---------------------------------------------------------------------------
# CLUBS
# ---------------------------------------------------------------------------

@app.route("/clubs")
@login_required
def clubs():
    return render_template("clubs.html", clubs=Club.query.order_by(Club.id.desc()).all())


# ---------------------------------------------------------------------------
# RESOURCES
# ---------------------------------------------------------------------------

@app.route("/resources")
@login_required
def resources():
    return render_template(
        "resources.html",
        resources=Resource.query.order_by(Resource.id.desc()).all()
    )

@app.route("/resources/upload", methods=["POST"])
@login_required
def upload_resource():
    title = request.form.get("title")
    subject = request.form.get("subject")
    description = request.form.get("description")
    
    if "note_file" not in request.files:
        flash("No file part provided.")
        return redirect(url_for("resources"))
        
    file = request.files["note_file"]
    if file.filename == "":
        flash("No selected file.")
        return redirect(url_for("resources"))
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        resource_url = url_for('static', filename=f"uploads/notes/{filename}")
        
        new_resource = Resource(
            title=title,
            subject=subject,
            description=description,
            resource_url=resource_url,
            created_by=session.get("user_id")
        )
        db.session.add(new_resource)
        db.session.commit()
        flash("Resource shared successfully.")
    else:
        flash("Invalid file format. Only PDF is allowed.")
        
    return redirect(url_for("resources"))



# ---------------------------------------------------------------------------
# LOST & FOUND
# ---------------------------------------------------------------------------

@app.route("/lost-found")
@login_required
def lost_found():
    return render_template("lost_found.html", items=LostFound.query.order_by(LostFound.id.desc()).all())


@app.route("/lost-found/add", methods=["POST"])
@login_required
def add_lost_found():
    db.session.add(LostFound(
        item_name=request.form["item_name"],
        description=request.form["description"],
        location=request.form["location"],
        item_type=request.form["item_type"],
        status="Active",
        posted_by=session["user_id"]
    ))
    db.session.commit()
    flash("Lost & Found report submitted successfully.")
    return redirect(url_for("lost_found"))


# ---------------------------------------------------------------------------
# CAMPUS ISSUES
# ---------------------------------------------------------------------------

@app.route("/issues")
@login_required
def issues():
    return render_template(
        "issues.html",
        issues=CampusIssue.query.order_by(CampusIssue.id.desc()).all()
    )


@app.route("/issues/add", methods=["POST"])
@login_required
def add_issue():
    db.session.add(CampusIssue(
        title=request.form["title"],
        category=request.form["category"],
        location=request.form["location"],
        description=request.form["description"],
        status="Pending",
        created_by=session["user_id"]
    ))
    db.session.commit()
    flash("Campus issue submitted successfully.")
    return redirect(url_for("issues"))


# ---------------------------------------------------------------------------
# NOTIFICATIONS
# ---------------------------------------------------------------------------

@app.route("/notifications")
@login_required
def notifications():
    return render_template(
        "notifications.html",
        notifications=Notification.query
            .filter_by(user_id=session["user_id"])
            .order_by(Notification.id.desc())
            .all()
    )


# ---------------------------------------------------------------------------
# ADMIN DASHBOARD
# ---------------------------------------------------------------------------

@app.route("/admin")
@admin_required
def admin_dashboard():
    return render_template(
        "admin/dashboard.html",
        total_users=User.query.count(),
        total_events=Event.query.count(),
        total_notices=Notice.query.count(),
        pending_issues=CampusIssue.query.filter_by(status="Pending").count(),
        login_logs=LoginLog.query.order_by(LoginLog.action_time.desc()).all()
    )


# ---------------------------------------------------------------------------
# ADMIN EVENTS
# ---------------------------------------------------------------------------

@app.route("/admin/events")
@admin_required
def admin_events():
    return render_template("admin/events.html", events=Event.query.order_by(Event.date.asc()).all())


@app.route("/admin/events/add", methods=["POST"])
@admin_required
def admin_add_event():
    db.session.add(Event(
        title=request.form["title"],
        date=datetime.strptime(request.form["event_date"], "%Y-%m-%d").date(),
        time=datetime.strptime(request.form["event_time"], "%H:%M").time(),
        location=request.form["location"],
        description=request.form["description"],
        category=request.form.get("category", "General") or "General",
        max_seats=int(request.form["max_seats"]),
        created_by=session["user_id"]
    ))
    db.session.commit()
    flash("Event added successfully.")
    return redirect(url_for("admin_events"))


@app.route("/admin/events/edit/<int:event_id>", methods=["GET", "POST"])
@admin_required
def admin_edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == "POST":
        event.title = request.form["title"]
        event.date = datetime.strptime(request.form["event_date"], "%Y-%m-%d").date()
        event.time = datetime.strptime(request.form["event_time"], "%H:%M").time()
        event.location = request.form["location"]
        event.description = request.form["description"]
        event.category = request.form.get("category", "General") or "General"
        event.max_seats = int(request.form["max_seats"])
        db.session.commit()
        flash("Event updated successfully.")
        return redirect(url_for("admin_events"))

    return render_template("admin/edit_event.html", event=event)


@app.route("/admin/events/delete/<int:event_id>", methods=["POST"])
@admin_required
def admin_delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    EventRegistration.query.filter_by(event_id=event.id).delete(synchronize_session=False)
    db.session.delete(event)
    db.session.commit()
    flash("Event deleted successfully.")
    return redirect(url_for("admin_events"))


# ---------------------------------------------------------------------------
# ADMIN NOTICES
# ---------------------------------------------------------------------------

@app.route("/admin/notices")
@admin_required
def admin_notices():
    return render_template(
        "admin/notices.html",
        notices=Notice.query.order_by(Notice.date_published.desc()).all()
    )


@app.route("/admin/notices/add", methods=["POST"])
@admin_required
def admin_add_notice():
    db.session.add(Notice(
        title=request.form["title"],
        content=request.form["content"],
        category=request.form["category"],
        priority=request.form["priority"]
    ))
    db.session.commit()
    flash("Notice published successfully.")
    return redirect(url_for("admin_notices"))


@app.route("/admin/notices/edit/<int:notice_id>", methods=["GET", "POST"])
@admin_required
def admin_edit_notice(notice_id):
    notice = Notice.query.get_or_404(notice_id)

    if request.method == "POST":
        notice.title = request.form["title"]
        notice.content = request.form["content"]
        notice.category = request.form["category"]
        notice.priority = request.form["priority"]
        db.session.commit()
        flash("Notice updated successfully.")
        return redirect(url_for("admin_notices"))

    return render_template("admin/edit_notice.html", notice=notice)


@app.route("/admin/notices/delete/<int:notice_id>", methods=["POST"])
@admin_required
def admin_delete_notice(notice_id):
    notice = Notice.query.get_or_404(notice_id)
    db.session.delete(notice)
    db.session.commit()
    flash("Notice deleted successfully.")
    return redirect(url_for("admin_notices"))


# ---------------------------------------------------------------------------
# ADMIN GROUPS
# ---------------------------------------------------------------------------

@app.route("/admin/groups")
@admin_required
def admin_groups():
    groups_list = StudyGroup.query.order_by(StudyGroup.id.desc()).all()
    memberships = GroupMembership.query.order_by(GroupMembership.join_date.desc()).all()

    group_requests = []
    for membership in memberships:
        user = db.session.get(User, membership.user_id)
        group = db.session.get(StudyGroup, membership.group_id)
        if user and group:
            group_requests.append({
                "id": membership.id,
                "user_name": user.name,
                "group_name": group.group_name,
                "join_date": membership.join_date.strftime("%d %b %Y"),
                "status": membership.status
            })

    return render_template("admin/groups.html", groups=groups_list, group_requests=group_requests)


@app.route("/admin/groups/add", methods=["POST"])
@admin_required
def admin_add_group():
    db.session.add(StudyGroup(
        subject=request.form["subject"],
        group_name=request.form["group_name"],
        meeting_time=request.form["meeting_time"],
        members_count=0,
        created_by=session["user_id"]
    ))
    db.session.commit()
    flash("Study group created successfully.")
    return redirect(url_for("admin_groups"))


@app.route("/admin/groups/delete/<int:group_id>", methods=["POST"])
@admin_required
def admin_delete_group(group_id):
    group = StudyGroup.query.get_or_404(group_id)
    GroupMembership.query.filter_by(group_id=group.id).delete(synchronize_session=False)
    db.session.delete(group)
    db.session.commit()
    flash("Study group deleted successfully.")
    return redirect(url_for("admin_groups"))


@app.route("/admin/groups/approve/<int:request_id>", methods=["POST"])
@admin_required
def approve_group_request(request_id):
    membership = db.session.get(GroupMembership, request_id)
    if membership is None:
        flash("Join request not found.")
        return redirect(url_for("admin_groups"))

    if membership.status == "Approved":
        flash("This request is already approved.")
        return redirect(url_for("admin_groups"))

    membership.status = "Approved"
    group = db.session.get(StudyGroup, membership.group_id)
    if group:
        group.members_count = (group.members_count or 0) + 1

    db.session.commit()
    flash("Join request approved.")
    return redirect(url_for("admin_groups"))


@app.route("/admin/groups/reject/<int:request_id>", methods=["POST"])
@admin_required
def reject_group_request(request_id):
    membership = db.session.get(GroupMembership, request_id)
    if membership is None:
        flash("Join request not found.")
        return redirect(url_for("admin_groups"))

    if membership.status == "Approved":
        group = db.session.get(StudyGroup, membership.group_id)
        if group and group.members_count > 0:
            group.members_count -= 1

    membership.status = "Rejected"
    db.session.commit()
    flash("Join request rejected.")
    return redirect(url_for("admin_groups"))


# ---------------------------------------------------------------------------
# ADMIN CLUBS
# ---------------------------------------------------------------------------

@app.route("/admin/clubs")
@admin_required
def admin_clubs():
    return render_template("admin/clubs.html", clubs=Club.query.order_by(Club.id.desc()).all())


@app.route("/admin/clubs/add", methods=["POST"])
@admin_required
def admin_add_club():
    db.session.add(Club(
        name=request.form["name"],
        description=request.form["description"],
        members_count=0,
        created_by=session["user_id"]
    ))
    db.session.commit()
    flash("Club created successfully.")
    return redirect(url_for("admin_clubs"))


@app.route("/admin/clubs/edit/<int:club_id>", methods=["GET", "POST"])
@admin_required
def admin_edit_club(club_id):
    club = Club.query.get_or_404(club_id)

    if request.method == "POST":
        club.name = request.form["name"]
        club.description = request.form["description"]
        db.session.commit()
        flash("Club updated successfully.")
        return redirect(url_for("admin_clubs"))

    return render_template("admin/edit_club.html", club=club)


@app.route("/admin/clubs/delete/<int:club_id>", methods=["POST"])
@admin_required
def admin_delete_club(club_id):
    club = Club.query.get_or_404(club_id)
    db.session.delete(club)
    db.session.commit()
    flash("Club deleted successfully.")
    return redirect(url_for("admin_clubs"))


# ---------------------------------------------------------------------------
# ADMIN RESOURCES
# ---------------------------------------------------------------------------

@app.route("/admin/resources")
@admin_required
def admin_resources():
    return render_template(
        "admin/resources.html",
        resources=Resource.query.order_by(Resource.id.desc()).all()
    )


@app.route("/admin/resources/add", methods=["POST"])
@admin_required
def admin_add_resource():
    db.session.add(Resource(
        title=request.form["title"],
        subject=request.form["subject"],
        description=request.form["description"],
        resource_url=request.form["resource_url"],
        created_by=session["user_id"]
    ))
    db.session.commit()
    flash("Resource added successfully.")
    return redirect(url_for("admin_resources"))


# ---------------------------------------------------------------------------
# ADMIN LOST & FOUND
# ---------------------------------------------------------------------------

@app.route("/admin/lost-found")
@admin_required
def admin_lost_found():
    return render_template("admin/lost_found.html", items=LostFound.query.order_by(LostFound.id.desc()).all())


@app.route("/admin/lost-found/resolve/<int:item_id>", methods=["POST"])
@admin_required
def admin_resolve_lost_found(item_id):
    item = LostFound.query.get_or_404(item_id)
    item.status = "Resolved"
    db.session.commit()
    flash("Lost & Found item marked as resolved.")
    return redirect(url_for("admin_lost_found"))


# ---------------------------------------------------------------------------
# ADMIN CAMPUS ISSUES
# ---------------------------------------------------------------------------

@app.route("/admin/issues")
@admin_required
def admin_issues():
    return render_template(
        "admin/issues.html",
        issues=CampusIssue.query.order_by(CampusIssue.id.desc()).all()
    )


@app.route("/admin/issues/update/<int:issue_id>", methods=["POST"])
@admin_required
def update_issue(issue_id):
    issue = CampusIssue.query.get_or_404(issue_id)
    new_status = request.form["status"]

    if new_status not in ["Pending", "In Progress", "Resolved"]:
        flash("Invalid status.")
        return redirect(url_for("admin_issues"))

    old_status = issue.status
    issue.status = new_status

    if old_status != new_status:
        db.session.add(Notification(
            user_id=issue.created_by,
            title="Campus Issue Update",
            message=f"Your reported issue '{issue.title}' is now {new_status}.",
            kind="Issue",
            is_read=False
        ))

    db.session.commit()
    flash("Issue status updated successfully.")
    return redirect(url_for("admin_issues"))


# ---------------------------------------------------------------------------
# ADMIN USERS
# ---------------------------------------------------------------------------

@app.route("/admin/users")
@admin_required
def admin_users():
    return render_template(
        "admin/users.html",
        users=User.query.order_by(User.created_at.desc()).all()
    )


# ---------------------------------------------------------------------------
# DB INIT & RUN
# ---------------------------------------------------------------------------

with app.app_context():
    db.create_all()

    # Seed admin if no admin exists
    if not User.query.filter_by(is_admin=True).first():
        admin = User(
            name="Admin",
            email="admin@campusmate.com",
            password_hash=generate_password_hash("admin123"),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=False)