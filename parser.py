"""Functions for parsing raw measurement data from the scale."""

from typing import Dict, Any
from calculations import calculate_bmi, calculate_bmr, estimate_body_fat_percentage
from config import AGE, HEIGHT_CM, GENDER


def parse_measurement_data(raw_data: bytearray,
                          age: int = AGE,
                          height_cm: float = HEIGHT_CM,
                          gender: str = GENDER) -> Dict[str, Any]:
    """Parse raw measurement data and return a dictionary with all calculated values."""
    weight = ((raw_data[12] << 8) + raw_data[11]) / 200
    impedance = (raw_data[10] << 8) + raw_data[9]

    bmi = calculate_bmi(weight, height_cm)
    bmr = calculate_bmr(weight, height_cm, age, gender)
    body_fat = estimate_body_fat_percentage(bmi, age, gender)

    return {
        'weight': weight,
        'impedance': impedance,
        'bmi': bmi,
        'bmr': bmr,
        'body_fat': body_fat,
        'age': age,
        'height_cm': height_cm,
        'gender': gender
    }

