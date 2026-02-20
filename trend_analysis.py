"""
Report Comparison & Trend Analysis module for GlucoBalance.
Compares reports and identifies patterns in health data.
"""
from typing import Optional, List, Dict
from models import HealthReport, WeeklyProgress, MonthlySummary, ProgressStatus
from datetime import date, timedelta


def compare_reports(
    current_report: HealthReport,
    previous_report: HealthReport
) -> Dict[str, Dict[str, any]]:
    """
    Compare current report with previous report.
    
    Returns:
        Dictionary with comparison data for each metric
    """
    comparison = {}
    
    # FBS comparison
    fbs_diff = current_report.fbs - previous_report.fbs
    fbs_percent_change = (fbs_diff / previous_report.fbs) * 100 if previous_report.fbs > 0 else 0
    
    comparison['fbs'] = {
        'current': current_report.fbs,
        'previous': previous_report.fbs,
        'difference': fbs_diff,
        'percent_change': fbs_percent_change,
        'trend': 'improving' if fbs_diff < 0 else 'stable' if abs(fbs_diff) < 5 else 'needs_attention',
        'days_between': (current_report.test_date - previous_report.test_date).days
    }
    
    # PPBS comparison
    ppbs_diff = current_report.ppbs - previous_report.ppbs
    ppbs_percent_change = (ppbs_diff / previous_report.ppbs) * 100 if previous_report.ppbs > 0 else 0
    
    comparison['ppbs'] = {
        'current': current_report.ppbs,
        'previous': previous_report.ppbs,
        'difference': ppbs_diff,
        'percent_change': ppbs_percent_change,
        'trend': 'improving' if ppbs_diff < 0 else 'stable' if abs(ppbs_diff) < 10 else 'needs_attention',
        'days_between': (current_report.test_date - previous_report.test_date).days
    }
    
    # HbA1c comparison
    hba1c_diff = current_report.hba1c - previous_report.hba1c
    hba1c_percent_change = (hba1c_diff / previous_report.hba1c) * 100 if previous_report.hba1c > 0 else 0
    
    comparison['hba1c'] = {
        'current': current_report.hba1c,
        'previous': previous_report.hba1c,
        'difference': hba1c_diff,
        'percent_change': hba1c_percent_change,
        'trend': 'improving' if hba1c_diff < 0 else 'stable' if abs(hba1c_diff) < 0.3 else 'needs_attention',
        'days_between': (current_report.test_date - previous_report.test_date).days
    }
    
    return comparison


