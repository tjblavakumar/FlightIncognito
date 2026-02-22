"""
Flight Incognito - Multi-site flight search launcher with incognito mode
Opens multiple flight aggregator sites in fresh browser incognito/private windows
"""

import streamlit as st
import streamlit.components.v1 as components
from datetime import date, timedelta, datetime
from urllib.parse import quote
from typing import Dict
import subprocess
import platform
import time
import tempfile
import os
import webbrowser
import json
import database as db

# Page config
st.set_page_config(
    page_title="Flight Incognito",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Additional CSS to completely disable sidebar collapse
st.markdown("""
    <style>
        /* Aggressively hide and disable ALL collapse controls */
        section[data-testid="stSidebar"] button,
        section[data-testid="stSidebar"] [role="button"] {
            pointer-events: none !important;
        }
        
        /* Re-enable pointer events for actual sidebar content buttons */
        section[data-testid="stSidebar"] .stButton button,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] button {
            pointer-events: auto !important;
        }
        
        /* Force sidebar to stay open */
        section[data-testid="stSidebar"][aria-expanded="false"] {
            display: block !important;
            margin-left: 0 !important;
            transform: none !important;
        }
        
        /* Hide ALL tooltips globally */
        [data-baseweb="tooltip"],
        [role="tooltip"],
        div[class*="Tooltip"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
        }
        
        /* Specifically target the collapse button area */
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 0 !important;
        }
        
        section[data-testid="stSidebar"] > div:first-child > button {
            display: none !important;
            visibility: hidden !important;
            width: 0 !important;
            height: 0 !important;
            overflow: hidden !important;
        }
    </style>
""", unsafe_allow_html=True)

# Load custom CSS for Ubuntu font
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

try:
    load_css()
except FileNotFoundError:
    pass  # CSS file not found, continue without custom styling

# Hide default Streamlit header
st.markdown("""
    <style>
        /* Hide default Streamlit header */
        header[data-testid="stHeader"] {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize database
db.init_database()

# Load airport data
@st.cache_data
def load_airports():
    """Load airport data from JSON file"""
    try:
        with open("airports.json", "r", encoding="utf-8") as f:
            airports = json.load(f)
        return airports
    except FileNotFoundError:
        st.error("airports.json file not found")
        return []

def format_airport_option(airport: dict) -> str:
    """Format airport for display in dropdown"""
    return f"{airport['code']} - {airport['city']}, {airport['country']} ({airport['name']})"

def get_airport_code_from_selection(selection: str) -> str:
    """Extract airport code from formatted selection"""
    if selection and " - " in selection:
        return selection.split(" - ")[0].strip()
    return selection

def search_airports(query: str, airports: list) -> list:
    """Search airports by code, city, or name"""
    if not query:
        return airports
    
    query = query.lower()
    results = []
    
    for airport in airports:
        if (query in airport['code'].lower() or 
            query in airport['city'].lower() or 
            query in airport['name'].lower()):
            results.append(airport)
    
    return results

# Load airports
airports_data = load_airports()
airport_options = [format_airport_option(airport) for airport in airports_data]

# Initialize session state for form values
if 'load_search' not in st.session_state:
    st.session_state.load_search = None


# URL Generator Functions
def generate_google_flights_url(
    origin: str,
    destination: str,
    depart_date: date,
    return_date: date = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    cabin: str = "Economy",
    trip_type: str = "Round Trip"
) -> str:
    """Generate Google Flights search URL"""
    depart_str = depart_date.strftime("%Y-%m-%d")
    
    if trip_type == "Round Trip" and return_date:
        return_str = return_date.strftime("%Y-%m-%d")
        query = f"Flights from {origin} to {destination} on {depart_str} through {return_str}"
    else:
        query = f"Flights from {origin} to {destination} on {depart_str}"
    
    encoded_query = quote(query)
    return f"https://www.google.com/travel/flights?q={encoded_query}"


def generate_kayak_url(
    origin: str,
    destination: str,
    depart_date: date,
    return_date: date = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    cabin: str = "Economy",
    trip_type: str = "Round Trip"
) -> str:
    """Generate Kayak search URL"""
    depart_str = depart_date.strftime("%Y-%m-%d")
    
    # Build passenger string
    passenger_str = f"{adults}adults" if adults > 0 else ""
    
    # Add children with ages (Kayak format: children-age1-age2-age3)
    if children > 0:
        # Default child ages to 11 for simplicity (can be customized)
        child_ages = "-".join(["11"] * children)
        if passenger_str:
            passenger_str += f"/children-{child_ages}"
        else:
            passenger_str = f"children-{child_ages}"
    
    # Build URL based on trip type
    if trip_type == "Round Trip" and return_date:
        return_str = return_date.strftime("%Y-%m-%d")
        url = f"https://www.kayak.com/flights/{origin}-{destination}/{depart_str}/{return_str}"
    else:
        url = f"https://www.kayak.com/flights/{origin}-{destination}/{depart_str}"
    
    # Add passenger string to URL path
    if passenger_str:
        url += f"/{passenger_str}"
    
    # Add query parameters
    url += "?sort=bestflight_a"
    
    # Note: Kayak doesn't have a standard parameter for infants in lap
    # They are typically handled during booking
    
    return url


def generate_momondo_url(
    origin: str,
    destination: str,
    depart_date: date,
    return_date: date = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    cabin: str = "Economy",
    trip_type: str = "Round Trip"
) -> str:
    """Generate Momondo search URL"""
    depart_str = depart_date.strftime("%Y-%m-%d")
    
    if trip_type == "Round Trip" and return_date:
        return_str = return_date.strftime("%Y-%m-%d")
        url = f"https://www.momondo.com/flights/{origin}-{destination}/{depart_str}/{return_str}"
    else:
        url = f"https://www.momondo.com/flights/{origin}-{destination}/{depart_str}"
    
    # Add passengers
    url += f"?adults={adults}"
    if children > 0:
        url += f"&children={children}"
    if infants > 0:
        url += f"&infants={infants}"
    
    return url


def generate_expedia_url(
    origin: str,
    destination: str,
    depart_date: date,
    return_date: date = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    cabin: str = "Economy",
    trip_type: str = "Round Trip"
) -> str:
    """Generate Expedia search URL using their deeplink format"""
    depart_str = depart_date.strftime("%Y-%m-%d")

    if trip_type == "Round Trip" and return_date:
        return_str = return_date.strftime("%Y-%m-%d")
        url = f"https://www.expedia.com/go/flight/search/Roundtrip/{depart_str}/{return_str}"
    else:
        # For one-way, use same date for both parameters
        url = f"https://www.expedia.com/go/flight/search/oneway/{depart_str}/{depart_str}"

    # Add parameters
    url += f"?load=1&FromAirport={origin}&ToAirport={destination}&FromTime=362&NumAdult={adults}"

    if children > 0:
        url += f"&NumChild={children}"
        # Add ages for children (default to age 10 for simplicity)
        for i in range(1, children + 1):
            url += f"&Child{i}Age=10"

    if infants > 0:
        url += f"&InfantInSeat={infants}"

    return url



def generate_priceline_url(
    origin: str,
    destination: str,
    depart_date: date,
    return_date: date = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    cabin: str = "Economy",
    trip_type: str = "Round Trip"
) -> str:
    """Generate Priceline search URL"""
    depart_str = depart_date.strftime("%Y%m%d")
    
    # Map cabin class
    cabin_map = {
        "Economy": "ECO",
        "Premium Economy": "PEC",
        "Business": "BUS",
        "First": "FST"
    }
    cabin_code = cabin_map.get(cabin, "ECO")

    if trip_type == "Round Trip" and return_date:
        return_str = return_date.strftime("%Y%m%d")
        url = f"https://www.priceline.com/m/fly/search/{origin}-{destination}-{depart_str}/{destination}-{origin}-{return_str}/"
    else:
        url = f"https://www.priceline.com/m/fly/search/{origin}-{destination}-{depart_str}/"

    # Add passengers and cabin
    url += f"?cabin-class={cabin_code}&no-date-search=false&search-type=0110&num-adults={adults}&num-children={children}"
    
    if infants > 0:
        url += f"&num-infants={infants}"

    return url



def generate_hopper_url(
    origin: str,
    destination: str,
    depart_date: date,
    return_date: date = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    cabin: str = "Economy",
    trip_type: str = "Round Trip"
) -> str:
    """Generate Hopper search URL"""
    depart_str = depart_date.strftime("%Y-%m-%d")

    # Hopper's web interface format
    if trip_type == "Round Trip" and return_date:
        return_str = return_date.strftime("%Y-%m-%d")
        url = f"https://www.hopper.com/flights/shop/?origin={origin}&destination={destination}&departureDate={depart_str}&returnDate={return_str}&tripCategory=round_trip"
    else:
        url = f"https://www.hopper.com/flights/shop/?origin={origin}&destination={destination}&departureDate={depart_str}&tripCategory=one_way"

    # Add passengers
    url += f"&adultsCount={adults}&childrenCount={children}&infantsInSeatCount={infants}&infantsOnLapCount=0"
    url += "&flightShopProgress=1&flightShopType=default&maxPrice=9007199254740991&noLCC=false&stopsOption=ANY_NUMBER"

    return url



def generate_cheapoair_url(
    origin: str,
    destination: str,
    depart_date: date,
    return_date: date = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    cabin: str = "Economy",
    trip_type: str = "Round Trip"
) -> str:
    """Generate CheapOair search URL"""
    depart_str = depart_date.strftime("%m/%d/%Y")

    # Map cabin class
    cabin_map = {
        "Economy": "1",
        "Premium Economy": "2",
        "Business": "3",
        "First": "4"
    }
    cabin_code = cabin_map.get(cabin, "1")

    if trip_type == "Round Trip" and return_date:
        return_str = return_date.strftime("%m/%d/%Y")
        url = f"https://www.cheapoair.com/air/listing?from={origin}&dtype1=City&to={destination}&rtype1=City&fromDt={depart_str}&toDt={return_str}&fromTm=1100&toTm=1100&rt=true"
    else:
        url = f"https://www.cheapoair.com/air/listing?from={origin}&dtype1=City&to={destination}&rtype1=City&fromDt={depart_str}&fromTm=1100&rt=false"

    # Add passengers and cabin
    url += f"&ad={adults}&se=0&ch={children}&infl={infants}&infs=0&class={cabin_code}"
    url += "&airpref=&preftyp=1&daan=&raan=&dst=&rst=&IsNS=false&lang=en-US&searchInitiated=true"
    
    # Add child age if children present
    if children > 0:
        url += "&childAge=c0-10"

    return url



def generate_skyscanner_url(
    origin: str,
    destination: str,
    depart_date: date,
    return_date: date = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    cabin: str = "Economy",
    trip_type: str = "Round Trip"
) -> str:
    """Generate Skyscanner search URL (uses YYMMDD format)"""
    # Skyscanner uses YYMMDD format
    depart_str = depart_date.strftime("%y%m%d")
    
    if trip_type == "Round Trip" and return_date:
        return_str = return_date.strftime("%y%m%d")
        url = f"https://www.skyscanner.com/transport/flights/{origin.lower()}/{destination.lower()}/{depart_str}/{return_str}/"
        rtn = "1"
    else:
        url = f"https://www.skyscanner.com/transport/flights/{origin.lower()}/{destination.lower()}/{depart_str}/"
        rtn = "0"
    
    # Map cabin class to Skyscanner format
    cabin_map = {
        "Economy": "economy",
        "Premium Economy": "premiumeconomy",
        "Business": "business",
        "First": "first"
    }
    cabin_code = cabin_map.get(cabin, "economy")
    
    # Build query parameters
    params = []
    params.append(f"adultsv2={adults}")
    params.append(f"cabinclass={cabin_code}")
    
    # Add children with ages (format: age1|age2|age3, URL encoded as %7C)
    if children > 0:
        # Default child ages to 10 for simplicity
        child_ages = "%7C".join(["10"] * children)
        params.append(f"childrenv2={child_ages}")
    
    params.append("ref=home")
    params.append(f"rtn={rtn}")
    params.append("preferdirects=false")
    params.append("outboundaltsenabled=false")
    params.append("inboundaltsenabled=false")
    
    # Note: Skyscanner doesn't have a standard parameter for infants in the URL
    # They are typically handled during the search results
    
    url += "?" + "&".join(params)
    
    return url


def generate_all_urls(
    origin: str,
    destination: str,
    depart_date: date,
    return_date: date = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    cabin: str = "Economy",
    trip_type: str = "Round Trip",
    selected_sites: list = None
) -> Dict[str, str]:
    """Generate URLs for all supported flight search sites"""
    
    # Normalize airport codes to uppercase
    origin = origin.upper().strip()
    destination = destination.upper().strip()
    
    # All available sites
    all_sites = {
        "Google Flights": generate_google_flights_url,
        "Kayak": generate_kayak_url,
        "Momondo": generate_momondo_url,
        "Skyscanner": generate_skyscanner_url,
        "Expedia": generate_expedia_url,
        "Priceline": generate_priceline_url,
        "Hopper": generate_hopper_url,
        "CheapOair": generate_cheapoair_url
    }
    
    # If no sites selected, use all
    if not selected_sites:
        selected_sites = list(all_sites.keys())
    
    urls = {}
    for site_name in selected_sites:
        if site_name in all_sites:
            urls[site_name] = all_sites[site_name](
                origin, destination, depart_date, return_date,
                adults, children, infants, cabin, trip_type
            )
    
    return urls


def generate_preview_html(urls: Dict[str, str], search_params: dict) -> str:
    """Generate HTML content for URL preview"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Flight Search URLs Preview</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem;
                min-height: 100vh;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                padding: 2rem;
            }}
            h1 {{
                color: #667eea;
                margin-bottom: 1rem;
                font-size: 2rem;
            }}
            .search-info {{
                background: #f8f9fa;
                padding: 1.5rem;
                border-radius: 8px;
                margin-bottom: 2rem;
                border-left: 4px solid #667eea;
            }}
            .search-info h2 {{
                color: #333;
                font-size: 1.2rem;
                margin-bottom: 1rem;
            }}
            .search-info p {{
                color: #555;
                margin: 0.5rem 0;
                font-size: 0.95rem;
            }}
            .url-card {{
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                transition: all 0.3s ease;
            }}
            .url-card:hover {{
                border-color: #667eea;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
                transform: translateY(-2px);
            }}
            .url-card h3 {{
                color: #333;
                margin-bottom: 1rem;
                font-size: 1.3rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }}
            .url-box {{
                background: #f8f9fa;
                padding: 1rem;
                border-radius: 6px;
                word-break: break-all;
                font-family: 'Courier New', monospace;
                font-size: 0.85rem;
                color: #333;
                margin-bottom: 1rem;
                border: 1px solid #dee2e6;
            }}
            .button-group {{
                display: flex;
                gap: 1rem;
                flex-wrap: wrap;
            }}
            .btn {{
                padding: 0.75rem 1.5rem;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.95rem;
                font-weight: 600;
                text-decoration: none;
                display: inline-block;
                transition: all 0.3s ease;
            }}
            .btn-primary {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .btn-primary:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }}
            .btn-secondary {{
                background: #6c757d;
                color: white;
            }}
            .btn-secondary:hover {{
                background: #5a6268;
            }}
            .footer {{
                text-align: center;
                margin-top: 2rem;
                padding-top: 2rem;
                border-top: 2px solid #e0e0e0;
                color: #666;
            }}
            .icon {{
                font-size: 1.5rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✈️ Flight Search URLs Preview</h1>
            
            <div class="search-info">
                <h2>Search Parameters</h2>
                <p><strong>Route:</strong> {search_params['origin']} → {search_params['destination']}</p>
                <p><strong>Departure:</strong> {search_params['depart_date']}</p>
                {f"<p><strong>Return:</strong> {search_params['return_date']}</p>" if search_params.get('return_date') else ""}
                <p><strong>Passengers:</strong> {search_params['adults']} adult(s), {search_params['children']} child(ren), {search_params['infants']} infant(s)</p>
                <p><strong>Cabin:</strong> {search_params['cabin']}</p>
                <p><strong>Trip Type:</strong> {search_params['trip_type']}</p>
            </div>
            
            <h2 style="margin-bottom: 1.5rem; color: #333;">Generated URLs ({len(urls)} sites)</h2>
    """
    
    # Add each URL card
    for site_name, url in urls.items():
        html_content += f"""
            <div class="url-card">
                <h3><span class="icon">🔗</span> {site_name}</h3>
                <div class="url-box">{url}</div>
                <div class="button-group">
                    <a href="{url}" target="_blank" class="btn btn-primary">Open in New Tab</a>
                    <button onclick="copyToClipboard('{url.replace("'", "\\'")}', this)" class="btn btn-secondary">📋 Copy URL</button>
                </div>
            </div>
        """
    
    html_content += """
            <div class="footer">
                <p>Flight Incognito v1.0 | Generated on """ + datetime.now().strftime('%B %d, %Y at %I:%M %p') + """</p>
            </div>
        </div>
        
        <script>
            function copyToClipboard(text, button) {
                navigator.clipboard.writeText(text).then(function() {
                    const originalText = button.textContent;
                    button.textContent = '✅ Copied!';
                    button.style.background = '#28a745';
                    setTimeout(function() {
                        button.textContent = originalText;
                        button.style.background = '';
                    }, 2000);
                }).catch(function(err) {
                    alert('Failed to copy: ' + err);
                });
            }
        </script>
    </body>
    </html>
    """
    
    return html_content


def open_preview_in_browser(urls: Dict[str, str], search_params: dict) -> tuple[bool, str]:
    """Generate temporary HTML file and open in browser"""
    try:
        # Generate HTML content
        html_content = generate_preview_html(urls, search_params)
        
        # Create temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_file_path = f.name
        
        # Open in default browser
        webbrowser.open('file://' + temp_file_path)
        
        return True, temp_file_path
    except Exception as e:
        return False, str(e)


def launch_incognito(url: str, browser: str = "Chrome") -> tuple[bool, str]:
    """
    Launch a URL in browser incognito/private mode
    Returns: (success: bool, message: str)
    """
    system = platform.system()
    
    try:
        if browser == "Chrome":
            if system == "Darwin":  # macOS
                subprocess.Popen([
                    "open", "-na", "Google Chrome", 
                    "--args", "--incognito", url
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True, "Launched on macOS"
                
            elif system == "Windows":
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                ]
                
                launched = False
                for chrome_path in chrome_paths:
                    try:
                        subprocess.Popen(
                            [chrome_path, "--incognito", url],
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL
                        )
                        launched = True
                        break
                    except FileNotFoundError:
                        continue
                
                if not launched:
                    subprocess.Popen(
                        f'start chrome --incognito "{url}"',
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                
                return True, "Launched on Windows"
                
            elif system == "Linux":
                try:
                    subprocess.Popen(
                        ["google-chrome", "--incognito", url],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    return True, "Launched on Linux"
                except FileNotFoundError:
                    try:
                        subprocess.Popen(
                            ["chromium-browser", "--incognito", url],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        return True, "Launched on Linux"
                    except FileNotFoundError:
                        return False, "Chrome not found"
        
        elif browser == "Firefox":
            if system == "Darwin":
                subprocess.Popen([
                    "open", "-na", "Firefox", 
                    "--args", "--private-window", url
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True, "Launched Firefox on macOS"
                
            elif system == "Windows":
                firefox_paths = [
                    r"C:\Program Files\Mozilla Firefox\firefox.exe",
                    r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
                ]
                
                launched = False
                for firefox_path in firefox_paths:
                    try:
                        subprocess.Popen(
                            [firefox_path, "-private-window", url],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        launched = True
                        break
                    except FileNotFoundError:
                        continue
                
                if not launched:
                    subprocess.Popen(
                        f'start firefox -private-window "{url}"',
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                
                return True, "Launched Firefox on Windows"
                
            elif system == "Linux":
                subprocess.Popen(
                    ["firefox", "-private-window", url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return True, "Launched Firefox on Linux"
        
        elif browser == "Edge":
            if system == "Windows":
                edge_paths = [
                    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                ]
                
                launched = False
                for edge_path in edge_paths:
                    try:
                        subprocess.Popen(
                            [edge_path, "--inprivate", url],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        launched = True
                        break
                    except FileNotFoundError:
                        continue
                
                if not launched:
                    subprocess.Popen(
                        f'start msedge --inprivate "{url}"',
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                
                return True, "Launched Edge on Windows"
            elif system == "Darwin":
                subprocess.Popen([
                    "open", "-na", "Microsoft Edge",
                    "--args", "--inprivate", url
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True, "Launched Edge on macOS"
            elif system == "Linux":
                subprocess.Popen(
                    ["microsoft-edge", "--inprivate", url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return True, "Launched Edge on Linux"
        
        elif browser == "Brave":
            if system == "Darwin":
                subprocess.Popen([
                    "open", "-na", "Brave Browser",
                    "--args", "--incognito", url
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True, "Launched Brave on macOS"
                
            elif system == "Windows":
                brave_paths = [
                    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                    r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
                ]
                
                launched = False
                for brave_path in brave_paths:
                    try:
                        subprocess.Popen(
                            [brave_path, "--incognito", url],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        launched = True
                        break
                    except FileNotFoundError:
                        continue
                
                if not launched:
                    return False, "Brave not found"
                
                return True, "Launched Brave on Windows"
                
            elif system == "Linux":
                subprocess.Popen(
                    ["brave-browser", "--incognito", url],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return True, "Launched Brave on Linux"
        
        return False, f"Browser {browser} not supported"
            
    except Exception as e:
        return False, f"Error: {str(e)}"


# Sidebar
with st.sidebar:
    st.title("✈️ Flight Incognito")
    st.markdown("---")
    
    st.subheader("About")
    st.markdown("""
    **Why Incognito?**
    
    Flight prices can change based on your browsing history and cookies. 
    Opening searches in fresh incognito windows helps avoid:
    - 🔒 Session tracking
    - 💰 Dynamic price increases
    - 🎯 Personalized pricing
    
    Each search opens in a clean browser session for fair comparison.
    """)
    
    st.markdown("---")
    
    st.subheader("Supported Sites")
    st.markdown("""
    - ✈️ Google Flights
    - 🔍 Kayak
    - 🌍 Momondo
    - 🛫 Skyscanner
    - 🏨 Expedia
    - 💰 Priceline
    - 📱 Hopper
    - ✈️ CheapOair
    """)

# Main header with SVG banner
components.html("""
<div style="margin-bottom: 1.5rem;">
    <svg width="100%" height="100" viewBox="0 0 1200 100" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="bannerGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
            </linearGradient>
        </defs>
        
        <rect width="100%" height="100" fill="url(#bannerGradient)" rx="12"/>
        
        <ellipse cx="150" cy="30" rx="25" ry="12" fill="rgba(255,255,255,0.15)"/>
        <ellipse cx="170" cy="30" rx="30" ry="15" fill="rgba(255,255,255,0.15)"/>
        <ellipse cx="950" cy="70" rx="30" ry="15" fill="rgba(255,255,255,0.15)"/>
        <ellipse cx="975" cy="70" rx="25" ry="12" fill="rgba(255,255,255,0.15)"/>
        
        <g transform="translate(80, 35)">
            <path d="M 0 15 L 25 10 L 25 5 L 30 5 L 35 0 L 40 5 L 40 10 L 45 15 L 40 15 L 35 20 L 30 20 L 25 15 Z" 
                  fill="white" opacity="0.9"/>
            <path d="M 25 10 L 15 12 L 10 15 L 15 15 L 25 13 Z" fill="white" opacity="0.9"/>
            <circle cx="42" cy="8" r="2" fill="#FFD700"/>
        </g>
        
        <text x="600" y="55" font-family="'Aptos', 'Segoe UI', sans-serif" font-size="42" 
              font-weight="700" fill="white" text-anchor="middle" letter-spacing="1">
            Flight Incognito
        </text>
        
        <text x="600" y="78" font-family="'Aptos', 'Segoe UI', sans-serif" font-size="16" 
              font-weight="400" fill="rgba(255,255,255,0.9)" text-anchor="middle" letter-spacing="0.5">
            Privacy-First Flight Search
        </text>
        
        <line x1="130" y1="45" x2="70" y2="45" stroke="rgba(255,255,255,0.3)" stroke-width="2" stroke-dasharray="5,5"/>
    </svg>
</div>
""", height=120)

st.markdown("### Search multiple flight sites simultaneously in incognito mode")
st.markdown("---")

# Form section
st.subheader("Flight Search Details")

# Load search from history if selected
loaded_search = st.session_state.load_search
if loaded_search:
    st.info(f"📥 Loaded search: {loaded_search['origin']} → {loaded_search['destination']}")
    # Clear after loading
    st.session_state.load_search = None

# Create tabs for better organization
tab1, tab2, tab3 = st.tabs(["✈️ Flight Details & Passengers", "🌐 Sites & Browser", "📚 Search History"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Trip type
        trip_type = st.radio(
            "Trip Type",
            options=["Round Trip", "One Way"],
            index=0 if not loaded_search else (0 if loaded_search['trip_type'] == "Round Trip" else 1),
            horizontal=True
        )
        
        # Origin with autocomplete
        st.markdown("**From (Airport)**")
        
        # Find default origin in airport options
        default_origin_code = loaded_search['origin'] if loaded_search else "SFO"
        default_origin_idx = 0
        for idx, option in enumerate(airport_options):
            if option.startswith(default_origin_code + " - "):
                default_origin_idx = idx
                break
        
        origin_selection = st.selectbox(
            "From (Airport)",
            options=airport_options,
            index=default_origin_idx,
            help="Search by airport code, city name, or airport name",
            label_visibility="collapsed"
        )
        origin = get_airport_code_from_selection(origin_selection)
        
        # Destination with autocomplete
        st.markdown("**To (Airport)**")
        
        # Find default destination in airport options
        default_dest_code = loaded_search['destination'] if loaded_search else "LAX"
        default_dest_idx = 0
        for idx, option in enumerate(airport_options):
            if option.startswith(default_dest_code + " - "):
                default_dest_idx = idx
                break
        
        destination_selection = st.selectbox(
            "To (Airport)",
            options=airport_options,
            index=default_dest_idx,
            help="Search by airport code, city name, or airport name",
            label_visibility="collapsed"
        )
        destination = get_airport_code_from_selection(destination_selection)
        
        # Cabin class
        cabin_options = ["Economy", "Premium Economy", "Business", "First"]
        default_cabin_idx = cabin_options.index(loaded_search['cabin']) if loaded_search and loaded_search['cabin'] in cabin_options else 0
        
        cabin = st.selectbox(
            "Cabin Class",
            options=cabin_options,
            index=default_cabin_idx,
            help="Select your preferred cabin class"
        )
    
    with col2:
        # Dates
        default_depart = date.fromisoformat(loaded_search['depart_date']) if loaded_search else date.today() + timedelta(days=30)
        depart_date = st.date_input(
            "Departure Date",
            value=default_depart,
            min_value=date.today(),
            help="Select your departure date"
        )
        
        # Return date (disabled for one-way)
        if trip_type == "Round Trip":
            if loaded_search and loaded_search['return_date']:
                default_return = date.fromisoformat(loaded_search['return_date'])
            else:
                default_return = max(date.today() + timedelta(days=37), depart_date + timedelta(days=7))
            
            return_date = st.date_input(
                "Return Date",
                value=default_return,
                min_value=depart_date,
                help="Select your return date"
            )
        else:
            default_return = max(date.today() + timedelta(days=37), depart_date + timedelta(days=7))
            return_date = st.date_input(
                "Return Date",
                value=default_return,
                min_value=depart_date,
                disabled=True,
                help="Not applicable for one-way trips"
            )
    
    st.markdown("---")
    st.markdown("#### Passengers")
    
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    
    with col_p1:
        adults = st.number_input(
            "Adults (18+)",
            min_value=1,
            max_value=9,
            value=loaded_search['adults'] if loaded_search else 1,
            help="Number of adult passengers"
        )
    
    with col_p2:
        children = st.number_input(
            "Children (2-17)",
            min_value=0,
            max_value=8,
            value=loaded_search['children'] if loaded_search else 0,
            help="Number of child passengers"
        )
    
    with col_p3:
        infants = st.number_input(
            "Infants (under 2)",
            min_value=0,
            max_value=4,
            value=loaded_search['infants'] if loaded_search else 0,
            help="Number of infant passengers"
        )
    
    with col_p4:
        total_passengers = adults + children + infants
        st.metric("Total", total_passengers)

with tab2:
    st.markdown("#### Select Flight Search Sites")
    
    # Site selection with columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        google_flights = st.checkbox("✈️ Google Flights", value=True)
        kayak = st.checkbox("🔍 Kayak", value=True)
        momondo = st.checkbox("🌍 Momondo", value=True)
    
    with col2:
        skyscanner = st.checkbox("🛫 Skyscanner", value=True)
        expedia = st.checkbox("🏨 Expedia", value=True)
        priceline = st.checkbox("💰 Priceline", value=True)
    
    with col3:
        hopper = st.checkbox("📱 Hopper", value=False)
        cheapoair = st.checkbox("✈️ CheapOair", value=False)
    
    # Quick select buttons
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("✅ Select All", use_container_width=True):
            st.session_state.select_all_sites = True
            st.rerun()
    with col_b:
        if st.button("❌ Deselect All", use_container_width=True):
            st.session_state.deselect_all_sites = True
            st.rerun()
    with col_c:
        if st.button("⭐ Top 4", use_container_width=True):
            st.session_state.select_top_sites = True
            st.rerun()
    
    # Handle quick select
    if 'select_all_sites' in st.session_state and st.session_state.select_all_sites:
        google_flights = kayak = momondo = skyscanner = expedia = priceline = hopper = cheapoair = True
        st.session_state.select_all_sites = False
    
    if 'deselect_all_sites' in st.session_state and st.session_state.deselect_all_sites:
        google_flights = kayak = momondo = skyscanner = expedia = priceline = hopper = cheapoair = False
        st.session_state.deselect_all_sites = False
    
    if 'select_top_sites' in st.session_state and st.session_state.select_top_sites:
        google_flights = kayak = momondo = skyscanner = True
        expedia = priceline = hopper = cheapoair = False
        st.session_state.select_top_sites = False
    
    st.markdown("---")
    st.markdown("#### Browser Selection")
    
    browser = st.radio(
        "Choose your browser",
        options=["Chrome", "Firefox", "Edge", "Brave"],
        index=0,
        horizontal=True,
        help="Select which browser to open searches in"
    )
    
    # Collect selected sites
    selected_sites = []
    if google_flights:
        selected_sites.append("Google Flights")
    if kayak:
        selected_sites.append("Kayak")
    if momondo:
        selected_sites.append("Momondo")
    if skyscanner:
        selected_sites.append("Skyscanner")
    if expedia:
        selected_sites.append("Expedia")
    if priceline:
        selected_sites.append("Priceline")
    if hopper:
        selected_sites.append("Hopper")
    if cheapoair:
        selected_sites.append("CheapOair")
    
    if selected_sites:
        st.success(f"✅ {len(selected_sites)} site(s) selected")
    else:
        st.warning("⚠️ Please select at least one site")

with tab3:
    st.markdown("#### Search History")
    
    # Get all searches
    total_searches = db.get_total_searches()
    
    if total_searches == 0:
        st.info("📭 No search history yet. Start by creating your first flight search!")
    else:
        # Summary stats at the top
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            st.metric("Total Searches", total_searches)
        
        with col_stat2:
            popular = db.get_popular_routes(limit=1)
            if popular:
                most_popular = f"{popular[0]['origin']} → {popular[0]['destination']}"
                st.metric("Most Popular Route", most_popular)
            else:
                st.metric("Most Popular Route", "N/A")
        
        with col_stat3:
            recent = db.get_recent_searches(limit=1)
            if recent:
                last_search_time = datetime.fromisoformat(recent[0]['search_timestamp'])
                time_diff = datetime.now() - last_search_time
                if time_diff.days > 0:
                    last_search_str = f"{time_diff.days} day(s) ago"
                elif time_diff.seconds // 3600 > 0:
                    last_search_str = f"{time_diff.seconds // 3600} hour(s) ago"
                else:
                    last_search_str = f"{time_diff.seconds // 60} min(s) ago"
                st.metric("Last Search", last_search_str)
            else:
                st.metric("Last Search", "N/A")
        
        st.markdown("---")
        
        # Get all searches for grouping
        all_searches = db.get_recent_searches(limit=1000)  # Get all searches
        
        # Group searches by date
        now = datetime.now()
        today_searches = []
        yesterday_searches = []
        this_week_searches = []
        older_searches = []
        
        for search in all_searches:
            search_time = datetime.fromisoformat(search['search_timestamp'])
            days_diff = (now - search_time).days
            
            if days_diff == 0:
                today_searches.append(search)
            elif days_diff == 1:
                yesterday_searches.append(search)
            elif days_diff <= 7:
                this_week_searches.append(search)
            else:
                older_searches.append(search)
        
        # Display grouped searches
        def display_search_group(title, searches, emoji):
            if searches:
                st.markdown(f"### {emoji} {title} ({len(searches)})")
                
                for search in searches:
                    search_time = datetime.fromisoformat(search['search_timestamp'])
                    
                    # Create a card for each search
                    with st.container():
                        col1, col2, col3 = st.columns([3, 2, 1])
                        
                        with col1:
                            route = f"**{search['origin']} → {search['destination']}**"
                            st.markdown(route)
                            
                            # Date range
                            depart = date.fromisoformat(search['depart_date']).strftime('%b %d')
                            if search['return_date']:
                                return_d = date.fromisoformat(search['return_date']).strftime('%b %d, %Y')
                                date_range = f"📅 {depart} - {return_d}"
                            else:
                                date_range = f"📅 {depart} (One Way)"
                            st.caption(date_range)
                        
                        with col2:
                            # Passengers and cabin
                            passengers = f"👥 {search['adults']} adult(s)"
                            if search['children'] > 0:
                                passengers += f", {search['children']} child(ren)"
                            if search['infants'] > 0:
                                passengers += f", {search['infants']} infant(s)"
                            st.caption(passengers)
                            st.caption(f"💺 {search['cabin']}")
                        
                        with col3:
                            # Action buttons
                            if st.button("📥 Load", key=f"load_hist_{search['id']}", use_container_width=True):
                                st.session_state.load_search = search
                                st.rerun()
                            
                            if st.button("🗑️ Delete", key=f"del_hist_{search['id']}", use_container_width=True, type="secondary"):
                                db.delete_search(search['id'])
                                st.rerun()
                        
                        st.markdown("---")
        
        # Display each group
        display_search_group("Today", today_searches, "📍")
        display_search_group("Yesterday", yesterday_searches, "📆")
        display_search_group("This Week", this_week_searches, "📅")
        display_search_group("Older", older_searches, "📂")
        
        # Clear all history button at the bottom
        st.markdown("---")
        col_clear1, col_clear2, col_clear3 = st.columns([1, 1, 1])
        with col_clear2:
            if st.button("🗑️ Clear All History", use_container_width=True, type="secondary"):
                count = db.clear_all_history()
                st.success(f"✅ Cleared {count} searches")
                st.rerun()

st.markdown("---")

# Action buttons
col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 3])

with col_btn1:
    search_button = st.button(
        f"🚀 Open {len(selected_sites)} Site(s) in {browser}",
        type="primary",
        use_container_width=True,
        disabled=len(selected_sites) == 0
    )

with col_btn2:
    preview_button = st.button(
        "👁️ Preview URLs",
        use_container_width=True,
        disabled=len(selected_sites) == 0
    )

with col_btn3:
    copy_button = st.button(
        "📋 Copy All URLs",
        use_container_width=True,
        disabled=len(selected_sites) == 0
    )

# Status area
st.markdown("---")
status_container = st.container()

with status_container:
    st.subheader("Status")
    
    # Validation
    is_valid = True
    error_msg = None
    
    if not origin or not destination:
        is_valid = False
        error_msg = "❌ Please select both origin and destination airports"
    elif origin == destination:
        is_valid = False
        error_msg = "❌ Origin and destination must be different"
    elif trip_type == "Round Trip" and return_date <= depart_date:
        is_valid = False
        error_msg = "❌ Return date must be after departure date"
    
    if search_button:
        if not is_valid:
            st.error(error_msg)
        else:
            # Generate URLs for selected sites
            urls = generate_all_urls(
                origin, destination, depart_date, 
                return_date if trip_type == "Round Trip" else None,
                adults, children, infants, cabin, trip_type,
                selected_sites
            )
            
            # Launch with spinner
            with st.spinner(f"🚀 Launching {len(urls)} site(s) in {browser}..."):
                st.markdown("### 🌐 Launching Sites")
                
                success_count = 0
                fail_count = 0
                
                for site_name, url in urls.items():
                    success, message = launch_incognito(url, browser)
                    
                    if success:
                        st.success(f"✅ {site_name} - Opened in {browser}")
                        success_count += 1
                    else:
                        st.error(f"❌ {site_name} - {message}")
                        fail_count += 1
                    
                    # Small delay between launches
                    time.sleep(0.3)
                
                st.markdown("---")
                if fail_count == 0:
                    st.success(f"🎉 Successfully launched all {success_count} sites in {browser}!")
                    st.balloons()
                else:
                    st.warning(f"⚠️ Launched {success_count} sites, {fail_count} failed")
                    if fail_count > 0:
                        st.info(f"💡 Tip: Make sure {browser} is installed on your system")
                
                # Show search parameters
                st.markdown("**Search Parameters:**")
                st.write(f"- Route: {origin.upper()} → {destination.upper()}")
                st.write(f"- Departure: {depart_date.strftime('%B %d, %Y')}")
                if trip_type == "Round Trip":
                    st.write(f"- Return: {return_date.strftime('%B %d, %Y')}")
                st.write(f"- Passengers: {adults} adult(s), {children} child(ren), {infants} infant(s)")
                st.write(f"- Cabin: {cabin}")
                st.write(f"- Browser: {browser}")
                st.write(f"- Sites: {', '.join(selected_sites)}")
            
            # Save search to database after launching
            try:
                search_id = db.save_search(
                    origin=origin,
                    destination=destination,
                    depart_date=depart_date,
                    return_date=return_date if trip_type == "Round Trip" else None,
                    trip_type=trip_type,
                    adults=adults,
                    children=children,
                    infants=infants,
                    cabin=cabin
                )
                st.success(f"💾 Search saved to history")
                # Refresh to update sidebar
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.warning(f"⚠️ Could not save to history: {str(e)}")
    
    elif preview_button:
        if not is_valid:
            st.error(error_msg)
        else:
            # Generate URLs for selected sites
            urls = generate_all_urls(
                origin, destination, depart_date,
                return_date if trip_type == "Round Trip" else None,
                adults, children, infants, cabin, trip_type,
                selected_sites
            )
            
            # Prepare search parameters for HTML
            search_params = {
                'origin': origin.upper(),
                'destination': destination.upper(),
                'depart_date': depart_date.strftime('%B %d, %Y'),
                'return_date': return_date.strftime('%B %d, %Y') if trip_type == "Round Trip" else None,
                'adults': adults,
                'children': children,
                'infants': infants,
                'cabin': cabin,
                'trip_type': trip_type
            }
            
            # Open preview in new browser window
            with st.spinner("🚀 Generating preview and opening in browser..."):
                success, result = open_preview_in_browser(urls, search_params)
                
                if success:
                    st.success(f"✅ Preview opened in your browser with {len(urls)} URLs!")
                    st.info(f"💡 Temporary file created at: {result}")
                else:
                    st.error(f"❌ Failed to open preview: {result}")
    
    elif copy_button:
        if not is_valid:
            st.error(error_msg)
        else:
            # Generate URLs for selected sites
            urls = generate_all_urls(
                origin, destination, depart_date,
                return_date if trip_type == "Round Trip" else None,
                adults, children, infants, cabin, trip_type,
                selected_sites
            )
            
            st.success("✅ URLs ready to copy")
            st.markdown("### 📋 All URLs")
            
            # Create markdown list
            url_list = "\n".join([f"- [{site}]({url})" for site, url in urls.items()])
            st.markdown(url_list)
            
            # Also provide plain text version
            with st.expander("📄 Plain text (for copying)"):
                plain_text = "\n\n".join([f"{site}:\n{url}" for site, url in urls.items()])
                st.text_area("Copy this:", plain_text, height=200)
    
    else:
        st.info("👆 Enter your flight details above and click a button to continue")

# Footer
st.markdown("---")
st.caption("Flight Incognito v1.0 | Made with ❤️ using Streamlit")
