from rawlogs import RawLog, RawSignal, get_conftools_rawlogs


__all__ = ['LogPart', 'LogPartSignal']


class LogPart(RawLog):
    """ Extracts part of a log. """    

    def __init__(self, rawlog, t0, t1, annotations={}):
        _, self.log = get_conftools_rawlogs().instance_smarter(rawlog)
        self.t0 = t0
        self.t1 = t1
        self.annotations = annotations
        
    def get_annotations(self):
        a = self.log.get_annotations()
        a.update(self.annotations)
        return a
        
    def get_signals(self):
        res = {}
        for k, v in self.log.get_signals().items(): 
            res[k] = LogPartSignal(v, self.t0, self.t1)
        return res
        
    def get_resources(self): 
        return self.log.get_resources()
        
    def read(self, topics, start=None, stop=None):
        if start is not None:
            start = max(self.t0, start)
        else:
            start = self.t0
            
        if stop is not None:
            stop = min(self.t1, stop)
        else:
            stop = self.t1
            
        for timestamp, x in self.log.read(topics, start=start, stop=stop):
            if not (start <= timestamp <= stop):
                msg = 'Bug in %r' % self.log
                raise Exception(msg)
            yield timestamp, x
            

 
class LogPartSignal(RawSignal):
    def __init__(self, s, t0, t1):
        self.s = s
        self.t0 = t0
        self.t1 = t1
     
    def get_signal_type(self):
        return self.s.get_signal_type()

    def get_time_reference(self):
        return self.s.get_time_reference()
        
    def get_resources(self):
        return self.s.get_resources()
    
    def get_time_bounds(self):
        a, b = self.s.get_time_bounds()
        a = max(a, self.t0)
        b = min(b, self.t1)
        return a, b 

     
                
