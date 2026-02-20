import os
from apscheduler.schedulers.background import BackgroundScheduler
from models import db, User, FoodLog
from datetime import datetime, timedelta

def send_mock_sms(phone, message):
    """
    Simulates sending an SMS via Twilio/Vonage.
    """
    print(f"\n" + "="*50)
    print(f"[MOCK SMS TO -> {phone}]")
    print(f"MESSAGE: {message}")
    print("="*50 + "\n")

def check_for_post_meal_reminders(app):
    """
    Checks for meals logged exactly 2 hours ago and sends a reminder.
    """
    with app.app_context():
        now = datetime.utcnow()
        # Find meals logged between 1 hour 55 mins and 2 hours 5 mins ago
        # Since this runs every 10 minutes, we catch them within this window exactly once.
        start_time = now - timedelta(minutes=125)
        end_time = now - timedelta(minutes=115)
        
        recent_meals = FoodLog.query.filter(
            FoodLog.timestamp >= start_time,
            FoodLog.timestamp <= end_time
        ).all()
        
        for meal in recent_meals:
            user = User.query.get(meal.user_id)
            if user and user.phone:
                msg = f"Hi {user.name or 'there'}, it's been about 2 hours since you enjoyed your {meal.name}. It's a great time to check and log your post-meal blood sugar!"
                send_mock_sms(user.phone, msg)

def init_scheduler(app):
    """
    Initializes and starts the APScheduler.
    """
    scheduler = BackgroundScheduler(daemon=True)
    # Check every 10 minutes
    scheduler.add_job(func=check_for_post_meal_reminders, args=[app], trigger="interval", minutes=10)
    scheduler.start()
    return scheduler
