from openai import AsyncOpenAI
from config import ENV
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
import asyncio
import json

# Assistant
class Assistant:
    def __init__(self):
        # OpenAI client
        self.client = AsyncOpenAI(api_key=ENV["openai_api_key"])

        # MCP URL
        self.MCP_URL = f"http://{ENV['host']}:{ENV['port']}/mcp/"

        # OpenAI tools
        self.OPENAI_TOOLS = None

        # System prompt
        self.SYSTEM_PROMPT = self.get_assistant_md()

    # Get assistant.md
    def get_assistant_md(self):
        with open("assistant.md", "r") as file:
            return file.read()

    # Get MCP tools
    async def get_mcp_tools(self):
        async def _fetch():
            async with streamablehttp_client(self.MCP_URL) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return (await session.list_tools()).tools

        mcp_tools = await _fetch()
        return [
            {
                "type": "function",
                "name": t.name,
                "description": t.description or "",
                "parameters": t.inputSchema or {"type": "object", "properties": {}},
            }
            for t in mcp_tools
        ]


    # Call MCP tool
    async def call_mcp_tool(self, tool_name: str, arguments: dict) -> str:
        async def _call():
            async with streamablehttp_client(self.MCP_URL) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments=arguments)
                    texts = [b.text for b in result.content if hasattr(b, "text")]
                    return "\n".join(texts)

        return await _call()


    # Execute tool calls
    async def execute_tool_calls(self, tool_calls: dict) -> tuple[list, list]:
        """Execute all tool calls against MCP, return (call_items, output_items)."""
        call_items = []
        output_items = []

        for tool_call in tool_calls.values():
            args = json.loads(tool_call["arguments"])
            try:
                result_text = await asyncio.wait_for(self.call_mcp_tool(tool_call["name"], args), timeout=10)
            except asyncio.TimeoutError:
                result_text = "Tool did not respond in time."
            except Exception as e:
                result_text = f"Tool call failed: {e}"

            call_items.append({
                "type": "function_call",
                "name": tool_call["name"],
                "call_id": tool_call["call_id"],
                "arguments": tool_call["arguments"],
            })
            output_items.append({
                "type": "function_call_output",
                "call_id": tool_call["call_id"],
                "output": result_text,
            })

        return call_items, output_items


    async def chat(self, message, history):

        history = history or []

        if self.OPENAI_TOOLS is None:
            self.OPENAI_TOOLS = await self.get_mcp_tools()

        # Messages
        messages = []
        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"] if isinstance(msg["content"], str) else msg["content"][0]["text"],
            })
        messages.append({"role": "user", "content": message})

        # Tool history
        tool_history = []
        max_rounds = 5  # safety limit to prevent infinite loops
        round_num = 0

        # Stream text to UI while collecting tool calls
        while round_num < max_rounds:
            round_num += 1

            stream = await self.client.responses.create(
                model=ENV["model"],
                instructions=self.SYSTEM_PROMPT,
                input=[*messages, *tool_history],
                tools=self.OPENAI_TOOLS,
                tool_choice="auto",
                stream=True,
            )

            partial = ""
            tool_calls = {}

            async for event in stream:
                if event.type == "response.output_text.delta":
                    partial += event.delta
                    yield partial

                elif event.type == "response.output_item.added":
                    if event.item.type == "function_call":
                        tool_calls[event.item.id] = {
                            "name": event.item.name,
                            "call_id": event.item.call_id,
                            "arguments": "",
                        }

                elif event.type == "response.function_call_arguments.delta":
                    if event.item_id in tool_calls:
                        tool_calls[event.item_id]["arguments"] += event.delta

            # No tool calls — we're done
            if not tool_calls:
                return

            yield 'Thinking....'

            call_items, output_items = await self.execute_tool_calls(tool_calls)
            tool_history.extend(call_items + output_items)
