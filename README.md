# Raspberry Pi Stock/Crypto Display

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Raspberry Pi Zero project that displays real-time stock or cryptocurrency prices on a 2.13-inch e-ink display.

## Features

- Real-time price display of stocks or cryptocurrencies
- 24-hour price history graph
- Remote symbol updates via REST API
- E-ink display for low power consumption
- Automatic updates every 5 minutes

## Hardware Requirements

- Raspberry Pi Zero (Zero 2 W)
- 2.13-inch E-ink Display from [Waveshare](https://www.waveshare.com/catalogsearch/result/?q=2.13)
- MicroSD card
- Power supply

## Software Requirements

All required Python packages are listed in `requirements.txt`. Install them using:

```bash
pip install -r requirements.txt
```

## Quick Installation

For the quickest setup, follow these steps:

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/pi_stock_display.git
   cd pi_stock_display
   ```

2. Run the installation script:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

The installation script will:
- Update your system
- Install all required system dependencies
- Set up a Python virtual environment
- Install all Python packages
- Create necessary directories
- Set up an auto-start service

After installation, the display service will start automatically and run on boot.

### Manual Control

- Check service status: `sudo systemctl status stock-display.service`
- View logs: `sudo journalctl -u stock-display.service -f`
- Stop service: `sudo systemctl stop stock-display.service`
- Start service: `sudo systemctl start stock-display.service`
- Disable auto-start: `sudo systemctl disable stock-display.service`

### Troubleshooting

1. If the display doesn't update:
   - Check the service status and logs using the commands above
   - Ensure your Pi has internet connectivity
   - Verify the display is properly connected

2. If the API is not accessible:
   - Check if the service is running
   - Ensure port 8000 is not blocked by your firewall
   - Verify you're using the correct IP address

For additional help, please open an issue on GitHub.


## API Usage

The API runs on port 8000 by default. To update the displayed symbol:

```bash
curl -X POST "http://[raspberry-pi-ip]:8000/update" -H "Content-Type: application/json" -d '{"symbol": "AAPL"}'
```

To get the current symbol:

```bash
curl "http://[raspberry-pi-ip]:8000/current"
```

## Configuration

Edit `config.py` to modify:
- Display settings
- Update intervals
- API settings
- Default symbol

## Contributing

Feel free to submit issues and pull requests.
