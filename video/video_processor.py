from moviepy import VideoFileClip, concatenate_videoclips
import os


class VideoProcessor:
    """
    Responsible for cutting the video
    using the segments generated
    by AudioProcessor.
    """

    def __init__(self):
        print("VideoProcessor started.")

    # ============================================
    # CUT VIDEO
    # ============================================

    def cut_video(
        self,
        video_path,
        video_segments,
        output_folder
    ):

        print("=" * 50)
        print("Starting video cutting...")

        video = VideoFileClip(video_path)

        clips = []

        print(
            f"Segments found: {len(video_segments)}"
        )

        for index, segment in enumerate(video_segments):

            start, end = segment

            print("=" * 50)
            print(f"Creating segment {index + 1}")
            print(f"{start:.2f}s -> {end:.2f}s")

            clip = video.subclipped(
                start,
                end
            )

            clips.append(clip)

        print("=" * 50)
        print("Joining segments...")

        final_video = concatenate_videoclips(
            clips,
            method="compose"
        )

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # ============================================
        # CREATE A UNIQUE OUTPUT FILE NAME
        # ============================================

        base_name = "video_cut"
        extension = ".mp4"

        counter = 0

        while True:

            if counter == 0:

                file_name = f"{base_name}{extension}"

            else:

                file_name = f"{base_name}_{counter}{extension}"

            output_path = os.path.join(
                output_folder,
                file_name
            )

            if not os.path.exists(output_path):
                break

            counter += 1

        print("=" * 50)
        print("Rendering video...")
        print(output_path)

        final_video.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac"
        )

        print("=" * 50)
        print("Closing files...")

        video.close()
        final_video.close()

        for clip in clips:
            clip.close()

        print("=" * 50)
        print("Video exported successfully!")
        print("=" * 50)

        return output_path