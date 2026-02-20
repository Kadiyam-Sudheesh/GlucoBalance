"""
Weekly & Monthly Progress Tracking module for GlucoBalance.
Tracks and evaluates progress over time.
"""
from typing import Optional, Dict
from models import WeeklyProgress, MonthlySummary, ProgressStatus, HealthReport
from trend_analysis import analyze_weekly_trends, analyze_monthly_trends


def evaluate_weekly_progress(weekly_progress: WeeklyProgress) -> Dict[str, any]:
    """
    Evaluate weekly progress and classify it.
    
    Returns:
        Dictionary with progress evaluation
    """
    if not weekly_progress.daily_readings:
        return {
            'status': ProgressStatus.NEEDS_ADJUSTMENT,
            'message': 'No data available for this week. Please start tracking your daily readings.',
            'score': 0
        }
    
    trends = analyze_weekly_trends(weekly_progress)
    
    if trends.get('status') == 'insufficient_data':
        return {
            'status': ProgressStatus.NEEDS_ADJUSTMENT,
            'message': 'Insufficient data for evaluation. Try to log readings more consistently.',
            'score': 0
        }
    
    # Calculate progress score
    score = 0
    positive_indicators = 0
    total_indicators = 0
    
    # Check fasting sugar trend
    if 'fasting' in trends:
        total_indicators += 1
        if trends['fasting']['trend'] == 'improving':
            score += 3
            positive_indicators += 1
        elif trends['fasting']['trend'] == 'stable':
            score += 2
            positive_indicators += 1
    
    # Check post-meal sugar trend
    if 'post_meal' in trends:
        total_indicators += 1
        if trends['post_meal']['trend'] == 'improving':
            score += 3
            positive_indicators += 1
        elif trends['post_meal']['trend'] == 'stable':
            score += 2
            positive_indicators += 1
    
    # Check activity
    if 'activity' in trends:
        total_indicators += 1
        activity = trends['activity']
        if activity['average_daily'] >= 30:
            score += 2
            positive_indicators += 1
        elif activity['average_daily'] >= 15:
            score += 1
    
    # Check diet adherence
    if 'diet' in trends:
        total_indicators += 1
        diet = trends['diet']
        if diet['status'] == 'excellent':
            score += 3
            positive_indicators += 1
        elif diet['status'] == 'good':
            score += 2
            positive_indicators += 1
    
    # Determine status
    if total_indicators == 0:
        status = ProgressStatus.NEEDS_ADJUSTMENT
        message = "Start tracking your daily readings to see progress."
    elif positive_indicators == total_indicators and score >= (total_indicators * 2.5):
        status = ProgressStatus.IMPROVING_STEADILY
        message = "Excellent progress this week! You're building great habits."
    elif positive_indicators >= total_indicators * 0.6:
        status = ProgressStatus.STABLE_CONTROLLED
        message = "Good consistency this week. Keep maintaining your routine."
    else:
        status = ProgressStatus.NEEDS_ADJUSTMENT
        message = "This week shows areas for improvement. Small adjustments can make a big difference."
    
    return {
        'status': status,
        'message': message,
        'score': score,
        'positive_indicators': positive_indicators,
        'total_indicators': total_indicators,
        'trends': trends
    }


def evaluate_monthly_progress(
    monthly_summary: MonthlySummary,
    previous_month: Optional[MonthlySummary] = None
) -> Dict[str, any]:
    """
    Evaluate monthly progress and classify it.
    
    Returns:
        Dictionary with monthly progress evaluation
    """
    if not monthly_summary.health_reports:
        return {
            'status': ProgressStatus.NEEDS_ADJUSTMENT,
            'message': 'No health reports available for this month.',
            'score': 0
        }
    
    # Get latest report
    latest_report = max(monthly_summary.health_reports, key=lambda x: x.test_date)
    
    # Compare with previous month if available
    if previous_month and previous_month.health_reports:
        previous_latest = max(previous_month.health_reports, key=lambda x: x.test_date)
        comparison = analyze_monthly_trends(monthly_summary, previous_month)
        
        month_over_month = comparison.get('month_over_month', {})
        
        # Calculate progress score
        score = 0
        improvements = 0
        
        if 'fbs' in month_over_month:
            if month_over_month['fbs']['trend'] == 'improving':
                score += 3
                improvements += 1
            elif month_over_month['fbs']['trend'] == 'stable':
                score += 1
        
        if 'ppbs' in month_over_month:
            if month_over_month['ppbs']['trend'] == 'improving':
                score += 3
                improvements += 1
            elif month_over_month['ppbs']['trend'] == 'stable':
                score += 1
        
        if 'hba1c' in month_over_month:
            if month_over_month['hba1c']['trend'] == 'improving':
                score += 4  # HbA1c is most important
                improvements += 1
            elif month_over_month['hba1c']['trend'] == 'stable':
                score += 2
        
        # Determine status
        if improvements >= 2:
            status = ProgressStatus.IMPROVING_STEADILY
            message = "Great monthly progress! Your consistent efforts are paying off."
        elif improvements >= 1 or score >= 5:
            status = ProgressStatus.STABLE_CONTROLLED
            message = "Stable progress this month. Keep up the consistency."
        else:
            status = ProgressStatus.NEEDS_ADJUSTMENT
            message = "This month shows areas for improvement. Focus on building consistent daily habits."
        
        return {
            'status': status,
            'message': message,
            'score': score,
            'improvements': improvements,
            'comparison': month_over_month
        }
    
    # No previous month - evaluate based on current values
    score = 0
    
    if latest_report.fbs < 126:
        score += 2
    if latest_report.ppbs < 200:
        score += 2
    if latest_report.hba1c < 7.0:
        score += 3
    
    if score >= 6:
        status = ProgressStatus.STABLE_CONTROLLED
        message = "Your current readings show good control. Maintain consistency."
    elif score >= 3:
        status = ProgressStatus.NEEDS_ADJUSTMENT
        message = "Your readings indicate room for improvement. Focus on lifestyle adjustments."
    else:
        status = ProgressStatus.NEEDS_ADJUSTMENT
        message = "Your readings need attention. Start with small, consistent changes."
    
    return {
        'status': status,
        'message': message,
        'score': score
    }


