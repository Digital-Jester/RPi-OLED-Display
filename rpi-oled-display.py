#!/bin/python3

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

# Define GPIO Numbers For Button Inputs
BUTTON_NEXT_PAGE = 4
BUTTON_SHUTDOWN = 17
BUTTON_REBOOT = 27

# Define OLED Reset Pin
RST = None     # on the PiOLED this pin isnt used
# Be aglebone Black pin configuration:
# RST = 'P9_12'

if __name__ == '__main__':
    # Setup GPIO Pin Mode
    GPIO.setmode(GPIO.BCM)
    # Setup GPIO Pins For Use
    GPIO.setup(BUTTON_NEXT_PAGE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON_SHUTDOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON_REBOOT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Setup OLED For Use
    # /////////////////////////////////////////////////////////////////////////////
    # 128x32 display with hardware I2C:
    # disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
    # /////////////////////////////////////////////////////////////////////////////
    # 128x64 display with hardware I2C:
    disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
    # /////////////////////////////////////////////////////////////////////////////
    # Note you can change the I2C address by passing an i2c_address parameter like:
    # disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)
    # /////////////////////////////////////////////////////////////////////////////
    # Alternatively you can specify an explicit I2C bus number, for example
    # with the 128x32 display you would use:
    # disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_bus=2)

    # Initialize The OLED Display.
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
    image = Image.new('1', (disp.width, disp.height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,disp.width,disp.height), outline=0, fill=0)

    # Setup for display height.
    if disp.height == 64:
        padding = 1
        size = 16
        # Load alt font.
        font = ImageFont.truetype('PixelOperator.ttf', size)

    # Setup for display height.
    if disp.height == 32:
        padding = 0
        size = 9
        # Load default font.
        # font = ImageFont.load_default()
        font = ImageFont.truetype('dogica.ttf', size)


    updatetime = 0.1

    showpage = 1
    showpagemax = 3

    x = 0
    y = 0

    # Load default font.
    #font = ImageFont.load_default()

    # Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
    # Some other nice fonts to try: http://www.dafont.com/bitmap.php
    #font = ImageFont.truetype('PixelOperator.ttf', 16)

    def NextPage(channel):
        global showpage, showpagemax
        showpage += 1
        if showpage > showpagemax:
            showpage = 1

    def ShutDown(channel):
        #print ("ShutDown")
        time.sleep(2)
        if not GPIO.input(BUTTON_SHUTDOWN):
            #print ("Exce Shutdown")
            subprocess.call(["sudo", "shutdown", "-h", "now"])

    def Reboot(channel):
        #print ("Reboot")
        time.sleep(1)
        if not GPIO.input(BUTTON_REBOOT):
            #print ("Exce Reboot")
            subprocess.call(["sudo", "shutdown", "-r", "now"])


    GPIO.add_event_detect(BUTTON_NEXT_PAGE, GPIO.FALLING, callback = NextPage, bouncetime = 500)
    GPIO.add_event_detect(BUTTON_SHUTDOWN, GPIO.FALLING, callback = ShutDown, bouncetime = 2500)
    GPIO.add_event_detect(BUTTON_REBOOT, GPIO.FALLING, callback = Reboot, bouncetime = 1500)

    while True:

        # Draw a black filled box to clear the image.
        draw.rectangle((0,0,disp.width,disp.height), outline=0, fill=0)

        y = 0 # Reset Line

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
            draw.text((x, y),    "IP: " + str(IP,'utf-8'),  font=font, fill=255)
            y = y + padding + size
            draw.text((x, y),    str(CPUL,'utf-8') + " " + str(Temp,'utf-8'), font=font, fill=255)
            y = y + padding + size
            draw.text((x, y),    str(CPUU,'utf-8'),  font=font, fill=255)
            y = y + padding + size
            draw.text((x, y),    str(MemUsage,'utf-8'),  font=font, fill=255)

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
            if not isinstance(Users,int): # If uptime is less than a day
                cmd = "uptime |cut -d , -f 2|awk '{print $1}'"
                Users = subprocess.check_output(cmd, shell = True)

            # Write Info To Display
            draw.text((x, y),    "IP: " + str(IP,'utf-8'),  font=font, fill=255)
            y = y + padding + size
            draw.text((x, y),    "Name: " + str(HostName,'utf-8'),  font=font, fill=255)
            y = y + padding + size
            draw.text((x, y),    "Uptime: " + str(UpTime,'utf-8'),  font=font, fill=255)
            y = y + padding + size
            draw.text((x, y),    "Users: " + str(Users,'utf-8'),  font=font, fill=255)
            y = y + padding + size

        if showpage == 3:
            # Get Display Info
            cmd = "df -h | grep '/dev/md\|/dev/sd\|/dev/root' | awk '{printf \"%s/%s %s, \", $3,$2,$5}'"
            DrvUse = str(subprocess.check_output(cmd, shell = True ),'utf-8')
            Drv = DrvUse.split(", ")

            # Write Info To Display
            i = 0
            while i < len(Drv)-1:
                draw.text((x, y),    "Drv" + str(i) + ": " + Drv[i],  font=font, fill=255)
                y = y + padding + size
                i += 1

        # Display image.
        disp.image(image)
        disp.display()

        # Wait
        time.sleep(updatetime)
