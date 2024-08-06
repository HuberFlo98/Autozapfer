import Jetson.GPIO as GPIO
import time

Motor1_einfahren = 31
Motor1_ausfahren = 33
Motor2_einfahren = 35
Motor2_ausfahren = 37


GPIO.setmode(GPIO.BOARD)

#Motor1

GPIO.setup(Motor1_einfahren, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Motor1_ausfahren, GPIO.OUT, initial=GPIO.LOW)

GPIO.output( Motor1_einfahren, GPIO.LOW)
GPIO.output( Motor1_ausfahren, GPIO.LOW)
#Motor2

GPIO.setup(Motor2_einfahren, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Motor2_ausfahren, GPIO.OUT, initial=GPIO.LOW)

GPIO.output( Motor2_einfahren, GPIO.LOW)
GPIO.output( Motor2_ausfahren, GPIO.LOW)


for n in range(1):
	# GPIO.output( Motor1_einfahren, GPIO.LOW)
	# GPIO.output( Motor1_ausfahren, GPIO.HIGH)
	# GPIO.output( Motor2_einfahren, GPIO.LOW)
	# GPIO.output( Motor2_ausfahren, GPIO.HIGH)
	# print("ausfahren")
	# time.sleep(1)
	GPIO.output( Motor1_einfahren, GPIO.HIGH)
	GPIO.output( Motor1_ausfahren, GPIO.LOW)
	GPIO.output( Motor2_einfahren, GPIO.HIGH)
	GPIO.output( Motor2_ausfahren, GPIO.LOW)
	print("einfahren")
	time.sleep(0.5)
GPIO.cleanup()