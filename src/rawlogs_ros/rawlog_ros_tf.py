from memos import memo_disk_cache
import numpy as np
from ros_node_utils import pose_from_ROS_transform
from rosbag_utils import read_bag_stats
from rosbag_utils import rosbag_info_cached

from .rawlog_ros import ROSLog, ROSLogSignal


__all__ = ['ROSLogTF']

class ROSLogTF(ROSLog):
    """ 
        This also creates signals for each tf frame.
        
        Note that this incurs the cost of reading the entire
        file once to make sure we know all possible TFs.
        The results are cached on disk.
        
        Poses datatype is a 4x4 array (SE3).
       
        tf_signals:
        - <name>:
            parent: '/map'
            child: '/odom_combined 
    """

    def __init__(self, filename, annotations, tf_signals, tf_topic='tf'):
        self.tf_topic = tf_topic
        ROSLog.__init__(self, filename, annotations=annotations)
        self.tf_signals = {}
        for name, x in tf_signals.items():
            self.tf_signals[name] = dict(parent=x['parent'], child=x['child'])

    def get_signals(self):
        # We use all the normal signals
        signals = ROSLog.get_signals(self)
        
        info = self.get_rosbag_info()
        bounds = info['start'], info['end']

        # If there is a 'tf' signal we also create extra TF
        # signals
        print list(signals.keys())
        if self.tf_topic in signals:
            tf_info = get_tf_info(self.bag, self.tf_topic)
            
            for name, x in self.tf_signals.items():
                key = (x['parent'], x['child'])
                if not key in tf_info:
                    msg = 'Could not find %s in %s' % (key, tf_info)
                    raise ValueError(msg)

                signals[name] = ROSLogSignal(signal_type=np.dtype(('float', (4, 4))),
                                             bagfile=self.bag, bounds=bounds)
        else:
            msg = 'No topic %s found.' % self.tf_topic
            raise ValueError(msg)
        return signals   
    
         
    
    def read(self, topics, start=None, stop=None, use_stamp_if_available=False):
        if any(x in topics for x in self.tf_signals):
            if not self.tf_topic in topics:
                topics.append(self.tf_topic)

        normal = ROSLog.read(self, topics=topics, start=start, stop=stop,
                             use_stamp_if_available=use_stamp_if_available)
        
        for timestamp, (signal, msg) in normal:
            if signal == self.tf_topic:
                for t in msg.transforms:
                    frame_id = t.header.frame_id
                    child_frame_id = t.child_frame_id
                    for name, x in self.tf_signals.items():
                        if x['parent'] == frame_id and x['child'] == child_frame_id:
                            transform = t.transform
                            pose = pose_from_ROS_transform(transform)
                            yield timestamp, (name, pose)

            else:
                yield timestamp, (signal, msg)


def get_tf_info(bagfile, tf_topic):
    return memo_disk_cache(bagfile, 'tf_info', get_tf_info_, bagfile, tf_topic)
        
def get_tf_info_(bagfile, tf_topic, read_interval=10):
    """ Returns a list of TF pairs (from, to) found in the log. """
    info = rosbag_info_cached(bagfile)
    start = info['start']
    stop = start + read_interval
    it = read_bag_stats(bagfile, topics=[tf_topic], start_time=start,
                        stop_time=stop)
    
    print('Reading file')
    pairs = set()
    for topic, msg, _, _ in it:
        if topic == tf_topic:
            for t in msg.transforms:
                frame_id = t.header.frame_id
                child_frame_id = t.child_frame_id
                key = (frame_id, child_frame_id)

                if not key in pairs:
                    pairs.add(key)
                    print key
    return pairs


# header:
#       seq: 0
#       stamp:
#         secs: 1312493271
#         nsecs: 266588249
#       frame_id: /narrow_stereo_gazebo_l_stereo_camera_frame
#     child_frame_id: /narrow_stereo_gazebo_l_stereo_camera_optical_frame
#     transform:
#       translation:
#         x: 0.0
#         y: 0.0
#         z: 0.0
#       rotation:
#         x: -0.5
#         y: 0.499999999998
#         z: -0.5
#         w: 0.500000000002
