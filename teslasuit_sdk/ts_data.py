from ctypes import *
from enum import Enum, unique
from . import ts_types
from . import ts_mapper

class TsTransformation(Structure):
    _pack_ = 1
    _fields_ = [('position', ts_types.TsVec3f),
                ('rotation', ts_types.TsQuat)]

    def to_string(self):
        return f'T(pos={self.position.to_string()}, rot={self.rotation.to_string()})'


class TsSkeletonBone(Structure):
    _pack_ = 1
    _fields_ = [('index', c_uint8),
                ('transformation', TsTransformation)]

    def to_string(self):
        return f'Bone index={self.index}, {self.transformation.to_string()}'


class TsSkeleton(Structure):
    _pack_ = 1
    _fields_ = [('root', TsTransformation),
                ('bones_size', c_uint8),
                ('bones', TsSkeletonBone * ts_mapper.get_max_number_of_bones())]

    def to_string(self, indent='  '):
        s = f'Skeleton -> Root: {self.root.to_string()}, number_of_bones={self.bones_size}'
        for bone_index in range(0, self.bones_size):
            s += '\n' + indent + bones[bones_index].to_string()
        return s


class TsRawImuData():
    def __init__(self):
        self.sensor_id = ts_types.TsSensor()
        self.q6 = ts_types.TsQuat()
        self.q9 = ts_types.TsQuat()
        self.gyro = ts_types.TsVec3f()
        self.magn = ts_types.TsVec3f()
        self.accel = ts_types.TsVec3f()
        self.linear_accel = ts_types.TsVec3f()
        self.timestamp = c_uint64(0)
        self.temperature = c_float(0)

    def to_string(self):
        return f'Raw IMU Data: sensor_id=({self.sensor_id.to_string()}), q6={self.q6.to_string()}, q9={self.q9.to_string()}, gyro={self.gyro.to_string()}, magn={self.magn.to_string()}, accel={self.accel.to_string()}, linear_accel={self.linear_accel.to_string()}, timestamp={self.timestamp}, temperature={self.temperature}'


class TsEmgOptions(Structure):
    _pack_ = 1
    _fields_ = [('sample_size', c_uint64),
                ('sampling_frequency', c_uint64),
                ('lower_bandwidth', c_uint64),
                ('upper_bandwidth', c_uint64)]

    def to_string(self):
        return f'sample_size={self.sample_size}, sampling_frequency={self.sampling_frequency}, lower_bandwidth={self.lower_bandwidth}, upper_bandwidth={self.upper_bandwidth}'

class TsEmgChannelSample(Structure):
    _pack_ = 1
    _fields_ = [('channel_index', c_uint32),
                ('sample', POINTER(c_int64))]

    def to_string(self, size=0):
        s = f'channel_index={self.channel_index}, sample=['
        for index in range(0, size):
            if index > 0:
                s += ', '
            s += str(self.sample[index])
        return s + ']'


class TsEmgNodeData(Structure):
    _pack_ = 1
    _fields_ = [('node_index', c_uint32),
                ('number_of_channels', c_uint32),
                ('channels', POINTER(TsEmgChannelSample)),
                ('sample_timestamps', POINTER(c_uint64))]


class TsEmgData(Structure):
    _pack_ = 1
    _fields_ = [('sensor_options', TsEmgOptions),
                ('number_of_nodes', c_uint32),
                ('nodes', POINTER(TsEmgNodeData))]


class TsEmgChannelDataBuffer():
    def __init__(self):
        self.channel_index = 0
        self.buffer = []

    def to_string(self):
        return f'EMG Channel Data Buffer: channel_index={self.channel_index}, buffer={self.buffer}'


class TsEmgNodeDataBuffer():
    def __init__(self):
        self.node_index = 0
        self.channels = []
        self.timestamps = []

    def to_string(self, indent='  '):
        s = f'EMG Node Data Buffer: node_index={self.node_index}, number_of_channels={len(self.channels)}'
        s += f'\n' + indent + f'Timestamps: {self.timestamps}'
        s += f'\n' + indent + f'Channels:'
        for channel in self.channels:
            s += f'\n' + indent + channel.to_string()
        return s


