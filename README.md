# 🥗 NutriSense AI Agents

Sistema de agentes de inteligencia artificial para nutrición personalizada y análisis alimentario.

## 📋 Descripción del Proyecto

NutriSense AI Agents es una plataforma modular que combina servicios de IA especializados y agentes inteligentes para proporcionar análisis nutricional avanzado, generación de planes alimentarios personalizados y monitoreo inteligente de la alimentación.

### 🎯 Arquitectura del Sistema

El proyecto está estructurado en **dos grupos principales** de funcionalidades de IA:

#### 🔧 **Servicios**

Funcionalidades directas que reciben un input, tienen contexto integrado en el prompt, y devuelven respuestas formateadas:

1. **Generador de plan nutricional** - Basado en cuestionario del usuario
2. **Generador de ficha de usuario** - Primera vez que entra el usuario
3. **Extractor de ingredientes** - Análisis de imágenes de comida
4. **Extractor de macronutrientes** - Análisis nutricional de ingredientes ✅ **IMPLEMENTADO**

#### 🤖 **Agentes**

Agentes inteligentes que toman decisiones, modifican registros en BD y envían mensajes:

- **Agente Central Nutricional** - Con acceso completo a datos de BD para modificar planes, añadir/quitar comidas, etc.

## 🏗️ Estructura del Proyecto

```
NutriSense-AI-Agents/
├── nutrisense_agents/                 # Paquete principal
│   ├── ai_companion/                  # Módulo de IA
│   │   ├── agents/                    # Agentes de IA
│   │   │   ├── example_agent.py       # Agente de ejemplo
│   │   │   └── macronutrient_agent.py # Agente extractor de macronutrientes
│   │   ├── schemas/                   # Esquemas Pydantic
│   │   │   ├── example_schema.py      # Esquema de ejemplo
│   │   │   └── macronutrient_schema.py # Esquemas nutricionales
│   │   ├── prompts/                   # Prompts especializados
│   │   │   ├── example_prompt.py      # Prompt de ejemplo
│   │   │   └── macronutrient_prompt.py # Prompt nutricional
│   │   └── graphs/                    # Grafos LangGraph
│   │       └── script_graph/          # Grafo de scripts
│   ├── api/                          # API y servicios
│   │   ├── services/                 # Servicios de IA
│   │   │   ├── example_service.py    # Servicio de ejemplo
│   │   │   ├── macronutrient_service.py # ✅ Servicio macronutrientes
│   │   │   └── ejemplo_macronutrientes.py # Ejemplos de uso
│   │   ├── routes/                   # Rutas de API
│   │   └── models/                   # Modelos de API
│   ├── config/                       # Configuración
│   │   ├── settings.py               # Configuración general
│   │   ├── agent_config.py           # Configuración de agentes
│   │   └── supabase_settings.py      # Configuración de Supabase
│   ├── db/                          # Base de datos
│   │   └── supabase/                # Integración con Supabase
│   ├── data_pipeline/               # Pipeline de datos
│   ├── events/                      # Sistema de eventos
│   ├── utils/                       # Utilidades
│   └── tests/                       # Tests
└── requirements.txt                 # Dependencias del proyecto
```

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recomendado) o pip
- Cuenta de OpenAI o Anthropic para los modelos de IA
- Proyecto de Supabase configurado (para servicios con BD)

### Instalación

1. **Clonar el repositorio**

```bash
git clone https://github.com/tu-usuario/NutriSense-AI-Agents.git
cd NutriSense-AI-Agents
```

2. **Instalar con uv (Recomendado) 🚀**

```bash
# Instalar uv si no lo tienes
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sincronizar dependencias y crear entorno virtual automáticamente
uv sync

# Activar el entorno virtual
source .venv/bin/activate  # En macOS/Linux
# o
.venv\Scripts\activate     # En Windows
```

> **Nota**: Si ya tienes un entorno virtual activado (como `venv`), desactívalo primero con `deactivate` antes de ejecutar `uv sync`, o usa `uv sync --active` para sincronizar en el entorno activo.

