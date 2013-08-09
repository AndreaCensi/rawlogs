from conf_tools.utils import check_is_in
from contracts import contract
from procgraph.core.registrar import default_library
from rawlogs import RawLog, get_conftools_rawlogs, RawSignal
import warnings


__all__ = ['ProcgraphFilter']


class ProcgraphFilter(RawLog):

    """ Filters a Rawlog with a Procgraph model. """
    
    @contract(rawlog='str|code_spec', model='list[2]', outputs='dict(str:str)', inputs='dict(str:str)')
    def __init__(self, rawlog, model, inputs, outputs):
        _, self.rawlog = get_conftools_rawlogs().instance_smarter(rawlog)
        
        model_name, model_config = model
        if '.' in model_name:
            tokens = model_name.split('.')
            module = '.'.join(tokens[:-1])
            __import__(module)
            model_name = tokens[-1]     
        
        self.model_name = model_name
        self.model_config = model_config
        
        self.inputs = inputs
        self.outputs = outputs
    
    def get_signals(self):
        bounds = [[], []]
        resources = set()
        log_signals = self.rawlog.get_signals()
        timerefs = set()
        for _, signal_name in self.inputs.items():
            check_is_in('signal', signal_name, log_signals)
            s = log_signals[signal_name]
            b = s.get_time_bounds()
            bounds[0].append(b[0])
            bounds[1].append(b[1])
            timerefs.add(s.get_time_reference())
            resources.update(s.get_resources())
        
        bounds = min(bounds[0]), max(bounds[1])
        resources = list(resources)
        
        timeref = '-'.join(sorted(timerefs))
        signals = {}
        for _, signal_name in self.outputs.items():
            warnings.warn('to finish')
            signal_type = '???'  # XXX
            s = ProcgraphFilterSignal(signal_type, timeref, resources, bounds)
            signals[signal_name] = s
        return signals
        
    def get_resources(self):
        return self.rawlog.get_resources() 
        
    def read(self, topics, start=None, stop=None):
        signals = self.get_signals()
        print('signals: %s' % signals)
        have = set(signals.keys())
        required = set(topics)
        
        if not (have & required):
            msg = 'Wrong topics: %s' % topics
            raise ValueError(msg)
         
        print('required: %s' % required)
        print('have: %s' % have)
        print('required-have: %s' % (required - have))
        if (required - have):
            msg = 'Missing topics: %s' % topics
            raise ValueError(msg) 
        
        original2mine = {}
        for x in self.inputs:
            original2mine[self.inputs[x]] = x  
        
        output2mine = {}
        for x in self.outputs:
            if self.outputs[x] in topics:
                output2mine[self.outputs[x]] = x
            else:
                print('not adding %s  %s ' % (x, self.outputs[x]))
            
        print output2mine
        # initialization
        model = default_library.instance(self.model_name, name='filter',
                                         config=self.model_config)

        model.init()
        
        log = self.rawlog.read(self.inputs.values(), start=start, stop=stop)
        
        from collections import defaultdict
        last_timestamps = defaultdict(lambda: None)
        
        for timestamp, (topic, value) in log:
            name = original2mine[topic]
            model.from_outside_set_input(name, value, timestamp)
            
            while model.has_more():
                model.update()
                
            for x, model_signal in output2mine.items(): 
                timestamp = model.get_output_timestamp(model_signal)
                value = model.get_output(model_signal)
                if timestamp != last_timestamps[x]:
                    yield timestamp, (x, value)
                    assert x in topics, (x, topics)
                last_timestamps[x] = timestamp    
        
        self.model.finish()
        
    @contract(returns='list(str)')
    def get_tags(self):
        return self.rawlog.get_tags()
    
    def get_annotations(self):
        return self.rawlog.get_annotations()
    
    
    

class ProcgraphFilterSignal(RawSignal):

    def __init__(self, signal_type, timeref, resources, bounds):
        self.signal_type = signal_type
        self.timeref = timeref
        self.resources = resources
        self.bounds = bounds
            
    def get_signal_type(self):
        return self.signal_type

    def get_time_reference(self):
        return self.timeref
        """ Returns the time reference for this signal. """

    def get_resources(self):
        return self.resources
    
    def get_time_bounds(self):
        return self.bounds
    
