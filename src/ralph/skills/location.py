import requests
import logging

def get_current_location() -> str:
    """
    Uses ip-api.com (JSON format) to determine the current physical location
    based on the system's IP address. No API key required for non-commercial use.
    """
    url = "http://ip-api.com/json/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "success":
            location_info = (
                f"City: {data.get('city')}\n"
                f"Region: {data.get('regionName')}\n"
                f"Country: {data.get('country')}\n"
                f"Lat/Lon: {data.get('lat')}, {data.get('lon')}\n"
                f"Timezone: {data.get('timezone')}\n"
                f"ISP: {data.get('isp')}"
            )
            return location_info
        else:
            return f"Geolocation failed: {data.get('message', 'Unknown error')}"
    except Exception as e:
        logging.error(f"Geolocation Error: {e}")
        return f"Error retrieving location: {e}"