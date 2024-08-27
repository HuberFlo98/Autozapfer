import Jetson.GPIO as GPIO
import time

Zapfhahn1 = 19
Zapfhahn2 = 21

#Magnetventil_1 = 13
Magnetventil_2 = 15
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)



#Zapfhahn
GPIO.setup(Zapfhahn1, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(Zapfhahn2, GPIO.OUT, initial=GPIO.LOW)
GPIO.output( Zapfhahn1, GPIO.HIGH)
GPIO.output( Zapfhahn2, GPIO.HIGH)

#Magnetventile
#GPIO.setup(Magnetventil_1, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Magnetventil_2, GPIO.OUT, initial=GPIO.HIGH)
#GPIO.output( Magnetventil_1, GPIO.LOW)
GPIO.output( Magnetventil_2, GPIO.HIGH)

GPIO.output( Zapfhahn2, GPIO.LOW)
time.sleep(2)
GPIO.output( Zapfhahn2, GPIO.HIGH)
time.sleep(1)





# for n in range(4):
# 	#GPIO.output( Magnetventil_2, GPIO.LOW)
# 	time.sleep(3)
# 	GPIO.output( Zapfhahn1, GPIO.HIGH)
# 	print("Zapfhahn1 an")
# 	time.sleep(3)
# 	GPIO.output( Zapfhahn1, GPIO.LOW)
# 	time.sleep(3)
# 	#GPIO.output( Magnetventil_1, GPIO.HIGH)
# 	print("Magnetventil_1 an")
# 	time.sleep(3)
# 	#GPIO.output( Magnetventil_1, GPIO.LOW)
# 	time.sleep(3)
# 	GPIO.output( Zapfhahn2, GPIO.HIGH)
# 	print("Zapfhahn2 an")
# 	time.sleep(3)
# 	GPIO.output( Zapfhahn2, GPIO.LOW)
# 	time.sleep(3)
# 	#GPIO.output( Magnetventil_2, GPIO.HIGH)
# 	print("Magnetventil_2 an")
# 	time.sleep(3)
# GPIO.cleanup()
