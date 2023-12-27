#!/usr/bin/python3

import json
import threading
import time
import inputs
import react
import reader

watchingIndices = []

class Supervisor:
    def onPlayStateChange(self, playing):
        react.onPlayStateChange(playing)

    def onClose(self, input):
        watchingIndices.remove(input.index)
        react.onPlayStateChange(False)
        print(f"Stopped watching {input}")

# Create an instance of Supervisor after the class definition
supervisorInstance = Supervisor()

def updateWatches():
    with open("config.json", "r") as f:
        config = json.load(f)

    inputsList = inputs.get()
    namesToWatch = [a["name"] for a in config["applications"] if a["role"] == "master"]
    inputsToWatch = [i for i in inputsList if i.name in namesToWatch]
    inputsToWatchNew = [i for i in inputsToWatch if i.index not in watchingIndices]

    for inputToWatch in inputsToWatchNew:
        print(f"Started watching {inputToWatch}")
        t = threading.Thread(target=reader.monitor, args=[inputToWatch, supervisorInstance])
        t.start()
        watchingIndices.append(inputToWatch.index)

    return config  # Return the config

# Main loop
while True:
    config = updateWatches()  # Get config from updateWatches function
    time.sleep(config["preferences"]["sourcesUpdateInterval"])

