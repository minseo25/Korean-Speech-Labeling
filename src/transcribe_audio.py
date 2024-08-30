import whisper, json, os
import torch
from omegaconf import DictConfig
import hydra

model = whisper.load_model("medium")

def get_transcripts(audio_path: str, subtitle_path: str, start_idx: int) -> None:
    audio_files = os.listdir(audio_path)
    i, N = start_idx, len(audio_files)

    for audio_file in audio_files[i:]:
        print(f"Processing ({i+1}/{N}) {audio_file}...")
        i += 1
        # get the name of the file without the extension
        name = os.path.splitext(audio_file)[0]
        output_file = os.path.join(subtitle_path, f"{name}.json")

        # Check if the JSON file already exists
        if os.path.exists(output_file):
            print(f"Skipping {audio_file}, transcript already exists.")
            continue

        # Transcribe the audio file
        audio_file_path = os.path.join(audio_path, audio_file)
        result = model.transcribe(audio_file_path, language="ko")

        # Save the transcription to a file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

@hydra.main(version_base='1.3', config_path='../configs', config_name='transcribe_audio.yaml')
def main(cfg: DictConfig) -> None:
    audio_path = os.path.join('data', cfg.audio_dir, 'korean_audio')
    subtitle_path = os.path.join('data', cfg.audio_dir, 'korean_subtitle')
    
    if not os.path.exists(subtitle_path):
        os.makedirs(subtitle_path)

    get_transcripts(audio_path, subtitle_path, cfg.start_idx)

    if torch.cuda.is_available():
        del model  # Delete the model to free up memory
        torch.cuda.empty_cache()  # Explicitly clear the GPU memory

if __name__ == "__main__":
    main()
