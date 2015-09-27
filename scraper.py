import re,requests, sys, pickle
from bs4 import BeautifulSoup
from gmaps import Geocoding, Directions, errors


def fetch_search_results(query=None, minAsk=None, maxAsk=None, bedrooms=None):
    search_params = {key: val for key, val in locals().items() if val is not None}
    if not search_params:
        raise ValueError("No valid keywords")
    qlist = []
    for k,v in search_params.items():
        qlist.append('='.join([k,str(v)]))

    qstring = '?' + '&'.join(qlist) + '#list'

    #base = 'https://milwaukee.craigslist.org/search/apa'
    base = 'http://milwaukee.craigslist.org/search/apa'
    print search_params
    #resp = requests.get(base, params=search_params, timeout=3)
    resp = requests.get(base+qstring, timeout=3)
    resp.raise_for_status()
    return resp.content, resp.encoding

def read_search_results():
    with open('results.html','r') as f:
        content = f.read()
    return content, 'utf-8'

def parse_source(html, encoding='utf-8'):
    parsed = BeautifulSoup(html, from_encoding=encoding)
    return parsed

def extract_listings(parsed, maxlistings=0):
    def fetch_listing(url):
        fullURL = 'http://milwaukee.craigslist.org/'+url
        resp = requests.get(fullURL)
        return resp.content, resp.encoding
    def parse_listing(html, encoding='utf-8'):
        parsed = BeautifulSoup(html, from_encoding=encoding)
        return parsed

    def scrape_coords(html_p):
        location_attrs = {'data-latitude': True, 'data-longitude': True}
        map_ = html_p.find('div', class_='viewposting')
        coords = {key: float(map_.attrs.get(key, '')) for key in location_attrs}
        return coords

    def scrape_address(html_p):
        link_gmap = html_p.find('p', class_='mapaddress').find('a')['href']
        ix = link_gmap.find('+')
        if ix == -1:
            addr = ''
        else:
            addr = link_gmap[ix+1:].replace('%3','').replace('%2E','').replace('+',' ')

        return addr

    def scrape_attributes(attrgroup):
        A = {'bed':0,'bath':0,'size':0,'furnished':False,'type':'',
                'availability':'','laundry':'','parking':'',
                'accessible':False,'nonsmoking':False,'dog':False,'cat':False}
        for a in attrgroup:
            if 'BR' in a.text:
                # Bed/Bath
                tmp = a.text.replace('BR','').replace('Ba','').split(' / ')
                A['bed'] = tmp[0]
                try:
                    A['bath'] = tmp[1]
                except IndexError:
                    A['bath'] = 0

            elif 'ft2' in a.text:
                # sq ft
                A['size'] = a.text

            elif 'furnished' in a.text:
                # furnished
                A['furnished'] = True

            elif a.text in ['apartment','condo','cottage/cabin','duplex','flat','house','in-law','loft','townhouse','manufactured','assisted living','land']:
                # housing type
                A['type'] = a.text

            elif 'available' in a.text:
                # availability
                A['availability'] = a.text

            elif a.text in ['w/d in unit','laundry in bldg','laundry on site','w/d hookups']:
                # laundry
                A['laundry'] = a.text

            elif a.text in ['carport','attached garage','detached garage','off-street parking','street parking','valet parking']:
                # parking
                A['parking'] = a.text

            elif a.text in ['wheelchair accessible']:
                # accessible
                A['accessible'] = True

            elif a.text in ['no smoking']:
                # smoking
                A['nonsmoking'] = True

            elif 'dog' in a.text:
                # dog
                A['dog'] = True

            elif 'cat' in a.text:
                #cat
                A['cat'] = True

            else:
                print 'I dont know how to handle this:', a.text

        return A

    def geolocate_address(coords):
        api_g = Geocoding() # to get address from coords
        loc = api_g.reverse(coords['data-latitude'], coords['data-longitude'])
        addr = loc[0]['formatted_address']
        return addr


    extracted = []
    # Scrape the page of results one listing at a  time.
    listings = parsed.find_all('p', class_='row')
    if maxlistings > 0:
        listings = listings[0:maxlistings]

    for listing in listings:
        link = listing.find('span', class_='pl').find('a')
        price_span = listing.find('span', class_='price')
        housing_span = unicode(listing.find('span', class_='housing'))
        m = re.search('[0-9]+br',housing_span)
        try:
            rooms = m.group()
        except AttributeError:
            rooms = 0

        m = re.search('[0-9]+ft',housing_span)
        try:
            feet = m.group()
        except AttributeError:
            feet = 0

        # Request html from listing itself, and scrape the page.
        # Get location info from map
        html, encoding = fetch_listing(link.attrs['href'])
        html_p = parse_listing(html, encoding)
        foundCoords = False
        try:
            coords = scrape_coords(html_p)
            foundCoords = True
        except:
            coords = {'data-latitude':0, 'data-longitude':0}

        try:
            addr = scrape_address(html_p)
        except:
            addr = ''

        if foundCoords:
            try:
                addr_g = geolocate_address(coords)
            except errors.GmapException:
                addr_g = ''
        else:
            addr_g = ''

        # Get property attributes
        attrgroup = html_p.find('p',class_='attrgroup').find_all('span')
        attributes = scrape_attributes(attrgroup)

        print link.attrs['href']

        this_listing = {
            'link': link.attrs['href'],
            'description': link.string.strip(),
            'price': price_span.string.strip(),
            'address': addr,
            'address_g': addr_g,
            'latitude':coords['data-latitude'],
            'longitude':coords['data-longitude']
        }
        this_listing.update(attributes)
        extracted.append(this_listing)
    return extracted

def gmap_distance(location,destination):
    # location and destination should be address strings.
    api = Directions()

    dist = {'car':0, 'transit':0}
    time = {'car':0, 'transit':0}
    d = api.directions(loc,dest)
    dist['car'] = d[0]['legs'][0]['distance']['value']
    time['car'] = d[0]['legs'][0]['duration']['value']
    d = api.directions(loc,dest,'transit')
    dist['transit'] = d[0]['legs'][0]['distance']['value']
    time['transit'] = d[0]['legs'][0]['duration']['value']
    return dist, time

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        html, encoding = read_search_results()
    else:
        html, encoding = fetch_search_results(
            #minAsk=200, maxAsk=600
            minAsk=200, maxAsk=1600, bedrooms=3
        )
    #dest = 'Lyles-Porter Hall, 715 Clinic Drive, West Lafayette, IN 47907'
    dest = '11000 West Lake Park Drive, Milwaukee Wisconsin, 53224'
    doc = parse_source(html, encoding)
    listings = extract_listings(doc)
    print 'Computing distances...'
    for i, listing in enumerate(listings):
        print i
        loc = listing['address']
        if loc:
            try:
                dist, time = gmap_distance(loc,dest)
            except:
                try:
                    loc = listing['address_g']
                    dist, time = gmap_distance(loc,dest)
                except:
                    print loc
                    continue
        else:
            loc = listing['address_g']
            try:
                dist, time = gmap_distance(loc,dest)
            except:
                print loc
                continue
        listings[i]['meters_car'] = dist['car']
        listings[i]['seconds_car'] = time['car']
        listings[i]['meters_transit'] = dist['transit']
        listings[i]['seconds_transit'] = time['transit']

    with open('LISTINGS.pkl','wb') as f:
        pickle.dump(listings,f)
