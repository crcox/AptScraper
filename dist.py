import re,requests, sys, pickle
from time import sleep
from bs4 import BeautifulSoup
from gmaps import Geocoding, Directions

def gmap_distance(origin,destination):
    # location and destination should be address strings.
    api = Directions()

    dist = {'car':0, 'walking':0}
    time = {'car':0, 'walking':0}
    d = api.directions(origin,dest)
    dist['car'] = d[0]['legs'][0]['distance']['value']
    time['car'] = d[0]['legs'][0]['duration']['value']
    d = api.directions(origin,dest,'walking')
    dist['walking'] = d[0]['legs'][0]['distance']['value']
    time['walking'] = d[0]['legs'][0]['duration']['value']
    sleep(1) # This is necessary to make less than 10 requests per second.
    return dist, time


with open('LISTINGS.pkl', 'rb') as f:
    listings = pickle.load(f)

#dest = 'Lyles-Porter Hall, 715 Clinic Drive, West Lafayette, IN 47907'
dest = 'Milwaukee County Transit System, 1942 N 17th St, Milwaukee, WI 53205'
print 'Computing distances...'
for i, listing in enumerate(listings):
    print i
    loc = listing['address']
    if loc == '':
        loc_g = listing['address_g']
        if loc_g == '':
            continue
        else:
            ix = loc_g.find('-')
            if ix > -1:
                loc_g = loc_g[ix+1:]

            try:
                dist, time = gmap_distance(loc_g,dest)
            except:
                print 'A: ', loc_g
                raise
                continue
    else:
        try:
            dist, time = gmap_distance(loc,dest)
        except:
            print 'B: ', loc
            raise
            continue

    listings[i]['meters_car'] = dist['car']
    listings[i]['seconds_car'] = time['car']
    listings[i]['meters_walking'] = dist['walking']
    listings[i]['seconds_walking'] = time['walking']

with open('LISTINGS.pkl','wb') as f:
    pickle.dump(listings,f)
