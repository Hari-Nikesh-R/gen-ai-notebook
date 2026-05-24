import asyncio
import sys
import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# The model must match the one you pulled in the prerequisites
MODEL_NAME = "llama3.2"

async def run_agent():
    # 1. Define how to start our background MCP server
    server_params = StdioServerParameters(
        command=sys.executable, # Uses your current Python environment
        args=["reference_server.py"]
    )
    
    print("[*] Starting local MCP Server...")
    
    # 2. Open the stdio connection and initialize the session
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 3. Fetch the tools from the server and translate them for Ollama
            mcp_tools = await session.list_tools()
            ollama_tools = []
            
            for tool in mcp_tools.tools:
                ollama_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })
            print(f"[✓] Server connected. Discovered tools: {[t.name for t in mcp_tools.tools]}")
            
            # 4. Set up the conversation
            messages = [{
                "role": "user", 
                "content": "Check my notes and tell me what the app idea was."
            }]
            
            print(f"\n[Prompt]: {messages[0]['content']}\n")
            print("[*] Thinking...")
            
            # 5. First Pass: Give Ollama the prompt and the tool menu
            response = ollama.chat(
                model=MODEL_NAME,
                messages=messages,
                tools=ollama_tools
            )
            
            assistant_msg = response["message"]
            messages.append(assistant_msg)
            
            # 6. Check if Ollama decided it needs to use a tool
            if "tool_calls" in assistant_msg and assistant_msg["tool_calls"]:
                
                # Execute every tool the model requested
                for tool_call in assistant_msg["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    tool_args = tool_call["function"]["arguments"]
                    
                    print(f"[!] Executing Tool: {tool_name}({tool_args})")
                    
                    # 7. Route the request down to the MCP server and wait for the result
                    mcp_result = await session.call_tool(tool_name, arguments=tool_args)
                    result_text = mcp_result.content[0].text
                    
                    # 8. Append the raw data back into the chat history as a "tool" role
                    messages.append({
                        "role": "tool",
                        "content": result_text
                    })
                
                # 9. Second Pass: Send the history (now containing the file data) back to Ollama
                print("[*] Passing data back to Ollama for final answer...\n")
                final_response = ollama.chat(
                    model=MODEL_NAME,
                    messages=messages
                )
                print(f"🤖 Final Answer: {final_response['message']['content']}")
            
            else:
                # If the model didn't need tools, just print its response
                print(f"🤖 Answer: {assistant_msg['content']}")

if __name__ == "__main__":
    # Suppress macOS/Windows asyncio warnings for clean output
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(run_agent())