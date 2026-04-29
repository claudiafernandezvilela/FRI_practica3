#
# Comportamiento: LedFeedback
# Cambia el color de los LEDs según el estado del robot.
#

from .behaviour import Behaviour
from robobopy.utils.LED import LED
from robobopy.utils.Color import Color

class LedFeedback(Behaviour):

    def __init__(self, robot, supress_list, params):
        super().__init__(robot, supress_list, params)

    def _get_state(self):
        if self.params.get("qr_centered"):
            return "pushing"
        if self.params.get("objeto_cerca"):
            return "container"
        if self.params.get("obj") is not None:
            return "detected"
        return "exploring"

    def take_control(self):
        return not self.supress

    def action(self):
        last_state = None

        while not self.stopped() and not self.supress:
            state = self._get_state()

            if state != last_state:
                last_state = state

                if state == "exploring":
                    self.robot.setLedColorTo(LED.All, Color.BLUE)
                    print("      LEDs: explorando (azul)")
                elif state == "detected":
                    self.robot.setLedColorTo(LED.All, Color.GREEN)
                    print("      LEDs: objeto detectado (verde)")
                elif state == "container":
                    self.robot.setLedColorTo(LED.All, Color.YELLOW)
                    print("      LEDs: buscando contenedor (amarillo)")
                elif state == "pushing":
                    self.robot.setLedColorTo(LED.All, Color.RED)
                    print("      LEDs: empujando (rojo)")

            self.robot.wait(0.1)