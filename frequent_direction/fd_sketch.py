# -*- coding: utf-8 -*-
#!/usr/bin/env python

#####
# BSD 2-clause "Simplified" License
# original repository https://github.com/hido/frequent-direction
# rearranged to class by AtsushiHashimoto (based on the clone accessed on 26th Jun. 2017)
#####

import numpy as np
import numpy.linalg as ln
import math
import sys

""" This is a simple and deterministic method for matrix sketch.
The original method has been introduced in [Liberty2013]_ .

[Liberty2013] Edo Liberty, "Simple and Deterministic Matrix Sketching", ACM SIGKDD, 2013.
"""

class FrequentDirection:
    def __init__(self,ell, k=None):
        self.ell = int(ell)
        if k is None:
            # the setting of original paper
            self.k = 2 * ell + 1
        else:
            self.k = int(k)
        self.M = None
        self.N = 0
        self.mat_b = None
        self.zero_rows = None

    def is_initialized(self):
        return (self.M is not None)

    def initialize(self,row):
        self.M = len(row)
        # Input error handling
        if self.ell >= self.M:
            raise ValueError('Error: ell must be smaller than M * 2')
        self.N = 0
        # initialize output matrix B
        self.mat_b = np.zeros([self.ell+self.k, self.M])

        # set all rows as the initial list of zero value rows
        self.zero_rows = list(range(self.ell + self.k))
        return

    def get_result(self,initialize=False):
        if self.ell+self.k >= self.N:
            raise ValueError('Error: ell + k must not be greater than N')

        # cut off zero vectors
        result = self.mat_b[:self.ell]
        if initialize:
            self.__init__(self.ell, self.k)
        return result

    def add_sample(self,row):
        if not self.is_initialized():
            self.initialize(row)

        # iteration
        i = self.N

        # insert a row into matrix B
        self.mat_b[self.zero_rows[0], :] = row

        # remove the consumed row from the zero values row list
        self.zero_rows.remove(self.zero_rows[0])

        # if there is no more zero valued row
        if len(self.zero_rows) == 0:

            # compute SVD of matrix B
            mat_u, vec_sigma, mat_v = ln.svd(self.mat_b, full_matrices=False)

            # obtain squared singular value for threshold
            squared_sv_center = vec_sigma[self.ell] ** 2

            # update sigma to shrink the row norms
            sigma_tilda = [(0.0 if d < 0.0 else math.sqrt(d)) for d in (vec_sigma ** 2 - squared_sv_center)]

            # update matrix B where at least half rows are all zero
            self.mat_b = np.dot(np.diagflat(sigma_tilda), mat_v)

            # update the zero valued row list
            self.zero_rows = np.nonzero([round(s, 7) == 0 for s in np.sum(self.mat_b, axis = 1)])[0].tolist()
        self.N = self.N + 1


def calculateError(mat_a, mat_b):
    """Compute the degree of error by sketching

    :param mat_a: original matrix
    :param mat_b: sketch matrix
    :returns: reconstruction error
    """
    dot_mat_a = np.dot(mat_a.T, mat_a)
    dot_mat_b = np.dot(mat_b.T, mat_b)
    return ln.norm(dot_mat_a - dot_mat_b, ord = 2)


def squaredFrobeniusNorm(mat_a):
    """Compute the squared Frobenius norm of a matrix

    :param mat_a: original matrix
    :returns: squared Frobenius norm
    """
    return ln.norm(mat_a, ord = 'fro') ** 2
