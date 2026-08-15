import os
import threading

import customtkinter as ctk

from tkinter import filedialog

from audio.audio_processor import AudioProcessor
from video.video_processor import VideoProcessor


# ============================================
# PROCESSORS
# ============================================

audio_processor = AudioProcessor()

video_processor = VideoProcessor()


# ============================================
# APPLICATION CONFIGURATION
# ============================================

app = ctk.CTk()

app.title(
    "AutoCut Studio"
)

app.geometry(
    "900x800"
)

app.resizable(
    False,
    False
)


# ============================================
# FILE SELECTION
# ============================================

def select_video():

    path = filedialog.askopenfilename(

        title="Select a video",

        filetypes=[

            (
                "Video Files",
                "*.mp4 *.mov *.avi *.mkv"
            ),

            (
                "All Files",
                "*.*"
            )
        ]
    )

    if path:

        video_entry.delete(
            0,
            "end"
        )

        video_entry.insert(
            0,
            path
        )


def select_output_folder():

    path = filedialog.askdirectory()

    if path:

        output_entry.delete(
            0,
            "end"
        )

        output_entry.insert(
            0,
            path
        )


# ============================================
# STATUS
# ============================================

def update_status(
    text,
    progress=None
):

    app.after(

        0,

        lambda: status.configure(
            text=text
        )
    )

    if progress is not None:

        app.after(

            0,

            lambda: progress_bar.set(
                progress
            )
        )


# ============================================
# ENABLE / DISABLE PROCESS BUTTON
# ============================================

def update_process_button():

    silence_enabled = (
        remove_silence.get() == 1
    )

    noise_enabled = (
        remove_noise.get() == 1
    )

    if silence_enabled or noise_enabled:

        process_button.configure(
            state="normal"
        )

    else:

        process_button.configure(
            state="disabled"
        )


# ============================================
# PROCESS THREAD
# ============================================

def start_thread():

    # ----------------------------------------
    # CHECK OPTIONS
    # ----------------------------------------

    silence_enabled = (
        remove_silence.get() == 1
    )

    noise_enabled = (
        remove_noise.get() == 1
    )

    if not silence_enabled and not noise_enabled:

        update_status(
            "Please select at least one "
            "processing option."
        )

        return

    # ----------------------------------------
    # START THREAD
    # ----------------------------------------

    thread = threading.Thread(
        target=process_video,
        daemon=True
    )

    thread.start()


# ============================================
# PROCESS VIDEO
# ============================================

def process_video():

    try:

        # ====================================
        # GET VALUES
        # ====================================

        video_path = (
            video_entry.get().strip()
        )

        output_folder = (
            output_entry.get().strip()
        )

        remove_silence_enabled = (
            remove_silence.get() == 1
        )

        reduce_noise_enabled = (
            remove_noise.get() == 1
        )

        # ====================================
        # VALIDATE VIDEO
        # ====================================

        if video_path == "":

            update_status(
                "Please select a video."
            )

            return

        if not os.path.isfile(
            video_path
        ):

            update_status(
                "The selected video "
                "does not exist."
            )

            return

        # ====================================
        # VALIDATE OUTPUT
        # ====================================

        if output_folder == "":

            update_status(
                "Please select an output folder."
            )

            return

        os.makedirs(
            output_folder,
            exist_ok=True
        )

        # ====================================
        # VALIDATE OPTIONS
        # ====================================

        if (
            not remove_silence_enabled
            and
            not reduce_noise_enabled
        ):

            update_status(
                "Please select at least one "
                "processing option."
            )

            return

        # ====================================
        # DISABLE BUTTON
        # ====================================

        app.after(

            0,

            lambda: process_button.configure(
                state="disabled"
            )
        )

        # ====================================
        # DETERMINE MODE
        # ====================================

        if (
            remove_silence_enabled
            and
            reduce_noise_enabled
        ):

            update_status(
                "Removing silence and "
                "reducing background noise...",
                0.05
            )

            output_name = (
                "video_processed.mp4"
            )

        elif remove_silence_enabled:

            update_status(
                "Removing silence...",
                0.05
            )

            output_name = (
                "video_cut.mp4"
            )

        else:

            update_status(
                "Reducing background noise...",
                0.05
            )

            output_name = (
                "video_noise_reduced.mp4"
            )

        # ====================================
        # AUDIO PROCESSING
        # ====================================

        clips = None

        audio_result = (
            audio_processor.load_video(

                video_path,

                output_folder,

                reduce_noise=(
                    reduce_noise_enabled
                ),

                detect_silence=(
                    remove_silence_enabled
                )
            )
        )

        # ====================================
        # DETERMINE AUDIO PATH
        # ====================================

        audio_path = None

        if reduce_noise_enabled:

            audio_path = os.path.join(

                output_folder,

                "audio_clean.wav"
            )

        # ====================================
        # DETERMINE VIDEO SEGMENTS
        # ====================================

        if remove_silence_enabled:

            clips = audio_result

        else:

            clips = None

        # ====================================
        # UPDATE PROGRESS
        # ====================================

        if reduce_noise_enabled:

            update_status(
                "Audio processing completed.",
                0.40
            )

        else:

            update_status(
                "Audio analysis completed.",
                0.40
            )

        # ====================================
        # PROCESS VIDEO
        # ====================================

        update_status(
            "Creating final video...",
            0.60
        )

        final_video = (
            video_processor.cut_video(

                video_path,

                clips,

                output_folder,

                audio_path=audio_path,

                output_name=output_name
            )
        )

        # ====================================
        # COMPLETED
        # ====================================

        update_status(

            "Completed!\n\n"
            "Output file:\n"
            f"{final_video}",

            1.0
        )

    except Exception as error:

        print("=" * 50)
        print("ERROR")
        print(error)
        print("=" * 50)

        update_status(
            f"Error:\n{error}"
        )

    finally:

        app.after(

            0,

            update_process_button
        )


