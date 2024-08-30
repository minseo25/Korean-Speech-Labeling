import json, os
from transformers import pipeline, Pipeline
from pydub import AudioSegment
import torch, torchaudio
from omegaconf import DictConfig
import hydra


def convert_m4a_to_wav(m4a_path: str, wav_path: str) -> None:
    # Convert m4a to wav using pydub
    audio = AudioSegment.from_file(m4a_path, format="m4a")
    audio.export(wav_path, format="wav")
    os.remove(m4a_path)

def transcribe_audio(pipe: Pipeline, audio_file_path: str) -> dict:
    # Convert .m4a to .wav
    wav_file_path = audio_file_path.replace(".m4a", ".wav")
    convert_m4a_to_wav(audio_file_path, wav_file_path)

    # Load the wav file using torchaudio
    audio, sample_rate = torchaudio.load(wav_file_path)

    # Convert to mono if the audio is stereo
    if audio.shape[0] > 1:
        audio = torch.mean(audio, dim=0, keepdim=True)
    
    # Resample the audio to 16000 Hz if necessary (whisper is trained on 16kHz audio)
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        audio = resampler(audio)
    
    # Transcribe the audio file and get timestamps
    prediction = pipe(audio.squeeze().numpy(), return_timestamps=True)["chunks"]
    
    return prediction

def get_transcripts(pipe: Pipeline, audio_path: str, subtitle_path: str, start_idx: int) -> None:
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
        transcription = transcribe_audio(pipe, audio_file_path)

        # Save the transcription to a file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(transcription, f, ensure_ascii=False, indent=4)

@hydra.main(version_base='1.3', config_path='../configs', config_name='transcribe_audio.yaml')
def main(cfg: DictConfig) -> None:
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_built():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    pipe = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-medium",
        chunk_length_s=30,
        device=device,
        generate_kwargs={"language": "ko"},
    )

    audio_path = os.path.join('data', cfg.audio_dir, 'korean_audio')
    subtitle_path = os.path.join('data', cfg.audio_dir, 'korean_subtitle')
    
    if not os.path.exists(subtitle_path):
        os.makedirs(subtitle_path)

    get_transcripts(pipe, audio_path, subtitle_path, cfg.start_idx)

    if device.type == "cuda":
        del pipe
        torch.cuda.empty_cache()
    elif device.type == "mps":
        del pipe
        torch.mps.exit()

if __name__ == "__main__":
    main()
