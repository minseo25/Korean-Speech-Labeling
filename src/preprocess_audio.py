import os
import subprocess
from pydub.utils import mediainfo
from omegaconf import DictConfig
import hydra

def trim_audio_files(folder_path: str, trim_start: int, trim_end: int) -> None:
    files = os.listdir(folder_path)
    
    for file in files:
        if file.endswith('.m4a'):
            print(f"Processing {file}...")

            file_path = os.path.join(folder_path, file)
            temp_file_path = os.path.join(folder_path, f"temp_{file}")

            try:
                audio_info = mediainfo(file_path)
                duration = float(audio_info['duration'])

                start_time = trim_start / 1000
                end_time = duration - (trim_end / 1000)

                if end_time <= start_time:
                    print(f"Skipping {file} due to invalid trim times.")
                    continue

                command = [
                    "ffmpeg",
                    "-i", file_path,
                    "-ss", str(start_time),
                    "-to", str(end_time),
                    "-c", "copy",
                    temp_file_path
                ]
                subprocess.run(command, check=True)

                if os.path.exists(temp_file_path):
                    os.remove(file_path)
                    os.rename(temp_file_path, file_path)
                
                print(f"Trimmed and saved {file}.")
            except subprocess.CalledProcessError as e:
                if os.path.exists(temp_file_path):
                    try:
                        os.remove(temp_file_path)
                    except PermissionError:
                        print(f"Failed to delete temp file: {temp_file_path}")
                print(f"Failed to process {file}: {e}")

@hydra.main(version_base='1.3', config_path='../configs', config_name='preprocess_audio.yaml')
def main(cfg: DictConfig) -> None:
    folder_path = f'data/{cfg.audio_dir}/korean_audio'
    trim_audio_files(folder_path, trim_start=cfg.trim_start, trim_end=cfg.trim_end)

if __name__ == "__main__":
    main()