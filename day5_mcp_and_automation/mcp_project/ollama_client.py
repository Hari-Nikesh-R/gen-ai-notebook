"""
Ollama + MCP Interactive Chatbot
=================================
This is the "client" side of the project.

It does three things:
  1. Starts the MCP server (mcp_tool.py) as a background process.
  2. Asks the LLM your questions, along with a list of available tools.
  3. If the LLM wants to use a tool, runs it and feeds the result back.

The conversation keeps going until you type 'exit' or press Ctrl+C.

HOW TO RUN:
  python ollama_client.py

COMMANDS INSIDE THE CHAT:
  exit / quit / :q   →  leave
  clear              →  wipe conversation history (start fresh)
  Ctrl+C             →  quit immediately
"""

import asyncio
import sys

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MODEL = "gemma4"
SERVER_SCRIPT = "mcp_tool.py"
SYSTEM_PROMPT = """You are a helpful personal assistant with two sets of tools:

NOTES (read-only):
  - list_available_notes  → see what .txt note files exist
  - read_note_content     → read a specific note file

TO-DO MANAGER (read + write):
  - add_todo      → create a new task
  - list_todos    → show tasks (filter: 'all', 'pending', or 'done')
  - complete_todo → mark a task done by its ID (records date & time)
  - delete_todo   → permanently remove a task by its ID

RULES — follow these strictly:
1. Whenever the user mentions a task, action item, reminder, or anything
   they need to do — call add_todo immediately, without being asked.
2. Whenever the user says they finished, completed, or are done with
   something — call complete_todo for the matching task.
3. When the user asks what they need to do, what's left, or for a
   summary — call list_todos with filter='pending'.
4. For notes, use list_available_notes first, then read_note_content.
5. Always confirm tool actions in your reply so the user knows what happened.
6. Answer concisely."""


async def chat_loop():
    server_params = StdioServerParameters(
        command=sys.executable, args=[SERVER_SCRIPT]
    )

    print("Starting MCP server...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)
            llm = ChatOllama(model=MODEL)
            agent = create_react_agent(llm, tools)

            print(f"Tools: {[t.name for t in tools]}")
            print("Type 'exit' to quit, 'clear' to reset history.\n")

            history = [SystemMessage(content=SYSTEM_PROMPT)]

            while True:
                try:
                    user = input("You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nGoodbye!")
                    return

                if not user:
                    continue

                cmd = user.lower()
                if cmd in {"exit", "quit", ":q"}:
                    print("Goodbye!")
                    return
                if cmd == "clear":
                    history = [SystemMessage(content=SYSTEM_PROMPT)]
                    print("(history cleared)\n")
                    continue

                history.append(HumanMessage(content=user))
                try:
                    result = await agent.ainvoke({"messages": history})
                except KeyboardInterrupt:
                    print("\n(interrupted)")
                    history.pop()
                    continue

                history = result["messages"]
                print(f"\nAI: {history[-1].content}\n")


if __name__ == "__main__":
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(chat_loop())
    except KeyboardInterrupt:
        print("\nGoodbye!")
