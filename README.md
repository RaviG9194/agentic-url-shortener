# Agentic URL Shortener

An agentic URL shortening service built with FastAPI, SQLAlchemy, SQLite, and an optional OpenAI-powered agent.

The application allows users to create short URLs, use custom aliases, configure expiration, track clicks, view URL statistics, and interact with the system using natural-language requests.

## Features

- Create short URLs
- Generate random short codes
- Support custom aliases
- Optional URL expiration
- Redirect short URLs to original URLs
- Track click counts
- View URL statistics
- Natural-language agent interface
- Rule-based agent fallback
- Optional OpenAI-powered agent
- Tool-based agent architecture
- SQLite persistence
- SQLAlchemy ORM
- FastAPI REST API
- Swagger/OpenAPI documentation
- Automated pytest test suite

## Technology Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- pytest
- OpenAI Python SDK

## Project Structure

agentic-url-shortener/
|
+-- app/
|   +-- __init__.py
|   +-- main.py
|   +-- agent.py
|   +-- llm_agent.py
|   +-- config.py
|   +-- database.py
|   +-- models.py
|   +-- schemas.py
|   +-- services.py
|   +-- tools.py
|   +-- tool_registry.py
|
+-- tests/
|   +-- test_agent.py
|   +-- test_config.py
|   +-- test_llm_agent.py
|   +-- test_schemas.py
|   +-- test_tools.py
|   +-- test_tool_registry.py
|   +-- test_urls.py
|
+-- .env.example
+-- .gitignore
+-- README.md
+-- urls.db

## Architecture

User
 |
 v
FastAPI API
 |
 v
Agent Layer
 |
 +-------------------+
 |                   |
 v                   v
LLM Agent      Rule-Based Agent
 |                   |
 +---------+---------+
           |
           v
         Tools
           |
     +-----+-----+
     |           |
     v           v
Create URL   Get Stats
Tool         Tool
     |           |
     +-----+-----+
           |
           v
     Service Layer
           |
           v
       SQLAlchemy
           |
           v
         SQLite

## How the Agent Works

The application supports two agent execution paths.

### Rule-Based Agent

The rule-based agent works without an external API key.

It analyzes the user's request and identifies supported intents such as:

- Creating a short URL
- Getting statistics for a short URL

Example request:

Shorten https://example.com with alias demo

The agent identifies this as the create_url intent and executes the predefined URL creation tool.

### LLM Agent

An optional OpenAI-powered agent can be used when an API key is configured.

The general flow is:

User Request
 |
 v
LLM
 |
 v
Structured Action
 |
 v
Validation
 |
 v
Predefined Tool
 |
 v
Database

The LLM does not directly execute database queries or arbitrary Python code.

It can only request supported application tools.

## Available Tools

The application currently provides two primary tools.

### Create URL Tool

Creates a short URL from an original URL.

Supported options include:

- Original URL
- Custom alias
- Expiration time

### Get Statistics Tool

Retrieves statistics for an existing short URL.

Statistics include:

- Short code
- Original URL
- Click count
- Creation time
- Expiration time
- Active/inactive status

## API Endpoints

### Health Check

GET /

Returns a basic application health response.

### Create Short URL

POST /api/v1/urls

Example request:

{
  "url": "https://example.com",
  "custom_alias": "example",
  "expires_in_minutes": 60
}

### Redirect Short URL

GET /{short_code}

Example:

http://127.0.0.1:8000/example

The application redirects the request to the original URL and increments the click count.

### Get Statistics

GET /api/v1/urls/{short_code}/stats

Example:

GET /api/v1/urls/example/stats

### Agent Endpoint

POST /api/v1/agent

Example request:

{
  "message": "Shorten https://example.com with alias demo"
}

Another example:

{
  "message": "How many clicks did demo get?"
}

## Installation

### 1. Open the project directory

cd C:\Users\ravig\agentic-url-shortener

### 2. Create a virtual environment

python -m venv .venv

### 3. Activate the virtual environment

.venv\Scripts\Activate.ps1

### 4. Install dependencies

pip install fastapi uvicorn sqlalchemy pydantic pytest httpx openai

## Running the Application

Start the FastAPI development server:

uvicorn app.main:app --reload

The application will run at:

http://127.0.0.1:8000

## API Documentation

FastAPI automatically provides interactive API documentation.

Open:

http://127.0.0.1:8000/docs

The Swagger interface can be used to test the API without writing additional code.

## Example Workflow

### Step 1: Create a Short URL

Send the following request to the agent:

Shorten https://example.com with alias demo

