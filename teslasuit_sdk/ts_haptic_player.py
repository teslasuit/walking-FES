from ctypes import *
from enum import Enum, unique
from . import ts_types

@unique
class TsHapticParamType(Enum):
    Undefined = 0
    Period = 1
    Amplitude = 2
    PulseWidth = 3
    Temperature = 4


class TsHapticParam(Structure):
    _pack_ = 1
    _fields_ = [('type', c_uint32),
                ('value', c_uint64)]


class TsHapticParamMultiplier(Structure):
    _pack_ = 1
    _fields_ = [('type', c_uint32),
                ('value', c_float)]


class TsHapticPlayer:
    """
    A player for haptic assets and instant touches. Player is binded to single device

    """
    def __init__(self, id, lib):
        self.id = id
        self.lib = lib

    def is_player_running(self):
        is_running = c_bool(False)
        self.lib.ts_haptic_is_player_running(pointer(self.id), pointer(is_running))
        return is_running.value

    def stop_player(self):
        self.lib.ts_haptic_stop_player(pointer(self.id))

    def is_player_paused(self):
        is_paused = c_bool(False)
        self.lib.ts_haptic_get_player_paused(pointer(self.id), pointer(is_paused))
        return is_paused.value
    
    def set_player_paused(self, is_paused):
        self.lib.ts_haptic_set_player_paused(pointer(self.id), c_bool(is_paused))

    def is_player_muted(self):
        is_muted = c_bool(False)
        self.lib.ts_haptic_get_player_muted(pointer(self.id), pointer(is_muted))
        return is_muted.value

    def set_player_muted(self, is_muted):
        self.lib.ts_haptic_set_player_muted(pointer(self.id), c_bool(is_muted))

    def get_player_time(self):
        player_time = c_uint64(0)
        self.lib.ts_haptic_get_player_muted(pointer(self.id), pointer(player_time))
        return player_time.value

    def get_number_of_master_multipliers(self):
        number = c_uint64(0)
        self.lib.ts_haptic_get_number_of_master_multipliers(pointer(self.id), pointer(number))
        self.number_of_master_multipliers = number.value
        return self.number_of_master_multipliers

    def get_master_multipliers(self):
        number = self.get_number_of_master_multipliers()
        self.master_multipliers = (TsHapticParamMultiplier * number)()
        self.lib.ts_haptic_get_master_multipliers(pointer(self.id), pointer(self.master_multipliers), c_uint64(number))
        return self.master_multipliers

    def set_master_multipliers(self, multipliers):
        number = self.get_number_of_master_multipliers()
        if len(multipliers) != number:
            print(f'TsHapticPlayer set_master_multiplier not valid argument: {multipliers}; expecting {number} multipliers')
            return
        self.master_multipliers = (TsHapticParamMultiplier * number)(*multipliers)
        self.lib.ts_haptic_set_master_multipliers(pointer(self.id), pointer(self.master_multipliers), c_uint64(number))

    def get_master_multiplier(self, type):
        multipliers = self.get_master_multipliers()
        for m in multipliers:
            if m.type == type.value:
                return m
        print(f'TsHapticPlayer get_master_multiplier failed to find multiplier of type: {type}')
        return TsHapticParamMultiplier(0, 0)

    def set_master_multiplier(self, multiplier):
        multipliers = self.get_master_multipliers()
        for m in multipliers:
            if m.type == multiplier.type:
                m.value = multiplier.value
                self.set_master_multipliers(multipliers)
                return
        print(f'TsHapticPlayer set_master_multiplier failed to find multiplier of type: {type}')

    def create_playable(self, asset_id, is_looped):
        playable_id = c_uint64(0)
        self.lib.ts_haptic_create_playable_from_asset(pointer(self.id), pointer(asset_id), c_bool(is_looped), pointer(playable_id))
        return playable_id

    def is_playable_exists(self, playable_id):
        is_exists = c_bool(False)
        self.lib.ts_haptic_is_playable_exists(pointer(self.id), c_uint64(playable_id), pointer(is_exists))
        return bool(is_exists)

    def play_playable(self, playable_id):
        self.lib.ts_haptic_play_playable(pointer(self.id), c_uint64(playable_id))

    def play_touch(self, params, channel_ids, duration):
        self.lib.ts_haptic_play_touch(pointer(self.id), (TsHapticParam * len(params))(*params), len(params), \
            (ts_types.TsUuid * len(channel_ids))(*channel_ids), len(channel_ids), c_uint64(duration))

    def create_touch(self, params, channel_ids, duration):
        playable_id = c_uint64(0)
        self.lib.ts_haptic_create_touch(pointer(self.id), (TsHapticParam * len(params))(*params), len(params), \
            (ts_types.TsUuid * len(channel_ids))(*channel_ids), len(channel_ids), c_uint64(duration), pointer(playable_id))
        return playable_id

    def is_playable_playing(self, playable_id):
        is_playing = c_bool(False)
        self.lib.ts_haptic_is_playable_playing(pointer(self.id), c_uint64(playable_id), pointer(is_playing))
        return bool(is_playing)

    def stop_playable(self, playable_id):
        self.lib.ts_haptic_stop_playable(pointer(self.id), c_uint64(playable_id))

    def remove_playable(self, playable_id):
        self.lib.ts_haptic_remove_playable(pointer(self.id), c_uint64(playable_id))

    def get_playable_paused(self, playable_id):
        is_paused = c_bool(False)
        self.lib.ts_haptic_get_playable_paused(pointer(self.id), c_uint64(playable_id), pointer(is_paused))
        return bool(is_paused)

    def set_playable_paused(self, playable_id, is_paused):
        self.lib.ts_haptic_set_playable_paused(pointer(self.id), c_uint64(playable_id), c_bool(is_paused))

    def get_playable_muted(self, playable_id):
        is_muted = c_bool(False)
        self.lib.ts_haptic_get_playable_muted(pointer(self.id), c_uint64(playable_id), pointer(is_muted))
        return bool(is_muted)

    def set_playable_muted(self, playable_id, is_muted):
        self.lib.ts_haptic_set_playable_muted(pointer(self.id), c_uint64(playable_id), c_bool(is_muted))

    def get_playable_looped(self, playable_id):
        is_looped = c_bool(False)
        self.lib.ts_haptic_get_playable_looped(pointer(self.id), c_uint64(playable_id), pointer(is_looped))
        return bool(is_looped)

    def set_playable_looped(self, playable_id, is_looped):
        self.lib.ts_haptic_set_playable_looped(pointer(self.id), c_uint64(playable_id), c_bool(is_looped))

    def get_number_of_playable_multipliers(self, playable_id):
        number = c_uint64(0)
        self.lib.ts_haptic_get_number_of_playable_multipliers(pointer(self.id), c_uint64(playable_id), pointer(number))
        return number

    def get_playable_multipliers(self, playable_id):
        number = self.get_number_of_playable_multipliers(playable_id)
        multipliers = (TsHapticParamMultiplier * number)()
        self.lib.ts_haptic_get_playable_multipliers(pointer(self.id), c_uint64(playable_id), pointer(multipliers), c_uint64(number))
        return multipliers

    def set_playable_multipliers(self, playable_id, multipliers):
        number = self.get_number_of_playable_multipliers(playable_id)
        if len(multipliers) != number:
            print(f'TsHapticPlayer set_playable_multipliers not valid argument: {multipliers}; expecting {number} multipliers')
            return
        playable_multipliers = (TsHapticParamMultiplier * number)(*multipliers)
        self.lib.ts_haptic_set_playable_multipliers(pointer(self.id), c_uint64(playable_id), pointer(playable_multipliers), c_uint64(number))

    def get_playable_local_time(self, playable_id):
        local_time = c_uint64(0)
        self.lib.ts_haptic_get_playable_local_time(pointer(self.id), c_uint64(playable_id), pointer(local_time))
        return int(local_time)

    def set_playable_local_time(self, playable_id, local_time):
        self.lib.ts_haptic_set_playable_local_time(pointer(self.id), c_uint64(playable_id), c_uint64(local_time))

    def get_playable_duration(self, playable_id):
        duration = c_uint64(0)
        self.lib.ts_haptic_get_playable_duration(pointer(self.id), c_uint64(playable_id), pointer(duration))
        return int(duration)

    def clear_all_playables():
        self.lib.ts_haptic_clear_all_playables(pointer(self.id))

    def add_channel_to_dynamic_playable(self, channel_id, playable_id):
        self.lib.ts_haptic_add_channel_to_dynamic_playable(pointer(self.id), pointer(channel_id), c_uint64(playable_id))

    def remove_channel_from_dynamic_playable(self, channel_id, playable_id):
        self.lib.ts_haptic_remove_channel_from_dynamic_playable(pointer(self.id), pointer(channel_id), c_uint64(playable_id))

    def set_material_channel_impact(self, channel_id, impact, playable_id):
        self.lib.ts_haptic_set_material_channel_impact(pointer(self.id), pointer(channel_id), c_float(impact), c_uint64(playable_id))
    