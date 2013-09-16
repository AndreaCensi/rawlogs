import itertools

from contracts import contract
from rawlogs import get_conftools_rawlogs

from .logwithannotations import LogWithAnnotations
from .multiple import _merge_annotations
from decent_logs import WithInternalLog


__all__ = ['LogSequence']


class LogSequence(LogWithAnnotations, WithInternalLog):    
    """ A set of logs in sequence """
    
    @contract(annotations='dict', logs='list(str|code_spec)')
    def __init__(self, logs, annotations={}):
        library = get_conftools_rawlogs()
        self._logs = [library.instance_smarter(l)[1] for l in logs]
        
        logs_annotations = [l.get_annotations() for l in self._logs]
        annotations = _merge_annotations(annotations, logs_annotations)
        LogWithAnnotations.__init__(self, annotations)
    
    def get_signals(self):
        signals0 = self._logs[0].get_signals()
        
        for log in self._logs[1:]:
            signals = log.get_signals()
            # We cannot introduce new signals
            if not (set(signals) <= set(signals0)):
                msg = ('Inconsistent signals:\n- first %s\n- another %s' % 
                       (set(signals0), set(signals)))
                raise ValueError(msg)
            
            if not set(signals) == set(signals0):
                self.warn('log does not have all signals:\n- %s\n- %s' % 
                           (set(signals0), set(signals)))
            
        return signals0

    def get_resources(self): 
        """ Returns the physical files needed for this log """
        resources = []
        for l in self._logs:
            lres = l.get_resources()
            resources.extend(lres)
        return resources
        
    def read(self, topics, start=None, stop=None):
        iterators = []
        for l in self._logs:
            signals = l.get_signals()
            l_topics = set(topics) & set(signals)
            it = l.read(l_topics, start=start, stop=stop)
            iterators.append(it)
            
        it = itertools.chain(*tuple(iterators))
        # TODO: unify with code in Multiple
        for timestamp, (name, value) in it:
            if (((start is not None) and (start > timestamp)) or 
                ((stop is not None) and (stop < timestamp))):
                raise Exception('Bug: unexpected signal %r %r (start %s stop %s)' % (timestamp, name, start, stop))
            if not name in topics:
                raise Exception('unrequested signal %r not in %r' % (name, topics))
            yield timestamp, (name, value)




                
                
                
                
                
                
                
                
            
    
    
    
    
