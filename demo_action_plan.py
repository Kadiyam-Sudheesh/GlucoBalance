"""
Demo script to generate and display action plans.
Shows both weekly and monthly action plans.
"""
import sys
import io

# Set UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from glucobalance import GlucoBalance
from action_plans import generate_weekly_action_plan, generate_monthly_improvement_plan
from models import UserProfile, HealthReport, DiabetesType
from datetime import date


def demo_action_plans():
    """Generate and display action plans."""
    print("=" * 70)
    print("GLUCOBALANCE - ACTION PLAN DEMONSTRATION")
    print("=" * 70)
    print("\nGenerating personalized action plans...\n")
    
    # Create example user profile
    user = UserProfile(
        age=45,
        diabetes_type=DiabetesType.TYPE_2,
        height_cm=170,
        weight_kg=75,
        name="Demo User"
    )
    
    # Create example health report
    current_report = HealthReport(
        fbs=140.0,
        ppbs=200.0,
        hba1c=7.5,
        test_date=date.today()
    )
    
    print("=" * 70)
    print("WEEKLY ACTION PLAN")
    print("=" * 70)
    print()
    
    # Generate weekly action plan
    weekly_plan = generate_weekly_action_plan(
        user_profile=user,
        weekly_progress=None,
        current_report=current_report
    )
    print(weekly_plan)
    
    print("\n" + "=" * 70)
    print("MONTHLY IMPROVEMENT PLAN")
    print("=" * 70)
    print()
    
    # Generate monthly improvement plan
    monthly_plan = generate_monthly_improvement_plan(
        user_profile=user,
        monthly_summary=None,
        current_report=current_report
    )
    print(monthly_plan)
    
    # Save to file
    output_filename = "action_plans_demo.txt"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("GLUCOBALANCE - ACTION PLANS\n")
        f.write("=" * 70 + "\n\n")
        f.write(weekly_plan)
        f.write("\n\n" + "=" * 70 + "\n\n")
        f.write(monthly_plan)
    
    print("\n" + "=" * 70)
    print("Action plans saved to:", output_filename)
    print("=" * 70)


if __name__ == "__main__":
    demo_action_plans()
