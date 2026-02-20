"""
Command-line interface for GlucoBalance.
Provides an easy way to interact with the health assistant.
"""
import sys
import json
from datetime import date, timedelta
from typing import Optional
from glucobalance import GlucoBalance
from models import (
    AnalysisContext,
    UserProfile,
    HealthReport,
    WeeklyProgress,
    DailyReading,
    MonthlySummary,
    DiabetesType
)


def create_user_profile_interactive() -> UserProfile:
    """Interactively create a user profile."""
    print("\n=== User Profile Setup ===")
    
    name = input("Enter your name (optional): ").strip() or None
    age = int(input("Enter your age: "))
    
    print("\nDiabetes Type:")
    print("1. Type 1")
    print("2. Type 2")
    print("3. Pre-diabetic")
    print("4. Gestational")
    choice = input("Select (1-4): ").strip()
    
    diabetes_type_map = {
        "1": DiabetesType.TYPE_1,
        "2": DiabetesType.TYPE_2,
        "3": DiabetesType.PRE_DIABETIC,
        "4": DiabetesType.GESTATIONAL
    }
    diabetes_type = diabetes_type_map.get(choice, DiabetesType.TYPE_2)
    
    height_cm = float(input("Enter height (cm): "))
    weight_kg = float(input("Enter weight (kg): "))
    
    return UserProfile(
        name=name,
        age=age,
        diabetes_type=diabetes_type,
        height_cm=height_cm,
        weight_kg=weight_kg
    )


def create_health_report_interactive() -> HealthReport:
    """Interactively create a health report."""
    print("\n=== Health Report ===")
    
    fbs = float(input("Enter Fasting Blood Sugar (FBS) in mg/dL: "))
    ppbs = float(input("Enter Post-Meal Sugar (PPBS) in mg/dL: "))
    hba1c = float(input("Enter HbA1c (%): "))
    
    date_str = input("Enter test date (YYYY-MM-DD) or press Enter for today: ").strip()
    if date_str:
        test_date = date.fromisoformat(date_str)
    else:
        test_date = date.today()
    
    notes = input("Any additional notes (optional): ").strip() or None
    
    return HealthReport(
        fbs=fbs,
        ppbs=ppbs,
        hba1c=hba1c,
        test_date=test_date,
        notes=notes
    )


def create_weekly_progress_interactive() -> Optional[WeeklyProgress]:
    """Interactively create weekly progress data."""
    print("\n=== Weekly Progress (Optional) ===")
    include = input("Do you want to add weekly progress data? (y/n): ").strip().lower()
    
    if include != 'y':
        return None
    
    week_start_str = input("Enter week start date (YYYY-MM-DD) or press Enter for 7 days ago: ").strip()
    if week_start_str:
        week_start = date.fromisoformat(week_start_str)
    else:
        week_start = date.today() - timedelta(days=7)
    
    daily_readings = []
    print("\nEnter daily readings (press Enter to skip a day):")
    
    for i in range(7):
        current_date = week_start + timedelta(days=i)
        print(f"\nDay {i+1} - {current_date.strftime('%Y-%m-%d')}:")
        
        fasting = input("  Fasting sugar (mg/dL, optional): ").strip()
        post_meal = input("  Post-meal sugar (mg/dL, optional): ").strip()
        activity = input("  Activity minutes (optional): ").strip()
        diet_score = input("  Diet adherence score 0-10 (optional): ").strip()
        
        reading = DailyReading(
            date=current_date,
            fasting_sugar=float(fasting) if fasting else None,
            post_meal_sugar=float(post_meal) if post_meal else None,
            activity_minutes=int(activity) if activity else None,
            diet_adherence_score=float(diet_score) if diet_score else None
        )
        
        daily_readings.append(reading)
    
    return WeeklyProgress(
        week_start_date=week_start,
        daily_readings=daily_readings
    )


def main():
    """Main CLI entry point."""
    print("=" * 70)
    print("GLUCOBALANCE - Digital Health Assistant")
    print("=" * 70)
    print("\nThis tool helps you understand your health data and track progress.")
    print("Let's get started!\n")
    
    # Create user profile
    user_profile = create_user_profile_interactive()
    
    # Create current health report
    print("\n" + "=" * 70)
    current_report = create_health_report_interactive()
    
    # Create previous report (optional)
    print("\n" + "=" * 70)
    print("Previous Health Report (Optional - for comparison)")
    include_previous = input("Do you have a previous report? (y/n): ").strip().lower()
    previous_report = None
    if include_previous == 'y':
        previous_report = create_health_report_interactive()
    
    # Create weekly progress (optional)
    print("\n" + "=" * 70)
    weekly_progress = create_weekly_progress_interactive()
    
    # Create monthly summary (optional)
    monthly_summary = None
    if weekly_progress:
        monthly_summary = MonthlySummary(
            month=date.today().month,
            year=date.today().year,
            weekly_progresses=[weekly_progress],
            health_reports=[current_report]
        )
        if previous_report:
            monthly_summary.health_reports.append(previous_report)
    
    # Create analysis context
    context = AnalysisContext(
        user_profile=user_profile,
        current_report=current_report,
        previous_report=previous_report,
        weekly_progress=weekly_progress,
        monthly_summary=monthly_summary
    )
    
    # Generate analysis
    print("\n" + "=" * 70)
    print("Generating your comprehensive health analysis...")
    print("=" * 70 + "\n")
    
    assistant = GlucoBalance()
    report = assistant.generate_comprehensive_analysis(context)
    
    # Save to file
    output_filename = f"glucobalance_report_{date.today().strftime('%Y%m%d')}.txt"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + "=" * 70)
    print("Analysis Complete!")
    print("=" * 70)
    print(f"\nYour comprehensive health analysis has been saved to:")
    print(f"  {output_filename}")
    print(f"\nReport length: {len(report)} characters")
    print("\nYou can open this file to view your complete analysis.")
    print("\nRemember: This platform is not a replacement for professional medical advice.")
    print("For medication changes or medical concerns, please consult your doctor.")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)
