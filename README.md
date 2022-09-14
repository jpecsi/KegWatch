# KegWatch

<br>

## Overview
KegWatch is a sensor written in Python that estimates beer remaining in a keg based on flow rate. The sensor relies on hardware (reed switches) to know when the taps are physically opened and closed. For this to work you will need to place reed switches at the top of of your kegerator behind the tap handles, and install the pairing magnets on the tap handles close enough to register as "closed" when the tap handle is in the closed position and "open" when you pour beer.

<br>

## Hardware
- Raspberry Pi 3B+

- 2x Reed switches

- 2x LEDs

- 2x 330 Ohm resistors

<br>

## Configuration

Settings and beer are maintained in setup/settings.conf

The MySQL database is used to log all pours as well as users/consumers (tracking feature to be added down the road)

<br>

## Setup

### Pre-Reqs

The following will need to be installed:

- Python3
- mysql-server
- mysql-connector-python
- paho-mqtt


### Configuration

1. After the pre-reqs have been installed, navigate to __KegWatch/setup__ and modify __settings.conf__ to match your environment

2. Restore the database template to your MySQL server: 
      `mysql -u [user] -p [database] > setup/kegwatch.sql`
      
3. Make all physical connections (reed switches to GPIO and ground, LED to GPIO and ground with resistor in line)

4. Run the sensor from the root of the _KegWatch_ directory
      `python3 sensor.py &`
      
5. Optionally, move the sensor to _/opt/kegwatch_ and configure it to run at boot through cron


<br>

## Considerations

- This is a fun side project, and I am no professional developer :)
- This is designed for a 2 tap system and will easily work for 1 or 2 taps. It should be somewhat easy to expand for 3+ taps though as all of that info is stored in the mongo database

