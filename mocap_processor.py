from suit_handler import Teslasuit
import numpy as np
from ctypes import *
import time
import torch
from scipy.spatial.transform import Rotation as R

from teslasuit_sdk.ts_mapper import TsBone2dIndex

# from torch import load
# from torch import FloatTensor as FT


class MocapStreamer():
    def __init__(self,suit):  
        self.ts=suit
        self.ts.connect_suit()
        # self.connected_suit = c_ulonglong(self.ts.get_connected_suit_ids()[0])
        # self.connected_suit =0
        # self.version=self.ts.get_version()
        # print(self.version._fields_)
        # print(self.ts.is_more_than_454_version())
        # print(self.version)
        # self.data = self.ts.get_mocap_data_bufferized()
        self.mocap_dict={}

        # if self.ts.is_more_than_454_version():
        self.model = torch.load('models/model.pt') 
        #     print('it is 4.5.5')
        # else:
        #     self.model = torch.load('models/model454.pt') 
        #     print('it is 4.5.4')

        # self.connected_suits = self.ts.get_connected_suit_ids()
        # self.ts.mocap_stop()
        # time.sleep(1)
        # self.ts.mocap_start(live_export=False)
        # self.model.eval()
        # if self.ts.is_more_than_454_version():
        #     self.node_index_min=6
        #     self.node_index_max=14
        # else:

        self.ts.start_mocap_streaming(1)
        self.node_index_min=1
        self.node_index_max=6
        self.nodes_list=[9,7,2,4,6,1,3,5]
        self.icm_indexes=np.arange(self.node_index_min,self.node_index_max)
        self.names = ['q6w', 'q6x', 'q6y', 'q6z',
                        'q9w', 'q9x', 'q9y', 'q9z',
                        'gx', 'gy', 'gz',
                        'ax','ay', 'az', 
                        'mx', 'my', 'mz',
                        'lx', 'ly', 'lz', 
                        'mn']
        self.paused = False


        self.modelbuffer = [0,0,0,0]

    def update(self):
        for icm in self.nodes_list:
            self.mocap_dict['gx'+'_'+str(icm)]=[]
            self.mocap_dict['gy'+'_'+str(icm)]=[]
            self.mocap_dict['gz'+'_'+str(icm)]=[]
            self.mocap_dict['ax'+'_'+str(icm)]=[]
            self.mocap_dict['ay'+'_'+str(icm)]=[]
            self.mocap_dict['az'+'_'+str(icm)]=[]
        self.data = self.ts.get_raw_mocap()
        for i in range(30):
            for icm in self.nodes_list:
                node_offset = icm * 1
                # for i in range(0,len(self.names)):
                self.mocap_dict['gx'+'_'+str(icm)].append(self.data[icm].gyro.x)
                self.mocap_dict['gy'+'_'+str(icm)].append(self.data[icm].gyro.y)
                self.mocap_dict['gz'+'_'+str(icm)].append(self.data[icm].gyro.z)
                self.mocap_dict['ax'+'_'+str(icm)].append(self.data[icm].accel.x)
                self.mocap_dict['ay'+'_'+str(icm)].append(self.data[icm].accel.y)
                self.mocap_dict['az'+'_'+str(icm)].append(self.data[icm].accel.z)
                # self.mocap_dict[self.names[i]+'_'+str(icm)]=self.data[icm].q6.w
                # self.mocap_dict[self.names[i]+'_'+str(icm)]=self.data[icm].q6.w
        # print(self.mocap_dict)


    def get_q6(self, index):
        self.update()
        # print(self.mocap_dict['q6x_'+str(index)])
        self.q6_data = [float(self.mocap_dict['q6x_'+str(index)][-1]), 
                        float(self.mocap_dict['q6y_'+str(index)][-1]),
                        float(self.mocap_dict['q6z_'+str(index)][-1]), 
                        float(self.mocap_dict['q6w_'+str(index)][-1])]
        return self.q6_data


    def get_features(self):

        def Normalize(features):

            mean = [
                4182.4042408231035,
                30.750189688649577,
                4208.148674918781,
                33.4070053753536,
                4391.742931746948,
                67.47317197442595,
                4359.720041048919,
                75.73250199289733,
                5031.490123148541,
                72.50770861438187,
                4432.243293026015,
                69.90705518256058,
                4297.27886536319,
                75.05356585026453,
                4937.5096534512995,
                75.31172725254183
            ]
            std = [
                912.7534056875603,
                27.307908652254074,
                962.5624529229248,
                31.71503030346569,
                1542.0626972532596,
                229.79301006113764,
                1159.7576578976025,
                189.96015282616946,
                2542.129651436191,
                199.95436492936332,
                1534.2638088811416,
                187.61541956983507,
                1156.8448023162816,
                143.23543756269459,
                2818.2853499899675,
                168.62266432818762
            ]
            return (np.asarray(self.features) - np.asarray(mean)) / np.asarray(std)

        def Normalize_old(features):

            mean = [
                4182.4042408231035,
                30.750189688649577,
                4208.148674918781,
                33.4070053753536,
                4391.742931746948,
                67.47317197442595,
                4359.720041048919,
                75.73250199289733,
                # 5031.490123148541,
                # 72.50770861438187,
                4432.243293026015,
                69.90705518256058,
                4297.27886536319,
                75.05356585026453,
                # 4937.5096534512995,
                # 75.31172725254183
            ]
            std = [
                912.7534056875603,
                27.307908652254074,
                962.5624529229248,
                31.71503030346569,
                1542.0626972532596,
                229.79301006113764,
                1159.7576578976025,
                189.96015282616946,
                # 2542.129651436191,
                # 199.95436492936332,
                1534.2638088811416,
                187.61541956983507,
                1156.8448023162816,
                143.23543756269459,
                # 2818.2853499899675,
                # 168.62266432818762
            ]
            return (np.asarray(self.features) - np.asarray(mean)) / np.asarray(std)

        self.features =np.empty(30)

        for i in self.nodes_list:
            raw_acc = np.array(
                [
                    self.mocap_dict[self.names[11]+'_'+str(i)],
                    self.mocap_dict[self.names[12]+'_'+str(i)],
                    self.mocap_dict[self.names[13]+'_'+str(i)],
                ]
            ).transpose()
            
            gyro = np.array(
                [
                    self.mocap_dict[self.names[8]+'_'+str(i)],
                    self.mocap_dict[self.names[9]+'_'+str(i)],
                    self.mocap_dict[self.names[10]+'_'+str(i)]
                ]
            ).transpose()
            
            norm_acc = []
            norm_gyro = []
            
            for k in range(len(raw_acc)):
                norm_acc.append(np.linalg.norm(raw_acc[k]))
                
            for k in range(len(gyro)):
                norm_gyro.append(np.linalg.norm(gyro[k]))
                    
            self.features = np.vstack((self.features, norm_acc))
            self.features = np.vstack((self.features, norm_gyro))
        self.features = self.features[1:].transpose()
        self.X = Normalize(self.features)
    



    def run_model(self):
        self.X = torch.FloatTensor(self.X)
        self.X = self.X.unsqueeze(0)
        self.out = self.model(self.X)
        self.features = np.zeros(30)
        self.modelbuffer.pop(0)
        self.modelbuffer.append((self.out.detach().numpy()[0])*1)
        print(np.mean(self.modelbuffer,axis=0)>0.6)
        return np.mean(self.modelbuffer,axis=0) >0.6

# suit=Teslasuit()
# streamer=MocapStreamer(suit)
# for i in range(100):
#     streamer.update()
#     streamer.get_features()
#     streamer.run_model()