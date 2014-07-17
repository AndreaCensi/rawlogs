from .generation import for_all_rawlogs
from rawlogs import RawLog
from contracts.utils import check_isinstance
from rawlogs import RawSignal
from blocks.library.timed.checks import check_timed_named

@for_all_rawlogs
def check_rawlog_type(id_rawlog, rawlog): #@UnusedVariable
    assert isinstance(rawlog, RawLog)
    
    signals = rawlog.get_signals()
    check_isinstance(signals, list)
    for s in signals:
        check_isinstance(s, RawSignal)
    
    resources = rawlog.get_resources()
    check_isinstance(signals, list)
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
    
    for x in rawlog.read(topics=signals):
        check_timed_named(x)
        timestamp, (name, value) = x  # @UnusedVariable
        assert name in signals
        # TODO: add type check
        
    
    