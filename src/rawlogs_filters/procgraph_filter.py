import warnings

from contracts import contract

from conf_tools.utils import check_is_in
from decent_logs import WithInternalLog
from procgraph.core.model import Model
from procgraph.core.registrar import default_library
from rawlogs import RawLog, get_conftools_rawlogs, RawSignal


__all__ = ['ProcgraphFilter']


class ProcgraphFilter(RawLog, WithInternalLog):

    """ 
        Filters a Rawlog with a Procgraph model. 
    
        model: [name, dict(config1=...)]
        
        inputs: 
            <log signal>: <model signal>
        outputs: 
            <model output signal>: <new signal>
      
      
        - id: "rsf-${dir}"
          desc: "Filtered rawseeds dataset ${dir}"
          code: 
          - rawlogs_filters.ProcgraphFilter
          - rawlog: "rs-${dir}"
            model: [procgraph_robotics.se2_from_SE2_seq, {}]
            inputs: 
              pose_SE2: 0
            outputs:
              0: velocity        
    
    """
    
    @contract(rawlog='str|code_spec', model='list[2]',
              inputs='dict(str:(str|int))',
              outputs='None|dict((str|int):str)')
    def __init__(self, rawlog, model, inputs, outputs=None):
        _, self.rawlog = get_conftools_rawlogs().instance_smarter(rawlog)
        
        self.model_module, self.model_name, self.model_config = self._interpret_name(model)
        # XXX I switched the meanings
        self.inputs = inputs
        self.outputs = outputs
    
    def _interpret_name(self, spec):
        model_name, model_config = spec
        if '.' in model_name:
            tokens = model_name.split('.')
            module = '.'.join(tokens[:-1])
            __import__(module)
            model_name = tokens[-1]
        else:
            module = None
        return module, model_name, model_config

    def get_signals(self):
        bounds = [[], []]
        resources = set()
        log_signals = self.rawlog.get_signals()
        timerefs = set()

        for signal_name, _ in self.inputs.items():
            check_is_in('signal', signal_name, log_signals)
            s = log_signals[signal_name]
            b = s.get_time_bounds()
            bounds[0].append(b[0])
            bounds[1].append(b[1])
            timerefs.add(s.get_time_reference())
            resources.update(s.get_resources())
        
        if bounds[0]:  # i.e. we had at least one signal
            bounds = min(bounds[0]), max(bounds[1])
            resources = list(resources)

        timeref = '-'.join(sorted(timerefs))
        signals = {}
        if self.outputs is None:
            raise Exception('TODO: assing names automatically')
        for model_output, signal_name in self.outputs.items():
            warnings.warn('to finish')
            model_output_dtypes = self._get_model_output_dtypes()
            signal_type = model_output_dtypes[model_output]
            s = ProcgraphFilterSignal(signal_type, timeref, resources, bounds)
            signals[signal_name] = s

        # also add other signals
        signals.update(log_signals)

        return signals

    @contract(returns='dict(str:*)')
    def _get_model_output_dtypes(self):
        """ Returns the declared datatypes for the outputs of the model. """
        generator = default_library.get_generator_for_block_type(self.model_name)
        res = {}
        for out in generator.output:
            res[out.name] = out.dtype
        return res

    def get_resources(self):
        return self.rawlog.get_resources() 
        
    def read(self, topics, start=None, stop=None):
        # xxx: don't filter if not requested?
        # TODO: if all signals are in topics, we don't need ours.

        signals = self.get_signals()
        self.info('signals: %s' % signals)
        have = set(signals.keys())
        required = set(topics)
        
        if not (have & required):
            msg = 'Wrong topics: %s' % topics
            raise ValueError(msg)
         
        self.debug('required: %s' % required)
        self.debug('have: %s' % have)
        self.debug('required-have: %s' % (required - have))
        if (required - have):
            msg = 'Missing topics: %s' % topics
            raise ValueError(msg)

        
        model = default_library.instance(self.model_name, name='filter',
                                         config=self.model_config)
        
        if not isinstance(model, Model):
            msg = 'This is a Block, not a Model: %s/ %s' % (model, type(model))

            warnings.warn('Should I put this automatically in instance()?')
            generator = model.generator
            model.define_input_signals_new([x.name for x in generator.input])
            model.define_output_signals_new([x.name for x in generator.output])


        model.init()

        # print('Model inputs: %s' % model.get_input_signals_names())
        # print('Model outputs: %s' % model.get_output_signals_names())
        for model_out_signal, _ in self.outputs.items():
            if not model.is_valid_output_name(model_out_signal):
                msg = ('Not a valid output name %r (%r).' % 
                       (model_out_signal, model.get_output_signals_names()))
                raise ValueError(msg)
            
        for _, model_in_signal in self.inputs.items():
            if not model.is_valid_input_name(model_in_signal):
                msg = ('Not a valid input name %r (%r).' %
                       (model_in_signal, model.get_input_signals_names()))
                raise ValueError(msg)
            

        require = list(set(self.inputs.keys()) | set(topics) - set(self.outputs.values()))


        # print('Required to me: %s' % topics)
        # print('Required by me to original: %s' % require)

        log = self.rawlog.read(require, start=start, stop=stop)
        
        from collections import defaultdict
        last_timestamps = defaultdict(lambda: None)

        for timestamp, (topic, value) in log:
            # self.debug('pushing %s %s' % (timestamp, topic))
            if topic in self.inputs:

                name = self.inputs[topic]
                model.from_outside_set_input(name, value, timestamp)

                while True:
                    if isinstance(model, Model):
                        if not model.has_more():
                            break

                    model.update()

                    for model_signal, output_signal in self.outputs.items():
                        timestamp = model.get_output_timestamp(model_signal)
                        value = model.get_output(model_signal)
                        # self.debug('seeing %s %s' % (timestamp, x))
                        if timestamp != last_timestamps[output_signal]:
                            yield timestamp, (output_signal, value)
                            # self.debug('yielding %s %s' % (timestamp, x))
                            warnings.warn('Should only output events that were required')
                            assert output_signal in topics, (output_signal, topics)
                        last_timestamps[output_signal] = timestamp

                    if not isinstance(model, Model):
                        break
            else:
                if topic in topics:
                    yield timestamp, (topic, value)

#         pipe()

        model.finish()
        
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
    
