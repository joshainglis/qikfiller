from os import mkdir
from os.path import abspath, exists, expanduser, join

config_path = join(abspath(expanduser('~')), '.qikfiller')

if not exists(config_path):
    mkdir(config_path)
