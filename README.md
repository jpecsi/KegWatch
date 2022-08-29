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

_Details to be added..._

