# ShadowCat

ShadowCat is a project of a robot car that cleans air ducts. It's powered by Raspberry Pi and ODrive. Other libraries used include ```pigpio```, and ```mjpg-streamer```. More info can be found here: 
https://abyz.me.uk/rpi/pigpio/python.html and; 
https://github.com/jacksonliam/mjpg-streamer;
respectively.

## Motor Calibration using ODrive
The motor in use is the E-Tech Brushless 4 Inch Electric Single Shaft Hub Motor Wheel. Different hub motor wheel, of course, will have different configuration to the one below. The datasheet from the manufacturer is a good place to start to find the technical specification which will help you in configuring your motors. You can refer to the official documentation for the ODrive for more detailed information: https://docs.odriverobotics.com/

```
odrv0.config.brake_resistance=11.5
odrv0.axis0.motor.config.pole_pairs=10
odrv0.axis0.motor.config.motor_type =MOTOR_TYPE_HIGH_CURRENT
odrv0.axis0.encoder.config.cpr=60
odrv0.axis0.motor.config.torque_constant = 1
odrv0.axis0.motor.config.resistance_calib_max_voltage = 15
odrv0.axis0.motor.config.requested_current_range = 25
odrv0.axis0.encoder.config.mode = ENCODER_MODE_HALL
odrv0.axis0.controller.config.pos_gain = 20
odrv0.axis0.controller.config.vel_gain = 0.02 * odrv0.axis1.motor.config.torque_constant * odrv0.axis1.encoder.config.cpr
odrv0.axis0.controller.config.vel_integrator_gain = 0.1 * odrv0.axis1.motor.config.torque_constant * odrv0.axis1.encoder.config.cpr
odrv0.axis0.controller.config.vel_limit = 10
odrv0.axis0.controller.config.control_mode = CONTROL_MODE_VELOCITY_CONTROL
```

These settings are required as well, and has helped increased the holding torque (makes the wheel hold stronger when external forces are applied)
```
odrv0.axis0.motor.config.current_control_bandwidth = 35
odrv0.axis0.motor.config.current_lim = 25
odrv0.axis0.encoder.config.bandwidth = 800
odrv0.axis0.controller.config.pos_gain = 70
odrv0.axis0.controller.config.vel_gain = 30
odrv0.axis0.controller.config.vel_indicator_gain = 30
```

Run these to save them:
```
odrv0.save_configuration()
odrv0.reboot()
```

After that, run each of these lines individually and ensure no errors had occured after each run:
```
odrv0.axis0.requested_state = AXIS_STATE_MOTOR_CALIBRATION
odrv0.axis0.requested_state = AXIS_STATE_ENCODER_OFFSET_CALIBRATION
```

To check for errors, simply run ```dump_errors(odrv0)```

When you have ensured that there are no errors, run these lines:
```
odrv0.axis0.motor.config.pre_calibrated = True
odrv0.axis0.encoder.config.pre_calibrated = True
```

Run these again:
```
odrv0.save_configuration()
odrv0.reboot()
```

## ODrive Speed Control
Prepare the motor for control by running these:
```
odrv0.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
```

To control the speed, run this:
```
odrv0.axis1.controller.input_vel = 2 
```
Feel free to play around the value (but of course, don't go crazy with it)

You can stop it simply by running this
```
odrv0.axis1.controller.input_vel = 0
```

To idle the motor and prevent further control, run:
```
odrv0.axis0.requested_state = AXIS_STATE_IDLE
```

More detailed information can be found in the official documentation of ODrive: https://docs.odriverobotics.com/
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
cd mjpg-streamer
cd mjpg-streamer-experimental
<<will update the remaining execution line here soon>>
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
