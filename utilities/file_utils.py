import os

# throw_if_file_unreadable
# Throws an exception if the given file does not exist, or is not readable
def throw_if_file_unreadable(f):
    if(not os.path.isfile(f)):
        raise ValueError("File not found: %s" % f)
    elif(not os.access(f, os.R_OK)):
        raise ValueError("File not readable: %s" % f)

    return
