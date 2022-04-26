import math
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
import random
from pynput import keyboard
import time
import simpleaudio as sa
import sys

filename = "input.wav"

if len(sys.argv) > 1:
  filename = sys.argv[1]


rate, data = wavfile.read(filename)
try:
    data = np.sum(data,1)
except np.AxisError:
    print("Already mono input")
nclips = math.floor(data.size/rate)
clips = np.split(data,[rate * i for i in range(1,nclips+1)])
print(rate)

chrom = [0.51098633,0.54136719,0.57355469,0.60767578,0.64380859,0.68208984,0.72263672,0.765625,0.81113281,0.859375,0.91046875,0.96461914] # starts at C, ends at B

pitch_names = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]

sorted_clips = {i:[] for i in pitch_names}

c = 1
m = len(clips)-1

#print(len(clips))

for clip in clips[:-1]:
    transformed = np.abs(np.fft.rfft(clip))
    transformed[:16] = 0
    transformed[4070:] = 0
    #transformed = transformed[16:7040]
    if np.argmax(transformed) == 0: continue
    freq = (np.argmax(transformed))
    while freq < 1:
        freq *= 2
    while freq > 1:
        freq /= 2
    #print(freq)
    min_diff = 100
    min = 0
    for i,f in enumerate(chrom):
        diff = np.abs(1-freq/f)
        if diff < min_diff:
            min_diff = diff
            min = i
    sorted_clips[pitch_names[min]].append(np.fft.irfft(transformed))
    #xscale = np.array(range(200))
    #plt.plot(xscale,transformed[:200])
    #plt.show()
    
    print("processed " + str(c) + " out of " + str(m))
    c += 1

print("---------------------------")

sounds = {}

for p in pitch_names:
    mat = sorted_clips[p]
    try:
        avg = mat[0]
    except:
        continue
    for clip in mat[1:]:
        #if random.randint(1,3) == 1:
        avg = np.add(avg,clip)
    avg = avg * 100000 / len(mat)
    avg = avg[math.floor(len(avg)/10):math.ceil(9*len(avg)/10)]
    filter = 2*np.sin(np.pi/(len(avg)*2)*(len(avg)/2 + np.linspace(0.0,len(avg),len(avg),False)))**4
    avg = avg*filter
    print("FILTER",filter)
    xscale = np.array(range(len(avg)))
    print(avg[-1],avg[-2])
    plt.plot(xscale,avg)
    #plt.plot(xscale,filter)
    for k in range(5): avg = np.concatenate((avg,avg),0)
    avg *= 32767 / max(abs(avg))
    print(avg.astype(np.int32))
    wavfile.write("OUTPUT_"+p+".wav",rate,avg.astype(np.int16))
    sounds[p] = avg.astype(np.int16)

plt.show()

print("FILES GENERATED, ready to play")

playing = {}

key2note = {'a':"C",'s':"D",'d':"E","f":"F","g":"G","h":"A","j":"B","w":"C#","e":"D#","t":"F#","y":"G#","u":"A#"}

def on_press(key):
    try:
        note = key2note[key.char]
    except AttributeError:
        return
    except KeyError:
        return
    s = []
    try:
        s = sounds[note]
    except KeyError:
        return
    try:
        val = playing[note]
        if not val.is_playing():
            playing[note] = sa.play_buffer(s,1,2,rate)
        else:
            return
    except KeyError:
        playing[note] = sa.play_buffer(s,1,2,rate)

def on_release(key):
    try:
        note = key2note[key.char]
    except AttributeError:
        return
    except KeyError:
        return
    try:
        playing[note].stop()
        playing.pop(note)
    except KeyError:
        return

with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()

while True:
    time.sleep(1000)
