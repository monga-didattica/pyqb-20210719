# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Programming in Python
# ## Exam: July 19, 2021
#
#
# You can solve the exercises below by using standard Python 3.9 libraries, NumPy, Matplotlib, Pandas, PyMC3.
# You can browse the documentation: [Python](https://docs.python.org/3.9/), [NumPy](https://numpy.org/doc/stable/user/index.html), [Matplotlib](https://matplotlib.org/3.3.1/contents.html), [Pandas](https://pandas.pydata.org/pandas-docs/version/1.2.5/), [PyMC3](https://docs.pymc.io/).
# You can also look at the [slides of the course](https://homes.di.unimi.it/monga/lucidi2021/pyqb00.pdf) or your code on [GitHub](https://github.com).
#
# **It is forbidden to communicate with others.** 
#

# %matplotlib inline
import numpy as np   # type: ignore
import pandas as pd  # type: ignore
import matplotlib.pyplot as plt # type: ignore
import pymc3 as pm   # type: ignore

# ### Exercise 1 (max 3 points)
#
# Consider a bidimensional grid with 33x33 dots. Plot the dots.

x = np.linspace(-16, 16, 33)
y = np.linspace(-16, 16, 33)
grid = np.meshgrid(x, y)

fig, ax = plt.subplots(figsize=(10,10))
_ = ax.scatter(grid[0], grid[1], s=.2)


# ### Exercise 2 (max 5 points)
#
# On the grid defined in Exercise 1, compute 5 random walks, starting in the central dot, going on for 100 steps of 1 in the horizontal, vertical or both directions. When a walk reaches the border of the grid, it starts again on the opposite side: in other words, on a line of dots to the left of the leftmost dot there is the rightmost one; same on the right, above, and below.

def one_step(start: tuple[int, int], step: tuple[int, int], dim: int = 16) -> tuple[int, int]:
    """Return the point after a step applied to start. 
    The borders are at -dim and dim. 
    
    >>> one_step((2, 1), (1, 1))
    (3, 2)
    
    >>> one_step((0,16), (0, 1))
    (0, -16)
    """
    
    ris = [0, 0]
    for axis in (0, 1):
        ris[axis] = start[axis] + step[axis]
        if ris[axis] > dim:
            ris[axis] = ris[axis] - dim*2 - 1
        elif ris[axis] < -dim:
            ris[axis] = ris[axis] + dim*2 + 1
    
    return (ris[0], ris[1])    


# +
walk = np.zeros((5, 100, 2))

for w in range(0, 5):
    steps = np.random.randint(-1, 1+1, size=(100-1, 2))

    i = 1
    for s in steps:
        walk[w][i] = np.array(one_step((walk[w][i-1][0], walk[w][i-1][1]), (s[0], s[1])))
        i = i + 1
# -

# ### Exercise 3 (max 3 points)
#
# Plot the walks computed in Exercise 2.

fig, ax = plt.subplots(figsize=(10,10))
ax.scatter(grid[0], grid[1], s=.2, color='black')
for w in range(0,5):
    _ = ax.plot(walk[w,:,0], walk[w,:,1])


# ### Exercise 4 (max 7 points)
#
# Define a function that takes two random walks and computes a new one. The resulting walk:
# - has a length equal to the sum of the lengths of the given walks minus one
# - the first half is the first given
# - the second half is the second given, traslated such as the first step is applied to the last position of the first given walk
#
# For example: if the two walks are `[(0,0), (1,1)]` and `[(0,0), (0,-1)]`, the resulting walk will be `[(0,0), (1,1), (1,0)]`
#
#
# To get the full marks, you should declare correctly the type hints (the signature of the function) and add a doctest string.

def append_walk(w1: list[tuple[int, int]], w2: list[tuple[int, int]], dim: int = 16) -> list[tuple[int, int]]:
    """Append w2 to w1.
    
    >>> append_walk([(0, 0), (1, 1)], [(0, 0), (0, -1)])
    [(0, 0), (1, 1), (1, 0)]
    
    """
    
    ris = w1.copy()
    i = len(w1) - 1
    for p in w2[1:]:
        iw = i - len(w1) + 1
        s = (p[0] - w2[iw][0], p[1] -  w2[iw][1])
        ris.append(one_step(w1[i], s, dim))
        i = i + 1
    return ris


# ### Exercise 5 (max 2 points)
#
# Load the data contained in the file `iris.csv` in a Pandas DataFrame.

iris = pd.read_csv('iris.csv', sep=',')
iris.head()

# ### Exercise 6 (max 3 points)
#
#
# Add to the dataframe two columns for the ratio between width and length, for petals and sepals.

iris['petal ratio'] = iris['petal width'] / iris['petal length']
iris['sepal ratio'] = iris['sepal width'] / iris['sepal length']

# ### Exercise 7 (max 5 points)
#
# Plot the histograms of the sepal ratio computed in Exercise 6 for each iris class. Put the three plots in a single chart.

# +
ig = iris.groupby('class')

fig, ax = plt.subplots(figsize=(10,10))
for g in ig.groups.keys():
    ax.hist(ig.get_group(g)['sepal ratio'], bins='auto', density=True, alpha=.6, label=g)
_ = fig.legend()


# -

# ### Exercise 8 (max 5 points)
#
# Consider this statistical model: the sepal ratio of Iris-setosa and Iris-virginica is normally distributed, with an unknown mean, and a standard deviation of 0.1. Your *a priori* estimation of the mean for both distribution is a normal distribution with mean 0.5 and standard deviation 0.1. Use PyMC to sample the posterior distributions after having seen the actual values for Iris-setosa and Iris-virginica.  Plot the results.

# +
mymodel = pm.Model()


with mymodel:
    mu_s = pm.Normal('mu_s', 0.5, 0.1)
    mu_v = pm.Normal('mu_v', 0.5, 0.1)
    
    sr_s = pm.Normal('sr_s', mu=mu_s, sigma=.1, observed=iris.query('`class` == "Iris-setosa"')['sepal ratio'])
    sr_v = pm.Normal('sr_v', mu=mu_v, sigma=.1, observed=iris.query('`class` == "Iris-virginica"')['sepal ratio'])
    
    post = pm.sample()
    
# -

with mymodel:
    pm.plot_posterior(post)
