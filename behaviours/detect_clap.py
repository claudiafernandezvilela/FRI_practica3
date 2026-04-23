#
# Comportamiento: DetectClap
# Un aplauso pausa el robot, otro aplauso lo reanuda.
# NOTA: Solo funciona con el robot real, no en el simulador.
#

from .behaviour import Behaviour

class DetectClap(Behaviour):

    def __init__(self, robot, supress_list, params):
        super().__init__(robot, supress_list, params)
        self.paused = False
        self.robot.resetClapCounter()

    def take_control(self):
        if self.supress:
            return False
        return self.robot.readClapCounter() > 0

    def action(self):
        self.robot.resetClapCounter()

        if not self.paused:
            print("----> control: DetectClap → PAUSADO")
            self.paused = True
            for bh in self.supress_list:
                bh.supress = True
            self.robot.stopMotors()

            # Esperar siguiente aplauso
            while not self.stopped():
                if self.robot.readClapCounter() > 0:
                    self.robot.resetClapCounter()
                    print("----> control: DetectClap → REANUDADO")
                    self.paused = False
                    for bh in self.supress_list:
                        bh.supress = False
                    break
                self.robot.wait(0.1)