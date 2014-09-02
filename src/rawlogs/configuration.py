from conf_tools import ConfigMaster

__all__ = ['get_conftools_rawlogs', 'get_rawlogs_config']

class RawlogsConfig(ConfigMaster):
    
    def __init__(self):
        ConfigMaster.__init__(self, 'rawlogs')

        from rawlogs.interface import RawLog
        
        self.rawlogs = self.add_class_generic('rawlogs', '*.rawlogs.yaml', RawLog)        
        
    def get_default_dir(self):
        return "rawlogs.configs"
        

get_rawlogs_config = RawlogsConfig.get_singleton


def get_conftools_rawlogs():
    return get_rawlogs_config().rawlogs



