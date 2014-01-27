from .main import RawlogsMainCmd
from conf_tools.utils import check_is_in
from quickapp import QuickAppBase
from rawlogs import get_conftools_rawlogs


__all___ = ['RawLogsRead']


class RawLogsRead(RawlogsMainCmd, QuickAppBase):
    """ Tries to read a log """
    
    cmd = 'read'
    
    def define_program_options(self, params):
        params.add_string("rawlog", help="Raw log ID")
        params.add_string_list("signals", help="Signals", default=[])
        params.add_float("start", help="Relative start time", default=None)
        params.add_float("stop", help="Relative stop time", default=None)

    def go(self):
        id_rawlog = self.options.rawlog
        rawlog = get_conftools_rawlogs().instance(id_rawlog)
        
        signals = self.options.signals
        start = self.options.start
        stop = self.options.stop
        read_log(rawlog, signals=signals, start=start, stop=stop)
        
    
def read_log(rawlog, signals=None, start=None, stop=None):
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
         
        print('reading %.5f (%6.4f) %s' % (timestamp, timestamp - start, name))
        
