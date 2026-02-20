from datetime import datetime, timedelta
from models import FoodLog, Report, db

def check_food_spike_alert(user_id, new_food_log):
    """
    Checks if a newly logged food could cause a glucose spike based on past data.
    Returns an alert message string if a spike is likely, else None.
    """
    if new_food_log.glycemic_impact != 'HIGH_RED':
        return None

    # Check user's historical PPBS (post-meal blood sugar)
    # If their average PPBS is generally high, or recent reports are high, alert them.
    recent_reports = Report.query.filter_by(user_id=user_id)\
        .order_by(Report.test_date.desc()).limit(5).all()
        
    if not recent_reports:
        return "You logged a high-impact food. Consider a 10-minute walk after eating to help control your blood sugar!"

    avg_recent_ppbs = sum(r.ppbs for r in recent_reports) / len(recent_reports)
    
    if avg_recent_ppbs > 150:
        return (f"Alert: Because your recent post-meal glucose averages {avg_recent_ppbs:.0f} mg/dL, "
                f"this {new_food_log.name} might cause a sharp spike. A quick 15-minute walk is highly recommended!")
    elif avg_recent_ppbs > 130:
        return (f"Heads up: This {new_food_log.name} is a high-impact food. "
                "Drinking water and taking a short walk can help minimize the glucose spike.")
        
    return None
