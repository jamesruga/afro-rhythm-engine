import os
import wave
import struct
import numpy as np

def create_synthetic_rhythm_stem(filename, duration=3.0, sr=22050, pattern_type="amapiano"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    t = np.linspace(0, duration, int(sr * duration), False)
    signal = np.zeros_like(t)

    # 120 BPM -> 0.5s per beat
    beat_length = int(sr * 0.5)
    
    if pattern_type == "amapiano":
        # Log-drum pitch slides & syncopated sub-bass
        for i in range(0, len(t), beat_length):
            segment_len = min(beat_length, len(t) - i)
            t_seg = t[i:i+segment_len] - t[i]
            # Frequency sweep from 120Hz down to 40Hz (characteristic log drum)
            freq = np.linspace(120, 40, segment_len)
            signal[i:i+segment_len] += 0.8 * np.sin(2 * np.pi * freq * t_seg) * np.exp(-3 * t_seg)

    elif pattern_type == "benga":
        # Fast 16th note guitar syncopation (high frequency arpeggios)
        sixteenth = int(sr * 0.125)
        notes = [440, 554.37, 659.25, 880] # A major arpeggio
        for idx, i in enumerate(range(0, len(t), sixteenth)):
            segment_len = min(sixteenth, len(t) - i)
            t_seg = t[i:i+segment_len] - t[i]
            note_freq = notes[idx % len(notes)]
            signal[i:i+segment_len] += 0.6 * np.sin(2 * np.pi * note_freq * t_seg) * np.exp(-8 * t_seg)

    elif pattern_type == "isukuti":
        # 12/8 Polyrhythmic triplet bell and drum accents
        triplet = int(sr * 0.166)
        for idx, i in enumerate(range(0, len(t), triplet)):
            if idx % 3 != 1: # Off-beat African polyrhythmic accent
                segment_len = min(triplet, len(t) - i)
                t_seg = t[i:i+segment_len] - t[i]
                signal[i:i+segment_len] += 0.7 * np.sin(2 * np.pi * 300 * t_seg) * np.exp(-12 * t_seg)

    # Normalize audio signal
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        signal = signal / max_val * 0.9

    # Write PCM WAV file
    packed_audio = struct.pack(f'<{len(signal)}h', *(int(s * 32767) for s in signal))
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sr)
        wav_file.writeframes(packed_audio)
    
    print(f"[Stem Generator] Successfully created synthetic {pattern_type} audio stem: {filename}")

if __name__ == "__main__":
    create_synthetic_rhythm_stem("data/stems/amapiano_logdrum.wav", pattern_type="amapiano")
    create_synthetic_rhythm_stem("data/stems/benga_guitar.wav", pattern_type="benga")
    create_synthetic_rhythm_stem("data/stems/isukuti_percussion.wav", pattern_type="isukuti")
