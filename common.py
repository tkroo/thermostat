from machine import Pin

# Note for esp32c3
# mosi and miso are swapped intentionally here because of this issue:
# https://forum.seeedstudio.com/t/xiao-esp32c3-expansion-board-sd-card-miso-line-stays-low-fix/268404
# using SoftSPI instead of SPI, avoids this problem. :)
PINS = {
    "spi_mosi": Pin(9),
    "spi_miso": Pin(10),
    "spi_sck": Pin(8),
    "spi_cs": Pin(20),

    "scl": Pin(7),
    "sda": Pin(6),
    "relay": Pin(21, Pin.OUT, value=0),
    "toggle": Pin(5, Pin.IN, Pin.PULL_UP),
    "temp_down": Pin(4, Pin.IN, Pin.PULL_UP),
    "temp_up": Pin(3, Pin.IN, Pin.PULL_UP),
}

SETTINGS_FILE = "sd/heating_schedule.json"
