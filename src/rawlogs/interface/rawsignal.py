from abc import abstractmethod
from contracts import ContractsMeta, contract


__all__ = ['RawSignal']


class RawSignal(object):
    """ Interface for a generic signal stream. """
    
    __metaclass__ = ContractsMeta

    @abstractmethod
    def get_signal_type(self):
        """ Returns the type of this signal (string or python class) """        

    @abstractmethod
    @contract(returns='str')
    def get_time_reference(self):
        """ Returns the time reference for this signal. """
        
    @abstractmethod
    @contract(returns='list(str)')
    def get_resources(self):
        """ Returns the list of files that this signal needs. """
      
    @abstractmethod
    @contract(returns='tuple(float, float)')
    def get_time_bounds(self):
        """ Returns a tuple of floats representing start and end times for this log. """ 
        pass
    
    def get_length(self):
        a, b = self.get_time_bounds()
        return b - a
    
    def __str__(self):
        cname = type(self).__name__
        s = ('%s(timeref=%s;type=%s)' % 
             (cname, self.get_time_reference(), self.get_signal_type()))
        return s 

