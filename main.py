from robobopy.Robobo import Robobo
from behaviours.detect_clap import DetectClap
from behaviours.avoid_wall import AvoidWall
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
        "stop":             False,
        "detected_object":  None,
        "objeto_cerca":     False,
        "qr_centered":      False,
        "obj":              None,
        "depositados":      set(),
    }

    explore        = Explore(robobo, [], params)
    avoid_wall     = AvoidWall(robobo, [explore], params)
    detect         = DetectObject(robobo, [explore, avoid_wall], params)
    find_container = FindContainer(robobo, [explore, avoid_wall, detect], params)
    push_to_zone   = PushToZone(robobo, [explore, avoid_wall, detect, find_container], params)
    detect_clap    = DetectClap(robobo, [explore, avoid_wall, detect, find_container, push_to_zone], params)

    threads = [explore, avoid_wall, detect, find_container, push_to_zone, detect_clap]

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