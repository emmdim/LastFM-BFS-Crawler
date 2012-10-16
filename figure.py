"""figure.py"""

__author__      = "H. Shang, M. Orazow, E. Dimogerontakis"
__copyright__   = "http://creativecommons.org/licenses/by-sa/3.0/"


import re
import numpy as np
import pylab as pl
from scipy.optimize.minpack import curve_fit

file = open("results", "r")
x = []
y = []
for line in file:
    numbers = re.findall("\d+", line)
    if len(numbers) == 3:
        x.append(numbers[0])
        y.append(numbers[1])

def func(x, a, b, c):
        return a * np.exp(-b * x) + c

#plot1=pl.plot(x,y,'r')
plot2, =pl.plot(x,y,'go')
pl.title('Average degree Versus Number of nodes')
pl.xlim(0.0,11000)
pl.ylim(0.0,500)
pl.xlabel('Number of nodes')
pl.ylabel('Average degree')
x1 = map(lambda x: float(x),x)
y1 = map(lambda x: float(x),y)

coeff = np.polyfit(x1,y1,3)
poly = np.poly1d(coeff)
xs= np.arange(600,10500,1)
ys=poly(xs)
#plot3 = pl.plot(xs,ys,'r')

xa = np.asarray(x1)
ya = np.asarray(y1)
popt, pcov = curve_fit(func, xa, ya)

out = str(round(popt[0],2))+"e^(-"+str(round(popt[1], 4))+"x)+"+str(round(popt[2],2))
plot3, =pl.plot(xa, func(xa, *popt), 'r')

pl.legend([plot2,plot3], ('Data',out), 'best', numpoints=1)

pl.show()