Example response:

Your short URL is http://127.0.0.1:8000/demo

### Step 2: Open the Short URL

Open:

http://127.0.0.1:8000/demo

The application redirects to:

https://example.com

The click count is incremented.

### Step 3: Request Statistics

Ask:

How many clicks did demo get?

The statistics tool retrieves the information.

Example:

The short URL demo has 1 clicks.

## URL Expiration

URLs can optionally have an expiration time.

For example:

{
  "url": "https://example.com",
  "custom_alias": "temporary",
  "expires_in_minutes": 60
}

After the configured expiration period, the URL is considered inactive and cannot be used for normal redirection.

## Custom Aliases

Users can provide their own short code.

Example:

Shorten https://example.com with alias my-link

The resulting URL can be:

http://127.0.0.1:8000/my-link

Duplicate aliases are rejected to prevent conflicts.

## Database

The project uses SQLite for persistence.

The database file is:

urls.db

SQLAlchemy is used as the ORM layer.

The database stores information such as:

- Original URL
- Short code
- Creation timestamp
- Expiration timestamp
- Click count

The local database file is excluded from Git using .gitignore.

## Configuration

Configuration is handled through environment variables.

The project contains:

.env.example

Example configuration:

OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.6

The application does not require an OpenAI API key for the rule-based agent.

If an API key is available, it can be configured through the environment.

For PowerShell:

$env:OPENAI_API_KEY="your-api-key"

Optionally:

$env:OPENAI_MODEL="gpt-5.6"

Real API keys should never be committed to Git.

## Tool Safety

The agent follows a controlled tool-execution approach.

The LLM does not receive unrestricted access to:

- Python execution
- SQL execution
- Shell commands
- The filesystem

Instead, the agent can select from predefined application tools.

Currently supported tools include:

- create_url
- get_stats

Tool inputs are validated before execution.

This keeps the agent architecture simple and controlled.

## Error Handling

The application handles common error cases including:

- Missing URL
- Invalid URL
- Duplicate custom alias
- Missing short code
- Unknown short code
- Expired URL
- Unsupported agent request
- Invalid tool request

The application returns structured success and error responses.

## Testing

The project contains an automated test suite using pytest.

Run all tests with:

python -m pytest

The tests cover:

- URL creation
- URL validation
- Custom aliases
- URL expiration
- Redirect behavior
- Click tracking
- Statistics
- Agent intent classification
- Agent tool execution
- Tool registry
- LLM agent behavior
- Configuration
- Request/response schemas

## Testing the Agent Manually

The rule-based agent can be tested without an OpenAI API key.

Example:

python -c "from uuid import uuid4; from app.agent import run_agent; from app.database import SessionLocal; a='demo-'+uuid4().hex[:8]; db=SessionLocal(); r=run_agent(f'Shorten https://example.com with alias {a}', db); print(r); db.close()"

A successful response should contain:

success: True
action: create_url

## Reliability

The core URL-shortening functionality does not depend on an external LLM.

This is intentional.

The application can continue to:

- Create short URLs
- Redirect URLs
- Track clicks
- Return statistics
- Process supported natural-language requests

even when an OpenAI API key is not configured.

The rule-based agent acts as a deterministic fallback.

## Security Considerations

The project follows several basic security practices:

- API keys are stored outside the source code.
- .env files are excluded from Git.
- Database files are excluded from Git.
- The agent uses predefined tools.
- Arbitrary code execution is not exposed.
- Tool inputs are validated.
- Database operations are handled through the application layer.

## Git

The project includes a .gitignore file that excludes:

.venv/
__pycache__/
.pytest_cache/
.env
*.db
*.sqlite
*.sqlite3

This prevents local environments, secrets, temporary files, and local databases from being committed accidentally.

## Future Improvements

Possible future improvements include:

- Authentication
- Rate limiting
- Redis caching
- PostgreSQL support
- Analytics dashboard
- User accounts
- More agent tools
- Background cleanup of expired URLs
- Docker deployment
- Production monitoring
- Better natural-language understanding
- More detailed analytics

## Educational Purpose

This project demonstrates how a relatively small backend application can combine:

- REST APIs
- Database persistence
- ORM-based data access
- Automated testing
- Tool-based agents
- Natural-language interaction
- Optional LLM integration
- Deterministic fallback behavior

The architecture intentionally keeps the system simple enough to understand while maintaining clear separation between the API, agent, tools, services, and database layers.

## License

This project was created as an educational project demonstrating FastAPI, database-backed URL shortening, tool-based agents, and optional LLM integration.
