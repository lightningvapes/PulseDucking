import json
import subprocess
import inputs
import time

fullVolume = 65536  # 100% volume

def current_milli_time():
    return round(time.time() * 1000)

def onPlayStateChange(playing):
    with open("config.json", "r") as f:
        config = json.load(f)

    duckPercent = int(config["preferences"]["duckByPercent"]) or 60
    duckRamp = int(config["preferences"]["rampUpMs"])

    inputsList = inputs.get()

    namesToDuck = [a["name"] for a in config["applications"] if a["role"] == "slave"]
    inputsToDuck = [i for i in inputsList if i.name in namesToDuck]

    starttime = current_milli_time()
    elapsedtime = 0

    while elapsedtime < duckRamp:
        elapsedtime = current_milli_time() - starttime
        rampFraction = elapsedtime / duckRamp
        time.sleep(0.01)
        for input in inputsToDuck:
            currentVolume = int(input.volume)
            
            if playing:
                targetVolume = fullVolume * duckPercent // 100
                volume = currentVolume - (currentVolume - targetVolume) * rampFraction
            else:
                # Restore to 100% volume after ducking period is over
                volume = currentVolume + (fullVolume - currentVolume) * rampFraction

            volume = max(0, min(int(volume), fullVolume))  # Clamp volume

            # Set the volume using pacmd
            try:
                subprocess.check_output(["pacmd", "set-sink-input-volume", str(input.index), str(volume)])
            except subprocess.CalledProcessError as e:
                print(f"Error setting volume: {e}")

# Other functions or code (if any) goes here

