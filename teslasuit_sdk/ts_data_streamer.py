import time
import copy
from ctypes import *
from enum import Enum, unique
from . import ts_data
from . import ts_types

class TsDataStreamer:
    """
    A class that provides data streaming of types: Mocap, EMG, ECG
    """
    def __init__(self, id, lib):
        self.id = id
        self.lib = lib
        self.__frame_wait_time = 0.005
        self.__init_mocap()
        self.__init_emg()
        self.__init_ppg()
        self.__init_temperature()

    def __init_mocap(self):
        c_number_of_imu_sensors = c_uint64(0)
        self.lib.ts_get_number_of_imu_sensors(pointer(self.id), pointer(c_number_of_imu_sensors))
        self.number_of_imu_sensors = c_number_of_imu_sensors.value

        self.imu_sensors = (ts_types.TsSensor * self.number_of_imu_sensors)()
        self.lib.ts_get_imu_sensors(pointer(self.id), pointer(self.imu_sensors), c_number_of_imu_sensors)

        self.__q6_buffer = (ts_types.TsQuat * self.number_of_imu_sensors)()
        self.__q9_buffer = (ts_types.TsQuat * self.number_of_imu_sensors)()
        self.__gyro_buffer = (ts_types.TsVec3f * self.number_of_imu_sensors)()
        self.__magn_buffer = (ts_types.TsVec3f * self.number_of_imu_sensors)()
        self.__accel_buffer = (ts_types.TsVec3f * self.number_of_imu_sensors)()
        self.__linear_accel_buffer = (ts_types.TsVec3f * self.number_of_imu_sensors)()
        self.__timestamp_buffer = (c_uint64 * self.number_of_imu_sensors)()
        self.__temperature_buffer = (c_float * self.number_of_imu_sensors)()

        self.is_mocap_skeleton_buffering_enabled = False
        self.mocap_skeleton_buffer_size = 0
        self.is_mocap_skeleton_buffer_ready = False
        self.mocap_skeleton = ts_data.TsSkeleton()
        self.mocap_skeleton_buffer = []
        self.__mocap_skeleton_collector = []

        self.is_mocap_raw_imu_buffering_enabled = False
        self.mocap_raw_imu_buffer_size = 0
        self.is_mocap_raw_imu_buffer_ready = False
        self.mocap_raw_imu = []
        self.mocap_raw_imu_buffer = []
        self.__mocap_raw_imu_collector = []

    def __init_emg(self):
        self.is_emg_buffering_enabled = False
        self.emg_buffer_size = 0
        self.is_emg_buffer_ready = False
        self.emg_data = ts_data.TsEmgData()
        self.emg_buffer = ts_data.TsEmgDataBuffer()
        self.__emg_collector = ts_data.TsEmgDataBuffer()

    def __init_ppg(self):
        self.is_ppg_buffering_enabled = False
        self.ppg_buffer_size = 0
        self.is_ppg_buffer_ready = False
        self.ppg_data = ts_data.TsPpgData()
        self.ppg_buffer = []
        self.__ppg_collector = []

        self.is_raw_ppg_buffering_enabled = False
        self.raw_ppg_buffer_size = 0
        self.is_raw_ppg_buffer_ready = False
        self.raw_ppg_data = ts_data.TsPpgRawData()
        self.raw_ppg_buffer = []
        self.__raw_ppg_collector = []

    def __init_temperature(self):
        self.is_temperature_buffering_enabled = False
        self.temperature_buffer_size = 0
        self.is_temperature_buffer_ready = False
        self.temperature_data = ts_data.TsTemperatureData()
        self.temperature_buffer = []
        self.__temperature_collector = []

    def get_imu_sensors_string(self, indent='  '):
        s = f'Imu Sensors: number_of_sensors={len(self.imu_sensors)}'
        for sensor in self.imu_sensors:
            s += '\n' + indent + sensor.to_string()
        return s

    def start_all(self):
        self.start_mocap_streaming()
        #self.start_emg_streaming()
        self.start_ppg_streaming()
        self.start_raw_ppg_streaming()
        self.start_temperature_streaming()

    def stop_all(self):
        self.stop_mocap_streaming()
        self.stop_emg_streaming()
        self.stop_ppg_streaming()
        self.stop_raw_ppg_streaming()
        self.start_temperature_streaming()

    def start_mocap_streaming(self):
        def on_skeleton_updated(id_ptr, skeleton_ptr):
            # TODO: fix bug with wrong device uuid in C API to enable device filtering
            #if id_ptr.contents != self.id:
            #    return
            self.mocap_skeleton = copy.deepcopy(skeleton_ptr.contents)
            if self.is_mocap_skeleton_buffering_enabled:
                self.__mocap_skeleton_collector.append(self.mocap_skeleton)
                if len(self.__mocap_skeleton_collector) >= self.mocap_skeleton_buffer_size:
                    self.mocap_skeleton_buffer = self.__mocap_skeleton_collector
                    self.__mocap_skeleton_collector = []
                    self.is_mocap_skeleton_buffer_ready = True

        def on_raw_imu_updated(id_ptr, handle_ptr):
            # TODO: fix bug with wrong device uuid in C API to enable device filtering
            #if id_ptr.contents != self.id:
            #    return
            self.parse_raw_imu_data(handle_ptr)
            if self.is_mocap_raw_imu_buffering_enabled:
                self.__mocap_raw_imu_collector.append(self.mocap_raw_imu)
                if len(self.__mocap_raw_imu_collector) >= self.mocap_raw_imu_buffer_size:
                    self.mocap_raw_imu_buffer = self.__mocap_raw_imu_collector
                    self.__mocap_raw_imu_collector = []
                    self.is_mocap_raw_imu_buffer_ready = True

        skeleton_update_fn_prototype = CFUNCTYPE(None, POINTER(ts_types.TsUuid), POINTER(ts_data.TsSkeleton))
        subscribe_skeleton_fn = self.lib.ts_subscribe_to_mocap_skeleton_update
        subscribe_skeleton_fn.argtypes = [POINTER(ts_types.TsUuid), skeleton_update_fn_prototype, POINTER(ts_types.TsUuid)]
        self.mocap_skeleton_callback = skeleton_update_fn_prototype(on_skeleton_updated)
        self.mocap_skeleton_subscription_id = ts_types.TsUuid()
        subscribe_skeleton_fn(pointer(self.id), self.mocap_skeleton_callback, pointer(self.mocap_skeleton_subscription_id))

        raw_imu_update_fn_prototype = CFUNCTYPE(None, POINTER(ts_types.TsUuid), c_void_p)
        subscribe_raw_imu_fn = self.lib.ts_subscribe_to_mocap_imu_sensors_update
        subscribe_raw_imu_fn.argtypes = [POINTER(ts_types.TsUuid), raw_imu_update_fn_prototype, POINTER(ts_types.TsUuid)]
        self.mocap_raw_imu_callback = raw_imu_update_fn_prototype(on_raw_imu_updated)
        self.mocap_raw_imu_subscription_id = ts_types.TsUuid()
        subscribe_raw_imu_fn(pointer(self.id), self.mocap_raw_imu_callback, pointer(self.mocap_raw_imu_subscription_id))

        self.lib.ts_start_mocap_streaming(pointer(self.id))


    def parse_raw_imu_data(self, handle_ptr):
        fn = self.lib.ts_get_imu_sensors_q6
        fn.argtypes = [c_void_p, POINTER(ts_types.TsSensor * self.number_of_imu_sensors), c_uint64, POINTER(ts_types.TsQuat * self.number_of_imu_sensors)]
        fn(handle_ptr, pointer(self.imu_sensors), c_uint64(self.number_of_imu_sensors), pointer(self.__q6_buffer))
        fn = self.lib.ts_get_imu_sensors_q9
        fn.argtypes = [c_void_p, POINTER(ts_types.TsSensor * self.number_of_imu_sensors), c_uint64, POINTER(ts_types.TsQuat * self.number_of_imu_sensors)]
        fn(handle_ptr, pointer(self.imu_sensors), c_uint64(self.number_of_imu_sensors), pointer(self.__q9_buffer))
        fn = self.lib.ts_get_imu_sensors_gyro
        fn.argtypes = [c_void_p, POINTER(ts_types.TsSensor * self.number_of_imu_sensors), c_uint64, POINTER(ts_types.TsVec3f * self.number_of_imu_sensors)]
        fn(handle_ptr, pointer(self.imu_sensors), c_uint64(self.number_of_imu_sensors), pointer(self.__gyro_buffer))
        fn = self.lib.ts_get_imu_sensors_magn
        fn.argtypes = [c_void_p, POINTER(ts_types.TsSensor * self.number_of_imu_sensors), c_uint64, POINTER(ts_types.TsVec3f * self.number_of_imu_sensors)]
        fn(handle_ptr, pointer(self.imu_sensors), c_uint64(self.number_of_imu_sensors), pointer(self.__magn_buffer))
        fn = self.lib.ts_get_imu_sensors_accel
        fn.argtypes = [c_void_p, POINTER(ts_types.TsSensor * self.number_of_imu_sensors), c_uint64, POINTER(ts_types.TsVec3f * self.number_of_imu_sensors)]
        fn(handle_ptr, pointer(self.imu_sensors), c_uint64(self.number_of_imu_sensors), pointer(self.__accel_buffer))
        fn = self.lib.ts_get_imu_sensors_linear_accel
        fn.argtypes = [c_void_p, POINTER(ts_types.TsSensor * self.number_of_imu_sensors), c_uint64, POINTER(ts_types.TsVec3f * self.number_of_imu_sensors)]
        fn(handle_ptr, pointer(self.imu_sensors), c_uint64(self.number_of_imu_sensors), pointer(self.__linear_accel_buffer))
        '''
        TODO: fix C API bug with timestamp and temperature

        fn = self.lib.ts_get_imu_sensors_timestamp
        fn.argtypes = [c_void_p, POINTER(ts_types.TsSensor * self.number_of_imu_sensors), c_uint64, POINTER(c_uint64 * self.number_of_imu_sensors)]
        fn(handle_ptr, pointer(self.imu_sensors), c_uint64(self.number_of_imu_sensors), pointer(self.__timestamp_buffer))
        fn = self.lib.ts_get_imu_sensors_temperature
        fn.argtypes = [c_void_p, POINTER(ts_types.TsSensor * self.number_of_imu_sensors), c_uint64, POINTER(c_float * self.number_of_imu_sensors)]
        fn(handle_ptr, pointer(self.imu_sensors), c_uint64(self.number_of_imu_sensors), pointer(self.__temperature_buffer))
        '''
        tmp_raw_imu = []
        for i in range(0, self.number_of_imu_sensors):
            imu_data = ts_data.TsRawImuData()
            imu_data.sensor_id = copy.deepcopy(self.imu_sensors[i])
            imu_data.q6 = copy.deepcopy(self.__q6_buffer[i])
            imu_data.q9 = copy.deepcopy(self.__q9_buffer[i])
            imu_data.gyro = copy.deepcopy(self.__gyro_buffer[i])
            imu_data.magn = copy.deepcopy(self.__magn_buffer[i])
            imu_data.accel = copy.deepcopy(self.__accel_buffer[i])
            imu_data.linear_accel = copy.deepcopy(self.__linear_accel_buffer[i])
            imu_data.timestamp = copy.deepcopy(self.__timestamp_buffer[i])
            imu_data.temperature = copy.deepcopy(self.__temperature_buffer[i])
            tmp_raw_imu.append(imu_data)
        self.mocap_raw_imu = tmp_raw_imu


    def start_emg_streaming(self):
        def on_emg_updated(id_ptr, data_ptr):
            # TODO: fix bug with wrong device uuid in C API to enable device filtering
            #if id_ptr.contents != self.id:
            #    return
            self.emg_data = data_ptr.contents
            if self.is_emg_buffering_enabled:
                self.__emg_collector.append_data(self.emg_data)
                if self.__emg_collector.get_len() >= self.emg_buffer_size:
                    self.emg_buffer = copy.deepcopy(self.__emg_collector)
                    self.__emg_collector.clear()
                    self.is_emg_buffer_ready = True

        callback_prototype = CFUNCTYPE(None, POINTER(ts_types.TsUuid), POINTER(ts_data.TsEmgData))
        subsribe_fn = self.lib.ts_subscribe_to_emg_update
        subsribe_fn.argtypes = [POINTER(ts_types.TsUuid), callback_prototype, POINTER(ts_types.TsUuid)]
        self.emg_callback = callback_prototype(on_emg_updated)
        self.emg_subscription_id = ts_types.TsUuid()
        subsribe_fn(pointer(self.id), self.emg_callback, pointer(self.emg_subscription_id))
        self.lib.ts_start_emg_streaming(pointer(self.id))

    def start_ppg_streaming(self):
        print('Start ppg streaming')

    def start_raw_ppg_streaming(self):
        print('Start raw ppg streaming')

    def start_temperature_streaming(self):
        print('Start temperature streaming')

    def wait_mocap_skeleton_buffer_ready(self):
        while not self.is_mocap_skeleton_buffer_ready:
            time.sleep(self.__frame_wait_time)
        self.is_mocap_skeleton_buffer_ready = False

    def wait_mocap_raw_imu_buffer_ready(self):
        while not self.is_mocap_raw_imu_buffer_ready:
            time.sleep(self.__frame_wait_time)
        self.is_mocap_raw_imu_buffer_ready = False

    def wait_emg_buffer_ready(self):
        while not self.is_emg_buffer_ready:
            time.sleep(self.__frame_wait_time)
        self.is_emg_buffer_ready = False

    def wait_ppg_buffer_ready(self):
        while not self.is_ppg_buffer_ready:
            time.sleep(self.__frame_wait_time)
        self.is_ppg_buffer_ready = False

    def wait_raw_ppg_buffer_ready(self):
        while not self.is_raw_ppg_buffer_ready:
            time.sleep(self.__frame_wait_time)
        self.is_raw_ppg_buffer_ready = False

    def wait_temperature_buffer_ready(self):
        while not self.is_temperature_buffer_ready:
            time.sleep(self.__frame_wait_time)
        self.is_temperature_buffer_ready = False

    def stop_mocap_streaming(self):
        self.lib.ts_stop_mocap_streaming(pointer(self.id))

    def stop_emg_streaming(self):
        self.lib.ts_stop_emg_streaming(pointer(self.id))

    def stop_ppg_streaming(self):
        self.lib.ts_stop_ppg_streaming(pointer(self.id))

    def stop_raw_ppg_streaming(self):
        self.lib.ts_stop_raw_ppg_streaming(pointer(self.id))

    def stop_temperature_streaming(self):
        self.lib.ts_stop_temperature_streaming(pointer(self.id))
