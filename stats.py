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

#import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

import RPi.GPIO as GPIO

BUTTON_GPIO = 4
button_pressed = False

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
time.sleep(3)

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
size = 16
#bottom = height-padding

page = 1
displaytime = 2
updatetime = .1
showtime = displaytime / updatetime

showpage = 1
showpagemax = 3

# Load default font.
#font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('Minecraftia.ttf', 8)
font = ImageFont.truetype('PixelOperator.ttf', 16)
#font = ImageFont.truetype('STV5730A.ttf', 14)

def NextPage():
    showpage += 1
    if showpage > showpagemax:
        showpage = 1

GPIO.add_event_detect(BUTTON_GPIO, GPIO.FALLING, callback = NextPage, bouncetime = 2000)

while True:

    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    x = 0
    top = 0
    #if page < showtime:
    if showpage == 1:
        # Get Display Info
        cmd = "hostname -I | cut -d\' \' -f1"
        IP = subprocess.check_output(cmd, shell = True )
        cmd = "top -bn1 | grep load | awk '{printf \"CPU: %.2f\", $(NF-2)}'"
        CPUL = subprocess.check_output(cmd, shell = True )
        cmd = "top -bn1 | grep Cpu | awk '{printf \"CPU: %.1f%%\", $2+$4+$6+$10+$12+$14}'"
        CPUU = subprocess.check_output(cmd, shell = True )
        #cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
        cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB\", $3,$2 }'"
        MemUsage = subprocess.check_output(cmd, shell = True )
        #cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
        #Disk = subprocess.check_output(cmd, shell = True )
        cmd = "vcgencmd measure_temp | cut -f 2 -d '='"
        Temp = subprocess.check_output(cmd, shell = True )

        # Write Info To Display
        draw.text((x, top),    "IP: " + str(IP,'utf-8'),  font=font, fill=255)
        top = top + padding + size
        draw.text((x, top),    str(CPUL,'utf-8') + " " + str(Temp,'utf-8'), font=font, fill=255)
        top = top + padding + size
        draw.text((x, top),    str(CPUU,'utf-8'),  font=font, fill=255)
        top = top + padding + size
        draw.text((x, top),    str(MemUsage,'utf-8'),  font=font, fill=255)

    #if page >= showtime and page < (showtime * 2):
    if showpage == 2:
        # Get Display Info
        cmd = "hostname -I | cut -d\' \' -f1"
        IP = subprocess.check_output(cmd, shell = True )
        cmd = "hostname"
        HostName = subprocess.check_output(cmd, shell = True)
        cmd = "uptime | awk '{print $3,$4}' | cut -f1 -d,"
        #cmd = "uptime | sed 's/^.*up //' | awk -F \", \" '{print $1,$2}'"
        UpTime = subprocess.check_output(cmd, shell = True )
        cmd = "uptime |cut -d , -f 3|awk '{print $1}'"
        Users = subprocess.check_output(cmd, shell = True)

        # Write Info To Display
        draw.text((x, top),    "IP: " + str(IP,'utf-8'),  font=font, fill=255)
        top = top + padding + size
        draw.text((x, top),    "Name: " + str(HostName,'utf-8'),  font=font, fill=255)
        top = top + padding + size
        draw.text((x, top),    "Uptime: " + str(UpTime,'utf-8'),  font=font, fill=255)
        top = top + padding + size
        draw.text((x, top),    "Users: " + str(Users,'utf-8'),  font=font, fill=255)
        top = top + padding + size

    #if page >= (showtime * 2) and page <= (showtime * 3):
    if showpage == 3:
        # Get Display Info
        cmd = "df -h | grep '/dev/md\|/dev/sd\|/dev/root' | awk '{printf \"%s/%s %s, \", $3,$2,$5}'"
        DrvUse = str(subprocess.check_output(cmd, shell = True ),'utf-8')
        Drv = DrvUse.split(", ")

        # Write Info To Display
        i = 0
        while i < len(Drv)-1:
            draw.text((x, top),    "Drv" + str(i) + ": " + Drv[i],  font=font, fill=255)
            top = top + padding + size
            i += 1

    #print(page)
    # Display image.
    disp.image(image)
    disp.display()

    page += 1
    if page > (showtime * 3):
        page = 1

    time.sleep(updatetime)
