import os
import json
import pytest
from src.stem_generator import create_synthetic_rhythm_stem
from src.audio_processor import load_wav_file, compute_energy_envelope, calculate_syncopation_index
from src.agent import AgenticRhythmOptimizer, run_agentic_optimization_pipeline

@pytest.fixture(scope="module")
def setup_test_stems():
    os.makedirs("data/stems", exist_ok=True)
    stem_file = "data/stems/test_amapiano.wav"
    create_synthetic_rhythm_stem(stem_file, duration=1.0, pattern_type="amapiano")
    yield stem_file

def test_audio_loading(setup_test_stems):
    stem_file = setup_test_stems
    assert os.path.exists(stem_file)
    data, sr = load_wav_file(stem_file)
    assert sr == 22050
    assert len(data) > 0

def test_dsp_feature_extraction(setup_test_stems):
    stem_file = setup_test_stems
    data, sr = load_wav_file(stem_file)
    envelope = compute_energy_envelope(data)
    assert len(envelope) > 0
    
    sync_index = calculate_syncopation_index(envelope)
    assert 0.0 <= sync_index <= 1.0

def test_agentic_optimizer(setup_test_stems):
    stem_file = setup_test_stems
    agent = AgenticRhythmOptimizer(target_confidence=0.80)
    report = agent.optimize_detection_parameters(stem_file)
    
    assert "status" in report
    assert report["confidence_score"] > 0.0
    assert len(report["tuning_history"]) > 0

def test_full_agent_pipeline_execution():
    run_agentic_optimization_pipeline()
    assert os.path.exists("docs/agent_diagnostics.json")
    with open("docs/agent_diagnostics.json") as f:
        data = json.load(f)
        assert isinstance(data, list)
