
import collections

# An event logged represents something that happened during the simulation
# that needs to be registered for debugging or statistics.
Event = collections.namedtuple("Event",
                               ("timestamp", "title", "description"),
                               defaults = (0, "Default", None)
                               )
