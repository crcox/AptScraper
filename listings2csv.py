import csv, codecs, cStringIO, pickle

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

with open('LISTINGS.pkl','rb') as f:
    listings = pickle.load(f)
keys=['price','bed','bath','description','address','address_g','meters_car','meters_transit','seconds_car','seconds_transit','laundry','type','availability','size','nonsmoking','parking','link','latitude','longitude']
with open('listings.csv', 'wb') as f:
    writer = UnicodeWriter(f)
    writer.writerow(keys)
    for listing in listings:
        writer.writerow([unicode(listing[k]) if k in listing.keys() else '' for k in keys])
