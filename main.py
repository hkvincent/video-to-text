import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, ttk
import os

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(fill="both", expand=True)  # Allow the frame to expand
        self.create_widgets()

    def create_widgets(self):
        self.left_frame = tk.Frame(self)
        self.left_frame.pack(side="left", fill="both", expand=True)  # Allow the frame to expand

        self.right_frame = tk.Frame(self)
        self.right_frame.pack(side="right", fill="both", expand=True)  # Allow the frame to expand

        self.upper_left_frame = tk.Frame(self.left_frame)
        self.upper_left_frame.pack(side="top", fill="both", expand=True)  # Allow the frame to expand

        self.lower_left_frame = tk.Frame(self.left_frame)
        self.lower_left_frame.pack(side="bottom", fill="both", expand=True)  # Allow the frame to expand

        self.label = tk.Label(self.lower_left_frame, text="Choose your video: ")
        self.label.pack(side="left")

        self.entry = tk.Entry(self.lower_left_frame)
        self.entry.pack(side="left")

        self.button = tk.Button(self.lower_left_frame, text="Choose", command=self.choose_video)
        self.button.pack(side="left")

        self.table = ttk.Treeview(self.upper_left_frame, columns=('Video Path', 'Audio Path', 'Text Path'), show='headings')

        self.table.heading('Video Path', text='Video Path')
        self.table.heading('Audio Path', text='Audio Path')
        self.table.heading('Text Path', text='Text Path')
        self.table.pack(fill="both", expand=True)  # Allow the table to expand

        # Make the columns resizable
        self.table.column('Video Path', stretch=True)
        self.table.column('Audio Path', stretch=True)
        self.table.column('Text Path', stretch=True)

        # Configure the table's parent frame to distribute extra space to the table
        self.upper_left_frame.columnconfigure(0, weight=1)
        self.upper_left_frame.rowconfigure(0, weight=1)

        self.extract_button = tk.Button(self.right_frame, text="Extract Audio", command=self.extract_audio)
        self.extract_button.pack()

        self.generate_button = tk.Button(self.right_frame, text="Generate Text", command=self.generate_text)
        self.generate_button.pack()

        self.summary_button = tk.Button(self.right_frame, text="Summary", command=self.summary)
        self.summary_button.pack()

        self.delete_button = tk.Button(self.right_frame, text="Delete", command=self.delete_row)
        self.delete_button.pack()

        # Bind double-click event
        self.table.bind("<Double-1>", self.on_double_click)

    def on_double_click(self, event):
        item_id = self.table.identify_row(event.y)
        column = self.table.identify_column(event.x)
        value = self.table.set(item_id, column)
        if value and os.path.exists(value):
            os.startfile(value)

    def choose_video(self):
        self.video_path = filedialog.askopenfilename()
        self.entry.insert(0, self.video_path)
        self.table.insert('', 'end', values=(self.video_path, '', ''))

    def extract_audio(self):
        # Use ffmpeg to extract audio
        audio_path = self.video_path.rsplit('.', 1)[0] + '.mp3'
        command = f'ffmpeg -i "{self.video_path}" -vn -acodec libmp3lame -ac 2 -q:a 4 "{audio_path}"'
        subprocess.call(command, shell=True)
        self.table.set(self.table.get_children()[0], 'Audio Path', audio_path)

    def generate_text(self):
        # Path to the audio file
        audio_path = self.table.item(self.table.get_children()[0], 'values')[1]
        # Directory to the output text file
        output_dir = os.path.dirname(audio_path)
        # Command to run Whisper
        command = f'whisper --output_dir {output_dir} --output_format txt {audio_path}'
        # Run the command
        # subprocess.run(command, shell=True, check=True)
        # Path to the output text file
        text_path = os.path.join(output_dir, os.path.splitext(os.path.basename(audio_path))[0] + '.txt')
        # Update the table with the path to the text file
        self.table.set(self.table.get_children()[0], 'Text Path', text_path)

        def run_subprocess():
            subprocess.run(command, shell=True, check=True)

        thread = threading.Thread(target=run_subprocess)
        thread.start()

    def summary(self):
        # Generate summary
        pass

    def delete_row(self):
        selected_item = self.table.selection()[0]  # get selected item
        self.table.delete(selected_item)

root = tk.Tk()
app = Application(master=root)
app.mainloop()
