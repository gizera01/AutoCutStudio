import os

import librosa
import noisereduce as nr
import numpy as np
import soundfile as sf


class NoiseReducer:
    """
    Reduces constant background noise such as:
    fans, air conditioners, computer noise and
    other continuous background sounds.
    """

    def __init__(self):

        print("NoiseReducer started.")

    # ============================================
    # REDUCE NOISE
    # ============================================

    def reduce_noise(
        self,
        input_audio,
        output_audio
    ):

        print("=" * 50)
        print("Starting noise reduction...")

        # ----------------------------------------
        # CHECK INPUT
        # ----------------------------------------

        if not os.path.exists(input_audio):

            raise FileNotFoundError(
                f"Audio file not found: {input_audio}"
            )

        # ----------------------------------------
        # LOAD AUDIO
        # ----------------------------------------

        print("Loading audio...")

        audio, sample_rate = librosa.load(
            input_audio,
            sr=None,
            mono=True
        )

        if len(audio) == 0:

            raise Exception(
                "The audio file is empty."
            )

        duration = (
            len(audio) /
            sample_rate
        )

        print(
            f"Sample rate: {sample_rate}"
        )

        print(
            f"Audio duration: "
            f"{duration:.2f} seconds"
        )

        # ----------------------------------------
        # FIND NOISE PROFILE
        # ----------------------------------------

        print("=" * 50)
        print("Detecting background noise...")

        noise_sample = self._find_noise_sample(
            audio,
            sample_rate
        )

        # ----------------------------------------
        # FALLBACK
        # ----------------------------------------

        if noise_sample is None:

            print(
                "Could not find a suitable "
                "noise-only section."
            )

            print(
                "Using the quietest section "
                "as fallback."
            )

            noise_sample = self._get_quietest_sample(
                audio,
                sample_rate
            )

        # ----------------------------------------
        # NOISE INFORMATION
        # ----------------------------------------

        noise_duration = (
            len(noise_sample) /
            sample_rate
        )

        print(
            "Noise sample duration: "
            f"{noise_duration:.2f}s"
        )

        # ----------------------------------------
        # REDUCE NOISE
        # ----------------------------------------

        print("=" * 50)
        print("Reducing background noise...")

        reduced_audio = nr.reduce_noise(

            y=audio,

            sr=sample_rate,

            y_noise=noise_sample,

            stationary=True,

            prop_decrease=0.95,

            n_fft=2048,

            win_length=2048,

            hop_length=512
        )

        # ----------------------------------------
        # NORMALIZE
        # ----------------------------------------

        reduced_audio = self._normalize_audio(
            reduced_audio
        )

        # ----------------------------------------
        # OUTPUT DIRECTORY
        # ----------------------------------------

        output_directory = os.path.dirname(
            output_audio
        )

        if output_directory:

            os.makedirs(
                output_directory,
                exist_ok=True
            )

        # ----------------------------------------
        # SAVE
        # ----------------------------------------

        print("=" * 50)
        print("Saving processed audio...")

        sf.write(

            output_audio,

            reduced_audio,

            sample_rate

        )

        print("=" * 50)
        print("Noise reduction completed.")

        print(
            f"Output: {output_audio}"
        )

        print("=" * 50)

        return output_audio

    # ============================================
    # FIND NOISE SAMPLE
    # ============================================

    def _find_noise_sample(
        self,
        audio,
        sample_rate
    ):
        """
        Finds a relatively quiet and stable section
        of the audio that can represent constant
        background noise.
        """

        print(
            "Searching for stable noise section..."
        )

        # ----------------------------------------
        # PARAMETERS
        # ----------------------------------------

        window_duration = 1.0

        window_size = int(
            sample_rate *
            window_duration
        )

        if len(audio) < window_size:

            return None

        # ----------------------------------------
        # CREATE WINDOWS
        # ----------------------------------------

        total_windows = (
            len(audio) //
            window_size
        )

        if total_windows == 0:

            return None

        candidates = []

        # ----------------------------------------
        # ANALYZE WINDOWS
        # ----------------------------------------

        for index in range(
            total_windows
        ):

            start = (
                index *
                window_size
            )

            end = (
                start +
                window_size
            )

            section = audio[
                start:end
            ]

            if len(section) < window_size:

                continue

            # ------------------------------------
            # RMS
            # ------------------------------------

            rms = float(
                np.sqrt(
                    np.mean(
                        section ** 2
                    )
                )
            )

            # ------------------------------------
            # RMS VARIATION
            # ------------------------------------

            frame_rms = librosa.feature.rms(
                y=section,
                frame_length=2048,
                hop_length=512
            )[0]

            if len(frame_rms) == 0:

                continue

            variation = float(
                np.std(frame_rms)
            )

            # ------------------------------------
            # SCORE
            # ------------------------------------

            score = (
                rms +
                variation * 2.0
            )

            candidates.append(
                (
                    score,
                    index
                )
            )

        if not candidates:

            return None

        # ----------------------------------------
        # SORT
        # ----------------------------------------

        candidates.sort(
            key=lambda item: item[0]
        )

        # ----------------------------------------
        # BEST CANDIDATE
        # ----------------------------------------

        best_score, best_index = (
            candidates[0]
        )

        start = (
            best_index *
            window_size
        )

        end = min(
            start +
            window_size,
            len(audio)
        )

        noise_sample = audio[
            start:end
        ]

        # ----------------------------------------
        # VALIDATE
        # ----------------------------------------

        minimum_size = int(
            sample_rate *
            0.5
        )

        if len(noise_sample) < minimum_size:

            return None

        print(
            "Stable noise section found."
        )

        print(
            f"Noise score: "
            f"{best_score:.6f}"
        )

        print(
            f"Noise position: "
            f"{start / sample_rate:.2f}s"
            " -> "
            f"{end / sample_rate:.2f}s"
        )

        return noise_sample

    # ============================================
    # QUIETEST SAMPLE
    # ============================================

    def _get_quietest_sample(
        self,
        audio,
        sample_rate
    ):
        """
        Fallback method that returns the quietest
        one-second section.
        """

        window_duration = 1.0

        window_size = int(
            sample_rate *
            window_duration
        )

        if len(audio) <= window_size:

            return audio

        total_windows = (
            len(audio) //
            window_size
        )

        best_index = 0

        best_rms = float(
            "inf"
        )

        for index in range(
            total_windows
        ):

            start = (
                index *
                window_size
            )

            end = (
                start +
                window_size
            )

            section = audio[
                start:end
            ]

            rms = float(
                np.sqrt(
                    np.mean(
                        section ** 2
                    )
                )
            )

            if rms < best_rms:

                best_rms = rms

                best_index = index

        start = (
            best_index *
            window_size
        )

        end = min(
            start +
            window_size,
            len(audio)
        )

        return audio[
            start:end
        ]

    # ============================================
    # NORMALIZE AUDIO
    # ============================================

    def _normalize_audio(
        self,
        audio
    ):

        peak = np.max(
            np.abs(audio)
        )

        if peak <= 0:

            return audio

        target_peak = 0.95

        return (
            audio /
            peak *
            target_peak
        )