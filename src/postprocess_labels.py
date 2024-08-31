import os
from collections import defaultdict
from omegaconf import DictConfig
import hydra

def confirm_and_delete(base_dir: str, delete_files: list, delete_folder: str) -> None:
    if not delete_files:
        return  # No files to delete
    
    for file in delete_files:
        try:
            os.remove(os.path.join(base_dir, file))
        except FileNotFoundError:
            print(f"File {file} not found, skipping deletion.")

    remaining_files = os.listdir(os.path.join(base_dir, delete_folder))
    if not remaining_files:
        # ask user to delete folder
        delete_folder_confirm = input(f"Delete folder {delete_folder} and its files? (y/n): ")
        if delete_folder_confirm.lower() == 'y':
            try:
                os.rmdir(os.path.join(base_dir, delete_folder))
                print(f"Deleted entire folder {delete_folder} and its files.")
            except OSError as e:
                print(f"Error deleting folder {delete_folder}: {e}")

def find_all_consecutive_durations(durations: list, count: int = 10) -> list:
    results = []
    consecutive = 0
    for i, duration in enumerate(durations):
        if duration.is_integer() and duration != 0:
            consecutive += 1
        else:
            if consecutive >= count:
                results.append((i - consecutive, consecutive))
            consecutive = 0
    if consecutive >= count:  # Check at the end of the list
        results.append((len(durations) - consecutive, consecutive))
    return results

def find_all_duplicate_transcripts(transcripts: list, min_count: int = 2) -> list:
    results = []
    consecutive = 1
    for i in range(1, len(transcripts)):
        if transcripts[i] == transcripts[i-1]:
            consecutive += 1
        else:
            if consecutive >= min_count:
                results.append((i - consecutive, consecutive))
            consecutive = 1
    if consecutive >= min_count:  # Check at the end of the list
        results.append((len(transcripts) - consecutive, consecutive))
    return results

def process_transcripts(base_dir: str) -> None:
    transcript_path = os.path.join(base_dir, 'transcripts.txt')
    with open(transcript_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    folder_data = defaultdict(list)
    for line in lines:
        parts = line.split('|')
        file_path = parts[0].strip()
        transcript = parts[1].strip()
        duration = float(parts[3].strip())
        folder = os.path.dirname(file_path)
        folder_data[folder].append((file_path, transcript, duration, line))

    new_lines = []
    
    for folder, files in folder_data.items():
        durations = [f[2] for f in files]
        transcripts = [f[1] for f in files]

        consecutive_duration_info = find_all_consecutive_durations(durations)
        duplicate_transcript_info = find_all_duplicate_transcripts(transcripts)
        
        delete_files = set()
        if consecutive_duration_info:
            print(f"Folder {folder} has a sequence of 10 or more consecutive .00 second durations.")
            for start, length in consecutive_duration_info:
                delete_files.update([f[0] for f in files[start:start+length]])
        if duplicate_transcript_info:
            print(f"Folder {folder} has a sequence of 2 or more duplicate transcripts.")
            for start, length in duplicate_transcript_info:
                delete_files.update([f[0] for f in files[start:start+length]])

        # delete wav files with 10 or more consecutive .00 second durations
        confirm_and_delete(base_dir, list(delete_files), folder)
        
        # now update the transcript file (with the deleted files removed)
        new_lines.extend([f[3] for f in files if f[0] not in delete_files])

    with open(transcript_path, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)
    
def print_transcript_stats(base_dir: str) -> None:
    transcript_path = os.path.join(base_dir, 'transcripts.txt')

    total_seconds = 0.0
    with open(transcript_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.strip().split('|')
            duration = float(parts[-2].strip())
            total_seconds += duration
    
    print(f"Total hours of dataset in {base_dir}: {total_seconds / 3600:.4f}")

@hydra.main(version_base='1.3', config_path='../configs', config_name='postprocess_labels.yaml')
def main(cfg: DictConfig) -> None:
    base_dir = os.path.join('labeled_data', cfg.target_dir)
    process_transcripts(base_dir)
    print_transcript_stats(base_dir)

if __name__ == "__main__":
    main()
