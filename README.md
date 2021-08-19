# ShadowCat

ShadowCat is a project of a robot car that cleans air ducts. It's powered by Raspberry Pi and ODrive. 

## How to run
This entire single filed program should be stored in the SDcard connected to the Raspberry Pi. I'm also running it via ssh from my laptop:

```
ssh pi@raspberrypi.local
```
The password is ```raspberry```.

To run the code, type:
```
python3 od_server.py
```

To run the camera stream:
```
lol gonna update this later
```

## Reference of ODrive Requested States
Below is the Python reference for the ODrive requested states. Use 8 before trying to control your motors programmatically using ODrive.
```
AXIS_STATE_UNDEFINED  —  0
* AXIS_STATE_IDLE  —  1
AXIS_STATE_STARTUP_SEQUENCE  —  2
* AXIS_STATE_FULL_CALIBRATION_SEQUENCE  —  3 
* AXIS_STATE_MOTOR_CALIBRATION  —  4 
AXIS_STATE_ENCODER_INDEX_SEARCH  —  6
AXIS_STATE_ENCODER_OFFSET_CALIBRATION  —  7
* AXIS_STATE_CLOSED_LOOP_CONTROL  —  8     <-- gets motor ready for being controlled
AXIS_STATE_LOCKIN_SPIN  —  9
AXIS_STATE_ENCODER_DIR_FIND  —  10
AXIS_STATE_HOMING  —  11
AXIS_STATE_ENCODER_HALL_POLARITY_CALIBRATION  —  12
AXIS_STATE_ENCODER_HALL_PHASE_CALIBRATION  —  13
```

My program assumes pre-calibration separately using the ```odrivetool``` command

## Raspberry Pi 
My programming assumed the address the Pi as 10.1.2.154. Please change it in od_server.py from ```host_name = '10.1.2.154'``` to host_name = ```'YOUR_PI_IP_ADDRESS'``` which can be found by typing ```ping raspberrypi.local``` in your terminal/command prompt.

## ODrive
Currently, the motors and ODrive are connected such that it looks like the below rough diagram sketch:
```
        The ODrive and the config atm for ShadowCat
        
                     BRUSH
        [] od2.axis1       [] od1.axis0


        [] od2.axis0       [] od1.axis1
```

The controlling of the motors are done through:
```
self.od1.axis0.controller.input_vel = N
self.od1.axis1.controller.input_vel = N
self.od2.axis0.controller.input_vel = -N
self.od2.axis1.controller.input_vel = -N
```
... where N is the speed. od2's value is -ve (reversing direction) so as to move in the same direction as od1's. 
