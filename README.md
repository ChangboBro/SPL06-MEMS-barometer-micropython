# SPL06-MEMS-barometer-micropython
A simple micropython library (class) used to drive SPL06 MEMS barometer. continuous measure mode, without interrupt

~~Sorry for some Chinese annotation, I didn't delete(translate) them because I'm lazy.~~ new version is annotated in English.

The SPL06 is a high precision MEMS barometer, its resolution of altitude can up to 5cm! (but I think maybe +-10cm, still very good)

It need some troublesome code to process the value you get from register and calculate altitude.

2 lib files to let you trade off between the refresh rate and precision.

I only tested it using my RaspberryPi Pico, didn't test it with other MCU...

2023.4.8: the SPL06.py is a new version of spl06_obsolete.py, I rewrote the code to improve readability.
The old version (use int.from_bytes(), new version just use buff[] to turn bytearray into int) somehow faster at first, but I change the procedure and made the pressure reading faster a little in the new version. 
