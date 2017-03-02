import os
from urllib2 import urlopen, URLError, HTTPError
import gzip
import time


def dnldfile(url):

    #try:
    while True:
        f = urlopen(url)
        print "downloading " + url

        # Open our local file for writing
        with open(os.path.basename(url), "wb") as local_file:
                local_file.write(f.read())

        inGZ = gzip.GzipFile("trafficspeed.xml.gz", 'rb')
        readGZ = inGZ.read()
        inGZ.close()

        outGZ = file("trafficspeed.xml", 'wb')
        outGZ.write(readGZ)
        outGZ.close()
        time.sleep(1 * 60)
    #handle errors
   # except HTTPError, e:
    #    print "HTTP Error:", e.code, url
    #except URLError, e:
     #   print "URL Error:", e.reason, url


def main():
    # Iterate over image ranges
    for index in range(150, 151):
        url = ("http://opendata.ndw.nu/trafficspeed.xml.gz")
        dnldfile(url)

if __name__ == '__main__':
    main()