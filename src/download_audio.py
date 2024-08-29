import yt_dlp
import os
from omegaconf import DictConfig
import hydra

class YoutubeAudioSubtitleDownloader:
  def __init__(self, channel_url: str, output_dir: str) -> None:
    self.channel_url = channel_url
    self.output_dir_audio = f'data/{output_dir}/korean_audio'
    self.video_url_path = f'data/{output_dir}/video_urls.txt'

    if not os.path.exists(self.output_dir_audio):
      os.makedirs(self.output_dir_audio)

    if os.path.exists(self.video_url_path):
      with open(self.video_url_path, 'r') as f:
        self.video_urls = f.read().splitlines()
    else:
      self.video_urls = self.get_channel_videos(self.channel_url)
      with open(self.video_url_path, 'w') as f:
        f.write('\n'.join(self.video_urls))

  def get_channel_videos(self, channel_url: str) -> list:
    ydl_opts = {
      'quiet': True,
      'extract_flat': True,
      'force_generic_extractor': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      result = ydl.extract_info(channel_url, download=False)
      if 'entries' in result:
        return [entry['url'] for entry in result['entries']]
      else:
        return []
      
  def get_korean_audio_format(self, video_url: str) -> str:
    ydl_opts = {
      'quiet': True,
      'listformats': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      result = ydl.extract_info(video_url, download=False)
      formats = result.get('formats', [])

      korean_audio_format = None
      for fmt in formats:
        try:
          if (fmt.get('ext') == 'm4a' and
            fmt.get('acodec') != 'none' and
            'ko' in fmt.get('language', '').lower() and
            'low' not in fmt.get('format_note', '').lower()):
            korean_audio_format = fmt.get('format_id')
            break
        except AttributeError:
          continue
      
      return korean_audio_format
  
  def download_korean_audio(self, video_url: str) -> None:
    format_id = self.get_korean_audio_format(video_url)
    if not format_id:
      print(f"No Korean audio track found for: {video_url}")
      return

    ydl_opts = {
      'quiet': True,
      'format': format_id,
      'outtmpl': os.path.join(self.output_dir_audio, '%(title)s.%(ext)s')
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      info_dict = ydl.extract_info(video_url, download=False)
      ydl.download([video_url])

@hydra.main(version_base='1.3', config_path='../configs', config_name='download_audio.yaml')
def main(cfg: DictConfig) -> None:
  downloader = YoutubeAudioSubtitleDownloader(cfg.channel_url, cfg.output_dir)

  for url in downloader.video_urls:
    print(f"Processing {url}")
    downloader.download_korean_audio(url)

  print("All done!")

if __name__ == '__main__':
  main()