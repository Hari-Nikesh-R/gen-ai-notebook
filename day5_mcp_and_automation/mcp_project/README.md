# How the MCP Code Works

You are now entering the world of **AI Agents and Tool Use**.

A beginner usually sees:

$$\text{Question} \rightarrow \text{LLM Answer}$$

But internally, an MCP-powered agent does something much richer:

$$\text{Question} \rightarrow \text{LLM} \rightleftharpoons \text{MCP Server} \rightleftharpoons \text{Tools / Files / APIs} \rightarrow \text{Grounded Answer}$$

We will break the entire system into:
1. **The MCP Server** (`mcp_tool.py`)
2. **Tool Registration** (`@mcp.tool` decorator)
3. **Transport** (stdio)
4. **The Client** (`ollama_client.py`)
5. **Tool Discovery**
6. **LLM Tool Selection**
7. **Tool Execution**
8. **Final Response**

This directly aligns with your AI syllabus **Module 6 on MCP & Automation**.

---

## What Is MCP?

**MCP** = **Model Context Protocol**.

Think of it as **USB-C for AI models**:
*   Any LLM (Ollama, Claude, GPT) can plug into any tool (files, APIs, databases).
*   The tool side never has to know which LLM is calling it.
*   The LLM side never has to know how the tool is implemented.

| Without MCP | With MCP |
| :--- | :--- |
| Each LLM app re-writes its own tool wrappers | One server works with every MCP client |
| Tightly coupled to one model | Model-agnostic |
| Custom JSON schema per project | Standard, discoverable schema |

---

## FULL MCP FLOW

```text
       [ User Question ]
              │
              ▼
        [ Ollama LLM ]  ◄──── tool list ◄────┐
              │                              │
              │ "I should call a tool"       │
              ▼                              │
       [ tool_call JSON ]                    │
              │                              │
              ▼                              │
        ─── stdio ───►  [ MCP Server ]       │
                              │              │
                              ▼              │
                       [ Python function ]   │
                              │              │
                              ▼              │
                        [ tool result ] ─────┘
              ▲
              │
       [ Ollama LLM ]
              │
              ▼
       [ Final Answer ]
```

---

## STEP 1 — The MCP Server

### Code
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SmartReferenceDesk")
```

### What happens internally?

`FastMCP` is a tiny framework that:
*   wraps your Python functions in JSON-RPC handlers
*   advertises them with names, descriptions, and JSON-Schema parameters
*   listens for requests from any MCP client

The string `"SmartReferenceDesk"` is just the **server identity** that clients see in their UI.

### Why a server?
Because the LLM and the tool live in **different processes**:
*   The LLM may run in Cursor, Claude Desktop, or our Python script.
*   The tool runs the actual file I/O, database calls, or API calls.
*   MCP is the contract between them.

---

## STEP 2 — Tool Registration

### Code
```python
@mcp.tool()
def list_available_notes() -> str:
    """Returns a list of all text files currently in the notes folder."""
    ...
```

### Internal Thinking

The decorator `@mcp.tool()` does three things:
1. Reads the function **name** → becomes the tool ID.
2. Reads the **docstring** → becomes the description the LLM sees.
3. Reads the **type hints** → auto-generates a JSON Schema for the arguments.

Example schema generated for `read_note_content(filename: str)`:
```json
{
  "name": "read_note_content",
  "description": "Reads and returns the exact text content of a specified note file.",
  "parameters": {
    "type": "object",
    "properties": { "filename": { "type": "string" } },
    "required": ["filename"]
  }
}
```

### Why Docstrings Matter
The docstring is **literally the only thing the LLM uses to decide whether to call your tool**.

Bad: `"Reads file."`
Good: `"Reads and returns the exact text content of a specified note file."`

### Industry Insight
Production MCP servers expose dozens of tools (GitHub, Slack, Postgres, Jira). The quality of your **tool descriptions** directly controls the agent's accuracy.

---

## STEP 3 — Transport (stdio)

### Code
```python
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### What Is stdio Transport?

The MCP server reads JSON-RPC messages from **stdin** and writes responses to **stdout**.

```text
[ Client process ]
       │  spawns
       ▼
[ Server subprocess ]  ──── stdout ───► JSON responses
       ▲
       │ stdin ◄───  JSON requests
```

