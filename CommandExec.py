# CommandExec
class CommandExec:
    # exec
    def exec(self, config, comm, args):
        if(comm in config.text_commands.keys()):
            print(config.text_commands[comm])
        elif(comm in config.func_commands.keys()):
            self.function_exec(config.func_commands[comm], args)
        else:
            print("Command not recognized!")

    # function_exec
    def function_exec(self, exec_func, args):
        print("EXECUTING FUNCTION: %s WITH ARGS: %s" % (exec_func, args))

        if(exec_func == "calc"):
            self.command_calc(args)
        else:
            print("UNRECOGNIZED EXECUTION FUNCTION:", exec_func)

    # command_calc
    def command_calc(self, args):
        game = args[0]
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
