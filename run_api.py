"""
Run the API server.
"""
from src.api import app
import os

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8000))
    print(f"Starting AI Chief of Staff API on http://localhost:{port}")
    try:
        app.run(debug=True, host='127.0.0.1', port=port)
    except OSError as e:
        if "address already in use" in str(e).lower() or "access" in str(e).lower():
            print(f"\nError: Port {port} is already in use or access denied.")
            print(f"Try using a different port by setting PORT in .env file")
            print(f"Or run: set PORT=8000 && python run_api.py")
        else:
            raise
