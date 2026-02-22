"""
Flight Incognito - Multi-site flight search launcher with incognito mode
Opens multiple flight aggregator sites in fresh browser incognito/private windows
"""

import streamlit as st
from datetime import date, timedelta, datetime
from urllib.parse import quote
from typing import Dict
import subprocess
import platform
import time
import database as db

# Page config
st.set_page_config(
    page_title="Flight Incognito",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"  # Force sidebar to be expanded
)

# Load custom CSS for Ubuntu font
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

try:
    load_css()
except FileNotFoundError:
    pass  # CSS file not found, continue without custom styling

# Custom Navigation Bar
st.markdown("""
    <style>
        /* Hide default Streamlit header */
        header[data-testid="stHeader"] {
            display: none;
        }
        
        .main-nav {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            padding: 0.75rem 2rem;
            margin: -4rem -4rem 2rem -4rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        .nav-content {
            display: flex;
            align-items: center;
            justify-content: center;
            max-width: 100%;
        }
        .nav-title {
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }
        .nav-title h1 {
            color: white;
            margin: 0;
            font-size: 36px;
            font-weight: 700;
            font-family: 'Aptos', 'Segoe UI', sans-serif;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            line-height: 1.2;
        }
        .nav-icon {
            font-size: 36px;
            line-height: 1;
        }
    </style>
    <div class="main-nav">
        <div class="nav-content">
            <div class="nav-title">
                <span class="nav-icon">✈️</span>
                <h1>Flight Incognito</h1>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Initialize database
db.init_database()

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
    
    if trip_type == "Round Trip" and return_date:
        return_str = return_date.strftime("%Y-%m-%d")
        url = f"https://www.kayak.com/flights/{origin}-{destination}/{depart_str}/{return_str}"
    else:
        url = f"https://www.kayak.com/flights/{origin}-{destination}/{depart_str}"
    
    # Add passengers and sorting
    url += f"?sort=bestflight_a&fs=adults={adults}"
    
    if children > 0:
        url += f";children={children}"
    if infants > 0:
        url += f";infants={infants}"
    
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
        url = f"https://www.skyscanner.com/transport/flights/{origin}/{destination}/{depart_str}/{return_str}/"
    else:
        url = f"https://www.skyscanner.com/transport/flights/{origin}/{destination}/{depart_str}/"
    
    # Map cabin class to Skyscanner format
    cabin_map = {
        "Economy": "economy",
        "Premium Economy": "premiumeconomy",
        "Business": "business",
        "First": "first"
    }
    cabin_code = cabin_map.get(cabin, "economy")
    
    # Add passengers, cabin, and currency (USD)
    url += f"?adults={adults}&children={children}&infants={infants}&cabinclass={cabin_code}&currency=USD&locale=en-US"
    
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
    
    # Test message to confirm sidebar is rendering
    st.write("Sidebar is visible!")
    
    # Search History Section
    st.subheader("📚 Search History")
    
    total_searches = db.get_total_searches()
    st.caption(f"Total searches: {total_searches}")
    
    # Recent searches
    if total_searches > 0:
        recent_searches = db.get_recent_searches(limit=5)
        
        st.markdown("**Recent Searches:**")
        for search in recent_searches:
            search_date = datetime.fromisoformat(search['search_timestamp']).strftime('%m/%d %H:%M')
            route = f"{search['origin']} → {search['destination']}"
            
            col_a, col_b = st.columns([3, 1])
            with col_a:
                if st.button(
                    f"{route}",
                    key=f"load_{search['id']}",
                    help=f"Searched on {search_date}",
                    use_container_width=True
                ):
                    st.session_state.load_search = search
                    st.rerun()
            with col_b:
                if st.button("🗑️", key=f"del_{search['id']}", help="Delete"):
                    db.delete_search(search['id'])
                    st.rerun()
        
        # Popular routes
        st.markdown("**Popular Routes:**")
        popular = db.get_popular_routes(limit=3)
        for route in popular:
            st.caption(f"✈️ {route['origin']} → {route['destination']} ({route['search_count']}x)")
        
        # Clear history button
        if st.button("🗑️ Clear All History", use_container_width=True):
            count = db.clear_all_history()
            st.success(f"Cleared {count} searches")
            st.rerun()
    else:
        st.info("No search history yet")
    
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
    
    st.markdown("---")
    st.caption(f"System: {platform.system()}")
    st.markdown("🔗 [GitHub](https://github.com/yourusername/flight-incognito)")

# Main header - removed since we have top nav bar now
# st.title("🚀 Flight Incognito")
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
tab1, tab2, tab3 = st.tabs(["✈️ Flight Details", "🌐 Sites & Browser", "👥 Passengers"])

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
        
        # Origin and destination
        origin = st.text_input(
            "From (Airport Code)",
            value=loaded_search['origin'] if loaded_search else "SFO",
            help="Enter IATA code, e.g. SFO, LAX, JFK",
            max_chars=3
        )
        
        destination = st.text_input(
            "To (Airport Code)",
            value=loaded_search['destination'] if loaded_search else "LAX",
            help="Enter IATA code, e.g. SFO, LAX, JFK",
            max_chars=3
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
        
        # Cabin class
        cabin_options = ["Economy", "Premium Economy", "Business", "First"]
        default_cabin_idx = cabin_options.index(loaded_search['cabin']) if loaded_search and loaded_search['cabin'] in cabin_options else 0
        
        cabin = st.selectbox(
            "Cabin Class",
            options=cabin_options,
            index=default_cabin_idx,
            help="Select your preferred cabin class"
        )

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
    col1, col2 = st.columns(2)
    
    with col1:
        # Passengers
        adults = st.number_input(
            "Adults (18+)",
            min_value=1,
            max_value=9,
            value=loaded_search['adults'] if loaded_search else 1,
            help="Number of adult passengers"
        )
        
        children = st.number_input(
            "Children (2-17)",
            min_value=0,
            max_value=8,
            value=loaded_search['children'] if loaded_search else 0,
            help="Number of child passengers"
        )
    
    with col2:
        infants = st.number_input(
            "Infants (under 2)",
            min_value=0,
            max_value=4,
            value=loaded_search['infants'] if loaded_search else 0,
            help="Number of infant passengers"
        )
        
        total_passengers = adults + children + infants
        st.metric("Total Passengers", total_passengers)

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
        error_msg = "❌ Please enter both origin and destination airport codes"
    elif len(origin.strip()) != 3 or len(destination.strip()) != 3:
        is_valid = False
        error_msg = "❌ Airport codes must be exactly 3 letters (e.g., SFO, LAX, JFK)"
    elif origin.upper().strip() == destination.upper().strip():
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
            # Generate and display URLs for selected sites
            urls = generate_all_urls(
                origin, destination, depart_date,
                return_date if trip_type == "Round Trip" else None,
                adults, children, infants, cabin, trip_type,
                selected_sites
            )
            
            st.success(f"✅ Generated {len(urls)} search URLs")
            st.markdown("### 🔗 Preview URLs")
            
            for site_name, url in urls.items():
                with st.expander(f"**{site_name}**", expanded=True):
                    st.code(url, language=None)
                    st.markdown(f"[Open {site_name} in browser →]({url})")
    
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
