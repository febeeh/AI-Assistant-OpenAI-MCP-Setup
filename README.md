# simple-ai-assistant-openai-mcp

A simple AI assistant with OPENAI & MCP (Model Context Protocol) tool support and a Gradio chat UI. Built with FastAPI, FastMCP, and Gradio.

## Architecture

```
User ↔ Gradio Chat UI ↔ OpenAI API ↔ MCP Server (FastAPI + FastMCP)
         /chat                            /mcp
```

- **Gradio** serves the chat interface at `/chat`
- **OpenAI Responses API** handles conversation and decides when to call tools
- **MCP Server** exposes tools via the `/mcp` endpoint using FastMCP
- Tool definitions are auto-discovered from MCP and passed to OpenAI as function tools

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/febeeh/simple-ai-assistant-openai-mcp
cd simple-ai-assistant-openai-mcp
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-your-key-here
MODEL=gpt-4o-mini
HOST=localhost
PORT=8000
```

### 5. Run the app

```bash
python main.py
```

- Chat UI: `http://localhost:8000/chat`
- MCP endpoint: `http://localhost:8000/mcp`

## How to Customize

### Change the assistant's system prompt

Edit `assistant.md` — update the system prompt:

### Add your MCP tools

Add new routes in `api/mcp/router.py`. Each FastAPI endpoint under the router automatically becomes an MCP tool:

```python
# api/mcp/router.py

@router.get("/tools/my_new_tool")
def my_new_tool(param: str):
    """Description of what this tool does (shown to the LLM)."""
    return {"result": "..."}
```

The function name becomes the tool name, and the docstring becomes the tool description that OpenAI sees. Parameters are extracted from the function signature.

### Change the OpenAI model

Update the `MODEL` value in your `.env` file:

```env
MODEL=gpt-4o
```

## Tech Stack

- **FastAPI** — API framework
- **FastMCP** — MCP server implementation
- **OpenAI Responses API** — LLM with streaming and tool use
- **Gradio** — Chat UI
- **Uvicorn** — ASGI server

## Project Structure

```
├── main.py              # App entry point — FastAPI + MCP + Gradio mounting
├── assistant.py         # Chat logic, OpenAI streaming, MCP tool execution
├── config.py            # Environment variable loader
├── api/
│   └── mcp/
│       └── router.py    # MCP tool routes
├── .env                 # Environment variables
└── requirements.txt
```
