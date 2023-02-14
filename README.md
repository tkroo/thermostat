# Micropython thermostat for heat only system.
A diy thermostat for 2-wire style heating units. Reads temperature from sensor, compares to set point, triggers relay if current temp is lower than set point minus a hysteresis value.  
Web interface allows to set a schedule or manually adjust temperature.  


## hardware
- Seeed Studio XIAO ESP32C3
- SHTC3 Temperature Sensor
- SPI sdcard module
- I2C OLED 128x64 0.96inch display
- KY-019 5V relay module


## credits
https://github.com/micropython/micropython  
https://github.com/miguelgrinberg/microdot  
https://github.com/alpinejs/alpine  
https://github.com/kevinkk525/pysmartnode/blob/dev/pysmartnode/utils/abutton.py  
https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/storage/sdcard/sdcard.py  
https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/display/ssd1306/ssd1306.py  
https://github.com/RAKWireless/Micropython-LoRaWAN-on-RAK4600/blob/master/shtc3.py  


## TODO
learn more python.  
decide about rate of readings and updates  
add mqtt for reporting and control   
rotary encoder for setting temp?  
re-write front-end  