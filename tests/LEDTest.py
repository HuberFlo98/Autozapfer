import Jetson.GPIO as GPIO
import time

LED2 = 23
LED1 = 13

GPIO.setmode(GPIO.BOARD)

GPIO.setup(LED2, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LED1, GPIO.OUT, initial=GPIO.LOW)

GPIO.output( LED2, GPIO.LOW)
GPIO.output( LED1, GPIO.LOW)



for n in range(10):
	time.sleep(1)
	GPIO.output( LED2, GPIO.HIGH)
	GPIO.output( LED1, GPIO.HIGH)
	print("on")
	time.sleep(600)
	# GPIO.output( LED2, GPIO.LOW)
	# GPIO.output( LED1, GPIO.LOW)
	# print("off")

GPIO.cleanup()