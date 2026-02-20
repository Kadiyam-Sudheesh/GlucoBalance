"""
GlucoBalance - Main orchestrator module.
Brings together all components to provide comprehensive health assistance.
"""
from typing import Optional
from models import AnalysisContext
from health_summary import generate_health_summary
from trend_analysis import generate_report_comparison
from progress_tracking import generate_weekly_progress_analysis, generate_monthly_progress_analysis
from visual_progress import generate_weekly_graph_explanation, generate_monthly_comparison_explanation
from action_plans import generate_weekly_action_plan, generate_monthly_improvement_plan
from motivation import generate_motivation_message, generate_reassurance_note, generate_medical_disclaimer
from suggestions import generate_suggestions, generate_future_scope_note


class GlucoBalance:
    """
    Main GlucoBalance assistant class.
    Provides comprehensive health assistance for diabetic and pre-diabetic patients.
    """
    
    def __init__(self):
        """Initialize GlucoBalance assistant."""
        self.name = "GlucoBalance"
        self.version = "1.0.0"
    
    def generate_comprehensive_analysis(self, context: AnalysisContext) -> str:
        """
        Generate comprehensive health analysis report.
        
        Args:
            context: AnalysisContext containing all relevant user data
            
        Returns:
            Complete formatted analysis report
        """
        report_sections = []
        
        # 1. Health Summary
        report_sections.append("=" * 70)
        report_sections.append("GLUCOBALANCE HEALTH ANALYSIS REPORT")
        report_sections.append("=" * 70)
        report_sections.append("")
        
        report_sections.append(generate_health_summary(
            context.user_profile,
            context.current_report,
            context.previous_report
        ))
        report_sections.append("")
        report_sections.append("")
        
        # 2. Report Comparison & Trend Analysis
        report_sections.append("=" * 70)
        report_sections.append(generate_report_comparison(
            context.current_report,
            context.previous_report,
            context.weekly_progress,
            context.monthly_summary
        ))
        report_sections.append("")
        report_sections.append("")
        
        # 3. Weekly Progress Analysis
        if context.weekly_progress:
            report_sections.append("=" * 70)
            report_sections.append(generate_weekly_progress_analysis(context.weekly_progress))
            report_sections.append("")
            report_sections.append("")
        
        # 4. Monthly Progress Analysis
        if context.monthly_summary:
            report_sections.append("=" * 70)
            report_sections.append(generate_monthly_progress_analysis(
                context.monthly_summary,
                None  # Could add previous month if available
            ))
            report_sections.append("")
            report_sections.append("")
        
        # 5. Visual Progress Explanation
        if context.weekly_progress:
            report_sections.append("=" * 70)
            report_sections.append(generate_weekly_graph_explanation(context.weekly_progress))
            report_sections.append("")
            report_sections.append("")
        
        if context.monthly_summary:
            report_sections.append("=" * 70)
            report_sections.append(generate_monthly_comparison_explanation(
                context.monthly_summary,
                None  # Could add previous month if available
            ))
            report_sections.append("")
            report_sections.append("")
        
        # 6. Weekly Action Plan
        report_sections.append("=" * 70)
        report_sections.append(generate_weekly_action_plan(
            context.user_profile,
            context.weekly_progress,
            context.current_report
        ))
        report_sections.append("")
        report_sections.append("")
        
        # 7. Monthly Improvement Plan
        report_sections.append("=" * 70)
        report_sections.append(generate_monthly_improvement_plan(
            context.user_profile,
            context.monthly_summary,
            context.current_report
        ))
        report_sections.append("")
        report_sections.append("")
        
        # 8. Motivation Message
        report_sections.append("=" * 70)
        report_sections.append(generate_motivation_message(
            context.weekly_progress,
            context.monthly_summary,
            context.current_report
        ))
        report_sections.append("")
        report_sections.append("")
        
        # 9. Suggestions & Next Steps
        report_sections.append("=" * 70)
        report_sections.append(generate_suggestions(
            context.user_profile,
            context.current_report,
            context.previous_report,
            context.weekly_progress,
            context.monthly_summary
        ))
        report_sections.append("")
        report_sections.append("")
        
        # 10. Reassurance Note
        report_sections.append("=" * 70)
        report_sections.append(generate_reassurance_note())
        report_sections.append("")
        report_sections.append("")
        
        # 11. Medical Disclaimer (MANDATORY)
        report_sections.append("=" * 70)
        report_sections.append(generate_medical_disclaimer())
        report_sections.append("")
        report_sections.append("")
        
        # 12. Future Scope (Optional)
        report_sections.append("=" * 70)
        report_sections.append(generate_future_scope_note())
        report_sections.append("")
        
        return "\n".join(report_sections)

    def generate_structured_analysis(self, context: AnalysisContext) -> dict:
        """
        Generate comprehensive health analysis report as a dictionary.
        
        Args:
            context: AnalysisContext containing all relevant user data
            
        Returns:
            Dictionary with section keys and formatted content values
        """
        sections = {}
        
        # 1. Health Summary
        sections['health_summary'] = generate_health_summary(
            context.user_profile,
            context.current_report,
            context.previous_report
        )
        
        # 2. Report Comparison & Trend Analysis
        sections['report_comparison'] = generate_report_comparison(
            context.current_report,
            context.previous_report,
            context.weekly_progress,
            context.monthly_summary
        )
        
        # 3. Weekly Progress Analysis
        if context.weekly_progress:
            sections['weekly_progress'] = generate_weekly_progress_analysis(context.weekly_progress)
        else:
            sections['weekly_progress'] = "Not enough data for weekly analysis yet. Continue tracking!"
        
        # 4. Monthly Progress Analysis
        if context.monthly_summary:
            sections['monthly_progress'] = generate_monthly_progress_analysis(
                context.monthly_summary,
                None
            )
        else:
            sections['monthly_progress'] = "Not enough data for monthly analysis yet."
        
        # 5. Visual Progress Explanation
        if context.weekly_progress:
            sections['visual_graph'] = generate_weekly_graph_explanation(context.weekly_progress)
        else:
            sections['visual_graph'] = "Graphs will appear here once you have more data points."

        if context.monthly_summary:
            sections['visual_graph'] += "\n\n" + generate_monthly_comparison_explanation(
                context.monthly_summary,
                None
            )
        
        # 6. Weekly Action Plan
        sections['weekly_action'] = generate_weekly_action_plan(
            context.user_profile,
            context.weekly_progress,
            context.current_report
        )
        
        # 7. Monthly Improvement Plan
        sections['monthly_improvement'] = generate_monthly_improvement_plan(
            context.user_profile,
            context.monthly_summary,
            context.current_report
        )
        
        # 8. Motivation Message
        sections['motivation'] = generate_motivation_message(
            context.weekly_progress,
            context.monthly_summary,
            context.current_report
        )
        
        # 9. Suggestions & Next Steps
        # Note: Suggestions generated as list, we'll join them
        # Actually generate_suggestions returns a formatted string if imported correctly?
        # Let's check imports. generate_suggestions returns string.
        sections['suggestions'] = generate_suggestions(
            context.user_profile,
            context.current_report,
            context.previous_report,
            context.weekly_progress,
            context.monthly_summary
        )
        
        # 10. Reassurance Note
        sections['reassurance'] = generate_reassurance_note()
        
        # 11. Medical Disclaimer
        sections['disclaimer'] = generate_medical_disclaimer()
        
        return sections
    
    def generate_quick_summary(self, context: AnalysisContext) -> str:
        """
        Generate a quick summary for dashboard or preview.
        
        Args:
            context: AnalysisContext with user data
            
        Returns:
            Short summary string
        """
        summary_parts = []
        
        summary_parts.append(f"**Quick Summary for {context.user_profile.name or 'You'}**\n")
        summary_parts.append(f"Test Date: {context.current_report.test_date.strftime('%B %d, %Y')}\n")
        summary_parts.append(f"FBS: {context.current_report.fbs:.1f} mg/dL | PPBS: {context.current_report.ppbs:.1f} mg/dL | HbA1c: {context.current_report.hba1c:.1f}%\n")
        
        if context.previous_report:
            comparison = generate_report_comparison(
                context.current_report,
                context.previous_report
            )
            summary_parts.append("\n**Trend:** ")
            # Extract trend info from comparison
            if context.current_report.fbs < context.previous_report.fbs:
                summary_parts.append("Improving")
            elif abs(context.current_report.fbs - context.previous_report.fbs) < 5:
                summary_parts.append("Stable")
            else:
                summary_parts.append("Needs Attention")
        
        return "\n".join(summary_parts)

    def get_health_summary_only(self, context: AnalysisContext) -> str:
        """
        Get only the health summary section.
        """
        return generate_health_summary(
            context.user_profile,
            context.current_report,
            context.previous_report
        )


