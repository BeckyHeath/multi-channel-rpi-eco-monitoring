# multi-channel-rpi-eco-monitoring

This is the code designed to run a MAARU (Multichannel Autonomous Acoustic Recording Unit). Full details on applications and hardware setup [here](https://beckyheath.github.io/MAARU/).

Code adapted by James Skinner, and Becky Heath from Sarab Sethi's work on Autonomous Ecosystem Monitoring. More information on that project and full details at: https://github.com/sarabsethi/rpi-eco-monitoring.

Key changes include:
  1. Installation of seeed multi-channel soundcard.
  2. Additional staging step for postprocessing.
  3. Added fault removal timeout in recording.
  4. Sensor adaptation to include multichannel recording.
  5. Added code to safely power down device, once button (on top of 6-mic Respeaker array) is pressed - instead of cutting power to the device
  6. Added code to check for remaining storage space on SD card, before recording - trying to record past limit causes corruption
  7. Added pre-set config.json file, specifically for offline data capture...
      a. Set to offline mode (won't attempt to connect to internet / FTP upload).
      b. Set compression to flac (in config.json & Respeaker6Mic.py)
  8. Old Data is deleted upon boot-up. Make sure that after the battery dies, DiskInternals Linux Reader - https://www.diskinternals.com/linux-reader/ - is used to recover the data.

NOTE! SD card should have sufficiently fast read/write speed (Class 10, **minimum 150 mb/s**), otherwise you will get overrun errors during recording. This means data won't record properly - you may see dead channels with no data.

This code has been setup to run on a **Raspberry Pi 3B**

## Setup 

### Pre setup image: 

We have made a new disk image for this fork. If using this image, clone the image to and SD card then skip ahead to the "RPI Configuration" steps below to customise your ecosystem monitoring protocol and finish install. This image can be found [here](https://drive.google.com/file/d/1sTKPgUOcT4SQeJqtF6wdd6rjtqFLZzfR/view?usp=sharing). If you'd like to set the Raspberry Pi up manually follow the manual setup below and *then* the Configuration procedure. 

### Manual Setup 

If you would rather start using a stock Raspbian image, there's an extra couple of steps before you start the setup process. The seeed soundcard only works on older versions of Raspbian Buster (Rasbian Buster, 13th Feb 2020 works well). 

### Setup overview

#### Pi OS setup: 

* Use a clean SD card - to erase contents of prev SD card, use 'Disk Utility' program on Mac or you can format the SD card fresh. 
* Download and extract the [recommended OS](https://downloads.raspberrypi.org/raspbian_full/images/raspbian_full-2020-02-14/) (the zip file) onto your computer.
* Flash the OS (.img file) to the SD card - you can use [Balana Etcher](https://www.balena.io/etcher/)
* Insert SD card into the pi and power on
* Make sure to use DEFAULT settings (don't change the password - keep as 'raspberry') - just click 'next'
* Connect to your wifi network
* **Do not install updates!** Make sure you **skip** this step as updated versions of raspbian are incompatible with the Respeaker sound card
* Update only the Pi Headers...
  * Open a new terminal
  * ``sudo apt-get install raspberrypi-kernel-headers``
  * ``sudo reboot`` (to ensure headers are properly updated)
* Then, prevent the kernels from further updates (which may break the Seeed Card firmware)...
  * Open new terminal
  * ``sudo apt-mark hold raspberrypi-kernel-headers raspberrypi-kernel``
  * ``sudo apt-mark showhold``  (to check it worked)
* Check that Python3 is already installed
  * ``python3`` in terminal --> Should show Python 3.7.3
  * Otherwise, install Python3 - ``sudo apt-get install python3``
* Install packages to read mounted drives
  * ``sudo apt-get install exfat-fuse``
  * ``sudo apt-get install exfat-utils``
 
#### Install [Seeed Voicard](https://wiki.seeedstudio.com/ReSpeaker_6-Mic_Circular_Array_kit_for_Raspberry_Pi/)

* Open Terminal
* Install git: ``sudo apt-get install git``
* Clone Seeed voice card repository into home directory of the Raspberry Pi ``git clone https://github.com/respeaker/seeed-voicecard.git``
* Switch to Seeed repository ``cd seeed-voicecard``
* Install the sound card ``sudo ./install.sh``
* Reboot the Pi ``sudo reboot``

##### Set up Multi-Channel Eco Monitoring

* Log in and open a terminal
* Clone this repository into the home directory of the Raspberry pi: ``git clone https://github.com/BeckyHeath/multi-channel-rpi-eco-monitoring.git`` (see below regarding branches)
* Install the required packages: ``sudo apt-get -y install fswebcam lftp ffmpeg usb-modeswitch ntpdate zip``
* If you want to use a different config file (e.g., want to upload to FTP server):
  * First, delete config.json from multi-channel-rpi-eco-monitoring folder
  * Open a new terminal
  * ``cd ~/multi-channel-rpi-eco-monitoring``
  * Run ``python setup.py`` and follow the prompts. This will create a ``config.json`` file which contains the sensor type, its configuration and the FTP server details.
* Make sure all the scripts in the repository are executable, and that ``recorder_startup_script.sh`` runs on startup...
  * Open a new terminal
  * ``sudo nano ../../etc/profile`` from the root directory
  * Add the following 2 lines to the end of the file:
    * ``chmod +x ~/multi-channel-rpi-eco-monitoring/*;``
    * ``sudo -u pi ~/multi-channel-rpi-eco-monitoring/recorder_startup_script.sh;``
* Make sure Pi boots to command line upon login (without login required)...
  * New terminal
  * ``sudo raspi-config``
  * _3 Boot Options_ -> _B1 Desktop / CLI_ -> _B2 Console Autologin_
  * Press ``Esc`` when this is complete -> Say No to reboot
  * Shutdown with ``sudo shutdown -h now``

### RPI Configuration

* Boot the Raspberry Pi with our prepared SD card inserted
* On first boot, the RasPi should automatically reboot, to expand the file system to max capacity of the SD Card (image is only 8 GB)
* A config file has already been provided in the image
  * Uses Respeaker 6 mic array
  * 1200 second (20 min) record time intervals
  * No upload to FTP server (fully offline)
**If you would like the Rasberry Pi to run online**...  press ``Ctrl+C`` when you see "Start of ecosystem monitoring startup script".
  * Type ``cd ~/multi-channel-rpi-eco-monitoring``
  * Run ``python setup.py`` and follow the prompts. This will create a ``config.json``   file which contains the sensor type, its configuration and the FTP server details. The config file can be created manually, or imported from external storage without running ``setup.py`` if preferred
  * Make sure the timezone is set correctly. Check by typing ``sudo dpkg-reconfigure tzdata`` and following the prompts
  * Type ``sudo halt`` to shut down the Pi
  * After reboot, the Pi should be good to go!

### Make a new disk image

* Take the microSD card from the Pi, and make a copy of it onto your computer [(How?)](https://howchoo.com/pi/create-a-backup-image-of-your-raspberry-pi-sd-card-in-mac-osx). 
  * Note: May need to run ``sudo -i`` (before sudo dd...) - this puts the terminal into root mode
  * Note: After running sudo dd... it may take a while - You get no indication of how far through you are - as long as the no error appears in the terminal, or no new line for code entry, just wait (up to 1 hour for 32 GB SD card)
* Now you can clone as many of these SD cards as you need for your monitoring devices with no extra setup required - install on new SD card with Balena Etcher


### Side Notes

* Be careful not to pull the power cable from the Pi (or pull the plug out the socket) - this has been known to corrupt the SD card, and requires a fresh install.
* Using a battery bank is a safe option - if it runs out of power, the Pi tends to shutdown safely.
* To safely power off, simply press the button on top of the Respeaker 6 Mic array, and wait for the green light (on the Pi) to stop flashing.

## Authors
This is a cross disciplinary research project based at Imperial College London, across the Faculties of Engineering, Natural Sciences and Life Sciences.

Work on this repo has been contributed by James Skinner, Becky Heath, Sarab Sethi, Rob Ewers, Nick Jones, David Orme, Lorenzo Picinali


## Citations
Please cite the below papers when referring to this work:

Sethi, SS, Ewers, RM, Jones, NS, Orme, CDL, Picinali, L. Robust, real‐time and autonomous monitoring of ecosystems with an open, low‐cost, networked device. Methods Ecol Evol. 2018; 9: 2383– 2387. https://doi.org/10.1111/2041-210X.13089 
