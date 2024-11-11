from m5stack import *
from m5stack_ui import *
from uiflow import *
import time
import machine
import unit
import wifiCfg
from m5mqtt import M5mqtt

# Output variables
hum = 0
temp = 0

# Input variables
txtTemp = None
txtAlert = None
txtHum = None
txtWifi = None
txtAlText = None
m5Info = None

# Alert variable
alert_val = 0
maxAlert = 120
minAlert = -40
alertCount = 0
alertNow = 3

# Screen variables
screen = M5Screen()
imgTemp = None
imgHum = None

# Sensor variable
env = unit.get(unit.ENV2, unit.PORTA)

# WiFi variable
WiFiSSID = "fg-11a-u"
WifiPassword = "Miroslavpatik"
rtc = machine.RTC()

# MQTT variables
name = "PatejdlM5"
host = "test.mosquitto.org"
port = 1883
topHum = "zpi/humidity"
topTem = "zpi/temperature"
topTime = "zpi/time"
m5mqtt = M5mqtt(name, host, port, '', '', 120)

# Time variable 
day = None
month = None
year = None
hour = None
minut = None
sec = None 

###########################################
# Functions which works with buttons 
def buttonA_wasPressed():
  """
  function decreaments alert_value if button A is pressed
  """
  global alert_val, minAlert
  if (alert_val > minAlert):
    alert_val = alert_val - 1
    updateAlert()


def buttonC_wasPressed():
  """
  function increaments alert_value if button C is pressed
  """
  global alert_val, maxAlert
  if (alert_val < maxAlert):
    alert_val = alert_val + 1
    updateAlert()
  
#############################################
# Functions, which works with screen
def Screen_Set():
  """
  This function set UI of m5stack 
  """
  global txtHum, txtTemp, screen, txtAlert, alert_val, txtAlText
  # screen
  screen.clean_screen()
  screen.set_screen_bg_color(0xffffff)
  
  # text position
  txtTemp = M5Label("", x = 10, y = 75, color = 0x000000, font = FONT_MONT_18)
  txtHum = M5Label("", x = 244, y = 75, color = 0x000000, font = FONT_MONT_18)
    
  # icons
  imgTemp = M5Img("res/thot.png", x = 90, y = 42, parent = None)
  imgHum = M5Img("res/hum.png", x = 165, y = 42, parent = None)
    
  # alert
  alert_sign = M5Label('ALERT VALUE', x = 73, y = 120, color = 0xff0000, font = FONT_MONT_26)
  txtAlert = M5Label(str(alert_val), x = 150, y = 160, color = 0x000000, font = FONT_MONT_38)
  txtAlText = M5Label("", x = 60, y = 210, color = 0x0000ff, font = FONT_MONT_26)
    
  # lines
  line_Hor = M5Line(0, 120, 320, 115, 0x0000ff, 5)  # horizontal line
  line_Ver = M5Line(160, 0, 160, 120, 0x0000ff, 5)  # vertical line


def updateAlert():
  """
  function updates alert value on screen
  """
  global txtAlert, alert_val
  if ((alert_val < 0 and alert_val > -10) or alert_val > 9):
    txtAlert.set_pos(145,160)
  elif (alert_val < -9 or alert_val == 100):
    txtAlert.set_pos(130,160)
  else:
    txtAlert.set_pos(150,160)

  txtAlert.set_text(str(alert_val))
  

def Screen_Update():
  """
  Functions updates temperature and humidity value on the screen
  Also changes pictuere of thermometer on the screen if temperature is under 0
  """
  global temp, hum, txtHum, txtTemp
  txtTemp.set_text("%.2f°C" %temp)
  txtHum.set_text("%.2f" %hum + "%")
  if (temp <= 0):
    imgTemp = M5Img("res/tcold.png", x = 80, y = 42, parent = None)
  else:
    imgTemp = M5Img("res/thot.png", x = 80, y = 42, parent = None)
  alertSign()
 
 ########################################################################### 

