import os
import time
from datetime import datetime

while (True):
    last_eye_close_timestamp = datetime.now()
    time.sleep(10)
    timeElapsed = (datetime.now() - last_eye_close_timestamp).seconds
    print timeElapsed
