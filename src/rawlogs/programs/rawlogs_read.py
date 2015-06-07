from types import GeneratorType

from contracts import contract, describe_value, describe_type

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
        params.add_string_list("rawlogs", help="Raw log ID")
        params.add_string_list("signals", help="Signals", default=[])
        params.add_float("start", help="Relative start time", default=None)
        params.add_float("stop", help="Relative stop time", default=None)
        params.add_flag('quiet', help='Do not output current signal')

    def go(self):
        config = get_conftools_rawlogs()
        
        id_rawlogs = config.expand_names(self.options.rawlogs)
        
        for id_rawlog in id_rawlogs:
            rawlog = config.instance(id_rawlog)
        
            signals = self.options.signals
            start = self.options.start
            stop = self.options.stop
            quiet = self.options.quiet
        
            read_log(rawlog,
                     signals=signals, start=start, stop=stop,
                     quiet=quiet)
        
    
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
    
    start = float(start)
    stop = float(stop)

    print('start: %s' % start)
    print('stop:  %s' % stop) 
    
    warned = set()  # already warned that we cannot check

    reading = rawlog.read(signals, start, stop)
    print('Reading from %s ' % reading)

    if not isinstance(reading, GeneratorType):
        msg = 'Expected GeneratorType, got %s' % describe_type(reading)
        raise ValueError(msg)

    for timestamp, (name, value) in reading:
        
        if not (start <= timestamp <= stop + 0.001):
            msg = 'Messages not filtered (%.5f <= %.5f <= %.5f)' % (start, timestamp, stop)
            msg += '\nname: %s' % name
            raise Exception(msg)

        if not quiet:
            if isinstance(value, np.ndarray):
                p = '%15.4f'
                if value.size > 1 and value.ndim == 1:
                    x = ','.join([p % v for v in value])
                else:
                    x = str(value)

            else:
                x = str(value)

            M = 120
            if len(x) > M:
                x = x[:M - 4] + ' ...'
                x = x.replace('\n', ' ')
            print('reading %.5f (%6.4f) %s %s' % (timestamp, timestamp - start, name, x))
        
        res = check_type(name, log_signals[name], value)
        if res == False:
            if not name in warned:
                print('Cannot check dtype for %s' % signal)
                warned.add(name)



@contract(name=str, signal=RawSignal, value='*')
def check_type(name, signal, value):
    """ Returns False if we don't know how to check. """
    dtype = signal.get_signal_type()
    try:
        def bail(msg):
            raise ValueError(msg)
            
        if isinstance(dtype, np.dtype):
            # print 'checking %s for %s' % (dtype, describe_value(value))
            if not isinstance(value, np.ndarray):
                bail('The value is not an array (%s).' % describe_type(value))
            its = np.dtype((value.dtype, value.shape))
            if not its == dtype:
                bail('Datatype does not match (found: %s).' % its)
            return True
        else:
            return False


    except ValueError as e:
        msg = ('%s\n\t   name: %s\n\t signal: %s\n\t   type: %s\n\t  value: %s'
               % (e, name, signal, dtype, describe_value(value)))
        raise ValueError(msg)


