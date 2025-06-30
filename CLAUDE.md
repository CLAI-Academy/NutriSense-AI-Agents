# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Package Management
This project uses **UV** as the preferred package manager (faster than pip):
```bash
uv sync                    # Install dependencies and create virtual environment
uv run <command>          # Run commands in virtual environment context
uv add <package>          # Add new dependencies
```

### Development and Testing
```bash
# Start FastAPI server
python -m nutrisense_agents.main
# or
uvicorn nutrisense_agents.main:app --host 0.0.0.0 --port 8080

# Test individual services
uv run python -m nutrisense_agents.api.services.macronutrient_service
uv run python -m nutrisense_agents.api.services.react_agent_service
uv run python -m nutrisense_agents.api.services.example_service

# Run specific examples
uv run python -m nutrisense_agents.api.services.ejemplo_macronutrientes
```

## Architecture

### High-Level Structure
This is an AI-powered nutrition platform using a **two-tier architecture**:
- **Services**: Direct input/output functions with integrated context
- **Agents**: Intelligent decision-making entities with database access

### Tech Stack
- **Python 3.12+** with **FastAPI** for REST API
- **LangChain/LangGraph** for AI agent orchestration
- **Supabase** for database and authentication
- **OpenAI GPT-4, Anthropic Claude, Groq** for AI models
- **Pydantic** for data validation and serialization
- **MCP (Model Context Protocol)** for tool integrations

### Main Package Structure
```
nutrisense_agents/
├── ai_companion/          # AI-specific modules
│   ├── agents/           # AI agents (ReAct, macronutrient, nutrition plan)
│   ├── schemas/          # Pydantic data models
│   ├── prompts/          # Specialized prompts for different tasks
│   ├── graphs/           # LangGraph workflow definitions
│   └── MCPs/             # Model Context Protocol integrations
├── api/                  # REST API layer
│   ├── routes/           # API endpoints
│   ├── services/         # Business logic services
│   └── models/           # API data models
├── config/               # Configuration management
├── db/supabase/         # Database integration
└── utils/               # Shared utilities
```

### Service Development Pattern
When creating new services, follow the established pattern:
1. Define Pydantic schemas in `ai_companion/schemas/`
2. Create prompts in `ai_companion/prompts/`
3. Implement agents in `ai_companion/agents/` if decision-making is needed
4. Create service layer in `api/services/`
5. Add routes in `api/routes/`

### Current Services
- **Macronutrient Extractor** (implemented): Analyzes ingredients and extracts nutritional information
- **ReAct Agent** (implemented): Reasoning and Acting agent for conversational interactions
- **Nutrition Plan Generator** (in development): Creates personalized meal plans
- **User Profile Generator** (planned): Initial user onboarding

### Configuration
Environment variables are managed through Pydantic settings. Required keys:
```bash
# AI Models
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
GROQ_API_KEY=your_key

# Database
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_key
```

### Key Implementation Notes
- Use `uv run` prefix for running Python modules in development
- Services can be tested individually using their module path
- All AI interactions use LangChain abstractions
- Database operations go through Supabase client
- Event system enables decoupled communication between components
- MCP integrations provide external tool capabilities to agents