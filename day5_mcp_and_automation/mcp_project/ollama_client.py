"""
Ollama + MCP Client
-------------------
A minimal client that lets a local Ollama LLM use the tools exposed by
our MCP server (mcp_tool.py).

Flow:
  1. Launch the MCP server as a child process over stdio.
  2. Ask the server which tools it offers.
  3. Send a user question to Ollama, along with the tool list.
  4. If the LLM decides to call a tool, run it via MCP and feed
     the result back into the conversation.
  5. Print the final, grounded answer.
"""

import asyncio
import sys

import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MODEL = "llama3.2"
SERVER_SCRIPT = "mcp_tool.py"
QUESTION = "Check my notes and tell me what the app idea was."


def to_ollama_tools(mcp_tools):
    """Convert MCP tool definitions into the schema Ollama expects."""
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,
            },
        }
        for tool in mcp_tools
    ]


async def main():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT],
    )

    print("[1/4] Starting MCP server...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = (await session.list_tools()).tools
            print(f"[2/4] Tools available: {[t.name for t in tools]}")

            messages = [{"role": "user", "content": QUESTION}]
            print(f"\n[User]  {QUESTION}\n")

            print("[3/4] Asking the LLM...")
            reply = ollama.chat(
                model=MODEL,
                messages=messages,
                tools=to_ollama_tools(tools),
            )["message"]
            messages.append(reply)

            tool_calls = reply.get("tool_calls") or []

            for call in tool_calls:
                name = call["function"]["name"]
                args = call["function"]["arguments"]
                print(f"   -> Tool call: {name}({args})")

                result = await session.call_tool(name, arguments=args)
                messages.append({
                    "role": "tool",
                    "content": result.content[0].text,
                })

            if tool_calls:
                print("[4/4] Generating final answer with tool results...\n")
                final = ollama.chat(model=MODEL, messages=messages)
                answer = final["message"]["content"]
            else:
                answer = reply["content"]

            print(f"[AI]    {answer}")


if __name__ == "__main__":
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
