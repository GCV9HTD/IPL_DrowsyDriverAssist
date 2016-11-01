##from urllib2 import urlopen
##my_ip = urlopen('http://ip.42.pl/raw').read()
##print my_ip
from urllib2 import urlopen
from contextlib import closing
import json
import time

# Automatically geolocate the connecting IP
url = 'http://freegeoip.net/json/'
try:
    with closing(urlopen(url)) as response:
        location = json.loads(response.read())
        print(location)
        location_city = location['city']
        location_state = location['region_name']
        location_country = location['country_name']
        location_zip = location['zipcode']
except:
    print("Location could not be determined automatically")


start = time.time()

time.sleep(10)  # or do something more productive

done = time.time()
elapsed = done - start
print(elapsed)
