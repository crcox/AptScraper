import argparse
import pickle
from aptscraper import scraper, export

parser = argparse.ArgumentParser(description='Get apartment listings from Craigslist.')
#parser.add_argument('-c','--config', type=str, nargs=1,help='Path to a yaml-formated file with configuation options.')
#parser.add_argument('-g', '--gui', dest='usegui', action='store_true', help='Launch GUI to fill in options.')
parser.add_argument('-m','--min', dest='minprice', type=int, help='Minimum price.')
parser.add_argument('-M','--max', dest='maxprice', type=int, help='Maximum price.')
parser.add_argument('-r','--rooms', dest='nrooms', type=int, choices=[1,2,3,4,5], help='Number of rooms.')
parser.add_argument('-l','--landmark', dest='dest', type=str, help='Landmark to compute distances and times from each each apartment listing. Multiple words must be enclosed "in quotes".')
parser.add_argument('-m','--methods', dest='method', type=str, nargs='+', choices=["car", "walking", "transit", "biking"], help='Any or several methods of transportation for distance and time computation.')
args = parser.parse_args()

def getDistancesAndTimesToLandmark(listings, dest):
    from aptscraper import dist
    for i, listing in enumerate(listings):
        print i
        loc = listing['address']
        if loc:
            try:
                dist, time = dist.gmap_distance(loc,dest,args.method)
            except:
                try:
                    loc = listing['address_g']
                    dist, time = dist.gmap_distance(loc,dest,args.method)
                except:
                    print loc
                    continue
        else:
            loc = listing['address_g']
            try:
                dist, time = dist.gmap_distance(loc,dest,args.method)
            except:
                print loc
                continue
    
        listings[i]['dist'] = dist
        listings[i]['time'] = time
        return listings

html, encoding = scraper.fetch_search_results(
    minAsk=args.minprice, maxAsk=args.maxprice, bedrooms=args.nrooms)
doc = scraper.parse_source(html, encoding)
listings = scraper.extract_listings(doc)

if args.dest:
    destAbv = args.dest.split(',')[0]
    destAbv = "".join(destAbv.split())
    filename = "{city:s}_{br:d}br_{min:d}-{max:d}_{lm:s}.csv".format(
        city=args.city,
        br=args.nrooms,
        min=args.minprice,
        max=args.maxprice,
        lm=destAbv
    )
    print 'Computing distances...'
    listings = getDistancesAndTimesToLandmark(listings, args.dest)
else:
    filename = "{city:s}_{br:d}br_{min:d}-{max:d}.csv".format(
        city=args.city,
        br=args.nrooms,
        min=args.minprice,
        max=args.maxprice
    )
    print "No landmark provided. Returning without distances or times."
  
with open('LISTINGS.pkl','wb') as f:
    pickle.dump(listings,f)
    
keys=['price','bed','bath','description','address','address_g','meters_car','meters_transit','seconds_car','seconds_transit','laundry','type','availability','size','nonsmoking','parking','link','latitude','longitude']
export.csv(filename, listings, keys)