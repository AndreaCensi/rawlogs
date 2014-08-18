from .generation import for_all_rawlogs
from blocks import check_timed_named
from compmake import progress
from contracts import check_isinstance
from rawlogs import RawLog, RawSignal
from rawlogs.library.logpart import rawlog_bounds


@for_all_rawlogs
def check_rawlog_type(id_rawlog, rawlog): #@UnusedVariable
    assert isinstance(rawlog, RawLog)
    
    signals = rawlog.get_signals()
    check_isinstance(signals, dict)
    for name, s in signals.items():
        check_isinstance(name, str)
        check_isinstance(s, RawSignal)
        
        stype = s.get_signal_type()  # @UnusedVariable
        tref = s.get_time_reference()  # @UnusedVariable
        r = s.get_resources()
        a, b = s.get_time_bounds()  # @UnusedVariable
        x = s.get_length()  # @UnusedVariable

    resources = rawlog.get_resources()
    check_isinstance(resources, list)
    for r in resources:
        check_isinstance(r, str)

    tags = rawlog.get_tags()
    check_isinstance(tags, list)
    for t in tags:
        check_isinstance(t, str)
        
    annotations = rawlog.get_annotations()
    check_isinstance(annotations, dict)
    
    
@for_all_rawlogs
def read_a_bit(id_rawlog, rawlog):
    
    signals = list(rawlog.get_signals())

    t0, t1 = rawlog_bounds(rawlog)
    
    delta = max(5.0, (t1-t0) / 100.0)
        
    t1 = t0 + delta
    print('Reading %.3f of %s.'  % (t1-t0, id_rawlog))
    seq = rawlog.read(topics=signals, start=t0, stop=t1)
    progress('reading', (0, t1-t0))
    count = 0
    for x in seq:
        check_timed_named(x)
        timestamp, (name, value) = x  # @UnusedVariable
        assert name in signals
        if count < 50:
            print('%10s: %10s' % (timestamp, name))
        # TODO: add type check
        
        if timestamp < t0:
            msg = ('Received message %r at %s which is < %s' % 
                   (name, timestamp, t0))
            raise ValueError(msg)
        
        if timestamp > t1:
            msg = ('Received message %r at %s which is outside %s' % 
                   (name, timestamp, t1))
            raise ValueError(msg)
        count += 1
        
        progress('reading', (timestamp-t0, t1-t0))
    progress('reading', (t1-t0,t1-t0))
        
        
        
        
        
    