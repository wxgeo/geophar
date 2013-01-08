"""
SymPy statistics module

Introduces a random variable type into the SymPy language.

Random variables may be declared using prebuilt functions such as
Normal, Exponential, Coin, Die, etc...  or built with functions like FiniteRV.

Queries on random expressions can be made using the functions

===================== =============================
    Expression                Meaning
--------------------- -----------------------------
 P(condition)          Probability
 E(expression)         Expectation value
 variance(expression)  Variance
 density(expression)   Probability Density Function
 sample(expression)    Produce a realization
 where(condition)      Where the condition is true
===================== =============================

Examples
========

>>> from sympy.stats import P, E, variance, Die, Normal
>>> from sympy import Eq, simplify
>>> X, Y = Die('X', 6), Die('Y', 6) # Define two six sided dice
>>> Z = Normal('Z', 0, 1) # Declare a Normal random variable with mean 0, std 1
>>> P(X>3) # Probability X is greater than 3
1/2
>>> E(X+Y) # Expectation of the sum of two dice
7
>>> variance(X+Y) # Variance of the sum of two dice
35/6
>>> simplify(P(Z>1)) # Probability of Z being greater than 1
-erf(sqrt(2)/2)/2 + 1/2
"""

__all__ = []

import rv_interface
from rv_interface import (
    cdf, covariance, density, dependent, E, given, independent, P, pspace,
    random_symbols, sample, sample_iter, skewness, std, variance, where,
)
__all__.extend(rv_interface.__all__)

import frv_types
from frv_types import (
    Bernoulli, Binomial, Coin, Die, DiscreteUniform, FiniteRV, Hypergeometric,
)
__all__.extend(frv_types.__all__)

import crv_types
from crv_types import (
    Arcsin, Benini, Beta, BetaPrime, Cauchy, Chi, ContinuousRV, Dagum,
    Exponential, Gamma, Laplace, Logistic, LogNormal, Maxwell, Nakagami,
    Normal, Pareto, Rayleigh, StudentT, Triangular, Uniform, UniformSum,
    Weibull, WignerSemicircle,
)
__all__.extend(crv_types.__all__)
