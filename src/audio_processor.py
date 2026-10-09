import wave
import struct
import numpy as np

def load_wav_file(filename):
    """Loads a WAV audio file into a normalized float array."""
    with wave.open(filename, 'rb') as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        sr = wf.getframerate()
        n_frames = wf.getnframes()
        raw_bytes = wf.readframes(n_frames)
        
        # Convert bytes to numpy float array
        if sampwidth == 2:
            data = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        else:
            data = np.frombuffer(raw_bytes, dtype=np.uint8).astype(np.float32) / 128.0 - 1.0

        if n_channels > 1:
            data = data[::n_channels] # Downmix to mono

        return data, sr

def compute_energy_envelope(signal, frame_size=512, hop_size=256):
    """Computes short-time Root Mean Square (RMS) energy envelope."""
    n_frames = 1 + (len(signal) - frame_size) // hop_size
    energy = np.zeros(max(1, n_frames))
    for i in range(n_frames):
        start = i * hop_size
        frame = signal[start:start + frame_size]
        energy[i] = np.sqrt(np.mean(frame**2)) if len(frame) > 0 else 0.0
    return energy

def calculate_syncopation_index(energy_envelope, threshold=0.1):
    """Calculates African syncopation index based on off-beat onset peak concentration."""
    peaks = np.where(energy_envelope > threshold)[0]
    if len(peaks) == 0:
        return 0.0
    
    # Measure off-beat concentration (even vs odd frame indices)
    off_beats = np.sum(peaks % 2 != 0)
    on_beats = np.sum(peaks % 2 == 0)
    
    total = off_beats + on_beats
    syncopation_score = float(off_beats / total) if total > 0 else 0.0
    return round(syncopation_score, 4)

def process_stem_analytics(audio_path):
    """Processes an audio stem and outputs a structured feature dictionary."""
    signal, sr = load_wav_file(audio_path)
    duration = len(signal) / sr
    envelope = compute_energy_envelope(signal)
    rms_energy = float(np.sqrt(np.mean(signal**2)))
    sync_score = calculate_syncopation_index(envelope)

    metrics = {
        "audio_path": audio_path,
        "sample_rate": sr,
        "duration_sec": round(duration, 2),
        "rms_energy": round(rms_energy, 4),
        "syncopation_index": sync_score
    }
    return metrics

if __name__ == "__main__":
    for stem in ["amapiano_logdrum.wav", "benga_guitar.wav", "isukuti_percussion.wav"]:
        path = f"data/stems/{stem}"
        analytics = process_stem_analytics(path)
        print(f"[DSP Engine Analytics] {stem}: {analytics}")
