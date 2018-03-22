import uuid
from collections import namedtuple
import os
import time as ttime
from ophyd import (ProsilicaDetector, SingleTrigger, Component as Cpt, Device,
                   EpicsSignal, EpicsSignalRO, ImagePlugin, StatsPlugin, ROIPlugin,
                   DeviceStatus)
from ophyd import DeviceStatus, set_and_wait
from bluesky.examples import NullStatus

from databroker.assets.handlers_base import HandlerBase

# temporarily put root dir here
ISS_ROOT_DIRECTORY = '/GPFS/xf08id/data/pizza_box_tests'

class Encoder(Device):
    """This class defines components but does not implement actual reading.

    See EncoderFS and EncoderParser"""
    pos_I = Cpt(EpicsSignal, '}Cnt:Pos-I')
    sec_array = Cpt(EpicsSignal, '}T:sec_Bin_')
    nsec_array = Cpt(EpicsSignal, '}T:nsec_Bin_')
    pos_array = Cpt(EpicsSignal, '}Cnt:Pos_Bin_')
    index_array = Cpt(EpicsSignal, '}Cnt:Index_Bin_')
    data_array = Cpt(EpicsSignal, '}Data_Bin_')
    # The '$' in the PV allows us to write 40 chars instead of 20.
    filepath = Cpt(EpicsSignal, '}ID:File.VAL', string=True)
    dev_name = Cpt(EpicsSignal, '}DevName')

    filter_dy = Cpt(EpicsSignal, '}Fltr:dY-SP')
    filter_dt = Cpt(EpicsSignal, '}Fltr:dT-SP')
    reset_counts = Cpt(EpicsSignal, '}Rst-Cmd')

    ignore_rb = Cpt(EpicsSignal, '}Ignore-RB')
    ignore_sel = Cpt(EpicsSignal, '}Ignore-Sel')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ready_to_collect = False
        if self.connected:
            self.ignore_sel.put(1)
            # self.filter_dt.put(10000)


class EncoderFS(Encoder):
    "Encoder Device, when read, returns references to data in filestore."
    chunk_size = 1024

    def stage(self):
        "Set the filename and record it in a 'resource' document in the filestore database."

        if(self.connected):
            print(self.name, 'stage')
            #DIRECTORY = ISS_ROOT_DIRECTORY
            #rpath = 'pizza_box_data'
            #filename = 'en_' + str(uuid.uuid4())[:6]
            #full_path = os.path.join(rpath, filename)
            #print('going')
            #self._full_path = os.path.join(DIRECTORY, full_path)  # stash for future reference
            #if len(self._full_path) > 40:
                #raise RuntimeError("Stupidly, EPICS limits the file path to 80 characters. "
                               #"Choose a different DIRECTORY with a shorter path. (I know....)")
            #self._full_path = os.path.join(DIRECTORY, full_path)  # stash for future reference
            #print(self._full_path)
            #self.filepath.put(self._full_path)
            self.resource_uid = str(uuid.uuid4())
            self._full_path = self.filepath.get()

            super().stage()
        else:
            raise RuntimeError("Not connected")


    def unstage(self):
        if(self.connected):
            set_and_wait(self.ignore_sel, 1)
            return super().unstage()
        else:
            raise RuntimeError("Not connected")

    def kickoff(self):
        print('kickoff', self.name)
        self._ready_to_collect = True
        "Start writing data into the file."

        set_and_wait(self.ignore_sel, 0)

        # Return a 'status object' that immediately reports we are 'done' ---
        # ready to collect at any time.
        return NullStatus()

    def complete(self):
        print('complete', self.name, '| filepath', self._full_path)
        if not self._ready_to_collect:
            raise RuntimeError("must called kickoff() method before calling complete()")
        # Stop adding new data to the file.
        set_and_wait(self.ignore_sel, 1)
        #while not os.path.isfile(self._full_path):
        #    ttime.sleep(.1)
        return NullStatus()

    def collect(self):
        """
        Record a 'datum' document in the filestore database for each encoder.

        Return a dictionary with references to these documents.
        """
        print('collect', self.name)
        self._ready_to_collect = False

        # Create an Event document and a datum record in filestore for each line
        # in the text file.
        now = ttime.time()
        ttime.sleep(1)  # wait for file to be written by pizza box
        if os.path.isfile(self._full_path):
            #with open(self._full_path, 'r') as f:
                #linecount = len(list(f))
            #chunk_count = linecount // self.chunk_size + int(linecount % self.chunk_size != 0)
            #for chunk_num in range(chunk_count):
                ## fake uid, nothing is saved! for testing ONLY!
            datum_uid = str(uuid.uuid4())
            data = {self.name: datum_uid}
            yield {'data': data,
                       'timestamps': {key: now for key in data}, 'time': now}
        else:
            print('collect {}: File was not created'.format(self.name))

    def describe_collect(self):
        # TODO Return correct shape (array dims)
        now = ttime.time()
        return {self.name: {self.name:
                     {'filename': self._full_path,
                      'devname': self.dev_name.value,
                      'source': 'pizzabox-enc-file',
                      'external': 'FILESTORE:',
                      'shape': [1024, 5],
                      'dtype': 'array'}}}


