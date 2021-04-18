for i in [11,12,13,14,15,16,17,18,19,20]:
    name = "one_circle/data"+str(i)+".txt"
    name2 = "one_circle/ndata"+str(i)+".txt"
    fo = open(name,"r")
    fo_write = open(name2,"w")
    for line in fo:
        line_data = line.split(" ")
        line_data[-1] = line_data[-1][0 : -1]
        line_data = list(map(float, line_data))
        line_data[1] = 0.05
        fo_write.write("%d %.2f %d %d %d %d %.3f %.3f %.3f\n" % (line_data[0],line_data[1],line_data[2],line_data[3],line_data[4],line_data[5],line_data[6],line_data[7],line_data[8]))
    fo.close()
    fo_write.close()