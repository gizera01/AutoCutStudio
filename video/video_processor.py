import os

from moviepy import (
    VideoFileClip,
    AudioFileClip,
    concatenate_videoclips,
    concatenate_audioclips
)


class VideoProcessor:
    """
    Responsible for final video processing.

    Supports:

    - Removing silence
    - Reducing background noise
    - Removing silence + reducing noise
    - Keeping the original video when only noise
      reduction is requested
    - Automatic output filename numbering
    - Protection against empty video segments
    """

    def __init__(self):

        print("VideoProcessor started.")

    # ============================================
    # PROCESS VIDEO
    # ============================================

    def cut_video(
        self,
        video_path,
        video_segments,
        output_folder,
        audio_path=None,
        output_name="video_processed.mp4"
    ):
        """
        Processes and exports the final video.

        Parameters
        ----------
        video_path:
            Original video path.

        video_segments:
            List of (start, end) segments when silence
            removal is enabled.

            Use None when silence removal is disabled.

        output_folder:
            Destination folder.

        audio_path:
            Processed audio path when noise reduction
            is enabled.

        output_name:
            Base output filename.
        """

        print("=" * 50)
        print("Starting video processing...")

        # ========================================
        # VALIDATE VIDEO
        # ========================================

        if not os.path.isfile(video_path):

            raise FileNotFoundError(
                f"Video file not found: {video_path}"
            )

        # ========================================
        # OUTPUT FOLDER
        # ========================================

        os.makedirs(
            output_folder,
            exist_ok=True
        )

        # ========================================
        # OPEN ORIGINAL VIDEO
        # ========================================

        print("Opening original video...")

        video = VideoFileClip(
            video_path
        )

        print(
            f"Original duration: "
            f"{video.duration:.2f}s"
        )

        # ========================================
        # MODE 1
        #
        # ONLY NOISE REDUCTION
        #
        # video_segments = None
        # audio_path != None
        # ========================================

        if video_segments is None:

            print("=" * 50)
            print(
                "Silence removal disabled."
            )

            print(
                "Keeping the complete video."
            )

            final_video = video

            # ------------------------------------
            # APPLY CLEAN AUDIO
            # ------------------------------------

            if audio_path is not None:

                print("=" * 50)
                print(
                    "Applying processed audio..."
                )

                if not os.path.isfile(
                    audio_path
                ):

                    video.close()

                    raise FileNotFoundError(
                        "Processed audio file not found: "
                        f"{audio_path}"
                    )

                processed_audio = (
                    AudioFileClip(
                        audio_path
                    )
                )

                # --------------------------------
                # MATCH AUDIO TO VIDEO DURATION
                # --------------------------------

                audio_duration = (
                    processed_audio.duration
                )

                video_duration = (
                    video.duration
                )

                print(
                    f"Processed audio duration: "
                    f"{audio_duration:.2f}s"
                )

                print(
                    f"Video duration: "
                    f"{video_duration:.2f}s"
                )

                # --------------------------------
                # PROTECT AGAINST SMALL DIFFERENCE
                # --------------------------------

                if audio_duration > video_duration:

                    processed_audio = (
                        processed_audio.subclipped(
                            0,
                            video_duration
                        )
                    )

                elif audio_duration < video_duration:

                    print(
                        "Warning: processed audio "
                        "is shorter than the video."
                    )

                final_video = (
                    video.with_audio(
                        processed_audio
                    )
                )

            # ------------------------------------
            # EXPORT
            # ------------------------------------

            output_path = (
                self._get_unique_output_path(
                    output_folder,
                    output_name
                )
            )

            print("=" * 50)
            print("Rendering video...")

            print(
                f"Output: {output_path}"
            )

            final_video.write_videofile(

                output_path,

                codec="libx264",

                audio_codec="aac",

                threads=4
            )

            # ------------------------------------
            # CLOSE
            # ------------------------------------

            print("=" * 50)
            print("Closing files...")

            try:
                final_video.close()
            except Exception:
                pass

            try:
                video.close()
            except Exception:
                pass

            print("=" * 50)
            print(
                "Video exported successfully!"
            )

            print(
                f"Output: {output_path}"
            )

            print("=" * 50)

            return output_path

        # ========================================
        # MODE 2 / 3
        #
        # SILENCE REMOVAL
        #
        # video_segments != None
        # ========================================

        print("=" * 50)
        print("Silence removal enabled.")

        print(
            f"Segments received: "
            f"{len(video_segments)}"
        )

        # ========================================
        # CREATE VIDEO SEGMENTS
        # ========================================

        video_clips = []

        try:

            for index, (
                start,
                end
            ) in enumerate(
                video_segments,
                start=1
            ):

                # --------------------------------
                # PROTECT TIMES
                # --------------------------------

                start = max(
                    0.0,
                    min(
                        float(start),
                        video.duration
                    )
                )

                end = max(
                    0.0,
                    min(
                        float(end),
                        video.duration
                    )
                )

                duration = (
                    end -
                    start
                )

                # --------------------------------
                # IGNORE EMPTY SEGMENT
                # --------------------------------

                if duration <= 0.05:

                    print(
                        f"Skipping empty "
                        f"segment {index}: "
                        f"{start:.2f}s -> "
                        f"{end:.2f}s"
                    )

                    continue

                print("=" * 50)

                print(
                    f"Creating segment {index}"
                )

                print(
                    f"{start:.2f}s -> "
                    f"{end:.2f}s"
                )

                clip = video.subclipped(
                    start,
                    end
                )

                video_clips.append(
                    clip
                )

            # ====================================
            # VALIDATE SEGMENTS
            # ====================================

            if not video_clips:

                raise Exception(
                    "No valid video segments "
                    "were created."
                )

            # ====================================
            # JOIN VIDEO SEGMENTS
            # ====================================

            print("=" * 50)
            print("Joining video segments...")

            final_video = (
                concatenate_videoclips(
                    video_clips,
                    method="compose"
                )
            )

            print(
                f"Final video duration: "
                f"{final_video.duration:.2f}s"
            )

            # ====================================
            # MODE 3
            #
            # SILENCE + NOISE
            # ====================================

            if audio_path is not None:

                print("=" * 50)
                print(
                    "Applying processed audio "
                    "to the cut segments..."
                )

                if not os.path.isfile(
                    audio_path
                ):

                    raise FileNotFoundError(
                        "Processed audio file not found: "
                        f"{audio_path}"
                    )

                # --------------------------------
                # OPEN CLEAN AUDIO
                # --------------------------------

                processed_audio = (
                    AudioFileClip(
                        audio_path
                    )
                )

                print(
                    f"Processed audio duration: "
                    f"{processed_audio.duration:.2f}s"
                )

                # --------------------------------
                # CREATE AUDIO SEGMENTS
                # --------------------------------

                audio_clips = []

                for index, (
                    start,
                    end
                ) in enumerate(
                    video_segments,
                    start=1
                ):

                    start = max(
                        0.0,
                        min(
                            float(start),
                            processed_audio.duration
                        )
                    )

                    end = max(
                        0.0,
                        min(
                            float(end),
                            processed_audio.duration
                        )
                    )

                    duration = (
                        end -
                        start
                    )

                    if duration <= 0.05:

                        continue

                    print(
                        f"Creating audio segment "
                        f"{index}: "
                        f"{start:.2f}s -> "
                        f"{end:.2f}s"
                    )

                    audio_clip = (
                        processed_audio.subclipped(
                            start,
                            end
                        )
                    )

                    audio_clips.append(
                        audio_clip
                    )

                # --------------------------------
                # VALIDATE AUDIO SEGMENTS
                # --------------------------------

                if not audio_clips:

                    processed_audio.close()

                    raise Exception(
                        "No valid audio segments "
                        "were created."
                    )

                # --------------------------------
                # JOIN AUDIO
                # --------------------------------

                print("=" * 50)
                print(
                    "Joining processed audio..."
                )

                final_audio = (
                    concatenate_audioclips(
                        audio_clips
                    )
                )

                print(
                    f"Final audio duration: "
                    f"{final_audio.duration:.2f}s"
                )

                # --------------------------------
                # ATTACH AUDIO TO VIDEO
                # --------------------------------

                final_video = (
                    final_video.with_audio(
                        final_audio
                    )
                )

                print(
                    "Processed audio successfully "
                    "attached to final video."
                )

            # ====================================
            # EXPORT
            # ====================================

            output_path = (
                self._get_unique_output_path(
                    output_folder,
                    output_name
                )
            )

            print("=" * 50)
            print("Rendering video...")

            print(
                f"Output: {output_path}"
            )

            final_video.write_videofile(

                output_path,

                codec="libx264",

                audio_codec="aac",

                threads=4
            )

            # ====================================
            # CLOSE FILES
            # ====================================

            print("=" * 50)
            print("Closing files...")

            try:
                final_video.close()
            except Exception:
                pass

            for clip in video_clips:

                try:
                    clip.close()
                except Exception:
                    pass

            if audio_path is not None:

                for clip in audio_clips:

                    try:
                        clip.close()
                    except Exception:
                        pass

                try:
                    processed_audio.close()
                except Exception:
                    pass

                try:
                    final_audio.close()
                except Exception:
                    pass

            try:
                video.close()
            except Exception:
                pass

            print("=" * 50)
            print(
                "Video exported successfully!"
            )

            print(
                f"Output: {output_path}"
            )

            print("=" * 50)

            return output_path

        except Exception:

            # ------------------------------------
            # CLEANUP AFTER ERROR
            # ------------------------------------

            for clip in video_clips:

                try:
                    clip.close()
                except Exception:
                    pass

            try:
                video.close()
            except Exception:
                pass

            raise

    # ============================================
    # UNIQUE OUTPUT PATH
    # ============================================

    def _get_unique_output_path(
        self,
        output_folder,
        filename
    ):
        """
        Prevents existing files from being
        overwritten.

        Examples:

        video_processed.mp4
        video_processed_1.mp4
        video_processed_2.mp4
        video_processed_3.mp4
        """

        base_name, extension = (
            os.path.splitext(
                filename
            )
        )

        # ----------------------------------------
        # FIRST FILE
        # ----------------------------------------

        output_path = os.path.join(
            output_folder,
            filename
        )

        if not os.path.exists(
            output_path
        ):

            return output_path

        # ----------------------------------------
        # NUMBERED FILE
        # ----------------------------------------

        counter = 1

        while True:

            numbered_filename = (
                f"{base_name}_"
                f"{counter}"
                f"{extension}"
            )

            output_path = os.path.join(
                output_folder,
                numbered_filename
            )

            if not os.path.exists(
                output_path
            ):

                return output_path

            counter += 1