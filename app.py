"""
Kerala Tourism Intelligence & Business Opportunity Platform
Root Application Entry Point
"""
import os
import sys
import webbrowser
import importlib.util
from threading import Timer
from pathlib import Path

# Resolve paths
ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT_DIR / "12_Frontend"

# Ensure 12_Frontend is in python search path
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

# Dynamically load the Flask application module from 12_Frontend/app.py
frontend_app_file = FRONTEND_DIR / "app.py"
spec = importlib.util.spec_from_file_location("frontend_application", str(frontend_app_file))
frontend_application = importlib.util.module_from_spec(spec)
sys.modules["frontend_application"] = frontend_application
spec.loader.exec_module(frontend_application)

# Expose the Flask instance
app = frontend_application.app

def open_browser(port):
    """Opens the user's default browser after the server has launched."""
    try:
        webbrowser.open(f"http://127.0.0.1:{port}")
    except Exception:
        pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    debug_mode = os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes")

    print("\n" + "=" * 68)
    print("  🌴 KERALA TOURISM INTELLIGENCE PLATFORM")
    print(f"  🚀 Server running at: http://127.0.0.1:{port}")
    print("  🌐 Opening web browser automatically...")
    print("  🛑 Press Ctrl + C in this terminal to stop the application")
    print("=" * 68 + "\n")

    # Schedule browser opening
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        Timer(1.2, open_browser, args=[port]).start()

    app.run(host=host, port=port, debug=debug_mode)
