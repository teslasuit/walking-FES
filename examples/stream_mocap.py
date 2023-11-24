#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import _setup_sys_path

from teslasuit_sdk import ts_api
import teslasuit_sdk.subsystems.ts_mocap 
from teslasuit_sdk.ts_mapper import TsBone2dIndex

def main():
    print("Initialize API")
    api = ts_api.TsApi()
    device = api.get_device_manager().get_or_wait_last_device_attached()
    mocap = device.mocap

    print("Start streaming...")
    mocap.start_streaming()

    frames = 100
    while frames > 0:
        data = mocap.get_raw_data_on_ready()
        print("Bone data:", data[TsBone2dIndex.RightUpperArm])
        frames = frames - 1

    mocap.stop_streaming()
    print("Finished")


if __name__ == '__main__':
    main()
