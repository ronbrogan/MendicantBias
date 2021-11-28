import argparse

from ConfigParser import Config

# Create global instance of our config
CONFIG = Config()

# parse_args
def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-config", type=str, default="./config.xml", help="Path to the configuration xml")

    return parser.parse_args()

# main
def main():
    args = parse_args()

    CONFIG.parse(args.config)

    while True:
        print("")
        command = input("Enter command > ")
        CONFIG.execute_command(command)

    return


if __name__ == "__main__":
    main()
