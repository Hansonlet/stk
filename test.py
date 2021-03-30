row = [1,2,34,5,6,7,8,0,1,23,4,6,87,43,5,6,3,54]
fo = open("test.txt", "w")
for i in range(100000):    
    fo.write("%d %.0f %d %d %d %d %d %.0f %d %d %d %d %.0f %.0f\n" % (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]))                
fo.close()
print("a thread finished")