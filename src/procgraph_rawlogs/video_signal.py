from contracts import contract
import contracts

from compmake.utils.describe import describe_value
import numpy as np
from procgraph.core.model_loader import model_from_string
from procgraph_mplayer.conversions import pg_video_info
from rawlogs import RawLog, RawSignal
from rawlogs_filters.procgraph_filter import ProcgraphFilter


__all__ = ['VideoLog']

class VideoLog(RawLog):
    """ 
        A log that it is in a line-based text format
        Just need to provide the parse function and the datatypes.
        
        The parsing function must provide a (possibly empty) list
        with tuples (timestamp, name, value).
    """

    @contract(filename=str)
    def __init__(self, filename, signal_name, time_reference='default'):
        self.filename = filename
        self.signal_name = signal_name
        
        self.signal = VideoSignal(filename, time_reference=time_reference)
        self.signals = {}
        self.signals[signal_name]= self.signal

    def get_resources(self):
        return [self.filename]

    def get_signals(self):
        return self.signals

    def read(self, topics, start=None, stop=None):
        assert self.signal_name in topics
        for timestamp, frame in iterate_frames(self.filename):
            ok1 = (start is None) or timestamp >= start
            ok2 = (stop is None) or timestamp <= stop
            if ok1 and ok2:
                yield timestamp, (self.signal_name, frame)


def iterate_frames(filename):
    model_desc = """
     config file
     output rgb
           |mplayer file=$file| -> a
           
           a -> |identity| -> |output name=rgb|
    """
    contracts.disable_all()
    model = model_from_string(model_desc, config=dict(file=filename))
    model.init()
    old_ts = None
    while model.has_more():
        model.update()
        timestamp = model.get_output_timestamp('rgb')
        value = model.get_output('rgb')
        if old_ts != timestamp:
            yield timestamp, value
        old_ts = timestamp
# 
# def iterate_frames(filename, start=None, stop=None):
#     model_spec = ['mplayer', dict(file=filename)]
#     empty_spec = ['rawlogs.library.Empty', {}]
#     pf = ProcgraphFilter(rawlog=empty_spec,
#                          model=model_spec,
#                          inputs={},
#                          outputs=dict(rgb='rgb'))
#     for timestamp, (_, value) in pf.read(topics=['rgb'],
#                                          start=start, stop=stop):
#         yield timestamp, value


class VideoSignal(RawSignal):
    
    def __init__(self, filename, time_reference):
        self.filename = filename
        self.time_reference = time_reference
        self.info = None
        
    def get_signal_type(self):
        info = self._get_info()
        w = info['width']
        h = info['height']
        dt = np.dtype(('uint8', (h, w, 3)))
        return dt
       
    def _get_info(self):
        if self.info is None:
            self.info = pg_video_info(self.filename)
        return self.info
            
    def get_time_reference(self):
        return self.time_reference
        
    def get_resources(self):
        return [self.filename]
      
    def get_time_bounds(self):
        info = self._get_info()
        t0 = info['timestamp']
        t1 = info['timestamp'] + info['length']
        return (t0, t1)
