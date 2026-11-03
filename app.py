import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "local-development-only-change-before-deployment")
database_url = os.environ.get("DATABASE_URL")
if database_url:
    # Some providers still expose the legacy postgres:// scheme.
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "calfit.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    level = db.Column(db.String(40), default="Beginner")
    duration = db.Column(db.Integer, default=45)
    reps = db.Column(db.String(40), default="12 reps")
    calories = db.Column(db.Integer, default=5)
    equipment = db.Column(db.String(100), default="None")
    primary_muscles = db.Column(db.String(180), nullable=False)
    secondary_muscles = db.Column(db.String(180), default="")
    instructions = db.Column(db.Text, default="")
    benefits = db.Column(db.Text, default="")
    recovery = db.Column(db.Text, default="")
    video_url = db.Column(db.String(500), default="")
    image_url = db.Column(db.String(500), default="")
    is_preset = db.Column(db.Boolean, default=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

class WorkoutLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    exercise_name = db.Column(db.String(120), nullable=False)
    duration = db.Column(db.Integer, default=0)
    calories = db.Column(db.Integer, default=0)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")
        # A session can outlive a deleted/reset database account.
        # Validate the account instead of trusting the session key alone.
        if not user_id or User.query.get(user_id) is None:
            session.clear()
            flash("Your session has expired. Please log in again.", "info")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapped

def seed():
    if Exercise.query.count():
        return
    samples = [
        ("Push-ups","Chest","Beginner",180,"3 sets × 12 reps",24,"None","Chest","Triceps, Shoulders","Start in a high plank with hands slightly wider than shoulders. Lower your chest with control, keeping your body in one straight line. Press the floor away to return. Complete 3 sets of 12 controlled reps, resting 45–60 seconds between sets.","Builds pushing strength and trains the chest, triceps and shoulders.","Allow about 48 hours before another hard chest session. Stop if you feel sharp wrist or shoulder pain.","https://images.unsplash.com/photo-1598971639058-fab3c3109a00?w=900&auto=format&fit=crop","https://www.youtube.com/embed/UIcct-7b6oE"),
        ("Bodyweight Squats","Legs","Beginner",210,"3 sets × 15 reps",28,"None","Quadriceps, Glutes","Hamstrings, Core","Stand with feet around shoulder-width apart. Sit your hips down and back, keep your heels grounded, then drive through the whole foot to stand. Complete 3 sets of 15 reps with 45–60 seconds of rest.","Develops lower-body strength, coordination and mobility.","Give trained leg muscles time to recover, often around 48 hours after a demanding session.","https://hips.hearstapps.com/hmg-prod/images/man-exercising-at-home-royalty-free-image-1645047847.jpg?resize=980:*","https://www.youtube.com/embed/n_xLyzPEX7A"),
        ("Forearm Plank","Core","Beginner",150,"3 sets × 30 sec hold",15,"None","Core","Shoulders, Glutes","Place forearms on the floor with elbows under shoulders. Extend your legs and brace your abdomen. Keep your hips level and breathe steadily. Complete 3 holds of 30 seconds, resting 30–45 seconds between holds.","Builds trunk endurance and body control.","Rest until you can maintain a steady brace without your lower back sagging.","https://appbefit.com/wp-content/uploads/2026/09/forearm-plank-proper-form-hero-1024x572.webp","https://www.youtube-nocookie.com/embed/UQ78pw0WNZI"),
        ("Pike Push-ups","Shoulders","Intermediate",180,"3 sets × 8 reps",25,"None","Shoulders","Triceps, Upper chest","Start in a downward-V position. Bend your elbows and lower the top of your head toward the floor, then press back up while keeping hips high. Complete 3 sets of 8 controlled reps.","Challenges shoulder pressing strength using bodyweight.","Allow adequate shoulder recovery before repeating high-volume pressing.","https://assets.st-note.com/production/uploads/images/250859068/rectangle_large_type_2_accf2afa26096d47f72bc683783b955f.png?width=1200","https://www.youtube.com/embed/89-8waE2XKI"),
        ("Reverse Lunges","Legs","Beginner",210,"3 sets × 10 reps each leg",28,"None","Quadriceps, Glutes","Hamstrings, Core","Stand tall, step one foot backward and lower both knees comfortably. Push through the front foot to return, then alternate sides. Complete 3 sets of 10 reps per leg.","Improves unilateral leg strength and balance.","Recover between demanding leg sessions; use a shorter range if balance is limited.","https://lifefitindia.com/wp-content/uploads/editor/dumbbell-rear-lunge-exercise.webp","https://www.youtube.com/embed/mzPFverp8tM"),
        ("Mountain Climbers","Full body","Intermediate",180,"3 sets × 30 reps total",27,"None","Core","Shoulders, Hip flexors","Begin in a strong high plank. Drive one knee toward your chest, return it, and alternate smoothly without letting your hips bounce. Complete 3 sets of 30 alternating knee drives.","Combines core stability with cardiovascular demand.","Reduce pace or take a rest interval if breathing or form becomes difficult.","https://i.barbend.com/383/645/323/6/mountain-climber-2-barbend.com_.webp","https://www.youtube.com/embed/7W4JEfEKuC4"),
        ("Glute Bridge","Glutes","Beginner",180,"3 sets × 15 reps",22,"None","Glutes","Hamstrings, Core","Lie on your back with knees bent and feet flat. Brace your core, squeeze your glutes and lift your hips until your body forms a comfortable line. Complete 3 sets of 15 reps, pausing briefly at the top.","Strengthens glutes and supports hip extension.","Allow recovery after a challenging glute session; avoid over-arching your lower back.","https://static.nike.com/a/images/f_auto/dpr_1.3,cs_srgb/h_1900,c_limit/44769a3a-b7ea-462a-a989-3b0e0e9830f9/7-variations-of-glute-bridges-that-will-shake-up-your-next-workout.jpg","https://www.youtube.com/embed/LEdVLzF6kR0"),
        ("Superman Hold","Back","Beginner",150,"3 sets × 20 sec hold",14,"None","Lower back","Glutes, Upper back","Lie face down with arms extended. Gently lift arms and legs a small distance while keeping your neck neutral. Hold for 20 seconds, lower with control and repeat for 3 sets.","Trains posterior-chain endurance and body awareness.","Use a comfortable range and stop if you feel spinal discomfort.","https://evofitness.at/wp-content/uploads/2025/05/evo_banner_june_24-1200x630.jpg","https://www.youtube.com/embed/VD6ma6oe4ZA"),
    ]
    for s in samples:
        db.session.add(Exercise(name=s[0], category=s[1], level=s[2], duration=s[3], reps=s[4], calories=s[5], equipment=s[6], primary_muscles=s[7], secondary_muscles=s[8], instructions=s[9], benefits=s[10], recovery=s[11], image_url=s[12], video_url=s[13]))
    db.session.commit()

def refresh_preset_exercises():
    """Refresh built-in exercise prescriptions/media in existing SQLite databases."""
    updates = [
        ("Push-ups",180,"3 sets × 12 reps",24,"https://images.unsplash.com/photo-1598971639058-fab3c3109a00?w=900&auto=format&fit=crop","https://www.youtube.com/embed/UIcct-7b6oE"),
        ("Bodyweight Squats",210,"3 sets × 15 reps",28,"https://hips.hearstapps.com/hmg-prod/images/man-exercising-at-home-royalty-free-image-1645047847.jpg?resize=980:*","https://www.youtube.com/embed/n_xLyzPEX7A"),
        ("Forearm Plank",150,"3 sets × 30 sec hold",15,"https://appbefit.com/wp-content/uploads/2026/09/forearm-plank-proper-form-hero-1024x572.webp","https://www.youtube-nocookie.com/embed/UQ78pw0WNZI"),
        ("Pike Push-ups",180,"3 sets × 8 reps",25,"https://assets.st-note.com/production/uploads/images/250859068/rectangle_large_type_2_accf2afa26096d47f72bc683783b955f.png?width=1200","https://www.youtube.com/embed/89-8waE2XKI"),
        ("Reverse Lunges",210,"3 sets × 10 reps each leg",28,"https://lifefitindia.com/wp-content/uploads/editor/dumbbell-rear-lunge-exercise.webp","https://www.youtube.com/embed/mzPFverp8tM"),
        ("Mountain Climbers",180,"3 sets × 30 reps total",27,"https://i.barbend.com/383/645/323/6/mountain-climber-2-barbend.com_.webp","https://www.youtube.com/embed/7W4JEfEKuC4"),
        ("Glute Bridge",180,"3 sets × 15 reps",22,"https://static.nike.com/a/images/f_auto/dpr_1.3,cs_srgb/h_1900,c_limit/44769a3a-b7ea-462a-a989-3b0e0e9830f9/7-variations-of-glute-bridges-that-will-shake-up-your-next-workout.jpg","https://www.youtube.com/embed/LEdVLzF6kR0"),
        ("Superman Hold",150,"3 sets × 20 sec hold",14,"https://evofitness.at/wp-content/uploads/2025/05/evo_banner_june_24-1200x630.jpg","https://www.youtube.com/embed/VD6ma6oe4ZA"),
    ]
    for name, duration, reps, calories, image_url, video_url in updates:
        exercise = Exercise.query.filter_by(name=name, is_preset=True).first()
        if exercise:
            exercise.duration = duration
            exercise.reps = reps
            exercise.calories = calories
            exercise.image_url = image_url
            exercise.video_url = video_url
    db.session.commit()

@app.context_processor
def inject_user():
    user = None
    user_id = session.get("user_id")
    if user_id:
        user = db.session.get(User, user_id)
        if user is None:
            session.pop("user_id", None)
    return {"current_user": user}

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("landing.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name, email, password = request.form.get("name","").strip(), request.form.get("email","").strip().lower(), request.form.get("password","")
        if not name or not email or len(password) < 8:
            flash("Enter your name, a valid email and a password of at least 8 characters.", "error")
        elif User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
        else:
            user = User(name=name, email=email, password_hash=generate_password_hash(password))
            db.session.add(user); db.session.commit()
            session["user_id"] = user.id
            flash("Welcome to CalFit. Your account is ready.", "success")
            return redirect(url_for("dashboard"))
    return render_template("auth.html", mode="register")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form.get("email","").strip().lower()).first()
        if user and check_password_hash(user.password_hash, request.form.get("password","")):
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))
        flash("Email or password is incorrect.", "error")
    return render_template("auth.html", mode="login")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    logs = WorkoutLog.query.filter_by(user_id=user_id).order_by(WorkoutLog.completed_at.desc()).limit(5).all()
    total = WorkoutLog.query.filter_by(user_id=user_id).count()
    calories = db.session.query(db.func.sum(WorkoutLog.calories)).filter_by(user_id=user_id).scalar() or 0
    minutes = db.session.query(db.func.sum(WorkoutLog.duration)).filter_by(user_id=user_id).scalar() or 0
    return render_template("dashboard.html", logs=logs, total=total, calories=calories, minutes=minutes)

