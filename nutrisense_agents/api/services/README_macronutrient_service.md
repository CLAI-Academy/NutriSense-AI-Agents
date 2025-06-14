# Servicio de Extracción de Macronutrientes

Este servicio implementa la funcionalidad número 4 del sistema NutriSense: **Extractor de macronutrientes en base a ingredientes**.

## Descripción

El servicio recibe una lista de ingredientes (previamente verificados por el usuario del servicio 3) y:

1. Extrae información nutricional detallada de cada ingrediente
2. Calcula macronutrientes totales de la comida
3. Inserta los datos en las tablas de la base de datos:
   - `ingredients` - Información nutricional de cada ingrediente
   - `food_diary` - Entrada del diario alimentario del usuario
   - `food_photo_analysis` - Análisis de la foto si está disponible

## 🚀 Inicio Rápido

### Prueba Local (Sin Base de Datos)

1. **Configurar API Key**

   ```bash
   cp .env.example .env
   # Editar .env con tu OPENAI_API_KEY
   ```

2. **Ejecutar prueba simple**

   ```bash
   uv run python -m nutrisense_agents.api.services.test_local_macronutrients
   ```

3. **Ver resultados** del análisis nutricional con IA

### Modo Completo (Con Base de Datos)

1. **Configurar Supabase** en `.env`
2. **Crear tablas** con el script SQL incluido
3. **Ejecutar con BD**
   ```bash
   uv run python -m nutrisense_agents.api.services.ejemplo_macronutrientes --full
   ```

## Estructura de archivos

```
nutrisense_agents/
├── ai_companion/
│   ├── schemas/
│   │   └── macronutrient_schema.py     # Esquemas Pydantic para la extracción
│   ├── prompts/
│   │   └── macronutrient_prompt.py     # Prompt especializado en análisis nutricional
│   └── agents/
│       └── macronutrient_agent.py      # Agente que procesa los ingredientes
├── api/
│   └── services/
│       ├── macronutrient_service.py    # Servicio principal con lógica de BD
│       ├── ejemplo_macronutrientes.py  # Script de ejemplos de uso
│       └── test_local_macronutrients.py # Prueba local simple (sin BD)
├── db/
│   └── supabase/
│       ├── client.py                   # Cliente de Supabase configurado
│       └── create_tables.sql           # Script SQL para crear tablas
└── config/
    ├── settings.py                     # Configuración general (actualizada)
    └── supabase_settings.py            # Configuración específica de Supabase
```

## Uso del servicio

### Importación básica

```python
from nutrisense_agents.api.services.macronutrient_service import extract_macronutrients_service

# Ejemplo de uso
result = extract_macronutrients_service(
    ingredients=[
        "100g de pechuga de pollo a la plancha",
        "150g de arroz integral cocido",
        "80g de brócoli al vapor"
    ],
    user_id="user_123",
    meal_type="almuerzo",
    preparation_method="a la plancha y al vapor",
    portion_size="porción mediana",
    photo_url="https://example.com/photo.jpg",  # Opcional
    additional_notes="Comida post-entreno"
)
```

### Parámetros de entrada

- `ingredients` (List[str]): Lista de ingredientes verificados por el usuario
- `user_id` (str): ID del usuario en el sistema
- `meal_type` (str): Tipo de comida (desayuno, almuerzo, cena, snack)
- `preparation_method` (str): Método de preparación de los alimentos
- `portion_size` (str): Descripción del tamaño de la porción
- `photo_url` (Optional[str]): URL de la foto analizada
- `additional_notes` (str): Notas adicionales del usuario

### Respuesta del servicio

