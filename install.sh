#!/bin/bash

# Get the absolute path of the current directory
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install system dependencies
echo "Installing system dependencies..."
# Update package list first
sudo apt-get update

# Install essential packages
sudo apt-get install -y coreutils
sudo apt-get install -y python3-pip
sudo apt-get install -y python3-venv
sudo apt-get install -y python3-full
sudo apt-get install -y libopenjp2-7
sudo apt-get install -y libtiff5
sudo apt-get install -y git
sudo apt-get install -y build-essential
sudo apt-get install -y python3-dev
sudo apt-get install -y python3-numpy
sudo apt-get install -y python3-rpi.gpio
sudo apt-get install -y python3-spidev
sudo apt-get install -y python3-gpiozero
sudo apt-get install -y python3-pillow
sudo apt-get install -y python3-pandas
sudo apt-get install -y python3-matplotlib
sudo apt-get install -y fonts-dejavu
sudo apt-get install -y ttf-dejavu

# Create and activate virtual environment
echo "Creating Python virtual environment..."
python3 -m venv "${INSTALL_DIR}/venv"
source "${INSTALL_DIR}/venv/bin/activate"

# Upgrade pip and install wheel in virtual environment
echo "Upgrading pip and installing wheel..."
pip install --upgrade pip
pip install wheel

# Install Python packages in virtual environment
echo "Installing Python packages..."
# Web server packages
pip install fastapi==0.104.1
pip install "uvicorn[standard]==0.24.0"
# Data handling packages
pip install pandas==2.1.3
pip install yfinance==0.2.31
pip install matplotlib==3.8.2
# Utility packages
pip install python-dotenv==1.0.0
pip install schedule==1.2.1
pip install requests==2.31.0
pip install pillow==10.1.0
# E-Paper display library
pip install git+https://github.com/waveshare/e-Paper.git@master#egg=waveshare-epd\&subdirectory=RaspberryPi/python

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p "${INSTALL_DIR}/output"

# Enable SPI if not already enabled
echo "Enabling SPI interface..."
if ! grep -q "^dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
    echo "SPI interface enabled. A reboot will be required."
fi

# Install BCM2835 library
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

# Set up systemd service for auto-start
echo "Setting up auto-start service..."
sudo tee /etc/systemd/system/stock-display.service << EOF
[Unit]
Description=Stock Display Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=${INSTALL_DIR}
Environment="PATH=${INSTALL_DIR}/venv/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/usr/local/sbin"
Environment="DISPLAY_TYPE=RaspberryPi"
Environment="GPIOZERO_PIN_FACTORY=rpigpio"
Environment="PYTHONPATH=${INSTALL_DIR}"
Environment="PYTHONUNBUFFERED=1"
ExecStart=${INSTALL_DIR}/venv/bin/python3 ${INSTALL_DIR}/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable stock-display.service
sudo systemctl start stock-display.service

echo "Installation complete! The stock display service is now running."
echo "To check the status, run: sudo systemctl status stock-display.service"
echo "To view logs, run: sudo journalctl -u stock-display.service -f"
echo ""
echo "Note: If this is the first time enabling SPI, please reboot your Raspberry Pi."
