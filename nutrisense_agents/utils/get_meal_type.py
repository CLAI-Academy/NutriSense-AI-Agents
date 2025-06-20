from datetime import datetime
from typing import Literal


def get_type_meal() -> Literal['desayuno', 'almuerzo', 'cena', 'snack']:
    """
    Determina qué comida corresponde según la hora actual del día.
    
    Returns:
        str: Uno de los siguientes valores según el tramo horario:
            - 'desayuno': de 6:00 AM a 11:59 AM
            - 'almuerzo': de 12:00 PM a 4:59 PM  
            - 'cena': de 5:00 PM a 9:59 PM
            - 'snack': de 10:00 PM a 5:59 AM
    
    Example:
        >>> get_type_meal()
        'desayuno'  # si son las 8:30 AM
    """
    # Obtener la hora actual del sistema
    current_time = datetime.now()
    current_hour = current_time.hour
    
    # Evaluar en qué tramo horario se encuentra
    if 6 <= current_hour <= 11:
        return 'desayuno'
    elif 12 <= current_hour <= 16:
        return 'almuerzo'
    elif 17 <= current_hour <= 23:
        return 'cena'
    else:
        # Caso especial: de 22:00 (10 PM) a 5:59 AM
        return 'snack'


def get_type_meal_with_time(hour: int) -> Literal['desayuno', 'almuerzo', 'cena', 'snack']:
    """
    Versión alternativa que permite especificar una hora específica para testing.
    
    Args:
        hour (int): Hora del día (0-23)
        
    Returns:
        str: Tipo de comida correspondiente
        
    Raises:
        ValueError: Si la hora no está en el rango válido (0-23)
    """
    if not 0 <= hour <= 23:
        raise ValueError("La hora debe estar entre 0 y 23")
    
    if 6 <= hour <= 11:
        return 'desayuno'
    elif 12 <= hour <= 16:
        return 'almuerzo'
    elif 17 <= hour <= 22:
        return 'cena'
    else:
        return 'snack'


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo con la hora actual
    current_meal = get_type_meal()
    print(f"Comida actual: {current_meal}")
    
    # Ejemplos con horas específicas
    test_hours = [6, 12, 18, 23, 2]
    for hour in test_hours:
        meal_type = get_type_meal_with_time(hour)
        print(f"Hora {hour:02d}:00 -> {meal_type}")
