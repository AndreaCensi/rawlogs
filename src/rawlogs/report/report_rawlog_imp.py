from contracts import contract

from rawlogs import RawLog
from reprep import Report


__all__ = ['report_rawlog']

@contract(returns=Report, rawlog=RawLog)
def report_rawlog(rawlog):
    
    r = Report()

    s = ""
    
    for name, signal in rawlog.get_signals().items():
        s += '%s : %s\n' % (name, signal)

    r.text('summary', s)
    return r




