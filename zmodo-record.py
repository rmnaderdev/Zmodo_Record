import os
from signal import signal, SIGTERM, SIGHUP, SIGINT
import subprocess
import hashlib
import requests
import pathlib
import time

# Global variables
USERNAME = os.environ['USERNAME']
PASSWORD = os.environ['PASSWORD']
ROOT_FOLDER = "/zmodo_output"

# Force refresh token after 4 hours
MAX_PROC_RUNTIME_SEC = (3600 * 4)

TOKEN = None
DEVICES = None
HEADERS={"referer": "https://user.zmodo.com/", \
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"}

PROC_LIST = {}
PROC_TIMERS = {}

def current_milli_time():
    return round(time.time() * 1000)

def safe_exit(signum=None, frame=None):
    global PROC_LIST
    # Safely close ffmpeg processes
    for proc in PROC_LIST:
        device_id = proc
        process = PROC_LIST[device_id]

        os.killpg(os.getpgid(process.pid), SIGTERM)

    print("Exiting. Goodbye!")
    exit(1)

def check_API_token():
    global TOKEN
    global HEADERS
    res = requests.get("https://user.zmodo.com/api/token/{token}".format(token=TOKEN), headers=HEADERS)
    if(res.status_code == 200):
        data = res.json()

        if(data["result"] == "ok"):
            return True
        else:
            print("Token is expired")
            return False
    else:
        print("Failed to check token (non 200 code), assuming it is bad.")
        return False

def refresh_API_token():
    global USERNAME
    global PASSWORD
    global TOKEN
    global HEADERS

    password = hashlib.md5(PASSWORD.encode('utf-8')).hexdigest()

    print("Refreshing token")

    res = requests.post("https://user.zmodo.com/api/login", \
        json={"username": USERNAME, "password": password}, headers=HEADERS)

    if(res.status_code == 200):
        data = res.json()

        if(data["result"] == "ok"):
            TOKEN = data["data"]
            print("Auth success!")
        else:
            print("Auth fail. " + data["error"])
    else:
        print("Auth fail. Non 200 return code.")

def refresh_devices():
    global TOKEN
    global DEVICES
    global HEADERS

    print("Refreshing devices")
    
    res = requests.get("https://user.zmodo.com/api/devices", cookies={"tokenid": TOKEN}, headers=HEADERS)
    
    if(res.status_code == 200):
        data = res.json()

        if(data["result"] == "ok"):
            DEVICES = list(map(lambda dev: { "name": dev["name"], "id": dev["physical_id"] }, data["data"]))
            print("Got device list:")
            print(DEVICES)
        else:
            print("Error getting devices. " + data["error"])
    else:
        print("Get devices fail. Non 200 return code.")

def start_record_process(deviceName, deviceId):
    global PROC_LIST
    global ROOT_FOLDER
    global TOKEN

    # Target folder
    deviceFolder = "{rootDataFolder}/{dev_id}".format(rootDataFolder=ROOT_FOLDER, dev_id=deviceId)

    # Ensure folder for device exists
    pathlib.Path(deviceFolder).mkdir(parents=True, exist_ok=True)

    # Start recording process
    print("Starting ffmpeg for device {name} with id={id}".format(name=deviceName, id=deviceId))
    command = "ffmpeg -timeout 5000000 -hide_banner -loglevel error -i \"https://flv.meshare.com/live?devid={dev_id}&token={token}&media_type=2&channel=0&rn=1623373509644\" -c copy -an -map 0 -f segment -reset_timestamps 1 -strftime 1 -segment_time 300 -segment_format mp4 \"{folder}/{name}_%Y-%m-%d_%H-%M-%S.mp4\"".format(token=TOKEN, name=deviceName, dev_id=deviceId, folder=deviceFolder)
    print("FFMPEG Command: " + command)

    # Start process
    PROC_LIST[deviceId] = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)

    # Set process start time
    PROC_TIMERS[deviceId] = current_milli_time()

def check_processes():
    global PROC_LIST
    global DEVICES
    global MAX_PROC_RUNTIME_SEC

    hadNetworkFail = False

    for proc in PROC_LIST:
        device_id = proc
        # Find device info based on ID
        device = next((x for x in DEVICES if x["id"] == device_id), None)
        process = PROC_LIST[device_id]
        processRunTime = current_milli_time() - PROC_TIMERS[device_id]

        if(hadNetworkFail):
            break

        # Check if process is dead
        if(process.poll() != None):
            print("[" + str(process.pid) + "] Process for " + device_id + " stopped. Getting new token and restarting.")

            try:
                if(not check_API_token()):
                    refresh_API_token()
                start_record_process(device["name"], device_id)
            except requests.ConnectionError:
                print("[" + str(process.pid) + "] Process for " + device_id + " failed to call API due to a network failure. Retrying in 10 seconds.")
                hadNetworkFail = True
        else:
            # If the process has been running for over x sec
            if(processRunTime >= (1000 * MAX_PROC_RUNTIME_SEC)):
                print("[" + str(process.pid) + "] Process for " + device_id + " has expired. Stopping the process, getting new token, and restarting.")
                # Kill the process
                os.killpg(os.getpgid(process.pid), SIGINT)
                process.wait()
                print("[" + str(process.pid) + "] Process for " + device_id + " has been terminated.")
                # Refresh token
                refresh_API_token()
                # Start record process
                start_record_process(device["name"], device_id)

# Is ffmpeg installed on the system?
from shutil import which
if(which("ffmpeg") is None):
    print("ffmpeg must be installed to use this program. Please install ffmpeg and rerun this program.")
    quit()


# Setup signal handling
signal(SIGTERM, safe_exit)
signal(SIGHUP, safe_exit)

refresh_API_token()
if(TOKEN != None):
    # Get device list
    refresh_devices()

    if(DEVICES != None):
        # Start processes initially
        print("Starting ffmpeg processes")
        for device in DEVICES:
            start_record_process(device["name"], device["id"])
        
        print("Listening for proccess changes...")

        while(True):
            check_processes()
            time.sleep(10)
else:
    print("Failed to get token.")