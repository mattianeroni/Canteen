# This file contains all the events, logs, and exceptions that
# provide a print or a message to the user.
# These logs might be useful for both debugging and statistics.
#
# Designed and developed by Mattia Neroni in March 2021.
# Author contact: mattianeroni@yahoo.it

import collections

# An event logged represents something that happened during the simulation
# that needs to be registered for debugging or statistics.
Event = collections.namedtuple("Event",
                               ("timestamp", "title", "description"),
                               defaults = (0, "Default", None)
                               )
