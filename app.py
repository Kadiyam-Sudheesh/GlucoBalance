"""
GlucoBalance Web App
Clean, professional UI for the GlucoBalance digital health assistant.
"""

from datetime import date, datetime, timedelta
import os
import json

from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response

from api import GlucoBalanceAPI
from models import db, User, Report, Medication, MedicationLog, EmergencyContact, HypoEvent, FoodLog, HydrationLog, LifestyleLog
from services.alerts import check_food_spike_alert
from services.action_plans import generate_action_plan
from deep_translator import GoogleTranslator
from xhtml2pdf import pisa
import io
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "glucobalance-default-key")
    
    # Database Configuration
    # Use SQLite. db file will be created in the instance folder or current folder.
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'glucocare.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    api = GlucoBalanceAPI()

    # Create tables within app context
    with app.app_context():
        db.create_all()

    # Initialize background scheduler for reminders once per process
    from services.sms_reminders import init_scheduler
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        init_scheduler(app)

    # Add custom Jinja2 filter for strftime
    def strftime_filter(fmt: str) -> str:
        """Format the current datetime using strftime."""
        return datetime.now().strftime(fmt)

    app.jinja_env.filters["strftime"] = strftime_filter
    
    # Session Configuration
    app.permanent_session_lifetime = timedelta(days=365) # Stay logged in for 1 year

    @app.before_request
    def require_login():
        """Global route protection."""
        # endpoints that do NOT require login
        public_endpoints = ['login', 'signup', 'static', 'index']
        
        if request.endpoint not in public_endpoints and "user_id" not in session:
            return redirect(url_for("login"))

    @app.route("/", methods=["GET"])
    def index():
        """Landing page."""
        return render_template("index.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Login page and handler."""
        if request.method == "POST":
            email = request.form.get("email", "").strip()
            email = request.form.get("email", "").strip()
            phone = request.form.get("phone", "").strip()
            country_code = request.form.get("country_code", "+91").strip()
            password = request.form.get("password", "").strip()
            
            # Validate at least one login credential is provided
            if not email and not phone:
                flash("Please enter either email address or phone number", "error")
                return redirect(url_for("login"))
            
            if not password:
                flash("Please enter your password", "error")
                return redirect(url_for("login"))
            
            # Determine login identifier (prefer email, fallback to phone)
            login_identifier = None
            if email:
                login_identifier = email
            elif phone:
                # Clean phone number (remove spaces, dashes)
                clean_phone = phone.replace(" ", "").replace("-", "")
                
                # If user typed a full international number (starts with +), ignore the dropdown
                if clean_phone.startswith("+"):
                     login_identifier = clean_phone
                else:
                     login_identifier = f"{country_code}{clean_phone}"

            # Check if user exists and password matches
            user = None
            if email:
                user = User.query.filter_by(email=email).first()
            elif phone:
                # Try finding user with the constructed phone number
                user = User.query.filter_by(phone=login_identifier).first()
                
                # Fallback: If not found, try without country code prefix just in case (though unlikely with current signup logic)
                if not user and not clean_phone.startswith("+"):
                    # Maybe they registered without country code? (Legacy data)
                    user = User.query.filter_by(phone=clean_phone).first()
            
            is_valid = False
            if user:
                if user.password.startswith('scrypt:') or user.password.startswith('pbkdf2:'):
                    is_valid = check_password_hash(user.password, password)
                elif user.password == password:
                    # Seamless upgrade of legacy plaintext passwords
                    user.password = generate_password_hash(password)
                    db.session.commit()
                    is_valid = True
            
            if is_valid:
                # Login successful - set session
                session.permanent = True
                session["user_id"] = user.id
                session["user_email"] = user.email
                session["user_name"] = user.name
                
                # Update last login timestamp
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                flash(f"Welcome back, {user.name or 'User'}!", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid credentials. Please try again.", "error")
                return redirect(url_for("login"))
        
        return render_template("login.html")

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        """Sign up page and handler."""
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            phone = request.form.get("phone", "").strip()
            country_code = request.form.get("country_code", "+91").strip()
            password = request.form.get("password", "").strip()
            confirm_password = request.form.get("confirm_password", "").strip()
            terms = request.form.get("terms")
            
            # Validate all required fields
            if not all([name, email, phone, country_code, password, confirm_password, terms]):
                flash("All fields are mandatory", "error")
                return redirect(url_for("signup"))
            
            if password != confirm_password:
                flash("Passwords do not match", "error")
                return redirect(url_for("signup"))
            
            if len(password) < 6:
                flash("Password must be at least 6 characters", "error")
                return redirect(url_for("signup"))
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("Email already registered. Please login.", "error")
                return redirect(url_for("signup"))
            
            # Create new user
            hashed_pw = generate_password_hash(password)
            new_user = User(
                name=name,
                email=email,
                phone=f"{country_code}{phone}",
                password=hashed_pw
            )
            db.session.add(new_user)
            db.session.commit()
            
            session["user_id"] = new_user.id
            session["user_email"] = new_user.email
            session["user_name"] = new_user.name
            flash("Account created successfully! Welcome to GlucoBalance.", "success")
            return redirect(url_for("analyze"))
        
        return render_template("signup.html")

    @app.route("/logout", methods=["GET"])
    def logout():
        """Logout user."""
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("index"))

    @app.route("/profile", methods=["GET", "POST"])
    def profile():
        """User profile page."""
        if "user_id" not in session:
            return redirect(url_for("login"))
        
        user = User.query.get(session["user_id"])
        
        if request.method == "POST":
            user.name = request.form.get("name")
            user.age = request.form.get("age")
            user.diabetes_type = request.form.get("diabetes_type")
            user.height_cm = request.form.get("height_cm")
            user.weight_kg = request.form.get("weight_kg")
            
            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for("profile"))
            
        return render_template("profile.html", user=user)

    @app.route("/delete_report/<int:report_id>", methods=["POST"])
    def delete_report(report_id):
        """Delete a specific report."""
        if "user_id" not in session:
            flash("Please login to delete reports", "error")
            return redirect(url_for("login"))
            
        report = Report.query.get_or_404(report_id)
        
        # Verify ownership
        if report.user_id != session["user_id"]:
            flash("You do not have permission to delete this report", "error")
            return redirect(url_for("dashboard"))
            
        try:
            db.session.delete(report)
            db.session.commit()
            flash("Report deleted successfully", "success")
        except Exception as e:
            db.session.rollback()
            flash("Error deleting report", "error")
            
        return redirect(url_for("dashboard"))

    @app.route("/edit_report/<int:report_id>", methods=["GET"])
    def edit_report(report_id):
        """Load report data into analyze form for editing."""
        if "user_id" not in session:
            flash("Please login to edit reports", "info")
            return redirect(url_for("login"))
            
        report = Report.query.get_or_404(report_id)
        
        # Verify ownership
        if report.user_id != session["user_id"]:
            flash("You do not have permission to edit this report", "error")
            return redirect(url_for("dashboard"))
            
        user = User.query.get(session["user_id"])
        
        # Render analyze template with report data pre-filled
        return render_template(
            "analyze.html",
            today=date.today().isoformat(),
            profile=user.to_profile_dict(),
            editing_report=report.to_dict() # Pass specific report to edit
        )

    @app.route("/analyze", methods=["GET", "POST"])
    def analyze():
        """Handle form submission and render full report."""
        if "user_id" not in session:
            flash("Please login to access the analysis tool", "info")
            return redirect(url_for("login"))
        
        user_id = session.get("user_id")
        user = User.query.get(user_id)
        
        # Retrieve existing reports
        existing_reports_objs = Report.query.filter_by(user_id=user_id).order_by(Report.test_date).all()
        # Convert to dicts for logic
        existing_reports = [r.to_dict() for r in existing_reports_objs]
        sorted_reports = existing_reports # Already sorted by query
        last_report = sorted_reports[-1] if sorted_reports else None

        if request.method == "GET":
            today_str = date.today().isoformat()
            return render_template(
                "analyze.html",
                today=today_str,
                profile=user.to_profile_dict(),
                last_report=last_report
            )
        
        # --- User profile ---
        name = request.form.get("name") or user.name
        age = int(request.form.get("age") or user.age or 0)
        diabetes_type = request.form.get("diabetes_type") or user.diabetes_type or "TYPE_2"
        height_cm = float(request.form.get("height_cm") or user.height_cm or 0)
        weight_kg = float(request.form.get("weight_kg") or user.weight_kg or 0)
        
        # Check if we are updating an existing report ID (hidden field)
        report_id = request.form.get("report_id")

        # Update profile in DB
        user.name = name
        user.age = age
        user.diabetes_type = diabetes_type
        user.height_cm = height_cm
        user.weight_kg = weight_kg
        db.session.commit()

        # --- Current report ---
        fbs = float(request.form.get("fbs") or 0)
        ppbs = float(request.form.get("ppbs") or 0)
        hba1c = float(request.form.get("hba1c") or 0)
        test_date_str = request.form.get("test_date") or date.today().isoformat()
        
        # Prepare data for API
        data = {
            "user": user.to_profile_dict(),
            "current_report": {
                "fbs": fbs,
                "ppbs": ppbs,
                "hba1c": hba1c,
                "test_date": test_date_str,
            },
        }

        # --- Previous report (Automated) ---
        previous_report = None
        if sorted_reports:
             current_test_date = date.fromisoformat(test_date_str)
             prior_reports = [r for r in sorted_reports if date.fromisoformat(r["test_date"]) < current_test_date]
             
             if prior_reports:
                 previous_report = prior_reports[-1]
             # logic for "same day" or if strictly latest is current
             elif sorted_reports and date.fromisoformat(sorted_reports[-1]["test_date"]) == current_test_date and len(sorted_reports) > 1:
                   # If we are editing the latest report, previous is the one before it
                   if report_id and int(report_id) == sorted_reports[-1]["id"]:
                        previous_report = sorted_reports[-2]
                   else:
                        previous_report = sorted_reports[-2]
             elif sorted_reports and not report_id:
                   # New report, previous is the last one
                   previous_report = sorted_reports[-1]


        if previous_report:
             data["previous_report"] = {
                "fbs": previous_report["fbs"],
                "ppbs": previous_report["ppbs"],
                "hba1c": previous_report["hba1c"],
                "test_date": previous_report["test_date"],
            }
        
        # --- Weekly Progress (Automated) ---
        current_test_date = date.fromisoformat(test_date_str)
        week_start = current_test_date - timedelta(days=6)
        weekly_readings = []
        
        for r in sorted_reports:
            # exclude current report if we are editing it (to avoid double counting if logic was complex, but mapped by date is fine)
            if report_id and int(report_id) == r["id"]:
                continue
                
            r_date = date.fromisoformat(r["test_date"])
            if week_start <= r_date <= current_test_date:
                weekly_readings.append({
                    "date": r_date,
                    "fasting_sugar": r["fbs"],
                    "post_meal_sugar": r["ppbs"],
                })
        
        # Add current (newly submitted) values to weekly progress for the analysis
        weekly_readings.append({
             "date": current_test_date,
             "fasting_sugar": fbs,
             "post_meal_sugar": ppbs,
        })
        
        # Deduplicate by date (latest wins)
        weekly_readings_map = {item['date']: item for item in weekly_readings}
        unique_weekly_readings = list(weekly_readings_map.values())

        if unique_weekly_readings:
            data["weekly_progress"] = {
                "week_start_date": week_start.isoformat(),
                "daily_readings": unique_weekly_readings
            }


        # Use API to generate the comprehensive textual report
        structured_analysis = api.analyze_structured_from_dict(data)
        full_report_text = api.analyze_from_dict(data) # Keep full text for the bottom section

        # Save report to user's history
        target_report = None
        
        if report_id:
            # Update specific report being edited
            target_report = Report.query.get(report_id)
            if target_report and target_report.user_id == user.id:
                target_report.fbs = fbs
                target_report.ppbs = ppbs
                target_report.hba1c = hba1c
                target_report.test_date = date.fromisoformat(test_date_str)
                target_report.timestamp = datetime.utcnow()
                flash("Report updated successfully", "success")
        else:
            # Check if report for this date already exists for this user to avoid duplicates
            existing_report_obj = Report.query.filter_by(user_id=user.id, test_date=date.fromisoformat(test_date_str)).first()
            
            if existing_report_obj:
                # Update existing for that date
                existing_report_obj.fbs = fbs
                existing_report_obj.ppbs = ppbs
                existing_report_obj.hba1c = hba1c
                existing_report_obj.timestamp = datetime.utcnow()
                flash("Existing report for this date updated", "info")
            else:
                new_report = Report(
                    user_id=user.id,
                    fbs=fbs,
                    ppbs=ppbs,
                    hba1c=hba1c,
                    test_date=date.fromisoformat(test_date_str)
                )
                db.session.add(new_report)
                flash("New report generated successfully", "success")
        
        db.session.commit()

        return render_template(
            "report.html",
            full_report=full_report_text,
            structured_analysis=structured_analysis,
            health_summary_heading="Health Summary",
            report_comparison_heading="Report Comparison",
            weekly_progress_heading="Weekly Progress Analysis",
            monthly_progress_heading="Monthly Progress Analysis",
            visual_graph_heading="Visual Graph Explanation",
            weekly_action_heading="Weekly Action Plan",
            monthly_improvement_heading="Monthly Improvement Plan",
            motivation_heading="Motivation Message",
            reassurance_heading="Reassurance Note",
            disclaimer_heading="Medical Disclaimer",
        )

    @app.route("/health_summary", methods=["GET"])
    def health_summary():
        """Show the detailed health summary."""
        if "user_id" not in session:
            flash("Please login to access your health summary", "info")
            return redirect(url_for("login"))
        
        user = User.query.get(session["user_id"])
        
        # Get latest report
        latest_report = Report.query.filter_by(user_id=user.id).order_by(Report.test_date.desc()).first()
        
        if not latest_report:
            flash("No reports found. Please submit a health report first.", "info")
            return redirect(url_for("analyze"))
            
        # Get previous report
        previous_report = Report.query.filter_by(user_id=user.id).filter(Report.test_date < latest_report.test_date).order_by(Report.test_date.desc()).first()
        
        data = {
            "user": user.to_profile_dict(),
            "current_report": latest_report.to_dict(),
        }
        
        if previous_report:
            data["previous_report"] = previous_report.to_dict()
            
        summary_text = api.get_health_summary(data)
        
        # Parse MD to HTML or just pass text? 
        # The user requested 'display this text', implying the formatting. 
        # We'll render it in a template that preserves white-space or renders markdown.
        # Since it uses **bold** and bullets, better to render markdown.
        # But we don't have a markdown filter installed in Flask by default.
        # We can simulate basic formatting in logic or template.
        # For now, let's pass it as text and use a simple markdown parser or just pre-formatted text.
        # Actually, let's look at `report.html` to see how it renders `full_report_text`.
        # It probably uses `| safe` or a markdown filter. 
        
        return render_template("summary.html", summary=summary_text)



    @app.route("/medications", methods=["GET", "POST"])
    def medications():
        """Medication tracking page."""
        if "user_id" not in session:
            flash("Please login to access medications", "info")
            return redirect(url_for("login"))

        user_id = session.get("user_id")

        if request.method == "POST":
            # Add new medication
            name = request.form.get("name")
            dosage = request.form.get("dosage")
            frequency = request.form.get("frequency")
            notes = request.form.get("notes")

            if not name or not dosage:
                flash("Medication name and dosage are required", "error")
            else:
                new_med = Medication(
                    user_id=user_id,
                    name=name,
                    dosage=dosage,
                    frequency=frequency,
                    notes=notes
                )
                db.session.add(new_med)
                db.session.commit()
                flash("Medication added successfully", "success")
            
            return redirect(url_for("medications"))

        # Get user's medications
        meds = Medication.query.filter_by(user_id=user_id).all()
        
        # Get today's logs
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_logs = MedicationLog.query.join(Medication).filter(
            Medication.user_id == user_id,
            MedicationLog.taken_at >= today_start
        ).all()
        
        logged_med_ids = [log.medication_id for log in today_logs]

        return render_template(
            "medications.html",
            medications=meds,
            logged_med_ids=logged_med_ids
        )

    @app.route("/medications/edit/<int:med_id>", methods=["GET", "POST"])
    def edit_medication(med_id):
        """Edit an existing medication."""
        if "user_id" not in session:
            flash("Please login", "info")
            return redirect(url_for("login"))
            
        med = Medication.query.get_or_404(med_id)
        if med.user_id != session["user_id"]:
            flash("Unauthorized access", "error")
            return redirect(url_for("medications"))
            
        if request.method == "POST":
            med.name = request.form.get("name")
            med.dosage = request.form.get("dosage")
            med.frequency = request.form.get("frequency")
            med.notes = request.form.get("notes")
            
            db.session.commit()
            flash(f"Updated {med.name} successfully", "success")
            return redirect(url_for("medications"))
            
        return render_template("edit_medication.html", medication=med)

    @app.route("/medications/log/<int:med_id>", methods=["POST"])
    def log_medication(med_id):
        """Log a medication as taken."""
        if "user_id" not in session:
             return {"error": "Unauthorized"}, 401
        
        med = Medication.query.get_or_404(med_id)
        if med.user_id != session["user_id"]:
            return {"error": "Unauthorized"}, 403

        # Check if already logged today? (Optional, but let's allow multiple for now if needed, 
        # though UI might toggle. For safety, maybe just log it.)
        
        log = MedicationLog(
            medication_id=med.id,
            status="TAKEN"
        )
        db.session.add(log)
        db.session.commit()
        
        flash(f"Logged {med.name}", "success")
        return redirect(url_for("medications"))

    @app.route("/medications/delete/<int:med_id>", methods=["POST"])
    def delete_medication(med_id):
        """Delete a medication."""
        if "user_id" not in session:
            flash("Please login", "error")
            return redirect(url_for("login"))
            
        med = Medication.query.get_or_404(med_id)
        if med.user_id != session["user_id"]:
            flash("Unauthorized", "error")
            return redirect(url_for("medications"))
            
        db.session.delete(med)
        db.session.commit()
        flash("Medication removed", "success")
        return redirect(url_for("medications"))

    @app.route("/translate", methods=["POST"])
    def translate_text():
        """Translate text to target language with chunking for long texts."""
        data = request.get_json()
        text = data.get("text")
        target_lang = data.get("target_lang", "en")
        
        if not text:
            return {"error": "No text provided"}, 400
            
        try:
            translator = GoogleTranslator(source='auto', target=target_lang)
            
            # Helper function to split text into chunks
            def chunk_text(text, limit=4500):
                chunks = []
                current_chunk = ""
                
                # Split by paragraphs first to preserve structure
                paragraphs = text.split('\n\n')
                
                for para in paragraphs:
                    if len(current_chunk) + len(para) < limit:
                        current_chunk += para + "\n\n"
                    else:
                        # If current chunk has content, add it
                        if current_chunk:
                            chunks.append(current_chunk)
                            current_chunk = ""
                        
                        # If the paragraph itself is too long (rare but possible), split by sentences
                        if len(para) > limit:
                            sentences = para.split('. ')
                            for sentence in sentences:
                                if len(current_chunk) + len(sentence) < limit:
                                    current_chunk += sentence + ". "
                                else:
                                    if current_chunk:
                                        chunks.append(current_chunk)
                                    current_chunk = sentence + ". "
                            if current_chunk:
                                current_chunk += "\n\n" # Add paragraph break after processing long para
                        else:
                            current_chunk = para + "\n\n"
                
                if current_chunk:
                    chunks.append(current_chunk)
                return chunks

            # Translate chunks
            translated_parts = []
            chunks = chunk_text(text)
            
            for chunk in chunks:
                if chunk.strip():
                    translated_parts.append(translator.translate(chunk))
                else:
                    translated_parts.append(chunk) # Preserve empty lines if any logic creates them
            
            return {"translated_text": "".join(translated_parts)}

        except Exception as e:
            print(f"Translation Error: {e}") # Log to console
            return {"error": str(e)}, 500

    @app.route("/emergency", methods=["GET"])
    def emergency():
        """Emergency mode page."""
        if "user_id" not in session:
            flash("Please login to access emergency features", "error")
            return redirect(url_for("login"))
        
        user_id = session.get("user_id")
        contacts = EmergencyContact.query.filter_by(user_id=user_id).all()
        
        return render_template("emergency.html", contacts=contacts)

    @app.route("/emergency/start", methods=["POST"])
    def emergency_start():
        """Log start of hypo event."""
        if "user_id" not in session:
            return {"error": "Unauthorized"}, 401
            
        event = HypoEvent(
            user_id=session["user_id"],
            status="STARTED",
            notes="User triggered emergency mode"
        )
        db.session.add(event)
        db.session.commit()
        return {"status": "success", "event_id": event.id}

    @app.route("/emergency/resolve", methods=["POST"])
    def emergency_resolve():
        """Log resolution of hypo event."""
        if "user_id" not in session:
            return {"error": "Unauthorized"}, 401
            
        data = request.json
        event_id = data.get("event_id")
        
        if event_id:
            event = HypoEvent.query.get(event_id)
            if event and event.user_id == session["user_id"]:
                event.status = "RESOLVED"
                event.notes += " - Resolved by user"
                db.session.commit()
        else:
            # If no ID (e.g. user refreshed), just log a generic resolution or ignore
            pass
            
        flash("Glad you're feeling better! Event logged.", "success")
        return {"status": "success"}

    @app.route("/settings/contacts", methods=["GET", "POST"])
    def manage_contacts():
        """Manage emergency contacts."""
        if "user_id" not in session:
            return redirect(url_for("login"))
            
        user_id = session.get("user_id")
        
        if request.method == "POST":
            name = request.form.get("name")
            phone = request.form.get("phone")
            
            if name and phone:
                new_contact = EmergencyContact(user_id=user_id, name=name, phone=phone)
                db.session.add(new_contact)
                db.session.commit()
                flash("Contact added", "success")
            else:
                flash("Name and phone required", "error")
                
            return redirect(url_for("manage_contacts"))
            
        contacts = EmergencyContact.query.filter_by(user_id=user_id).all()
        return render_template("contacts.html", contacts=contacts)

    @app.route("/settings/contacts/delete/<int:contact_id>", methods=["POST"])
    def delete_contact(contact_id):
        """Delete emergency contact."""
        if "user_id" not in session:
            return redirect(url_for("login"))
            
        contact = EmergencyContact.query.get_or_404(contact_id)
        if contact.user_id != session["user_id"]:
            return "Unauthorized", 403
            
        db.session.delete(contact)
        db.session.commit()
        flash("Contact removed", "success")
        return redirect(url_for("manage_contacts"))

    @app.route("/settings/contacts/edit/<int:contact_id>", methods=["GET", "POST"])
    def edit_contact(contact_id):
        """Edit emergency contact."""
        if "user_id" not in session:
            return redirect(url_for("login"))
            
        contact = EmergencyContact.query.get_or_404(contact_id)
        if contact.user_id != session["user_id"]:
            return "Unauthorized", 403
            
        if request.method == "POST":
            contact.name = request.form.get("name")
            contact.phone = request.form.get("phone")
            
            if contact.name and contact.phone:
                db.session.commit()
                flash("Contact updated", "success")
                return redirect(url_for("manage_contacts"))
            else:
                flash("Name and phone required", "error")
                
        return render_template("edit_contact.html", contact=contact)

    @app.route("/food", methods=["GET"])
    def food_log():
        """Food logging page."""
        if "user_id" not in session:
            flash("Please login to access food log", "error")
            return redirect(url_for("login"))
        
        user_id = session.get("user_id")
        
        # Get logs for today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_logs = FoodLog.query.filter(
            FoodLog.user_id == user_id,
            FoodLog.timestamp >= today_start
        ).order_by(FoodLog.timestamp.desc()).all()
        
        # Get recent history (last 50 items)
        history_logs = FoodLog.query.filter(
            FoodLog.user_id == user_id
        ).order_by(FoodLog.timestamp.desc()).limit(50).all()

        return render_template("food_log.html", today_logs=today_logs, history_logs=history_logs)

    @app.route("/hydration/add", methods=["POST"])
    def add_hydration():
        """Increment daily water glass count."""
        if "user_id" not in session:
            return {"error": "Unauthorized"}, 401

        user_id = session.get("user_id")
        today = date.today()
        
        log = HydrationLog.query.filter_by(user_id=user_id, date=today).first()
        
        if log:
            log.glasses_count += 1
        else:
            log = HydrationLog(user_id=user_id, glasses_count=1, date=today)
            db.session.add(log)
            
        db.session.commit()
        
        return {"status": "success", "glasses": log.glasses_count}

    @app.route("/lifestyle/add", methods=["POST"])
    def add_lifestyle():
        """Log daily sleep and stress."""
        if "user_id" not in session:
            return redirect(url_for("login"))
            
        user_id = session.get("user_id")
        sleep_hours = request.form.get("sleep_hours")
        stress_level = request.form.get("stress_level")
        
        if sleep_hours and stress_level:
            log = LifestyleLog(
                user_id=user_id,
                sleep_hours=float(sleep_hours),
                stress_level=int(stress_level),
                date=date.today()
            )
            db.session.add(log)
            db.session.commit()
            flash("Lifestyle details logged successfully", "success")
        else:
            flash("Please provide both sleep and stress values", "error")
            
        return redirect(url_for("dashboard"))

    @app.route("/dashboard")
    def dashboard():
        if "user_id" not in session:
            return redirect(url_for("login"))

        user = User.query.get(session["user_id"])
        # Calculate recent reports... (existing logic for charts)
        reports = Report.query.filter_by(user_id=user.id).order_by(Report.test_date.desc()).all()
        
        # Calculate Estimated HbA1c
        hba1c_estimate = user.get_estimated_hba1c()

        # Update Streak if needed
        today = date.today()
        # Simple logic: If they view the dashboard today, count as activity or require explicit log
        # To make it simple, we just pass what models have.

        # Fetch today's hydration
        hydration_log = HydrationLog.query.filter_by(user_id=user.id, date=today).first()
        water_glasses = hydration_log.glasses_count if hydration_log else 0

        # Fetch recent lifestyle logs for the chart
        lifestyle_logs = LifestyleLog.query.filter_by(user_id=user.id).order_by(LifestyleLog.date.desc()).limit(14).all()
        lifestyle_logs.reverse() # chronological
        
        lifestyle_dates = [l.date.strftime("%Y-%m-%d") for l in lifestyle_logs]
        sleep_data = [l.sleep_hours for l in lifestyle_logs]
        stress_data = [l.stress_level for l in lifestyle_logs]

        dates = [r.test_date.strftime("%Y-%m-%d") for r in reports]
        fbs_data = [r.fbs for r in reports]
        ppbs_data = [r.ppbs for r in reports]
        hba1c_data = [r.hba1c for r in reports]
        
        # Action Plans & Recommendations
        action_plan_items = generate_action_plan(user.id)
        
        # If user has no reports, pass empty data to avoid JS errors
        if not reports:
             flash("Welcome! Add your first health report to see your dashboard.", "info")

        return render_template(
            "dashboard.html", 
            user=user, 
            reports=reports, 
            dates=dates[::-1], 
            fbs_values=fbs_data[::-1], 
            ppbs_values=ppbs_data[::-1],
            hba1c_values=hba1c_data[::-1],
            hba1c_estimate=hba1c_estimate,
            water_glasses=water_glasses,
            lifestyle_dates=lifestyle_dates,
            sleep_data=sleep_data,
            stress_data=stress_data,
            action_plan_items=action_plan_items
        )
    @app.route("/food/add", methods=["POST"])
    def add_food():
        """Log a new meal."""
        if "user_id" not in session:
            return redirect(url_for("login"))
            
        user_id = session.get("user_id")
        name = request.form.get("name")
        category = request.form.get("category")
        glycemic_impact = request.form.get("glycemic_impact")
        portion = request.form.get("portion")
        notes = request.form.get("notes")
        
        if name and category and glycemic_impact:
            log = FoodLog(
                user_id=user_id,
                name=name,
                category=category,
                glycemic_impact=glycemic_impact,
                portion=portion,
                notes=notes
            )
            db.session.add(log)
            db.session.commit()
            
            # Trigger predictive alert if necessary
            alert_message = check_food_spike_alert(user_id, log)
            if alert_message:
                flash(alert_message, "warning")
            else:
                flash("Meal logged successfully", "success")
        else:
            flash("Please fill in all required fields", "error")
            
        return redirect(url_for("food_log"))

    @app.route("/export/doctor_report", methods=["GET"])
    def export_doctor_report():
        """Generate and download a comprehensive PDF report for doctors."""
        if "user_id" not in session:
            flash("Please login to download reports", "info")
            return redirect(url_for("login"))
            
        user_id = session.get("user_id")
        user = User.query.get(user_id)
        
        # Get data for last 30 days
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        # Reports
        reports_objs = Report.query.filter(
            Report.user_id == user_id,
            Report.test_date >= start_date
        ).order_by(Report.test_date.desc()).all()
        
        reports = [r.to_dict() for r in reports_objs]
        
        # Medications
        meds = Medication.query.filter_by(user_id=user_id).all()
        med_list = []
        for med in meds:
            # Count logs in last 30 days
            logs_count = MedicationLog.query.filter(
                MedicationLog.medication_id == med.id,
                MedicationLog.taken_at >= datetime.combine(start_date, datetime.min.time())
            ).count()
            
            med_dict = med.to_dict()
            med_dict['adherence_count'] = logs_count
            med_list.append(med_dict)
            
        # Averages
        avg_fbs = 0
        avg_ppbs = 0
        latest_hba1c = 0
        if reports:
            avg_fbs = sum(r['fbs'] for r in reports) / len(reports)
            avg_ppbs = sum(r['ppbs'] for r in reports) / len(reports)
            latest_hba1c = reports[0]['hba1c']
            
        # Render HTML
        rendered_html = render_template(
            "pdf_report.html",
            user=user.to_profile_dict(),
            reports=reports,
            medications=med_list,
            generated_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            today=date.today().isoformat(),
            avg_fbs=int(avg_fbs),
            avg_ppbs=int(avg_ppbs),
            latest_hba1c=latest_hba1c
        )
        
        # Convert to PDF
        pdf_output = io.BytesIO()
        pisa_status = pisa.CreatePDF(
            io.BytesIO(rendered_html.encode("UTF-8")),
            dest=pdf_output
        )
        
        if pisa_status.err:
            return "Error generating PDF", 500
            
        # Create response
        pdf_output.seek(0)
        response = make_response(pdf_output.read())
        response.headers['Content-Type'] = 'application/pdf'
        safe_name = "".join([c for c in user.name if c.isalnum() or c in (' ', '-', '_')]).strip().replace(' ', '_')
        response.headers['Content-Disposition'] = f'attachment; filename="GlucoBalance_Report_{safe_name}_{date.today()}.pdf"'
        
        return response

    return app


if __name__ == "__main__":
    application = create_app()
    # Debug can be toggled as needed; host 0.0.0.0 for broader access if required.
    application.run(debug=True, host='0.0.0.0')
