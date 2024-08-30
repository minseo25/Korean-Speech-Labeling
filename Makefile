help:  ## Show help
	@grep -E '^[.a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean: ## Clean autogenerated files
	find . -type f -name "*.DS_Store" -ls -delete
	find . | grep -E "(__pycache__|\.pyc|\.pyo)" | xargs rm -rf

download: ## Download korean audio files from youtube
	poetry run python src/download_audio.py

preprocess: ## Preprocess korean audio files (trim intro, outtro if needed)
	poetry run python src/preprocess_audio.py

transcribe: ## Transcribe korean audio files using whisper model
	poetry run python src/transcribe_audio.py

label: ## Label korean audio files and transcriptions
	poetry run python src/label_transcripts.py

postprocess: ## Postprocess dataset (inaccurate segmentation)
	poetry run python src/postprocess_labels.py
