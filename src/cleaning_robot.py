import time

from src.display_manager import DisplayManager
from src.room import Room

DEPLOYMENT = False  # This variable is to understand whether you are deploying on the actual hardware

try:
    import RPi.GPIO as GPIO
    import board
    import IBS
    DEPLOYMENT = True
except:
    import mock.GPIO as GPIO
    import mock.board as board
    import mock.ibs as IBS


class CleaningRobot:

    RECHARGE_LED_PIN = 12
    CLEANING_SYSTEM_PIN = 13
    INFRARED_PIN = 15
    BUZZER_PIN = 36

    # Wheel motor pins
    PWMA = 16
    AIN2 = 18
    AIN1 = 22

    # Rotation motor pins
    BIN1 = 29
    BIN2 = 31
    PWMB = 32
    STBY = 33

    N = 'N'
    S = 'S'
    E = 'E'
    W = 'W'

    LEFT = 'l'
    RIGHT = 'r'
    FORWARD = 'f'

    def __init__(self, room: Room):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.INFRARED_PIN, GPIO.IN)
        GPIO.setup(self.RECHARGE_LED_PIN, GPIO.OUT)
        GPIO.setup(self.CLEANING_SYSTEM_PIN, GPIO.OUT)

        GPIO.setup(self.PWMA, GPIO.OUT)
        GPIO.setup(self.AIN2, GPIO.OUT)
        GPIO.setup(self.AIN1, GPIO.OUT)
        GPIO.setup(self.PWMB, GPIO.OUT)
        GPIO.setup(self.BIN2, GPIO.OUT)
        GPIO.setup(self.BIN1, GPIO.OUT)
        GPIO.setup(self.STBY, GPIO.OUT)

        ic2 = board.I2C()
        self.ibs = IBS.IBS(ic2)

        self.pos_x = None
        self.pos_y = None
        self.heading = None

        self.recharge_led_on = False
        self.cleaning_system_on = False

        self.room = room

        self.display_manager = DisplayManager(ic2)

    def initialize_robot(self) -> None:
        self.pos_x = 0
        self.pos_y = 0
        self.heading = 'N'

    def robot_status(self) -> str:
        return f"({self.pos_x},{self.pos_y},{self.heading})"

    def execute_command(self, command: str) -> str:
        charge_left = self.ibs.get_charge_left()

        if charge_left <= 10:
            self.__enter_low_power_mode()
            return f"!{self.robot_status()}"

        match command:
            case self.FORWARD:
                if not self.room.is_position_valid(self.__get_future_position_after_forward_movement()):
                    raise CleaningRobotError

                if self.obstacle_found():
                    self.__play_buzzer_tone()
                    return f"{self.robot_status()},{self.__get_obstacle_position_str()}"

                self.activate_wheel_motor()
                self.__compute_new_position_on_forward()
                self.display_manager.update_display_info((self.pos_x, self.pos_y, self.heading), None, self.ibs.get_charge_left())
            case self.LEFT:
                self.activate_rotation_motor(self.LEFT)
                self.__compute_new_heading_on_rotation(self.LEFT)
            case self.RIGHT:
                self.activate_rotation_motor(self.RIGHT)
                self.__compute_new_heading_on_rotation(self.RIGHT)
            case _:
                raise CleaningRobotError

    def __compute_new_position_on_forward(self) -> None:
        match self.heading:
            case self.N:
                self.pos_y += 1
            case self.S:
                self.pos_y -= 1
            case self.E:
                self.pos_x += 1
            case self.W:
                self.pos_x -= 1

    def __compute_new_heading_on_rotation(self, direction: str) -> None:
        headings = (self.N, self.E, self.S, self.W)
        new_heading = None

        match direction:
            case self.LEFT:
                new_heading = (headings.index(self.heading) - 1) % 4
            case self.RIGHT:
                new_heading = (headings.index(self.heading) + 1) % 4

        self.heading = headings[new_heading]

    def __get_future_position_after_forward_movement(self) -> tuple[int, int]:
        x = self.pos_x
        y = self.pos_y

        match self.heading:
            case self.N:
                y += 1
            case self.S:
                y -= 1
            case self.E:
                x += 1
            case self.W:
                x -= 1

        return x, y

    def __is_position_valid(self, position: tuple[int, int]) -> bool:
        x, y = position
        return x >= 0 and y >= 0

    def __get_obstacle_position(self) -> tuple[int, int]:
        # The position of the obstacle is the position that the robot
        # would have had if it had moved forward
        return self.__get_future_position_after_forward_movement()

    def __get_obstacle_position_str(self) -> str:
        x, y = self.__get_obstacle_position()
        return f"({x},{y})"

    def obstacle_found(self) -> bool:
        return GPIO.input(self.INFRARED_PIN)

    def manage_cleaning_system(self) -> None:
        if self.ibs.get_charge_left() <= 10:
            self.__enter_low_power_mode()
        else:
            self.__enter_cleaning_mode()

    def __enter_cleaning_mode(self) -> None:
        GPIO.output(self.CLEANING_SYSTEM_PIN, GPIO.HIGH)
        GPIO.output(self.RECHARGE_LED_PIN, GPIO.LOW)
        self.cleaning_system_on = True
        self.recharge_led_on = False

    def __enter_low_power_mode(self) -> None:
        GPIO.output(self.CLEANING_SYSTEM_PIN, GPIO.LOW)
        GPIO.output(self.RECHARGE_LED_PIN, GPIO.HIGH)
        self.cleaning_system_on = False
        self.recharge_led_on = True

    def __play_buzzer_tone(self) -> None:
        GPIO.output(self.BUZZER_PIN, GPIO.HIGH)
        if DEPLOYMENT:
            time.sleep(0.2)
        GPIO.output(self.BUZZER_PIN, GPIO.LOW)

    def activate_wheel_motor(self) -> None:
        """
        Let the robot move forward by activating its wheel motor
        """
        # Drive the motor clockwise
        GPIO.output(self.AIN1, GPIO.HIGH)
        GPIO.output(self.AIN2, GPIO.LOW)
        # Set the motor speed
        GPIO.output(self.PWMA, GPIO.HIGH)
        # Disable STBY
        GPIO.output(self.STBY, GPIO.HIGH)

        if DEPLOYMENT: # Sleep only if you are deploying on the actual hardware
            time.sleep(1) # Wait for the motor to actually move

        # Stop the motor
        GPIO.output(self.AIN1, GPIO.LOW)
        GPIO.output(self.AIN2, GPIO.LOW)
        GPIO.output(self.PWMA, GPIO.LOW)
        GPIO.output(self.STBY, GPIO.LOW)

    def activate_rotation_motor(self, direction) -> None:
        """
        Let the robot rotate towards a given direction
        :param direction: "l" to turn left, "r" to turn right
        """
        if direction == self.LEFT:
            GPIO.output(self.BIN1, GPIO.HIGH)
            GPIO.output(self.BIN2, GPIO.LOW)
        elif direction == self.RIGHT:
            GPIO.output(self.BIN1, GPIO.LOW)
            GPIO.output(self.BIN2, GPIO.HIGH)

        GPIO.output(self.PWMB, GPIO.HIGH)
        GPIO.output(self.STBY, GPIO.HIGH)

        if DEPLOYMENT:  # Sleep only if you are deploying on the actual hardware
            time.sleep(1)  # Wait for the motor to actually move

        # Stop the motor
        GPIO.output(self.BIN1, GPIO.LOW)
        GPIO.output(self.BIN2, GPIO.LOW)
        GPIO.output(self.PWMB, GPIO.LOW)
        GPIO.output(self.STBY, GPIO.LOW)


class CleaningRobotError(Exception):
    pass
