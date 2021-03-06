#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Runs an entire experiment for benchmarking PURE_RANDOM_SEARCH on a testbed.

CAPITALIZATION indicates code adaptations to be made.
This script as well as files bbobbenchmarks.py and fgeneric.py need to be
in the current working directory.

Under unix-like systems: 
    nohup nice python exampleexperiment.py [data_path [dimensions [functions [instances]]]] > output.txt &

"""
import sys # in case we want to control what to run via command line args
import time
import numpy as np
import fgeneric
import bbobbenchmarks
# import genetic as ga

argv = sys.argv[1:] # shortcut for input arguments

datapath = 'bbob_pproc/testing13' if len(argv) < 1 else argv[0]

dimensions = [2]
function_ids = [14] 
# function_ids = bbobbenchmarks.noisyIDs if len(argv) < 3 else eval(argv[2])
instances = range(1, 6) + range(41, 51) if len(argv) < 4 else eval(argv[3])

opts = dict(algid='1',
            comments='note')
maxfunevals = '10 * dim' # 10*dim is a short test-experiment taking a few minutes 
# INCREMENT maxfunevals SUCCESSIVELY to larger value(s)
minfunevals = 'dim + 2'  # PUT MINIMAL sensible number of EVALUATIONS before to restart
maxrestarts = 10000      # SET to zero if algorithm is entirely deterministic 

        #ans = 0
    #return np.asarray(newlist)

def run_optimizer(fun, dim, maxfunevals, ftarget=-np.Inf):
    """start the optimizer, allowing for some preparation. 
    This implementation is an empty template to be filled 
    
    """
    # prepare

    x_start = 8. * np.random.rand(dim) - 4
    #x_start is the values that will be input into the
    #
    #print"X_START", x_start, "\n"
    # call, REPLACE with optimizer to be tested
    PURE_RANDOM_SEARCH(fun, x_start, maxfunevals, ftarget)
    #NN(fun, x_start, maxfunevals, ftarget)

def NN(fun, x, maxfunevals, ftarget=-np.Inf):
    #Attempt at implementation of Neural Network
    for _ in range(0,int(maxfunevals)):
        flist = ga.Genetically(10,30, [tuple(x)])
        fvalues = fun(x)
        ydx = np.argsort(flist)
        idx = np.argsort(fvalues)
        fbest = flist[ydx[0]]
        xbest = fbest 
    #return xbest


def PURE_RANDOM_SEARCH(fun, x, maxfunevals, ftarget):
    """samples new points uniformly randomly in [-5,5]^dim and evaluates
    them on fun until maxfunevals or ftarget is reached, or until
    1e8 * dim function evaluations are conducted.

    """
    popsize = min(maxfunevals, 200)
    dim = len(x)
    maxfunevals = min(1e8 * dim, maxfunevals)
    fbest = np.inf
    
    for _ in range(0, int(np.ceil(maxfunevals / popsize))):
        xpop = 10. * np.random.rand(popsize, dim) - 5.
        fvalues = fun(xpop)
        idx = np.argsort(fvalues)
        if fbest > fvalues[idx[0]].any():
            fbest = fvalues[idx[0]]
            xbest = xpop[idx[0]]
        if fbest < ftarget:  # task achieved 
            break

    return xbest

t0 = time.time()
np.random.seed(int(t0))

f = fgeneric.LoggingFunction(datapath, **opts)
for dim in dimensions:  # small dimensions first, for CPU reasons
    for fun_id in function_ids:
        for iinstance in instances:
            f.setfun(*bbobbenchmarks.instantiate(fun_id, iinstance=iinstance))

            # independent restarts until maxfunevals or ftarget is reached
            for restarts in xrange(maxrestarts + 1):
                if restarts > 0:
                    f.restart('independent restart') # additional info
                
                run_optimizer(f.evalfun, dim,  eval(maxfunevals) - f.evaluations,
                              f.ftarget)
                if (f.fbest < f.ftarget
                    or f.evaluations + eval(minfunevals) > eval(maxfunevals)):
                    break

            f.finalizerun()

            print('  f%d in %d-D, instance %d: FEs=%d with %d restarts, '
                  'fbest-ftarget=%.4e, elapsed time [h]: %.2f'
                  % (fun_id, dim, iinstance, f.evaluations, restarts,
                     f.fbest - f.ftarget, (time.time()-t0)/60./60.))

        print '      date and time: %s' % (time.asctime())
    print '---- dimension %d-D done ----' % dim
