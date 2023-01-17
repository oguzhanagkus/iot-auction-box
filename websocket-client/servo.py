import time
import lgpio


class Servo:
    """
    This class represents a servo motor.
    It creates generates PWM signals to move arm.
    It locks and unlocks the box.
    """

    duration = 1
    handler = lgpio.gpiochip_open(0)

    def __init__(self, pin):
        self.pin = pin

    def __del__(self):
        lgpio.gpiochip_close(self.handler)

    def lock(self):
        lgpio.tx_servo(self.handler, self.pin, 1500, 50, 1, 1)
        time.sleep(self.duration)

    def unlock(self):
        lgpio.tx_servo(self.handler, self.pin, 500, 50, 1, 1)
        time.sleep(self.duration)


def test():
    try:
        servo = Servo(17)
        servo.lock()
        time.sleep(5)
        servo.unlock()
    except Exception as exception:
        print(exception)


if __name__ == "__main__":
    test()
