# labeling.py
import os
import json
from pydub import AudioSegment
from omegaconf import DictConfig
import hydra

def decompose_korean(text: str) -> str:
    CHO = [chr(i) for i in range(0x1100, 0x1113)]  # 초성 리스트
    JUNG = [chr(i) for i in range(0x1161, 0x1176)]  # 중성 리스트
    JONG = [chr(i) for i in range(0x11A8, 0x11C3)]  # 종성 리스트
    JONG.insert(0, '')  # 종성 없는 경우

    decomposed_text = ''

    for char in text:
        if ord('가') <= ord(char) <= ord('힣'):
            base_code = ord(char) - ord('가')
            cho = CHO[base_code // 588]
            jung = JUNG[(base_code % 588) // 28]
            jong = JONG[base_code % 28]
            decomposed_text += f'{cho}{jung}{jong}'
        else:
            decomposed_text += char

    return decomposed_text.strip()


def labeling(target_dir: str, start_idx: int) -> None:
    audio_dir = os.path.join('data', target_dir, 'korean_audio')
    subtitle_dir = os.path.join('data', target_dir, 'korean_subtitle')
    output_dir = os.path.join('labeled_data', target_dir)

    os.makedirs(output_dir, exist_ok=True)

    audios = os.listdir(audio_dir)

    with open(os.path.join(output_dir, "transcripts.txt"), "a", encoding="utf-8") as file:
        for i, audio in enumerate(audios):
            if i < start_idx:
                continue
            
            print(f"Processing {i}: {audio}...")
            name = os.path.splitext(audio)[0]
            audio_output_dir = os.path.join(output_dir, str(i+1))
            os.makedirs(audio_output_dir, exist_ok=True)

            # 오디오 파일 열기
            audio_file_path = os.path.join(audio_dir, audio)
            audio_segment = AudioSegment.from_file(audio_file_path, format="m4a")
            
            with open(os.path.join(subtitle_dir, f"{name}.json"), "r", encoding="utf-8") as f:
                data = json.load(f)
                for j, segment in enumerate(data):
                    if segment["timestamp"][0] is None or segment["timestamp"][1] is None:
                        continue
                    start = segment["timestamp"][0] * 1000  # pydub는 밀리초 단위 사용
                    end = segment["timestamp"][1] * 1000
                    transcript = segment["text"]
                    decomposed_transcript = decompose_korean(transcript)
                    file.write(f"{i+1}/{j+1}.wav|{transcript}|{decomposed_transcript}|{(end-start)/1000:.2f}|KO\n")

                    output_wav_path = os.path.join(audio_output_dir, f"{j+1}.wav")
                    segment_audio = audio_segment[start:end]
                    segment_audio.export(output_wav_path, format="wav")

@hydra.main(version_base='1.3', config_path='../configs', config_name='label_transcripts.yaml')
def main(cfg: DictConfig) -> None:
    labeling(cfg.target_dir, cfg.start_idx)

if __name__ == "__main__":
    main()
