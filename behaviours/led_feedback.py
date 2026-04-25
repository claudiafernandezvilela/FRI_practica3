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
        self.last_state = None

    def _get_state(self):
        if self.params.get("qr_centered"):
            return "pushing"
        if self.params.get("objeto_cerca"):
            return "container"
        if self.params.get("obj") is not None:
            return "detected"
        return "exploring"

    def take_control(self):
        if self.supress:
            return False
        return self._get_state() != self.last_state  # solo actúa si cambia el estado

    def action(self):
        state = self._get_state()
        self.last_state = state

        if state == "exploring":
            # Azul: explorando
            self.robot.setLedColorTo(LED.All, Color.BLUE)
            print("      LEDs: explorando (azul)")

        elif state == "detected":
            # Verde: objeto detectado
            self.robot.setLedColorTo(LED.All, Color.GREEN)
            print("      LEDs: objeto detectado (verde)")

        elif state == "container":
            # Amarillo: objeto cerca, buscando contenedor
            self.robot.setLedColorTo(LED.All, Color.YELLOW)
            print("      LEDs: buscando contenedor (amarillo)")

        elif state == "pushing":
            # Rojo: empujando al contenedor
            self.robot.setLedColorTo(LED.All, Color.RED)
            print("      LEDs: empujando (rojo)")