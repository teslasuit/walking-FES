import time
from ctypes import *



class TSHapticMasterMultiplier(Structure):
    _fields_ = [('frequency', c_float),
                ('amplitude', c_float),
                ('pulse_width', c_float),
                ('temperature', c_float)]

class Fes_streamer():
    def __init__(self,assets,haptic):
        self.haptic=haptic
        self.Left_haptic_state = 0
        self.Right_haptic_state = 0
        self.asset_id_list = assets
        self.L_animation = 'No'
        self.R_animation = 'No'

        self.legstate={}
        self.legstate['right']=0
        self.legstate['left']=0

        self.left_haptic_checked={}
        self.right_haptic_checked={}
        self.right_haptic_checked['Right_gastrocnemius']=0
        self.right_haptic_checked['Right_hamstring']=0
        self.right_haptic_checked['Right_quadriceps']=0
        self.right_haptic_checked['Right_tibialis']=0
        self.left_haptic_checked['Left_gastrocnemius']=0
        self.left_haptic_checked['Left_hamstring']=0
        self.left_haptic_checked['Left_quadriceps']=0
        self.left_haptic_checked['Left_tibialis']=0

        self.haptic_playing={}
        self.haptic_playing['Right_gastrocnemius']=0
        self.haptic_playing['Right_hamstring']=0
        self.haptic_playing['Right_quadriceps']=0
        self.haptic_playing['Right_tibialis']=0
        self.haptic_playing['Left_gastrocnemius']=0
        self.haptic_playing['Left_hamstring']=0
        self.haptic_playing['Left_quadriceps']=0
        self.haptic_playing['Left_tibialis']=0

        self.haptic_timers={}
        self.haptic_timers['Right_gastrocnemius']=0
        self.haptic_timers['Right_hamstring']=0
        self.haptic_timers['Right_quadriceps']=0
        self.haptic_timers['Right_tibialis']=0
        self.haptic_timers['Left_gastrocnemius']=0
        self.haptic_timers['Left_hamstring']=0
        self.haptic_timers['Left_quadriceps']=0
        self.haptic_timers['Left_tibialis']=0

        self.haptic_delay={}
        self.haptic_delay['Right_gastrocnemius']=0.1
        self.haptic_delay['Right_hamstring']=0.4
        self.haptic_delay['Right_quadriceps']=0.1
        self.haptic_delay['Right_tibialis']=0.0
        self.haptic_delay['Left_gastrocnemius']=0.1
        self.haptic_delay['Left_hamstring']=0.4
        self.haptic_delay['Left_quadriceps']=0.1
        self.haptic_delay['Left_tibialis']=0.0

        self.haptic_len={}
        self.haptic_len['Right_gastrocnemius']=0.3
        self.haptic_len['Right_hamstring']=0.2
        self.haptic_len['Right_quadriceps']=0.4
        self.haptic_len['Right_tibialis']=1
        self.haptic_len['Left_gastrocnemius']=0.3
        self.haptic_len['Left_tibialis']=1
        self.haptic_len['Left_quadriceps']=0.4
        self.haptic_len['Left_hamstring']=0.2


    
    def play_callback(opaque):
        return 0

    # def load_asset(self, asset_path, asset_name):
    #     # def get_haptic_asset_bin(asset):
    #     #     return open(asset, "rb").read()
    #     # asset_bin = get_haptic_asset_bin(asset_path)
    #     # asset_id = c_ulonglong()
    #     # self.teslasuit_api_dll.ts_haptic_load_asset(
    #     #     asset_bin,
    #     #     len(asset_bin),
    #     #     True, #is_static
    #     #     True, #is_looped 
    #     #     0,    #layer_index
    #     #     pointer(asset_id))
    #     self.get_playable
    #     self.asset_id_list[asset_name] = asset_id
        
    def play_R_Sw(self):
        self.R_animation = 'Swing'
        for muscle in ['Right_quadriceps','Right_tibialis','Right_hamstring']:
            if self.right_haptic_checked[muscle]==1:
                # self.teslasuit_api_dll.ts_haptic_play_by_id_async(self.suit_id, self.asset_id_list[muscle], self.play_callback())
                self.haptic_timers[muscle]=time.time()
    def play_R_St(self):
        self.R_animation = 'Stance'
        for muscle in ['Right_gastrocnemius']:
            if self.right_haptic_checked[muscle]==1:
                # self.teslasuit_api_dll.ts_haptic_play_by_id_async(self.suit_id, self.asset_id_list[muscle], self.play_callback())
                self.haptic_timers[muscle]=time.time()

    def play_L_Sw(self):
        self.L_animation = 'Swing'
        for muscle in ['Left_quadriceps','Left_tibialis','Left_hamstring']:
            if self.left_haptic_checked[muscle]==1:
                # self.teslasuit_api_dll.ts_haptic_play_by_id_async(self.suit_id, self.asset_id_list[muscle], self.play_callback())
                self.haptic_timers[muscle]=time.time()
    def play_L_St(self):
        self.L_animation = 'Stance'
        for muscle in ['Left_gastrocnemius']:
            if self.left_haptic_checked[muscle]==1:
                # self.teslasuit_api_dll.ts_haptic_play_by_id_async(self.suit_id, self.asset_id_list[muscle], self.play_callback())
                self.haptic_timers[muscle]=time.time()
        
    def end_All_assets(self):
            # self.teslasuit_api_dll.ts_haptic_stop(self.suit_id)
            self.L_animation = 'No'
            self.R_animation = 'No'
            for muscle in self.haptic_timers:
                self.haptic_timers[muscle]=0
                self.haptic_playing[muscle]=0
                self.haptic.stop_player()

    def _update_playing_assets(self):
        now=time.time()
        for muscle in self.haptic_playing:
            if (now-self.haptic_timers[muscle]-self.haptic_delay[muscle])<=self.haptic_len[muscle] and (now-self.haptic_timers[muscle]-self.haptic_delay[muscle])>0:
                self.haptic_playing[muscle]=1
            else:
                self.haptic_playing[muscle]=0
        # return self.haptic_playing

    def _update_playing(self,haptic):
        for muscle in self.haptic_playing:
            if self.haptic_playing[muscle]==1:

                haptic.play_playable(self.asset_id_list[muscle])


        
    def run_walking_fes(self,result):

        if result[1] == 0:
            L_state = 'Swing'
        else:
            L_state = 'Stance'
        if result[3] == 0:
            R_state = 'Swing'
        else:
            R_state = 'Stance'

        if L_state == 'Swing':
            if R_state == 'Stance':
                if self.L_animation == 'Stance' or self.L_animation == 'No':
                    self.play_L_Sw()
                if self.R_animation == 'Swing' or self.R_animation == 'No':
                    self.play_R_St()

            if R_state == 'Swing':
                if self.L_animation == 'Stance' or self.L_animation == 'No': 
                    self.play_L_Sw()
                if self.R_animation == 'Stance' or self.R_animation == 'No':
                    self.play_R_Sw()
            
        if L_state == 'Stance':
            if R_state == 'Stance':
                if not self.L_animation == 'No':
                    self.end_All_assets()

            if R_state == 'Swing':
                if self.L_animation == 'Swing' or self.L_animation == 'No':
                    self.play_L_St()
                if self.R_animation == 'Stance' or self.R_animation == 'No':
                    self.play_R_Sw()


    def ChangeLegState(self,side,state):
        if state == 2:
            print(side,' ON')
            self.legstate[side]=1
        else:
            self.legstate[side]=0

    def ChangeHapticChecked(self,side,muscle,state):
        if side == 'left':
            if state == 0:
                self.left_haptic_checked[muscle]=0
                print(side,muscle,' OFF')
            else:
                self.left_haptic_checked[muscle]=1
                print(side,muscle,' ON')
        else:
            if state == 0:
                self.right_haptic_checked[muscle]=0
                print(side,muscle,' OFF')
            else:
                self.right_haptic_checked[muscle]=1
                print(side,muscle,' ON')
    