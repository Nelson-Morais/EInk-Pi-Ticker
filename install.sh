#!/bin/bash

# Get the absolute path of the current directory
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install system dependencies
echo "Installing system dependencies..."
# Update package list first
sudo apt-get update

# Install essential packages
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    gpiod \
    libgpiod-dev \
    libopenjp2-7 \
    libtiff5 \
    libatlas-base-dev \
    git
sudo apt-get install -y build-essential
sudo apt-get install -y coreutils

# Install font packages
sudo apt-get install -y fonts-dejavu
sudo apt-get install -y ttf-dejavu

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv "${INSTALL_DIR}/venv"
source "${INSTALL_DIR}/venv/bin/activate"

# Upgrade pip and install wheel in virtual environment
echo "Upgrading pip and installing wheel..."
pip install --upgrade pip
pip install wheel

# Install Python packages from requirements.txt
echo "Installing Python packages from requirements.txt..."
pip install -r "${INSTALL_DIR}/requirements.txt"

# Install Waveshare e-Paper library
echo "Installing Waveshare e-Paper library..."
cd /tmp
rm -rf e-Paper
git clone https://github.com/waveshareteam/e-Paper.git
cd e-Paper/RaspberryPi_JetsonNano/python/
python setup.py install
cd "${INSTALL_DIR}"

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

# Add current user to gpio and spi groups
echo "Adding user to gpio and spi groups..."
sudo usermod -a -G gpio,spi $USER

# Set up systemd service for auto-start
echo "Setting up auto-start service..."
sudo tee /etc/systemd/system/ticker-display.service << EOF
[Unit]
Description=Ticker Display Service
After=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=${INSTALL_DIR}
Environment="PATH=${INSTALL_DIR}/venv/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/usr/local/sbin"
Environment="DISPLAY_TYPE=RaspberryPi"
Environment="GPIOZERO_PIN_FACTORY=rpigpio"
Environment="PYTHONPATH=${INSTALL_DIR}:/tmp/e-Paper/RaspberryPi_JetsonNano/python"
Environment="PYTHONUNBUFFERED=1"
ExecStart=${INSTALL_DIR}/venv/bin/python3 ${INSTALL_DIR}/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable ticker-display.service
sudo systemctl start ticker-display.service

echo "Installation complete! The Ticker display service is now running."
echo "To check the status, run: sudo systemctl status ticker-display.service"
echo "To view logs, run: sudo journalctl -u ticker-display.service -f"
echo ""
echo "Note: If this is the first time enabling SPI, please reboot your Raspberry Pi."
