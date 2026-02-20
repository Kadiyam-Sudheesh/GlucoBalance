"""
API wrapper for GlucoBalance.
Provides programmatic access to the health assistant functionality.
"""
from typing import Optional, Dict, List, Any
from datetime import date
from glucobalance import GlucoBalance
from models import (
    AnalysisContext,
    UserProfile,
    HealthReport,
    WeeklyProgress,
    DailyReading,
    MonthlySummary,
    DiabetesType,
    ProgressStatus
)


class GlucoBalanceAPI:
    """
    API wrapper for GlucoBalance functionality.
    Provides easy programmatic access to health analysis features.
    """
    
    def __init__(self):
        """Initialize the API."""
        self.assistant = GlucoBalance()
    
    def create_user_profile(
        self,
        age: int,
        diabetes_type: str,
        height_cm: float,
        weight_kg: float,
        name: Optional[str] = None
    ) -> UserProfile:
        """
        Create a user profile.
        
        Args:
            age: User's age
            diabetes_type: "TYPE_1", "TYPE_2", "PRE_DIABETIC", or "GESTATIONAL"
            height_cm: Height in centimeters
            weight_kg: Weight in kilograms
            name: Optional user name
            
        Returns:
            UserProfile object
        """
        diabetes_type_map = {
            "TYPE_1": DiabetesType.TYPE_1,
            "TYPE_2": DiabetesType.TYPE_2,
            "PRE_DIABETIC": DiabetesType.PRE_DIABETIC,
            "GESTATIONAL": DiabetesType.GESTATIONAL
        }
        
        return UserProfile(
            name=name,
            age=age,
            diabetes_type=diabetes_type_map.get(diabetes_type.upper(), DiabetesType.TYPE_2),
            height_cm=height_cm,
            weight_kg=weight_kg
        )
    
    def create_health_report(
        self,
        fbs: float,
        ppbs: float,
        hba1c: float,
        test_date: date,
        notes: Optional[str] = None
    ) -> HealthReport:
        """
        Create a health report.
        
        Args:
            fbs: Fasting Blood Sugar (mg/dL)
            ppbs: Post-Prandial Blood Sugar (mg/dL)
            hba1c: HbA1c percentage
            test_date: Date of the test
            notes: Optional notes
            
        Returns:
            HealthReport object
        """
        return HealthReport(
            fbs=fbs,
            ppbs=ppbs,
            hba1c=hba1c,
            test_date=test_date,
            notes=notes
        )
    
    def create_weekly_progress(
        self,
        week_start_date: date,
        daily_readings: List[Dict[str, Any]]
    ) -> WeeklyProgress:
        """
        Create weekly progress data.
        
        Args:
            week_start_date: Start date of the week
            daily_readings: List of dictionaries with daily reading data
                Each dict should have: date, fasting_sugar, post_meal_sugar,
                activity_minutes, diet_adherence_score (all optional except date)
                
        Returns:
            WeeklyProgress object
        """
        readings = []
        for reading_data in daily_readings:
            readings.append(DailyReading(
                date=reading_data['date'],
                fasting_sugar=reading_data.get('fasting_sugar'),
                post_meal_sugar=reading_data.get('post_meal_sugar'),
                activity_minutes=reading_data.get('activity_minutes'),
                diet_adherence_score=reading_data.get('diet_adherence_score'),
                notes=reading_data.get('notes')
            ))
        
        return WeeklyProgress(
            week_start_date=week_start_date,
            daily_readings=readings
        )
    
    def analyze(
        self,
        user_profile: UserProfile,
        current_report: HealthReport,
        previous_report: Optional[HealthReport] = None,
        weekly_progress: Optional[WeeklyProgress] = None,
        monthly_summary: Optional[MonthlySummary] = None
    ) -> str:
        """
        Generate comprehensive health analysis.
        
        Args:
            user_profile: User profile
            current_report: Current health report
            previous_report: Previous health report (optional)
            weekly_progress: Weekly progress data (optional)
            monthly_summary: Monthly summary data (optional)
            
        Returns:
            Complete formatted analysis report as string
        """
        context = AnalysisContext(
            user_profile=user_profile,
            current_report=current_report,
            previous_report=previous_report,
            weekly_progress=weekly_progress,
            monthly_summary=monthly_summary
        )
        
        return self.assistant.generate_comprehensive_analysis(context)
    
    def quick_summary(
        self,
        user_profile: UserProfile,
        current_report: HealthReport,
        previous_report: Optional[HealthReport] = None
    ) -> str:
        """
        Generate a quick summary.
        
        Args:
            user_profile: User profile
            current_report: Current health report
            previous_report: Previous health report (optional)
            
        Returns:
            Quick summary string
        """
        context = AnalysisContext(
            user_profile=user_profile,
            current_report=current_report,
            previous_report=previous_report,
            weekly_progress=None,
            monthly_summary=None
        )
        
        return self.assistant.generate_quick_summary(context)
    
    def analyze_from_dict(self, data: Dict[str, Any]) -> str:
        """
        Analyze health data from a dictionary.
        
        Args:
            data: Dictionary containing:
                - user: {age, diabetes_type, height_cm, weight_kg, name?}
                - current_report: {fbs, ppbs, hba1c, test_date, notes?}
                - previous_report?: {fbs, ppbs, hba1c, test_date, notes?}
                - weekly_progress?: {week_start_date, daily_readings: [...]}
                
        Returns:
            Complete formatted analysis report
        """
        # Create user profile
        user_data = data['user']
        user_profile = self.create_user_profile(
            age=user_data['age'],
            diabetes_type=user_data['diabetes_type'],
            height_cm=user_data['height_cm'],
            weight_kg=user_data['weight_kg'],
            name=user_data.get('name')
        )
        
        # Create current report
        current_data = data['current_report']
        current_report = self.create_health_report(
            fbs=current_data['fbs'],
            ppbs=current_data['ppbs'],
            hba1c=current_data['hba1c'],
            test_date=date.fromisoformat(current_data['test_date']) if isinstance(current_data['test_date'], str) else current_data['test_date'],
            notes=current_data.get('notes')
        )
        
        # Create previous report if provided
        previous_report = None
        if 'previous_report' in data:
            prev_data = data['previous_report']
            previous_report = self.create_health_report(
                fbs=prev_data['fbs'],
                ppbs=prev_data['ppbs'],
                hba1c=prev_data['hba1c'],
                test_date=date.fromisoformat(prev_data['test_date']) if isinstance(prev_data['test_date'], str) else prev_data['test_date'],
                notes=prev_data.get('notes')
            )
        
        # Create weekly progress if provided
        weekly_progress = None
        if 'weekly_progress' in data:
            week_data = data['weekly_progress']
            weekly_progress = self.create_weekly_progress(
                week_start_date=date.fromisoformat(week_data['week_start_date']) if isinstance(week_data['week_start_date'], str) else week_data['week_start_date'],
                daily_readings=week_data['daily_readings']
            )
        
        # Generate analysis
        return self.analyze(
            user_profile=user_profile,
            current_report=current_report,
            previous_report=previous_report,
            weekly_progress=weekly_progress
        )
    
    def analyze_structured_from_dict(self, data: Dict[str, Any]) -> dict:
        """
        Analyze health data from a dictionary and return structured sections.
        """
        # Create user profile
        user_data = data['user']
        user_profile = self.create_user_profile(
            age=user_data['age'],
            diabetes_type=user_data['diabetes_type'],
            height_cm=user_data['height_cm'],
            weight_kg=user_data['weight_kg'],
            name=user_data.get('name')
        )
        
        # Create current report
        current_data = data['current_report']
        current_report = self.create_health_report(
            fbs=current_data['fbs'],
            ppbs=current_data['ppbs'],
            hba1c=current_data['hba1c'],
            test_date=date.fromisoformat(current_data['test_date']) if isinstance(current_data['test_date'], str) else current_data['test_date'],
            notes=current_data.get('notes')
        )
        
        # Create previous report if provided
        previous_report = None
        if 'previous_report' in data:
            prev_data = data['previous_report']
            previous_report = self.create_health_report(
                fbs=prev_data['fbs'],
                ppbs=prev_data['ppbs'],
                hba1c=prev_data['hba1c'],
                test_date=date.fromisoformat(prev_data['test_date']) if isinstance(prev_data['test_date'], str) else prev_data['test_date'],
                notes=prev_data.get('notes')
            )
        
        # Create weekly progress if provided
        weekly_progress = None
        if 'weekly_progress' in data:
            week_data = data['weekly_progress']
            weekly_progress = self.create_weekly_progress(
                week_start_date=date.fromisoformat(week_data['week_start_date']) if isinstance(week_data['week_start_date'], str) else week_data['week_start_date'],
                daily_readings=week_data['daily_readings']
            )
        
        context = AnalysisContext(
            user_profile=user_profile,
            current_report=current_report,
            previous_report=previous_report,
            weekly_progress=weekly_progress,
            monthly_summary=None
        )
        
        return self.assistant.generate_structured_analysis(context)
    
    def get_health_summary(self, data: Dict[str, Any]) -> str:
        """
        Get only the health summary section from a dictionary.
        """
        # Create user profile
        user_data = data['user']
        user_profile = self.create_user_profile(
            age=user_data['age'],
            diabetes_type=user_data['diabetes_type'],
            height_cm=user_data['height_cm'],
            weight_kg=user_data['weight_kg'],
            name=user_data.get('name')
        )
        
        # Create current report
        current_data = data['current_report']
        current_report = self.create_health_report(
            fbs=current_data['fbs'],
            ppbs=current_data['ppbs'],
            hba1c=current_data['hba1c'],
            test_date=date.fromisoformat(current_data['test_date']) if isinstance(current_data['test_date'], str) else current_data['test_date'],
            notes=current_data.get('notes')
        )
        
        # Create previous report if provided
        previous_report = None
        if 'previous_report' in data:
            prev_data = data['previous_report']
            previous_report = self.create_health_report(
                fbs=prev_data['fbs'],
                ppbs=prev_data['ppbs'],
                hba1c=prev_data['hba1c'],
                test_date=date.fromisoformat(prev_data['test_date']) if isinstance(prev_data['test_date'], str) else prev_data['test_date'],
                notes=prev_data.get('notes')
            )
            
        context = AnalysisContext(
            user_profile=user_profile,
            current_report=current_report,
            previous_report=previous_report,
            weekly_progress=None,
            monthly_summary=None
        )
        
        return self.assistant.get_health_summary_only(context)


# Example usage
if __name__ == "__main__":
    api = GlucoBalanceAPI()
    
    # Example: Create analysis from dictionary
    example_data = {
        "user": {
            "age": 45,
            "diabetes_type": "TYPE_2",
            "height_cm": 170,
            "weight_kg": 75,
            "name": "John Doe"
        },
        "current_report": {
            "fbs": 135.0,
            "ppbs": 185.0,
            "hba1c": 7.2,
            "test_date": "2026-02-09"
        },
        "previous_report": {
            "fbs": 145.0,
            "ppbs": 195.0,
            "hba1c": 7.5,
            "test_date": "2026-01-10"
        }
    }
    
    report = api.analyze_from_dict(example_data)
    
    print("API Example - Analysis Generated:")
    print("=" * 70)
    print(report[:500] + "...")  # Print first 500 characters
    print("\n... (truncated)")