@app.route("/exercises")
@login_required
def exercises():
    q = request.args.get("q","").strip()
    muscle = request.args.get("muscle","")
    query = Exercise.query
    if q: query = query.filter(Exercise.name.ilike(f"%{q}%"))
    if muscle: query = query.filter(Exercise.primary_muscles.ilike(f"%{muscle}%"))
    return render_template("exercises.html", exercises=query.order_by(Exercise.is_preset.desc(), Exercise.name).all(), q=q, muscle=muscle)

@app.route("/exercise/<int:exercise_id>")
@login_required
def exercise_detail(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    if not exercise.is_preset and exercise.owner_id != session["user_id"]:
        abort(404)
    return render_template("exercise_detail.html", exercise=exercise)

@app.route("/exercise/add", methods=["POST"])
@login_required
def add_exercise():
    e = Exercise(name=request.form["name"], category=request.form.get("category","Full body"), level=request.form.get("level","Beginner"),
                 duration=int(request.form.get("duration",45)), reps=request.form.get("reps","12 reps"), calories=int(request.form.get("calories",5)),
                 equipment=request.form.get("equipment","None"), primary_muscles=request.form.get("primary_muscles","Full body"),
                 secondary_muscles=request.form.get("secondary_muscles",""), instructions=request.form.get("instructions",""),
                 benefits=request.form.get("benefits",""), recovery=request.form.get("recovery",""), video_url=request.form.get("video_url",""),
                 image_url=request.form.get("image_url",""), is_preset=False, owner_id=session["user_id"])
    db.session.add(e); db.session.commit()
    flash("Exercise added to your library.", "success")
    return redirect(url_for("exercises"))

@app.route("/exercise/<int:exercise_id>/delete", methods=["POST"])
@login_required
def delete_exercise(exercise_id):
    e = Exercise.query.get_or_404(exercise_id)
    if e.is_preset or e.owner_id != session["user_id"]:
        abort(403)
    db.session.delete(e); db.session.commit()
    flash("Your exercise was deleted.", "info")
    return redirect(url_for("exercises"))

@app.route("/generator", methods=["GET","POST"])
@login_required
def generator():
    result = None
    if request.method == "POST":
        total_minutes = max(1, min(120, int(request.form.get("minutes",20))))
        selected = request.form.getlist("muscles")
        level = request.form.get("level","All")
        # Candidate pool is filtered before the 0/1 knapsack DP.
        pool = Exercise.query.all()
        pool = [e for e in pool if (not selected or any(m.lower() in (e.primary_muscles + "," + e.secondary_muscles).lower() for m in selected))]
        if level != "All":
            allowed = {"Beginner": ["Beginner"], "Intermediate": ["Beginner","Intermediate"], "Advanced": ["Beginner","Intermediate","Advanced"]}[level]
            pool = [e for e in pool if e.level in allowed]
        capacity = total_minutes * 60
        n = len(pool)
        dp = [[0] * (capacity + 1) for _ in range(n + 1)]
        for i, e in enumerate(pool, 1):
            weight = max(1, e.duration + 15) # exercise time plus standard transition/rest allowance
            value = max(1, len(e.primary_muscles.split(",")) * 3 + (2 if e.level == level else 0) + 4)
            for t in range(capacity + 1):
                dp[i][t] = dp[i-1][t]
                if weight <= t:
                    dp[i][t] = max(dp[i][t], value + dp[i-1][t-weight])
        chosen, t = [], capacity
        for i in range(n, 0, -1):
            if dp[i][t] != dp[i-1][t]:
                e = pool[i-1]; chosen.append(e); t -= e.duration + 15
        chosen.reverse()
        result = {"items": chosen, "minutes": total_minutes, "used": sum(e.duration+15 for e in chosen), "calories": sum(e.calories for e in chosen)}
    return render_template("generator.html", result=result)

@app.route("/start-workout", methods=["POST"])
@login_required
def start_workout():
    ids = request.form.getlist("exercise_ids")
    found = {e.id: e for e in Exercise.query.filter(Exercise.id.in_(ids)).all()}
    ordered_exercises = [found[int(exercise_id)] for exercise_id in ids if int(exercise_id) in found]
    return render_template("workout.html", exercises=ordered_exercises)

@app.route("/log-workout", methods=["POST"])
@login_required
def log_workout():
    names = request.form.getlist("names")
    durations = request.form.getlist("durations")
    calories = request.form.getlist("calories")
    for name, duration, kcal in zip(names, durations, calories):
        db.session.add(WorkoutLog(user_id=session["user_id"], exercise_name=name, duration=int(duration), calories=int(kcal)))
    db.session.commit()
    flash("Workout saved to your history.", "success")
    return redirect(url_for("history"))

@app.route("/history")
@login_required
def history():
    logs = WorkoutLog.query.filter_by(user_id=session["user_id"]).order_by(WorkoutLog.completed_at.desc()).all()
    return render_template("history.html", logs=logs)

@app.route("/privacy")
def privacy(): return render_template("legal.html", page="privacy")
@app.route("/license")
def license_page(): return render_template("legal.html", page="license")
@app.route("/terms")
def terms(): return render_template("legal.html", page="terms")

@app.errorhandler(404)
def not_found(e): return render_template("error.html", code=404, title="Page not found", message="The page you are looking for may have moved or no longer exists."), 404
@app.errorhandler(403)
def forbidden(e): return render_template("error.html", code=403, title="Access denied", message="You do not have permission to view this page."), 403
@app.errorhandler(500)
def server_error(e):
    db.session.rollback()
    return render_template("error.html", code=500, title="Something went wrong", message="CalFit hit an unexpected error. Please try again."), 500

with app.app_context():
    db.create_all()
    seed()
    refresh_preset_exercises()

@app.route("/robots.txt")
def robots():
    from flask import send_from_directory
    return send_from_directory(BASE_DIR, "robots.txt")

if __name__ == "__main__":
    app.run(debug=True)
