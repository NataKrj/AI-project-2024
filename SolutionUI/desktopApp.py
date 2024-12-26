import tkinter as tk
from tkinter import filedialog
import subprocess
import os
import threading

selected_file_path = None
result_csv_path = None

def load_file():
    global selected_file_path
    file_path = filedialog.askopenfilename(
        title="Select a File",
        filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
    )
    if file_path:
        selected_file_path = file_path
        label_file.config(text=f"Selected File: {file_path}", fg="#29577e")
    else:
        label_file.config(text="No file selected", fg="#9e366b")

def process_scripts():
    global selected_file_path, result_csv_path
    if selected_file_path:
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            scripts = [
                ("First script", os.path.join(current_dir, "getSanctionData.py"), status_first),
                ("Second script", os.path.join(current_dir, "asyncScrapKBO.py"), status_second),
                ("Third script", os.path.join(current_dir, "CompanyAnalysis.py"), status_third),
                ("Fourth script", os.path.join(current_dir, "finAnalysis.py"), status_fourth)
            ]
            for script_name, script_path, status_label in scripts:
                status_label.config(text=f"{script_name}: In progress...", fg="#9e366b")
                root.update_idletasks()
                print(f"Running {script_name} with file {selected_file_path}")
                result = subprocess.run(
                    ["python", script_path, selected_file_path],
                    text=True,
                    capture_output=True
                )
                print(f"{script_name} stdout: {result.stdout}")
                print(f"{script_name} stderr: {result.stderr}")
                if result.returncode == 0:
                    status_label.config(text=f"{script_name}: Completed ✅", fg="#29577e")
                else:
                    status_label.config(text=f"{script_name}: Failed ❌", fg="#9e366b")
                    status_global.config(
                        text=f"Error in {script_name}: {result.stderr.strip()}",
                        fg="#9e366b"
                    )
                    return
            result_csv_path = os.path.join(current_dir, "result.csv")
            status_global.config(
                text=f"Processing completed! Result saved at:\n{result_csv_path}",
                font=("Arial", 12, "bold"),
                fg="#674e74"
            )
        except Exception as e:
            status_global.config(text=f"Unexpected error: {str(e)}", fg="#9e366b")
            print(f"Unexpected error: {str(e)}")
    else:
        status_global.config(text="Please select a file first!", fg="#9e366b")

def start_processing():
    thread = threading.Thread(target=process_scripts)
    thread.start()

root = tk.Tk()
root.title("CSV File Processor")
root.geometry("700x500")
root.configure(bg="#BEBCBB")

title_label = tk.Label(
    root, 
    text="File Processing Application",
    font=("Helvetica", 16, "bold"),
    bg="#BEBCBB",
    fg="#35707f"
)
title_label.pack(pady=20)

frame_file = tk.Frame(root, bg="#BEBCBB", padx=10, pady=10, relief="groove", bd=2)
frame_file.pack(pady=10)

label_file = tk.Label(frame_file, text="No file selected", font=("Arial", 12), bg="#BEBCBB", fg="#29577e")
label_file.pack(pady=5)

button_load = tk.Button(
    frame_file, 
    text="Select File", 
    font=("Arial", 12), 
    bg="#3da8aa", 
    fg="white",
    activebackground="#954F72", 
    activeforeground="white",
    command=load_file
)
button_load.pack(pady=5)

frame_status = tk.Frame(root, bg="#BEBCBB", padx=10, pady=10)
frame_status.pack(pady=10)

status_global = tk.Label(frame_status, text="", font=("Arial", 12), bg="#BEBCBB", fg="#9e366b", wraplength=650, justify="center")
status_global.pack(pady=5)

status_first = tk.Label(frame_status, text="First script: Not started", font=("Arial", 12), bg="#BEBCBB", fg="black")
status_first.pack(pady=5)

status_second = tk.Label(frame_status, text="Second script: Not started", font=("Arial", 12), bg="#BEBCBB", fg="black")
status_second.pack(pady=5)

status_third = tk.Label(frame_status, text="Third script: Not started", font=("Arial", 12), bg="#BEBCBB", fg="black")
status_third.pack(pady=5)

status_fourth = tk.Label(frame_status, text="Fourth script: Not started", font=("Arial", 12), bg="#BEBCBB", fg="black")
status_fourth.pack(pady=5)

frame_buttons = tk.Frame(root, bg="#BEBCBB")
frame_buttons.pack(pady=20)

button_process = tk.Button(
    frame_buttons, 
    text="Process File", 
    font=("Arial", 12), 
    bg="#29577e", 
    fg="white",
    activebackground="#954F72", 
    activeforeground="white",
    command=start_processing
)
button_process.grid(row=0, column=0, padx=10, pady=5)

button_exit = tk.Button(
    frame_buttons, 
    text="Exit", 
    font=("Arial", 12), 
    bg="#9e366b", 
    fg="white",
    activebackground="#674e74", 
    activeforeground="white",
    command=root.destroy
)
button_exit.grid(row=0, column=1, padx=10, pady=5)

root.mainloop()
