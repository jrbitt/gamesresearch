#juntar os generos e clusters
arq = open("nova3.csv",'r')
first = True
header = ""
screens = []
scrOut = []
for line in arq:
    if first:
        header = line.split('\t')
        first = False
    else:
        tk = line.split('\t')
        screens.append(tk)
arq.close()

header[len(header)-1] = header[len(header)-1][:-1]
header.append('cluster')
header.append('genre')

def glue(filename,genre):
    act = open(filename,'r')
    actTk = []
    for line in act:
        tk = line.split(' ')
        actTk.append(tk)
    act.close()

    for a in actTk:
        for s in screens:
            if a[1] == s[1]:
                s[len(s)-1] = s[len(s)-1][:-1]
                s.append(a[0])
                s.append(genre)
                scrOut.append(s)
                print s
                
def glueGenres():
    glue('temp.csv','1000') #action
    glue('temp_adv.csv','100') #adventure
    glue('temp_strat.csv','10') #strategy

    out = open('nova4.csv','w')
    for h in header:
        out.write(h+" ")
    out.write('\n')
    for s in scrOut:
        for i in s:
            out.write(i+" ")
        out.write('\n')
    out.close()
    
    
glueGenres()