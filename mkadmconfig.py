# default configuration for mkdocs-admin.py


class Config(object):
    # session key used for site notifications
    SECRET_KEY = 'CHANGEME'

    # host and port to be used when running this script manually
    # when using a webserver this will be the location to proxy to
    HOST = 'localhost'
    PORT = 5000

    # log file to write to, if not specified the log will be written to
    # the path the script is run
    LOGFILE = ''

    # mkdocs paths and configuration is below
    # MKDOCS_BIN    : path the mkdocs binary itself, can be in a virtualenv
    # MKDOCS_DIR    : directory of the mkdocs project written with trailing /
    # MKDOCS_CLEAN  : will not retain html files that do not have a matching
    #                 markdown file in the docs directory if set to True
    MKDOCS_BIN = ''
    MKDOCS_DIR = ''
    MKDOCS_CLEAN = True
