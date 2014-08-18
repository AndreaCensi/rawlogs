from contracts import contract

from rawlogs import RawLog
from reprep import Report


__all__ = [
    'report_rawlog',
]

@contract(returns=Report, rawlog=RawLog)
def report_rawlog(rawlog):
    
    r = Report()

    cols = ['signal', 'bounds']
    rows = []
    data = []
    
    for name, signal in rawlog.get_signals().items():
        rows.append(name)
        row = [str(signal),
               signal.get_time_bounds()]
        data.append(row)
#         s += '%s : %s\n' % (name, signal)

    r.table('summary', cols=cols, rows=rows, data=data)
#     r.text('summary', s)
    return r




