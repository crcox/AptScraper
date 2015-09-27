import sys, pickle
from time import sleep
from gmaps import Directions

def gmap_distance(origin,destination,method=['car','walking']):
    # origin and destination should be address strings.
    api = Directions()
    if not isinstance(method, list):
        method = [method]

    dist = dict([(i, 0) for k in method])
    time = dict([(i, 0) for k in method])

    for m in method:
        d = api.directions(origin,dest,m)
        dist[m] = d[0]['legs'][0]['distance']['value']
        time[m] = d[0]['legs'][0]['duration']['value']
        sleep(0.5) # This is necessary to make less than 10 requests per second.

    return dist, time

if __name__ == '__main__':
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        dest  = sys.argv[2]
    else:
        print "Error: Wrong number of arguments."
        print "Usage: dist <listings_file.pkl> <'desination string'>"
        sys.exit(1)

    print "Warning: This will only give car and walking distances and times."
    with open(filename, 'rb') as f:
        listings = pickle.load(f)

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

    print "Overwriting {file:s} with updated destination information.".format(file=filename)
    with open(filename,'wb') as f:
        pickle.dump(listings,f)
