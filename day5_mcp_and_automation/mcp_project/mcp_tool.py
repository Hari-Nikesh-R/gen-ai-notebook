import os
from mcp.server.fastmcp import FastMCP

# 1. Initialize the server
mcp = FastMCP("SmartReferenceDesk")
NOTES_FOLDER = "./my_notes"

# Make sure the notes folder exists so first-run never crashes
os.makedirs(NOTES_FOLDER, exist_ok=True)

# 2. Tool to list available files
@mcp.tool()
def list_available_notes() -> str:
    """Returns a list of all text files currently in the notes folder."""
    try:
        files = [f for f in os.listdir(NOTES_FOLDER) if f.endswith(".txt")]
        if not files:
            return "No text files found."
        return f"Available notes: {', '.join(files)}"
    except Exception as e:
        return f"Error reading folder: {str(e)}"

# 3. Tool to read a specific file
@mcp.tool()
def read_note_content(filename: str) -> str:
    """Reads and returns the exact text content of a specified note file."""
    if not filename.endswith(".txt"):
        return "Error: Can only read .txt files."

    filepath = os.path.join(NOTES_FOLDER, filename)
    try:
        with open(filepath, 'r') as file:
            return f"--- Content of {filename} ---\n{file.read()}"
    except FileNotFoundError:
        return f"Error: Note '{filename}' does not exist."

if __name__ == "__main__":
    # Standard I/O allows local clients to run this as a subprocess
    mcp.run(transport="stdio")
