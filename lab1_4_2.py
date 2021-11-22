"""
Monte Carlo to simulate an unfair die
"""
import matplotlib.pyplot as plt
import numpy as np
import random as r

Nsamp = 10
po = 1/6.0
bias = 0.05

p6 = po + bias
p = (1 - p6)/5

probVect = [p, p, p, p, p, p6]
cumVect = np.cumsum(probVect)

values = np.zeros(Nsamp)
trials = list(range(Nsamp)) # range works and is commonly used in a for loop
dieToss = np.zeros(Nsamp)

for i in trials:
    values[i] = r.random()
    if values[i] < cumVect[0]:
        dieToss[i] = 1
    elif cumVect[0] <= values[i] < cumVect[1]:
        dieToss[i] = 2
    elif cumVect[1] <= values[i] < cumVect[2]:
        dieToss[i] = 3
    elif cumVect[2] <= values[i] < cumVect[3]:
        dieToss[i] = 4
    elif cumVect[3] <= values[i] < cumVect[4]:
        dieToss[i] = 5
    else: # End with else, since all other possibilities are counted
        dieToss[i] = 6

numToss = np.zeros(6)
for i in range(1,7):
    numToss[i-1] = sum(dieToss==i)

numTossPercent = 100*(numToss/Nsamp)

plt.figure()

plt.subplot(1, 2, 1)
plt.plot(trials, dieToss, 'o')
plt.xlabel('toss trials')
plt.ylabel('toss value')

plt.subplot(1, 2, 2)
plt.bar(range(1,7), numTossPercent, width = 0.8)
plt.xlabel('toss value')
plt.ylabel('counts')

plt.tight_layout()