from datetime import datetime, timedelta
from models import FoodLog, Report, db

def generate_action_plan(user_id):
    """
    Analyzes user's food logs and reports to generate an actionable plan or recommendation.
    Returns a string or a list of recommendation strings.
    """
    # 1. Food Recommendations based on recent logs
    recent_foods = FoodLog.query.filter_by(user_id=user_id)\
        .order_by(FoodLog.timestamp.desc()).limit(20).all()
        
    recommendations = []
    
    high_impact_count = sum(1 for f in recent_foods if f.glycemic_impact == 'HIGH_RED')
    
    if len(recent_foods) > 0 and high_impact_count / len(recent_foods) > 0.3:
        recommendations.append(
            "Based on your recent meals, consider swapping some high-impact foods (like white bread and sweets) "
            "with lower GI alternatives like whole grains, nuts, and leafy greens."
        )

    # 2. Weekly Recap & Goal
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_reports = Report.query.filter(
        Report.user_id == user_id, 
        Report.test_date >= one_week_ago
    ).all()
    
    if len(weekly_reports) > 0:
        avg_fbs = sum(r.fbs for r in weekly_reports) / len(weekly_reports)
        if avg_fbs > 110:
            recommendations.append(
                f"Your average fasting blood sugar this week is {avg_fbs:.0f} mg/dL, which is slightly above target. "
                "Goal for next week: Try a 15-minute walk after dinner to help lower your morning levels."
            )
        elif avg_fbs < 100:
            recommendations.append(
                "Great job! Your fasting levels are well controlled this week. "
                "Goal: Maintain your current routine and hydration."
            )
    else:
        recommendations.append(
            "Weekly Goal: Try logging your health report at least three times this week so we can personalize your plan!"
        )
        
    if not recommendations:
         recommendations.append("Keep logging your meals and reports to get personalized action plans!")

    return recommendations