```python
{
    "success": True,
    "food_diary_id": "uuid-string",
    "photo_analysis_id": "uuid-string",  # Si se proporcionó foto
    "ingredient_ids": ["uuid1", "uuid2", "uuid3"],
    "extracted_macronutrients": [
        {
            "name": "Pechuga de pollo",
            "calories_per_100g": 165,
            "protein_per_100g": 31,
            "carbs_per_100g": 0,
            "fat_per_100g": 3.6,
            "estimated_quantity_grams": 100,
            "total_calories": 165,
            "total_protein": 31,
            "total_carbs": 0,
            "total_fat": 3.6,
            "confidence_score": 0.95
        },
        # ... más ingredientes
    ],
    "total_nutrition": {
        "calories": 425,
        "protein": 45,
        "carbs": 55,
        "fat": 8,
        "fiber": 6,
        "sugar": 2,
        "sodium": 150
    },
    "message": "Se procesaron exitosamente 3 ingredientes"
}
```

## Configuración

### Variables de entorno

La configuración requerida depende del modo de uso:

#### 🧪 Para Modo LOCAL (solo IA, sin BD)

```bash
# Solo necesitas configuración de IA
OPENAI_API_KEY=tu_openai_api_key
OPENAI_MODEL=gpt-4-turbo

# O alternativamente Anthropic
ANTHROPIC_API_KEY=tu_anthropic_api_key
ANTHROPIC_MODEL=claude-3-sonnet
```

#### 🔗 Para Modo COMPLETO (IA + Base de Datos)

```bash
# Configuración de IA (requerida)
OPENAI_API_KEY=tu_openai_api_key
OPENAI_MODEL=gpt-4-turbo

# Configuración de Supabase (requerida para modo completo)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu_anon_key
SUPABASE_SERVICE_ROLE_KEY=tu_service_role_key
```

**💡 Tip**: Empieza con solo las variables de IA para hacer pruebas locales, y añade Supabase cuando estés listo para la integración completa.

### Tablas de base de datos (Solo para Modo Completo)

El servicio espera que existan las siguientes tablas en Supabase. Puedes crearlas ejecutando el script SQL proporcionado:

```sql
-- Ejecutar en Supabase SQL Editor
\i nutrisense_agents/db/supabase/create_tables.sql
```

O copiar y pegar el contenido del archivo `create_tables.sql` en el SQL Editor de Supabase.

**Tablas creadas:**

1. **ingredients**

   - id (uuid, primary key)
   - name (text)
   - description (text, nullable)
   - brand (text, nullable)
   - calories_per_100g (numeric)
   - protein_per_100g (numeric)
   - carbs_per_100g (numeric)
   - fat_per_100g (numeric)
   - fiber_per_100g (numeric, nullable)
   - sugar_per_100g (numeric, nullable)
   - sodium_per_100g (numeric, nullable)
   - category (text, nullable)
   - preparation_method (text, nullable)
   - confidence_score (numeric)
   - created_at (timestamp)

2. **food_diary**

   - id (uuid, primary key)
   - user_id (text)
   - meal_type (text)
   - consumed_at (timestamp)
   - total_calories (numeric)
   - total_protein (numeric)
   - total_carbs (numeric)
   - total_fat (numeric)
   - total_fiber (numeric, nullable)
   - total_sugar (numeric, nullable)
   - total_sodium (numeric, nullable)
   - notes (text, nullable)
   - created_at (timestamp)

3. **food_photo_analysis**

   - id (uuid, primary key)
   - food_diary_id (uuid, foreign key)
   - photo_url (text)
   - analysis_confidence (numeric)
   - detected_foods (text[])
   - analysis_notes (text, nullable)
   - created_at (timestamp)

4. **food_diary_ingredients** (tabla de relación)
   - food_diary_id (uuid, foreign key)
   - ingredient_id (uuid, foreign key)
   - quantity_grams (numeric)
   - calories_consumed (numeric)
   - protein_consumed (numeric)
   - carbs_consumed (numeric)
   - fat_consumed (numeric)
   - created_at (timestamp)

## Pruebas

El servicio ofrece múltiples opciones de prueba según tu entorno y necesidades:

### 🧪 Modo LOCAL (Sin Base de Datos)

**Ideal para:**

