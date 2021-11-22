import matplotlib.pyplot as plt
import random as r
import numpy as np
 
Nsamp=10
values = np.zeros(Nsamp)
trials = list(range(Nsamp)) # could work with range(Nsamp)
for i in trials:
    values[i] = r.random()
print('mean', np.mean(values))
print('std', np.std(values))

binNumber = 20
plt.figure() # call figure so figures can be separated
plt.subplot(1,2,1)
plt.plot(trials, values, 'o') # don't need to plot x if it's just the indices
plt.xlabel('trials')
plt.ylabel('values')
plt.subplot(1,2,2)
plt.hist(values, bins=binNumber)
plt.xlabel('value')
plt.ylabel('counts')
plt.tight_layout() # to avoid overlap

