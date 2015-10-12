"""
Attribute to feature mapping functions for items

map-knn(k) : predict matrix factor H with cosine similarity as weight.
map-lin(alpha, lambda) : linear model train with LeastMSE cost function. 
map-bpr(alpha, lambda) : linear model train with BPR-OPT cost function.
cbf-knn() : k=infinity, predict score directly with sum of cosine similarity.
random() : predict a random set of items as baseline

Inside brackets are parameters needed which can be train via cross-validation.

A, W, H, S matrix might be needed.

"""

import bpr
from math import sqrt
import numpy as np
import scipy.sparse as sp
import sys
import random

class Mapper(object):

    def __init__(self):
        pass

    def init(self, data, attr, bpr_k=None, bpr_args=None):
        assert sp.isspmatrix_csr(data)
        assert sp.isspmatrix_csr(attr)
        self.data = data
        self.num_users, self.num_items = data.shape
        print "Mapper train data : ", self.num_users, "x", self.num_items
        self.attr = attr
        assert attr.shape[0] >= self.num_items
        self.bpr_k = [self.num_users/5,bpr_k][bpr_k!=None]
        if bpr_args==None:
            self.bpr_args = bpr.BPRArgs(0.01, 1.0, 0.02125, 0.00355, 0.00355)
        else:
            self.bpr_args = bpr_args
        self.bpr_model = bpr.BPR(self.bpr_k, self.bpr_args)
    
    def test_init(self, test_data, test_attr):
        assert sp.isspmatrix_csr(test_data)
        assert sp.isspmatrix_csr(test_attr)
        self.num_test_items, _ = test_attr.shape
        self.test_data = test_data

    def prec_at_n(self, prec_n):
        #precision of top-n recommended results, average across users
        prec_n = min(prec_n, self.num_test_items)
        result = 0
        for u in range(self.num_users):
            print "Predicting for user ",u,"......."
            cand = []
            for i in range(self.num_test_items):
                cand.append((self.map_predict(u, i), i))
            cand.sort(lambda x,y : cmp(x[0],y[0]), reverse=True)
            tmp = 0.0
            row_u = self.test_data[u].toarray()[0]
            for i in range(prec_n):
                if row_u[cand[i][1]]>0:
                    tmp += 1
            result += tmp/prec_n
        result /= self.num_users
        return result

    def auc(self):
        #area under ROC curve, compute , average across users
        result = 0
        for u in range(self.num_users):
            tmp = 0.0
            for i in range(self.num_test_items):
                #wrong here, should be compute via comparing actual I+ and I- prediction in test dataset
                if self.map_predict(u, i)>=0:
                    tmp += 1
            real_pos = len(self.test_data[u].indices)
            result += tmp/max(real_pos, 1)/max(self.num_test_items-real_pos, 1)
        result /= self.num_users
        return result 

    def _row_dot(self, x, y):
        return x.dot(y.transpose()).sum()

class Map_KNN(Mapper):

    def __init__(self, data, attr, bpr_k=None, bpr_args=None, k=None):
        pass

class Map_Linear(Mapper):

    def __init__(self, data, attr, bpr_k=None, bpr_args=None, learning_rate=None, penalty=None):
        pass

    def _cross_validation():
        pass

class Map_BPR(Mapper):

    def __init__(self, data, attr, bpr_k=None, bpr_args=None, learning_rate=None, penalty=None):
        pass

    def _cross_validation():
        pass

class CBF_KNN(Mapper):

    def __init__(self, data, attr, bpr_k=None, bpr_args=None, k=None):
        self.init(data, attr, bpr_k, bpr_args)
        self.k = k

    def train(self, num_iters):
        #self.bpr_model.train(self.data, self.sampler, num_iters)
        pass

    def test(self, test_data, test_attr, prec_n=5):
        self.test_init(test_data, test_attr)
        sp.vstack( [self.attr, test_attr] ).tocsr()
           
        return [self.prec_at_n(prec_n), self.auc()]   
        
    def bpr_predict(self, u, i):
        #return bpr_model.predict(self, u, i)
        pass

    def map_predict(self, u, i):
        result = 0
        if self.k==None:
            for j in self.data[u].indices:
                result += self._row_dot(self.attr[i], self.attr[j]) / sqrt(self._row_dot(self.attr[i], self.attr[i]) * self._row_dot(self.attr[j], self.attr[j]))
        else:
            sim = []
            for j in self.data[u].indices:
                sim.append(self._row_dot(self.attr[i], self.attr[j]) / sqrt(self._row_dot(self.attr[i], self.attr[i]) * self._row_dot(self.attr[j], self.attr[j])))
            sim.sort()
            for j in range(self.k):
                result += sim[j]
        return result

class Map_Random(Mapper):

    def __init__(self, data, attr, bpr_k=None, bpr_args=None):
        self.init(data, attr, bpr_k, bpr_args)

    def train(self, num_iters):
        pass

    def test(self, test_data, test_attr, prec_n=5):
        self.test_init(test_data, test_attr)
        return [self.prec_at_n(prec_n), self.auc()]   

    def map_predict(self, u, i):
        return random.random()