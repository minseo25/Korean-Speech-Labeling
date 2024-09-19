import os
from omegaconf import DictConfig
import hydra
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
import math

def export_to_parquet(base_dir: str, output_dir: str, MAX_SAMPLES: int) -> None:
    data = []
    with open(os.path.join(base_dir, 'transcripts.txt'), 'r', encoding='utf-8') as f:
        for line in f:
            # filename | transcription | transcription_normalised | duration (in seconds)
            parts = line.strip().split('|')
            if len(parts) >= 4:
                file_name = parts[0].replace('.wav', '')
                transcription = parts[1]
                transcription_normalised = parts[2]
                audio_path = os.path.join(base_dir, parts[0].replace('/', os.sep))

                # read audio file in bytes
                if os.path.exists(audio_path):
                    with open(audio_path, 'rb') as audio_file:
                        audio_bytes = audio_file.read()

                    # add to data (parler TTS dataset format)
                    data.append({
                        'file_name': file_name,
                        'transcription': transcription,
                        'transcription_normalised': transcription_normalised,
                        'audio': {'bytes': audio_bytes}
                    })
            else:
                print(f'Invalid line: {line.strip()}')

    total_samples = len(data)
    num_files = math.ceil(total_samples / MAX_SAMPLES)

    # save data to parquet files
    for i in range(num_files):
        start_idx = i * MAX_SAMPLES
        end_idx = min((i + 1) * MAX_SAMPLES, total_samples)
        df_chunk = pd.DataFrame(data[start_idx:end_idx])

        filename = os.path.join(output_dir, f'train-{i:05d}-of-{num_files:05d}.parquet')

        table = pa.Table.from_pandas(df_chunk)
        pq.write_table(table, filename)

        print(f'Saved {filename} with {len(df_chunk)} samples')

@hydra.main(version_base='1.3', config_path='../configs', config_name='export_to_parquet.yaml')
def main(cfg: DictConfig) -> None:
    base_dir = os.path.join('labeled_data', cfg.target_dir)
    output_dir = os.path.join('parquet_data', cfg.target_dir)

    os.makedirs(output_dir, exist_ok=True)
    
    export_to_parquet(base_dir, output_dir, cfg.MAX_SAMPLES)

if __name__ == "__main__":
    main()