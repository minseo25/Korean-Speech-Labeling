## _About Project_

한국어 특화 TTS model 학습을 위해 음성 데이터셋을 제작하는 코드.

유튜브 영상에서 음원을 추출하고, 전처리하고, whisper STT 모델을 통해 transcript를 얻고, 후처리 및 labeling을 진행한다.

## _Project Setting (for mac)_

install poetry

```shell
curl -sSL https://install.python-poetry.org | python3 -
vi ~/.zshrc # Add `export PATH="/Users/minseokim/.local/bin:$PATH"`
source ~/.zshrc
```

install dependencies (requires python >= 3.10)
```shell
poetry install
```

install ffmpeg (for managing audio files)
```shell
brew install ffmpeg
```

## _Project Setting (for windows)_

install poetry and add a path to a system environment variable (`C:\Users\[Username]\AppData\Roaming\Python\Scripts`)

```shell
curl -sSL https://install.python-poetry.org | python -
# if above command doesn't work, then ...
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

install dependencies (requires python >= 3.10)
```shell
poetry install
```

install ffmpeg (for managing audio files) : https://jeongdev55.tistory.com/111

reinstall torch & torchaudio for cuda support
```shell
poetry run pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

install make : https://jstar0525.tistory.com/264

## _Workflow_

STEP1. download audio files
- m4a format, medium quality
- set `configs/download_audio.yaml`
- and "딸깍"

```shell
make download
```

STEP1.5. preprocess audio files (optional)
- 인트로, 아웃트로 길이 ms로 지정 시 잘라버림
- set `configs/preprocess_audio.yaml`
- and "딸깍"

```shell
make preprocess
```

STEP2. transcribe audio files using whisper
- 약간의 전처리(wav format, sampling rate 조절, mono) whisper 모델에 넣어 transcribe
- set `configs/transcribe_audio.yaml`
- and "딸깍"

```shell
make transcribe
```

STEP3. create dataset (with splitted wav files and corresponding labels)
- set `configs/label_transcripts.yaml`
- and "딸깍"

```shell
make label
```

STEP4. postprocess dataset
- set `configs/postprocess_labels.yaml`
- and "딸깍"

```shell
make postprocess
```

STEP5. convert dataset suitable for training (parquet format)
- set `configs/export_to_parquet.yaml`
- and "딸깍"

```shell
make convert
```
