import math
import numpy as np

def KLD(y_true,y_pred):
    '''Calculates Kullback Leibler Divergence of y_pred from y_true'''
    KLD = 0.0
    classes = set(y_true)
    y_true_probs = []
    y_pred_probs = []
    for cl in classes:
        y_true_probs.append(np.count_nonzero(y_true == cl)/len(y_true))
        y_pred_probs.append(np.count_nonzero(y_pred == cl)/len(y_pred))
    for i in range(0,len(y_true_probs)):
        KLD += y_pred_probs[i] * math.log(y_true_probs[i]/y_pred_probs[i],2)
    return -KLD

y_true = np.array(['cat','cat','cat','cat','cat','dog'])
y_pred = np.array(['cat','cat','cat','cat','dog','dog'])

print(KLD(y_true,y_pred))