def connectWiFi():
  """
  Functionn connects device to wifi
  """
  global txtWifi, WifiPassword, WiFiSSID
  txtWifi = M5Label("Connecting Wi-Fi...", x = 70, y = 120, color = 0x000000, font = FONT_MONT_18)
  wait(1)
  wifiCfg.doConnect(WiFiSSID, WifiPassword)
  txtWifi.set_text("Wi-Fi connected.")
  wait(2)
  txtWifi.set_text("")
  
def alertSign():
  """
  Function shows text, which indicates exeeding of aler value
  """
  global alert_val, alertNow, alertCount, temp, txtAlText
  if (alert_val < temp):
    alertCount += 1
    if (alertCount == alertNow):
      txtAlText.set_text("Value Exceeded!")
  else:
    alertCount = 0
    txtAlText.set_text("")


##########################################################
#                 Time Settings function                 #
##########################################################
def setTimeAndScreen():
  """
  function sets actual time and calls Screen_Set for preparation of screen 
  """
  global day, month, year, hour, minut, sec, rtc, m5Info
  
  screen.clean_screen()
  screen.set_screen_bg_color(0xffffff)
  m5Info = M5Label("Set Actuall Time", x = 70, y = 120, color = 0x000000, font = FONT_MONT_18)
  while (day is None or month is None or year is None or hour is None or minut is None or sec is None):
    m5Info.set_text("Set Actuall Time")
    wait(2)
  
  m5Info.set_text(str(day) + "." + str(month) + "." + str(year) + " " + str(hour) + ":" + str(minut) + ":" + str(sec))
  rtc.datetime((int(year), int(month), int(day), 0, int(hour), int(minut), int(sec), 0))
  wait(2)
  m5Info.set_text("")
  
  Screen_Set()
  
def buttonB_wasPressed():
  """
  function resets time's variables to None
  """
  global day, month, year, hour, minut, sec
  day = None
  month = None
  year = None
  hour = None
  minut = None
  sec = None
  setTimeAndScreen()
##############################################################################

def loadData():
  """
  Loads data form sensor
  """
  global env, temp, hum
  temp = env.temperature
  hum = env.humidity

def sentData():
  """
  function sent data to MQTT server
  """
  global temp, hum, m5mqtt, topHum, topTem, rtc
  currentTime = rtc.datetime()
  year, month, day, _, hour, minute, second, _ = currentTime
  convTime = str(day)+ "."  + str(month) + "."  + str(year) + " " + str(hour) + ":" + str(minute) + ":" +  str(second)
  m5mqtt.publish(topTem, json.dumps({"temperature": temp, "time": convTime}))
  m5mqtt.publish(topHum, json.dumps({"humidity": hum, "time": convTime}))
  
  
def sub_cb(data):
  """
  function for recieving data from server
  """
  global day, month, year, hour, minut, sec, m5Info
  data = str(data)
  try:
    dayOfyear, timeOfday = data.split(" ")
    day, month, year = dayOfyear.split(".")
    hour, minut, sec = timeOfday.split(":")
  except:
    m5Info.set_text("Invalid input")
    wait(2)
    pass
  
##############################################################################

def main():
  global m5mqtt, day, month, year, hour, minut, sec, m5Info
  # connecting WiFi
  connectWiFi()
  
  # setting MQTT interface
  m5mqtt.subscribe(str(topTime), sub_cb)
  m5mqtt.set_last_will("zpi", '...End...')
  
  m5mqtt.start()
  
  m5mqtt.publish("zpi", "...Start...")
  m5Info = M5Label("MQTT Activated", x = 70, y = 120, color = 0x000000, font = FONT_MONT_18)
  wait(2)
  m5Info.set_text("")
  
  # setting what to do if btnA or btnC is pressed
  btnA.wasPressed(buttonA_wasPressed)
  btnB.wasPressed(buttonB_wasPressed)
  btnC.wasPressed(buttonC_wasPressed)
  
  setTimeAndScreen()
  
  while (True):
    loadData()
    sentData()
    Screen_Update()
  
    time.sleep(20)
  
main()
