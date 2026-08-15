from moviepy import VideoFileClip

import librosa
import os

from audio.noise_reducer import NoiseReducer


class AudioProcessor:
    """
    Handles audio extraction and silence detection.

    Noise reduction is optional and controlled by the caller.
    """

    def __init__(self):

        print("AudioProcessor started.")

        self.noise_reducer = NoiseReducer()

    # ============================================
    # LOAD VIDEO
    # ============================================

    def load_video(
        self,
        video_path,
        output_folder,
        reduce_noise=False,
        detect_silence=False
    ):

        print("=" * 50)
        print("Opening video...")

        video = VideoFileClip(
            video_path
        )

        print(
            f"Duration : {video.duration:.2f} seconds"
        )

        print(
            f"FPS      : {video.fps}"
        )

        print(
            f"Size     : {video.size}"
        )

        # ----------------------------------------
        # CHECK AUDIO
        # ----------------------------------------

        if video.audio is None:

            video.close()

            raise Exception(
                "This video does not contain "
                "an audio track."
            )

        # ----------------------------------------
        # CREATE OUTPUT FOLDER
        # ----------------------------------------

        os.makedirs(
            output_folder,
            exist_ok=True
        )

        # ----------------------------------------
        # TEMP AUDIO
        # ----------------------------------------

        audio_path = os.path.join(
            output_folder,
            "audio_temp.wav"
        )

        print("=" * 50)
        print("Extracting audio...")

        video.audio.write_audiofile(
            audio_path,
            codec="pcm_s16le"
        )

        print(
            "Audio extracted successfully!"
        )

        video.close()

        # ----------------------------------------
        # NOISE REDUCTION
        # ----------------------------------------

        audio_to_analyze = audio_path

        if reduce_noise:

            print("=" * 50)
            print(
                "Background noise reduction enabled."
            )

            cleaned_audio_path = os.path.join(
                output_folder,
                "audio_clean.wav"
            )

            audio_to_analyze = (
                self.noise_reducer.reduce_noise(
                    audio_path,
                    cleaned_audio_path
                )
            )

        else:

            print("=" * 50)
            print(
                "Background noise reduction disabled."
            )

        # ----------------------------------------
        # SILENCE DETECTION
        # ----------------------------------------

        if detect_silence:

            return self.detect_silence(
                audio_to_analyze
            )

        # ----------------------------------------
        # NO SILENCE DETECTION
        # ----------------------------------------

        print("=" * 50)
        print(
            "Silence removal disabled."
        )

        print(
            "Keeping the complete video duration."
        )

        print("=" * 50)

        return {
            "audio_path": audio_to_analyze,
            "duration": self._get_audio_duration(
                audio_to_analyze
            )
        }

    # ============================================
    # GET AUDIO DURATION
    # ============================================

    def _get_audio_duration(
        self,
        audio_path
    ):

        audio, sample_rate = librosa.load(
            audio_path,
            sr=None
        )

        if len(audio) == 0:

            raise Exception(
                "The selected audio is empty."
            )

        return (
            len(audio) /
            sample_rate
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

        # ----------------------------------------
        # CHECK AUDIO
        # ----------------------------------------

        if len(audio) == 0:

            raise Exception(
                "The selected audio is empty."
            )

        duration = (
            len(audio) /
            sample_rate
        )

        # ----------------------------------------
        # CHECK AUDIO VOLUME
        # ----------------------------------------

        if abs(audio).max() < 0.000001:

            raise Exception(
                "The selected video has no audio."
            )

        print(
            f"Audio duration: "
            f"{duration:.2f} seconds"
        )

        # ----------------------------------------
        # CALCULATE RMS
        # ----------------------------------------

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
        # FIND SILENCES
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

        # ----------------------------------------
        # CLOSE FINAL SILENCE
        # ----------------------------------------

        if inside_silence:

            silences.append(
                (
                    silence_start,
                    len(rms) - 1
                )
            )

        # ----------------------------------------
        # FILTER SHORT SILENCES
        # ----------------------------------------

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
            f"Valid silences: "
            f"{len(valid_silences)}"
        )

        # ========================================
        # CREATE VIDEO SEGMENTS
        # ========================================

        print("=" * 50)
        print("Creating video segments...")

        video_segments = []

        current_start = 0.0

        minimum_segment_duration = 0.05

        for silence_start, silence_end in valid_silences:

            silence_start = max(
                0.0,
                min(
                    silence_start,
                    duration
                )
            )

            silence_end = max(
                0.0,
                min(
                    silence_end,
                    duration
                )
            )

            segment_duration = (
                silence_start -
                current_start
            )

            if segment_duration >= (
                minimum_segment_duration
            ):

                video_segments.append(
                    (
                        current_start,
                        silence_start
                    )
                )

            current_start = max(
                current_start,
                silence_end
            )

        # ----------------------------------------
        # FINAL SEGMENT
        # ----------------------------------------

        final_segment_duration = (
            duration -
            current_start
        )

        if final_segment_duration >= (
            minimum_segment_duration
        ):

            video_segments.append(
                (
                    current_start,
                    duration
                )
            )

        # ----------------------------------------
        # FINAL VALIDATION
        # ----------------------------------------

        valid_video_segments = []

        for start, end in video_segments:

            start = max(
                0.0,
                min(
                    start,
                    duration
                )
            )

            end = max(
                0.0,
                min(
                    end,
                    duration
                )
            )

            segment_duration = (
                end -
                start
            )

            if segment_duration < (
                minimum_segment_duration
            ):

                continue

            valid_video_segments.append(
                (
                    start,
                    end
                )
            )

        video_segments = (
            valid_video_segments
        )

        # ----------------------------------------
        # RESULTS
        # ----------------------------------------

        print(
            f"Segments created: "
            f"{len(video_segments)}"
        )

        for index, (
            start,
            end
        ) in enumerate(
            video_segments,
            start=1
        ):

            print(
                f"Segment {index}: "
                f"{start:.2f}s -> "
                f"{end:.2f}s"
            )

        print("=" * 50)
        print("Audio analysis completed.")
        print("=" * 50)

        return video_segments