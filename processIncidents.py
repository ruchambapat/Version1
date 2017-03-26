import csv
import geocoder

#Saving incidents
data = []
f = open('convertcsv (10).csv','rU')
csv_f = csv.reader(f)
headers = []
headers = csv_f.next()
for i, header in enumerate(headers):
    if header == 'situationVersionTime':
        index_time=i
    if header == 'situationRecord/groupOfLocations/locationForDisplay/latitude':
        index_lat=i
    if header == 'situationRecord/groupOfLocations/locationForDisplay/longitude':
        index_long=i
    if header == 'situationRecord/_xsi:type':
        index_type=i
    if header == '_id':
        index_id=i
next(csv_f)
for row in csv_f:
        id = row[index_id]
        situation_time = row[index_time]
        latitude =  row[index_lat]
        longitude = row[index_long]
        situation_type = row[index_type]
        mydict = {latitude: longitude}
        g = geocoder.google([latitude, longitude], method='reverse')
        city = g.city
        data.append(str(id)+ ", "+ str(situation_time)+ ", "+ str(latitude)+ ", "+ str(longitude) + ", " +str(situation_type) + ", "+str(city))
with open('incidents.csv', 'w') as file:
    file.writelines("%s\n" % item for item in data)
print "Incidents file updated"