**Alternativamente, instalación con pip:**

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En macOS/Linux
# o
venv\Scripts\activate     # En Windows

# Instalar dependencias
pip install -r requirements.txt
```

3. **Configurar variables de entorno**

```bash
cp .env.example .env
# Editar .env con tus API keys
```

### Configuración de Variables de Entorno

```bash
# Modelos de IA
OPENAI_API_KEY=tu_openai_api_key
OPENAI_MODEL=gpt-4-turbo
ANTHROPIC_API_KEY=tu_anthropic_api_key
ANTHROPIC_MODEL=claude-3-sonnet

# Supabase (para servicios con BD)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu_anon_key
SUPABASE_SERVICE_ROLE_KEY=tu_service_role_key
```

### Troubleshooting

#### Error: "Unable to determine which files to ship inside the wheel"

Si encuentras este error al ejecutar `uv sync`, significa que hay un problema con la configuración del paquete:

```bash
# Solución: Elimina entornos virtuales existentes y empieza desde cero
deactivate  # Si tienes un entorno activo
rm -rf venv .venv  # Eliminar entornos virtuales anteriores
uv sync  # Crear nuevo entorno desde cero
```

#### Error: "VIRTUAL_ENV does not match the project environment path"

Este warning aparece cuando tienes un entorno virtual manual activado:

```bash
# Opción 1: Desactivar el entorno manual
deactivate
uv sync

# Opción 2: Usar el entorno activo
uv sync --active
```

### Comandos Útiles con uv

```bash
# Ejecutar comandos en el entorno virtual (sin activar manualmente)
uv run python -m nutrisense_agents.api.services.example_service

# Agregar nuevas dependencias
uv add nueva-dependencia

# Agregar dependencias de desarrollo
uv add --dev pytest black flake8

# Actualizar todas las dependencias
uv sync --upgrade

# Ejecutar scripts directamente
uv run python script.py

# Crear shell en el entorno virtual
uv shell
```

## 🧪 Pruebas y Ejemplos

### Servicio de Ejemplo

```bash
# Con uv (recomendado)
uv run python -m nutrisense_agents.api.services.example_service

# Con pip tradicional
python -m nutrisense_agents.api.services.example_service
```

### Servicio de Macronutrientes (Implementado)

```bash
# Prueba básica
uv run python -m nutrisense_agents.api.services.macronutrient_service
# o
python -m nutrisense_agents.api.services.macronutrient_service

# Ejemplos completos
uv run python -m nutrisense_agents.api.services.ejemplo_macronutrientes
# o
python -m nutrisense_agents.api.services.ejemplo_macronutrientes
```

## 📖 Servicios Implementados

### ✅ Servicio 4: Extractor de Macronutrientes

**Descripción**: Analiza una lista de ingredientes verificados y extrae información nutricional completa.

**Funcionalidades**:

- Extracción de macronutrientes por 100g
- Cálculo de cantidades consumidas
- Inserción automática en base de datos
- Análisis de fotos de comida (opcional)
- Manejo inteligente de errores

**Uso**:

```python
from nutrisense_agents.api.services.macronutrient_service import extract_macronutrients_service

result = extract_macronutrients_service(
    ingredients=["100g pechuga de pollo", "150g arroz integral"],
    user_id="user_123",
    meal_type="almuerzo",
    photo_url="https://ejemplo.com/foto.jpg"
)
```

**Documentación completa**: [README del servicio](nutrisense_agents/api/services/README_macronutrient_service.md)

## 🌐 API REST

### Servidor FastAPI

```bash
# Iniciar el servidor de desarrollo
uvicorn nutrisense_agents.main:app --reload --port 8001

