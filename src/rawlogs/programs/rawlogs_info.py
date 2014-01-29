from .main import RawlogsMainCmd
from conf_tools.utils import friendly_path, indent
from pprint import pformat
from quickapp import QuickAppBase
from rawlogs import get_conftools_rawlogs


__all___ = ['RawLogsInfo']


class RawLogsInfo(RawlogsMainCmd, QuickAppBase):
    """ Displays the signals defined in the raw log """
    
    cmd = 'info'
    
    def define_program_options(self, params):
        params.add_string_list("rawlogs", help="Raw log IDs", default=['*'])

    def go(self):
#         id_rawlog = self.options.rawlog
        
        library = get_conftools_rawlogs()
#
#         if id_rawlog is None:
#             logs = set(library.keys())
#             if not logs:
#                 self.error('Could not find any log and none specified.')
#         else:
#             logs = [id_rawlog]

        config = get_conftools_rawlogs()

        id_rawlogs = config.expand_names(self.options.rawlogs)
        
        for id_rawlog in id_rawlogs:
            rawlog = library.instance(id_rawlog)
            print('------- %s ' % id_rawlog)
            print(summarize(rawlog))
        
        
        
def summarize(rawlog):
    s = ""
    s += 'Resources:\n'
    for x in rawlog.get_resources():
        s += ' - %s\n' % friendly_path(x)

    s += 'Signals:\n'
    signals = rawlog.get_signals()
    names = sorted(signals.keys())
    
    for x in names:
        v = signals[x]
        t0, t1 = v.get_time_bounds()
        length = t1 - t0
        reftime = v.get_time_reference()
        s += '%-55s  %10s %4.2f %10.4f %10.4f %s\n' % (x, reftime, length, t0, t1, v)
        
    s += 'Tags: %s\n' % rawlog.get_tags()

    
    s += 'Annotations:\n'
    s += indent(pformat(rawlog.get_annotations()), ' | ')

    return s
         
        
