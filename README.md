# PropStream Data Extractor

A Python tool for extracting property data from PropStream by replicating authenticated API calls. Exports data to JSON, CSV, or SQLite database.

## Prerequisites

- Python 3.8+
- An active PropStream subscription
- Your PropStream authentication token (see [Capturing Your Auth Token](#capturing-your-auth-token))

## Installation

1. Clone or download this repository

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your configuration:
   ```bash
   # Copy the example config
   copy config.example.json config.json
   
   # Edit config.json and add your auth token
   ```

## Capturing Your Auth Token

To use this tool, you need to capture your authentication token from PropStream. Here's how:

### Step 1: Open PropStream and DevTools

1. Log into PropStream in your web browser (Chrome recommended)
2. Press `F12` to open Developer Tools
3. Click the **Network** tab
4. Check the "Preserve log" checkbox

### Step 2: Capture API Requests

1. Perform a property search in PropStream
2. In the Network tab, look for requests to `api.propstream.com` (or similar)
3. Click on one of the API requests

### Step 3: Find Your Auth Token

1. In the request details, click the **Headers** tab
2. Look for one of these in the Request Headers:
   - `Authorization: Bearer <your_token>`
   - `Cookie` header with session information
   - `X-Auth-Token` or similar custom header

3. Copy the full token value

### Step 4: Add Token to Config

Edit your `config.json` file:

```json
{
    "auth_token": "your_copied_token_here",
    "base_url": "https://api.propstream.com",
    "rate_limit_delay": 1.0,
    "max_retries": 3,
    "timeout": 30
}
```

**Note:** If PropStream uses cookie-based authentication, you may need to modify the client to use cookies instead. See [Advanced Configuration](#advanced-configuration).

## Usage

### Test Connection

Verify your authentication is working:

```bash
python main.py test
```

### Search Properties

Search by various criteria:

```bash
# Search by ZIP code
python main.py search --zip 90210

# Search by city and state
python main.py search --city "Los Angeles" --state CA

# Search by county
python main.py search --county "Los Angeles" --state CA

# Search with output to file
python main.py search --zip 90210 -o data/results.json

# Search with multiple export formats
python main.py search --zip 90210 -o data/results -f json csv sqlite
```

### Look Up Specific Property

```bash
python main.py lookup "123 Main St" "Los Angeles" "CA"

# With output
python main.py lookup "123 Main St" "Los Angeles" "CA" -o data/property.json
```

### Batch Search

Search multiple ZIP codes or counties:

```bash
# Multiple ZIP codes
python main.py batch --zips 90210 90211 90212 -o data/beverly_hills.csv -f csv

# Multiple counties
python main.py batch --counties "Los Angeles" "Orange" --state CA -o data/socal.db -f sqlite
```

### Initialize Database

Create an optimized SQLite database with indexes:

```bash
python main.py init-db -o data/properties.db
```

## Export Formats

### JSON
Full property data with nested structure. Use `--raw` flag to include original API response.

### CSV
Flattened data suitable for spreadsheets. All nested fields are converted to columns.

### SQLite
Database with indexed columns for fast queries. Schema includes:
- Primary key on property ID
- Indexes on ZIP code, city/state, county, APN, owner name
- Indexes on property type, estimated value, absentee status, tax delinquent

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `auth_token` | Your PropStream authentication token | Required |
| `base_url` | PropStream API base URL | `https://api.propstream.com` |
| `rate_limit_delay` | Seconds between requests | `1.0` |
| `max_retries` | Retry attempts for failed requests | `3` |
| `timeout` | Request timeout in seconds | `30` |

## Advanced Configuration

### Cookie-Based Authentication

If PropStream uses cookies instead of Bearer tokens, modify your usage:

```python
from extractor import PropStreamClient

client = PropStreamClient()
client.set_cookies({
    "session_id": "your_session_cookie",
    "other_cookie": "value",
})
```

### Custom Headers

If PropStream requires additional headers:

```python
client.set_custom_headers({
    "X-Custom-Header": "value",
    "X-API-Version": "2",
})
```

### Discovering the API

The API endpoints in this tool are placeholders. You'll need to discover the actual endpoints by:

1. Monitoring Network requests in DevTools
2. Looking for patterns like:
   - `/v1/properties/search`
   - `/v1/properties/{id}`
   - `/api/search`
3. Updating `extractor/client.py` with the correct endpoints

## Project Structure

```
scraper/
├── main.py              # CLI entry point
├── config.json          # Your configuration (gitignored)
├── config.example.json  # Example configuration
├── requirements.txt     # Python dependencies
├── extractor/
│   ├── __init__.py
│   ├── client.py        # PropStream API client
│   ├── models.py        # Property data models
│   └── export.py        # Export functions
└── data/                # Output directory
```

## Troubleshooting

### "Config file not found"
Copy `config.example.json` to `config.json` and add your auth token.

### "Connection failed"
- Verify your token is correct and not expired
- Tokens typically expire after a period - re-capture from browser if needed
- Check if PropStream's API URL has changed

### "No properties found"
- The API endpoints may be different - check DevTools for actual endpoints
- Your search criteria might not match PropStream's expected format

### Rate Limiting
If you're getting blocked:
- Increase `rate_limit_delay` in config.json
- PropStream may have stricter rate limits during peak hours

## Legal Notice

This tool is for personal use with your own PropStream subscription. Review PropStream's Terms of Service regarding automated access and data export. The tool uses your authenticated session - it does not bypass any security measures.

Use responsibly and respect PropStream's API limits.

## License

MIT License - Use at your own risk.
