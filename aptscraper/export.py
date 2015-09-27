import csv, codecs, cStringIO

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

def csvfile(filename, listings, keys=[]):
    def unpackListing(listing):
        d = listing
        if "dist" in listing.keys():
            for m in listing["dist"].keys():
                k = "meters_{m:s}".format(m=m)
                d[k] = listing["dist"][m]
            del d["dist"]

        if "time" in listing.keys():
            for m in listing["time"].keys():
                k = "seconds_{m:s}".format(m=m)
                d[k] = listing["time"][m]
            del d["time"]

        return d

    if not keys:
        keys = listings[0].keys()

    with open(filename, 'wb') as f:
        writer = UnicodeWriter(f)
        writer.writerow(keys)
        for listing in listings:
            d = unpackListing(listing)
            writer.writerow(
                [unicode(d[k])
                if k in d.keys()
                else ''
                for k in keys]
            )
