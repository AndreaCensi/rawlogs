from .main import RawlogsMainCmd
from conf_tools.utils import friendly_path
from quickapp import QuickAppBase
from rawlogs import get_conftools_rawlogs
from conf_tools.utils.indent_string import indent
from pprint import pformat

__all___ = ['RawLogsInfo']


class RawLogsInfo(RawlogsMainCmd, QuickAppBase):
    cmd = 'info'
    
    def define_program_options(self, params):
        params.add_string("rawlog", help="Raw log ID", default=None)

    def go(self):
        id_rawlog = self.options.rawlog
        
        library = get_conftools_rawlogs()
        
        if id_rawlog is None:
            logs = set(library.keys())
            if not logs:
                self.error('Could not find any log and none specified.')
        else:
            logs = [id_rawlog]  
        
        for id_rawlog in logs:
            rawlog = library.instance(id_rawlog)
            print('------- %s ' % id_rawlog)
            print(summarize(rawlog))
        
        
        
def summarize(rawlog):
    s = ""
    s += 'Resources:\n'
    for x in rawlog.get_resources():
        s += ' - %s\n' % friendly_path(x)

    s += 'Signals:\n'
    for x, v in rawlog.get_signals().items():
        t0, t1 = v.get_time_bounds()
        length = t1 - t0
        reftime = v.get_time_reference()
        s += '%50s  %10s %4.2f  %s\n' % (x, reftime, length, v)
        
    s += 'Tags: %s\n' % rawlog.get_tags()

    
    s += 'Annotations:\n'
    s += indent(pformat(rawlog.get_annotations()), ' | ')

    return s
         
        
