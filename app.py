import customtkinter as ctk
from tkinter import filedialog
import threading

from audio.audio_processor import AudioProcessor
from video.video_processor import VideoProcessor


audio_processor = AudioProcessor()
video_processor = VideoProcessor()


# ============================================
# APPLICATION CONFIGURATION
# ============================================

app = ctk.CTk()

app.title("AutoCut Studio")
app.geometry("900x800")


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

        video_entry.delete(0, "end")
        video_entry.insert(0, path)


def select_output_folder():

    path = filedialog.askdirectory()

    if path:

        output_entry.delete(0, "end")
        output_entry.insert(0, path)


# ============================================
# STATUS
# ============================================

def update_status(text, progress=None):

    app.after(

        0,

        lambda: status.configure(
            text=text
        )

    )

    if progress is not None:

        app.after(

            0,

            lambda: progress_bar.set(progress)

        )


# ============================================
# PROCESSING
# ============================================

def start_thread():

    thread = threading.Thread(
        target=process_video
    )

    thread.daemon = True
    thread.start()


def process_video():

    try:

        video_path = video_entry.get()

        output_folder = output_entry.get()

        # ----------------------------------------
        # Validate video
        # ----------------------------------------

        if video_path == "":

            update_status(
                "Please select a video."
            )

            return

        # ----------------------------------------
        # Validate output folder
        # ----------------------------------------

        if output_folder == "":

            update_status(
                "Please select an output folder."
            )

            return

        # ----------------------------------------
        # Validate processing option
        # ----------------------------------------

        if remove_silence.get() == 0:

            update_status(
                "Please enable 'Remove Silence' before processing."
            )

            return

        update_status(
            "Analyzing audio...",
            0.20
        )

        clips = audio_processor.load_video(
            video_path,
            output_folder
        )

        update_status(
            "Cutting video...",
            0.60
        )

        final_video = video_processor.cut_video(
            video_path,
            clips,
            output_folder
        )

        update_status(
            f"Completed!\n\nOutput file:\n{final_video}",
            1
        )

    except Exception as error:

        print("=" * 50)
        print("ERROR")
        print(error)
        print("=" * 50)

        update_status(
            f"Error:\n{error}"
        )
        # ============================================
# USER INTERFACE
# ============================================

title = ctk.CTkLabel(
    app,
    text="AutoCut Studio",
    font=("Arial", 32, "bold")
)

title.pack(pady=30)


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

video_entry.pack(pady=10)

ctk.CTkButton(
    app,
    text="Select Video",
    command=select_video
).pack(pady=10)


# ============================================
# OUTPUT FOLDER
# ============================================

ctk.CTkLabel(
    app,
    text="Output Folder:"
).pack(pady=(20, 0))

output_entry = ctk.CTkEntry(
    app,
    width=600
)

output_entry.pack(pady=10)

ctk.CTkButton(
    app,
    text="Select Folder",
    command=select_output_folder
).pack(pady=10)


# ============================================
# PROCESSING OPTIONS
# ============================================

ctk.CTkLabel(
    app,
    text="Processing Options",
    font=("Arial", 18, "bold")
).pack(pady=20)

remove_silence = ctk.CTkCheckBox(
    app,
    text="Remove Silence"
)

remove_silence.pack(pady=5)

# Enabled by default
remove_silence.select()


# ============================================
# FUTURE FEATURES
# (Keep commented until implementation)
# ============================================

# remove_breath = ctk.CTkCheckBox(
#     app,
#     text="Remove Breathing"
# )
# remove_breath.pack(pady=5)

# remove_noise = ctk.CTkCheckBox(
#     app,
#     text="Remove Background Noise"
# )
# remove_noise.pack(pady=5)


# ============================================
# PROCESS BUTTON
# ============================================

ctk.CTkButton(
    app,
    text="PROCESS VIDEO",
    width=250,
    height=40,
    command=start_thread
).pack(pady=30)


# ============================================
# PROGRESS BAR
# ============================================

progress_bar = ctk.CTkProgressBar(
    app,
    width=600
)

progress_bar.set(0)

progress_bar.pack(pady=20)


# ============================================
# STATUS
# ============================================

status = ctk.CTkLabel(
    app,
    text="Status: Waiting for a video...",
    font=("Arial", 14, "bold"),
    wraplength=700
)

status.pack(pady=15)


# ============================================
# START APPLICATION
# ============================================

app.mainloop()