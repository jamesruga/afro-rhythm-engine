import os
from src.stem_generator import generate_stems
from src.agent import run_agentic_optimization_pipeline

if __name__ == "__main__":
    print("Initializing AfroRhythm Engine Execution...")
    os.makedirs("data/stems", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    generate_stems()
    run_agentic_optimization_pipeline()
    print("AfroRhythm Engine Pipeline completed successfully.")
