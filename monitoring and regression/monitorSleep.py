import publishMqtt as mqtt
import preprocess as prep
import sleepRatioLinearRegression

import time
from datetime import datetime

DAY = 86400 

# loop scipt to run every 24 hours
while(True):
    # prep the data
    prep.preprocessData()

    # run linear regression, and publish via mqtt
    # sleepRatioLinearRegression.runLinearRegression()
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    print("Last Updated: ", now)
    time.sleep(DAY)