class DigitalOutput(Device):
    """ DigitalOutput """
    enable = Cpt(EpicsSignal, '}Ena-Cmd')
    period_sp = Cpt(EpicsSignal, '}Period-SP')
    unit_sel = Cpt(EpicsSignal, '}Unit-Sel')
    dutycycle_sp = Cpt(EpicsSignal, '}DutyCycle-SP')
    default_pol = Cpt(EpicsSignal, '}Dflt-Sel')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ready_to_collect = False
        if self.connected:
            self.enable.put(0)


class DigitalInput(Device):
    """This class defines components but does not implement actual reading.

    See DigitalInputFS """
    data_I = Cpt(EpicsSignal, '}Raw:Data-I_')
    sec_array = Cpt(EpicsSignal, '}T:sec_Bin_')
    nsec_array = Cpt(EpicsSignal, '}T:nsec_Bin_')
    index_array = Cpt(EpicsSignal, '}Cnt:Index_Bin_')
    data_array = Cpt(EpicsSignal, '}Data_Bin_')
    # The '$' in the PV allows us to write 40 chars instead of 20.
    filepath = Cpt(EpicsSignal, '}ID:File.VAL', string=True)
    dev_name = Cpt(EpicsSignal, '}DevName')

    ignore_rb = Cpt(EpicsSignal, '}Ignore-RB')
    ignore_sel = Cpt(EpicsSignal, '}Ignore-Sel')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ready_to_collect = False
        if self.connected:
            self.ignore_sel.put(1)



class DIFS(DigitalInput):
    "Encoder Device, when read, returns references to data in filestore."
    chunk_size = 1024

    def stage(self):
        "Set the filename and record it in a 'resource' document in the filestore database."


        print(self.name, 'stage')
        self._full_path = self.filepath.get()
        #DIRECTORY = ISS_ROOT_DIRECTORY
        #rpath = 'pizza_box_data'
        #filename = 'di_' + str(uuid.uuid4())[:6]
        #full_path = os.path.join(rpath, filename)
        #self._full_path = os.path.join(DIRECTORY, full_path)  # stash for future reference
        #if len(self._full_path) > 40:
            #raise RuntimeError("Stupidly, EPICS limits the file path to 80 characters. "
                           #"Choose a different DIRECTORY with a shorter path. (I know....)")
        #self._full_path = os.path.join(DIRECTORY, full_path)  # stash for future reference
        #self.filepath.put(self._full_path)
        self.resource_uid = str(uuid.uuid4())

        super().stage()

    def unstage(self):
        set_and_wait(self.ignore_sel, 1)
        return super().unstage()

    def kickoff(self):
        print('kickoff', self.name)
        self._ready_to_collect = True
        "Start writing data into the file."

        set_and_wait(self.ignore_sel, 0)

        # Return a 'status object' that immediately reports we are 'done' ---
        # ready to collect at any time.
        return NullStatus()

    def complete(self):
        print('complete', self.name, '| filepath', self._full_path)
        if not self._ready_to_collect:
            raise RuntimeError("must called kickoff() method before calling complete()")
        # Stop adding new data to the file.
        set_and_wait(self.ignore_sel, 1)
        #while not os.path.isfile(self._full_path):
        #    ttime.sleep(.1)
        return NullStatus()

    def collect(self):
        """
        Record a 'datum' document in the filestore database for each encoder.

        Return a dictionary with references to these documents.
        """
        print('collect', self.name)
        self._ready_to_collect = False

        # Create an Event document and a datum record in filestore for each line
        # in the text file.
        now = ttime.time()
        ttime.sleep(1)  # wait for file to be written by pizza box
        if os.path.isfile(self._full_path):
            #with open(self._full_path, 'r') as f:
                #linecount = len(list(f))
            #chunk_count = linecount // self.chunk_size + int(linecount % self.chunk_size != 0)
            #for chunk_num in range(chunk_count):
            data = {self.name: str(uuid.uuid4())}

            yield {'data': data,
                       'timestamps': {key: now for key in data}, 'time': now}
        else:
            print('collect {}: File was not created'.format(self.name))

    def describe_collect(self):
        # TODO Return correct shape (array dims)
        now = ttime.time()
        return {self.name: {self.name:
                     {'filename': self._full_path,
                      'devname': self.dev_name.value,
                      'source': 'pizzabox-di-file',
                      'external': 'FILESTORE:',
                      'shape': [1024, 5],
                      'dtype': 'array'}}}

