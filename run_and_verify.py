from numpy.testing import assert_array_almost_equal
import numpy as np

def make_filenames(prefix, nfiles):
    '''
        This is reliant on the c Code
        calls pb_test_write prefix num
    '''
    filenames = ["{}{:05}.txt".format(prefix, i) for i in range(nfiles)]
    return filenames

def run(prefix, numlines, nfiles):
    '''
        run pizzabox tester on prefix, numlines and nfiles (number files)
    '''
    from subprocess import call
    args = ["./pb_test_write", prefix, "{}".format(numlines), "{}".format(nfiles)]
    print("Running : {}".format(args))
    call(args)

def verify(prefix, numlines, nfiles):
    test_array = np.arange(numlines)[:, np.newaxis] + np.zeros(4)[np.newaxis, :]

    filenames = make_filenames(prefix, nfiles)
    for filename in filenames:
        res = np.loadtxt(filename)
        if res.shape[0] != numlines:
            print("Error, got {} lines, expected {}".format(res.shape[0],
                                                            numlines))
        assert_array_almost_equal(test_array, res)

def run_and_verify(prefix, numlines, nfiles):
    run(prefix, numlines, nfiles)
    verify(prefix, numlines, nfiles)

