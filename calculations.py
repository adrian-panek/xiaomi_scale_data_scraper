"""Functions for calculating BMI, BMR, and body fat percentage."""

def calculate_bmi(weight: float, height_cm: float) -> float:
    """Calculate Body Mass Index (BMI)."""
    height_m = height_cm / 100
    return weight / (height_m * height_m)


def calculate_bmr(weight: float, height_cm: float, age: int, gender: str) -> float:
    """Calculate Basal Metabolic Rate (BMR) using the Mifflin-St Jeor equation."""
    if gender.lower() == 'male':
        return 10 * weight + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height_cm - 5 * age - 161


def estimate_body_fat_percentage(bmi: float, age: int, gender: str) -> float:
    """
    Estimate body fat percentage using the Deurenberg formula.
    
    Formula:
    - Male: BFP = 1.20 × BMI + 0.23 × Age - 16.2
    - Female: BFP = 1.20 × BMI + 0.23 × Age - 5.4
    
    Note: This is an estimation. For more accurate results, consider using
    bioelectrical impedance analysis (BIA) with the impedance value from the scale.
    """
    if gender.lower() == 'male':
        return 1.20 * bmi + 0.23 * age - 16.2
    else:
        return 1.20 * bmi + 0.23 * age - 5.4