### Why stdio?
*   **No network setup** — no ports, no firewalls, no auth.
*   **Local sandbox** — the server only lives while the client needs it.
*   **Cross-platform** — works identically on macOS, Linux, Windows.

### Other Transports (FYI)
| Transport | When to use |
| :--- | :--- |
| `stdio` | Local desktop tools (this project) |
| `sse` / `http` | Remote MCP servers, multi-tenant SaaS |
| `websocket` | Bidirectional streaming use cases |

---

## STEP 4 — The Client (LangChain Edition)

### Code
```python
server_params = StdioServerParameters(
    command=sys.executable, args=["mcp_tool.py"],
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await load_mcp_tools(session)
        agent = create_react_agent(ChatOllama(model="llama3.2"), tools)
```

### What happens internally?
1. The client **spawns** `python mcp_tool.py` as a subprocess.
2. It opens two pipes: `read` (server stdout) and `write` (server stdin).
3. `session.initialize()` does the MCP **handshake** — version negotiation, capability exchange.
4. `load_mcp_tools(session)` calls `list_tools()` under the hood and wraps each one as a LangChain `Tool` (handles JSON-Schema → LangChain conversion for you).
5. `create_react_agent(llm, tools)` wires up a LangGraph state machine that loops *LLM → tool calls → LLM* until a final answer is produced.

### Why one session, many questions
The client keeps **one** session open for the whole chat. Spawning the
server once and reusing it means:
*   Tool discovery happens only at startup — instant follow-ups.
*   Conversation history is preserved → real multi-turn dialogue.
*   Tool calls in turn 5 are as fast as in turn 1.

### Visualization
```text
ollama_client.py
       │ subprocess.Popen
       ▼
   mcp_tool.py
       │
       ▼
  FastMCP listening on stdio
       ▲
       │ load_mcp_tools(session)
       │
   LangGraph agent (ChatOllama + MCP tools)
```

---

## STEP 5 — Tool Discovery (Auto)

### Without LangChain (manual — what we used to write)
```python
mcp_tools = (await session.list_tools()).tools
ollama_tools = [
    {
        "type": "function",
        "function": {
            "name": t.name,
            "description": t.description,
            "parameters": t.inputSchema,
        },
    }
    for t in mcp_tools
]
```

### With LangChain (one line)
```python
tools = await load_mcp_tools(session)
```

`load_mcp_tools` reads the same `name / description / inputSchema` triple
and returns a list of `BaseTool` objects that any LangChain agent can use.
This is the **adapter pattern** — same job, less boilerplate.

This is also the same pattern Cursor, Claude Desktop, and other MCP
clients use internally to reuse one MCP server everywhere.

---

## STEP 6 — LLM Tool Selection (Done by `create_react_agent`)

When you call `agent.ainvoke({"messages": history})`, LangGraph runs the
following loop on your behalf:

```text
   [LLM]
     │ "Should I call a tool?"
     ▼
  tool_calls?  ── no ──►  return final answer
     │ yes
     ▼
  [run tool] ── result ──► append to history ──► back to LLM
```

Under the hood the LLM still emits a `tool_calls` JSON block — we just
don't have to write the dispatch code.

### Example LLM Response (raw)
```json
{
  "role": "assistant",
  "tool_calls": [
    { "function": { "name": "list_available_notes", "arguments": {} } }
  ]
}
```

The LLM is **NOT** executing anything — it is **proposing** which tool to run.

