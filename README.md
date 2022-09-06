# KegWatch

<br>

## Overview
KegWatch is a sensor written in Python that estimates beer remaining in a keg based on flow rate. The sensor relies on hardware (reed switches) to know when the taps are physically opened and closed. 

<br>

## Hardware
- Raspberry Pi 3B+

- 2x Reed switches

- 2x LEDs

- 2x 330 Ohm resistors

<br>

## Configuration

Settings and configuration items are maintained in the _conf_ collection of the __kegwatch__ database. Configuration items include GPIO pin selection, calibration data, etc.

The _beer_ collection maintains all of the information related to each tap (in my case a 2 tap system). Things like beer name, keg size, remaining oz, etc. are stored.

The _consumption_ collection is an active log, any time a beer is poured the date/time, beer name, and amount (in oz) is logged here

<br>

## Setup

### Pre-Reqs

The following will need to be installed:

- Python3
- Mongodb
- pymongo
- paho-mqtt


### Configuration

1. After the pre-reqs have been installed, navigate to __KegWatch/setup__ and modify __beer.json__ to match your environment
2. Next, modify the __conf.json__ file and update the GPIO pins (numbering based on board) and MQTT server (don't worry about the oz_per_second, we will calibrate the system)
3. Execute the database configuration tool to create the database and collections: 
      `python3 setupdb.py`
      
4. Optionally use __manage.py__ to add/remove kegs from the system
5. Make all physical connections (reed switches to GPIO and ground, LED to GPIO and ground with resistor in line)
6. Run the sensor from the root of the _KegWatch_ directory
      `python3 sensor.py &`
      
7. Optionally, move the sensor to _/opt/kegwatch_ and configure it to run at boot through cron


<br>

## Considerations

- This is a fun side project, and I am no professional developer :)
- This is the first iteration of KegWatch so there are bound to be some issues somewhere
- This is designed for a 2 tap system and will easily work for 1 or 2 taps. It should be somewhat easy to expand for 3+ taps though as all of that info is stored in the mongo database

