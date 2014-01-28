from abc import abstractmethod

from contracts import ContractsMeta, contract


__all__ = ['RawLog']


class RawLog(object):    
    """ 
        A RawLog is a collection of related signals with possibly different
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
            Yields a sequence of:
                 timestamp, (name, value)
                 
        """
        
    @contract(returns='list(str)')
    def get_tags(self):
        """ Returns a list of tags used to organize the logs. """
        ann = self.get_annotations()
        return ann.get('tags', [])
    
    @contract(returns='dict')
    def get_annotations(self):
        """ 
            Returns a free-form, YAML-dumpable dictionary of application-specific
            attributes. 
        """
        return {}
    
    def read_signal_all(self, signal_name):
        """ Read the complete values for a signal.
            Returns array of timestamp values, and a sequence of values. """
        import numpy as np
        values = []
        timestamps = []
        for timestamp, (name, value) in self.read([signal_name]):
            assert name == signal_name
            values.append(value)
            timestamps.append(timestamp)
        return np.array(timestamps), values

    def read_signal_all_as_array(self, signal_name):
        """ returns the data as an array with fields 'timestamp' and 'value' """
        import numpy as np
        timestamps, values = self.read_signal_all(signal_name)
        v0 = np.asarray(values[0])
        dtype = [('timestamp', 'float'),
                 ('value', v0.dtype, v0.shape)]
        x = np.zeros(shape=len(timestamps), dtype=dtype)
        x['timestamp'] = timestamps
        x['value'] = values
        return x
