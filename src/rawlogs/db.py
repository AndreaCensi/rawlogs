from contracts import contract
from .configuration import get_conftools_rawlogs


__all__ = ['get_rawlogs_by_tag']


@contract(tags='seq[>=1](str)', returns='dict(str:isinstance(RawLog))')
def get_rawlogs_by_tag(tags):
    """ Get all rawlogs that have the given tags. Returns a dictionary string -> RawLog. """
    return dict(get_rawlogs_by_tag_it(tags))
    
    
def get_rawlogs_by_tag_it(tags):
    library = get_conftools_rawlogs()
    
    for id_rawlog in library:
        rawlog = library.instance(id_rawlog)
        
        ltags = rawlog.get_tags()
        
        if set(tags) <= set(ltags):
            yield id_rawlog, rawlog
