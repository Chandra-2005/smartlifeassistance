import tkinter as tk
from tkinter import messagebox
import time
import threading
from datetime import datetime
from plyer import notification

class PhoneUsageTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Phone Usage Tracker")
        self.root.geometry("400x400")  
        self.root.config(bg="#f5f5f5")  

        
        self.activities = {}
        self.is_tracking = False
        
        
        self.activity_label = tk.Label(root, text="Enter activities for each hour (24-hour format):", bg="#f5f5f5", font=("Helvetica", 12))
        self.activity_label.pack(pady=10)

        
        time_frame = tk.Frame(root, bg="#f5f5f5")
        time_frame.pack(pady=5)

        self.hour_label = tk.Label(time_frame, text="Hour (0-23):", bg="#f5f5f5", font=("Helvetica", 12))
        self.hour_label.pack(side=tk.LEFT)

        self.hour_entry = tk.Entry(time_frame, width=5)
        self.hour_entry.pack(side=tk.LEFT, padx=5)

        self.minute_label = tk.Label(time_frame, text="Minute (0-59):", bg="#f5f5f5", font=("Helvetica", 12))
        self.minute_label.pack(side=tk.LEFT)

        self.minute_entry = tk.Entry(time_frame, width=5)
        self.minute_entry.pack(side=tk.LEFT, padx=5)

        self.activity_hour_label = tk.Label(root, text="Enter Activity for this Time:", bg="#f5f5f5", font=("Helvetica", 12))
        self.activity_hour_label.pack(pady=5)

        self.activity_entry = tk.Entry(root, width=50)
        self.activity_entry.pack(pady=5)

        self.add_activity_button = tk.Button(root, text="Add Activity", command=self.add_activity, bg="#4CAF50", fg="white", font=("Helvetica", 12))
        self.add_activity_button.pack(pady=10)

        self.start_button = tk.Button(root, text="Start Tracking", command=self.start_tracking, bg="#2196F3", fg="white", font=("Helvetica", 12))
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop Tracking", command=self.stop_tracking, bg="#F44336", fg="white", font=("Helvetica", 12))
        self.stop_button.pack(pady=10)

        self.quit_button = tk.Button(root, text="Quit", command=root.quit, bg="#9E9E9E", fg="white", font=("Helvetica", 12))
        self.quit_button.pack(pady=10)

    def add_activity(self):
        hour = self.hour_entry.get()
        minute = self.minute_entry.get()
        activity = self.activity_entry.get()
        
        if not hour.isdigit() or not 0 <= int(hour) <= 23:
            messagebox.showwarning("Input Error", "Please enter a valid hour (0-23).")
            return
        
        if not minute.isdigit() or not 0 <= int(minute) <= 59:
            messagebox.showwarning("Input Error", "Please enter a valid minute (0-59).")
            return
        
        if not activity.strip():
            messagebox.showwarning("Input Error", "Please enter an activity.")
            return
        
        
        self.activities[(int(hour), int(minute))] = activity.strip()
        messagebox.showinfo("Activity Added", f"Activity for {hour}:{minute} has been set to: {activity}")
        
        
        self.hour_entry.delete(0, tk.END)
        self.minute_entry.delete(0, tk.END)
        self.activity_entry.delete(0, tk.END)
    
    def start_tracking(self):
        if not self.activities:
            messagebox.showwarning("Input Error", "Please add at least one activity.")
            return
        
        if self.is_tracking:
            messagebox.showwarning("Tracking", "Tracking is already in progress!")
            return
        
        self.is_tracking = True
        messagebox.showinfo("Tracking Started", "Phone usage tracking started!")
        
        
        tracking_thread = threading.Thread(target=self.track_phone_usage)
        tracking_thread.daemon = True  
        tracking_thread.start()

    def track_phone_usage(self):
        while self.is_tracking:
            current_time = (datetime.now().hour, datetime.now().minute)
            
            
            if current_time in self.activities:
                self.send_notification(current_time[0], current_time[1])
            
            
            time.sleep(60)

    def send_notification(self, hour, minute):
        activity = self.activities[(hour, minute)]
        notification.notify(
            title="Phone Usage Alert!",
            message=f"You are using your phone at {hour:02d}:{minute:02d}. Consider doing: {activity}",
            timeout=10  
        )
        messagebox.showinfo("Notification Sent", f"Try this activity for {hour:02d}:{minute:02d}: {activity}")
    
    def stop_tracking(self):
        self.is_tracking = False
        messagebox.showinfo("Tracking Stopped", "Phone usage tracking stopped.")


if __name__ == "__main__":
    root = tk.Tk()
    app = PhoneUsageTracker(root)
    root.mainloop()
