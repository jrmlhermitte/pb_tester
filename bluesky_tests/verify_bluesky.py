# still needs to be modified for testing
from ophyd.sim import motor1, flyer1
from bluesky import RunEngine
import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp

from uuid import uuid4


def set_and_fly(filepaths, flyers, sleeptime=10):
    '''
        Fly on flyers with file prefix for a certain sleep time.
        fileprefix: file prefix
        sleeptime : sleep time to let flyer run for
    '''

    # set the file paths
    for filepath, flyer in zip(filepaths, flyers):
        yield from bps.abs_set(flyer.filepath, filename)

    # now fly
    yield from bpp.fly_during_wrapper(bps.sleep(sleeptime), [flyer])

# a simple run to write to temp files
def run_pb(flyers, root='/tmp', collection_time=10):
    # make some filenames
    filenames = list()
    for flyer in flyers:
        filenames.append(root + "/" + str(uuid4()) + "." + flyer.name)


    RE = RunEngine()
    RE(set_and_fly(filenames, flyers, sleeptime=10))

    return filenames

def verify_pb(filenames):
    for filename in filenames:
        verify(filename)

def verify:
    pass

def run_and_verify(flyers, root='/tmp', collection_time=10):
    filenames = run_pb(flyers, root=root, collection_time=collection_time)
    verify_pb(filenames)
