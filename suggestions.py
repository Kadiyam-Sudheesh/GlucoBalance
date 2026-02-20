"""
Suggestions & Next Steps module for GlucoBalance.
Provides personalized lifestyle suggestions based on trends.
"""
from typing import Optional, List, Dict
from models import UserProfile, HealthReport, WeeklyProgress, MonthlySummary
from trend_analysis import analyze_weekly_trends, compare_reports


def generate_suggestions(
    user_profile: UserProfile,
    current_report: HealthReport,
    previous_report: Optional[HealthReport] = None,
    weekly_progress: Optional[WeeklyProgress] = None,
    monthly_summary: Optional[MonthlySummary] = None
) -> str:
    """
    Generate 3-5 personalized lifestyle suggestions based on trends.
    
    Returns:
        Formatted suggestions string
    """
    parts = []
    parts.append("💡 **Personalized Suggestions & Next Steps**\n")
    parts.append("Based on your health data and trends, here are some actionable suggestions:\n")
    
    suggestions = []
    
    # Analyze trends to determine focus areas
    if previous_report:
        comparison = compare_reports(current_report, previous_report)
        
        # FBS suggestions
        if comparison['fbs']['trend'] == 'needs_attention':
            suggestions.append({
                'category': 'Diet',
                'title': 'Focus on Breakfast & Evening Meals',
                'details': [
                    "Your fasting sugar suggests we focus on evening meal timing and composition.",
                    "Try having dinner 2-3 hours before bedtime.",
                    "Include protein and vegetables in your evening meal.",
                    "Avoid heavy carbohydrates late in the day."
                ]
            })
        
        # PPBS suggestions
        if comparison['ppbs']['trend'] == 'needs_attention':
            suggestions.append({
                'category': 'Diet',
                'title': 'Improve Meal-Time Sugar Control',
                'details': [
                    "Your post-meal sugar indicates we should focus on meal composition.",
                    "Start meals with vegetables or protein before carbohydrates.",
                    "Control portion sizes, especially rice, bread, and other carbs.",
                    "Consider taking a 10-15 minute walk after meals.",
                    "Space meals evenly throughout the day (every 4-5 hours)."
                ]
            })
        
        # HbA1c suggestions
        if comparison['hba1c']['trend'] == 'needs_attention':
            suggestions.append({
                'category': 'Lifestyle',
                'title': 'Build Consistent Daily Habits',
                'details': [
                    "Your long-term average suggests we need more consistency.",
                    "Focus on building daily routines that become automatic.",
                    "Small, consistent actions have bigger impact than occasional perfect days.",
                    "Track your habits daily to build awareness.",
                    "Celebrate small wins to maintain motivation."
                ]
            })
    
    # Weekly progress suggestions
    if weekly_progress:
        trends = analyze_weekly_trends(weekly_progress)
        
        # Activity suggestions
        if 'activity' in trends:
            activity = trends['activity']
            if activity['average_daily'] < 20:
                suggestions.append({
                    'category': 'Physical Activity',
                    'title': 'Increase Daily Movement',
                    'details': [
                        f"Your current activity is {activity['average_daily']:.0f} minutes/day.",
                        "Aim for at least 30 minutes of moderate activity daily.",
                        "Start with 10-minute walks and gradually increase.",
                        "Break activity into smaller sessions if needed (e.g., 15 min morning + 15 min evening).",
                        "Find activities you enjoy - walking, dancing, cycling, or gardening."
                    ]
                })
        
        # Diet adherence suggestions
        if 'diet' in trends:
            diet = trends['diet']
            if diet['status'] == 'needs_improvement':
                suggestions.append({
                    'category': 'Diet',
                    'title': 'Improve Diet Consistency',
                    'details': [
                        f"Your diet adherence score is {diet['average_score']:.1f}/10.",
                        "Focus on one meal at a time - start with breakfast consistency.",
                        "Plan meals ahead to avoid unhealthy choices.",
                        "Keep healthy snacks available (nuts, fruits, vegetables).",
                        "Don't skip meals - regular eating helps stabilize sugar levels."
                    ]
                })
    
    # General suggestions based on current values
    if not suggestions or len(suggestions) < 3:
        if current_report.fbs > 130:
            suggestions.append({
                'category': 'Diet',
                'title': 'Optimize Meal Timing',
                'details': [
                    "Eat meals at regular times each day.",
                    "Don't skip breakfast - it helps stabilize fasting sugar.",
                    "Have your last meal 2-3 hours before bedtime.",
                    "Consider smaller, more frequent meals if needed."
                ]
            })
        
        if current_report.ppbs > 200:
            suggestions.append({
                'category': 'Diet',
                'title': 'Manage Carbohydrate Intake',
                'details': [
                    "Choose whole grains over refined carbohydrates.",
                    "Control portion sizes - use smaller plates.",
                    "Fill half your plate with vegetables.",
                    "Include protein in every meal to slow sugar absorption."
                ]
            })
    
    # Always include activity suggestion if not already present
    activity_present = any(s['category'] == 'Physical Activity' for s in suggestions)
    if not activity_present:
        suggestions.append({
            'category': 'Physical Activity',
            'title': 'Regular Physical Activity',
            'details': [
                "Aim for 30 minutes of moderate activity most days of the week.",
                "Walking is excellent - start with what feels comfortable.",
                "Activity helps your body use insulin more effectively.",
                "Even 10-15 minutes of activity after meals helps control post-meal sugar."
            ]
        })
    
    # Always include sleep/stress suggestion
    suggestions.append({
        'category': 'Sleep & Stress',
        'title': 'Prioritize Sleep and Stress Management',
        'details': [
            "Aim for 7-8 hours of quality sleep each night.",
            "Poor sleep affects sugar control - make it a priority.",
            "Practice stress-reduction techniques (deep breathing, meditation, hobbies).",
            "Manage stress through regular physical activity and relaxation.",
            "Create a calming bedtime routine for better sleep quality."
        ]
    })
    
    # Limit to 5 suggestions
    suggestions = suggestions[:5]
    
    # Format suggestions
    for i, suggestion in enumerate(suggestions, 1):
        category_emoji = {
            'Diet': '🍽️',
            'Physical Activity': '🚶',
            'Lifestyle': '🔄',
            'Sleep & Stress': '😴'
        }
        
        emoji = category_emoji.get(suggestion['category'], '💡')
        parts.append(f"**{i}. {emoji} {suggestion['title']}** ({suggestion['category']})\n")
        
        for detail in suggestion['details']:
            parts.append(f"- {detail}")
        
        parts.append("")
    
    # Next steps summary
    parts.append("**Your Next Steps:**\n")
    parts.append("1. Choose 1-2 suggestions that feel most achievable for you")
    parts.append("2. Focus on implementing them consistently for the next week")
    parts.append("3. Track your progress and adjust as needed")
    parts.append("4. Add more suggestions gradually as habits become automatic")
    parts.append("5. Remember: small, consistent changes lead to lasting improvements")
    
    parts.append("")
    parts.append("**Remember:** These are general suggestions. Always consult your doctor before making significant changes to your diet or exercise routine.")
    
    return "\n".join(parts)


def generate_future_scope_note() -> str:
    """
    Generate note about future enhancements.
    
    Returns:
        Formatted future scope message string
    """
    parts = []
    parts.append("🔮 **Future Enhancements**\n")
    parts.append("We're continuously improving GlucoBalance to better serve you. Future enhancements may include:\n")
    
    parts.append("**Coming Soon:**")
    parts.append("🤖 **AI-Based Sugar Trend Prediction** - Forecast future sugar levels based on your patterns")
    parts.append("⚠️ **Early Risk Alerts** - Get notified about potential issues before they become problems")
    parts.append("👨‍⚕️ **Doctor Dashboards** - Share your progress with healthcare providers for monitored care")
    parts.append("📊 **Advanced Analytics** - Deeper insights into long-term patterns and correlations")
    parts.append("🎯 **Personalized Goal Setting** - Custom goals tailored to your specific needs and progress")
    parts.append("📱 **Smart Reminders** - Intelligent notifications for medication, meals, and activity")
    
    parts.append("")
    parts.append("We're committed to supporting your health journey with the best tools and insights available!")
    
    return "\n".join(parts)
