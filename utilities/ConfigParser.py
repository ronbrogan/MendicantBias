from xml.etree import ElementTree
import logging
from datetime import datetime
import os

from .file_utils import throw_if_file_unreadable

LOG_FORMATTER = logging.Formatter("%(asctime)s  %(levelname)s  %(message)s")

# Config
class Config:
    # __init__
    def __init__(self):
        # XML tree and root
        self.config_file = None
        self.xml_tree = None
        self.xml_root = None

        # Token file and parsed token
        self.token_file = None
        self.token = None

        # log level and directory
        self.log_level = None
        self.log_dir = None

        # paramters parsed from configuration
        self.streams_source = None
        self.records_source = None
        self.oldest_source = None

        # discord channel ids
        self.notifs_channel = None
        self.records_channel = None
        self.test_channel = None

        # default streams channel text
        self.info_text = None
        self.no_streams_text = None
        self.currently_live_text = None

        # List of nohr terms
        self.nohr = None

        # dictionary of commands
        # Text commands write simple text
        # Embed commands embed the given text (discord embedding)
        # Function commands execute the specified function in the command executor
        self.text_commands = dict()
        self.embed_commands = dict()
        self.func_commands = dict()
    # end __init__

    # parse_config
    def parse_config(self, config_file):
        throw_if_file_unreadable(config_file)

        self.config_file = config_file
        self.xml_tree = ElementTree.parse(config_file)
        self.xml_root = self.xml_tree.getroot()

        self.streams_source = self.parse_from_subtree(self.xml_root, "StreamsSource").text.strip()
        self.records_source = self.parse_from_subtree(self.xml_root, "RecordsSource").text.strip()
        self.oldest_source = self.parse_from_subtree(self.xml_root, "OldestSource").text.strip()

        self.notifs_channel = self.parse_from_subtree(self.xml_root, "NotifsChannelId").text.strip()
        self.records_channel = self.parse_from_subtree(self.xml_root, "RecordsChannelId").text.strip()
        self.test_channel = self.parse_from_subtree(self.xml_root, "TestChannelId").text.strip()

        self.info_text = self.parse_from_subtree(self.xml_root, "InfoText").text.strip()
        self.no_streams_text = self.parse_from_subtree(self.xml_root, "NoStreamsText").text.strip()
        self.currently_live_text = self.parse_from_subtree(self.xml_root, "CurrentlyLiveText").text.strip()

        # nohr is a comma-separated list
        self.nohr = self.parse_from_subtree(self.xml_root, "NoHr").text.strip().split(",")

        self.parse_log_level(self.xml_root)
        self.parse_commands(self.xml_root)
    # end parse

    # parse_token
    def parse_token(self, token_file):
        throw_if_file_unreadable(token_file)

        with open(token_file, "r") as i_stream:
            lines = i_stream.readlines()

        # Check for error
        if(len(lines) != 1):
            raise ValueError( \
                "Token file must contain a single line containing the token: %s", token_file)

        self.token_file = token_file
        self.token = lines[0].strip()

    # setup_logging
    # creates and manages time-stamped directory where all log files are written
    # should only be called once
    def setup_logging(self):
        cur_datetime = datetime.now().strftime("%m%d%Y_%H%M%S")
        self.log_dir = "logs_%s" % cur_datetime

        os.mkdir(self.log_dir)

    # create_log
    # Creates a new log file with the given name. Returns logging object that will log to this file
    def create_log(self, log_name):
        full_log_path = os.path.join(self.log_dir, "%s.log" % log_name)

        handler = logging.FileHandler(full_log_path)
        handler.setFormatter(LOG_FORMATTER)

        logger = logging.getLogger(log_name)
        logger.setLevel(self.log_level)
        logger.addHandler(handler)

        return logger

    # log_config
    def log_config(self, logger):
        # NOTE: For security reasons, we will not log the auth token
        logger.info("=============== CONFIG ===============")
        logger.info("Config file: %s" % self.config_file)
        logger.info("Token file: %s" % self.token_file)
        logger.info("streams_source: %s" % self.streams_source)
        logger.info("records_source: %s" % self.records_source)
        logger.info("oldest_source: %s" % self.oldest_source)
        logger.info("notifs_channel: %s" % self.notifs_channel)
        logger.info("records_channel: %s" % self.records_channel)
        logger.info("test_channel: %s" % self.test_channel)
        logger.info("nohr: %s" % self.nohr)
        logger.info("=============== END CONFIG ===============\n")

    # parse_from_subtree
    def parse_from_subtree(self, subtree, elem):
        ret = subtree.find(elem)

        # Throw detailed exception if we didn't find it
        if ret is None:
            raise ValueError("Could not find xml child %s from subtree %s" % (elem, subtree))

        return ret
    # end parse_from_subtree

    # parse_log_level
    def parse_log_level(self, subtree):
        log_level_text = self.parse_from_subtree(self.xml_root, "LogLevel").text.strip()
        if(log_level_text == "debug"):
            self.log_level = logging.DEBUG
        elif(log_level_text == "info"):
            self.log_level = logging.INFO
        elif(log_level_text == "warn"):
            self.log_level = logging.WARNING
        elif(log_level_text == "error"):
            self.log_level = logging.ERROR
        elif(log_level_text == "critical"):
            self.log_level = logging.CRITICAL
        else:
            raise ValueError("Unrecognized log level:", log_level_text)

    # parses list of commands
    def parse_commands(self, subtree):
        self.text_commands = dict()
        self.embed_commands = dict()
        self.func_commands = dict()

        command_tree = self.parse_from_subtree(subtree, "Commands")
        for i, command in enumerate(command_tree.findall("command")):
            if("id" not in command.attrib.keys()):
                raise ValueError("Command idx %d does not have an \"id\" attribute" % i)

            # If given an 'exec' child, this is a function command, else this must be a text command
            # Throws exception if there is a child that is not one of our allowed nodes or
            # we have more than one child

            # Get command identified (parsed from discord messages)
            id = command.attrib["id"].strip()

            # Number of child nodes (should be 0 or 1)
            num_children = len(command)

            # Text command
            if(num_children == 0):
                self.text_commands[id] = command.text.strip()
            # Special command
            elif(len(command) == 1):
                # valid tags
                embed = command.find("embed")
                exec = command.find("exec")

                # Add tags to their appropriate containers
                if(embed is not None):
                    self.embed_commands[id] = embed.text.strip()
                elif(exec is not None):
                    self.func_commands[id] = exec.text.strip()
                else:
                    raise ValueError("Error at command id=%s: Child node is not a valid tag" % (id,))

            # Error, too many children
            else:
                raise ValueError( \
                    "Error at command id=%s: Too many child nodes. Should either be none, or 1 " \
                     % (id,))
    # end parse_commands
