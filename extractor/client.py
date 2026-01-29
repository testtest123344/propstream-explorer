"""PropStream API client with authentication, rate limiting, and retry logic."""

import json
import random
import time
from datetime import datetime, date
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class RateLimitExceeded(Exception):
    """Raised when rate limits are exceeded."""
    pass


class PropStreamClient:
    """Client for interacting with PropStream API."""

    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the PropStream client.

        Args:
            config_path: Path to the configuration JSON file.
        """
        self.config = self._load_config(config_path)
        self.base_url = self.config.get("base_url", "https://api.propstream.com")
        self.auth_token = self.config.get("auth_token", "")
        self.max_retries = self.config.get("max_retries", 3)
        self.timeout = self.config.get("timeout", 30)
        
        # Anti-detection: Random delay settings
        self.min_delay = self.config.get("min_delay", 0.5)
        self.max_delay = self.config.get("max_delay", 3.0)
        
        # Anti-detection: Rate limits
        self.hourly_limit = self.config.get("hourly_limit", 100)
        self.daily_limit = self.config.get("daily_limit", 500)
        
        # Request tracking
        self._last_request_time: Optional[float] = None
        self._session_start = time.time()
        self._session_request_count = 0
        self._request_log_path = Path("data/.request_log")
        
        self._session = self._create_session()

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Config file not found: {config_path}\n"
                "Copy config.example.json to config.json and add your auth token."
            )
        
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update(self._get_default_headers())
        
        return session

    def _get_default_headers(self) -> dict:
        """Get default headers for API requests."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
            "Referer": "https://app.propstream.com/search",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        
        if self.auth_token:
            # PropStream uses X-Auth-Token header
            headers["X-Auth-Token"] = self.auth_token
        
        return headers

    def _rate_limit(self) -> None:
        """Enforce rate limiting with random delays for anti-detection."""
        # Check limits before making request
        self._check_limits()
        
        # Random delay between min_delay and max_delay
        delay = random.uniform(self.min_delay, self.max_delay)
        
        # If we've made a recent request, ensure minimum delay
        if self._last_request_time is not None:
            elapsed = time.time() - self._last_request_time
            if elapsed < delay:
                sleep_time = delay - elapsed
                time.sleep(sleep_time)
        else:
            # First request - add a small random delay anyway
            time.sleep(random.uniform(0.1, 0.5))
        
        self._last_request_time = time.time()
        
        # Track this request
        self._session_request_count += 1
        self._log_request()

    def _check_limits(self) -> None:
        """Check if we've exceeded hourly or daily limits."""
        # Check hourly limit (session-based)
        session_duration = time.time() - self._session_start
        if session_duration < 3600:  # Within the same hour
            if self._session_request_count >= self.hourly_limit:
                remaining = 3600 - session_duration
                raise RateLimitExceeded(
                    f"Hourly limit of {self.hourly_limit} requests reached. "
                    f"Wait {int(remaining / 60)} minutes or restart the session."
                )
            elif self._session_request_count >= self.hourly_limit * 0.8:
                remaining = self.hourly_limit - self._session_request_count
                print(f"Warning: Approaching hourly limit ({remaining} requests remaining)")
        else:
            # Reset hourly counter after an hour
            self._session_start = time.time()
            self._session_request_count = 0
        
        # Check daily limit (file-based)
        daily_count = self._get_daily_request_count()
        if daily_count >= self.daily_limit:
            raise RateLimitExceeded(
                f"Daily limit of {self.daily_limit} requests reached. "
                "Try again tomorrow."
            )
        elif daily_count >= self.daily_limit * 0.8:
            remaining = self.daily_limit - daily_count
            print(f"Warning: Approaching daily limit ({remaining} requests remaining)")

    def _get_daily_request_count(self) -> int:
        """Get the number of requests made today."""
        if not self._request_log_path.exists():
            return 0
        
        today = date.today().isoformat()
        count = 0
        
        try:
            with open(self._request_log_path, "r") as f:
                for line in f:
                    if line.startswith(today):
                        count += 1
        except Exception:
            return 0
        
        return count

    def _log_request(self) -> None:
        """Log this request for daily tracking."""
        # Ensure data directory exists
        self._request_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Clean old entries (keep only today's)
        today = date.today().isoformat()
        existing_lines = []
        
        if self._request_log_path.exists():
            try:
                with open(self._request_log_path, "r") as f:
                    existing_lines = [line for line in f if line.startswith(today)]
            except Exception:
                existing_lines = []
        
        # Add new entry
        timestamp = datetime.now().isoformat()
        existing_lines.append(f"{timestamp}\n")
        
        # Write back
        try:
            with open(self._request_log_path, "w") as f:
                f.writelines(existing_lines)
        except Exception:
            pass  # Don't fail if we can't write the log

    def get_request_stats(self) -> dict:
        """Get current request statistics."""
        session_duration = time.time() - self._session_start
        daily_count = self._get_daily_request_count()
        
        return {
            "session_requests": self._session_request_count,
            "session_duration_minutes": int(session_duration / 60),
            "hourly_limit": self.hourly_limit,
            "hourly_remaining": max(0, self.hourly_limit - self._session_request_count),
            "daily_requests": daily_count,
            "daily_limit": self.daily_limit,
            "daily_remaining": max(0, self.daily_limit - daily_count),
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        **kwargs,
    ) -> dict:
        """
        Make an API request with rate limiting.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            **kwargs: Additional arguments for requests

        Returns:
            JSON response as dictionary

        Raises:
            requests.RequestException: If the request fails after retries
        """
        self._rate_limit()
        
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=self.timeout,
                **kwargs,
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.JSONDecodeError:
            # Return raw text if not JSON
            return {"raw_response": response.text, "status_code": response.status_code}
        
        except requests.exceptions.HTTPError as e:
            error_info = {
                "error": str(e),
                "status_code": e.response.status_code if e.response else None,
                "response_text": e.response.text if e.response else None,
            }
            raise requests.RequestException(f"API request failed: {error_info}") from e

    def get(self, endpoint: str, params: Optional[dict] = None, **kwargs) -> dict:
        """Make a GET request."""
        return self._make_request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint: str, data: Optional[dict] = None, **kwargs) -> dict:
        """Make a POST request."""
        return self._make_request("POST", endpoint, data=data, **kwargs)

    # -------------------------------------------------------------------------
    # PropStream API methods (based on discovered endpoints)
    # -------------------------------------------------------------------------

    def get_property_by_id(
        self,
        property_id: str,
        address: Optional[str] = None,
        apn: Optional[str] = None,
        city_id: Optional[str] = None,
        address_type: str = "P",
    ) -> dict:
        """
        Get property details by PropStream property ID.

        Args:
            property_id: The PropStream property ID
            address: Street address (URL encoded)
            apn: Assessor's Parcel Number
            city_id: PropStream city ID
            address_type: Address type (default 'P')

        Returns:
            Property details as dictionary
        """
        params = {
            "id": property_id,
            "addressType": address_type,
        }
        
        if address:
            params["streetAddress"] = address
        if apn:
            params["apn"] = apn
        if city_id:
            params["cityId"] = city_id

        return self.get("/eqbackend/resource/auth/ps4/property", params=params)

    def search_properties(
        self,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
        county: Optional[str] = None,
        apn: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        """
        Search for properties based on criteria.

        Note: You may need to discover the exact search endpoint by
        performing searches in the browser and checking Network tab.

        Args:
            address: Street address to search
            city: City name
            state: State abbreviation (e.g., 'CA')
            zip_code: ZIP code
            county: County name
            apn: Assessor's Parcel Number
            limit: Maximum results to return
            offset: Pagination offset

        Returns:
            Search results as dictionary
        """
        # Build search query - PropStream likely uses a different structure
        # This is a placeholder - check browser DevTools for actual search endpoint
        params = {}
        
        if address:
            params["streetAddress"] = address
        if city:
            params["city"] = city
        if state:
            params["state"] = state
        if zip_code:
            params["zip"] = zip_code
        if county:
            params["county"] = county
        if apn:
            params["apn"] = apn

        # Try the search endpoint - may need adjustment
        return self.get("/eqbackend/resource/auth/ps4/search", params=params)

    def get_property_details(self, property_id: str) -> dict:
        """
        Get detailed information for a specific property.

        Args:
            property_id: The property's unique identifier

        Returns:
            Property details as dictionary
        """
        return self.get_property_by_id(property_id)

    def get_property_by_address(self, address: str, city: str, state: str) -> dict:
        """
        Look up a property by its full address.

        Note: This may require a search first to get the property ID,
        then fetching details. Check browser DevTools for the flow.

        Args:
            address: Street address
            city: City name
            state: State abbreviation

        Returns:
            Property details as dictionary
        """
        return self.search_properties(address=address, city=city, state=state)

    def search_by_zip(self, zip_code: str, limit: int = 100) -> dict:
        """
        Search all properties in a ZIP code.

        Args:
            zip_code: The ZIP code to search
            limit: Maximum results

        Returns:
            List of properties
        """
        return self.search_properties(zip_code=zip_code, limit=limit)

    def search_by_county(self, county: str, state: str, limit: int = 100) -> dict:
        """
        Search all properties in a county.

        Args:
            county: County name
            state: State abbreviation
            limit: Maximum results

        Returns:
            List of properties
        """
        return self.search_properties(county=county, state=state, limit=limit)

    def search_address(self, query: str) -> list:
        """
        Search for properties by address using autocomplete.

        Args:
            query: Address search string (partial or full address)

        Returns:
            List of matching address suggestions with property IDs
        """
        result = self.get("/eqbackend/resource/auth/ps4/property/suggestionsnew", params={"q": query})
        # The API may return a list directly or wrapped in an object
        if isinstance(result, list):
            return result
        return result.get("suggestions", result.get("results", []))

    def lookup_address(self, address: str, fetch_details: bool = True) -> dict:
        """
        Search for an address and optionally fetch full property details.

        This combines the autocomplete search with property detail fetch
        for a seamless address-to-details lookup.

        Args:
            address: Full or partial address string to search
            fetch_details: If True, fetch full property details for top match

        Returns:
            If fetch_details=True: Full property details dict
            If fetch_details=False: List of matching suggestions
        """
        # First, search for matching addresses
        suggestions = self.search_address(address)
        
        if not suggestions:
            return {"error": "No matching addresses found", "query": address}
        
        if not fetch_details:
            return {"suggestions": suggestions}
        
        # Get the top match
        top_match = suggestions[0]
        property_id = top_match.get("id") or top_match.get("propertyId")
        
        if not property_id:
            return {"error": "No property ID in suggestion", "suggestion": top_match}
        
        # Fetch full property details
        return self.get_property_by_id(str(property_id))

    def test_connection(self) -> bool:
        """
        Test if the API connection and authentication work.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Test with a known property ID from your screenshots
            # This validates the auth token is working
            response = self._session.get(
                f"{self.base_url}/eqbackend/resource/auth/ps4/property",
                params={"id": "1863342326"},
                timeout=self.timeout,
            )
            return response.status_code == 200
        except Exception:
            return False

    def set_custom_headers(self, headers: dict) -> None:
        """
        Add custom headers to the session.
        
        Useful when PropStream requires additional headers discovered
        from browser DevTools.

        Args:
            headers: Dictionary of headers to add
        """
        self._session.headers.update(headers)

    def set_cookies(self, cookies: dict) -> None:
        """
        Set cookies for the session.
        
        Some APIs use cookie-based authentication instead of tokens.

        Args:
            cookies: Dictionary of cookies to set
        """
        self._session.cookies.update(cookies)
