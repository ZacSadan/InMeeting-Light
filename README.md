# InMeeting-Light-Notification


installation:

```
[needs python 3]
pip install yeelight
pip install -U google-api-python-client
```

Testing :

```
from yeelight import discover_bulbs
from yeelight import Bulb
discover_bulbs() # get the ip address
bulb = Bulb("10.0.0.11")
bulb.turn_on()
bulb.set_rgb(255, 105, 180)
bulb.turn_off()
```
Code:
