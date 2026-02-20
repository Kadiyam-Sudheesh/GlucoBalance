"""
Action Plan generators for GlucoBalance.
Creates realistic and achievable weekly and monthly plans.
"""
from typing import Optional, List, Dict
from models import UserProfile, WeeklyProgress, MonthlySummary, HealthReport, ProgressStatus
from progress_tracking import evaluate_weekly_progress, evaluate_monthly_progress


def generate_weekly_action_plan(
    user_profile: UserProfile,
    weekly_progress: Optional[WeeklyProgress] = None,
    current_report: Optional[HealthReport] = None
) -> str:
    """
    Generate a realistic and achievable weekly action plan.
    
    Returns:
        Formatted weekly action plan string
    """
    parts = []
    parts.append("📋 **Weekly Action Plan**\n")
    parts.append("Here's your personalized plan for this week. Remember: small, consistent steps lead to big improvements!\n")
    
    # Determine plan intensity based on current status
    if current_report:
        if current_report.fbs > 150 or current_report.ppbs > 250:
            intensity = "moderate"
        elif current_report.fbs > 126 or current_report.ppbs > 200:
            intensity = "moderate"
        else:
            intensity = "maintenance"
    else:
        intensity = "moderate"
    
    # Physical Activity Plan
    parts.append("**1. Physical Activity** 🚶\n")
    if intensity == "moderate":
        parts.append("- **Goal:** 20-30 minutes of walking, 5 days this week")
        parts.append("- **Start small:** Begin with 10-15 minutes if you're new to exercise")
        parts.append("- **Best times:** Morning walk after breakfast or evening walk after dinner")
        parts.append("- **Tip:** Use a step counter or phone app to track your progress")
    else:
        parts.append("- **Goal:** 30-45 minutes of activity, 5-6 days this week")
        parts.append("- **Options:** Walking, light jogging, cycling, or any activity you enjoy")
        parts.append("- **Consistency:** Focus on daily routine rather than intensity")
        parts.append("- **Tip:** Break it into two shorter sessions if needed (15 min morning + 15 min evening)")
    parts.append("")
    
    # Diet Focus Plan
    parts.append("**2. Simple Diet Focus** 🍽️\n")
    if intensity == "moderate":
        parts.append("- **Portion Control:** Use smaller plates and fill half with vegetables")
        parts.append("- **Meal Timing:** Eat meals at regular times (breakfast, lunch, dinner)")
        parts.append("- **Carb Awareness:** Choose whole grains over refined carbs when possible")
        parts.append("- **Hydration:** Drink 6-8 glasses of water throughout the day")
        parts.append("- **Tip:** Don't skip meals - regular eating helps stabilize sugar levels")
    else:
        parts.append("- **Portion Control:** Maintain consistent portion sizes")
        parts.append("- **Meal Timing:** Keep regular meal schedule")
        parts.append("- **Balanced Meals:** Include protein, vegetables, and whole grains")
        parts.append("- **Snacking:** Choose healthy snacks (nuts, fruits) between meals if needed")
        parts.append("- **Tip:** Plan your meals ahead to avoid unhealthy choices")
    parts.append("")
    
    # Sleep and Stress Management
    parts.append("**3. Sleep & Stress Management** 😴\n")
    parts.append("- **Sleep Goal:** 7-8 hours of quality sleep each night")
    parts.append("- **Sleep Routine:** Go to bed and wake up at the same time daily")
    parts.append("- **Stress Reduction:** Practice 5-10 minutes of deep breathing or meditation daily")
    parts.append("- **Relaxation:** Engage in activities you enjoy (reading, music, hobbies)")
    parts.append("- **Tip:** Stress affects sugar levels - managing stress is as important as diet")
    parts.append("")
    
    # Monitoring Plan
    parts.append("**4. Daily Monitoring** 📝\n")
    parts.append("- **Track:** Log your fasting sugar each morning")
    parts.append("- **Optional:** Log post-meal sugar 2 hours after main meals (2-3 times/week)")
    parts.append("- **Activity Log:** Note your daily activity minutes")
    parts.append("- **Diet Score:** Rate your diet adherence (1-10) each day")
    parts.append("- **Tip:** Use the app to log readings - tracking helps identify patterns")
    parts.append("")
    
    # Weekly Goals Summary
    parts.append("**This Week's Focus:**\n")
    parts.append("✅ Stay consistent with meal timing")
    parts.append("✅ Complete 5 days of physical activity")
    parts.append("✅ Get adequate sleep (7-8 hours)")
    parts.append("✅ Log your readings daily")
    parts.append("")
    
    parts.append("**Remember:** This plan is flexible. If you miss a day, don't worry - just get back on track the next day. Progress, not perfection! 💪")
    
    return "\n".join(parts)


