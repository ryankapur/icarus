from actuator_pwm import Run
from solarserver import MyServer
import json 
from constants import constants as x

#instantiate websocketclient
##DEMO REAL-TIME
# now = datetime.datetime.utcnow()
# go = Run("127.0.0.1", "8080", x.maxActuatorHeight, now)

now = datetime.datetime.utcnow()
go = Run("127.0.0.1", "8080", x.maxActuatorHeight, SUNSET, sunrise)
print("client obj:", go.client)

#instantiate server, thereby the factory/listening
server = MyServer()

#connect wsclient <--> server
go.connectToServer()

#start reactor
go.reactorLoop()



