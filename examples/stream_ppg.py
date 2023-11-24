#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import _setup_sys_path

from teslasuit_sdk import ts_api
import teslasuit_sdk.subsystems.ts_mocap 

def main():
    print("Initialize API")
    api = ts_api.TsApi()
    device = api.get_device_manager().get_or_wait_last_device_attached()
    ppg = device.ppg

    print("Wait for ppg data...")
    ppg.start_raw_streaming()

    while True:
        data = ppg.get_hrv_data_on_ready()
        print("Mean R-R:", data.mean_rr)


if __name__ == '__main__':
    main()
