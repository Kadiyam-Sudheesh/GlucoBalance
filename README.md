# GlucoCare - Intelligent Diabetes Management System 🩸

GlucoCare is a comprehensive web application designed to help individuals with diabetes manage their condition effectively. It goes beyond simple tracking by offering intelligent insights, emergency features, and comprehensive reporting.

## 🚀 Key Features

### 1. **Smart Dashboard** 📊
- Visualizes blood glucose trends (Fasting & Post-Prandial).
- Displays calculated **Estimated HbA1c** based on 90-day history.
- Highlights recent activity and alerts.

### 2. **Food Logger with Traffic Light System** 🍎
- Log meals with a visual **Glycemic Impact** selector:
    - 🟢 **Low Impact**: Veggies, Proteins, Nuts.
    - 🟡 **Medium Impact**: Fruits, Whole Grains.
    - 🔴 **High Impact**: Sweets, White Bread, Pasta.
- Visual **Portion Size** cards (Small, Medium, Large).
- Tracks meal history with color-coded entries.

### 3. **Emergency Mode** 🚨
- Dedicated "I FEEL LOW" button for hypoglycemia emergencies.
- Step-by-step guidance (Sugar intake -> Wait 15 mins -> Retest).
- **One-Tap Emergency Actions**:
    - 📞 **Call**: Immediately dial emergency contacts.
    - 💬 **SMS**: Send a pre-filled distress message with location details (if applicable).
    - 📱 **WhatsApp**: Send a pre-filled WhatsApp message: *"I am feeling low (Hypoglycemia). Please help!"*

### 4. **Reports & exports** 📄
- **PDF Report Generation**: Download comprehensive health reports for doctor visits.
- **Data Analysis**: View weekly progress and averages.

### 5. **Medication Tracking** 💊
- Log insulin and medication intake.
- Track adherence history.

## 🛠️ Technology Stack

- **Backend**: Python (Flask)
- **Database**: SQLite (via SQLAlchemy)
- **Frontend**: HTML5, CSS3 (Tailwind-inspired utility classes), JavaScript
- **Visualization**: Chart.js
- **PDF Generation**: ReportLab

## 📦 Installation & Setup

1.  **Clone the Repository** (if applicable) or download source code.
2.  **Install Dependencies**:
    ```bash
    pip install flask flask-sqlalchemy reportlab
    ```
3.  **Run the Application**:
    ```bash
    python app.py
    ```
4.  **Access the App**:
    Open your browser and navigate to `http://127.0.0.1:5000`.

## 🧪 Verification & Testing

The project includes several verification scripts to ensure core logic integrity:
- `verify_hba1c.py`: Validates the HbA1c estimation formula.
- `verify_food_log.py`: Tests the food logging backend.
- `verify_pdf.py`: Checks PDF report generation.

## 📝 Usage Guide

1.  **Sign Up/Login**: Create an account to start tracking.
2.  **Dashboard**: View your current stats and estimated HbA1c.
3.  **Add Report**: Log your daily Fasting (FBS) and Post-Prandial (PPBS) readings.
4.  **Food Log**: Track what you eat to understand its impact.
5.  **Emergency**: Use the top-right "I FEEL LOW" button in case of hypoglycemia.

---
*Built with ❤️ for better health management.*
