import numpy as np
    
def H(array):
    '''Calculates Shannon's entropy with class labels: numpy array'''
    ent = 0.0
    classes = set(array)
    for cl in classes:
        p = np.count_nonzero(array == cl)/len(array)
        ent+= p*np.log2(p)
    return -ent

array = np.array(['cat','cat','cat','cat','cat','dog'])
print(H(array))
