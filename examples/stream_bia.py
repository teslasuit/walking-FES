#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import _setup_sys_path

from teslasuit_sdk import ts_api


def main():
    print("Initialize API")
    api = ts_api.TsApi()
    device = api.get_device_manager().get_or_wait_last_device_attached()
    bia = device.bia

    print("Setup channels and frequencies")
    channels_indexes = [2, 3]
    bia.set_node_channels(0, channels_indexes)
    bia.set_frequencies(1000, 100000, 10000)

    print("Streaming...")
    bia.start_streaming()
    time.sleep(5)

    print("Finished")
    bia.stop_streaming()


if __name__ == '__main__':
    main()
