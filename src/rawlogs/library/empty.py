from rawlogs import RawLog


__all__ = ['Empty']


class Empty(RawLog):
    """ 
        An empty rawlog.
    """

    def get_signals(self):
        return {}

    def get_resources(self):
        return []

    def read(self, topics, start=None, stop=None):  # @UnusedVariable
        for x in []:
            yield x
