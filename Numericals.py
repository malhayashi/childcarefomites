import numpy
import operator
from math import *
from matplotlib.pylab import *

def metropolisHastings(distribution, iterations=10**4):
    n = iterations
    alpha = 1
    x = 0.
    vec = []
    vec.append(x)
    innov = numpy.random.uniform(-alpha,alpha,n)
    for i in xrange(1,n):
        can = x + innov[i]
        aprob = min([1.,distribution(can)/distribution(x)])
        u = uniform(0,1)
        if u < aprob:
            x = can
            vec.append(x)

    #plot
    '''x = arange(-3,3,.1)
    y = distribution(x)
    subplot(211)
    title('Metropolis-Hastings')
    plot(vec)
    subplot(212)

    hist(vec, bins=30,normed=1)
    plot(x,y,'ro')
    ylabel('Frequency')
    xlabel('x')
    legend(('PDF','Samples'))
    show()'''
    return vec

def multiSpatialMC(oracle=False, dimension=2, iterations=10**5):
    oldPoint = []
    newPoint = []
    trans = []
    for i in range(0,dimension):
        oldPoint.append(0)
        newPoint.append(0)
        trans.append(0)
    for count in range(0,iterations):
        for i in range(0,dimension):
            axial_displacement = numpy.random.uniform()
            if axial_displacement < .5:
                trans[i] = -1
            else:
                trans[i] = 1
            newPoint = add(oldPoint, trans)
            if oracle(newPoint):
                oldPoint = newPoint
    return oldPoint

def add(listA, listB):
    temp = []
    for i in range(0,len(listA)):
        temp.append(0)
    print(temp, listA, listB)
    for i in range(0, len(listA)):
        temp[i] = listA[i] + listB[i]
    return temp

def chaosRain(function=0.0, dimension=2, center=[0,0]):
    #wtf high dimensional brownian motion is a pain in the ass
    pass


def monteCarlo(function,iterations=10**4):
    vals = []
    for i in range(0,iterations):
        vals.append(function())
    return sum(vals)/len(vals)

def lagrange_interpolation(node, x_values=(), y_values=()):
    def _basis(j):
        p = [(node - x_values[m])/(x_values[j] - x_values[m]) for m in xrange(k) if m != j]
        return reduce(operator.mul, p)
    assert len(x_values) != 0 and (len(x_values) == len(y_values)), 'bruh'
    k = len(x_values)
    return sum(_basis(j)*y_values[j] for j in xrange(k))

def testmodel():
    psi = numpy.random.normal()
    #psi = 1
    return 5 + 2*psi

def testDistribution(X):
    return exp(-X*X/2.)/sqrt(2*pi)

if __name__ == '__main__':
    print(monteCarlo(function=lambda: testmodel()))
    metropolisHastings(distribution=lambda out: testDistribution(out), iterations=10**4)
