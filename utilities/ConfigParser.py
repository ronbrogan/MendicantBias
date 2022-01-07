from xml.etree import ElementTree
import logging
from datetime import datetime

# Config
class Config:
    # __init__
    def __init__(self):
        # XML tree and root
        self.config_file = None
        self.xml_tree = None
        self.xml_root = None

        # log level
        self.log_level = None

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

    # parse
    def parse(self, config_file):
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

    # setup_logger
    def setup_logger(self):
        now = datetime.now()
        s = now.strftime("%m%d%Y_%H%M%S")
        log_file = "log_%s.txt" % s

        logging.basicConfig(
            format="%(asctime)s  %(levelname)s  %(message)s",
            filename=log_file,
            level=self.log_level)

    # log_config
    def log_config(self):
        logging.info("=============== CONFIG ===============")
        logging.info("Config file: %s" % self.config_file)
        logging.info("streams_source: %s" % self.streams_source)
        logging.info("records_source: %s" % self.records_source)
        logging.info("oldest_source: %s" % self.oldest_source)
        logging.info("notifs_channel: %s" % self.notifs_channel)
        logging.info("records_channel: %s" % self.records_channel)
        logging.info("test_channel: %s" % self.test_channel)
        logging.info("nohr: %s" % self.nohr)
        logging.info("=============== END CONFIG ===============\n")

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
