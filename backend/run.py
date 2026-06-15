import os
import sys
from app import app

# Set UTF-8 encoding for console output
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = False
    print(f"[START] MyWelthAI Backend on http://localhost:{port}")
    print(f"[START] Database: MongoDB")
    app.run(debug=debug, host='0.0.0.0', port=port, threaded=True)
