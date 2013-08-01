from abc import abstractmethod
from contracts import ContractsMeta, contract


__all__ = ['RawLog']


class RawLog(object):    
    """ 
        A log is a collection of related signals with possibly different
        reference frames with attached resources (files).
    """
    
    __metaclass__ = ContractsMeta

    @abstractmethod
    @contract(returns='dict(str:isinstance(RawSignal))') 
    def get_signals(self):
        """ Returns the signals available """
    
    @abstractmethod
    @contract(returns='list(str)')
    def get_resources(self): 
        """ Returns the physical files needed for this log """
        
    @abstractmethod
    def read(self, topics, start=None, stop=None):
        """ 
            Yields a sequence of RawSignalData
        """
        
    @contract(returns='list(str)')
    def get_tags(self):
        """ Returns a list of tags used to organize the logs. """
        return []
    
    @contract(returns='dict')
    def get_annotations(self):
        """ 
            Returns a free-form, YAML-dumpable dictionary of application-specific
            attributes. 
        """
        return {}
    
    