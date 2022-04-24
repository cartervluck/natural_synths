import math
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
import random

rate, data = wavfile.read('test3.wav')
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

for clip in clips[:-1]:
    transformed = np.abs(np.fft.rfft(clip))
    transformed[:16] = 0
    transformed[7040:] = 0
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

print("---------------------------")

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
    #avg = avg*filter
    avg = np.concatenate((avg,avg),0)
    print(avg.astype(np.int32))
    wavfile.write("OUTPUT_"+p+"_4.wav",rate,avg.astype(np.int32))
    xscale = np.array(range(len(avg)))
    print(avg[-1],avg[-2])
    plt.plot(xscale,avg)
    #plt.show()

plt.show()