# ============================================
# USER INTERFACE
# ============================================

title = ctk.CTkLabel(

    app,

    text="AutoCut Studio",

    font=(
        "Arial",
        32,
        "bold"
    )
)

title.pack(
    pady=30
)


# ============================================
# VIDEO
# ============================================

ctk.CTkLabel(

    app,

    text="Video:"
).pack()


video_entry = ctk.CTkEntry(

    app,

    width=600
)

video_entry.pack(
    pady=10
)


ctk.CTkButton(

    app,

    text="Select Video",

    command=select_video

).pack(
    pady=10
)


# ============================================
# OUTPUT FOLDER
# ============================================

ctk.CTkLabel(

    app,

    text="Output Folder:"
).pack(
    pady=(20, 0)
)


output_entry = ctk.CTkEntry(

    app,

    width=600
)

output_entry.pack(
    pady=10
)


ctk.CTkButton(

    app,

    text="Select Folder",

    command=select_output_folder

).pack(
    pady=10
)


# ============================================
# PROCESSING OPTIONS
# ============================================

ctk.CTkLabel(

    app,

    text="Processing Options",

    font=(
        "Arial",
        18,
        "bold"
    )

).pack(
    pady=20
)


# ============================================
# REMOVE SILENCE
# ============================================

remove_silence = ctk.CTkCheckBox(

    app,

    text="Remove Silence",

    command=update_process_button
)

remove_silence.pack(
    pady=5
)


# ============================================
# REDUCE BACKGROUND NOISE
# ============================================

remove_noise = ctk.CTkCheckBox(

    app,

    text="Reduce Background Noise",

    command=update_process_button
)

remove_noise.pack(
    pady=5
)


# ============================================
# PROCESS BUTTON
# ============================================

process_button = ctk.CTkButton(

    app,

    text="PROCESS VIDEO",

    width=250,

    height=40,

    command=start_thread,

    state="disabled"
)

process_button.pack(
    pady=30
)


# ============================================
# PROGRESS BAR
# ============================================

progress_bar = ctk.CTkProgressBar(

    app,

    width=600
)

progress_bar.set(
    0
)

progress_bar.pack(
    pady=20
)


# ============================================
# STATUS
# ============================================

status = ctk.CTkLabel(

    app,

    text=(
        "Status: "
        "Select at least one processing option."
    ),

    font=(
        "Arial",
        14,
        "bold"
    ),

    wraplength=700
)

status.pack(
    pady=15
)


# ============================================
# START APPLICATION
# ============================================

app.mainloop()