"""
Nobi Tools Integration
----------------------
सारे tools यहां पर import करके एक list TOOLS में डाल दिए गए हैं।
"""

from Nobi_google_search import google_search, get_current_datetime
from Nobi_window_CTRL import open, close, folder_file
from Nobi_file_opner import Play_file
from keyboard_mouse_CTRL import (
    move_cursor_tool, mouse_click_tool, scroll_cursor_tool,
    type_text_tool, press_key_tool, swipe_gesture_tool,
    press_hotkey_tool, control_volume_tool
)



# सारे tools एक ही जगह
TOOLS = [
    google_search, get_current_datetime,
    open, close, folder_file, Play_file,
    move_cursor_tool, mouse_click_tool, scroll_cursor_tool,
    type_text_tool, press_key_tool, press_hotkey_tool,
    control_volume_tool, swipe_gesture_tool,
]


