# I mixed the axample from adafruit BLE connect app example
# and the example from https://www.rototron.info/circuitpython-nrf52840-lcd-displays-tutorial/
# example from ROTOTRON WAS USING SOME #from adafruit_ble.uart import UARTServer
# which doesn't exist now at 4/18/2020 whiled chase but did the work around.
# he he he he he
# BLE stuff from https://learn.adafruit.com/circuitpython-nrf52840?view=all
# make fonts here https://learn.adafruit.com/custom-fonts-for-pyportal-circuitpython-display?view=all
# 4/27/20


from adafruit_display_text import label
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
import time
import board
import displayio
import adafruit_ili9341
#from adafruit_dht import DHT22
#from adafruit_ble.uart import UARTServer
from adafruit_ble.services.nordic import UARTService
import adafruit_ble
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.device_info import DeviceInfoService
from adafruit_ble.services.nordic import UARTService
from adafruit_ble_heart_rate import HeartRateService
from terminalio import FONT, Terminal
from time import sleep
from digitalio import DigitalInOut, Direction


# Initialize UART server & start advertising
uart_server = UARTService()
ble = BLERadio()
advertisement = ProvideServicesAdvertisement(uart_server)
#uart_server.start_advertising()
ble.start_advertising(advertisement)

spi = board.SPI()
tft_cs = board.D9
tft_dc = board.D10

displayio.release_displays()
display_bus = displayio.FourWire(
    spi, command=tft_dc, chip_select=tft_cs, reset=board.D6
)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)

## ON BOARD LEDssss

# Feather on-board status LEDs setup
red_led = DigitalInOut(board.RED_LED)
red_led.direction = Direction.OUTPUT
red_led.value = True

blue_led = DigitalInOut(board.BLUE_LED)
blue_led.direction = Direction.OUTPUT
blue_led.value = False

# print ( "hello world")
main_group = displayio.Group(max_size=5) # main group or background
main_group.x = 0
main_group.y = 0


# image one
image_file = open("/MTB.bmp", "rb")
image = displayio.OnDiskBitmap(image_file)
image_sprite = displayio.TileGrid(image, pixel_shader=displayio.ColorConverter())
# main_group.append(image_sprite)

# image two

image_file2 = open("/fallout_boy.bmp", "rb")                  #("/bio_small.bmp", "rb")
image2 = displayio.OnDiskBitmap(image_file2)
image_sprite2 = displayio.TileGrid(image2, pixel_shader=displayio.ColorConverter())

# define additional groups.
view1 = displayio.Group(max_size=15, x=0, y=40) # Group for View 1 objects
view2 = displayio.Group(max_size=15, x=0, y=40) # Group for View 2 objects
view3 = displayio.Group(max_size=15, x=0, y=100)  # Group for view 3 objects
view4 = displayio.Group(max_size=15,scale=1, x=220, y=0) # Group for view 4 objects

# load a font
# Set the font and preload letters
font = bitmap_font.load_font("/-30.bdf")
font.load_glyphs(b'abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890- ()')

# font placement
# Default Label postion
TABS_X = 0
TABS_Y = 0

TABS2_X = 0
TABS2_Y = 30

TABS3_X = 60
TABS3_Y = 0

#TABS4_X = 0
#TABS4_Y = 120

# text lable Object

other_data =  Label(font, text="OTHER DATA", color=0x0000ff, max_glyphs=100)
sensor_data = Label(font, text="HR: ", color=0xFF0000, max_glyphs=100)

# place marker for HR value before making it equal to bpm in the while statement.

sensor_HR = Label(font, color=0xFF0000, max_glyphs=100)

# AREA FOR SENSOR DATA
sensor_data.x = TABS_X
sensor_data.y = TABS_Y

# AREA FOR OTHER DATA
other_data.x = TABS2_X
other_data.y = TABS2_Y

# AREA FOR HR DATA
sensor_HR.x = TABS3_X
sensor_HR.y = TABS3_Y


# AREA FOR HR DATA


# ------------- Layer Functions ------------- #
# Hide a given Group by removing it from the main display Group.
def hideLayer(i):
    try:
        main_group.remove(i)
    except ValueError:
        pass
# Show a given Group by adding it to the main display Group.
def showLayer(i):
    try:
        main_group.append(i)
    except ValueError:
        pass
#_________________________________________________#############

# sticking to the views
view1.append(sensor_data)
view1.append(sensor_HR)
view2.append(other_data)
view3.append(image_sprite) # I put the image on view3 group so I can take it off if needed.
view4.append(image_sprite2)

# stick views to main_group
main_group.append(view4)
main_group.append(view3)
main_group.append(view2)
main_group.append(view1)
display.show(main_group)


# PyLint can't find BLERadio for some reason so special case it here.
ble = adafruit_ble.BLERadio()    # pylint: disable=no-member

hr_connection = None
# Start with a fresh connection.

if ble.connected:
    print("connected")
    time.sleep(1)

    for connection in ble.connections:
        if HeartRateService in connection:
            connection.disconnect()
        break



while True:

    #sleep(1)
    #hideLayer(view2)
    #sleep(1)
    #showLayer(view2)
    #sleep(1)
    #hideLayer(view2)
    #sleep(1)
    #showLayer(view2)


    print("Scanning...")
    sensor_HR.text = ("Scanning...")
    red_led.value = True
    blue_led.value = False
    time.sleep(1)
    for adv in ble.start_scan(ProvideServicesAdvertisement, timeout=5):
        if HeartRateService in adv.services:
            print("found a HeartRateService advertisement")
            hr_connection = ble.connect(adv)
            time.sleep(2)
            print("Connected")
            blue_led.value = True
            red_led.value = False
            break

    # Stop scanning whether or not we are connected.
    ble.stop_scan()
    print("Stopped scan")
    red_led.value = False
    blue_led.value = True
    time.sleep(0.5)

    if hr_connection and hr_connection.connected:
        print("Fetch connection")
        if DeviceInfoService in hr_connection:
            dis = hr_connection[DeviceInfoService]
            try:
                manufacturer = dis.manufacturer
            except AttributeError:
                manufacturer = "(Manufacturer Not specified)"
            try:
                model_number = dis.model_number
            except AttributeError:
                model_number = "(Model number not specified)"
            print("Device:", manufacturer, model_number)
        else:
            print("No device information")

        hr_service = hr_connection[HeartRateService]
        print("Location:", hr_service.location)

        while hr_connection.connected:
            values = hr_service.measurement_values
            print(values)  # returns the full heart_rate data set
            if values:
                bpm = (values.heart_rate)
                print("heart rate:", bpm)
                sensor_HR.text = bpm
                time.sleep(0.9)
