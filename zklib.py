
import hashlib
import time
import logging
import requests
import traceback
import pyttsx3
from zk import ZK

# Initialize the TTS engine
tts_engine = pyttsx3.init()

# Function to play a success sound
def play_success_sound():
    tts_engine.say("Device connected successfully")
    tts_engine.runAndWait()

# Function to play an error sound
def play_error_sound():
    tts_engine.say("Error: Device disconnected or connection failed")
    tts_engine.runAndWait()

def reconnect_machine():
    zk = ZK("192.168.1.201", port=4370, timeout=60)
    return zk.connect()

def generate_hash(log):
    data = f"{log.user_id}_{log.timestamp}_{log.status}_{log.punch}_{log.uid}"
    return hashlib.sha256(data.encode()).hexdigest()

def load_saved_hashes(filename="punches_with_sms_sent.txt"):
    try:
        with open(filename, "r") as file:
            return set(file.read().splitlines())
    except FileNotFoundError:
        return set()

def save_hash(hash_value, filename="punches_with_sms_sent.txt"):
    with open(filename, "a") as file:
        file.write(hash_value + "\n")

def send_data_to_server(log):
    log_data = {
        "user_id": log.user_id,
        "date": str(log.timestamp.date()),
        "time": str(log.timestamp.time()),
        "status": log.status,
        "punch": log.punch,
        "uid": log.uid,
        "hash": generate_hash(log)
    }

    saved_hashes = load_saved_hashes()

    if log_data['hash'] in saved_hashes:
        print(f"Skipping duplicate entry for: {log_data['user_id']} {log_data['date']}")
        return True

    api_url = "http://localhost:8080/"
    
    try:
        response = requests.post(api_url, json=log_data)
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get("status") == "duplicate":
                print(f"Duplicate entry for: {log_data['user_id']} {log_data['date']}, skipping.")
            else:
                print(f"Data sent to server successfully: {log_data}")
                save_hash(log_data['hash'])
        else:
            print(f"Failed to send data to server: {log_data}")
            print(f"Server response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        logging.error(f"Exception occurred while sending data to server: {str(e)}")
        print(f"Exception occurred while sending data to server: {str(e)}")
        return False

def fetch_attendance_and_process_logs(conn):
    print("--- Fetching Attendance Logs ---")
    logs = conn.get_attendance()

    saved_hashes = load_saved_hashes()

    for log in logs:
        log_hash = generate_hash(log)
        if log_hash not in saved_hashes:
            if send_data_to_server(log):
                print(f"Data sent to server for: {log.user_id}")
            else:
                print(f"Failed to send data to server for: {log.user_id}")
        else:
            print(f"Skipping duplicate entry for: {log.user_id}")

    print("Enabling device ...")
    conn.enable_device()
    interval = 10 + int(time.time()) % 30
    print(f"Waiting for {interval} seconds...")
    time.sleep(interval)

if __name__ == "__main__":
    conn = None
    zk = reconnect_machine()

    logging.basicConfig(
        filename="attendance_script.log",
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    try:
        print("Connecting to device ...")
        conn = zk.connect()
        print("Disabling device ...")
        conn.disable_device()
        print("Firmware Version: {}".format(conn.get_firmware_version()))
        fetch_attendance_and_process_logs(conn)
    except KeyboardInterrupt:
        print("Script terminated by user.")
        logging.info("Script terminated by user.")
    except Exception as e:
        error_message = f"Process terminated: {e}"
        print(error_message)
        logging.error(error_message)
        traceback.print_exc()
    finally:
        if conn:
            try:
                conn.disconnect()
                print("Disconnected successfully.")
            except Exception as disconnect_error:
                print(f"Error disconnecting: {disconnect_error}")
