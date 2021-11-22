"""
Monte Carlo to generate exponentially distributed random values
"""
import matplotlib.pyplot as plt
import numpy as np
import random as r

# good to group parameters at beginning
# of code so you can find/modify them easily
Nsamp = 100
binNumber = 20
cumBinNumber = 100
a = 1

def cumExpModel(a, x):
    x = np.array(x) # not need when used with binCenter, already np array
    return 1 - np.exp(-a * x)

values = np.zeros(Nsamp)
trials = list(range(Nsamp)) # range works since the list is just an index

for i in trials:
    ro = r.random()
    values[i] = -(1/a) * np.log(1 - ro)
    
print('mean', np.mean(values))
print('std', np.std(values))

histValues, binEdges = np.histogram(values, cumBinNumber)
cumHistValues = np.cumsum(histValues)/Nsamp

binCenter = np.zeros(len(binEdges)-1)

# convert bin edges to bin center position
# note len() gives number of elements in array
for i in range(len(binEdges) - 1):
    binCenter[i] = 0.5 * (binEdges[i] + binEdges[i + 1])
    
plt.figure()

plt.subplot(2, 2, 1)
plt.plot(trials, values, 'o')
plt.xlabel('trials')
plt.ylabel('values')

plt.subplot(2, 2, 2)
plt.hist(values, bins = binNumber)
plt.xlabel('values')
plt.ylabel('counts')

plt.subplot(2, 2, 3)
plt.plot(binCenter, cumHistValues, 'o')
plt.xlabel('value')
plt.ylabel('cumulative co')

plt.subplot(2, 2, 4)
plt.plot(binCenter, cumExpModel(a, binCenter),'o')
plt.xlabel('value')
plt.ylabel('cumulative counts')

plt.tight_layout()

np.savetxt('nonuniform.csv', 
           np.transpose([binCenter, cumHistValues]), delimiter = ",")