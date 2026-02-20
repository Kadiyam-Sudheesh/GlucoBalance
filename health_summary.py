"""
AI Health Summary module for GlucoBalance.
Provides simple, easy-to-understand health condition summaries.
"""
from typing import Optional, Dict
from models import HealthReport, UserProfile, DiabetesType


def interpret_sugar_level(fbs: float, ppbs: float, hba1c: float) -> Dict[str, str]:
    """
    Interpret sugar levels and return simple explanations.
    
    Returns:
        Dictionary with interpretations for each metric
    """
    interpretations = {}
    
    # Fasting Blood Sugar interpretation
    if fbs < 100:
        interpretations['fbs'] = "normal"
        interpretations['fbs_message'] = "Your fasting sugar is in the normal range."
    elif fbs < 126:
        interpretations['fbs'] = "pre-diabetic"
        interpretations['fbs_message'] = "Your fasting sugar is slightly elevated (pre-diabetic range)."
    else:
        interpretations['fbs'] = "diabetic"
        interpretations['fbs_message'] = "Your fasting sugar is elevated and needs attention."
    
    # Post-Prandial Blood Sugar interpretation
    if ppbs < 140:
        interpretations['ppbs'] = "normal"
        interpretations['ppbs_message'] = "Your post-meal sugar is well controlled."
    elif ppbs < 200:
        interpretations['ppbs'] = "elevated"
        interpretations['ppbs_message'] = "Your post-meal sugar is slightly elevated."
    else:
        interpretations['ppbs'] = "high"
        interpretations['ppbs_message'] = "Your post-meal sugar is high and needs attention."
    
    # HbA1c interpretation
    if hba1c < 5.7:
        interpretations['hba1c'] = "normal"
        interpretations['hba1c_message'] = "Your average sugar control over the past 3 months is excellent."
    elif hba1c < 6.5:
        interpretations['hba1c'] = "pre-diabetic"
        interpretations['hba1c_message'] = "Your average sugar control shows room for improvement."
    else:
        interpretations['hba1c'] = "diabetic"
        interpretations['hba1c_message'] = "Your average sugar control needs consistent management."
    
    return interpretations


def generate_health_summary(
    user_profile: UserProfile,
    current_report: HealthReport,
    previous_report: Optional[HealthReport] = None
) -> str:
    """
    Generate a simple, easy-to-understand health summary.
    
    Args:
        user_profile: User's profile information
        current_report: Current health report
        previous_report: Previous health report for comparison
        
    Returns:
        Formatted health summary string
    """
    interpretations = interpret_sugar_level(
        current_report.fbs,
        current_report.ppbs,
        current_report.hba1c
    )
    
    summary_parts = []
    
    # Opening statement
    name = user_profile.name if user_profile.name else "You"
    summary_parts.append(f"**Health Summary for {name}**\n")
    summary_parts.append(f"Based on your test results from {current_report.test_date.strftime('%B %d, %Y')}:\n")
    
    # Highlight improvements first if previous report exists
    if previous_report:
        improvements = []
        
        if current_report.fbs < previous_report.fbs:
            improvement = previous_report.fbs - current_report.fbs
            improvements.append(f"Your fasting sugar has reduced by {improvement:.1f} mg/dL compared to last month.")
        
        if current_report.ppbs < previous_report.ppbs:
            improvement = previous_report.ppbs - current_report.ppbs
            improvements.append(f"Your post-meal sugar has improved by {improvement:.1f} mg/dL.")
        
        if current_report.hba1c < previous_report.hba1c:
            improvement = previous_report.hba1c - current_report.hba1c
            improvements.append(f"Your HbA1c has decreased by {improvement:.1f}%, showing better long-term control.")
        
        if improvements:
            summary_parts.append("\n✅ **Positive Changes:**")
            for improvement in improvements:
                summary_parts.append(f"- {improvement}")
            summary_parts.append("")
    
    # Current status
    summary_parts.append("**Current Status:**\n")
    
    # FBS
    summary_parts.append(f"• **Fasting Blood Sugar (FBS):** {current_report.fbs:.1f} mg/dL")
    summary_parts.append(f"  {interpretations['fbs_message']}")
    
    # PPBS
    summary_parts.append(f"\n• **Post-Meal Sugar (PPBS):** {current_report.ppbs:.1f} mg/dL")
    summary_parts.append(f"  {interpretations['ppbs_message']}")
    
    # HbA1c
    summary_parts.append(f"\n• **HbA1c (3-month average):** {current_report.hba1c:.1f}%")
    summary_parts.append(f"  {interpretations['hba1c_message']}")
    
    # Overall assessment
    summary_parts.append("\n**What This Means:**")
    
    # Determine overall status
    normal_count = sum([
        interpretations['fbs'] == 'normal',
        interpretations['ppbs'] == 'normal',
        interpretations['hba1c'] == 'normal'
    ])
    
    if normal_count == 3:
        summary_parts.append("Your sugar levels are well controlled. Keep maintaining your healthy habits!")
    elif normal_count >= 1:
        summary_parts.append("You're making progress! Some of your readings are improving. Continue with consistency.")
    else:
        summary_parts.append("Your sugar levels need attention, but remember - diabetes can be controlled and improved with consistency. Focus on building healthy habits one day at a time.")
    
    return "\n".join(summary_parts)