- Desarrollo inicial
- Pruebas de IA sin configuración de BD
- Validación de funcionalidad básica

#### Opción 1: Prueba Simple y Rápida

```bash
# Con uv
uv run python -m nutrisense_agents.api.services.test_local_macronutrients

# Con pip tradicional
python -m nutrisense_agents.api.services.test_local_macronutrients
```

- ✅ Más fácil de usar
- ✅ Análisis directo sin configuración extra
- ✅ Output limpio y organizado

#### Opción 2: Servicio Principal (Modo Local)

```bash
# Con uv
uv run python -m nutrisense_agents.api.services.macronutrient_service

# Con pip tradicional
python -m nutrisense_agents.api.services.macronutrient_service
```

- ✅ Prueba la función principal pero en modo local
- ✅ Misma lógica que usarás en producción
- ✅ Output detallado paso a paso

#### Opción 3: Ejemplos Completos (Modo Local)

```bash
# Modo local por defecto (sin BD)
uv run python -m nutrisense_agents.api.services.ejemplo_macronutrientes

# Con pip tradicional
python -m nutrisense_agents.api.services.ejemplo_macronutrientes
```

- ✅ Múltiples ejemplos de uso
- ✅ Formato visual atractivo
- ✅ Solo requiere API keys configuradas

### 🔗 Modo COMPLETO (Con Base de Datos)

**Ideal para:**

- Pruebas de integración
- Validación completa del flujo
- Ambiente de producción

#### Opción 1: Ejemplos Completos (Modo BD)

```bash
# Modo completo con base de datos
uv run python -m nutrisense_agents.api.services.ejemplo_macronutrientes --full

# Con pip tradicional
python -m nutrisense_agents.api.services.ejemplo_macronutrientes --full
```

#### Opción 2: Usando la función principal directamente

```python
from nutrisense_agents.api.services.macronutrient_service import extract_macronutrients_service

result = extract_macronutrients_service(
    ingredients=["100g pollo", "150g arroz"],
    user_id="test_user",
    meal_type="almuerzo"
)
```

### 📋 Requisitos por Modo

| Modo        | API Keys     | Supabase        | Descripción               |
| ----------- | ------------ | --------------- | ------------------------- |
| 🧪 LOCAL    | ✅ Requerido | ❌ No necesario | Solo análisis de IA       |
| 🔗 COMPLETO | ✅ Requerido | ✅ Requerido    | Análisis + guardado en BD |

### 🎯 Recomendación de Prueba

1. **Empezar con modo LOCAL** para validar funcionalidad básica:

   ```bash
   uv run python -m nutrisense_agents.api.services.test_local_macronutrients
   ```

2. **Configurar Supabase** cuando esté listo para integración completa

3. **Cambiar a modo COMPLETO** para pruebas finales:
   ```bash
   uv run python -m nutrisense_agents.api.services.ejemplo_macronutrientes --full
   ```

## Consideraciones técnicas

1. **Nueva dependencia**: Se agregó `supabase==2.6.0` al archivo `requirements.txt` para la conexión con la base de datos.

2. **Precisión nutricional**: El agente utiliza bases de datos nutricionales estándar (USDA, tablas españolas) para obtener valores precisos.

3. **Manejo de errores**: El servicio maneja errores graciosamente y continúa procesando ingredientes incluso si uno falla.

4. **Optimización de BD**: Verifica si los ingredientes ya existen antes de insertar nuevos registros.

5. **Confianza del análisis**: Cada extracción incluye un score de confianza basado en la precisión de los datos nutricionales.

6. **Flexibilidad**: Acepta descripciones de ingredientes con cantidades, métodos de preparación y contexto.

## Integración con otros servicios

Este servicio está diseñado para integrarse con:

- **Servicio 3**: Recibe la lista de ingredientes verificados
- **Frontend**: Utiliza la API de Supabase directamente para consultas
- **Servicio de agentes**: Proporcionará datos para modificaciones del plan nutricional
