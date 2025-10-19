
# from __future__ import annotations

# import asyncio
# import openai
# import os
# import json
# import time
# # import semantic_memory
# from datetime import datetime
# from dataclasses import dataclass, asdict
# from typing import List, Dict, Any, Optional
# from dotenv import load_dotenv
# from livekit import agents
# from livekit.agents import AgentSession, Agent, RoomInputOptions
# from livekit.plugins import google

# # --- Your existing imports ---
# from Nobi_prompts import build_behavior_prompts, build_reply_prompts, build_friends_prompts



# from Nobi_google_search import google_search, get_current_datetime
# from Nobi_window_CTRL import open, close, open_folder, play_file
# from Nobi_file_opner import Play_file
# from keyboard_mouse_CTRL import (
#     move_cursor_tool, mouse_click_tool, scroll_cursor_tool
# )
#          # ✅ Import
# # from audio_utils import save_audio_chunk  # ✅ Import

# # --- Import Tools from separate file ---
# from Nobi_tools import TOOLS

# # ---------------- Load env & prompts ---------------- #
# load_dotenv()
# behavior_prompts = build_behavior_prompts()
# Reply_prompts = build_reply_prompts()

# class Assistant(Agent):
#     def __init__(self) -> None:
#         super().__init__(
#             instructions=behavior_prompts,
#             tools=TOOLS,
#         )


   
#     async def process_user_message(self, session: AgentSession, user_id: str, message: str, audio_file: str = None):
#         """
#         Handle user input → check speaker voice lock → generate reply → save.
#         """


#         # ✅ Context + reply
#         # context = self.memory.build_context_for_query(user_id, message)
#         reply = await session.generate_reply(
#             instructions=f"""{Reply_prompts}

# ### Conversation Context:


# ### User says:
# {message}

# ### Assistant:"""
#         )

#         reply_text = str(reply)
#         self.memory.save_interaction(user_id, "user", message)
#         self.memory.save_interaction(user_id, "assistant", reply_text)

#         return reply_text
    
# async def main():
#     print(await google_search("Mahadev wallpaper"))
#     print(await get_current_datetime())

# # ---------------- Entrypoint ---------------- #
# async def entrypoint(ctx: agents.JobContext):
#     session = AgentSession(
#         llm=google.beta.realtime.RealtimeModel(voice="Charon")
#     )

#     assistant = Assistant()

#     await session.start(
#         room=ctx.room,
#         agent=assistant,
#         room_input_options=RoomInputOptions(
#             noise_cancellation="high",   # strong noise filter
#             video_enabled=False,
#             audio_enabled=True,
#         ),
#     )

#     await ctx.connect()

#     # ✅ Startup Greeting
#     greeting = await session.generate_reply(instructions=Reply_prompts)
#     greeting_text = str(greeting)
#     print("[Startup Greeting]", greeting_text)
#     # assistant.memory.save_interaction("system", "assistant", greeting_text)


# if __name__ == "__main__":
#     agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))




from __future__ import annotations
import asyncio
import os
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import Agent, AgentSession, RoomInputOptions
from livekit.plugins import google
from livekit import rtc

# --- Custom Imports --- #
from Nobi_google_search import google_search, get_current_datetime
from Nobi_window_CTRL import open, close, open_folder, play_file
from Nobi_file_opner import Play_file
from keyboard_mouse_CTRL import move_cursor_tool, mouse_click_tool, scroll_cursor_tool
from Nobi_tools import TOOLS
from Nobi_prompts import build_behavior_prompts, build_reply_prompts
from memory_loop import MemoryExtractor
from resoning import thinking_capability
import datetime


# ---------------- Load ENV ---------------- #
load_dotenv()

behavior_prompts = build_behavior_prompts()
Reply_prompts = build_reply_prompts()


# ==========================================================
# 🧰 Noise Cancellation Auto Compatibility Helper
# ==========================================================
def get_noise_cancellation():
    """
    Automatically creates a compatible NoiseCancellationOptions object
    for both old and new versions of livekit.rtc.
    """
    try:
        # 🆕 Newer versions of LiveKit use level argument
        return rtc.NoiseCancellationOptions(level="high")
    except TypeError:
        try:
            # 🧩 Older versions only support 'enabled' flag
            return rtc.NoiseCancellationOptions(enabled=True)
        except Exception as e:
            print("[Warning] Could not enable noise cancellation:", e)
            return None


# ====================================================================
# 🧠 ASSISTANT CLASS (Smart Context + Recall + Memory)
# ====================================================================
class Assistant(Agent):
    def __init__(self, chat_ctx) -> None:
        super().__init__(
            chat_ctx=chat_ctx,
            instructions=behavior_prompts,
            llm=google.beta.realtime.RealtimeModel(voice="Charon"),
            tools=[thinking_capability]
        )


# ====================================================================
# 🚀 ENTRYPOINT FUNCTION
# ====================================================================
async def entrypoint(ctx: agents.JobContext):
    # Create a new Agent session
    session = AgentSession(preemptive_generation=True)
    current_ctx = session.history.items  # current memory chat context

    # ✅ Auto noise cancellation handling
    noise_cancellation = get_noise_cancellation()

    # Start the session with assistant and room settings
    await session.start(
        room=ctx.room,
        agent=Assistant(chat_ctx=current_ctx),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation,
            video_enabled=False,
            audio_enabled=True,
        ),
    )

    # Generate reply based on behavior + reply prompts
    await session.generate_reply(instructions=Reply_prompts)

    # 🧠 Memory extraction and processing
    conv_ctx = MemoryExtractor()
    await conv_ctx.run(current_ctx)


# ====================================================================
# 🏁 MAIN
# ====================================================================
if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
