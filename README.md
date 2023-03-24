# multi-channel-rpi-eco-monitoring

Code adapted from Becky Heath's work on multi channel acoustic recording - see: https://github.com/BeckyHeath/multi-channel-rpi-eco-monitoring
Changes here have been made for remote deployment in areas where solar charging is not feasible, and so batteries must be regularly swapped in and out. Similarly, SD cards will need swapping in and out, as these areas will have very limited internet access (no possibility of remote uploading of data). Key changes:
  1. Added code to safely power down device, once button (on top of 6-mic Respeaker array) is pressed - instead of cutting power to the device
  2. Added code to check for remaining storage space on SD card, before recording - trying to record past limit causes corruption
  3. Added pre-set config.json file, specifically for offline data capture...
      a. Set to offline mode (won't attempt to connect to internet / FTP upload).
      b. Set compression to flac (in config.json & Respeaker6Mic.py)

NOTE! SD card should have sufficiently fast read/write speed (Class 10, **minimum 150 mb/s**), otherwise you will get overrun errors during recording. This means data won't record properly - you may see dead channels with no data.

## Setup 

### Pre setup image: 

We have made a new disk image for this fork. If using this image, clone the image to and SD card then skip ahead to the "RPI Configuration" steps below to customise your ecosystem monitoring protocol and finish install. This image can be found here: XXX. If you'd like to set the Raspberry Pi up manually follow the manual setup below and *then* the Configuration procedure. 

### Manual Setup 

If you would rather start using a stock Raspbian image, there's an extra couple of steps before you start the setup process. The seeed soundcard only works on older versions of Raspbian Buster. The following instructions are modified from Becky Heath's Repository...

### Setup overview

#### Pi OS setup: 

* Use a clean SD card - to erase contents of prev SD card, use 'Disk Utility' program on Mac
* Download and extract the [recommended OS](https://downloads.raspberrypi.org/raspbian_full/images/raspbian_full-2020-02-14/) (the zip file) onto your computer.
* Flash the OS (.img file) to the SD card - you can use [Balana Etcher](https://www.balena.io/etcher/)
* Insert SD card into the pi and power on
* Make sure to use DEFAULT settings (don't change the password - keep as 'raspberry')
* Set Date and Time
* **Do not install updates!** Make sure you skip this step as updated versions of raspbian are incompatible with the Respeaker sound card
* Update only the Pi Headers
  * Open a new terminal
  * sudo apt-get install raspberrypi-kernel-headers
  * sudo reboot (to ensure headers are properly updated)
* Then, prevent the kernels from further updates (which may break the Seeed Card firmware)...
  * Open new terminal
  * sudo apt-mark hold raspberrypi-kernel-headers raspberrypi-kernel
  * sudo apt-mark showhold  (to check it worked)
* Install Python3
  * sudo apt-get install python3
 
#### Install [Seeed Voicard](https://wiki.seeedstudio.com/ReSpeaker_6-Mic_Circular_Array_kit_for_Raspberry_Pi/)

* Open Terminal
* Install git: ``sudo apt-get install git``
* Clone Seeed voice card repository into home directory of the Raspberry Pi ``git clone https://github.com/respeaker/seeed-voicecard.git``
* Switch to Seeed repository ``cd seeed-voicecard``
* Install the sound card ``sudo ./install.sh`` (you may need to use ``sudo ./install.sh --compat-kernel`` if you run into trouble installing on an incompatible kernel)
* Reboot the Pi ``sudo reboot``

##### Set up Multi-Channel Eco Monitoring

* Log in and open a terminal
* Clone this repository into the home directory of the Raspberry pi: ``git clone https://github.com/JamesSkinna/multi-channel-rpi-eco-monitoring.git`` (see below regarding branches)
* Make sure all the scripts in the repository are executable, and that ``recorder_startup_script.sh`` runs on startup...
  * Open a new terminal
  * ``sudo nano ../../etc/profile`` from the root directory
  * Add the following 2 lines to the end of the file:
    * ``chmod +x ~/multi-channel-rpi-eco-monitoring/*;``
    * ``sudo -u pi ~/multi-channel-rpi-eco-monitoring/recorder_startup_script.sh;``
* Install the required packages: ``sudo apt-get -y install fswebcam lftp ffmpeg usb-modeswitch ntpdate zip``
* Make sure Pi boots to command line upon login (without login required)...
  * New terminal
  * ``sudo raspi-config``
  * _3 Boot Options_ -> _B1 Desktop / CLI_ -> _B2 Console Autologin_
  * Press ``Esc`` when this is complete and reboot with ``sudo reboot``

### RPI Configuration

* Boot the Raspberry Pi with our prepared SD card inserted
* On first boot, the RasPi should automatically reboot, to expand the file system to max capacity of the SD Card (image is only 8 GB)
* A config file has already been provided in the image
  * Uses Respeaker 6 mic array
  * 1200 second (20 min) record time intervals
  * No upload to FTP server (fully offline)
* After reboot, the Pi should be good to go!
* If you want to use a different config file (e.g., want to upload to FTP server):
  * First, delete config.json from multi-channel-rpi-eco-monitoring folder
  * Open a new terminal
  * ``cd ~/multi-channel-rpi-eco-monitoring``
  * Run ``python setup.py`` and follow the prompts. This will create a ``config.json`` file which contains the sensor type, its configuration and the FTP server details.
* Take the microSD card from the Pi, and make a copy of it onto your computer [(How?)](https://www.raspberrypi.org/documentation/installation/installing-images/). Now you can clone as many of these SD cards as you need for your monitoring devices with no extra setup required

### Side Notes

* Be careful not to pull the power cable from the Pi (or pull the plug out the socket) - this has been known to corrupt the SD card, and requires a fresh install
* Using a battery bank is a safe option - if it runs out of power, the Pi tends to shutdown safely
* To safely power off, simply press the button on top of the Respeaker 6 Mic array, and wait for the green light (on the Pi) to stop flashing

## Authors
This is a cross disciplinary research project based at Imperial College London, across the Faculties of Engineering, Natural Sciences and Life Sciences.

Work unique to this repo: James Skinner 

All foundation work from the rpi-eco-monitoring repo: Sarab Sethi, Rob Ewers, Nick Jones, David Orme, Lorenzo Picinali

Feel free to [drop me an email](mailto:jts19@ic.ac.uk) with questions 


## Citations
Please cite the below papers when referring to this work:

Sethi, SS, Ewers, RM, Jones, NS, Orme, CDL, Picinali, L. Robust, real‐time and autonomous monitoring of ecosystems with an open, low‐cost, networked device. Methods Ecol Evol. 2018; 9: 2383– 2387. https://doi.org/10.1111/2041-210X.13089 

Sethi, SS, Ewers, RM, Jones, NS, Signorelli, A., Picinali, L, Orme, CDL. SAFE Acoustics: an open-source, real-time eco-acoustic monitoring network in the tropical rainforests of Borneo. biorxiv 968867. https://doi.org/10.1101/2020.02.27.968867