class PizzaBoxFS(Device):
    ts_sec = Cpt(EpicsSignal, '}T:sec-I')
    #internal_ts_sel = Cpt(EpicsSignal, '}T:Internal-Sel')

    enc1 = Cpt(EncoderFS, ':1')
    enc2 = Cpt(EncoderFS, ':2')
    enc3 = Cpt(EncoderFS, ':3')
    enc4 = Cpt(EncoderFS, ':4')
    di = Cpt(DIFS, ':DI')
    do0 = Cpt(DigitalOutput, '-DO:0')
    do1 = Cpt(DigitalOutput, '-DO:1')
    do2 = Cpt(DigitalOutput, '-DO:2')
    do3 = Cpt(DigitalOutput, '-DO:3')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # must use internal timestamps or no bytes are written

    def kickoff(self):
        "Call encoder.kickoff() for every encoder."
        for attr_name in ['enc1', 'enc2', 'enc3', 'enc4']:
            status = getattr(self, attr_name).kickoff()
            print("Eli's test", self.attr_name)
        # it's fine to just return one of the status objects
        return status

    def collect(self):
        "Call encoder.collect() for every encoder."
        # Stop writing data to the file in all encoders.
        for attr_name in ['enc1', 'enc2', 'enc3', 'enc4']:
            set_and_wait(getattr(self, attr_name).ignore_sel, 1)
        # Now collect the data accumulated by all encoders.
        for attr_name in ['enc1', 'enc2', 'enc3', 'enc4']:
            yield from getattr(self, attr_name).collect()




class Adc(Device):
    file_size = Cpt(EpicsSignal, '}FileSize')
    reset = Cpt(EpicsSignal, '}Rst-Cmd')
    filepath = Cpt(EpicsSignal, '}ID:File.VAL', string=True)
    sec_array = Cpt(EpicsSignal, '}T:sec_Bin_')
    nsec_array = Cpt(EpicsSignal, '}T:nsec_Bin_')
    #pos_array = Cpt(EpicsSignal, '}Cnt:Pos_Bin_')
    index_array = Cpt(EpicsSignal, '}Cnt:Index_Bin_')
    data_array = Cpt(EpicsSignal, '}Data_Bin_')
    sample_rate = Cpt(EpicsSignal,'}F:Sample-I_', write_pv='}F:Sample-SP')
    enable_averaging = Cpt(EpicsSignal, '}Avrg-Sts', write_pv='}Avrg-Sel')
    averaging_points = Cpt(EpicsSignal, '}Avrg-SP')
    averaging_points_rbv = Cpt(EpicsSignal, '}GP-ADC:Reg0-RB_')
    volt_array = Cpt(EpicsSignal, '}V-I')
    volt = Cpt(EpicsSignal, '}E-I')
    offset = Cpt(EpicsSignal, '}Offset')
    dev_name = Cpt(EpicsSignal, '}DevName')
    dev_saturation = Cpt(EpicsSignal, '}DevSat')
    polarity = 'neg'

    enable_sel = Cpt(EpicsSignal, '}Ena-Sel')
    enable_rb = Cpt(EpicsSignal, '}Ena-Sts')

    def timeout_handler(self, signum, frame):
        print("{}.connected timeout".format(self.name))
        raise Exception("end of time")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ready_to_collect = False

        #signal.signal(signal.SIGALRM, self.timeout_handler)
        #signal.setitimer(signal.ITIMER_REAL, 2)
        #try:
        #    while(self.connected == False):
        #        pass
        if self.connected:
            #self.enable_sel.put(1)
            #self.sample_rate.put(350)
            self.enable_averaging.put(1)
            if self.averaging_points.value == 0:
                self.averaging_points.put("1024")
        #except Exception as exc:
        #    pass
        #signal.alarm(0)



