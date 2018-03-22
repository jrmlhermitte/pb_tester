# still needs to be modified for testing
from ophyd.sim import motor1, flyer1
from bluesky import RunEngine
import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp

from uuid import uuid4

#from iss_detectors_workaround import pb1, pba1

def set_and_fly(filepaths, flyers, sleeptime=10):
    '''
        Fly on flyers with file prefix for a certain sleep time.
        fileprefix: file prefix
        sleeptime : sleep time to let flyer run for
    '''

    # set the file paths
    for filepath, flyer in zip(filepaths, flyers):
        yield from bps.abs_set(flyer.filepath, filepath)

    yield from bps.open_run()
    for flyer in flyers:
        yield from bps.stage(flyer)

    grp = str(uuid4())
    for flyer in flyers:
        yield from bps.kickoff(flyer, group=grp, wait=False)

    yield from bps.wait(group=grp)
    yield from bps.sleep(sleeptime)

    for flyer in flyers:
        yield from bps.complete(flyer, group=grp, wait=False)

    for flyer in flyers:
        yield from bps.collect(flyer)

    for flyer in flyers:
        yield from bps.unstage(flyer)

    yield from bps.close_run()


    # now fly
    #yield from bpp.fly_during_wrapper(bps.sleep(sleeptime), flyers)

# a simple run to write to temp files
def run_pb(flyers, root='/tmp', collection_time=10):
    # make some filenames
    filenames = list()
    for flyer in flyers:
        filenames.append(root + "/" + str(uuid4())[:8] + "." + flyer.name)

    RE = RunEngine()
    RE(set_and_fly(filenames, flyers, sleeptime=10))

    return filenames

def verify_pb(filenames):
    for filename in filenames:
        verify(filename)

def verify(filenames):
    pass

def run_and_verify(flyers, root='/tmp', collection_time=10):
    filenames = run_pb(flyers, root=root, collection_time=collection_time)
    verify_pb(filenames)

all_flyers = [pba2.adc7, pba1.adc6, pb9.enc1, pba1.adc1, pba2.adc6, pba1.adc7]
