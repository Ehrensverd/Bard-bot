import io
from sys import platform

from pydub import AudioSegment


class FileHandler:
    def __init__(self):
        #check what file system'
        self.system_os = platform

        pass

        if platform == "linux" or platform == "linux2":
            pass
        elif platform == "darwin":
            pass
        elif platform == "win32":
            pass


    def audio_file_downloader(self):
        pass

    def segment_processer(self, mp3):
        # Segment
        segment = AudioSegment.from_file(io.BytesIO(mp3), format='mp3', frame_rate=48000,
                                              parameters=["-vol", str(1)])

        fade_in_amount = fade_out_amount = 20

        # chunk larger segments for smaller ffmpeg subprocesses to prevent playback starvation
        if segment.duration_seconds > 45:
            sliced_chunks = segment[::45001]
            segment = None  # AudioSegment.empty()
            current_chunk = next(sliced_chunks, None)
            while True:
                next_chunk = next(sliced_chunks, None)
                if not segment:  # First chunk
                    segment = current_chunk.set_frame_rate(48000).fade_in(fade_in_amount)
                elif next_chunk:  # In between chunks
                    segment += current_chunk.set_frame_rate(48000)
                else:  # Last chunk
                    segment += current_chunk.set_frame_rate(48000).fade_out(fade_out_amount)
                    break
                current_chunk = next_chunk
        else:
            segment.set_frame_rate(48000).fade_in(fade_in_amount).fade_out(fade_out_amount)

        return segment


    def import_ambient(self, url):
        pass

    def import_sndup(self, urls):
        pass

    def export_sndup(self, scene):
        pass

    def save_scene_as(self, scene, path):
        pass

    def save_scene(self, scene):
        pass

    def load_scene(self, path):
        pass

    def save_collection_as(self, scenes, path):
        pass