class AdcFS(Adc):
    "Adc Device, when read, returns references to data in filestore."
    chunk_size = 1024

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def stage(self):
        "Set the filename and record it in a 'resource' document in the filestore database."


        # don't set a file path (do it externally)
        if(self.connected):
            print(self.name, 'is staging')
            #DIRECTORY = ISS_ROOT_DIRECTORY
            #rpath = 'pizza_box_data'
            #filename = 'an_' + str(uuid.uuid4())[:6]
            #full_path = os.path.join(rpath, filename)
            #self._full_path = os.path.join(DIRECTORY, full_path)  # stash for future reference
            #if len(self._full_path) > 40:
                #raise RuntimeError("Stupidly, EPICS limits the file path to 80 characters. "
                               #"Choose a different DIRECTORY with a shorter path. (I know....)")
            #self._full_path = os.path.join(DIRECTORY, full_path)  # stash for future reference
            #print(self._full_path)
            self._full_path = self.filepath.get()
            self.resource_uid = uuid.uuid4()
            print(self.name, 'staging complete')
            super().stage()
        else:
            raise RuntimeError("Not connected")

    def unstage(self):
        if(self.connected):
            set_and_wait(self.enable_sel, 1)
            return super().unstage()
        else:
            raise RuntimeError("Not connected")

    def kickoff(self):
        print('kickoff', self.name)
        self._ready_to_collect = True
        "Start writing data into the file."

        set_and_wait(self.enable_sel, 0)

        # Return a 'status object' that immediately reports we are 'done' ---
        # ready to collect at any time.
        return NullStatus()

    def complete(self):
        print('complete', self.name, '| filepath', self._full_path)
        if not self._ready_to_collect:
            raise RuntimeError("must called kickoff() method before calling complete()")
        # Stop adding new data to the file.
        set_and_wait(self.enable_sel, 1)
        return NullStatus()

    def collect(self):
        """
        Record a 'datum' document in the filestore database for each encoder.

        Return a dictionary with references to these documents.
        """
        print('collecting', self.name)
        self._ready_to_collect = False

        # Create an Event document and a datum record in filestore for each line
        # in the text file.
        now = ttime.time()
        ttime.sleep(1)  # wait for file to be written by pizza box
        if os.path.isfile(self._full_path):
            #print(self._full_path)
            #with open(self._full_path, 'r') as f:
                #linecount = 0
                #for ln in f:
                    #linecount += 1
            #chunk_count = linecount // self.chunk_size + int(linecount % self.chunk_size != 0)
            #for chunk_num in range(chunk_count):
            datum_uid = str(uuid.uuid4())
            data = {self.name: datum_uid}

            yield {'data': data,
                   'timestamps': {key: now for key in data}, 'time': now}
        else:
            print('collect {}: File was not created'.format(self.name))

    def describe_collect(self):
        # TODO Return correct shape (array dims)
        now = ttime.time()
        return {self.name: {self.name:
                     {'filename': self._full_path,
                      'devname': self.dev_name.value,
                      'source': 'pizzabox-adc-file',
                      'external': 'FILESTORE:',
                      'shape': [5,],
                      'dtype': 'array'}}}


class PizzaBoxAnalogFS(Device):
    #internal_ts_sel = Cpt(EpicsSignal, 'Gen}T:Internal-Sel')

    adc1 = Cpt(AdcFS, 'ADC:1')
    adc6 = Cpt(AdcFS, 'ADC:6')
    adc7 = Cpt(AdcFS, 'ADC:7')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # must use internal timestamps or no bytes are written
        # self.stage_sigs[self.internal_ts_sel] = 1

    def kickoff(self):
        "Call encoder.kickoff() for every encoder."
        for attr_name in ['adc1']: #, 'adc2', 'adc3', 'adc4']:
            status = getattr(self, attr_name).kickoff()
        # it's fine to just return one of the status objects
        return status

    def collect(self):
        "Call adc.collect() for every encoder."
        # Stop writing data to the file in all encoders.
        for attr_name in ['adc1']: #, 'adc2', 'adc3', 'adc4']:
            set_and_wait(getattr(self, attr_name).enable_sel, 0)
        # Now collect the data accumulated by all encoders.
        for attr_name in ['adc1']: #, 'adc2', 'adc3', 'adc4']:
            yield from getattr(self, attr_name).collect()

pb1 = PizzaBoxFS('XF:08IDA-CT{Enc01', name = 'pb1')
pb2 = PizzaBoxFS('XF:08IDA-CT{Enc02', name = 'pb2')
pb4 = PizzaBoxFS('XF:08IDA-CT{Enc04', name = 'pb4') #PB inside hutch B (for now)
pb5 = PizzaBoxFS('XF:08IDA-CT{Enc05', name = 'pb5')
pb6 = PizzaBoxFS('XF:08IDA-CT{Enc06', name = 'pb6')
pb7 = PizzaBoxFS('XF:08IDA-CT{Enc07', name = 'pb7')
pb9 = PizzaBoxFS('XF:08IDA-CT{Enc09', name = 'pb9')
pb9.enc1.pulses_per_deg = 360000
pba1 = PizzaBoxAnalogFS('XF:08IDB-CT{GP1-', name = 'pba1')
pba2 = PizzaBoxAnalogFS('XF:08IDB-CT{GP-', name = 'pba2')


