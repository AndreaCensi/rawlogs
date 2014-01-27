from rawlogs import RawLog, RawSignal, get_conftools_rawlogs, logger
from contracts import contract


__all__ = ['LogPart', 'LogPartSignal']


class LogPart(RawLog):
    """ Extracts part of a log. """    

    @contract(t0='number,x', t1='number,>=x', relative='bool', annotations='dict(str:*)')
    def __init__(self, rawlog, t0, t1, relative=False, annotations={}):
        _, self.log = get_conftools_rawlogs().instance_smarter(rawlog)
        self.t0 = float(t0)
        self.t1 = float(t1)
        self.annotations = annotations
        self.relative = relative
        
    def get_annotations(self):
        a = self.log.get_annotations()
        a.update(self.annotations)
        return a
        
    def get_signals(self):
        res = {}
        for k, v in self.log.get_signals().items(): 
            res[k] = LogPartSignal(v, self.t0, self.t1, self.relative)
        return res
        
    def get_resources(self): 
        return self.log.get_resources()

    def read(self, topics, start=None, stop=None):
        before = [start, stop]
        start, stop = self._get_real_bounds(start, stop)
        after = [start, stop]
        logger.info('reading part (%s => %s)' % (before, after))
        for timestamp, x in self.log.read(topics, start=start, stop=stop):
            if not (start <= timestamp <= stop):
                msg = 'Bug in %r' % self.log
                raise Exception(msg)
            yield timestamp, x

    def _get_real_bounds(self, start, stop):
        if self.relative is False:
            if start is not None:
                start = max(self.t0, start)
            else:
                start = self.t0
                
            if stop is not None:
                stop = min(self.t1, stop)
            else:
                stop = self.t1
            return start, stop
        else:
            A, B = self._get_log_bounds()
            a = min(A + self.t0, B)
            b = min(A + self.t1, B)
            return a, b
            
    @contract(returns='tuple(float,float)')
    def _get_log_bounds(self):
        """ Returns the minimum/maximum of the signals of the original logs. """
        starts = []
        stops = []
        for s in self.log.get_signals().values():
            a, b = s.get_time_bounds()
            starts.append(a)
            stops.append(b)
        return min(starts), max(stops)
        
            
 
class LogPartSignal(RawSignal):
    def __init__(self, s, t0, t1, relative):
        self.s = s
        self.t0 = t0
        self.t1 = t1
        self.relative = relative
     
    def get_signal_type(self):
        return self.s.get_signal_type()

    def get_time_reference(self):
        return self.s.get_time_reference()
        
    def get_resources(self):
        return self.s.get_resources()
    
    def get_time_bounds(self):
        a, b = self.s.get_time_bounds()
        if self.relative:
            a = min(a + self.t0, self.t1)
            b = min(a + self.t1, self.t1)
        else:
            a = max(a, self.t0)
            b = min(b, self.t1)
        return a, b 

     
                
