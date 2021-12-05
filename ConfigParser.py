from xml.etree import ElementTree

# Config
class Config:
    # __init__
    def __init__(self):
        # XML tree and root
        self.config_file = None
        self.xml_tree = None
        self.xml_root = None

        # paramters parsed from configuration
        self.streams_source = None
        self.records_source = None
        self.oldest_source = None

        # discord channel ids
        self.notifs_channel = None
        self.records_channel = None
        self.test_channel = None

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

        self.parse_commands(self.xml_root)
    # end parse

    # parse_from_subtree
    def parse_from_subtree(self, subtree, elem):
        ret = subtree.find(elem)

        # Throw detailed exception if we didn't find it
        if ret is None:
            raise ValueError("Could not find xml child %s from subtree %s" % (elem, subtree))

        return ret
    # end parse_from_subtree

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
