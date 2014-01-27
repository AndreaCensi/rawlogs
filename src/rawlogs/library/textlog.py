import os

from contracts import contract

from rawlogs import RawLog, RawSignal


__all__ = ['RawTextSignal', 'RawTextLog']

class RawTextLog(RawLog):
    """ 
        A log that it is in a line-based text format
        Just need to provide the parse function and the datatypes.
        
        The parsing function must provide a (possibly empty) list
        with tuples (timestamp, name, value).
    """

    @contract(filename=str, dtypes='dict(str:*)', time_reference=str)
    def __init__(self, filename,
                 dtypes, parse_function,
                 time_reference='default'):
        self.dtypes = dtypes
        self.filename = filename
        self.parse_function = parse_function
        self.time_reference = time_reference
        
        self.signals = {}
        for signal_name in self.dtypes:
            signal = RawTextSignal(filename,
                                   parse_function=parse_function,
                                   time_reference=time_reference,
                                   select=[signal_name],
                                   dtype=self.dtypes[signal_name])
            self.signals[signal_name] = signal

    def get_resources(self):
        return [self.filename]

    def get_signals(self):
        return self.signals

    def read(self, topics, start=None, stop=None):

        allofthem = RawTextSignal(self.filename,
                                   parse_function=self.parse_function,
                                   time_reference='unused',
                                   select=topics,
                                   dtype='unused')

        for time, (name, value) in allofthem.read(start, stop):
            assert name in topics
            yield time, (name, value)


class RawTextSignal(RawSignal):

    @contract(filename=str, time_reference=str)
    def __init__(self, filename, parse_function, time_reference, dtype, select):
        self.parse_function = parse_function
        self.time_reference = time_reference
        self.dtype = dtype
        self.select = select

        filename = os.path.expandvars(filename)
        filename = os.path.expanduser(filename)
        self.filename = filename

    def get_signal_type(self):
        return self.dtype

    def get_time_reference(self):
        return self.time_reference

    def get_resources(self):
        return [self.filename]
    
    def get_time_bounds(self):
        """ Returns a tuple of floats representing start and end times for this log. """
        t0, _ = self._get_first_message()
        t1, _ = self._get_last_message()
        return (t0, t1)

    def read(self, start=None, stop=None):
        """ Yields timestamp, value """
        for line in iterate_lines(self._get_stream()):
            res = self._parse(line)
            for timestamp, name, value in res:
                ok1 = (start is None) or timestamp >= start
                ok2 = (stop is None) or timestamp <= stop
                if ok1 and ok2:
                    yield timestamp, (name, value)

    def _get_first_message(self):
        """ Returns timestamp, value for the first message in the file. """
        for line in iterate_lines(self._get_stream()):
            res = self._parse(line)
            if res:
                timestamp, _, value = res[0]
                return timestamp, value

        msg = 'Empty log'
        raise ValueError(msg)

    def _get_last_message(self):
        """ Returns timestamp, value for the last message in the file. """
        for line in iterate_lines_reverse(self._get_stream()):
            res = self._parse(line)
            if res:
                timestamp, _, value = res[-1]
                return timestamp, value
        msg = 'Empty log'
        raise ValueError(msg)

    @contract(returns='list(tuple(float, str, *))')
    def _parse(self, line):
        """ Wraps the user-defined parse function """
        res = self.parse_function(line)
        
        if not isinstance(res, list):
            msg = 'Invalid result.\n-> %r' % (str(res))
            raise ValueError(msg)
        
        r = []
        for (timestamp, signal, value) in res:
            if signal in self.select:
                r.append((timestamp, signal, value))
        return r

    def _get_stream(self):
        # TODO: add .gz
        if self.filename.endswith('bz2'):
            import bz2
            stream = bz2.BZ2File(self.filename)
        else:
            stream = open(self.filename, 'r')
        return stream


def iterate_lines(f):
    for line in f:
        yield line

def iterate_lines_reverse(f):
    for line in reverse_lines(f):
        yield line

def reverse_lines(f):
    "Generate the lines of file in reverse order."
    part = ''
    for block in reversed_blocks(f):
        for c in reversed(block):
            if c == '\n' and part:
                yield part[::-1]
                part = ''
            part += c
    if part:
        yield part[::-1]

def reversed_blocks(f, blocksize=4096):
    "Generate blocks of file's contents in reverse order."
    f.seek(0, os.SEEK_END)
    here = f.tell()
    while 0 < here:
        delta = min(blocksize, here)
        here -= delta
        f.seek(here, os.SEEK_SET)
        yield f.read(delta)


