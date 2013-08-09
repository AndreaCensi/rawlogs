from .logwithannotations import LogWithAnnotations
from contracts import contract
from rawlogs import get_conftools_rawlogs
import heapq

__all__ = ['Multiple']


class Multiple(LogWithAnnotations):    

    @contract(annotations='dict', logs='list(str|code_spec)')
    def __init__(self, logs, annotations={}):
        library = get_conftools_rawlogs()
        self._logs = [library.instance_smarter(l)[1] for l in logs]
        
        logs_annotations = [l.get_annotations() for l in self._logs]
        annotations = _merge_annotations(annotations, logs_annotations)
        LogWithAnnotations.__init__(self, annotations)
    
    def get_signals(self):
        signals = {}
        for log in self._logs:
            log_signals = log.get_signals()
            for k in log_signals:
                if k in signals:
                    msg = 'Signal %r repeated' % k
                    raise ValueError(msg)
            signals.update(log_signals)
        return signals

    def get_resources(self): 
        """ Returns the physical files needed for this log """
        resources = []
        for l in self._logs:
            lres = l.get_resources()
            resources.extend(lres)
        return resources
        
    def read(self, topics, start=None, stop=None):
        found = set()
        iterators = []
        for l in self._logs:
            log_signals = list(set(l.get_signals().keys()) & set(topics))
            found.update(log_signals)
            if log_signals: 
                it = l.read(log_signals, start=start, stop=stop)
                iterators.append(it)
            
        notfound = set(topics) - found
        if notfound:
            msg = ('Could not find signals %s.\nKnown: %s.' % 
                    (notfound, self.get_signals().keys()))
            raise ValueError(msg)

        it = heapq.merge(*tuple(iterators))
        for timestamp, (name, value) in it:
            if (((start is not None) and (start > timestamp)) or 
                ((stop is not None) and (stop < timestamp))):
                raise Exception('Bug: unexpected signal %r %r (start %s stop %s)' % (timestamp, name, start, stop))
            if not name in topics:
                raise Exception('unrequested signal %r not in %r' % (name, topics))
            yield timestamp, (name, value)


@contract(master='dict', others='seq(dict)')
def _merge_annotations(master, others):
    res = master.copy()
    if not 'tags' in res:
        res['tags'] = []
        
    for x in others:
        for k, v in x.items():
            if k == 'tags':
                res['tags'].extend(v)
            else:
                if k in res and not v == res[k]:
                    print('Warning: field %r already exists: %s and %s' % 
                          (k, res, x))
                else:
                    res[k] = v
                    
    res['tags'] = list(set(res['tags']))
    return res        
                
                
                
                
                
                
                
                
            
    
    
    
    
