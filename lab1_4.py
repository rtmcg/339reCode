"""
Monte Carlo to simulate an unfair coin
"""

import matplotlib.pyplot as plt
import random as r
import numpy as np

nsamp = 100
probCoin = 0.8

values = np.zeros(nsamp)
trials = list(range(nsamp)) # can work with just range(nsamp) though
coinFlips = np.zeros(nsamp)

for i in trials:
    values[i] = r.random()
    if values[i] < probCoin: # parentheses are not needed
        coinFlips[i] = 0
    else:
        coinFlips[i] = 1
       
numTails = sum(coinFlips)

print('coin flips mean', np.mean(coinFlips))
print('coin flips std', np.std(coinFlips))

binNumber = 20
binNumberFlips = 10

plt.figure()
plt.subplot(2,2,1)
plt.plot(trials, values, 'o')
plt.xlabel('trials')
plt.ylabel('values')

plt.subplot(2,2,2)
plt.hist(values, bins=binNumber)
plt.xlabel('value')
plt.ylabel('counts')

plt.subplot(2,2,3)
plt.plot(trials, coinFlips, 'o')
plt.xlabel('trials')
plt.ylabel('flips')

plt.subplot(2,2,4)
tailsPercent = 100 * (numTails/nsamp)
headsPercent = 100 - tailsPercent
plt.bar([0,1], [headsPercent, tailsPercent], width = 0.8)
plt.xlabel('flips')
plt.ylabel('counts')

plt.tight_layout()