
from sklearn.cluster import KMeans

import numpy as np
import collections

CLUSTERS = 25

np.set_printoptions(suppress=True)
#As entradas
#arq = open('gui.csv', 'r')
#dataset = np.loadtxt(arq, delimiter=",")
start = 63
ninputs = 843
dataset = np.loadtxt('base_shooter.csv', dtype=None, delimiter=",", skiprows=1,usecols=range(start,ninputs)) 

#inputs
#inputs = dataset.tolist()

inputs = dataset.reshape(405,780)
print dataset[0]

model = KMeans(n_clusters=CLUSTERS, random_state=0,init="k-means++",verbose=True,n_init=100,tol=0.00001)
out = model.fit(inputs)


cnt = collections.Counter(out.labels_)
som = 0
keys = cnt.keys()
for i in keys:
    som += cnt[i]
    print cnt[i]
print "total:"+str(som)
    
pred = model.predict(inputs)

print out.inertia_
print pred
    
np.savetxt('centroides_shooter_'+str(CLUSTERS)+'.txt',out.cluster_centers_,delimiter=",",fmt="%10.5f")
np.savetxt('classes_shooter_'+str(CLUSTERS)+'.txt',pred,delimiter=",",fmt="%3s")