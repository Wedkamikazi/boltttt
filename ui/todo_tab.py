import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import tkcalendar
from utils.todo_system import TodoManager, Task, TaskPriority, TaskStatus, UserRole
from pathlib import Path

class TodoTab:
    def __init__(self, parent, current_user):
        self.parent = parent
        self.current_user = current_user
        self.todo_manager = TodoManager()
        
        # Set data file path and ensure directory exists
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.todo_manager.data_file = self.data_dir / "todo_data.json"
        
        # Create main frame with padding
        self.main_frame = ttk.Frame(parent, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create paned window for resizable split
        self.paned = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # Create left frame (task list)
        left_frame = ttk.Frame(self.paned)
        self.paned.add(left_frame, weight=1)
        
        # Create right frame (task details)
        right_frame = ttk.Frame(self.paned)
        self.paned.add(right_frame, weight=1)
        
        # Task List Frame
        task_frame = ttk.LabelFrame(left_frame, text="Tasks", padding=5)
        task_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add New Task button at the top
        new_task_frame = ttk.Frame(task_frame)
        new_task_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(new_task_frame, text="New Task", command=self.start_new_task).pack(side=tk.LEFT, padx=5)
        
        # Create Treeview with scrollbar
        tree_frame = ttk.Frame(task_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(tree_frame, columns=('Owner', 'Reviewer', 'Status', 'Deadline', 'Priority'))
        
        # Configure column headings
        self.tree.heading('#0', text='Description')
        self.tree.heading('Owner', text='Owner')
        self.tree.heading('Reviewer', text='Reviewer')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Deadline', text='Deadline')
        self.tree.heading('Priority', text='Priority')
        
        # Set initial column widths
        self.tree.column('#0', width=200, minwidth=150)  # Description column
        self.tree.column('Owner', width=100, minwidth=80)
        self.tree.column('Reviewer', width=100, minwidth=80)
        self.tree.column('Status', width=100, minwidth=80)
        self.tree.column('Deadline', width=100, minwidth=80)
        self.tree.column('Priority', width=80, minwidth=60)
        
        # Configure column stretching
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout for tree and scrollbars
        self.tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        # Task Details Frame
        self.details_frame = ttk.LabelFrame(right_frame, text="Task Details", padding=5)
        self.details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Task Form
        form_frame = ttk.Frame(self.details_frame)
        form_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Grid layout for form
        row = 0
        
        ttk.Label(form_frame, text="Description:").grid(row=row, column=0, sticky='w', pady=2)
        self.description_var = tk.StringVar()
        self.description_entry = ttk.Entry(form_frame, textvariable=self.description_var)
        self.description_entry.grid(row=row, column=1, sticky='ew', pady=2)
        row += 1
        
        ttk.Label(form_frame, text="Owner:").grid(row=row, column=0, sticky='w', pady=2)
        self.owner_var = tk.StringVar()
        self.owner_entry = ttk.Entry(form_frame, textvariable=self.owner_var)
        self.owner_entry.grid(row=row, column=1, sticky='ew', pady=2)
        row += 1
        
        ttk.Label(form_frame, text="Reviewer:").grid(row=row, column=0, sticky='w', pady=2)
        self.reviewer_var = tk.StringVar()
        self.reviewer_entry = ttk.Entry(form_frame, textvariable=self.reviewer_var)
        self.reviewer_entry.grid(row=row, column=1, sticky='ew', pady=2)
        row += 1
        
        ttk.Label(form_frame, text="Deadline:").grid(row=row, column=0, sticky='w', pady=2)
        deadline_frame = ttk.Frame(form_frame)
        deadline_frame.grid(row=row, column=1, sticky='ew', pady=2)
        self.deadline_cal = tkcalendar.DateEntry(deadline_frame, width=12, background='darkblue',
                                               foreground='white', borderwidth=2)
        self.deadline_cal.pack(side=tk.LEFT)
        row += 1
        
        ttk.Label(form_frame, text="Priority:").grid(row=row, column=0, sticky='w', pady=2)
        self.priority_var = tk.StringVar(value=TaskPriority.MEDIUM.value)
        priority_frame = ttk.Frame(form_frame)
        priority_frame.grid(row=row, column=1, sticky='ew', pady=2)
        for priority in TaskPriority:
            ttk.Radiobutton(priority_frame, text=priority.value,
                          variable=self.priority_var, value=priority.value).pack(side=tk.LEFT)
        row += 1
        
        # Configure grid column weights
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Feedback History Frame
        feedback_frame = ttk.LabelFrame(self.details_frame, text="Feedback History", padding=5)
        feedback_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Feedback history display
        self.feedback_history = tk.Text(feedback_frame, height=8, width=40, state='disabled')
        self.feedback_history.pack(fill=tk.BOTH, expand=True)
        
        # New feedback entry
        feedback_entry_frame = ttk.Frame(feedback_frame)
        feedback_entry_frame.pack(fill=tk.X, pady=5)
        self.new_feedback = tk.Text(feedback_entry_frame, height=3, width=40)
        self.new_feedback.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Button(feedback_entry_frame, text="Add Feedback", command=self.add_feedback).pack(side=tk.RIGHT, padx=5)
        
        # Action buttons
        button_frame = ttk.Frame(self.details_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.save_button = ttk.Button(button_frame, text="Save", command=self.save_task)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.archive_button = ttk.Button(button_frame, text="Archive", command=self.archive_task)
        self.archive_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="View History", command=self.show_history).pack(side=tk.LEFT, padx=5)
        
        # Bind tree selection
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Initial update
        self.update_task_list()
        self.is_new_task = True
        self.disable_form_editing()

    def start_new_task(self):
        """Start creating a new task"""
        self.is_new_task = True
        self.enable_form_editing()
        self.clear_form()
        self.owner_var.set(self.current_user.username)
        self.tree.selection_remove(self.tree.selection())
        self.update_button_states()
        
    def enable_form_editing(self):
        """Enable form fields for editing"""
        self.description_entry.configure(state='normal')
        self.owner_entry.configure(state='normal')
        self.reviewer_entry.configure(state='normal')
        self.deadline_cal.configure(state='normal')
        
    def disable_form_editing(self):
        """Disable form fields for editing"""
        self.description_entry.configure(state='disabled')
        self.owner_entry.configure(state='disabled')
        self.reviewer_entry.configure(state='disabled')
        self.deadline_cal.configure(state='disabled')

    def clear_form(self):
        """Clear all form fields"""
        self.description_var.set("")
        self.owner_var.set("")
        self.reviewer_var.set("")
        self.deadline_cal.set_date(datetime.now())
        self.priority_var.set(TaskPriority.MEDIUM.value)
        self.new_feedback.delete("1.0", tk.END)
        self.feedback_history.configure(state='normal')
        self.feedback_history.delete("1.0", tk.END)
        self.feedback_history.configure(state='disabled')

    def add_feedback(self):
        """Add feedback to the current task"""
        task = self._get_selected_task()
        if not task:
            messagebox.showwarning("Warning", "Please select a task")
            return
            
        feedback = self.new_feedback.get("1.0", tk.END).strip()
        if not feedback:
            messagebox.showwarning("Warning", "Please enter feedback")
            return
            
        task.add_feedback(self.current_user.username, feedback)
        self.todo_manager.save_tasks()
        self.update_feedback_history(task)
        self.new_feedback.delete("1.0", tk.END)
        messagebox.showinfo("Success", "Feedback added successfully")

    def update_feedback_history(self, task):
        """Update the feedback history display"""
        self.feedback_history.configure(state='normal')
        self.feedback_history.delete("1.0", tk.END)
        
        for entry in task.feedback_history:
            self.feedback_history.insert(tk.END, 
                f"[{entry['timestamp']}] {entry['user']}:\n{entry['message']}\n\n")
        
        self.feedback_history.configure(state='disabled')

    def save_task(self):
        """Save new task only"""
        if not self.is_new_task:
            messagebox.showwarning("Warning", "Cannot modify existing task details")
            return
            
        description = self.description_var.get().strip()
        owner = self.owner_var.get().strip()
        reviewer = self.reviewer_var.get().strip()
        deadline = self.deadline_cal.get_date().strftime("%Y-%m-%d")
        priority = TaskPriority(self.priority_var.get())

        if not all([description, owner, deadline]):
            messagebox.showwarning("Warning", "Description, owner, and deadline are required")
            return

        # Create new task
        task = Task(
            description=description,
            owner=owner,
            deadline=deadline,
            priority=priority,
            created_by=self.current_user.username
        )

        # Add task to manager
        self.todo_manager.add_task(task)

        # Then assign reviewer if provided
        if reviewer:
            try:
                self.todo_manager.assign_reviewer(task, reviewer)
            except ValueError as e:
                messagebox.showwarning("Warning", str(e))

        # Update GUI
        self.update_task_list()
        self.clear_form()
        self.disable_form_editing()
        self.is_new_task = False
        messagebox.showinfo("Success", "New task created successfully")

    def on_select(self, event):
        """Handle task selection"""
        selected = self.tree.selection()
        if not selected:
            self.clear_form()
            self.is_new_task = True
            self.enable_form_editing()
            return

        task = self._get_selected_task()
        if not task:
            return

        # Load task details into form
        self.description_var.set(task.description)
        self.owner_var.set(task.owner)
        self.reviewer_var.set(task.reviewer if task.reviewer else "")
        self.deadline_cal.set_date(datetime.strptime(task.deadline, "%Y-%m-%d"))
        self.priority_var.set(task.priority.value)
        
        # Update feedback history
        self.update_feedback_history(task)
        
        # Disable form editing for existing tasks
        self.disable_form_editing()
        self.is_new_task = False
        self.update_button_states()

    def update_task_list(self):
        """Update task list display"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add active tasks
        for i, task in enumerate(self.todo_manager.get_active_tasks()):
            item_id = f"I{i+1:03d}"  # Generate predictable IDs
            self.tree.insert('', 'end', iid=item_id, text=task.description, values=(
                task.owner,
                task.reviewer if task.reviewer else "",
                task.status.value,
                task.deadline,
                task.priority.value
            ))

    def update_button_states(self):
        """Update button states based on selected task and user permissions"""
        selected = self.tree.selection()
        if not selected:
            self.save_button.configure(state='normal')
            self.archive_button.configure(state='disabled')
            return

        task = self._get_selected_task()
        if not task:
            self.save_button.configure(state='disabled')
            self.archive_button.configure(state='disabled')
            return

        # Disable save button for existing tasks
        self.save_button.configure(state='disabled')
        
        # Enable archive button only for owner, reviewer, or admin
        can_archive = (
            task.owner == self.current_user.username or
            task.reviewer == self.current_user.username or
            self.current_user.role == UserRole.ADMIN
        )
        self.archive_button.configure(state='normal' if can_archive else 'disabled')

    def _get_selected_task(self):
        """Get task object from selected tree item"""
        selected = self.tree.selection()
        if not selected:
            return None

        item = selected[0]
        description = self.tree.item(item)["text"]
        owner = self.tree.item(item)["values"][0]

        for task in self.todo_manager.get_active_tasks():
            if task.description == description and task.owner == owner:
                return task

        return None

    def start_work(self):
        """Start work on selected task"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task")
            return

        task = self._get_selected_task()
        if not task:
            return

        try:
            self.todo_manager.update_task_status(task, TaskStatus.IN_PROGRESS, self.current_user.username)
            self.update_task_list()
            self.update_button_states()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def submit_task(self):
        """Submit task for review"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task")
            return

        task = self._get_selected_task()
        if not task:
            return

        try:
            self.todo_manager.update_task_status(task, TaskStatus.SUBMITTED, self.current_user.username)
            self.update_task_list()
            self.update_button_states()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def start_review(self):
        """Start reviewing selected task"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task")
            return

        task = self._get_selected_task()
        if not task:
            return

        try:
            self.todo_manager.update_task_status(task, TaskStatus.UNDER_REVIEW, self.current_user.username)
            self.update_task_list()
            self.update_button_states()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def complete_task(self):
        """Mark task as completed"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task")
            return

        task = self._get_selected_task()
        if not task:
            return

        try:
            self.todo_manager.update_task_status(task, TaskStatus.COMPLETED, self.current_user.username)
            self.update_task_list()
            self.update_button_states()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def return_task(self):
        """Return task for revision"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task")
            return

        task = self._get_selected_task()
        if not task:
            return

        feedback = self.feedback_text.get("1.0", tk.END).strip()
        if not feedback:
            messagebox.showwarning("Warning", "Please provide feedback for the return")
            return

        try:
            self.todo_manager.update_task_status(task, TaskStatus.RETURNED, self.current_user.username, feedback)
            self.update_task_list()
            self.update_button_states()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def archive_task(self):
        """Archive selected task"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task")
            return

        task = self._get_selected_task()
        if not task:
            return

        try:
            self.todo_manager.archive_task(task, self.current_user)
            self.update_task_list()
            self.clear_form()
            self.disable_form_editing()
            messagebox.showinfo("Success", "Task archived successfully")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def show_history(self):
        """Show archived tasks"""
        HistoryWindow(self.parent, self.todo_manager)

class HistoryWindow(tk.Toplevel):
    def __init__(self, parent, todo_manager):
        super().__init__(parent)
        self.title("Task History")
        self.todo_manager = todo_manager
        
        # Configure window
        self.geometry("800x600")
        self.minsize(600, 400)
        
        # Create main frame
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create tree view
        self.tree = ttk.Treeview(main_frame, columns=('Owner', 'Reviewer', 'Status', 'Deadline', 'Priority', 'Archived Date'))
        self.tree.heading('#0', text='Description')
        self.tree.heading('Owner', text='Owner')
        self.tree.heading('Reviewer', text='Reviewer')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Deadline', text='Deadline')
        self.tree.heading('Priority', text='Priority')
        self.tree.heading('Archived Date', text='Archived Date')
        
        self.tree.column('#0', width=200)
        self.tree.column('Owner', width=100)
        self.tree.column('Reviewer', width=100)
        self.tree.column('Status', width=100)
        self.tree.column('Deadline', width=100)
        self.tree.column('Priority', width=80)
        self.tree.column('Archived Date', width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add close button
        close_button = ttk.Button(self, text="Close", command=self.destroy)
        close_button.pack(pady=10)
        
        # Populate tree
        self.populate_tree()
        
        # Make window modal
        self.transient(parent)
        self.grab_set()
        
    def populate_tree(self):
        """Populate tree with archived tasks"""
        for task in self.todo_manager.get_archived_tasks():
            self.tree.insert("", tk.END, text=task.description, values=(
                task.owner,
                task.reviewer if task.reviewer else "",
                task.status.value,
                task.deadline,
                task.priority.value,
                task.archived_date
            ))
