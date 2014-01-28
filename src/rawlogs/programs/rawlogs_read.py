from contracts import contract, describe_value

from conf_tools.utils import check_is_in
import numpy as np
from quickapp import QuickAppBase
from rawlogs import RawSignal, get_conftools_rawlogs

from .main import RawlogsMainCmd


__all___ = ['RawLogsRead']


class RawLogsRead(RawlogsMainCmd, QuickAppBase):
    """ Tries to read a log """
    
    cmd = 'read'
    
    def define_program_options(self, params):
        params.add_string("rawlog", help="Raw log ID")
        params.add_string_list("signals", help="Signals", default=[])
        params.add_float("start", help="Relative start time", default=None)
        params.add_float("stop", help="Relative stop time", default=None)
        params.add_flag('quiet', help='Do not output current signal')

    def go(self):
        id_rawlog = self.options.rawlog
        rawlog = get_conftools_rawlogs().instance(id_rawlog)
        
        signals = self.options.signals
        start = self.options.start
        stop = self.options.stop
        read_log(rawlog, signals=signals, start=start, stop=stop,
                 quiet=self.options.quiet)
        
    
def read_log(rawlog, signals=None, start=None, stop=None, quiet=False):
    log_signals = rawlog.get_signals()
   
    if not signals:
        signals = list(log_signals.keys())
    else:
        for x in signals:
            check_is_in('signal', x, log_signals)

    # sync to first signal
    signal = log_signals[signals[0]]
    bounds = signal.get_time_bounds()
    
    if start is not None:
        start = bounds[0] + start
    else:
        start = bounds[0]
        
    if stop is not None:
        stop = bounds[0] + stop
    else:
        stop = bounds[1]
    
    print('start: %s' % start)
    print('stop:  %s' % stop) 
    
    for timestamp, (name, value) in rawlog.read(signals, start, stop):  # @UnusedVariable
        
        if not (start <= timestamp <= stop + 0.001):
            msg = 'Messages not filtered (%.5f <= %.5f <= %.5f)' % (start, timestamp, stop)
            msg += '\nname: %s' % name
            raise Exception(msg)

        if not quiet:
            print('reading %.5f (%6.4f) %s' % (timestamp, timestamp - start, name))
        
        check_type(name, log_signals[name], value)

@contract(name=str, signal=RawSignal, value='*')
def check_type(name, signal, value):
    dtype = signal.get_signal_type()
    try:
        def bail(msg):
            raise ValueError(msg)
            
        if isinstance(dtype, np.dtype):
            # print 'checking %s for %s' % (dtype, describe_value(value))

            if not isinstance(value, np.ndarray):
                bail('The value is not an array.')
            its = np.dtype((value.dtype, value.shape))
            if not its == dtype:
                bail('Datatype does not match (found: %s).' % its)
        else:
            print('Cannot check dtype for %s' % signal)


    except ValueError as e:
        msg = ('%s\n\t   name: %s\n\t signal: %s\n\t   type: %s\n\t  value: %s'
               % (e, name, signal, dtype, describe_value(value)))
        raise ValueError(msg)