class TsEmgDataBuffer():
    def __init__(self):
        self.clear()

    def append_data(self, emg_data):
        self.options = emg_data.sensor_options
        for node_index in range(0, emg_data.number_of_nodes):
            self.__append_node_data(node_index, emg_data.nodes[node_index])            

    def __append_node_data(self, node_index, emg_node_data):
        node_data_buffer = TsEmgNodeDataBuffer()
        is_add_node = True
        if node_index < len(self.nodes):
            node_data_buffer = self.nodes[node_index]
            is_add_node = False
        node_data_buffer.node_index = emg_node_data.node_index
        for index in range(0, self.options.sample_size):
            node_data_buffer.timestamps.append(emg_node_data.sample_timestamps[index])
        for channel_index in range(0, emg_node_data.number_of_channels):
            self.__append_channel_sample(channel_index, node_data_buffer, emg_node_data.channels[channel_index])
        if is_add_node:
            self.nodes.append(node_data_buffer)

    def __append_channel_sample(self, channel_index, node_data_buffer, emg_channel_sample):
        channel_data_buffer = TsEmgChannelDataBuffer()
        is_add_channel = True
        if channel_index < len(node_data_buffer.channels):
            channel_data_buffer = node_data_buffer.channels[channel_index]
            is_add_channel = False
        channel_data_buffer.channel_index = emg_channel_sample.channel_index
        for index in range(0, self.options.sample_size):
            channel_data_buffer.buffer.append(emg_channel_sample.sample[index])
        if is_add_channel:
            node_data_buffer.channels.append(channel_data_buffer)

    def clear(self):
        self.nodes = []
        self.options = TsEmgOptions()

    def get_len(self):
        if len(self.nodes) == 0:
            return 0
        first_node = self.nodes[0]
        if len(first_node.channels) == 0:
            return 0
        l = len(first_node.channels[0].buffer)
        return l

    def to_string(self, indent='  '):
        s = f'EMG Data Buffer: number_of_nodes={len(self.nodes)}, buffer_size={self.get_len()}'
        s += f'\n' + indent + f'Options=({self.options.to_string()})'
        for node in self.nodes:
            s += f'\n' + indent + node.to_string(indent + '  ')
        return s


class TsPpgNodeData(Structure):
    _pack_ = 1
    _fields_ = [('heart_rate', c_uint32),
                ('oxygen_percent', c_uint8),
                ('is_heart_rate_valid', c_bool),
                ('is_oxygen_percent_valid', c_bool),
                ('timestamp', c_uint32)]


class TsPpgData(Structure):
    _pack_ = 1
    _fields_ = [('number_of_nodes', c_uint32),
                ('nodes', TsPpgNodeData * ts_mapper.get_max_number_of_channels())]


class TsPpgRawSample(Structure):
    _pack_ = 1
    _fields_ = [('sample_size', c_uint64),
                ('red_sample', c_uint64 * ts_mapper.get_max_number_of_channels()),
                ('ir_sample', c_uint64 * ts_mapper.get_max_number_of_channels()),
                ('timestamp', c_uint32)]


class TsPpgRawData(Structure):
    _pack_ = 1
    _fields_ = [('number_of_nodes', c_uint32),
                ('nodes', TsPpgRawSample * ts_mapper.get_max_number_of_channels())]


@unique
class TsTemperatureSensorType(Enum):
    Undefined = 0
    Si7051 = 1
    LX90632 = 2


class TsTemperatureNodeData(Structure):
    _pack_ = 1
    _fields_ = [('sensor_type', c_uint8),
                ('temperature', c_uint16)]


class TsTemperatureData(Structure):
    _pack_ = 1
    _fields_ = [('number_of_nodes', c_uint32),
                ('nodes', TsTemperatureNodeData * ts_mapper.get_max_number_of_channels()),
                ('timestamp', c_uint64)]
