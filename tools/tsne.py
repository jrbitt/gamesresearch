
from sklearn.manifold import TSNE

import numpy as np
import collections


np.set_printoptions(suppress=True)
#As entradas
#arq = open('gui.csv', 'r')
#dataset = np.loadtxt(arq, delimiter=",")
start = 63
ninputs = 843
dataset = np.loadtxt('pca.txt', dtype=None, delimiter=",") 

#inputs
#inputs = dataset.tolist()
inputs = dataset

model = PCA(n_components=12, svd_solver='randomized')
out = model.fit_transform(inputs)

#print out.explained_variance_
#print out.explained_variance_ratio_

#out.n_components = 12
#X_reduced = out.transform(inputs)
#print X_reduced.shape

print out
np.savetxt('pca.txt',out,delimiter=",",fmt="%10.5f")