# Example usage function
def create_example_context():
    """
    Create an example AnalysisContext for testing.
    """
    from models import UserProfile, HealthReport, WeeklyProgress, DailyReading, MonthlySummary, DiabetesType
    from datetime import date, timedelta
    
    # Create user profile
    user = UserProfile(
        age=45,
        diabetes_type=DiabetesType.TYPE_2,
        height_cm=170,
        weight_kg=75,
        name="John Doe"
    )
    
    # Create current report
    current_report = HealthReport(
        fbs=135.0,
        ppbs=185.0,
        hba1c=7.2,
        test_date=date.today()
    )
    
    # Create previous report
    previous_report = HealthReport(
        fbs=145.0,
        ppbs=195.0,
        hba1c=7.5,
        test_date=date.today() - timedelta(days=30)
    )
    
    # Create weekly progress
    week_start = date.today() - timedelta(days=7)
    daily_readings = []
    for i in range(7):
        daily_readings.append(DailyReading(
            date=week_start + timedelta(days=i),
            fasting_sugar=130 + (i * 2) - 3,  # Slight downward trend
            post_meal_sugar=180 + (i * 3) - 5,
            activity_minutes=25 + (i % 3) * 5,
            diet_adherence_score=7.0 + (i % 2) * 0.5
        ))
    
    weekly_progress = WeeklyProgress(
        week_start_date=week_start,
        daily_readings=daily_readings,
        average_fasting=132.0,
        average_post_meal=182.0,
        total_activity_minutes=175,
        average_diet_score=7.2
    )
    
    # Create monthly summary
    monthly_summary = MonthlySummary(
        month=date.today().month,
        year=date.today().year,
        weekly_progresses=[weekly_progress],
        health_reports=[current_report, previous_report]
    )
    
    # Create context
    context = AnalysisContext(
        user_profile=user,
        current_report=current_report,
        previous_report=previous_report,
        weekly_progress=weekly_progress,
        monthly_summary=monthly_summary
    )
    
    return context


if __name__ == "__main__":
    # Example usage
    assistant = GlucoBalance()
    context = create_example_context()
    
    print(assistant.generate_comprehensive_analysis(context))
