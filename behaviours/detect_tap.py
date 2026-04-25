from .behaviour import Behaviour

class DetectTap(Behaviour):

    def __init__(self, robot, supress_list, params):
        super().__init__(robot, supress_list, params)
        self.paused = False
        self.robot.resetTapSensor()

    def take_control(self):
        if self.supress:
            return False
        return self.robot.readTapSensor().x > 0

    def action(self):
        # Resetear y esperar a que el sensor vuelva a 0 antes de continuar
        self.robot.resetTapSensor()
        self.robot.wait(0.5)  # dar tiempo a que el dedo se levante

        if not self.paused:
            print("----> control: DetectTap → PAUSADO")
            self.paused = True
            for bh in self.supress_list:
                bh.supress = True
            self.robot.stopMotors()

            # Confirmar que el sensor está a 0 antes de escuchar el siguiente tap
            while not self.stopped():
                if self.robot.readTapSensor().x == 0:
                    break
                self.robot.resetTapSensor()
                self.robot.wait(0.1)

            self.robot.wait(0.3)  # margen extra para evitar doble lectura

            # Esperar siguiente tap para reanudar
            while not self.stopped():
                if self.robot.readTapSensor().x > 0:
                    self.robot.resetTapSensor()
                    print("----> control: DetectTap → REANUDADO")
                    self.paused = False
                    for bh in self.supress_list:
                        bh.supress = False
                    break
                self.robot.wait(0.1)