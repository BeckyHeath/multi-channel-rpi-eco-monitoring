# multi-channel-rpi-eco-monitoring

unfinished code adapted from Sarab Sethi's work on Autonomous Ecosystem Monitoring. More information on that project and full details at: https://github.com/sarabsethi/rpi-eco-monitoring

## Setup 

Pending: The setup will either be done manually from a SD card image 

. If using the image, follow the "Configuration" steps below to customise your ecosystem monitoring protocol and finish install. If you'd like to set the Raspberry Pi up manually follow the manual setup below and *then* the Configuration procedure. 

### Manual Setup 

If you would rather start using a stock Raspbian image, there's an extra couple of steps before you start the above process. The below steps assume you have downloaded and installed the [Raspbian Stretch Lite image](https://www.raspberrypi.org/downloads/raspbian/).

You will need the Pi to be connected to the internet for the below process.

#### Install [Seeed Voicard](https://wiki.seeedstudio.com/ReSpeaker_6-Mic_Circular_Array_kit_for_Raspberry_Pi/)

* Login when prompted with user 'pi' and password 'raspberry'
* Open Terminal
* Update the system by running ``sudo apt-get update`` and ``sudo apt-get upgrade``
* Install git: ``sudo apt-get install git``
* Clone Seeed voice card repository into home directory of the Raspberry Pi ``git clone https://github.com/respeaker/seeed-voicecard.git``
* Switch to Seeed repository ``cd seeed-voicecard``
* Install the sound card ``sudo ./install.sh``
* Reboot the Pi ``sudo reboot``

##### Set up Multi-Channel Eco Monitoring

* Log in and open a terminal
* Clone this repository in the home directory of the Raspberry pi: ``git clone https://github.com/BeckyHeath/multi-channel-rpi-eco-monitoring.git`` (see below regarding branches)
* Make sure all the scripts in the repository are executable: ``chmod +x ~/multi-channel-rpi-eco-monitoring/*``
* Configure the Pi to run ``recorder_startup_script.sh`` on boot by adding ``sudo -u pi ~/multi-channel-rpi-eco-monitoring/recorder_startup_script.sh;`` to the last line of the file ``/etc/profile`` (requires root). You can do this manually or by running ``sudo nano /etc/profile``
* Install the required packages: ``sudo apt-get -y install fswebcam lftp ffmpeg usb-modeswitch ntpdate zip``
* Type ``sudo raspi-config`` and configure the Pi to boot to a command line, without login required: option _Boot Options_ -> _Desktop / CLI_ -> _Console Autologin_. Press ``Esc`` when this is complete

* Then follow the instructions below to complete the setup

### RPI Configuration

These steps are adapted from the [Single Channel Eco Monitoring Setup](https://github.com/sarabsethi/rpi-eco-monitoring)
Pending : add in link to pre-prepared SD card

* Boot the Raspberry Pi with our prepared SD card inserted. Let the startup script run until it exits with the message "Config file not found!". If you would like to change an existing configuration, press ``Ctrl+C`` when you see "Start of ecosystem monitoring startup script"
* Type ``cd ~/multi-channel-rpi-eco-monitoring``
* Run ``python setup.py`` and follow the prompts. This will create a ``config.json`` file which contains the sensor type, its configuration and the FTP server details. The config file can be created manually, or imported from external storage without running ``setup.py`` if preferred
* Make sure the timezone is set correctly. Check by typing ``sudo dpkg-reconfigure tzdata`` and following the prompts
* If your SD card is larger than the size of our pre-prepared image (4GB) run ``sudo raspi-config`` and choose: _Advanced Options_ -> _Expand Filesystem_. Press ``Esc`` when this is complete
* Type ``sudo halt`` to shut down the Pi
* Take the microSD card from the Pi, and make a copy of it onto your computer [(How?)](https://www.raspberrypi.org/documentation/installation/installing-images/). Now you can clone as many of these SD cards as you need for your monitoring devices with no extra setup required


### Importing New Sensors 

Importing addional sensors is possible by following protocol explained [here] (https://github.com/sarabsethi/rpi-eco-monitoring)


## Authors
This is a cross disciplinary research project based at Imperial College London, across the Faculties of Engineering, Natural Sciences and Life Sciences.

Work unique to this repo: Becky Heath 

All foundation work from the rpi-eco-monitoring repo: Sarab Sethi, Rob Ewers, Nick Jones, David Orme, Lorenzo Picinali

Feel free to [drop me an email](mailto:r.heath18@imperial.ac.uk) with questions 


## Citations
Please cite the below papers when referring to this work:

Sethi, SS, Ewers, RM, Jones, NS, Orme, CDL, Picinali, L. Robust, real‐time and autonomous monitoring of ecosystems with an open, low‐cost, networked device. Methods Ecol Evol. 2018; 9: 2383– 2387. https://doi.org/10.1111/2041-210X.13089 

Sethi, SS, Ewers, RM, Jones, NS, Signorelli, A., Picinali, L, Orme, CDL. SAFE Acoustics: an open-source, real-time eco-acoustic monitoring network in the tropical rainforests of Borneo. biorxiv 968867. https://doi.org/10.1101/2020.02.27.968867

