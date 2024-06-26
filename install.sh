#!/bin/bash

MYDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

clear
cat <<EOF
#########################################################
          Raspberry Pi OLED Display Install
#########################################################
Incorrect wiring of the Raspberry Pi GPIO pins
can cause permanent damage to your Pi. 

You assume all responsibility when wiring your Pi.
#########################################################
Remember To make sure the I2C on Raspberry Pi is Enabled:
sudo rasp-config

I2C Check:
i2cdetect -y 1
#########################################################
EOF
read -n 1 -s -r -p "Press any key to continue"
clear

tool=$(which git)
if [[ $tool == "" ]]; then
    sudo apt-get install -y git
fi

tool=$(which python3)
if [[ $tool == "" ]]; then
    sudo apt-get install -y python3 python3-pip python3-pil python3-pil.imagetk
fi

if [ -f "~/Adafruit_Python_SSD1306/.git" ]; then
    echo "Adafruit_Python_SSD1306 already exists"
else
    cd ~

    git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git

    cd Adafruit_Python_SSD1306

    sudo python3 setup.py install

    cd $MYDIR
fi

echo;echo "installing script and service"

if [ -d "/usr/local/bin/rpi-oled" ]; then
    echo "/usr/local/bin/rpi-oled already exists"
else
    sudo mkdir /usr/local/bin/rpi-oled
fi

sudo cp $MYDIR/rpi-oled-display.py /usr/local/bin/rpi-oled
sudo cp $MYDIR/pi_logo.png /usr/local/bin/rpi-oled
sudo cp $MYDIR/PixelOperator.ttf /usr/local/bin/rpi-oled
sudo cp $MYDIR/PixelOperator8.ttf /usr/local/bin/rpi-oled
sudo cp $MYDIR/rpi-oled-display.service /lib/systemd/system/

echo "enabling service"

sudo systemctl enable rpi-oled-display.service
sudo systemctl start rpi-oled-display.service

#get status of service
STATUS=$(sudo systemctl is-enabled rpi-oled-display.service)


cat <<EOF

Script installed and $STATUS

To disable the script from running at boot, run:
sudo systemctl disable rpi-oled-display.service

To enable the script to run at boot, run:
sudo systemctl enable rpi-oled-display.service

EOF

exit 0