def generate_weekly_progress_analysis(weekly_progress: WeeklyProgress) -> str:
    """
    Generate formatted weekly progress analysis.
    
    Returns:
        Formatted progress analysis string
    """
    evaluation = evaluate_weekly_progress(weekly_progress)
    
    parts = []
    parts.append("📅 **Weekly Progress Analysis**\n")
    
    status_emoji = {
        ProgressStatus.IMPROVING_STEADILY: "✅",
        ProgressStatus.STABLE_CONTROLLED: "➡️",
        ProgressStatus.NEEDS_ADJUSTMENT: "📝"
    }
    
    parts.append(f"{status_emoji[evaluation['status']]} **Status:** {evaluation['status'].value}\n")
    parts.append(f"{evaluation['message']}\n")
    
    if weekly_progress.daily_readings:
        parts.append(f"\n**Week Summary:**")
        parts.append(f"- Days tracked: {len(weekly_progress.daily_readings)}")
        
        if weekly_progress.average_fasting:
            parts.append(f"- Average fasting sugar: {weekly_progress.average_fasting:.1f} mg/dL")
        
        if weekly_progress.average_post_meal:
            parts.append(f"- Average post-meal sugar: {weekly_progress.average_post_meal:.1f} mg/dL")
        
        if weekly_progress.total_activity_minutes:
            parts.append(f"- Total activity: {weekly_progress.total_activity_minutes} minutes")
            parts.append(f"- Average per day: {weekly_progress.total_activity_minutes / len(weekly_progress.daily_readings):.0f} minutes")
        
        if weekly_progress.average_diet_score:
            parts.append(f"- Average diet adherence: {weekly_progress.average_diet_score:.1f}/10")
    
    return "\n".join(parts)


def generate_monthly_progress_analysis(
    monthly_summary: MonthlySummary,
    previous_month: Optional[MonthlySummary] = None
) -> str:
    """
    Generate formatted monthly progress analysis.
    
    Returns:
        Formatted monthly progress analysis string
    """
    evaluation = evaluate_monthly_progress(monthly_summary, previous_month)
    
    parts = []
    parts.append("📊 **Monthly Progress Analysis**\n")
    
    status_emoji = {
        ProgressStatus.IMPROVING_STEADILY: "✅",
        ProgressStatus.STABLE_CONTROLLED: "➡️",
        ProgressStatus.NEEDS_ADJUSTMENT: "📝"
    }
    
    parts.append(f"{status_emoji[evaluation['status']]} **Status:** {evaluation['status'].value}\n")
    parts.append(f"{evaluation['message']}\n")
    
    if monthly_summary.health_reports:
        latest_report = max(monthly_summary.health_reports, key=lambda x: x.test_date)
        parts.append(f"\n**Month Summary:**")
        parts.append(f"- Health reports: {len(monthly_summary.health_reports)}")
        parts.append(f"- Latest FBS: {latest_report.fbs:.1f} mg/dL")
        parts.append(f"- Latest PPBS: {latest_report.ppbs:.1f} mg/dL")
        parts.append(f"- Latest HbA1c: {latest_report.hba1c:.1f}%")
        
        if monthly_summary.weekly_progresses:
            parts.append(f"- Weeks tracked: {len(monthly_summary.weekly_progresses)}")
    
    return "\n".join(parts)
