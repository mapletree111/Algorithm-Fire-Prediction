import numpy as np
from matplotlib import pyplot as plt  #contains both numpy and pyplot
import os
import shapefile
from dbfread import DBF



def printMap(filename):
    sf = shapefile.Reader(filename)

    plt.figure()
    for shape in sf.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        plt.plot(x,y)

    plt.show()

def print_records(filename):
    sf = shapefile.Reader(filename)
    fields = sf.fields
    records = sf.records()
    print fields
    print records[:3]
    
shp_file_path = os.path.join('tl_2017_37_tract', 'tl_2017_37_tract.shp')
#print_records(shp_file_path)


reader = shapefile.Reader(shp_file_path)
writer = shapefile.Writer()
writer.fields = list(reader.fields)

writer.field("Tot_Pop",'N',8)
i = 1000
for rec in reader.records():
    rec.append(i)
    i+=10
    writer.records.append(rec)

writer._shapes.extend(reader.shapes())
writer.save("out")

print_records('out.shp')

#printMap(shpFilePath)
