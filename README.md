# ✈️ Flight Incognito

A production-ready local web app that automates opening multiple flight search sites in fresh incognito browser windows. Search once, compare everywhere—without price tracking or session cookies affecting your results.

## 🎯 Core Features

- **8 Flight Search Sites**: Google Flights, Kayak, Momondo, Skyscanner, Expedia, Priceline, Hopper, CheapOair
- **Selective Site Search**: Choose which sites to search with checkboxes (Select All, Deselect All, Top 4 quick buttons)
- **Multi-Browser Support**: Chrome, Firefox, Edge, and Brave with incognito/private mode
- **Search History**: Automatically saves searches to local SQLite database for quick reuse
- **Popular Routes**: Track your most frequently searched routes
- **One-Click Load**: Click any saved search to instantly populate all fields
- **URL Preview in Browser**: Generate and open a beautiful HTML preview of all search URLs in a new browser window
- **No Price Manipulation**: Avoid dynamic pricing based on browsing history
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Modern UI**: 
  - Custom SVG banner with gradient design
  - Static left navigation (always visible, no collapse)
  - Streamlined 2-tab interface for faster workflow
  - Bold Aptos font throughout
  - Clean, professional design

## 🌐 Supported Flight Search Sites

- ✈️ **Google Flights** - Comprehensive search with flexible dates
- 🔍 **Kayak** - Price alerts and predictions
- 🌍 **Momondo** - Budget-friendly options
- 🛫 **Skyscanner** - Global coverage (USD currency)
- 🏨 **Expedia** - Package deals and rewards
- 💰 **Priceline** - Express deals and bidding
- 📱 **Hopper** - Price predictions and alerts
- ✈️ **CheapOair** - Discount flights

## 🌐 Supported Browsers

- **Chrome** - Incognito mode
- **Firefox** - Private browsing
- **Edge** - InPrivate mode
- **Brave** - Private window

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- One or more supported browsers installed (Chrome, Firefox, Edge, or Brave)
- pip (Python package manager)

### Installation

1. **Clone or download this repository**
   ```bash
   git clone https://github.com/yourusername/flight-incognito.git
   cd flight-incognito
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   - The app will automatically open at `http://localhost:8501`
   - If it doesn't, manually navigate to that URL

## 📖 How to Use

### Basic Search

1. **Enter Flight Details & Passengers** (Tab 1):
   - Select trip type (Round Trip or One Way)
   - Enter origin and destination airport codes (e.g., SFO, LAX, JFK)
   - Choose departure and return dates
   - Select cabin class (Economy, Premium Economy, Business, First)
   - Enter number of adults, children, and infants (all in one convenient tab)

2. **Select Sites & Browser** (Tab 2):
   - Check the flight search sites you want to use
   - Use quick buttons: "Select All", "Deselect All", or "Top 4"
   - Choose your preferred browser (Chrome, Firefox, Edge, Brave)

3. **Launch Search**:
   - Click "🚀 Open X Site(s) in [Browser]" button
   - Each selected site opens in a fresh incognito/private window
   - Search is automatically saved to history

### Additional Features

- **Preview URLs**: Click "👁️ Preview URLs" to generate a beautiful HTML page with all search URLs that opens in a new browser window. Features:
  - Professional gradient design matching the app theme
  - Search parameters summary
  - Individual cards for each site with "Open in New Tab" and "Copy URL" buttons
  - Responsive layout with hover effects
  - Timestamp of when the preview was generated
- **Copy URLs**: Click "📋 Copy All URLs" to view and copy all search URLs in the app
- **Load from History**: Click any recent search in the sidebar to instantly populate fields
- **Delete History**: Remove individual searches or clear all history
- **Popular Routes**: View your most frequently searched routes
- **Static Sidebar**: Left navigation stays visible at all times for easy access to search history

## 🗂️ Project Structure

```
flight-incognito/
├── app.py                  # Main Streamlit application with SVG banner
├── database.py             # SQLite database functions for search history
├── style.css               # Custom CSS styling (Aptos font, static sidebar)
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore rules
├── .streamlit/
│   └── config.toml        # Streamlit configuration
├── flight_searches.db     # SQLite database (auto-created)
└── venv/                  # Virtual environment (if created)
```

## ✨ Recent Updates

### UI/UX Improvements
- **Removed top navigation bar**: Eliminated redundant header to reduce whitespace
- **Added custom SVG banner**: Professional gradient banner with airplane graphics and app branding
- **Static sidebar**: Left navigation now stays visible at all times (no collapse button)
- **Merged tabs**: Combined "Flight Details" and "Passengers" into one tab for faster workflow (reduced from 3 tabs to 2)
- **Enhanced preview feature**: "Preview URLs" now opens a beautiful HTML page in a new browser window with:
  - Gradient design matching app theme
  - Interactive copy buttons for each URL
  - Search parameters summary
  - Professional card-based layout

### Technical Improvements
- Added `streamlit.components.v1` for better HTML rendering
- Implemented temporary HTML file generation for URL previews
- Enhanced CSS for sidebar stability and visibility
- Improved passenger input layout with 4-column design

## 🔧 Configuration

### Browser Paths

The app automatically detects browser installations in standard locations:

- **Windows**: `C:\Program Files\` and `C:\Program Files (x86)\`
- **macOS**: Uses `open` command with application names
- **Linux**: Uses standard command names (`google-chrome`, `firefox`, etc.)

### Database

- Search history is stored in `flight_searches.db` (SQLite)
- Database is automatically created on first run
- Location: Same directory as `app.py`

### Styling

- Custom CSS in `style.css`
- Font: Aptos (bold, 16px) with fallbacks to Segoe UI, Helvetica Neue, Arial
- Custom SVG banner with purple gradient (#667eea to #764ba2)
- Static sidebar (no collapse functionality)
- Professional card-based layouts

## 🛠️ Troubleshooting

### Browser Not Opening

**Issue**: Sites don't open in incognito mode

**Solutions**:
- Ensure the selected browser is installed
- Check browser installation path matches standard locations
- Try a different browser from the dropdown
- On Windows, try running as administrator

### Sidebar Not Visible

**Issue**: Left navigation (sidebar) is hidden or collapsed

**Solutions**:
- The sidebar is now static and should always be visible
- If you don't see it, try refreshing the page (F5)
- Clear browser cache and reload
- Check that your browser window is wide enough to display the sidebar

### Search History Not Saving

**Issue**: Searches don't appear in history

**Solutions**:
- Check that `flight_searches.db` file is created
- Ensure write permissions in the app directory
- Check terminal for error messages

### URLs Not Working

**Issue**: Flight search sites show empty fields

**Solutions**:
- Use "Preview URLs" to verify URL format
- Check that airport codes are valid 3-letter IATA codes
- Ensure dates are in the future
- Some sites (Hopper) have limited web support - primarily mobile apps

## 📝 Dependencies

- **streamlit** - Web application framework
- **Python 3.8+** - Programming language

All dependencies are listed in `requirements.txt`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Flight search sites: Google Flights, Kayak, Momondo, Skyscanner, Expedia, Priceline, Hopper, CheapOair

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Note**: This tool opens flight search sites in incognito/private mode to help avoid price tracking. It does not guarantee the lowest prices or prevent all forms of price variation. Always compare prices and read terms before booking.
