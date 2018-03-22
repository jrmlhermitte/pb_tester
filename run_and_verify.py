def make_filenames(nprocs, prefix):
    '''
        This is reliant on the c Code
        calls pb_test_write prefix num
    '''
    filenames = ["{}{:05}.out".format(prefix, i) for i in range(nprocs)]
    return filenames

def run(nprocs, prefix="foo"):
    from subprocess import call
    call(["./pb_test_write", prefix, "{}".format(nprocs)])

def verify(nprocs, prefix="foo"):
    nlines = 50000;
    test_array = np.arange(nlines);

    filenames = make_filenames(nprocs)
    for filename in filenames:


