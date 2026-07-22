from moviepy import VideoFileClip
import librosa
import os


class AudioProcessor:
    """
    Handles audio extraction, silence detection
    and prepares the video segments that should
    be kept.
    """

    def __init__(self):

        print("AudioProcessor started.")

    # ============================================
    # LOAD VIDEO
    # ============================================

    def load_video(
        self,
        video_path,
        output_folder
    ):

        print("=" * 50)
        print("Opening video...")

        video = VideoFileClip(video_path)

        print(f"Duration : {video.duration:.2f} seconds")
        print(f"FPS      : {video.fps}")
        print(f"Size     : {video.size}")

        # ----------------------------------------
        # CHECK IF VIDEO HAS AUDIO
        # ----------------------------------------

        if video.audio is None:

            video.close()

            raise Exception(
                "This video does not contain an audio track."
            )

        # ----------------------------------------
        # CREATE OUTPUT FOLDER
        # ----------------------------------------

        if not os.path.exists(output_folder):

            os.makedirs(output_folder)

        audio_path = os.path.join(
            output_folder,
            "audio_temp.wav"
        )

        print("Extracting audio...")

        video.audio.write_audiofile(
            audio_path,
            codec="pcm_s16le"
        )

        print("Audio extracted successfully!")

        video.close()

        return self.detect_silence(
            audio_path
        )

    # ============================================
    # DETECT SILENCE
    # ============================================

    def detect_silence(
        self,
        audio_path
    ):

        print("=" * 50)
        print("Loading audio...")

        audio, sample_rate = librosa.load(
            audio_path,
            sr=None
        )

        duration = len(audio) / sample_rate

        print(
            f"Audio duration: {duration:.2f} seconds"
        )

        print("=" * 50)
        print("Calculating RMS volume...")

        rms = librosa.feature.rms(
            y=audio
        )[0]

        silence_threshold = 0.01

        silences = []

        inside_silence = False

        silence_start = 0

        # ----------------------------------------
        # FIND ALL SILENCES
        # ----------------------------------------

        for index, volume in enumerate(rms):

            if volume < silence_threshold:

                if not inside_silence:

                    inside_silence = True
                    silence_start = index

            else:

                if inside_silence:

                    silences.append(
                        (
                            silence_start,
                            index - 1
                        )
                    )

                    inside_silence = False

        print("=" * 50)
        print("Filtering short silences...")

        minimum_duration = 0.30

        valid_silences = []

        for start_frame, end_frame in silences:

            start_time = float(
                librosa.frames_to_time(
                    start_frame,
                    sr=sample_rate
                )
            )

            end_time = float(
                librosa.frames_to_time(
                    end_frame,
                    sr=sample_rate
                )
            )

            silence_duration = (
                end_time - start_time
            )

            if silence_duration >= minimum_duration:

                valid_silences.append(
                    (
                        start_time,
                        end_time
                    )
                )

        print(
            f"Valid silences found: {len(valid_silences)}"
        )

        print("=" * 50)
        print("Generating video segments...")

        video_segments = []

        video_start = 0.0
                # ============================================
        # CHECK IF THE VIDEO HAS AUDIO
        # ============================================

        if len(audio) == 0:
            raise Exception(
                "The selected video has no audio."
            )

        duracao = len(audio) / sample_rate

        # If the maximum volume is practically zero,
        # consider the file as a video without audio.
        if abs(audio).max() < 0.000001:
            raise Exception(
                "The selected video has no audio."
            )

        print("=" * 50)
        print("Audio loaded successfully.")

        print(
            f"Duration: {duracao:.2f} seconds"
        )

        print("=" * 50)
        print("Calculating audio volume...")

        rms = librosa.feature.rms(
            y=audio
        )[0]

        silence_threshold = 0.01

        silences = []

        inside_silence = False
        silence_start = 0

        for index, volume in enumerate(rms):

            if volume < silence_threshold:

                if not inside_silence:

                    inside_silence = True
                    silence_start = index

            else:

                if inside_silence:

                    silences.append(
                        (
                            silence_start,
                            index - 1
                        )
                    )

                    inside_silence = False

        print("=" * 50)
        print("Filtering short silences...")

        minimum_duration = 0.30

        valid_silences = []

        for start, end in silences:

            start_time = float(
                librosa.frames_to_time(
                    start,
                    sr=sample_rate
                )
            )

            end_time = float(
                librosa.frames_to_time(
                    end,
                    sr=sample_rate
                )
            )

            silence_duration = (
                end_time -
                start_time
            )

            if silence_duration >= minimum_duration:

                valid_silences.append(
                    (
                        start_time,
                        end_time
                    )
                )

        print(
            f"Valid silences: {len(valid_silences)}"
        )

        print("=" * 50)
        print("Creating video segments...")

        video_segments = []

        current_start = 0.0

        for silence_start, silence_end in valid_silences:

            if silence_start > current_start:

                video_segments.append(
                    (
                        current_start,
                        silence_start
                    )
                )

            current_start = silence_end

        if current_start < duracao:

            video_segments.append(
                (
                    current_start,
                    duracao
                )
            )

        print(
            f"Segments created: {len(video_segments)}"
        )

        print("=" * 50)
        print("Audio analysis completed.")
        print("=" * 50)

        return video_segments