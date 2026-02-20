"""
Motivation & Emotional Support module for GlucoBalance.
Provides continuous motivation and reassurance.
"""
from typing import Optional, List
from models import UserProfile, ProgressStatus, HealthReport, WeeklyProgress, MonthlySummary
from progress_tracking import evaluate_weekly_progress, evaluate_monthly_progress
import random


MOTIVATION_MESSAGES = {
    ProgressStatus.IMPROVING_STEADILY: [
        "Excellent progress! Your consistent efforts are paying off. Keep up the great work!",
        "You're doing amazing! The improvements you're seeing are a result of your dedication.",
        "Outstanding! Your commitment to healthy habits is showing positive results.",
        "Fantastic work! You're building a strong foundation for long-term health.",
        "Wonderful progress! Every small step forward is a victory worth celebrating."
    ],
    ProgressStatus.STABLE_CONTROLLED: [
        "Great job maintaining consistency! Stability is a sign of good management.",
        "You're doing well! Keeping things stable is progress in itself.",
        "Excellent consistency! Your routine is working - keep it up!",
        "Good work! Stability shows you're managing your condition effectively.",
        "Well done! Consistency is key, and you're showing great discipline."
    ],
    ProgressStatus.NEEDS_ADJUSTMENT: [
        "Don't worry - every journey has ups and downs. Small adjustments can make a big difference.",
        "This is a learning opportunity. You're gathering valuable information about what works for you.",
        "Remember, managing diabetes is a journey. Today's challenges are tomorrow's successes.",
        "Stay positive! Small, consistent changes lead to meaningful improvements over time.",
        "You've got this! Every day is a chance to make progress, no matter how small."
    ]
}

REASSURANCE_MESSAGES = [
    "Diabetes is manageable, and you're taking the right steps to control it.",
    "Many people live healthy, active lives with diabetes - you can too!",
    "Early and consistent care brings strong results. You're on the right path.",
    "Remember, you're not alone in this journey. Every small improvement matters.",
    "Diabetes doesn't define you - your actions and determination do.",
    "With consistent care and healthy habits, diabetes can be well-controlled.",
    "You have the power to improve your health, one day at a time.",
    "Small, consistent steps lead to significant long-term improvements."
]

GENERAL_MOTIVATION = [
    "Managing diabetes is a journey, and you are moving in the right direction.",
    "Every positive choice you make is a step toward better health.",
    "Consistency beats perfection - keep showing up for yourself.",
    "Your health is worth the effort, and you're proving that every day.",
    "Small daily improvements compound into remarkable results over time.",
    "You're stronger than you think - look how far you've come!",
    "Progress isn't always linear, but your commitment is what matters most.",
    "Every day you manage your diabetes well is a victory worth celebrating."
]


def generate_motivation_message(
    weekly_progress: Optional[WeeklyProgress] = None,
    monthly_summary: Optional[MonthlySummary] = None,
    current_report: Optional[HealthReport] = None
) -> str:
    """
    Generate a personalized motivation message based on progress.
    
    Returns:
        Formatted motivation message string
    """
    parts = []
    parts.append("💪 **Motivation & Support**\n")
    
    # Determine status for personalized message
    status = None
    if weekly_progress:
        evaluation = evaluate_weekly_progress(weekly_progress)
        status = evaluation['status']
    elif monthly_summary:
        evaluation = evaluate_monthly_progress(monthly_summary)
        status = evaluation['status']
    
    # Generate personalized motivation
    if status:
        messages = MOTIVATION_MESSAGES.get(status, GENERAL_MOTIVATION)
        parts.append(f"{random.choice(messages)}\n")
    else:
        parts.append(f"{random.choice(GENERAL_MOTIVATION)}\n")
    
    parts.append("")
    
    # Add specific encouragement based on context
    if current_report:
        if current_report.fbs < 126 and current_report.ppbs < 200:
            parts.append("Your current readings show good control. Keep maintaining your healthy habits!")
        elif current_report.fbs < 150 and current_report.ppbs < 250:
            parts.append("You're making progress! Continue with consistency and you'll see further improvements.")
        else:
            parts.append("Remember, every small improvement counts. Focus on building one healthy habit at a time.")
        parts.append("")
    
    # General encouragement
    parts.append("**Remember:**")
    parts.append("- Consistency is more important than perfection")
    parts.append("- Small fluctuations are normal - focus on overall trends")
    parts.append("- Every day you make healthy choices is progress")
    parts.append("- You're building sustainable habits, not just following a diet")
    parts.append("- Patience and persistence are your greatest allies")
    
    return "\n".join(parts)


def generate_reassurance_note() -> str:
    """
    Generate reassurance about diabetes management.
    
    Returns:
        Formatted reassurance message string
    """
    parts = []
    parts.append("💙 **Reassurance & Awareness**\n")
    
    parts.append(f"{random.choice(REASSURANCE_MESSAGES)}\n")
    
    parts.append("**Key Points to Remember:**\n")
    parts.append("✅ Diabetes is manageable with proper care and lifestyle adjustments")
    parts.append("✅ Early and consistent management leads to excellent outcomes")
    parts.append("✅ Many people with diabetes live full, active, and healthy lives")
    parts.append("✅ Small, daily improvements compound into significant long-term benefits")
    parts.append("✅ You have the tools and knowledge to take control of your health")
    parts.append("✅ Setbacks are normal - what matters is getting back on track")
    parts.append("✅ Your health journey is unique - focus on your own progress")
    parts.append("✅ Every positive choice you make strengthens your foundation for better health")
    
    parts.append("")
    parts.append("**You're doing great!** Keep taking it one day at a time. 🌟")
    
    return "\n".join(parts)


def generate_medical_disclaimer() -> str:
    """
    Generate mandatory medical disclaimer.
    
    Returns:
        Formatted medical disclaimer string
    """
    parts = []
    parts.append("⚠️ **Important Medical Disclaimer**\n")
    parts.append("This platform is not a replacement for professional medical advice.")
    parts.append("For medication changes or medical concerns, please consult your doctor.")
    parts.append("")
    parts.append("**When to Consult Your Doctor:**")
    parts.append("- Before making any changes to your medication")
    parts.append("- If you experience unusual symptoms or concerns")
    parts.append("- For personalized medical advice tailored to your specific condition")
    parts.append("- For regular health check-ups and monitoring")
    parts.append("- If your sugar levels are consistently outside target ranges")
    
    return "\n".join(parts)
