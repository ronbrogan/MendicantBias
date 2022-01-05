import argparse
import logging

from ConfigParser import Config
from CommandExec import CommandExec

# Create global instances
CONFIG = Config()
COMMAND_EXEC = CommandExec()

# parse_args
def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-config", type=str, default="./config.xml", help="Path to the configuration xml")

    return parser.parse_args()

# main
def main():
    args = parse_args()

    CONFIG.parse(args.config)
    CONFIG.setup_logger()
    CONFIG.log_config()

    print("Testing ground for command (type 'exit' to exit)")
    while True:
        print("")
        full_command = input("Enter command > ")

        if(full_command.strip() == "exit"):
            break

        full_command_split = full_command.split()

        # Command portion
        command = full_command_split[0]
        args = full_command_split[1:]

        COMMAND_EXEC.exec(CONFIG, command, args)

    return


if __name__ == "__main__":
    main()
