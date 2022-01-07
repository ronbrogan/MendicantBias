import argparse

from utilities.ConfigParser import Config
from utilities.CommandExec import CommandExec

# Create global instances
CONFIG = Config()
COMMAND_EXEC = CommandExec()

# parse_args
def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-config", type=str, default="./config.xml", help="Path to the configuration xml")
    parser.add_argument("-token", type=str, default="./TOKEN.txt", help="Discord verification token")

    return parser.parse_args()

# main
def main():
    args = parse_args()

    CONFIG.parse_config(args.config)
    CONFIG.parse_token(args.token)
    CONFIG.setup_logging()

    main_logger = CONFIG.create_log("main")
    CONFIG.log_config(main_logger)

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

        COMMAND_EXEC.exec(CONFIG, main_logger, command, args)

    return


if __name__ == "__main__":
    main()
