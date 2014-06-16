# from blocks import WithQueue
# 
# 
# class Filter(object):
#     
#     def put(self, timestamp, value):
#         pass
#     
# 
# class se2_from_SE2(WithQueue):
#     
#     def __init__(self, pass):
#         pass
#     
#     def put(self, x):
#         timestamp, value = x
#         
#
# from abc import abstractmethod
# from contracts import describe_value, contract
# from geometry import SE2
# from itertools import tee, izip
# from procgraph import Block
# from types import GeneratorType
# from procgraph.block_utils.iterator_generator import IteratorGenerator
#
# class se2_from_SE2_seq(Block):
#     ''' Block used by :ref:`block:pose2commands`. '''
#     Block.alias('se2_from_SE2_seq')
#
#     Block.input('pose', 'Pose as an element of SE2')
#     Block.output('velocity', 'Velocity as an element of se(2).')
#
#     def init(self):
#         self.state.prev = None
#
#     def update(self):
#         q2 = self.get_input(0)
#         t2 = self.get_input_timestamp(0)
#
#         if self.state.prev is not None:
#             t1, q1 = self.state.prev
#             vel = velocity_from_poses(t1, q1, t2, q2)
#             self.set_output(0, vel, timestamp=t2)
#
#         self.state.prev = t2, q2
#
#
#
# def pose_difference(poses, S=SE2):
#     """ poses: sequence of (timestamp, pose) """
#
#     for p1, p2 in pairwise(poses):
#         t1, q1 = p1
#         t2, q2 = p2
#         v = velocity_from_poses(t1, q1, t2, q2, S=S)
#         yield v
#
# def velocity_from_poses(t1, q1, t2, q2, S=SE2):
#     delta = t2 - t1
#     if not delta > 0:
#         raise ValueError('invalid sequence')
#
#     x = S.multiply(S.inverse(q1), q2)
#     xt = S.algebra_from_group(x)
#     v = xt / delta
#     return v
#
# def pairwise(iterable):
#     "s -> (s0,s1), (s1,s2), (s2, s3), ..."
#     a, b = tee(iterable)
#     next(b, None)
#     return izip(a, b)
