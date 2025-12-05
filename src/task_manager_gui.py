import json
import os
import sys
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import ctypes  # Fix taskbar icon on Windows


# -------------------- Task Manager Logic -------------------- #
class TaskManager:
    def __init__(self, file_name="tasks.json"):
        self.file_name = file_name
        self.tasks = self.load_tasks()

    def load_tasks(self):
        if not os.path.exists(self.file_name):
            return []
        try:
            with open(self.file_name, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def save_tasks(self):
        with open(self.file_name, "w") as f:
            json.dump(self.tasks, f, indent=4)

    def add_task(self, title):
        task = {
            "id": len(self.tasks) + 1,
            "title": title,
            "completed": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.tasks.append(task)
        self.save_tasks()

    def delete_task(self, task_id):
        self.tasks = [task for task in self.tasks if task["id"] != task_id]
        self.save_tasks()

    def mark_done(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
        self.save_tasks()


# -------------------- GUI -------------------- #
class TaskManagerGUI:
    def __init__(self, root):
        self.manager = TaskManager()
        self.root = root

        self.root.title("Task Manager")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)

        icon_path = os.path.join(base_path, "../assets/task_icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u"taskmanager.app")
            except:
                pass

        tk.Label(root, text="Task Manager", font=("Arial", 20, "bold")).pack(pady=10)

        self.tree = ttk.Treeview(root, columns=("Title", "Status", "Created"), show="headings")
        self.tree.heading("Title", text="Task Title")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Created", text="Created At")
        self.tree.column("Title", width=250, anchor="w")
        self.tree.column("Status", width=100, anchor="center")
        self.tree.column("Created", width=150, anchor="center")
        self.tree.pack(pady=20, fill=tk.BOTH, expand=True)

        frame = tk.Frame(root)
        frame.pack(pady=10)
        tk.Button(frame, text="Add Task", width=12, command=self.add_task).grid(row=0, column=0, padx=5)
        tk.Button(frame, text="Mark Done", width=12, command=self.mark_done).grid(row=0, column=1, padx=5)
        tk.Button(frame, text="Delete Task", width=12, command=self.delete_task).grid(row=0, column=2, padx=5)
        tk.Button(frame, text="Refresh", width=12, command=self.refresh).grid(row=0, column=3, padx=5)

        self.refresh()

    # -------------------- GUI Actions -------------------- #
    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for task in self.manager.tasks:
            status = "✔ Done" if task["completed"] else "⏳ Pending"
            self.tree.insert("", "end", iid=task["id"], values=(task["title"], status, task["created_at"]))

    def add_task(self):
        title = simpledialog.askstring("Add Task", "Enter task title:")
        if title:
            self.manager.add_task(title)
            self.refresh()

    def delete_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No task selected")
            return
        task_id = int(selected[0])
        self.manager.delete_task(task_id)
        self.refresh()

    def mark_done(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No task selected")
            return
        task_id = int(selected[0])
        self.manager.mark_done(task_id)
        self.refresh()


# -------------------- Run App -------------------- #
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerGUI(root)
    root.mainloop()