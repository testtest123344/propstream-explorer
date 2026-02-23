"""Flask API server for PropStream data."""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractor import PropStreamClient, RateLimitExceeded

# Determine if we're in production
IS_PRODUCTION = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('PRODUCTION')

# Path to React build
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web', 'dist')

app = Flask(__name__, static_folder=STATIC_FOLDER if IS_PRODUCTION else None)
CORS(app)  # Enable CORS for React dev server

# Initialize client once
client = None

def get_client():
    """Get or create PropStream client."""
    global client
    if client is None:
        # In production, use environment variable for auth token
        auth_token = os.environ.get('PROPSTREAM_AUTH_TOKEN')
        if auth_token:
            # Create client with env-based config
            client = PropStreamClientFromEnv(auth_token)
        else:
            # Fall back to config file for local development
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
            client = PropStreamClient(config_path)
    return client


class PropStreamClientFromEnv(PropStreamClient):
    """PropStream client that uses environment variables instead of config file."""
    
    def __init__(self, auth_token):
        # Skip parent __init__ and set up manually
        self.config = {
            'auth_token': auth_token,
            'base_url': os.environ.get('PROPSTREAM_BASE_URL', 'https://app.propstream.com'),
            'min_delay': float(os.environ.get('MIN_DELAY', '0.5')),
            'max_delay': float(os.environ.get('MAX_DELAY', '3.0')),
            'hourly_limit': int(os.environ.get('HOURLY_LIMIT', '100')),
            'daily_limit': int(os.environ.get('DAILY_LIMIT', '500')),
            'max_retries': 3,
            'timeout': 30,
        }
        self.base_url = self.config['base_url']
        self.auth_token = self.config['auth_token']
        self.max_retries = self.config['max_retries']
        self.timeout = self.config['timeout']
        self.min_delay = self.config['min_delay']
        self.max_delay = self.config['max_delay']
        self.hourly_limit = self.config['hourly_limit']
        self.daily_limit = self.config['daily_limit']
        
        self._last_request_time = None
        self._session_start = __import__('time').time()
        self._session_request_count = 0
        self._request_log_path = __import__('pathlib').Path('/tmp/.request_log')
        
        self._session = self._create_session()


@app.route('/api/lookup', methods=['GET'])
def lookup_address():
    """Look up a property by address."""
    address = request.args.get('address', '').strip()
    
    if not address:
        return jsonify({'error': 'Address parameter required'}), 400
    
    try:
        c = get_client()
        result = c.lookup_address(address)
        
        if 'error' in result:
            return jsonify(result), 404
        
        return jsonify(result)
    
    except RateLimitExceeded as e:
        return jsonify({'error': str(e), 'type': 'rate_limit'}), 429
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['GET'])
def search_address():
    """Search for addresses (autocomplete)."""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 3:
        return jsonify([])
    
    try:
        c = get_client()
        suggestions = c.search_address(query)
        return jsonify(suggestions[:10])  # Return top 10
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get request statistics."""
    try:
        c = get_client()
        stats = c.get_request_stats()
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})


@app.route('/webhook/lead-enriched', methods=['POST'])
def lead_enriched_webhook():
    """
    Called by Dialer after enrichment completes.
    Wakes OpenClaw main session to run lead intel analysis.
    Expects JSON: {"filing_id": 123, "lead_id": 456, "address": "...", "owner": "..."}
    """
    data = request.get_json(silent=True) or {}
    filing_id = data.get('filing_id', '?')
    lead_id = data.get('lead_id', '?')
    owner = data.get('owner', 'Unknown')
    address = data.get('address', '')

    # Trigger agent turn — runs in background so webhook returns immediately
    # The agent turn pulls data, writes analysis, posts note, messages Justin
    try:
        import subprocess
        import threading

        def run_agent():
            try:
                subprocess.run(
                    [
                        'openclaw', 'agent',
                        '-m', f'LEAD_INTEL_TRIGGER: A new lead just finished enrichment. Analyze it now.\n\n'
                              f'lead_id={lead_id}\nfiling_id={filing_id}\nowner={owner}\naddress={address}\n\n'
                              f'Steps:\n'
                              f'1. Pull full data: curl with -H "X-System-Key: ccdf2555deac548ba7fd9b39b395685479cdca363462b4bfd707b9b2a06f97cf" from https://dialer-production-d020.up.railway.app/api/crm/lead/{lead_id}/full-data\n'
                              f'2. Write a natural-language intel analysis (compare ATTOM vs PropStream, flag red flags, note loan details)\n'
                              f'3. Post the note to the lead card: POST /api/crm/notes with same system key, json body lead_id and content\n'
                              f'4. Classify as URGENT/STANDARD/HOLD\n'
                              f'5. Send the analysis to Justin on Telegram using the message tool\n'
                              f'Keep the note concise (5-10 lines). Be specific about data discrepancies.',
                        '--to', '7704575065',
                        '--channel', 'telegram',
                        '--deliver',
                        '--timeout', '300',
                    ],
                    capture_output=True, text=True, timeout=310
                )
            except Exception:
                pass

        # Fire and forget — webhook returns immediately
        thread = threading.Thread(target=run_agent, daemon=True)
        thread.start()

        return jsonify({'status': 'ok', 'message': f'Intel analysis triggered for lead {lead_id}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Serve React static files in production
if IS_PRODUCTION:
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_react(path):
        """Serve React app."""
        if path and os.path.exists(os.path.join(STATIC_FOLDER, path)):
            return send_from_directory(STATIC_FOLDER, path)
        return send_from_directory(STATIC_FOLDER, 'index.html')


if __name__ == '__main__':
    print("Starting PropStream API server...")
    print("API available at http://localhost:5000")
    print("\nEndpoints:")
    print("  GET /api/lookup?address=<address>  - Look up property")
    print("  GET /api/search?q=<query>          - Search addresses")
    print("  GET /api/stats                     - Request statistics")
    print("  GET /api/health                    - Health check")
    print("\nPress Ctrl+C to stop")
    app.run(debug=False, port=5000)
