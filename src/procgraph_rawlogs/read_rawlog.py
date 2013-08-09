from procgraph import Block
from procgraph.block_utils import IteratorGenerator
from rawlogs import get_conftools_rawlogs
from procgraph import BadConfig
from conf_tools import GlobalConfig
    
__all__ = ['RawlogRead']


class RawlogRead(IteratorGenerator):
    '''
        Reads any rawlog.
    '''
    Block.alias('read_rawlog')
    Block.output_is_defined_at_runtime('The signals read from the log.')
    
    Block.config('rawlog', 'Rawlog ID or code spec')
    Block.config('config_dirs', 'Additional config dirs', default='') 
    
    Block.config('signals', 'Which signals to output (and in what order). '
                 'Should be a comma-separated list. If you do not specify it '
                 ' will be all signals (TODO: in the original order).',
                 default=None)

    def get_output_signals(self):
        dirnames = self.config.config_dirs.split(':')
        for d in dirnames:
            if d:
                GlobalConfig.global_load_dir(d)
        
        rawlog = self.config.rawlog
        
        id_rawlog, self.rawlog = get_conftools_rawlogs().instance_smarter(rawlog)
        all_signals = self.rawlog.get_signals()
        
        if self.config.signals is None:
            self.signals = list(all_signals.keys())
        else:
            signal_list = filter(lambda x: x, self.config.signals.split(','))
            if not signal_list:
                msg = 'Bad format: %r.' % self.config.signals
                raise BadConfig(msg, self, 'signals')
            
            self.signals = []
            for s in signal_list:
                if not s in all_signals:
                    msg = ('Signal %r not present in log %r (available: %r)' % 
                            (s, id_rawlog, all_signals.keys()))
                    raise BadConfig(msg, self, 'signals')
                self.signals.append(s)

        return self.signals

    def init_iterator(self):
        """ Must return an iterator yielding signal, timestamp, value """
        for timestamp, (name, value) in self.rawlog.read(self.signals):
            yield name, timestamp, value
        

