import numpy as np

def calcNorm(weight):
    res = []
    for l in xrange(len(weight)):
        res.append([])
        for r in xrange(len(weight[l])):
            res[l].append(np.linalg.norm(weight[l][r]))
    return res