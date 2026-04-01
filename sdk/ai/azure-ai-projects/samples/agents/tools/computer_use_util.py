# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
Shared helper functions and classes for Computer Use Agent samples.
"""

import os
import base64
from enum import Enum


class SearchState(Enum):
    """Enum for tracking the state of the simulated web search workflow."""

    INITIAL = "initial"  # Browser search page
    TYPED = "typed"  # Text entered in search box
    PRESSED_ENTER = "pressed_enter"  # Enter key pressed, transitioning to results


def image_to_base64(image_path: str) -> str:
    """Convert an image file to a Base64-encoded string.

    Args:
        image_path: The path to the image file (e.g. 'image_file.png')

    Returns:
        A Base64-encoded string representing the image.

    Raises:
        FileNotFoundError: If the provided file path does not exist.
        OSError: If there's an error reading the file.
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"File not found at: {image_path}")

    try:
        with open(image_path, "rb") as image_file:
            file_data = image_file.read()
        return base64.b64encode(file_data).decode("utf-8")
    except Exception as exc:
        raise OSError(f"Error reading file '{image_path}'") from exc


def load_screenshot_assets():
    """Load and convert screenshot images to base64 data URLs.

    Returns:
        dict: Dictionary mapping state names to screenshot info with filename and data URL

    Raises:
        FileNotFoundError: If any required screenshot asset files are missing
    """
    # Load demo screenshot images from assets directory
    # Flow: search page -> typed search -> search results
    screenshot_paths = {
        "browser_search": os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/cua_browser_search.png")),
        "search_typed": os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/cua_search_typed.png")),
        "search_results": os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/cua_search_results.png")),
    }

    # Convert images to base64 data URLs with filenames
    screenshots = {}
    filename_map = {
        "browser_search": "cua_browser_search.png",
        "search_typed": "cua_search_typed.png",
        "search_results": "cua_search_results.png",
    }

    for key, path in screenshot_paths.items():
        try:
            image_base64 = image_to_base64(path)
            screenshots[key] = {"filename": filename_map[key], "url": f"data:image/png;base64,{image_base64}"}
        except FileNotFoundError as e:
            print(f"Error: Missing required screenshot asset: {e}")
            raise

    return screenshots


def handle_computer_action_and_take_screenshot(action, current_state, screenshots):
    """Process a computer action and simulate its execution.

    In a real implementation, you might want to execute real browser operations
    instead of just printing, take screenshots, and return actual screenshot data.

    Args:
        action: The computer action to process (click, type, key press, etc.)
        current_state: Current SearchState of the simulation
        screenshots: Dictionary of screenshot data

    Returns:
        tuple: (screenshot_info, updated_current_state)
    """
    print(f"Executing computer action: {action.type}")

    # State transitions based on actions
    if action.type == "type" and hasattr(action, "text") and action.text:
        current_state = SearchState.TYPED
        print(f"  Typing text: '{action.text}' - Simulating keyboard input")

    # Check for ENTER key press
    elif (
        action.type in ["key", "keypress"]
        and hasattr(action, "keys")
        and action.keys
        and ("Return" in str(action.keys) or "ENTER" in str(action.keys))
    ):
        current_state = SearchState.PRESSED_ENTER
        print("  -> Detected ENTER key press")

    # Check for click after typing (alternative submit method)
    elif action.type == "click" and current_state == SearchState.TYPED:
        current_state = SearchState.PRESSED_ENTER
        print("  -> Detected click after typing")

    # Provide more realistic feedback based on action type
    if hasattr(action, "x") and hasattr(action, "y"):
        if action.type == "click":
            print(f"  Click at ({action.x}, {action.y}) - Simulating click on UI element")
        elif action.type == "drag":
            path_str = " -> ".join([f"({p.x}, {p.y})" for p in action.path])
            print(f"  Drag path: {path_str} - Simulating drag operation")
        elif action.type == "scroll":
            print(f"  Scroll at ({action.x}, {action.y}) - Simulating scroll action")

    if hasattr(action, "keys") and action.keys:
        print(f"  Key press: {action.keys} - Simulating key combination")

    if action.type == "screenshot":
        print("  Taking screenshot - Capturing current screen state")

    print(f"  -> Action processed: {action.type}")

    # Determine screenshot based on current state
    if current_state == SearchState.PRESSED_ENTER:
        screenshot_info = screenshots["search_results"]
    elif current_state == SearchState.TYPED:
        screenshot_info = screenshots["search_typed"]
    else:  # SearchState.INITIAL
        screenshot_info = screenshots["browser_search"]

    return screenshot_info, current_state


def print_final_output(response):
    """Print the final output when the agent completes the task.

    Args:
        response: The response object containing the agent's final output
    """
    print("No computer calls found. Agent completed the task:")
    final_output = ""
    for item in response.output:
        if item.type == "message":
            contents = item.content
            for part in contents:
                final_output += getattr(part, "text", None) or getattr(part, "refusal", None) or "" + "\n"

    print(f"Final status: {response.status}")
    print(f"Final result: {final_output.strip()}")
