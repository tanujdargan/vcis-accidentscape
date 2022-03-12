import wiringpi as wiringpi
from time import sleep

wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(25, 0)
count=0
while(count<20):
	my_input=wiringpi.digitalRead(25)
	if(my_input):
		print("Not Detected !")
	else:
		print("Alcohol Detected")
	count=count+1
	sleep(1)