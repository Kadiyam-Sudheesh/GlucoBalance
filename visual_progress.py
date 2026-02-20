"""
Visual Progress Representation module for GlucoBalance.
Helps users understand graphs and visual data in plain language.
"""
from typing import Optional, List, Dict
from models import WeeklyProgress, MonthlySummary, HealthReport
from datetime import date
import json


def interpret_line_graph(
    data_points: List[float],
    labels: List[str],
    metric_name: str = "Sugar Level"
) -> Dict[str, str]:
    """
    Interpret a line graph and provide plain language explanation.
    
    Args:
        data_points: List of numeric values
        labels: List of labels (dates) for each point
        metric_name: Name of the metric being graphed
        
    Returns:
        Dictionary with interpretation
    """
    if len(data_points) < 2:
        return {
            'trend': 'insufficient_data',
            'message': 'Not enough data points to identify a trend.',
            'direction': None
        }
    
    # Calculate trend
    first_half = data_points[:len(data_points)//2]
    second_half = data_points[len(data_points)//2:]
    
    first_avg = sum(first_half) / len(first_half)
    second_avg = sum(second_half) / len(second_half)
    
    change = second_avg - first_avg
    percent_change = (change / first_avg) * 100 if first_avg > 0 else 0
    
    # Determine trend direction
    if abs(change) < (first_avg * 0.05):  # Less than 5% change
        trend = 'stable'
        direction = 'stable'
        message = f"The {metric_name.lower()} graph shows a stable trend, which indicates consistent control."
    elif change < 0:
        trend = 'decreasing'
        direction = 'downward'
        if abs(percent_change) > 10:
            message = f"The {metric_name.lower()} graph shows a clear downward trend, indicating significant improvement."
        else:
            message = f"The {metric_name.lower()} graph shows a gradual downward trend, showing steady progress."
    else:
        trend = 'increasing'
        direction = 'upward'
        if abs(percent_change) > 10:
            message = f"The {metric_name.lower()} graph shows an upward trend, suggesting we should focus on lifestyle adjustments."
        else:
            message = f"The {metric_name.lower()} graph shows a slight upward trend, which is normal but worth monitoring."
    
    # Find peaks and valleys
    max_val = max(data_points)
    min_val = min(data_points)
    variation = max_val - min_val
    
    return {
        'trend': trend,
        'direction': direction,
        'message': message,
        'first_half_avg': first_avg,
        'second_half_avg': second_avg,
        'change': change,
        'percent_change': percent_change,
        'max_value': max_val,
        'min_value': min_val,
        'variation': variation,
        'stability': 'high' if variation < (first_avg * 0.15) else 'moderate' if variation < (first_avg * 0.30) else 'low'
    }


def generate_weekly_graph_explanation(weekly_progress: WeeklyProgress) -> str:
    """
    Generate explanation for weekly sugar trend graph.
    
    Returns:
        Formatted graph explanation string
    """
    parts = []
    parts.append("📈 **Visual Progress: Weekly Sugar Trends**\n")
    
    if not weekly_progress.daily_readings:
        parts.append("No data available for graph visualization. Start logging daily readings to see trends.\n")
        return "\n".join(parts)
    
    # Extract fasting sugar readings
    fasting_data = []
    fasting_dates = []
    for reading in sorted(weekly_progress.daily_readings, key=lambda x: x.date):
        if reading.fasting_sugar is not None:
            fasting_data.append(reading.fasting_sugar)
            fasting_dates.append(reading.date.strftime('%b %d'))
    
    # Extract post-meal sugar readings
    post_meal_data = []
    post_meal_dates = []
    for reading in sorted(weekly_progress.daily_readings, key=lambda x: x.date):
        if reading.post_meal_sugar is not None:
            post_meal_data.append(reading.post_meal_sugar)
            post_meal_dates.append(reading.date.strftime('%b %d'))
    
    # Explain fasting sugar graph
    if len(fasting_data) >= 2:
        fasting_interpretation = interpret_line_graph(fasting_data, fasting_dates, "Fasting Sugar")
        parts.append("**Fasting Sugar Graph:**\n")
        parts.append(f"{fasting_interpretation['message']}")
        
        if fasting_interpretation['direction'] == 'downward':
            parts.append(f"This downward trend shows your sugar levels are becoming more stable.")
        elif fasting_interpretation['direction'] == 'stable':
            parts.append(f"Stability in your readings is a positive sign of consistent management.")
        
        parts.append(f"\n- Average at start of week: {fasting_interpretation['first_half_avg']:.1f} mg/dL")
        parts.append(f"- Average at end of week: {fasting_interpretation['second_half_avg']:.1f} mg/dL")
        parts.append(f"- Variation: {fasting_interpretation['variation']:.1f} mg/dL ({fasting_interpretation['stability']} stability)")
        parts.append("")
    elif len(fasting_data) == 1:
        parts.append("**Fasting Sugar Graph:**\n")
        parts.append(f"Only one reading available ({fasting_data[0]:.1f} mg/dL). Log more readings to see trends.\n")
    
    # Explain post-meal sugar graph
    if len(post_meal_data) >= 2:
        post_meal_interpretation = interpret_line_graph(post_meal_data, post_meal_dates, "Post-Meal Sugar")
        parts.append("**Post-Meal Sugar Graph:**\n")
        parts.append(f"{post_meal_interpretation['message']}")
        
        if post_meal_interpretation['direction'] == 'downward':
            parts.append(f"This downward trend indicates better meal-time sugar control.")
        elif post_meal_interpretation['direction'] == 'stable':
            parts.append(f"Consistent post-meal readings suggest good meal planning and timing.")
        
        parts.append(f"\n- Average at start of week: {post_meal_interpretation['first_half_avg']:.1f} mg/dL")
        parts.append(f"- Average at end of week: {post_meal_interpretation['second_half_avg']:.1f} mg/dL")
        parts.append(f"- Variation: {post_meal_interpretation['variation']:.1f} mg/dL ({post_meal_interpretation['stability']} stability)")
    elif len(post_meal_data) == 1:
        parts.append("**Post-Meal Sugar Graph:**\n")
        parts.append(f"Only one reading available ({post_meal_data[0]:.1f} mg/dL). Log more readings to see trends.")
    
    return "\n".join(parts)


def generate_monthly_comparison_explanation(
    monthly_summary: MonthlySummary,
    previous_month: Optional[MonthlySummary] = None
) -> str:
    """
    Generate explanation for monthly comparison chart.
    
    Returns:
        Formatted comparison explanation string
    """
    parts = []
    parts.append("📊 **Visual Progress: Monthly Comparison**\n")
    
    if not monthly_summary.health_reports:
        parts.append("No health reports available for comparison.\n")
        return "\n".join(parts)
    
    # Get reports sorted by date
    reports = sorted(monthly_summary.health_reports, key=lambda x: x.test_date)
    
    if len(reports) >= 2:
        parts.append("**Month-over-Month Comparison Chart:**\n")
        
        # Extract FBS values
        fbs_values = [r.fbs for r in reports]
        fbs_dates = [r.test_date.strftime('%b %Y') for r in reports]
        
        fbs_interpretation = interpret_line_graph(fbs_values, fbs_dates, "Fasting Sugar")
        parts.append(f"**Fasting Sugar Trend:**\n")
        parts.append(f"{fbs_interpretation['message']}")
        
        if fbs_interpretation['direction'] == 'downward':
            parts.append("This downward trend in the graph shows your sugar levels are becoming more stable over time.")
        elif fbs_interpretation['direction'] == 'stable':
            parts.append("The stable line in your graph indicates consistent sugar control.")
        
        parts.append(f"\n- Started at: {fbs_values[0]:.1f} mg/dL")
        parts.append(f"- Current: {fbs_values[-1]:.1f} mg/dL")
        parts.append(f"- Change: {fbs_interpretation['change']:.1f} mg/dL")
        parts.append("")
        
        # Extract PPBS values
        ppbs_values = [r.ppbs for r in reports]
        ppbs_interpretation = interpret_line_graph(ppbs_values, fbs_dates, "Post-Meal Sugar")
        parts.append(f"**Post-Meal Sugar Trend:**\n")
        parts.append(f"{ppbs_interpretation['message']}")
        
        parts.append(f"\n- Started at: {ppbs_values[0]:.1f} mg/dL")
        parts.append(f"- Current: {ppbs_values[-1]:.1f} mg/dL")
        parts.append(f"- Change: {ppbs_interpretation['change']:.1f} mg/dL")
        parts.append("")
        
        # Extract HbA1c values
        hba1c_values = [r.hba1c for r in reports]
        hba1c_interpretation = interpret_line_graph(hba1c_values, fbs_dates, "HbA1c")
        parts.append(f"**HbA1c (3-Month Average) Trend:**\n")
        parts.append(f"{hba1c_interpretation['message']}")
        
        if hba1c_interpretation['direction'] == 'downward':
            parts.append("This downward trend shows your long-term sugar control is improving.")
        
        parts.append(f"\n- Started at: {hba1c_values[0]:.1f}%")
        parts.append(f"- Current: {hba1c_values[-1]:.1f}%")
        parts.append(f"- Change: {hba1c_interpretation['change']:.1f}%")
    
    elif len(reports) == 1:
        parts.append("Only one report available. After your next test, you'll see comparison charts.\n")
    
    # Compare with previous month if available
    if previous_month and previous_month.health_reports:
        parts.append("\n**Previous Month Comparison:**\n")
        current_latest = max(monthly_summary.health_reports, key=lambda x: x.test_date)
        previous_latest = max(previous_month.health_reports, key=lambda x: x.test_date)
        
        fbs_change = current_latest.fbs - previous_latest.fbs
        if fbs_change < 0:
            parts.append(f"✅ Fasting sugar improved by {abs(fbs_change):.1f} mg/dL compared to last month.")
        elif abs(fbs_change) < 5:
            parts.append(f"➡️ Fasting sugar remained stable (change: {fbs_change:.1f} mg/dL).")
        else:
            parts.append(f"⚠️ Fasting sugar increased by {fbs_change:.1f} mg/dL. Focus on lifestyle adjustments.")
    
    return "\n".join(parts)
