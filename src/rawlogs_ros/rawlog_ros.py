from rawlogs import RawSignal, logger
from rawlogs.library import LogWithAnnotations
from rosbag_utils import read_bag_stats, rosbag_info_cached, read_bag_stats_progress


__all__ = ['ROSLog']


class ROSLog(LogWithAnnotations):
    
    def __init__(self, filename, annotations={}):
        LogWithAnnotations.__init__(self, annotations=annotations)
        self.bag = filename
        
        self._bag_info = None  # cached result
        
    def get_rosbag_info(self):
        if self._bag_info is None:
            self._bag_info = rosbag_info_cached(self.bag)
        return self._bag_info
    
    def get_signals(self):
        info = self.get_rosbag_info()
        bounds = info['start'], info['end']
        signals = {}
        for t in info['topics']:
            name = t['topic']
            ros_type = t['type']
            s = ROSLogSignal(signal_type=ros_type, bagfile=self.bag, bounds=bounds)
            signals[name] = s
             
        return signals   
    
    def get_resources(self): 
        return [self.bag]

    def read(self, topics, start=None, stop=None, use_stamp_if_available=False):
        source = read_bag_stats(self.bag, topics, logger=None, start_time=start, stop_time=stop)
        source = read_bag_stats_progress(source, logger, interval=2)
        
        oldt = None
        for topic, msg, t, _ in source:  
            name = topic
            
            value = msg
            
            if use_stamp_if_available:
                try:
                    stamp = msg.header.stamp
                except:
                    timestamp = t.to_sec()
                else:
                    timestamp = stamp.to_sec()

                    if timestamp == 0:
                        timestamp = t.to_sec()
            else:
                timestamp = t.to_sec()
                
            
            if oldt is not None:
                if oldt == timestamp:
                    logger.error('Sequence with invalid timestamp? %s' % timestamp)
            
            if start is not None:
                if timestamp < start:
                    logger.warn('Skipping %s < %s because not included in interval.'
                                % (timestamp, start))
                    continue
                    
            if stop is not None:
                if timestamp > stop:
                    logger.warn('Skipping %s > %s because not included in interval.'
                                % (timestamp, stop))
                    continue
            
            if start is not None:
                assert start <= timestamp
            
            if stop is not None:
                assert stop >= timestamp
                                           
            yield timestamp, (name, value)

            oldt = timestamp

        

class ROSLogSignal(RawSignal):
    
    def __init__(self, signal_type, bagfile, bounds):
        self.bagfile = bagfile
        self.signal_type = signal_type
        self.bounds = bounds
        
    def get_signal_type(self):
        return self.signal_type
                
    def get_time_reference(self):
        return 'rostime'
        
    def get_resources(self):
        return [self.bagfile]
    
    def get_time_bounds(self):
        return self.bounds
    
    
    
