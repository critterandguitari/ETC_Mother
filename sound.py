import alsaaudio, audioop

inp = None
etc = None

def init (etc_object) :
    global inp, etc
    etc = etc_object
    #setup alsa for sound in
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NONBLOCK)
    inp.setchannels(1)
    inp.setrate(8000)
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    inp.setperiodsize(300)

def recv() :
    global inp, etc
    # get audio
    l,data = inp.read()
    etc.trig = False
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
                etc.audio_in[i] = avg
            except :
                pass
        l,data = inp.read()


