from ctypes import *
from teslasuit_sdk import ts_api
# from teslasuit_sdk import ts_mapper
# from teslasuit_sdk import ts_haptic_player

# from colorama import init as colorama_init
# from colorama import Fore, Back, Style
from teslasuit_sdk import ts_api
from teslasuit_sdk.subsystems.ts_haptic import TsHapticParam, TsHapticParamType

class Teslasuit():
    def __init__(self):
        # colorama_init()
        self.api = ts_api.TsApi()
        self.asset_manager = self.api.asset_manager

        self.asset_id_list={}
        

    def connect_suit(self):
        device_manager = self.api.get_device_manager()
        suit = device_manager.get_or_wait_last_device_attached()
        print('Suit is connected.')

        self.haptic = suit.haptic

        self.streamer = suit.mocap


        mapper = self.api.mapper

        mapping_handle = suit.get_mapping()
        layouts = mapper.get_layouts(mapping_handle)
        for i in range(0, len(layouts)):
            if mapper.get_layout_element_type(layouts[i]) == 2 and mapper.get_layout_type(layouts[i]) == 1:
                break
        found_layout_index = i    
        bones = mapper.get_layout_bones(layouts[i])
        self.right_upper_arm_channels = mapper.get_bone_contents(bones[14])
        self.left_upper_arm_channels = mapper.get_bone_contents(bones[12])
        
        self.haptic_powwa=0
        


        
    def haptic_play_touch(self, channel_id, ampl = 100, period = 20000, pw = 100, duration = 100):


        params = [TsHapticParam() for i in range(0, 3)]
        params[0].type = TsHapticParamType.Period.value
        params[0].value = period

        params[1].type = TsHapticParamType.Amplitude.value
        params[1].value = ampl

        params[2].type = TsHapticParamType.PulseWidth.value
        params[2].value = pw
        self.haptic.play_touch(params, channel_id, duration)
            

    def stop_player(self):
        print('Stop player')
        self.player.stop_player()

    def load_asset(self, asset_path, asset_name):


            asset_handle = self.asset_manager.load_asset_from_path(asset_path)
            playable_id = self.haptic.create_playable(asset_handle, False)


            
            self.asset_id_list[asset_name] = playable_id
        
    # def haptic_calibration(self, channel): 
    #     min_value = 1
    #     max_value = 30
    #     while 1==1:
    #         min_input = easygui.integerbox("Enter minimal amplitude. Enter '0' to confirm.", 'Min calibration', min_value, 0, 100)
    #         if min_input == 0:
    #             break
    #         min_value = min_input
    #         self.haptic_play_touch([channel], ampl = min_value, freq = 40, pw = 240, duration = 1000)
    #     while 1==1:
    #         max_input = easygui.integerbox("Enter maximal amplitude. Enter '0' to confirm.", 'Max calibration', max_value, 0, 100)
    #         if max_input == 0:
    #             break
    #         max_value = max_input
    #         self.haptic_play_touch([channel], ampl = max_value, freq = 40, pw = 240, duration = 1000)
    #     print('MIN:', min_value, 'MAX:', max_value)
    #     return min_value, max_value    


    def start_mocap_streaming(self, buffer = 3):
        self.streamer.start_streaming()
        
    def stop_mocap_streaming(self):
        self.streamer.stop_mocap_streaming()

    def get_raw_mocap(self):
        return self.streamer.get_raw_data_on_ready()

    def get_q6(self, index):
        last_imu_data = self.streamer.get_raw_data_on_ready()

        q6_data = [last_imu_data[index].q6.x, last_imu_data[index].q6.y, last_imu_data[index].q6.z, last_imu_data[index].q6.w]
        return q6_data


    def start_emg_streaming(self, buffer = 100):
        self.streamer.is_emg_buffering_enabled = True
        self.streamer.emg_buffer_size = buffer
        print('Start emg...')
        self.streamer.start_emg_streaming()
        print('Wait for buffer ready')
        self.streamer.wait_emg_buffer_ready()


    def stop_emg_streaming(self):
        print('Stop emg')
        self.streamer.stop_mocap_streaming()


    def get_current_emg_channel_data(self,node,channel):
        return self.streamer.emg_buffer.nodes[node].channels[channel].buffer


