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
        self.commands = dict()

    # parse
    def parse(self, config_file):
        self.config_file = config_file
        self.xml_tree = ElementTree.parse(config_file)
        self.xml_root = self.xml_tree.getroot()

        self.streams_source = self.parse_from_subtree(self.xml_root, "StreamsSource").text.strip()
        self.records_source = self.parse_from_subtree(self.xml_root, "RecordsSource").text.strip()
        self.oldest_source = self.parse_from_subtree(self.xml_root, "OldestSource").text.strip()

        print("StreamsSource:", self.streams_source)
        print("RecordsSource:", self.records_source)
        print("OldestSource:", self.oldest_source)
        print("")

        self.notifs_channel = self.parse_from_subtree(self.xml_root, "NotifsChannelId").text.strip()
        self.records_channel = self.parse_from_subtree(self.xml_root, "RecordsChannelId").text.strip()
        self.test_channel = self.parse_from_subtree(self.xml_root, "TestChannelId").text.strip()

        print("NotifsChannel:", self.notifs_channel)
        print("RecordsChannel:", self.records_channel)
        print("TestChannel:", self.test_channel)
        print("")

        self.parse_commands(self.xml_root)

    # execute_command
    # NOTE: Will likely want some kind of actual command execution class, but this works for now
    def execute_command(self, command):
        if(command not in self.commands.keys()):
            print("ERROR: No such command")
        else:
            print(self.commands[command])

    # parse_from_subtree
    def parse_from_subtree(self, subtree, elem):
        ret = subtree.find(elem)

        # Throw detailed exception if we didn't find it
        if ret is None:
            raise ValueError("Could not find xml child %s from subtree %s" % (elem, subtree))

        return ret

    # parses list of commands
    def parse_commands(self, subtree):
        self.commands = dict()
        command_tree = self.parse_from_subtree(subtree, "Commands")
        for i, command in enumerate(command_tree.findall("command")):
            if("id" not in command.attrib.keys()):
                raise ValueError("Command idx %d does not have an \"id\" attribute" % i)

            id = command.attrib["id"].strip()
            body = command.text.strip()

            self.commands[id] = body