# El servidor estará disponible en:
# - API: http://127.0.0.1:8001
# - Documentación Swagger: http://127.0.0.1:8001/docs
# - Documentación ReDoc: http://127.0.0.1:8001/redoc
```

### ✅ Endpoint: Extractor de Macronutrientes

**POST** `/api/macronutrients`

- Análisis completo con guardado en base de datos
- Requiere configuración de Supabase

**POST** `/api/macronutrients/local`

- Modo de prueba local (sin base de datos)
- Ideal para desarrollo y testing

**Ejemplo de uso:**

```bash
curl -X POST "http://127.0.0.1:8001/api/macronutrients/local" \
-H "Content-Type: application/json" \
-d '{
  "ingredients": ["100g pechuga de pollo", "150g arroz blanco cocido", "50g brócoli"],
  "user_id": "test_user_123",
  "meal_type": "almuerzo",
  "preparation_method": "cocido",
  "portion_size": "porción mediana",
  "additional_notes": "comida casera sin aceite adicional"
}'
```

**Respuesta de ejemplo:**

```json
{
  "success": true,
  "mode": "LOCAL_TEST",
  "extracted_macronutrients": [
    {
      "name": "Pechuga de pollo",
      "calories_per_100g": 165.0,
      "protein_per_100g": 31.0,
      "carbs_per_100g": 0.0,
      "fat_per_100g": 3.6,
      "estimated_quantity_grams": 100.0,
      "total_calories": 165.0,
      "total_protein": 31.0,
      "confidence_score": 0.95
    }
  ],
  "total_nutrition": {
    "calories": 377.0,
    "protein": 36.45,
    "carbs": 45.6,
    "fat": 4.25
  }
}
```

## 🛠️ Tecnologías Utilizadas

- **🐍 Python 3.12+** - Lenguaje principal
- **🦜 LangChain** - Framework para aplicaciones de IA
- **🤖 OpenAI GPT / Anthropic Claude** - Modelos de lenguaje
- **📊 Pydantic** - Validación y serialización de datos
- **🗄️ Supabase** - Base de datos y backend
- **⚡ FastAPI** - API web (preparado para implementar)
- **🧪 pytest** - Testing (preparado para implementar)

## 🏗️ Desarrollo

### Añadir un Nuevo Servicio

1. **Crear el esquema** en `ai_companion/schemas/`
2. **Definir el prompt** en `ai_companion/prompts/`
3. **Implementar el agente** en `ai_companion/agents/`
4. **Crear el servicio** en `api/services/`
5. **Añadir tests** en `tests/`

### Ejemplo de Estructura para Nuevo Servicio:

```python
# schemas/mi_servicio_schema.py
class MiServicio(BaseModel):
    resultado: str = Field(description="Resultado del servicio")

# prompts/mi_servicio_prompt.py
MI_PROMPT = "Eres un experto en..."

# agents/mi_servicio_agent.py
def get_mi_servicio_chain():
    # Implementación del agente
    pass

# services/mi_servicio_service.py
def mi_servicio(input_data):
    # Lógica del servicio
    pass
```

## 📝 Estado del Proyecto

### ✅ Implementado

- [x] Estructura base del proyecto
- [x] Configuración de modelos de IA (OpenAI/Anthropic)
- [x] Servicio de ejemplo funcional
- [x] **Servicio 4: Extractor de macronutrientes**
- [x] **API REST para macronutrientes (FastAPI)**
- [x] Integración con Supabase
- [x] Sistema de esquemas Pydantic
- [x] Configuración modular

### 🚧 En Desarrollo

- [ ] Servicio 1: Generador de plan nutricional
- [ ] Servicio 2: Generador de ficha de usuario
- [ ] Servicio 3: Extractor de ingredientes
- [ ] Agente central nutricional
- [ ] Tests automatizados

### 🔮 Futuro

- [ ] Interface web
- [ ] Aplicación móvil
- [ ] Integración con wearables
- [ ] Machine Learning personalizado
- [ ] Sistema de notificaciones

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Añade nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Equipo

- **Desarrollador Principal**: [Tu Nombre]
- **Arquitecto de IA**: [Nombre]
- **Especialista en Nutrición**: [Nombre]

## 📞 Contacto

- **Email**: contacto@nutrisense.ai
- **Website**: https://nutrisense.ai
- **Discord**: [Servidor de la Comunidad]

---

<div align="center">
<strong>🥗 NutriSense AI Agents - Revolucionando la nutrición con inteligencia artificial</strong>
</div>
