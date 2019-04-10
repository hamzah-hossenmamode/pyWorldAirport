import urllib.request
import json
import math

class AirportLocation:
    def __init__(self,name,lon,lat):
        self.name = name
        self.lon = lon
        self.lat = lat
    def Distance(self,lon,lat):
        dLon = self.lon - lon
        dLat = self.lat - lat
        self.distance = math.sqrt(dLon * dLon + dLat * dLat)

class WorldAircraftQuery:
    queryHead = 'https://mikerhodes.cloudant.com/airportdb/_design/view1/_search/geo?q=lon:[{}%20TO%20{}]%20AND%20lat:[{}%20TO%20{}]'
    querySort = '&sort="<distance,lon,lat,{},{},km>"'
    queryTail = '&bookmark={}'
    def __init__(self, localSort=True):
        self.queryValue = ''
        self.airports = []
        self.localSort = localSort
    def ShowHead(self):
        print('World Of Airport Query Program')
        print('Please input the starting and ending longitudes and latitudes when prompted')
    def GetInput(self):
        try:
            lon1 = float(input('Enter starting longitude : '))
            lon2 = float(input('Enter ending longitude   : '))
            lat1 = float(input('Enter starting latitude  : '))
            lat2 = float(input('Enter ending latitude    : '))
            lonMin = '{:.2f}'.format(min(lon1,lon2))
            lonMax = '{:.2f}'.format(max(lon1,lon2))
            latMin = '{:.2f}'.format(min(lat1,lat2))
            latMax = '{:.2f}'.format(max(lat1,lat2))
            self.lonCentre = (lon1 + lon2) / 2
            self.latCentre = (lat1 + lat2) / 2
            self.queryValue = WorldAircraftQuery.queryHead.format(lonMin,lonMax,latMin,latMax)
        except:
            return True
        return False
    def ShowError(self,error):
        print('Error: {}'.format(error))
    def Process(self):
        try:
            bookmark = ''
            cumulativeRows = 0
            while True:
                fullQuery = self.queryValue
                if not self.localSort:
                    fullQuery+=WorldAircraftQuery.querySort.format(str(self.lonCentre),str(self.latCentre))
                if bookmark != '':
                    fullQuery+=WorldAircraftQuery.queryTail.format(bookmark)
                with urllib.request.urlopen(fullQuery) as response:
                    responseValue = response.read()
                    results = json.loads(responseValue)
                    bookmark = results['bookmark']
                    allRows = results['total_rows']
                    availableRows = len(results['rows'])
                    for rowIndex in range(availableRows):
                        cumulativeRows+=1
                        row = results['rows'][rowIndex]
                        fields = row['fields']
                        order = row['order'][0]
                        airport = AirportLocation(fields['name'],fields['lon'],fields['lat'])
                        if self.localSort:
                            airport.Distance(self.lonCentre,self.latCentre)
                        else:
                            airport.distance = order
                        self.airports.append((airport.distance,airport))
                if allRows == cumulativeRows:
                    break
            if self.localSort:
                self.airports.sort(key=lambda tup: tup[0])
        except:
            return True
        return False

    def ShowResult(self):
        try:
            print('')
            tableView = '{:5} {:30} {:10} {:10} {:10}'
            print('From Centre Longitude: {:.2f}, Latitude: {:.2f}'.format(self.lonCentre,self.latCentre))
            print(tableView.format('Order','Airport','Distance','Longitude','Latitude',))
            for airportIndex in range(len(self.airports)):
                distance = self.airports[airportIndex][0]
                airport = self.airports[airportIndex][1]
                print(tableView.format(str(airportIndex + 1),airport.name,'{:.2f}'.format(distance),'{:.2f}'.format(airport.lon),'{:.2f}'.format(airport.lat),))
        except:
            return True
        return False

if __name__ == '__main__':
    query = WorldAircraftQuery(True)
    query.ShowHead()
    if query.GetInput():
        query.ShowError('Illegal Input')
    elif query.Process():
        query.ShowError('Processing Failed')
    else:
        query.ShowResult()