> **Day 4 connection.** Day 4 used `AgentType.ZERO_SHOT_REACT_DESCRIPTION`
> which built ReAct on top of *prompt templates* (because the old
> `Ollama` LLM didn't have native tool calling). `ChatOllama` + llama3.2
> support **native tool calling**, so `create_react_agent` uses the
> proper structured `tool_calls` field. Same idea, cleaner mechanics.

---

## STEP 7 — Tool Execution (Auto)

LangGraph dispatches each `tool_call` through the MCP session for us:

```text
agent ──► load_mcp_tools wrapper ──► session.call_tool(name, args)
                                          │
                                          ▼
                                      MCP server
                                          │
                                          ▼
                                    Python function
```

We never write `session.call_tool(...)` by hand. The result is appended
to the conversation as a `ToolMessage` and fed back to the LLM.

### Real Internal Conversation
```text
[user]      What was the app idea I wrote down?
[assistant] tool_call: list_available_notes()
[tool]      Available notes: app_idea.txt, ...
[assistant] tool_call: read_note_content(filename="app_idea.txt")
[tool]      --- Content of app_idea.txt ---
            App Idea: PocketProfessor ...
[assistant] Your note describes PocketProfessor ...
```

---

## STEP 8 — Final Response

### Code
```python
result = await agent.ainvoke({"messages": history})
print(result["messages"][-1].content)
```

`result["messages"]` is the **entire** conversation including every tool
call and tool result. The last message is always the final assistant
answer, so we just print that.

### Sample Output
> "Your note `app_idea.txt` describes **PocketProfessor**, a mobile app
> that lets students chat with any textbook PDF and works offline."

### Why MCP Is Powerful
*   **Without MCP:** the LLM hallucinates about your files.
*   **With MCP:** the LLM reads the real file and tells you the truth.

### Why LangChain Is Powerful Here
*   No JSON-Schema translation code.
*   No hand-rolled tool-call loop.
*   Multi-turn tool chaining works for free — LangGraph keeps looping until the LLM stops asking for tools.
*   Conversation memory is just a list of `messages` you keep around.
*   Same agent runtime as your day 4 project — only the tools change.

---

## How To Run This Project

### Prerequisites

| Requirement | Why |
| :--- | :--- |
| Python 3.10+ | MCP SDK requires modern type hints |
| [Ollama](https://ollama.com) installed and running | local LLM runtime |
| `llama3.2` model pulled | the LLM we call |

### 1. Install the dependencies

```bash
pip install mcp langchain-ollama langchain-mcp-adapters langgraph
```

| Package | Why |
| :--- | :--- |
| `mcp` | The protocol SDK (server + stdio transport) |
| `langchain-ollama` | `ChatOllama` chat model with native tool-calling |
| `langchain-mcp-adapters` | Auto-converts MCP tools → LangChain tools |
| `langgraph` | `create_react_agent` runs the LLM ↔ tool loop for us |

> **From day 4 → day 5.** In `day4_beyond_llm/agentic_ai/app.py` we used
> `langchain_community.llms.Ollama` with `initialize_agent`. Here we
> upgrade to `ChatOllama` (native tool calling) and `create_react_agent`
> (the modern LangGraph successor to `initialize_agent`). The mental
> model is identical — just less code and better tool routing.

### 2. Pull the LLM model

```bash
ollama pull llama3.2
```

Verify Ollama is running:
```bash
ollama list
```

### 3. Project layout

```text
mcp_project/
├── mcp_tool.py        # The MCP server (tools — pure mcp SDK)
├── ollama_client.py   # Chatbot client (LangChain + LangGraph + MCP)
├── my_notes/          # Auto-created on first run; sample notes inside
│   ├── app_idea.txt
│   ├── meeting_notes.txt
│   ├── project_ideas.txt
│   └── ... (more sample notes)
└── README.md
```

### 4. Run the chatbot

```bash
cd day5_mcp_and_automation/mcp_project
python ollama_client.py
```

You'll drop into an interactive chat. Ask as many questions as you want;
press **Ctrl+C** or type `exit` to quit.

### Expected Output
```text
Starting MCP server...
============================================================
  Ollama + MCP Chatbot
============================================================
  Model:  llama3.2
  Tools:  list_available_notes, read_note_content
  Type 'help' for commands, 'exit' to quit (or Ctrl+C).
============================================================

You: what notes do I have?
   [tool] list_available_notes({})

AI: You have 10 notes: app_idea, meeting_notes, reading_list,
project_ideas, reminders, learning_goals, travel_japan, bug_log,
recipe_rasam, cheatsheet.

You: summarize the app idea and the project I picked for this quarter
   [tool] read_note_content({'filename': 'app_idea.txt'})
   [tool] read_note_content({'filename': 'project_ideas.txt'})

AI: Your app idea is "PocketProfessor" — a mobile app that lets
students chat with any textbook PDF, fully offline. The project you
picked for this quarter is "CommitWhisperer", a CLI that reads
git diffs and writes conventional-commit messages using a local LLM.

You: exit
Goodbye!
```

### Chatbot Commands

| Command | Effect |
| :--- | :--- |
| `exit` / `quit` / `:q` | leave the chatbot |
| `clear` | wipe conversation history (start fresh) |
| `help` | show available commands |
| `Ctrl+C` (at prompt) | quit immediately |
| `Ctrl+C` (mid-answer) | cancel the current turn, keep chatting |

### 5. Try your own notes

Drop any `.txt` file into `my_notes/` and ask about it — no restart needed:
```bash
echo "Remember: standup at 10am every day." > my_notes/standup.txt
```

Then in the chatbot:
```text
You: when is standup?
```

The LLM will call `list_available_notes`, then `read_note_content('standup.txt')`, then answer.

---

## Using This MCP Server With Desktop Apps

The same `mcp_tool.py` server can be plugged into any MCP-compatible app — **without changing a single line of server code.**

> Replace `/ABSOLUTE/PATH/TO/mcp_project` below with the real path on your machine.
> On macOS you can copy it with: `pwd` from inside the project folder.

### Option A — Cursor

Cursor reads MCP servers from a JSON config.

1. **Open the config file**
   *   Project-level (recommended): `.cursor/mcp.json` in your repo root.
   *   Global: `~/.cursor/mcp.json`.

2. **Add the server**
   ```json
   {
     "mcpServers": {
       "smart-reference-desk": {
         "command": "python",
         "args": ["/ABSOLUTE/PATH/TO/mcp_project/mcp_tool.py"]
       }
     }
   }
   ```

3. **Restart Cursor** → open Settings → **MCP** → you should see `smart-reference-desk` with a green dot and two tools listed.

4. **Use it** — open the Cursor chat and ask: *"What notes do I have? Read app_idea.txt."* Cursor will auto-call the MCP tools.

---

### Option B — Antigravity (Google's Agentic IDE)

Antigravity supports MCP servers through its Agent settings.

1. Open Antigravity → **Settings** → **Agents** → **MCP Servers**.
2. Click **Add Server** and paste the JSON config (or use the form):
   ```json
   {
     "name": "smart-reference-desk",
     "command": "python",
     "args": ["/ABSOLUTE/PATH/TO/mcp_project/mcp_tool.py"]
   }
   ```
3. Hit **Save** → Antigravity will auto-spawn the server.
4. In any agent task, the agent can now call `list_available_notes` and `read_note_content`.

> Tip: If Antigravity does not detect the server, make sure the `python` command points to a Python with `mcp` installed (use the absolute path to the venv's `python` if needed).

---

### Option C — Claude Desktop

Claude Desktop is the original reference MCP client.

1. **Locate the config file**
   | OS | Path |
   | :--- | :--- |
   | macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
   | Windows | `%APPDATA%\Claude\claude_desktop_config.json` |

2. **Add the server**
   ```json
   {
     "mcpServers": {
       "smart-reference-desk": {
         "command": "python",
         "args": ["/ABSOLUTE/PATH/TO/mcp_project/mcp_tool.py"]
       }
     }
   }
   ```

3. **Quit and reopen Claude Desktop.** The hammer icon in the chat box should now show **2 tools**.

4. Ask Claude: *"List my notes and summarize app_idea.txt."*

---

### Option D — Any other MCP client (generic)

Most MCP clients (Continue, Zed, VS Code Copilot, custom apps) follow the same shape:

```json
{
  "command": "python",
  "args": ["/ABSOLUTE/PATH/TO/mcp_project/mcp_tool.py"],
  "transport": "stdio"
}
```

If a client supports MCP, this triple is all you ever need.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
| :--- | :--- | :--- |
| `ModuleNotFoundError: mcp` / `langchain_ollama` / `langgraph` | Deps not installed | `pip install mcp langchain-ollama langchain-mcp-adapters langgraph` |
| `connection closed` instantly | Server crashed on startup | Run `python mcp_tool.py` directly to see the error |
| Tools list is empty | Wrong path in config | Use an **absolute** path to `mcp_tool.py` |
| LLM never calls a tool | Model lacks tool-calling support | Use `llama3.2`, `qwen2.5`, or `mistral-nemo` — not every model supports tools |
| LLM never calls a tool (right model) | Question is too vague | Be explicit: *"Use my notes to answer..."* |
| Ollama connection refused | Ollama daemon not running | Start the Ollama app or `ollama serve` |
| `pydantic` version conflict | Old LangChain pinned | `pip install -U langchain-core langgraph` |

---

## Common Beginner Confusions

1. **"Is the LLM running my Python code?"**
   No. The LLM only **proposes** a tool call. The MCP server runs the code in a separate process.

2. **"Why is everything `async`?"**
   Because stdio is non-blocking I/O. The client and server are talking on pipes, so we use Python's `asyncio` to wait without freezing.

3. **"What's the difference between MCP and OpenAI function calling?"**
   Function calling is a **per-LLM feature**. MCP is a **standard** that wraps function calling so any LLM can use any tool.

   Concretely: in this project, `ChatOllama` uses Ollama's tool-calling. `langchain-mcp-adapters` is the bridge that says *"here's an MCP tool, expose it as a LangChain tool that fits any tool-calling LLM."*

4. **"Do I need a database for MCP?"**
   No. Tools can do *anything* Python can do — read files, hit APIs, run shell commands, query DBs.

5. **"Can a tool call another tool?"**
   Not directly. The LLM is always the orchestrator — it sees a result and decides what to call next.

---

## REAL INDUSTRY ARCHITECTURE

| Layer | Technologies |
| :--- | :--- |
| **MCP Servers** | GitHub MCP, Postgres MCP, Slack MCP, Filesystem MCP |
| **MCP Clients** | Cursor, Claude Desktop, Antigravity, Continue, Zed |
| **LLMs** | Claude, GPT-4o, Llama 3, Mistral, Qwen |
| **Transport** | stdio (local), SSE/HTTP (remote) |
| **Auth (remote)** | OAuth 2.1 |
| **Orchestration** | LangGraph, CrewAI, custom Python |

---

## Where MCP Is Used In Real Companies

*   **Developer tooling**
    *   IDE agents that read your repo, run tests, open PRs.
*   **Internal knowledge agents**
    *   Slack + Notion + Google Drive MCP servers for HR/IT bots.
*   **Data analytics**
    *   Postgres / Snowflake MCP servers letting analysts ask English questions.
*   **Customer support**
    *   Zendesk + Stripe MCP servers for refund/ticket automation.
*   **Personal productivity**
    *   Calendar, email, file system MCP servers for "do-it-for-me" assistants.

---

## Common Production Problems

1. **Vague tool descriptions** → LLM picks the wrong tool.
2. **Too many tools at once** → context bloat, latency, hallucinated arguments.
3. **No auth on remote servers** → anyone on the internet can read your data.
4. **Long-running tools blocking stdio** → use `async` + timeouts.
5. **No observability** → log every tool call with inputs, outputs, and latency.

---

## What You Just Built

A complete agent stack in **~80 lines of Python**:
*   A **server** that exposes Python functions as tools (`mcp_tool.py`, ~30 lines).
*   A **LangChain-powered chatbot client** (`ollama_client.py`, ~70 lines) that:
    *   Discovers MCP tools via `load_mcp_tools(session)` (one line).
    *   Runs the LLM ↔ tool ↔ LLM loop via `create_react_agent` (one line).
    *   Keeps a single MCP session alive across many questions.
    *   Chains multiple tool calls per turn for free.
    *   Supports `exit`, `clear`, and graceful Ctrl+C.
*   A **transport** that works locally and plugs into Cursor, Antigravity, and Claude Desktop unchanged.

### Stack at a glance

```text
   ChatOllama (llama3.2, native tool calling)
            │
            ▼
   create_react_agent  ← LangGraph
            │
            ▼
   load_mcp_tools(session)  ← langchain-mcp-adapters
            │
            ▼
       MCP session  ← mcp SDK (stdio)
            │
            ▼
       mcp_tool.py
```

This is the same pattern that powers Cursor's tool-using agent, Claude's filesystem access, and every modern AI IDE — just smaller. And it is the natural progression from the LangChain-on-Ollama agent you built in **day 4**.
