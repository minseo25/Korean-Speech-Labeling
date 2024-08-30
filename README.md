## _Project Setting_

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

if windows, may need to re-install torch like this to enable GPU acceleration with CUDA support
```
poetry run pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

## _Workflow_

STEP1. download audio files
- set `configs/download_audio.yaml`
- and "딸깍"

```shell
make download
```

STEP1.5. preprocess audio files (optional)
- set `configs/preprocess_audio.yaml` (인트로, 아웃트로 길이 ms로 지정)
- and "딸깍"

```shell
make preprocess
```

STEP2. transcribe audio files using whisper
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
