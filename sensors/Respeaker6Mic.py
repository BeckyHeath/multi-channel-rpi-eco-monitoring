import time
import subprocess
import os
import sensors
import logging
from sensors.SensorBase import SensorBase

class Respeaker6Mic(SensorBase):

    def __init__(self, config=None):

        """
        A class to record audio from a USB Soundcard microphone.

        Args:
            config: A dictionary loaded from a config JSON file used to replace
            the default settings of the sensor.
        """

        # Initialise the sensor config, double checking the types of values. This
        # code uses the variables named and described in the config static to set
        # defaults and override with any passed in the config file.
        opts = self.options()
        opts = {var['name']: var for var in opts}

        self.record_length = sensors.set_option('record_length', config, opts)
        self.compress_data = sensors.set_option('compress_data', config, opts)
        self.capture_delay = sensors.set_option('capture_delay', config, opts)

        # set internal variables and required class variables
        self.working_file = 'currentlyRecording.wav'
        self.current_file = None
        self.working_dir = None
        self.upload_dir = None
        self.pre_upload_dir = '/home/pi/pre_upload_dir'
        self.server_sync_interval = self.record_length + self.capture_delay

    @staticmethod
    def options():
        """
        Static method defining the config options and defaults for the sensor class
        """
        return [{'name': 'record_length',
                 'type': int,
                 'default': 1200,
                 'prompt': 'What is the time in seconds of the audio segments?'},
                {'name': 'compress_data',
                 'type': bool,
                 'default': False,
                 'prompt': 'Should the audio data be compressed from WAV to FLAC Lossless Compression?'},
                {'name': 'capture_delay',
                 'type': int,
                 'default': 0,
                 'prompt': 'How long should the system wait between audio samples?'}
                ]

    def setup(self):

        try:
            # Load alsactl file - increased microphone volume level
            subprocess.call('alsactl --file ./audio_sensor_scripts/asound.state restore', shell=True)
            return True
        except:
            raise EnvironmentError

    def capture_data(self, working_dir, upload_dir, pre_upload_dir):
        """
        Method to capture raw audio data from the USB Soundcard Mic

        Args:
            working_dir: A working directory to use for file processing
            upload_dir: The directory to write the final data file to for upload.
        """

        # populate the working and upload directories
        self.working_dir = working_dir
        self.upload_dir = upload_dir
        self.pre_upload_dir = pre_upload_dir

        # Name files by start time and duration
        start_time = time.strftime('%H-%M-%S')
        self.current_file = '{}_dur={}secs'.format(start_time, self.record_length)

        # Record for a specific duration
        wfile = os.path.join(self.working_dir, self.current_file)
        ofile = os.path.join(self.pre_upload_dir, self.current_file)
        logging.info('\n{} - Started recording at {} \n'.format(self.current_file, start_time))
        try:
            cmd = 'sudo arecord -Dac108 -f S32_LE -r 16000 -c 6 --duration {} {}'
            subprocess.call(cmd.format(self.record_length, wfile), shell=True)
            end_time = time.strftime('%H-%M-%S')
            logging.info('\n{} - Finished recording at {}\n'.format(self.current_file, end_time))
            self.uncomp_file_name = ofile + '.wav'
            os.rename(wfile, self.uncomp_file_name)
            logging.info('\n{} transferred to {}\n'.format(self.current_file, wfile))
        except Exception:
            logging.info('Error recording from audio card. Creating dummy file')
            open(ofile + '_ERROR_audio-record-failed', 'a').close()
            time.sleep(1)

        end_time = time.strftime('%H-%M-%S')
        logging.info('\n{} recording and transfer complete at {}\n'.format(self.current_file, end_time))
        

    def postprocess(self, wfile, upload_dir):
        """
        Method to optionally compress raw audio data to FLAC and stage data to
        upload folder
        """
        
        # Take it to the session working directory
        start_date = time.strftime('%Y-%m-%d')
        s_wfile = os.path.join('/home/pi/pre_upload_dir', start_date, wfile)

        if self.compress_data:

            # Move File to Pre-Upload Directory
            ofilename = wfile.replace(".wav",".flac")
            ofile = os.path.join(upload_dir, start_date, ofilename)
            time_now = time.strftime('%H-%M-%S')
            
            # Audio is compressed using a FLAC Encoding            
            # Removed:  >/dev/null 2>&1
            try: 
                logging.info('\n Starting compression of {} to {} at {}\n'.format(wfile, ofile, time_now))
                cmd = ('ffmpeg -i {} -c:a flac {} >/dev/null 2>&1') 
                subprocess.call(cmd.format(s_wfile, ofile), shell=True)
                os.remove(s_wfile)
                time_now = time.strftime('%H-%M-%S')
                logging.info('\n Finished compression of {} to {} at {}\n'.format(wfile, ofile, time_now))
            except Exception:
                logging.info('Error compressing {}'. format(wfile))
            

        else:
            # Don't compress, store as wav
            logging.info('\n{} - No postprocessing of audio data\n'.format(wfile))
            ofile = os.path.join(upload_dir, wfile) 
            os.rename(s_wfile, ofile)
