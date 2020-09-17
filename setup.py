#!/usr/bin/python
import json
import os
import sys
import sensors
import inspect


def config_parse(opt, cnfg):
    """
    Method to parse a config option (dictionary with name, prompt, type, optional default,
    optional list of valid values), validate and append the choice to an existing
    config dictionary.

    Parameters:
        opt: A config option dictionary.
        cnfg: The config dictionary to extend.
    """

    if 'default' in opt.keys():
        opt['dft_str'] = '\nPress return to accept default value [{}]'.format(opt['default'])
    else:
        opt['dft_str'] = ""

    if 'valid' in opt.keys():
        opt['vld_str'] = ', valid options: '
        vld_opts = ', '.join([str(vl) for vl in opt['valid']])
        opt['vld_str'] += vld_opts
    else:
        opt['vld_str'] = ""

    valid_choice = False
    target_type = opt['type']

    print('{prompt} [{name}{vld_str}]{dft_str}'.format(**opt))

    while not valid_choice:
        value = raw_input()
        try:
            # check for input and handle defaults
            if value == '' and 'default' in opt.keys():
                value = opt['default']
                valid_choice = True
            elif value == '' and 'default' not in opt.keys():
                print('No value entered and no default value is set')
                continue

            # need to be a little careful here in parsing raw inputs because
            # bool() convert anything but an empty string to True, so handle
            # those differently
            if target_type.__name__ == 'bool' and not isinstance(value, bool):
                if value.lower() in ['t', 'true']:
                    value = True
                    valid_choice = True
                elif value.lower() in ['f', 'false']:
                    value = False
                    valid_choice = True
                else:
                    print('Value not recognized as true or false')
                    continue
            else:
                try:
                    value = target_type(value)
                except ValueError:
                    print('Value "{}" cannot be converted to type {}'.format(value, target_type.__name__))
                    continue

            # check if entries appear in the list of valid options, if there is one
            if 'valid' in opt.keys() and value not in opt['valid']:
                print('Value not in {}'.format(vld_opts))
            else:
                valid_choice = True
                cnfg[opt['name']] = value
        except ValueError, AttributeError:
            print('Unable to validate entered value. Please try again.')


# Don't try and merge existing configs - could be a clash of option names
# in different sensor types which might be problematic. Replace entirely or leave alone.

config_file = 'config.json'
if os.path.exists(config_file):
    replace = {}
    config_parse({'prompt': 'Config file already exists. Replace?',
                  'default': 'n',
                  'type': str,
                  'name': 'replace',
                  'valid': ['y', 'n']}, replace)
    if replace['replace'] == 'n':
        sys.exit()
    else:
        os.remove(config_file)

# Get the config options for the sensors by loading the available sensor classes from
# the sensors module, ignoring the base class.
# The sensor_classes variable is list of tuples: (name, class_reference)
sensor_classes = inspect.getmembers(sensors, inspect.isclass)
sensor_classes = [sc for sc in sensor_classes if sc[0] != 'SensorBase']
sensor_numbers = [idx + 1 for idx in range(len(sensor_classes))]
sensor_options = {nm: tp for nm, tp in zip(sensor_numbers, sensor_classes)}
sensor_menu = [" " + str(ky) + ": " + tp[0] for ky, tp in sensor_options.iteritems()]

sensor_prompt = ('Hello! Follow these instructions to perform a one-off set up of your '
                 'ecosystem monitoring unit\nFirst lets do the sensor setup. Select one '
                 'of the following available sensor types:\n')
sensor_prompt += '\n'.join(sensor_menu) + '\n'

# select a sensor and then call the config method of the selected class to
# get the config options
sensor_config = {}
config_parse({'prompt': sensor_prompt,
              'valid': sensor_numbers,
              'type': int,
              'name': 'sensor_index'}, sensor_config)

# convert index to name by looking up the index in the dictionary
sensor_config['sensor_type'] = sensor_options[sensor_config['sensor_index']][0]
# and also call the options method
sensor_config_options = sensor_options[sensor_config['sensor_index']][1].options()

# populate the sensor config dictionary
for option in sensor_config_options:
    config_parse(option, sensor_config)

# test for offline mode
offline_options = [{'name': 'offline_mode',
                    'type': int,
                    'prompt': 'Should the recorder run in offline mode (1) or use 3G to upload data to an FTP server?',
                    'default': 0,
                    'valid': [0, 1]}]

offline_config = {}

# populate the offline config dictionary
for option in offline_options:
    config_parse(option, offline_config)

# Populate the FTP config unless the user has chosen offline mode

ftp_config = {}

if not offline_config['offline_mode']:

    ftp_config_options = [
                  {'name': 'uname',
                   'type': str,
                   'prompt': 'Enter FTP server username'},
                  {'name': 'pword',
                   'type': str,
                   'prompt': 'Enter FTP server password'},
                  {'name': 'host',
                   'type': str,
                   'prompt': 'Enter FTP server hostname'},
                  {'name': 'use_ftps',
                   'type': int,
                   'prompt': 'Use FTPS (1) or FTP (0)?',
                   'default': 1,
                   'valid': [0, 1]}]

    print("\nNow let's do the FTP server details...")

    # populate the ftp config dictionary
    for option in ftp_config_options:
        config_parse(option, ftp_config)

# Popualte the system config options
sys_config_options = [
              {'name': 'working_dir',
               'type': str,
               'prompt': 'Enter the working directory path',
               'default': '/home/pi/tmp_dir'},
              {'name': 'upload_dir',
               'type': str,
               'prompt': 'Enter the upload directory path',
               'default': '/home/pi/multi_channel_monitoring_data'},
              {'name': 'reboot_time',
               'type': str,
               'prompt': 'Enter the time for the daily reboot',
               'default': '02:00'}]

print("\nNow let's do the system details...")
sys_config = {}

# populate the sensor config dictionary
for option in sys_config_options:
    config_parse(option, sys_config)

config = {'ftp': ftp_config, 'offline_mode': offline_config['offline_mode'],
          'sensor': sensor_config, 'sys': sys_config}

# save the config
with open(config_file, 'w') as fp:
    json.dump(config, fp, indent=4)

print('\nAll done!')
