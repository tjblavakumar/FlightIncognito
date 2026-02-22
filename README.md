# ✈️ Flight Incognito

A production-ready local web app that automates opening multiple flight search sites in fresh incognito browser windows. Search once, compare everywhere—without price tracking or session cookies affecting your results.

## 🎯 Core Features

- **8 Flight Search Sites**: Google Flights, Kayak, Momondo, Skyscanner, Expedia, Priceline, Hopper, CheapOair
- **Selective Site Search**: Choose which sites to search with checkboxes (Select All, Deselect All, Top 4 quick buttons)
- **Multi-Browser Support**: Chrome, Firefox, Edge, and Brave with incognito/private mode
- **Search History**: Automatically saves searches to local SQLite database for quick reuse
- **Popular Routes**: Track your most frequently searched routes
- **One-Click Load**: Click any saved search to instantly populate all fields
- **No Price Manipulation**: Avoid dynamic pricing based on browsing history
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Modern UI**: Clean tabbed interface with custom navigation bar and bold Aptos font

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

1. **Enter Flight Details** (Tab 1):
   - Select trip type (Round Trip or One Way)
   - Enter origin and destination airport codes (e.g., SFO, LAX, JFK)
   - Choose departure and return dates
   - Select cabin class (Economy, Premium Economy, Business, First)

2. **Select Sites & Browser** (Tab 2):
   - Check the flight search sites you want to use
   - Use quick buttons: "Select All", "Deselect All", or "Top 4"
   - Choose your preferred browser (Chrome, Firefox, Edge, Brave)

3. **Add Passengers** (Tab 3):
   - Enter number of adults, children, and infants
   - View total passenger count

4. **Launch Search**:
   - Click "🚀 Open X Site(s) in [Browser]" button
   - Each selected site opens in a fresh incognito/private window
   - Search is automatically saved to history

### Additional Features

- **Preview URLs**: Click "👁️ Preview URLs" to see generated search URLs before launching
- **Copy URLs**: Click "📋 Copy All URLs" to copy all search URLs to clipboard
- **Load from History**: Click any recent search in the sidebar to instantly populate fields
- **Delete History**: Remove individual searches or clear all history
- **Popular Routes**: View your most frequently searched routes

## 🗂️ Project Structure

```
flight-incognito/
├── app.py                  # Main Streamlit application
├── database.py             # SQLite database functions for search history
├── style.css               # Custom CSS styling (Aptos font, bold text)
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore rules
├── .streamlit/
│   └── config.toml        # Streamlit configuration
├── flight_searches.db     # SQLite database (auto-created)
└── venv/                  # Virtual environment (if created)
```

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
- Theme colors: Purple gradient navigation bar

## 🛠️ Troubleshooting

### Browser Not Opening

**Issue**: Sites don't open in incognito mode

**Solutions**:
- Ensure the selected browser is installed
- Check browser installation path matches standard locations
- Try a different browser from the dropdown
- On Windows, try running as administrator

### Sidebar Not Visible

**Issue**: Left navigation (sidebar) is hidden

**Solutions**:
- Look for the >> arrow button in the top-left corner
- Click it to expand the sidebar
- Refresh the page (F5)
- Clear browser cache

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
