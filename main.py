from robobopy.Robobo import Robobo
from behaviours.explore import Explore
from behaviours.detect_object import DetectObject
from behaviours.find_container import FindContainer
from behaviours.push_to_zone import PushToZone
import time

def main():
    robobo = Robobo("localhost")
    robobo.connect()
    robobo.wait(1)

    robobo.startObjectRecognition()
    robobo.wait(0.5)

    robobo.moveTiltTo(120, 60)
    robobo.wait(1)

    params = {
        "stop":            False,
        "detected_object": None,
        "objeto_cerca":    False,
        "qr_centered":     False,
        "obj":             None,
    }

    explore        = Explore(robobo, [], params)
    detect         = DetectObject(robobo, [explore], params)
    find_container = FindContainer(robobo, [explore, detect], params)
    push_to_zone   = PushToZone(robobo, [explore, detect, find_container], params)

    threads = [explore, detect, find_container, push_to_zone]
    for t in threads:
        t.start()

    while not params["stop"]:
        time.sleep(0.1)

    print("=== Misión completada. ===")

    for t in threads:
        t.join(timeout=2)

    robobo.stopMotors()
    robobo.stopObjectRecognition()
    robobo.disconnect()

if __name__ == "__main__":
    main()