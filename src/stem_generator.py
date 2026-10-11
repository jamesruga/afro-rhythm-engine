import wave
import struct
import math
import os
import numpy as np

SAMPLE_RATE = 44100

def karplus_strong(freq, duration, sr=22050, decay=0.985):
    """Karplus-Strong plucked string synthesis for authentic Benga electric guitar."""
    buf_len = max(2, int(sr / freq))
    buf = np.random.uniform(-1.0, 1.0, buf_len)
    num_samples = int(sr * duration)
    samples = np.zeros(num_samples)
    
    ptr = 0
    for i in range(num_samples):
        val = buf[ptr]
        samples[i] = val
        next_ptr = (ptr + 1) % buf_len
        buf[ptr] = 0.5 * (val + buf[next_ptr]) * decay
        ptr = next_ptr
    return samples

def amapiano_log_drum(duration, sr=22050, start_freq=170, end_freq=42):
    """Amapiano Log Drum FM synthesis with wood resonance and sub-bass pitch drop."""
    num_samples = int(sr * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    freq_env = end_freq + (start_freq - end_freq) * np.exp(-18 * t)
    phase = 2 * np.pi * np.cumsum(freq_env) / sr
    
    fm_modulator = np.sin(phase * 2.0) * 0.35
    carrier = np.sin(phase + fm_modulator)
    sub = np.sin(phase * 0.5) * 0.3
    signal = np.tanh((carrier + sub) * 2.0)
    
    amp_env = np.exp(-4.5 * t)
    return signal * amp_env

def isukuti_bell(freq, duration, sr=22050):
    """Inharmonic modal synthesis for African metallic Isukuti bell."""
    num_samples = int(sr * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    m1 = np.sin(2 * np.pi * freq * t) * 0.5
    m2 = np.sin(2 * np.pi * (freq * 1.58) * t) * 0.3
    m3 = np.sin(2 * np.pi * (freq * 2.42) * t) * 0.2
    amp = np.exp(-14 * t)
    return (m1 + m2 + m3) * amp

def isukuti_membrane(duration, sr=22050):
    """Acoustic Isukuti skin drum strike."""
    num_samples = int(sr * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    pitch_env = 130 * np.exp(-22 * t) + 50
    phase = 2 * np.pi * np.cumsum(pitch_env) / sr
    body = np.sin(phase) * np.exp(-7 * t)
    noise = np.random.uniform(-0.15, 0.15, num_samples) * np.exp(-30 * t)
    return body + noise

def save_wav(filename, signal, sr=22050):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    signal = signal / (np.max(np.abs(signal)) + 1e-6)
    scaled = (signal * 32767).astype(np.int16)
    
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        for val in scaled:
            wf.writeframes(struct.pack('<h', val))

def generate_stems():
    sr = SAMPLE_RATE
    total_sec = 4.0
    num_samples = int(sr * total_sec)
    
    # 1. Benga Guitar Stem
    benga = np.zeros(num_samples)
    scale = [329.63, 392.00, 493.88, 587.33, 659.25, 493.88, 392.00, 329.63]
    step_time = 0.125
    for i in range(32):
        t_idx = int(i * step_time * sr)
        note_freq = scale[i % len(scale)]
        pluck = karplus_strong(note_freq, 0.4, sr)
        end_idx = min(num_samples, t_idx + len(pluck))
        benga[t_idx:end_idx] += pluck[:end_idx - t_idx] * 0.7
    save_wav('data/stems/benga_stem.wav', benga)

    # 2. Amapiano Log Drum Stem
    amapiano = np.zeros(num_samples)
    rhythm_hits = [0.0, 0.375, 0.75, 1.125, 1.5, 2.0, 2.375, 2.75, 3.125, 3.5]
    for hit_t in rhythm_hits:
        t_idx = int(hit_t * sr)
        log_hit = amapiano_log_drum(0.5, sr)
        end_idx = min(num_samples, t_idx + len(log_hit))
        amapiano[t_idx:end_idx] += log_hit[:end_idx - t_idx]
    save_wav('data/stems/amapiano_stem.wav', amapiano)

    # 3. 12/8 Isukuti Polyrhythm Stem
    isukuti = np.zeros(num_samples)
    bell_pattern = [0.0, 0.166, 0.333, 0.5, 0.666, 0.833, 1.0, 1.166, 1.333, 1.5]
    for hit_t in bell_pattern:
        for loop in range(2):
            t_idx = int((hit_t + loop * 2.0) * sr)
            is_high = (hit_t in [0.0, 0.5, 1.0, 1.5])
            bell = isukuti_bell(880 if is_high else 587, 0.25, sr)
            drum = isukuti_membrane(0.35, sr)
            end_idx = min(num_samples, t_idx + len(bell))
            isukuti[t_idx:end_idx] += bell[:end_idx - t_idx] * 0.5 + drum[:end_idx - t_idx] * 0.6
    save_wav('data/stems/isukuti_stem.wav', isukuti)

if __name__ == '__main__':
    generate_stems()
    print("General MIDI XG Acoustic Physical Modeling Stems Successfully Generated.")

def create_synthetic_rhythm_stem(filename, duration=1.0, pattern_type="amapiano", sr=22050):
    if pattern_type == "amapiano":
        signal = amapiano_log_drum(duration, sr=sr)
    elif pattern_type == "isukuti":
        signal = isukuti_membrane(duration, sr=sr)
    else:
        signal = karplus_strong(220, duration, sr=sr)
    save_wav(filename, signal, sr=sr)
    return filename