def analyze_weekly_trends(weekly_progress: WeeklyProgress) -> Dict[str, any]:
    """
    Analyze weekly trends from daily readings.
    
    Returns:
        Dictionary with trend analysis
    """
    if not weekly_progress.daily_readings:
        return {'status': 'insufficient_data', 'message': 'Not enough data for weekly analysis'}
    
    # Extract sugar readings
    fasting_readings = [r.fasting_sugar for r in weekly_progress.daily_readings if r.fasting_sugar is not None]
    post_meal_readings = [r.post_meal_sugar for r in weekly_progress.daily_readings if r.post_meal_sugar is not None]
    
    if not fasting_readings and not post_meal_readings:
        return {'status': 'insufficient_data', 'message': 'No sugar readings available for this week'}
    
    trends = {}
    
    # Analyze fasting sugar trend
    if len(fasting_readings) >= 3:
        first_half = fasting_readings[:len(fasting_readings)//2]
        second_half = fasting_readings[len(fasting_readings)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        trend_direction = 'improving' if second_avg < first_avg else 'stable' if abs(second_avg - first_avg) < 5 else 'needs_attention'
        
        trends['fasting'] = {
            'trend': trend_direction,
            'first_half_avg': first_avg,
            'second_half_avg': second_avg,
            'change': second_avg - first_avg,
            'readings_count': len(fasting_readings)
        }
    
    # Analyze post-meal sugar trend
    if len(post_meal_readings) >= 3:
        first_half = post_meal_readings[:len(post_meal_readings)//2]
        second_half = post_meal_readings[len(post_meal_readings)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        trend_direction = 'improving' if second_avg < first_avg else 'stable' if abs(second_avg - first_avg) < 10 else 'needs_attention'
        
        trends['post_meal'] = {
            'trend': trend_direction,
            'first_half_avg': first_avg,
            'second_half_avg': second_avg,
            'change': second_avg - first_avg,
            'readings_count': len(post_meal_readings)
        }
    
    # Activity trend
    activity_days = [r.activity_minutes for r in weekly_progress.daily_readings if r.activity_minutes is not None]
    if activity_days:
        trends['activity'] = {
            'total_minutes': sum(activity_days),
            'average_daily': sum(activity_days) / len(activity_days),
            'active_days': len(activity_days),
            'total_days': len(weekly_progress.daily_readings)
        }
    
    # Diet adherence trend
    diet_scores = [r.diet_adherence_score for r in weekly_progress.daily_readings if r.diet_adherence_score is not None]
    if diet_scores:
        trends['diet'] = {
            'average_score': sum(diet_scores) / len(diet_scores),
            'readings_count': len(diet_scores),
            'status': 'excellent' if sum(diet_scores) / len(diet_scores) >= 8 else 'good' if sum(diet_scores) / len(diet_scores) >= 6 else 'needs_improvement'
        }
    
    return trends


def analyze_monthly_trends(
    monthly_summary: MonthlySummary,
    previous_month: Optional[MonthlySummary] = None
) -> Dict[str, any]:
    """
    Analyze monthly trends and patterns.
    
    Returns:
        Dictionary with monthly trend analysis
    """
    trends = {}
    
    # Compare health reports
    if len(monthly_summary.health_reports) >= 2:
        reports = sorted(monthly_summary.health_reports, key=lambda x: x.test_date)
        first_report = reports[0]
        last_report = reports[-1]
        
        trends['reports'] = compare_reports(last_report, first_report)
    
    # Compare with previous month
    if previous_month and monthly_summary.health_reports and previous_month.health_reports:
        current_latest = max(monthly_summary.health_reports, key=lambda x: x.test_date)
        previous_latest = max(previous_month.health_reports, key=lambda x: x.test_date)
        
        trends['month_over_month'] = compare_reports(current_latest, previous_latest)
    
    # Weekly progress consistency
    if monthly_summary.weekly_progresses:
        avg_fbs_list = [w.average_fasting for w in monthly_summary.weekly_progresses if w.average_fasting is not None]
        if avg_fbs_list:
            trends['weekly_consistency'] = {
                'average_fbs': sum(avg_fbs_list) / len(avg_fbs_list),
                'variation': max(avg_fbs_list) - min(avg_fbs_list) if len(avg_fbs_list) > 1 else 0,
                'weeks_tracked': len(avg_fbs_list),
                'status': 'consistent' if (max(avg_fbs_list) - min(avg_fbs_list)) < 15 else 'variable'
            }
    
    return trends


def generate_report_comparison(
    current_report: HealthReport,
    previous_report: Optional[HealthReport] = None,
    weekly_progress: Optional[WeeklyProgress] = None,
    monthly_summary: Optional[MonthlySummary] = None
) -> str:
    """
    Generate formatted report comparison and trend analysis.
    
    Returns:
        Formatted comparison string
    """
    parts = []
    
    parts.append("📈 **Report Comparison & Trend Analysis**\n")
    
    # Compare with previous report
    if previous_report:
        comparison = compare_reports(current_report, previous_report)
        
        parts.append(f"**Comparison with Previous Report ({previous_report.test_date.strftime('%B %d, %Y')}):**\n")
        
        # FBS comparison
        fbs_comp = comparison['fbs']
        if fbs_comp['trend'] == 'improving':
            parts.append(f"✅ **Fasting Sugar:** {fbs_comp['current']:.1f} mg/dL (was {fbs_comp['previous']:.1f} mg/dL)")
            parts.append(f"   Improved by {abs(fbs_comp['difference']):.1f} mg/dL - Great progress!")
        elif fbs_comp['trend'] == 'stable':
            parts.append(f"➡️ **Fasting Sugar:** {fbs_comp['current']:.1f} mg/dL (was {fbs_comp['previous']:.1f} mg/dL)")
            parts.append(f"   Remained stable - Consistency is key!")
        else:
            parts.append(f"⚠️ **Fasting Sugar:** {fbs_comp['current']:.1f} mg/dL (was {fbs_comp['previous']:.1f} mg/dL)")
            parts.append(f"   Increased by {fbs_comp['difference']:.1f} mg/dL - Let's focus on lifestyle adjustments.")
        
        # PPBS comparison
        ppbs_comp = comparison['ppbs']
        if ppbs_comp['trend'] == 'improving':
            parts.append(f"\n✅ **Post-Meal Sugar:** {ppbs_comp['current']:.1f} mg/dL (was {ppbs_comp['previous']:.1f} mg/dL)")
            parts.append(f"   Improved by {abs(ppbs_comp['difference']):.1f} mg/dL - Excellent!")
        elif ppbs_comp['trend'] == 'stable':
            parts.append(f"\n➡️ **Post-Meal Sugar:** {ppbs_comp['current']:.1f} mg/dL (was {ppbs_comp['previous']:.1f} mg/dL)")
            parts.append(f"   Remained stable - Keep it up!")
        else:
            parts.append(f"\n⚠️ **Post-Meal Sugar:** {ppbs_comp['current']:.1f} mg/dL (was {ppbs_comp['previous']:.1f} mg/dL)")
            parts.append(f"   Increased by {ppbs_comp['difference']:.1f} mg/dL - Consider meal timing and portion control.")
        
        # HbA1c comparison
        hba1c_comp = comparison['hba1c']
        if hba1c_comp['trend'] == 'improving':
            parts.append(f"\n✅ **HbA1c (3-month average):** {hba1c_comp['current']:.1f}% (was {hba1c_comp['previous']:.1f}%)")
            parts.append(f"   Decreased by {abs(hba1c_comp['difference']):.1f}% - Your long-term control is improving!")
        elif hba1c_comp['trend'] == 'stable':
            parts.append(f"\n➡️ **HbA1c (3-month average):** {hba1c_comp['current']:.1f}% (was {hba1c_comp['previous']:.1f}%)")
            parts.append(f"   Remained stable - Consistent management is working!")
        else:
            parts.append(f"\n⚠️ **HbA1c (3-month average):** {hba1c_comp['current']:.1f}% (was {hba1c_comp['previous']:.1f}%)")
            parts.append(f"   Increased by {hba1c_comp['difference']:.1f}% - Focus on building consistent daily habits.")
        
        parts.append("")
    else:
        parts.append("No previous report available for comparison. This will be your baseline for future comparisons.\n")
    
    # Weekly trends
    if weekly_progress:
        parts.append("**Weekly Trend Analysis:**\n")
        weekly_trends = analyze_weekly_trends(weekly_progress)
        
        if weekly_trends.get('status') != 'insufficient_data':
            if 'fasting' in weekly_trends:
                fasting_trend = weekly_trends['fasting']
                if fasting_trend['trend'] == 'improving':
                    parts.append(f"✅ **Fasting Sugar Trend:** Improving over the week")
                    parts.append(f"   Average decreased from {fasting_trend['first_half_avg']:.1f} to {fasting_trend['second_half_avg']:.1f} mg/dL")
                elif fasting_trend['trend'] == 'stable':
                    parts.append(f"➡️ **Fasting Sugar Trend:** Stable throughout the week")
                else:
                    parts.append(f"⚠️ **Fasting Sugar Trend:** Needs attention")
                    parts.append(f"   Average increased from {fasting_trend['first_half_avg']:.1f} to {fasting_trend['second_half_avg']:.1f} mg/dL")
            
            if 'activity' in weekly_trends:
                activity = weekly_trends['activity']
                parts.append(f"\n📊 **Activity:** {activity['active_days']} active days, {activity['average_daily']:.0f} minutes/day average")
            
            if 'diet' in weekly_trends:
                diet = weekly_trends['diet']
                parts.append(f"\n🍽️ **Diet Adherence:** Average score {diet['average_score']:.1f}/10 ({diet['status']})")
        else:
            parts.append("Insufficient weekly data for trend analysis.\n")
    
    # Monthly trends
    if monthly_summary:
        parts.append("\n**Monthly Pattern Analysis:**\n")
        monthly_trends = analyze_monthly_trends(monthly_summary)
        
        if 'weekly_consistency' in monthly_trends:
            consistency = monthly_trends['weekly_consistency']
            parts.append(f"📅 **Consistency:** {consistency['weeks_tracked']} weeks tracked")
            parts.append(f"   Average fasting sugar: {consistency['average_fbs']:.1f} mg/dL")
            parts.append(f"   Variation: {consistency['variation']:.1f} mg/dL ({consistency['status']})")
    
    return "\n".join(parts)
