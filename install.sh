#!/bin/bash

# Get the absolute path of the current directory
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check Python version
if ! python3 -c "import sys; assert sys.version_info >= (3, 7), 'Python 3.7+ required'"; then
    echo "Error: Python 3.7 or higher is required"
    exit 1
fi

# 1. Enable SPI interface (as per Waveshare docs)
echo "Enabling SPI interface..."
if ! grep -q "dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
    echo "SPI interface enabled. A reboot will be required."
fi

# 2. Install BCM2835 (as per Waveshare docs)
echo "Installing BCM2835 library..."
cd /tmp
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.71.tar.gz
tar zxvf bcm2835-1.71.tar.gz
cd bcm2835-1.71/
./configure
make
sudo make check
sudo make install
cd "${INSTALL_DIR}"

# 3. Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-spidev \
    build-essential

# Add user to spi and gpio groups if not already a member
if ! groups | grep -q "\bspi\b"; then
    echo "Adding user to spi group..."
    sudo usermod -a -G spi $USER
fi
if ! groups | grep -q "\bgpio\b"; then
    echo "Adding user to gpio group..."
    sudo usermod -a -G gpio $USER
fi

# 4. Setup Python environment
echo "Setting up Python environment..."
python3 -m venv "${INSTALL_DIR}/venv"
source "${INSTALL_DIR}/venv/bin/activate"

# Remove any existing GPIO packages to avoid conflicts
pip uninstall -y RPi.GPIO Jetson.GPIO gpiozero || true

# Install GPIO packages in the correct order
pip install RPi.GPIO==0.7.1
pip install gpiozero==1.6.2

# Install other requirements
pip install --upgrade pip
pip install -r "${INSTALL_DIR}/requirements.txt"

# 5. Create output directory
mkdir -p "${INSTALL_DIR}/output"

# 6. Setup service
echo "Setting up systemd service..."
sudo tee /etc/systemd/system/ticker-display.service << EOF
[Unit]
Description=Ticker Display Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=${INSTALL_DIR}
Environment=PYTHONPATH=${INSTALL_DIR}/venv/lib/python3.11/site-packages
Environment=GPIOZERO_PIN_FACTORY=rpigpio
ExecStart=${INSTALL_DIR}/venv/bin/python3 ${INSTALL_DIR}/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ticker-display.service
sudo systemctl start ticker-display.service

echo "Installation complete! The Ticker display service is now running."
echo "To check the status, run: sudo systemctl status ticker-display.service"
echo "To view logs, run: sudo journalctl -u ticker-display.service -f"
echo ""
echo "Note: If this is the first time enabling SPI, please reboot your Raspberry Pi."
echo "Note: If you were added to the gpio or spi groups, you'll need to log out and back in for it to take effect."