import alsaaudio, audioop
import time

inp = None
etc = None
trig_this_time = 0
trig_last_time = 0

def init (etc_object) :
    global inp, etc, trig_this_time, trig_last_time
    etc = etc_object
    #setup alsa for sound in
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NONBLOCK)
    inp.setchannels(1)
    inp.setrate(8000)
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    inp.setperiodsize(300)
    trig_last_time = time.time()
    trig_this_time = time.time()

def recv() :
    global inp, etc, trig_this_time, trig_last_time
    # get audio
    l,data = inp.read()
    peak = 0
    while l:
        for i in range(0,100) :
            try :
                avg = audioop.getsample(data, 2, i * 3)
                avg += audioop.getsample(data, 2, (i * 3) + 1)
                avg += audioop.getsample(data, 2, (i * 3) + 2)
                avg = avg / 3
                if (avg > 20000) :
                    trig_this_time = time.time()
                    if (trig_this_time - trig_last_time) > .05:
                        etc.trig = True
                        trig_last_time = trig_this_time
                if avg > peak :
                    etc.audio_peak = avg
                    peak = avg
                etc.audio_in[i] = avg
            except :
                pass
        l,data = inp.read()


