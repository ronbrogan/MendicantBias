import math
import traceback
import logging
from datetime import datetime

# CommandExec
class CommandExec:
    # exec
    def exec(self, config, comm, args):
        # Text command
        if(comm in config.text_commands.keys()):
            print(config.text_commands[comm])
        # Embed command
        elif(comm in config.embed_commands.keys()):
            print("DISCORD EMBEDDING:")
            print(config.embed_commands[comm])
        # Function command
        elif(comm in config.func_commands.keys()):
            self.function_exec(config, config.func_commands[comm], args)
        # Unrecognized command
        else:
            print("Command not recognized!")
    # end exec

    # function_exec
    def function_exec(self, config, exec_func, args):
        logging.debug("EXECUTING FUNCTION: %s WITH ARGS: %s" % (exec_func, args))

        if(exec_func == "calc"):
            self.command_calc(args)
        elif(exec_func == "points"):
            self.command_points(args)
        elif(exec_func == "nohr"):
            self.command_nohr(config)
        else:
            print("UNRECOGNIZED EXECUTION FUNCTION:", exec_func)
    # end function_exec

    # command_calc
    def command_calc(self, args):
        game = args[0].lower()
        if(game == "reach"):
            print("https://haloruns.com/calc/reach")
        elif(game in ["h1", "hce", "ce"]):
            print("https://haloruns.com/calc/hce")
        elif(game == "h2"):
            print("https://haloruns.com/calc/h2")
        elif(game == "h2a"):
            print("https://haloruns.com/calc/h2a")
        elif(game == "h3"):
            print("https://haloruns.com/calc/h3")
        elif(game == "odst"):
            print("https://haloruns.com/calc/odst")
        elif(game == "h4"):
            print("https://haloruns.com/calc/h4")
        elif(game == "h5"):
            print("https://haloruns.com/calc/h5")
        else:
            print("UNRECOGNIZED GAME:", game)
    # end command_calc

    # command_points
    def command_points(self, args):
        if(len(args) < 3):
            print("Need 3 args to calc points")
            return

        print("Calc points with args:", args[0:3])
        print("")
        print("Use like this: .points [hh:]mm:ss [hh:]mm:ss MaxPoints\n")

        ### Returns a formatted string for the embed used by the .points command

        pb = args[0]
        wr = args[1]
        points = int(args[2])

        pointsStr = ""
        try:
            # print("checking points", pb, wr)
            #replace periods for catching weird input?
            pb = pb.replace('.', ':')
            wr = wr.replace('.', ':')

            pb = self.pad_time(pb)
            wr = self.pad_time(wr)

            pbFormat = self.get_time_format(pb)
            wrFormat = self.get_time_format(wr)

            # print(f"{pb} {pbFormat}")
            # print(f"{wr} {wrFormat}")

            pbTime = datetime.strptime(pb, pbFormat) - datetime.strptime("0", "%S")
            wrTime = datetime.strptime(wr, wrFormat) - datetime.strptime("0", "%S")

            if(wrTime > pbTime):
                pbTime, wrTime = wrTime, pbTime # swap so PB is always larger

            pointsExact = 0.008 * math.exp(4.8284*(wrTime.seconds/pbTime.seconds)) * points

            # print(pointsExact)
            pointsStr = f"Your PB of {pbTime} against {wrTime} is worth {int(pointsExact)} points"
            # print(pointsStr)
        except Exception:
            print("EXCEPTION")
            print("===============================")
            print(traceback.format_exc(), end="")
            print("===============================")
            print("")
            pointsStr = "One of your times is probably not formatted correctly."
        finally:
            print(pointsStr)
    # end command_points

    # command_nohr
    def command_nohr(self, config):
        msg = \
            "Add one of these tags to your stream title to be hidden from the stream list," \
            " when you don't want to be listed, or are doing something non-speedrun related:\n%s" \
            % " ".join(config.nohr)

        print(msg)

    # HELPER FOR command_points
    # pad_time
    def pad_time(self, s):
        ### Pads time strings to fit the format 00:00:00

        out = ""
        x = s.split(':')
        for t in x[:-1]:
            out += t.zfill(2) + ':'
        out += x[-1].zfill(2)
        return out
    # end pad_time

    # HELPER FOR command_points
    # get_time_format
    def get_time_format(self, s):
        ### Formats a time string for strptime
        count = s.count(':')
        if count == 0:
            return "%S"
        if count == 1:
            return "%M:%S"
        if count == 2:
            return "%H:%M:%S"
    # end get_time_format
