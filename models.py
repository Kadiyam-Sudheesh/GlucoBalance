"""
Data models for GlucoBalance health assistant.
"""
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

class DiabetesType(Enum):
    TYPE_1 = "Type 1"
    TYPE_2 = "Type 2"
    PRE_DIABETIC = "Pre-diabetic"
    GESTATIONAL = "Gestational"


class ProgressStatus(Enum):
    IMPROVING_STEADILY = "Improving steadily"
    STABLE_CONTROLLED = "Stable and controlled"
    NEEDS_ADJUSTMENT = "Needs lifestyle adjustment"


# --- SQLAlchemy Models for Persistence ---

class User(db.Model):
    """User database model."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True) # Optional if email is primary, but app treats them similarly
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Profile fields stored directly on User for simplicity
    age = db.Column(db.Integer, nullable=True)
    diabetes_type = db.Column(db.String(50), default="TYPE_2")
    height_cm = db.Column(db.Float, nullable=True)
    weight_kg = db.Column(db.Float, nullable=True)

    # Gamification & Accessibility Fields
    current_streak_days = db.Column(db.Integer, default=0)
    best_streak_days = db.Column(db.Integer, default=0)
    last_log_date = db.Column(db.Date, nullable=True)
    theme_preference = db.Column(db.String(20), default="light") # light, dark, high-contrast
    caregiver_token = db.Column(db.String(100), unique=True, nullable=True) # For sharing dashboard

    # Relationships
    reports = db.relationship('Report', backref='user', lazy=True)

    def to_profile_dict(self):
        """Convert to dictionary for profile."""
        return {
            "name": self.name,
            "age": self.age,
            "diabetes_type": self.diabetes_type,
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg
        }

    def get_estimated_hba1c(self):
        """Calculate estimated HbA1c from last 90 days of reports."""
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        recent_reports = Report.query.filter(
            Report.user_id == self.id,
            Report.test_date >= ninety_days_ago
        ).all()

        if not recent_reports:
            return None

        total_bg = 0
        count = 0
        for report in recent_reports:
            # Use both FBS and PPBS if available for a better average
            if report.fbs:
                total_bg += report.fbs
                count += 1
            if report.ppbs:
                total_bg += report.ppbs
                count += 1
        
        if count == 0:
            return None
            
        avg_bg = total_bg / count
        # Formula: (Avg BG + 46.7) / 28.7
        hba1c = (avg_bg + 46.7) / 28.7
        return round(hba1c, 1)

class Report(db.Model):
    """Health Report database model."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    fbs = db.Column(db.Float, nullable=False)
    ppbs = db.Column(db.Float, nullable=False)
    hba1c = db.Column(db.Float, nullable=False)
    test_date = db.Column(db.Date, nullable=False, default=date.today)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "fbs": self.fbs,
            "ppbs": self.ppbs,
            "hba1c": self.hba1c,
            "test_date": self.test_date.isoformat(),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "notes": self.notes
        }

class Medication(db.Model):
    """Medication information."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    logs = db.relationship('MedicationLog', backref='medication', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "dosage": self.dosage,
            "frequency": self.frequency,
            "notes": self.notes
        }

class MedicationLog(db.Model):
    """Log of taken medications."""
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    taken_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="TAKEN")  # TAKEN, SKIPPED, MISSED

    def to_dict(self):
        return {
            "id": self.id,
            "medication_id": self.medication_id,
            "taken_at": self.taken_at.isoformat(),
            "status": self.status
        }

class EmergencyContact(db.Model):
    """Emergency contact information."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone
        }

class HypoEvent(db.Model):
    """Log of hypoglycemia events."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="STARTED") # STARTED, RESOLVED
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "notes": self.notes
        }


class FoodLog(db.Model):
    """Log of food and meals."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(20), nullable=False)  # Breakfast, Lunch, Dinner, Snack
    glycemic_impact = db.Column(db.String(20), nullable=False)  # LOW_GREEN, MEDIUM_YELLOW, HIGH_RED
    portion = db.Column(db.String(20), nullable=False)  # Small, Medium, Large
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "glycemic_impact": self.glycemic_impact,
            "portion": self.portion,
            "timestamp": self.timestamp.isoformat(),
            "notes": self.notes
        }

class HydrationLog(db.Model):
    """Log of daily water intake (glasses)."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    glasses_count = db.Column(db.Integer, default=0)
    date = db.Column(db.Date, nullable=False, default=date.today)

    def to_dict(self):
        return {
            "id": self.id,
            "glasses_count": self.glasses_count,
            "date": self.date.isoformat()
        }

class LifestyleLog(db.Model):
    """Log of sleep and stress levels."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sleep_hours = db.Column(db.Float, nullable=True)
    stress_level = db.Column(db.Integer, nullable=True) # 1-10 scale
    date = db.Column(db.Date, nullable=False, default=date.today)

    def to_dict(self):
        return {
            "id": self.id,
            "sleep_hours": self.sleep_hours,
            "stress_level": self.stress_level,
            "date": self.date.isoformat()
        }

class CGMReading(db.Model):
    """Imported Continuous Glucose Monitor readings."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    glucose_value = db.Column(db.Float, nullable=False)
    trend_arrow = db.Column(db.String(20), nullable=True) # Optional Dexcom/Libre trend arrow
    
    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "glucose_value": self.glucose_value,
            "trend_arrow": self.trend_arrow
        }

# --- Dataclasses for Analysis/API Logic (Keep as is) ---

@dataclass
class UserProfile:
    """User profile information."""
    age: int
    diabetes_type: DiabetesType
    height_cm: float
    weight_kg: float
    name: Optional[str] = None


@dataclass
class HealthReport:
    """Health report with blood sugar measurements."""
    fbs: float  # Fasting Blood Sugar (mg/dL)
    ppbs: float  # Post-Prandial Blood Sugar (mg/dL)
    hba1c: float  # HbA1c (%)
    test_date: date
    notes: Optional[str] = None


@dataclass
class DailyReading:
    """Daily sugar reading entry."""
    date: date
    fasting_sugar: Optional[float] = None
    post_meal_sugar: Optional[float] = None
    activity_minutes: Optional[int] = None
    diet_adherence_score: Optional[float] = None  # 0-10 scale
    notes: Optional[str] = None


@dataclass
class WeeklyProgress:
    """Weekly progress data."""
    week_start_date: date
    daily_readings: List[DailyReading]
    average_fasting: Optional[float] = None
    average_post_meal: Optional[float] = None
    total_activity_minutes: Optional[int] = None
    average_diet_score: Optional[float] = None


@dataclass
class MonthlySummary:
    """Monthly summary data."""
    month: int
    year: int
    weekly_progresses: List[WeeklyProgress]
    health_reports: List[HealthReport]
    average_fbs: Optional[float] = None
    average_ppbs: Optional[float] = None
    average_hba1c: Optional[float] = None


@dataclass
class AnalysisContext:
    """Context for analysis containing all relevant data."""
    user_profile: UserProfile
    current_report: HealthReport
    previous_report: Optional[HealthReport]
    weekly_progress: Optional[WeeklyProgress]
    monthly_summary: Optional[MonthlySummary]
    historical_reports: List[HealthReport] = None
    historical_weekly_data: List[WeeklyProgress] = None
