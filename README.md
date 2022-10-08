# SPL06-MEMS-barometer-micropython
A simple micropython library (class) used to drive SPL06 MEMS barometer. continuous measure mode, without interrupt

Sorry for some Chinese annotation, I didn't delete(translate) them because I'm lazy.

The SPL06 is a high precision MEMS barometer, its resolution of altitude can up to 5cm! (but I think maybe it's +-10cm, still very good)

It need some troublesome code to process the value you get from register and calculate altitude.

2 lib files to let you trade off between the refresh rate and precision.

I only tested it using my RaspberryPi Pico, didn't test it with other MCU...
