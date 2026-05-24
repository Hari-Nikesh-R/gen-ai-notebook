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

## STEP 4 — The Client

### Code
```python
server_params = StdioServerParameters(
    command=sys.executable,
    args=["mcp_tool.py"],
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
```

### What happens internally?
1. The client **spawns** `python mcp_tool.py` as a subprocess.
2. It opens two pipes: `read` (server stdout) and `write` (server stdin).
3. `session.initialize()` does the MCP **handshake** — version negotiation, capability exchange.

### Visualization
```text
ollama_client.py
       │ subprocess.Popen
       ▼
   mcp_tool.py
       │
       ▼
  FastMCP listening on stdio
```

---

## STEP 5 — Tool Discovery

### Code
```python
tools = (await session.list_tools()).tools
```

### What Comes Back
A list of tool objects, each containing:
*   `name`
*   `description`
*   `inputSchema` (JSON Schema)

### Translating for Ollama
Different LLM SDKs expect slightly different shapes. We convert MCP → Ollama:

```python
def to_ollama_tools(mcp_tools):
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
```

This **adapter pattern** is exactly how Cursor, Claude Desktop, and other clients reuse the same MCP server.

---

## STEP 6 — LLM Tool Selection

### Code
```python
reply = ollama.chat(
    model=MODEL,
    messages=messages,
    tools=to_ollama_tools(tools),
)["message"]
```

### Internal Thinking

Ollama receives:
*   The user's question
*   A menu of available tools

It returns one of two things:
1. A **plain answer** (no tool needed), OR
2. A **`tool_calls`** list saying *"please run `read_note_content(filename='app_idea.txt')` for me"*.

### Example LLM Response
```json
{
  "role": "assistant",
  "tool_calls": [
    {
      "function": {
        "name": "list_available_notes",
        "arguments": {}
      }
    }
  ]
}
```

The LLM is **NOT** running the function — it is just **proposing** which one to run.

---

## STEP 7 — Tool Execution

### Code
```python
for call in tool_calls:
    name = call["function"]["name"]
    args = call["function"]["arguments"]

    result = await session.call_tool(name, arguments=args)
    messages.append({
        "role": "tool",
        "content": result.content[0].text,
    })
```

### What Happens Internally
1. The client sends the tool name + args **down the stdio pipe** to the server.
2. The server runs the actual Python function (e.g. opens the `.txt` file).
3. The text result comes back over stdio.
4. We add it to the chat history with `role: "tool"`.

### Real Internal Conversation
```text
[user]      Check my notes and tell me what the app idea was.
[assistant] tool_call: list_available_notes()
[tool]      Available notes: app_idea.txt
[assistant] tool_call: read_note_content(filename="app_idea.txt")
[tool]      --- Content of app_idea.txt ---
            App Idea: PocketProfessor ...
```

---

## STEP 8 — Final Response

### Code
```python
final = ollama.chat(model=MODEL, messages=messages)
print(final["message"]["content"])
```

The LLM now has:
*   The original question
*   Its own reasoning steps
*   The **real data** from the tool

…and produces a grounded final answer.

### Sample Output
> "Your note `app_idea.txt` describes **PocketProfessor**, a mobile app
> that lets students chat with any textbook PDF and works offline."

### Why MCP Is Powerful
*   **Without MCP:** the LLM hallucinates about your files.
*   **With MCP:** the LLM reads the real file and tells you the truth.

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
pip install mcp ollama
```

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
├── mcp_tool.py        # The MCP server (tools)
├── ollama_client.py   # The MCP client (LLM driver)
├── my_notes/          # Auto-created on first run
│   └── app_idea.txt   # Sample note for the demo
└── README.md
```

### 4. Run the demo

```bash
cd day5_mcp_and_automation/mcp_project
python ollama_client.py
```

### Expected Output
```text
[1/4] Starting MCP server...
[2/4] Tools available: ['list_available_notes', 'read_note_content']

[User]  Check my notes and tell me what the app idea was.

[3/4] Asking the LLM...
   -> Tool call: list_available_notes({})
   -> Tool call: read_note_content({'filename': 'app_idea.txt'})
[4/4] Generating final answer with tool results...

[AI]    Your note describes "PocketProfessor", an app that lets students chat with any textbook PDF...
```

### 5. Try your own notes

Drop any `.txt` file into `my_notes/` and re-run:
```bash
echo "Remember: standup at 10am every day." > my_notes/reminders.txt
python ollama_client.py
```

Edit the `QUESTION` constant at the top of `ollama_client.py` to ask anything you want.

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
| `ModuleNotFoundError: mcp` | SDK not installed | `pip install mcp` |
| `connection closed` instantly | Server crashed on startup | Run `python mcp_tool.py` directly to see the error |
| Tools list is empty | Wrong path in config | Use an **absolute** path to `mcp_tool.py` |
| LLM never calls a tool | Question is too vague | Be explicit: *"Use my notes to answer..."* |
| Ollama connection refused | Ollama daemon not running | Start the Ollama app or `ollama serve` |

---

## Common Beginner Confusions

1. **"Is the LLM running my Python code?"**
   No. The LLM only **proposes** a tool call. The MCP server runs the code in a separate process.

2. **"Why is everything `async`?"**
   Because stdio is non-blocking I/O. The client and server are talking on pipes, so we use Python's `asyncio` to wait without freezing.

3. **"What's the difference between MCP and OpenAI function calling?"**
   Function calling is a **per-LLM feature**. MCP is a **standard** that wraps function calling so any LLM can use any tool.

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

A complete agent stack in **~70 lines of Python**:
*   A **server** that exposes Python functions as tools.
*   A **client** that lets a local LLM discover and call those tools.
*   A **transport** that works locally and plugs into Cursor, Antigravity, and Claude Desktop unchanged.

This is the same pattern that powers Cursor's tool-using agent, Claude's filesystem access, and every modern AI IDE — just smaller.
