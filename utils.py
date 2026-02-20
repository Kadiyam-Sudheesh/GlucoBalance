"""
Utility functions for GlucoBalance.
Helper functions for data processing and analysis.
"""
from typing import List, Optional, Dict
from datetime import date, timedelta
from models import (
    HealthReport,
    WeeklyProgress,
    DailyReading,
    MonthlySummary
)


def calculate_averages(weekly_progress: WeeklyProgress) -> WeeklyProgress:
    """
    Calculate and populate averages for weekly progress.
    
    Args:
        weekly_progress: WeeklyProgress object with daily readings
        
    Returns:
        WeeklyProgress with calculated averages
    """
    if not weekly_progress.daily_readings:
        return weekly_progress
    
    # Calculate fasting sugar average
    fasting_readings = [r.fasting_sugar for r in weekly_progress.daily_readings if r.fasting_sugar is not None]
    if fasting_readings:
        weekly_progress.average_fasting = sum(fasting_readings) / len(fasting_readings)
    
    # Calculate post-meal sugar average
    post_meal_readings = [r.post_meal_sugar for r in weekly_progress.daily_readings if r.post_meal_sugar is not None]
    if post_meal_readings:
        weekly_progress.average_post_meal = sum(post_meal_readings) / len(post_meal_readings)
    
    # Calculate total activity
    activity_minutes = [r.activity_minutes for r in weekly_progress.daily_readings if r.activity_minutes is not None]
    if activity_minutes:
        weekly_progress.total_activity_minutes = sum(activity_minutes)
    
    # Calculate average diet score
    diet_scores = [r.diet_adherence_score for r in weekly_progress.daily_readings if r.diet_adherence_score is not None]
    if diet_scores:
        weekly_progress.average_diet_score = sum(diet_scores) / len(diet_scores)
    
    return weekly_progress


def create_monthly_summary_from_reports(
    reports: List[HealthReport],
    weekly_progresses: Optional[List[WeeklyProgress]] = None
) -> MonthlySummary:
    """
    Create a monthly summary from health reports and weekly progress data.
    
    Args:
        reports: List of health reports for the month
        weekly_progresses: Optional list of weekly progress data
        
    Returns:
        MonthlySummary object
    """
    if not reports:
        raise ValueError("At least one health report is required")
    
    # Determine month and year from first report
    first_report = min(reports, key=lambda x: x.test_date)
    month = first_report.test_date.month
    year = first_report.test_date.year
    
    # Calculate averages
    avg_fbs = sum(r.fbs for r in reports) / len(reports)
    avg_ppbs = sum(r.ppbs for r in reports) / len(reports)
    avg_hba1c = sum(r.hba1c for r in reports) / len(reports)
    
    return MonthlySummary(
        month=month,
        year=year,
        weekly_progresses=weekly_progresses or [],
        health_reports=reports,
        average_fbs=avg_fbs,
        average_ppbs=avg_ppbs,
        average_hba1c=avg_hba1c
    )


def parse_date_string(date_str: str) -> date:
    """
    Parse a date string in various formats.
    
    Supported formats:
    - YYYY-MM-DD
    - YYYY/MM/DD
    - DD-MM-YYYY
    - DD/MM/YYYY
    
    Args:
        date_str: Date string to parse
        
    Returns:
        date object
    """
    # Try ISO format first
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        pass
    
    # Try other formats
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y"
    ]
    
    for fmt in formats:
        try:
            from datetime import datetime
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date string: {date_str}")


def validate_health_report(report: HealthReport) -> Dict[str, bool]:
    """
    Validate a health report for reasonable values.
    
    Args:
        report: HealthReport to validate
        
    Returns:
        Dictionary with validation results
    """
    results = {
        'valid': True,
        'warnings': []
    }
    
    # Check FBS range (typically 70-300 mg/dL)
    if report.fbs < 50 or report.fbs > 400:
        results['warnings'].append(f"FBS value {report.fbs} seems unusual")
    
    # Check PPBS range (typically 100-400 mg/dL)
    if report.ppbs < 80 or report.ppbs > 500:
        results['warnings'].append(f"PPBS value {report.ppbs} seems unusual")
    
    # Check HbA1c range (typically 4-15%)
    if report.hba1c < 3 or report.hba1c > 20:
        results['warnings'].append(f"HbA1c value {report.hba1c} seems unusual")
    
    # Check date is not in future
    if report.test_date > date.today():
        results['warnings'].append("Test date is in the future")
    
    # Check date is not too old (more than 5 years)
    if report.test_date < date.today() - timedelta(days=365*5):
        results['warnings'].append("Test date is more than 5 years old")
    
    if results['warnings']:
        results['valid'] = False
    
    return results


def get_trend_direction(values: List[float]) -> str:
    """
    Determine trend direction from a list of values.
    
    Args:
        values: List of numeric values
        
    Returns:
        "improving", "stable", or "needs_attention"
    """
    if len(values) < 2:
        return "insufficient_data"
    
    first_half = values[:len(values)//2]
    second_half = values[len(values)//2:]
    
    first_avg = sum(first_half) / len(first_half)
    second_avg = sum(second_half) / len(second_half)
    
    change = second_avg - first_avg
    percent_change = abs(change / first_avg * 100) if first_avg > 0 else 0
    
    if percent_change < 5:
        return "stable"
    elif change < 0:
        return "improving"
    else:
        return "needs_attention"


def format_date_for_display(d: date) -> str:
    """
    Format a date for user-friendly display.
    
    Args:
        d: date object
        
    Returns:
        Formatted date string (e.g., "February 9, 2026")
    """
    return d.strftime("%B %d, %Y")


def format_date_short(d: date) -> str:
    """
    Format a date in short format.
    
    Args:
        d: date object
        
    Returns:
        Short formatted date string (e.g., "Feb 9, 2026")
    """
    return d.strftime("%b %d, %Y")


def days_between_dates(date1: date, date2: date) -> int:
    """
    Calculate days between two dates.
    
    Args:
        date1: First date
        date2: Second date
        
    Returns:
        Number of days between dates
    """
    return abs((date2 - date1).days)


def get_target_ranges(diabetes_type: str) -> Dict[str, Dict[str, float]]:
    """
    Get target ranges for different diabetes types.
    
    Args:
        diabetes_type: Type of diabetes
        
    Returns:
        Dictionary with target ranges for FBS, PPBS, and HbA1c
    """
    ranges = {
        "TYPE_1": {
            "fbs": {"min": 80, "max": 130, "ideal": 100},
            "ppbs": {"min": 100, "max": 180, "ideal": 140},
            "hba1c": {"min": 6.5, "max": 7.5, "ideal": 7.0}
        },
        "TYPE_2": {
            "fbs": {"min": 80, "max": 130, "ideal": 100},
            "ppbs": {"min": 100, "max": 180, "ideal": 140},
            "hba1c": {"min": 6.5, "max": 7.0, "ideal": 6.5}
        },
        "PRE_DIABETIC": {
            "fbs": {"min": 100, "max": 125, "ideal": 110},
            "ppbs": {"min": 140, "max": 199, "ideal": 160},
            "hba1c": {"min": 5.7, "max": 6.4, "ideal": 6.0}
        },
        "GESTATIONAL": {
            "fbs": {"min": 70, "max": 95, "ideal": 85},
            "ppbs": {"min": 100, "max": 140, "ideal": 120},
            "hba1c": {"min": 5.0, "max": 6.0, "ideal": 5.5}
        }
    }
    
    return ranges.get(diabetes_type.upper(), ranges["TYPE_2"])
