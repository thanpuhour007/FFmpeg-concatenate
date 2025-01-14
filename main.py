import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar, Button, END
import os
import subprocess

class VideoConcatenator:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Concatenator")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)
        
        # Center the window on the screen
        self.center_window()

    def center_window(self):
        # Get the screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate the x and y coordinates to center the window
        x = (screen_width // 2) - (1000 // 2)
        y = (screen_height // 2) - (800 // 2)
        
        # Set the geometry to center the window
        self.root.geometry(f"1000x800+{x}+{y}")

        self.video_dir = ""
        self.selected_videos = []
        self.video_extensions = ['.mp4', '.avi', '.mkv', '.mov']

        # Frame for video selection
        self.frame1 = tk.Frame(self.root)
        self.frame1.pack(pady=10, fill=tk.BOTH, expand=True)

        # Button to select video directory
        self.btn_select_dir = tk.Button(self.frame1, text="Select Video Directory", command=self.select_video_directory)
        self.btn_select_dir.pack(side=tk.TOP, padx=5, pady=5)

        # Listbox to display videos
        self.lb_videos = Listbox(self.frame1, selectmode=tk.MULTIPLE, width=100, height=30)
        self.lb_videos.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)

        # Scrollbar for the Listbox
        self.scrollbar = Scrollbar(self.frame1, orient="vertical", command=self.lb_videos.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.lb_videos.config(yscrollcommand=self.scrollbar.set)

        # Frame for concatenation buttons
        self.frame2 = tk.Frame(self.root)
        self.frame2.pack(pady=10, fill=tk.X)

        # Button to move videos up (aligned to the left)
        self.btn_move_up = tk.Button(self.frame2, text="Move Up", command=self.move_up)
        self.btn_move_up.pack(side=tk.LEFT, padx=5, pady=5)

        # Button to move videos down (aligned to the left)
        self.btn_move_down = tk.Button(self.frame2, text="Move Down", command=self.move_down)
        self.btn_move_down.pack(side=tk.LEFT, padx=5, pady=5)

        # Button to concatenate videos (aligned to the right)
        self.btn_concatenate = tk.Button(self.frame2, text="Concatenate Videos", command=self.concatenate_videos)
        self.btn_concatenate.pack(side=tk.RIGHT, padx=5, pady=5)

        # Status bar
        self.status = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def select_video_directory(self):
        self.video_dir = filedialog.askdirectory()
        if self.video_dir:
            self.lb_videos.delete(0, END)
            videos = [f for f in os.listdir(self.video_dir) if os.path.isfile(os.path.join(self.video_dir, f)) and os.path.splitext(f)[1].lower() in self.video_extensions]
            for video in videos:
                self.lb_videos.insert(END, video)
            self.status.config(text=f"Loaded {len(videos)} videos from {self.video_dir}")

    def move_up(self):
        selected_indices = self.lb_videos.curselection()
        if selected_indices:
            for index in selected_indices:
                if index > 0:
                    self.lb_videos.insert(index - 1, self.lb_videos.get(index))
                    self.lb_videos.delete(index + 1)
                    self.lb_videos.selection_set(index - 1)

    def move_down(self):
        selected_indices = self.lb_videos.curselection()
        if selected_indices:
            indices = list(selected_indices)
            indices.sort(reverse=True)
            for index in indices:
                if index < self.lb_videos.size() - 1:
                    self.lb_videos.insert(index + 2, self.lb_videos.get(index))
                    self.lb_videos.delete(index)
                    self.lb_videos.selection_set(index + 1)

    def concatenate_videos(self):
        selected_indices = self.lb_videos.curselection()
        if not selected_indices:
            messagebox.showwarning("No Videos Selected", "Please select at least two videos to concatenate.")
            return
        if len(selected_indices) < 2:
            messagebox.showwarning("Not Enough Videos", "Please select at least two videos to concatenate.")
            return

        # Get the selected video filenames
        self.selected_videos = [self.lb_videos.get(i) for i in selected_indices]
        # Ask for output filename
        output_file = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4"), ("AVI files", "*.avi"), ("MKV files", "*.mkv")])
        if not output_file:
            return  # User canceled the save dialog

        # Create a text file with the list of input videos
        with open("input_list.txt", "w") as f:
            for video in self.selected_videos:
                f.write(f"file '{os.path.join(self.video_dir, video)}'\n")

        # ffmpeg command to concatenate videos
        ffmpeg_cmd = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'input_list.txt', '-c', 'copy', output_file]

        self.status.config(text="Concatenating videos...")

        try:
            subprocess.call(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.status.config(text="Videos have been concatenated successfully.")
            messagebox.showinfo("Success", "Videos have been concatenated successfully.")
        except Exception as e:
            self.status.config(text=f"Error: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            # Remove the input list file
            if os.path.exists("input_list.txt"):
                os.remove("input_list.txt")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoConcatenator(root)
    root.mainloop()