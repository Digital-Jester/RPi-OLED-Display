# Copyright (c) 2017 Adafruit Industries
# Author: Tony DiCola & James DeVito
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used

# Beaglebone Black pin configuration:
# RST = 'P9_12'

# 128x32 display with hardware I2C:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# 128x64 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Note you can change the I2C address by passing an i2c_address parameter like:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)

# Alternatively you can specify an explicit I2C bus number, for example
# with the 128x32 display you would use:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_bus=2)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# RPi Splash
# Alternatively load a different format image, resize it, and convert to 1 bit color.
image = Image.open('pi_logo.png').resize((disp.width, disp.height), Image.ANTIALIAS).convert('1')

# Display image.
disp.image(image)
disp.display()
time.sleep(5)

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = 1
top = 0
size = 10
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

page = 0
showtime = 1000

# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('Minecraftia.ttf', 8)
#font = ImageFont.truetype('PixelOperator.ttf', 16)
#font = ImageFont.truetype('STV5730A.ttf', 14)

while True:

    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    cmd = "hostname -I | cut -d\' \' -f1"
    IP = subprocess.check_output(cmd, shell = True )
    cmd = "top -bn1 | grep load | awk '{printf \"CPU: %.2f\", $(NF-2)}'"
    CPU = subprocess.check_output(cmd, shell = True )
    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell = True )
    cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
    Disk = subprocess.check_output(cmd, shell = True )
    cmd = "vcgencmd measure_temp |cut -f 2 -d '='"
    Temp = subprocess.check_output(cmd, shell = True )
    cmd = "uptime | awk '{print $3,$4}' | cut -f1 -d,"
    UpTime = subprocess.check_output(cmd, shell = True )
    cmd = "hostname"
    HostName = subprocess.check_output(cmd, shell = True)

    # Write Pi Stats.
    top = 0
    if page < showtime:
        draw.text((x, top),       "IP: " + str(IP,'utf-8'),  font=font, fill=255)
        top = top + padding + size
        draw.text((x, top),     str(CPU,'utf-8') + " " + str(Temp,'utf-8'), font=font, fill=255)
        top = top + padding + size
        draw.text((x, top),    str(MemUsage,'utf-8'),  font=font, fill=255)
        top = top + padding + size
        draw.text((x, top),    str(Disk,'utf-8'),  font=font, fill=255)
        top = top + padding + size
        draw.text((x, top),    "Up Time: " + str(UpTime,'utf-8'),  font=font, fill=255)

    if page > showtime and page < showtime * 2:
        draw.text((x, top),       "IP: " + str(IP,'utf-8'),  font=font, fill=255)
        top = top + padding + size
        draw.text((x, top),    str(HostName,'utf-8'),  font=font, fill=255)
        top = top + padding + size

    # Display image.
    disp.image(image)
    disp.display()
    page += 1
    if page > showtime * 2:
        page = 0 
    time.sleep(.1)
