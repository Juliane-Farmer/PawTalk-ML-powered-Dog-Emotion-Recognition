import RPi.GPIO as GPIO

class RGB_LED:
    def __init__(self, red_pin, green_pin, blue_pin):
        self.red_pin = red_pin
        self.green_pin = green_pin
        self.blue_pin = blue_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.red_pin, GPIO.OUT)
        GPIO.setup(self.green_pin, GPIO.OUT)
        GPIO.setup(self.blue_pin, GPIO.OUT)
        self.turn_off()

    def turn_off(self):
        GPIO.output(self.red_pin, GPIO.HIGH)
        GPIO.output(self.green_pin, GPIO.HIGH)
        GPIO.output(self.blue_pin, GPIO.HIGH)

    def set_color(self, color):
        self.turn_off()
        if color == 'white':
            GPIO.output(self.red_pin, GPIO.LOW)
            GPIO.output(self.green_pin, GPIO.LOW)
            GPIO.output(self.blue_pin, GPIO.LOW)
        elif color == 'red':
            GPIO.output(self.red_pin, GPIO.LOW)
        elif color == 'green':
            GPIO.output(self.green_pin, GPIO.LOW)
        elif color == 'blue':
            GPIO.output(self.blue_pin, GPIO.LOW)

    def cleanup(self):
        self.turn_off()
        GPIO.cleanup()
        print("RGB LED program terminated.")
