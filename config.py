#!/usr/bin/env python3

import configparser
import sys

_config_parser = configparser.ConfigParser()
_config_parser.optionxform = str
_config_parser.read(sys.argv[1])
#name = config.get(str(sys.argv[1]))
moss_files = _config_parser['DEFAULT']['MOSS_FILES']
print(moss_files.split(','))

with open("MOSS_FILES/ASS"+sys.argv[2]+".moss") as f:
    file_content = f.read()
    _config_parser['DEFAULT']['MOSS_FILES'] = file_content
    with open("config.ini.new", "w+") as fp:
        _config_parser.write(fp)
