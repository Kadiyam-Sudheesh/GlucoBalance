"""
Example usage of GlucoBalance - Simple example showing how to use the system.
"""
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
from datetime import date, timedelta


def simple_example():
    """Simple example with minimal data."""
    print("=" * 70)
    print("SIMPLE EXAMPLE - Minimal Data")
    print("=" * 70)
    
    # Create user profile
    user = UserProfile(
        age=50,
        diabetes_type=DiabetesType.TYPE_2,
        height_cm=165,
        weight_kg=70,
        name="Jane Smith"
    )
    
    # Create current health report
    current_report = HealthReport(
        fbs=140.0,  # mg/dL
        ppbs=200.0,  # mg/dL
        hba1c=7.5,  # %
        test_date=date.today()
    )
    
    # Create previous report (optional)
    previous_report = HealthReport(
        fbs=150.0,
        ppbs=220.0,
        hba1c=7.8,
        test_date=date.today() - timedelta(days=30)
    )
    
    # Create analysis context
    context = AnalysisContext(
        user_profile=user,
        current_report=current_report,
        previous_report=previous_report,
        weekly_progress=None,  # Optional
        monthly_summary=None   # Optional
    )
    
    # Generate analysis
    assistant = GlucoBalance()
    report = assistant.generate_comprehensive_analysis(context)
    
    # Save to file
    with open('simple_example_output.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("✓ Analysis generated!")
    print("✓ Saved to 'simple_example_output.txt'")
    print(f"✓ Report length: {len(report)} characters\n")


def full_example():
    """Full example with weekly and monthly data."""
    print("=" * 70)
    print("FULL EXAMPLE - With Weekly & Monthly Data")
    print("=" * 70)
    
    # Use the built-in example context creator
    from glucobalance import create_example_context
    
    context = create_example_context()
    
    # Generate analysis
    assistant = GlucoBalance()
    report = assistant.generate_comprehensive_analysis(context)
    
    # Save to file
    with open('full_example_output.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("✓ Full analysis generated!")
    print("✓ Saved to 'full_example_output.txt'")
    print(f"✓ Report length: {len(report)} characters\n")


def quick_summary_example():
    """Example of generating just a quick summary."""
    print("=" * 70)
    print("QUICK SUMMARY EXAMPLE")
    print("=" * 70)
    
    user = UserProfile(
        age=45,
        diabetes_type=DiabetesType.PRE_DIABETIC,
        height_cm=175,
        weight_kg=80,
        name="Bob Johnson"
    )
    
    current_report = HealthReport(
        fbs=110.0,
        ppbs=150.0,
        hba1c=6.0,
        test_date=date.today()
    )
    
    previous_report = HealthReport(
        fbs=115.0,
        ppbs=160.0,
        hba1c=6.2,
        test_date=date.today() - timedelta(days=30)
    )
    
    context = AnalysisContext(
        user_profile=user,
        current_report=current_report,
        previous_report=previous_report
    )
    
    assistant = GlucoBalance()
    summary = assistant.generate_quick_summary(context)
    
    print(summary)
    print()


if __name__ == "__main__":
    # Run examples
    simple_example()
    full_example()
    quick_summary_example()
    
    print("=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)
