"""
llm_file_opener_agent.py
------------------------
AI-driven Windows File/App opener using OpenAI function calling.
-----------------------------------------
Requirements:
    pip install openai
    (and set your OpenAI API key as environment variable)
-----------------------------------------
Usage:
    python llm_file_opener_agent.py
"""

import os
import platform
import subprocess
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("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"))

# -------- SAFE ALLOWLIST --------
ALLOWLIST = {
    "notepad": r"C:\Windows\System32\notepad.exe",
    "calculator": r"C:\Windows\System32\calc.exe",
    "paint": r"C:\Windows\System32\mspaint.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "vscode": r"C:\Users\osmro\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Visual Studio Code",
    "notes": r"C:\Users\Public\Documents\notes.txt",
}

# ---------- TOOL FUNCTION ----------
def open_file_or_app(app_name: str) -> str:
    """Safely open an allowlisted app/file on Windows."""
    app_name = app_name.strip().lower()
    if app_name not in ALLOWLIST:
        return f"❌ '{app_name}' is not in the allowlist."

    path = ALLOWLIST[app_name]
    try:
        if platform.system().lower().startswith("windows"):
            os.startfile(path)
            return f"✅ Opened: {path}"
        else:
            return "⚠️ This feature only works on Windows."
    except Exception as e:
        return f"❌ Failed to open {path}: {e}"

# ---------- TOOL SCHEMA ----------
tools = [
    {
        "type": "function",
        "function": {
            "name": "open_file_or_app",
            "description": "Open a safe allowlisted app or file on Windows.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "Name of the app or file to open (must exist in allowlist).",
                    }
                },
                "required": ["app_name"],
            },
        },
    }
]

# ---------- AGENT LOOP ----------
def run_agent():
    print("🤖 Windows File Opener Agent (LLM-driven)")
    print("Type a command like: open notepad, launch chrome, open calculator")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("🗣️ You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        # Step 1: Send to LLM with tool support
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # You can use 'gpt-4o' if available
            messages=[
                {
                    "role": "system",
                    "content": "You are a desktop assistant that helps open apps or files on Windows safely. Use the function tool to perform actions.",
                },
                {"role": "user", "content": user_input},
            ],
            tools=tools,
        )

        # Step 2: Check if LLM requested a tool call
        message = response.choices[0].message

        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                args = tool_call.function.arguments

                if func_name == "open_file_or_app":
                    import json
                    try:
                        params = json.loads(args)
                        app_name = params.get("app_name")
                        result = open_file_or_app(app_name)
                        print("🧠 Agent:", result)
                    except Exception as e:
                        print("❌ Error parsing tool args:", e)
        else:
            # Normal text response
            print("💬 Agent:", message.content)


if __name__ == "__main__":
    run_agent()
