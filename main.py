from fastapi import FastAPI
from fastmcp import FastMCP
from api.mcp.router import router as mcp_router
import uvicorn
from config import ENV
import gradio as gr
from assistant import Assistant

# MCP Initialization
app = FastAPI(title="AI Assistant (With MCP)")
app.include_router(mcp_router)

mcp = FastMCP.from_fastapi(app)
mcp_http = mcp.http_app(path="/", stateless_http=True) 

# Main app
app = FastAPI(
    title="AI Assistant (With MCP)",
    lifespan=mcp_http.lifespan 
)

# Mount MCP HTTP app to /mcp
app.mount("/mcp", mcp_http)

Assistant = Assistant()

# Gradio app Initialization
demo = gr.ChatInterface(fn=Assistant.chat)
gr.mount_gradio_app(app, demo, path="/chat")

# Run the app
if __name__ == "__main__":  
    # Get port and host from environment variables
    port = int(ENV['port']) if ENV['port'] else 8000
    host = ENV['host'] if ENV['host'] else 'localhost'
    # Run the app
    uvicorn.run(app, host=host, port=port)