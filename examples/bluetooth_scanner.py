#!/usr/bin/env python
from bt_proximity import BluetoothRSSI
import datetime
import time
import threading
import sys

# List of bluetooth addresses to scan
BT_ADDR_LIST = ['B8:27:EB:D2:06:F5', 'D4:9D:C0:7F:B4:7D', '28:8F:F6:DF:A8:58', 'B8:27:EB:64:D2:16']
DAILY = True  # Set to True to invoke callback only once per day per address
DEBUG = True  # Set to True to print out debug messages
THRESHOLD = (-10, 10)
SLEEP = 1


def dummy_callback():
    pass

def average(lst):
    return sum(lst) / len(lst)

def bluetooth_listen(
        addr, threshold, callback, sleep=1, daily=True, debug=False):
    """Scans for RSSI value of bluetooth address in a loop. When the value is
    within the threshold, calls the callback function.

    @param: addr: Bluetooth address
    @type: addr: str

    @param: threshold: Tuple of integer values (low, high), e.g. (-10, 10)
    @type: threshold: tuple

    @param: callback: Callback function to invoke when RSSI value is within
                      the threshold
    @type: callback: function

    @param: sleep: Number of seconds to wait between measuring RSSI
    @type: sleep: int

    @param: daily: Set to True to invoke callback only once per day
    @type: daily: bool

    @param: debug: Set to True to print out debug messages and does not 
                   actually sleep until tomorrow if `daily` is True.
    @type: debug: bool
    """
    datapoints = {}
    for i in range (0, len(BT_ADDR_LIST)):
        datapoints[BT_ADDR_LIST[i]] = []

    b = BluetoothRSSI(addr=addr)
    while True:
        rssi = b.request_rssi()
        dst = 10 **((-69 - rssi[0]) /(10 *2))
        datapoints[addr].append(dst)

        print(dst)

        if debug:
            print("addr: {}, rssi: {}".format(addr, rssi))

        # Sleep and then skip to next iteration if device not found
        if rssi is None:
            time.sleep(sleep)
            continue


def start_thread(addr, callback, threshold=THRESHOLD, sleep=SLEEP,
                 daily=DAILY, debug=DEBUG):
    """Helper function that creates and starts a thread to listen for the
    bluetooth address.

    @param: addr: Bluetooth address
    @type: addr: str

    @param: callback: Function to call when RSSI is within threshold
    @param: callback: function

    @param: threshold: Tuple of the high/low RSSI value to trigger callback
    @type: threshold: tuple of int

    @param: sleep: Time in seconds between RSSI scans
    @type: sleep: int or float

    @param: daily: Daily flag to pass to `bluetooth_listen` function
    @type: daily: bool

    @param: debug: Debug flag to pass to `bluetooth_listen` function
    @type: debug: bool

    @return: Python thread object
    @rtype: threading.Thread
    """
    thread = threading.Thread(
        target=bluetooth_listen,
        args=(),
        kwargs={
            'addr': addr,
            'threshold': threshold,
            'callback': callback,
            'sleep': sleep,
            'daily': daily,
            'debug': debug
        }
    )
    # Daemonize
    thread.daemon = True
    # Start the thread
    thread.start()
    return thread


def main():
    if not BT_ADDR_LIST:
        print("Please edit this file and set BT_ADDR_LIST variable")
        sys.exit(1)
    threads = []
    for addr in BT_ADDR_LIST:
        th = start_thread(addr=addr, callback=dummy_callback)
        threads.append(th)
    while True:
        # Keep main thread alive
        time.sleep(1)


if __name__ == '__main__':
    main()
