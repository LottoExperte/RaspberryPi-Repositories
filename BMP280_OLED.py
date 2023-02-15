#! /usr/bin/python3

#  Joerg Hoffmann  joerg@hoffmann-software.de
#  Dieses kleine Programm zeigt die Temperatur und den Luftdruck 
#  auf einem kleinem OLED Display an. Gemessen wird mit einem 
#  BMP280 am Raspberry PI
#  Die Daten werden in das HTML Verzeichnis des Web-Servers gespeicher.
#  Ich lesen diesen Daten dann in mein Home Assistant ein.

# -*- coding: utf-8 -*-
import smbus
import time
import datetime
import codecs

#Bibliotheken einbinden
from lib_oled96 import ssd1306
from PIL import ImageFont, ImageDraw, Image
font = ImageFont.load_default()
# number of I2C bus
BUS = 1

# BMP280 address, 0x76 or 0x77
BMP280ADDR = 0x76
OLEDADDR = 0x3c

# altitude 500 m
ALTITUDE = 450

# get I2C bus
bus = smbus.SMBus(BUS)
time.sleep(1)
#geloescht
oled = ssd1306(bus)
draw = oled.canvas


#logo = Image.open("pi_logo.png")
#draw.bitmap(0,0, logo, fill=0)

#geloesch
#oled.cls()
#oled.display()

temperatur1 = 0.0
temperatur2 = 0.0
druck1 = 0.0
druck2 = 0.0
wetterdatei = "/var/www/html/StubeTemp.htm"
druckdatei = "/var/www/html/StubeDruck.htm"
druckmerk = 0.0
merktemp = 0.0
while 1:
 try:
  # temperature calibration coeff. array
  T = [0, 0, 0];
  # pressure calibration coeff. array
  P = [0, 0, 0, 0, 0, 0, 0, 0, 0];

  # read calibration data from 0x88, 24 bytes
  data = bus.read_i2c_block_data(BMP280ADDR, 0x88, 24)

  # temp coefficents
  T[0] = data[1] * 256 + data[0]
  T[1] = data[3] * 256 + data[2]
  if T[1] > 32767:
    T[1] -= 65536
  T[2] = data[5] * 256 + data[4]
  if T[2] > 32767:
    T[2] -= 65536

  # pressure coefficents
  P[0] = data[7] * 256 + data[6];
  for i in range (0, 8):
    P[i+1] = data[2*i+9]*256 + data[2*i+8];
    if P[i+1] > 32767:
      P[i+1] -= 65536

  # select control measurement register, 0xF4
  # 0x27: pressure/temperature oversampling rate = 1, normal mode
  bus.write_byte_data(BMP280ADDR, 0xF4, 0x27)

  # select configuration register, 0xF5
  # 0xA0: standby time = 1000 ms
  bus.write_byte_data(BMP280ADDR, 0xF5, 0xA0)

  time.sleep(1.0)

  # read data from 0xF7, 8 bytes
  data = bus.read_i2c_block_data(BMP280ADDR, 0xF7, 8)
  
  # convert pressure and temperature data to 19 bits
  adc_p = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
  adc_t = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)

  # convert pressure and temperature data to 19 bits
  adc_p = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
  adc_t = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)

  # temperature offset calculations
  temp1 = ((adc_t)/16384.0 - (T[0])/1024.0)*(T[1]);
  temp3 = (adc_t)/131072.0 - (T[0])/8192.0;
  temp2 = temp3*temp3*(T[2]);
  temperature = (temp1 + temp2)/5120.0

  # pressure offset calculations
  press1 = (temp1 + temp2)/2.0 - 64000.0
  press2 = press1*press1*(P[5])/32768.0
  press2 = press2 + press1*(P[4])*2.0
  press2 = press2/4.0 + (P[3])*65536.0
  press1 = ((P[2])*press1*press1/524288.0 + (P[1])*press1)/524288.0
  press1 = (1.0 + press1/32768.0)*(P[0])
  press3 = 1048576.0 - (adc_p)
  if press1 != 0:
    press3 = (press3 - press2/4096.0)*6250.0/press1
    press1 = press3*press3*(P[8])/2147483648.0
    press2 = press3*(P[7])/32768.0
    pressure = (press3 + (press1 + press2 + (P[6]))/16.0)/100
  else:
    pressure = 0
  # pressure relative to sea level
  pressure_nn = pressure/pow(1 - ALTITUDE/44330.0, 5.255)

  # output data to screen
  temperature = round(temperature,2)
  pressure = round(pressure,2)
  
  #oled.display()
  #oled.cls()
  # Feld komplett löschen
  
  #geloescht
  draw.rectangle((11,0, 127, 63), outline=0, fill=0)
  font = ImageFont.truetype('/home/pi/FreeSans.ttf', 12)
  draw.text((5, 1), datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S') , font=font, fill=1)
  font = ImageFont.truetype('/home/pi/FreeSans.ttf', 30)
  draw.text((10, 15), str(temperature)+ "°C " , font=font,fill=1)
  font = ImageFont.truetype('/home/pi/FreeSans.ttf', 12)
  draw.text((55, 50), str(pressure) + " hPa  ", font=font, fill=1)
  

  #draw.bitmap((0,0, logo, fill=0)
  
  #geloescht
  oled.display()

  temperatur2 = temperatur1
  druck2 = druck1
  temperatur1 = temperature

  if (temperatur1 != temperatur2):
    merktemp = temperatur2
    file = codecs.open(wetterdatei, "w", "utf-8")
    file.write(str(int(temperatur1*100)))
    file.close()

  druck1 = pressure
  draw.rectangle((0,10, 127, 63), outline=0, fill=0) 
  if (temperatur1 > merktemp):
    draw.line((5, 15, 5, 45), fill=1)
    draw.line((5, 15, 0, 20), fill=1)
    draw.line((5, 15, 10, 20), fill=1)
  else:
    draw.line((5, 15, 5, 45), fill=1)
    draw.line((5, 45, 0, 40), fill=1)
    draw.line((5, 45, 10, 40), fill=1)
  

  if (druck1 != druck2):
    druckmerk = druck2
    file = codecs.open(druckdatei, "w", "utf-8")
    file.write(str(int(round(druck1*100)))+"\n")
    file.close()


  if (druck1 > merkdruck):
    draw.line((45, 50, 45, 60), fill=1)
    draw.line((45, 50, 42, 53), fill=1)
    draw.line((45, 50, 48, 53), fill=1)
  else:
    draw.line((45, 50, 45, 60), fill=1)
    draw.line((45, 60, 42, 57), fill=1)
    draw.line((45, 60, 48, 57), fill=1)

    #print("Temperature: ",temperature, "C    =>" , round(temperatur1-temperatur2,2))
    #print("Pressure:    ", pressure, "hPa  =>", round(druck1-druck2,2))
    #print("Pressure NN: ", round(pressure_nn,2),"hPa")
  oled.display()
  time.sleep(60-int(datetime.datetime.now().strftime("%S")))
 except:
  time.sleep(60)
  try:
   bus = smbus.SMBus(BUS)
   oled = ssli306(bus)
  except:
   time.sleep(60)

    