def generate_monthly_improvement_plan(
    user_profile: UserProfile,
    monthly_summary: Optional[MonthlySummary] = None,
    current_report: Optional[HealthReport] = None
) -> str:
    """
    Generate a structured monthly improvement plan.
    
    Returns:
        Formatted monthly improvement plan string
    """
    parts = []
    parts.append("🗓️ **Monthly Improvement Plan**\n")
    parts.append("A structured approach to gradual sugar control and healthy habit building.\n")
    
    # Determine focus areas based on current status
    if current_report:
        focus_areas = []
        if current_report.fbs > 126:
            focus_areas.append("fasting_sugar")
        if current_report.ppbs > 200:
            focus_areas.append("post_meal_sugar")
        if current_report.hba1c > 7.0:
            focus_areas.append("long_term_control")
    else:
        focus_areas = ["general_improvement"]
    
    # Week-by-week breakdown
    parts.append("**Month Structure (Week-by-Week):**\n")
    
    parts.append("**Week 1: Foundation Building** 🏗️\n")
    parts.append("- Establish regular meal timing (3 meals at consistent times)")
    parts.append("- Start with 15-20 minutes of daily walking")
    parts.append("- Begin logging daily fasting sugar readings")
    parts.append("- Focus on adequate sleep (7-8 hours)")
    parts.append("- **Goal:** Build consistency in basic habits\n")
    
    parts.append("**Week 2: Habit Strengthening** 💪\n")
    parts.append("- Increase activity to 25-30 minutes, 5 days/week")
    parts.append("- Focus on portion control at meals")
    parts.append("- Continue daily sugar logging")
    parts.append("- Add stress management practice (5-10 min daily)")
    parts.append("- **Goal:** Strengthen Week 1 habits and add new ones\n")
    
    parts.append("**Week 3: Optimization** ⚡\n")
    parts.append("- Maintain 30+ minutes of activity, 5-6 days/week")
    parts.append("- Refine meal choices (more vegetables, whole grains)")
    parts.append("- Track post-meal sugar 2-3 times/week")
    parts.append("- Optimize sleep schedule for quality rest")
    parts.append("- **Goal:** Fine-tune your routine based on what's working\n")
    
    parts.append("**Week 4: Consistency & Review** 📊\n")
    parts.append("- Maintain all established habits")
    parts.append("- Review your progress and patterns")
    parts.append("- Prepare for next month's health check")
    parts.append("- Celebrate small wins and improvements")
    parts.append("- **Goal:** Solidify habits and prepare for continued progress\n")
    
    parts.append("")
    
    # Monthly Focus Areas
    parts.append("**Monthly Focus Areas:**\n")
    
    if "fasting_sugar" in focus_areas or "general_improvement" in focus_areas:
        parts.append("**1. Gradual Sugar Control** 📉\n")
        parts.append("- Focus on consistent meal timing to stabilize fasting sugar")
        parts.append("- Monitor fasting sugar daily to identify patterns")
        parts.append("- Small improvements (5-10 mg/dL) are meaningful progress")
        parts.append("- **Target:** Reduce fasting sugar by 10-20 mg/dL over the month\n")
    
    if "post_meal_sugar" in focus_areas or "general_improvement" in focus_areas:
        parts.append("**2. Meal-Time Management** 🍽️\n")
        parts.append("- Control portion sizes, especially carbohydrates")
        parts.append("- Include protein and vegetables in every meal")
        parts.append("- Monitor post-meal sugar to understand meal impact")
        parts.append("- **Target:** Keep post-meal sugar below 180 mg/dL\n")
    
    parts.append("**3. Habit Consistency** 🔄\n")
    parts.append("- Build daily routines that become automatic")
    parts.append("- Focus on doing small things consistently rather than perfect execution")
    parts.append("- Track your habits to see progress over time")
    parts.append("- **Target:** Maintain 80%+ adherence to daily habits\n")
    
    parts.append("**4. Mental & Emotional Well-being** 🧘\n")
    parts.append("- Manage stress through relaxation techniques")
    parts.append("- Get adequate sleep for better sugar control")
    parts.append("- Stay positive and patient with the process")
    parts.append("- **Target:** Reduce stress and improve sleep quality\n")
    
    parts.append("**5. Regular Health Monitoring** 📋\n")
    parts.append("- Log daily readings consistently")
    parts.append("- Review weekly progress to identify patterns")
    parts.append("- Prepare for monthly health check-up")
    parts.append("- **Target:** Complete daily logging 90%+ of days\n")
    
    parts.append("")
    
    # Success Metrics
    parts.append("**Monthly Success Indicators:**\n")
    parts.append("✅ Consistent daily habit tracking")
    parts.append("✅ Regular physical activity (5+ days/week)")
    parts.append("✅ Stable or improving sugar readings")
    parts.append("✅ Better sleep and stress management")
    parts.append("✅ Feeling more confident about managing diabetes")
    
    parts.append("")
    
    # Encouragement
    parts.append("**Remember:**\n")
    parts.append("- Progress is gradual - small daily improvements add up over time")
    parts.append("- Consistency matters more than perfection")
    parts.append("- Every positive choice counts, even if you have setbacks")
    parts.append("- You're building a sustainable lifestyle, not just following a temporary plan")
    parts.append("- Managing diabetes is a journey, and you're moving in the right direction! 🌟")
    
    return "\n".join(parts)
