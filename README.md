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
