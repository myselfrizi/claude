import math, random, wave, array
SR = 44100; DUR = 13.0; N = int(SR * DUR)
buf = [0.0] * N
random.seed(7)
def f(note):  # midi -> hz
    return 440.0 * 2 ** ((note - 69) / 12)
def add(t0, dur, fn, gain):
    a = int(t0 * SR); b = min(N, a + int(dur * SR))
    for i in range(a, b):
        buf[i] += gain * fn((i - a) / SR)
def pluck(note, decay=3.2):
    hz = f(note)
    def fn(t):
        env = min(1, t / 0.004) * math.exp(-decay * t)
        w = 2 * math.pi * hz * t
        return env * (math.sin(w) + 0.35 * math.sin(2 * w) * math.exp(-4 * t) + 0.15 * math.sin(3 * w) * math.exp(-7 * t))
    return fn
def bass(note):
    hz = f(note)
    def fn(t):
        env = min(1, t / 0.008) * math.exp(-2.5 * t)
        return env * (math.sin(2 * math.pi * hz * t) + 0.2 * math.sin(4 * math.pi * hz * t))
    return fn
def shaker(t):
    return random.uniform(-1, 1) * math.exp(-40 * t)
def boom(t):
    hz = 70 * math.exp(-1.5 * t) + 38
    return math.sin(2 * math.pi * hz * t) * math.exp(-3.2 * t) * min(1, t / 0.003)
def stab(notes, decay=1.6):
    def fn(t):
        env = min(1, t / 0.01) * math.exp(-decay * t)
        s = 0
        for n in notes:
            hz = f(n); w = 2 * math.pi * hz * t
            s += math.sin(w) + 0.5 * math.sin(2 * w) + 0.3 * math.sin(3 * w) + 0.15 * math.sin(5 * w)
        return env * s / len(notes)
    return fn
def scratch(t):
    hz = 900 * math.exp(-9 * t) + 120
    return (0.6 * math.sin(2 * math.pi * hz * t) + 0.4 * random.uniform(-1, 1)) * math.sin(math.pi * min(1, t / 0.22))

E = 0.25  # eighth note at 120 bpm
# Part A: playful melody (0 - 2.6)
melA = [76, 79, 84, 79, 81, 79, 76, 74, 76, 79]
for k, n in enumerate(melA):
    add(k * E, 0.6, pluck(n), 0.16)
for t0, n in [(0, 48), (0.5, 48), (1.0, 43), (1.5, 43), (2.0, 45)]:
    add(t0, 0.5, bass(n), 0.20)
for k in range(10):
    add(k * E + E / 2, 0.08, shaker, 0.025)
# record scratch + minor sting
add(2.58, 0.24, scratch, 0.10)
add(2.64, 1.6, boom, 0.30)
add(2.64, 2.2, stab([36, 48, 51, 55]), 0.17)
# drone under the threat (4.8 - 8.1)
def drone(t):
    sw = min(1, t / 0.4) * min(1, (3.3 - t) / 0.3)
    trem = 0.8 + 0.2 * math.sin(2 * math.pi * 5 * t)
    return sw * trem * (math.sin(2 * math.pi * f(36) * t) + 0.6 * math.sin(2 * math.pi * f(43) * t) + 0.25 * math.sin(2 * math.pi * f(48) * t))
add(4.8, 3.3, drone, 0.09)
for t0 in (5.0, 6.0):
    add(t0, 1.4, boom, 0.32)
    add(t0, 1.0, stab([48, 51, 55], 2.6), 0.13)
add(7.0, 1.0, stab([47, 50, 55], 2.2), 0.09)  # unresolved tension
# Part B: melody returns (8.4 - 11)
melB = [79, 76, 72, 76, 79, 84, 83, 84, 79, 76]
for k, n in enumerate(melB):
    add(8.45 + k * E, 0.6, pluck(n), 0.15)
for t0, n in [(8.45, 48), (8.95, 48), (9.45, 41), (9.95, 41), (10.45, 43)]:
    add(t0, 0.5, bass(n), 0.20)
for k in range(10):
    add(8.45 + k * E + E / 2, 0.08, shaker, 0.022)
# sparkle chime when the bowl is home
for k, n in enumerate([84, 88, 91, 96]):
    add(9.5 + k * 0.06, 1.0, pluck(n, 4.5), 0.06)
# outro: resolve
for k, n in enumerate([81, 79, 76, 74]):
    add(10.95 + k * E, 0.6, pluck(n), 0.15)
add(10.95, 0.5, bass(41), 0.2); add(11.45, 0.5, bass(43), 0.2)
add(11.95, 1.05, stab([60, 64, 67, 72], 1.4), 0.15)
add(11.95, 1.05, bass(36), 0.24)
add(11.95, 1.05, pluck(84, 1.6), 0.10)
# gentle soft-clip, normalize to -1 dBFS, fade tail
peak = max(abs(x) for x in buf) or 1
g = 0.89 / peak
out = array.array('h')
for i, x in enumerate(buf):
    y = math.tanh(1.2 * x * g) / math.tanh(1.2)
    fade = min(1, (N - i) / (0.4 * SR))
    out.append(int(max(-1, min(1, y * fade)) * 32000))
w = wave.open('audio.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes()); w.close()
print('ok', peak)
