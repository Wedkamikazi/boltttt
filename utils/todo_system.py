from enum import Enum
import json
from datetime import datetime
from pathlib import Path

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class TaskStatus(Enum):
    """Task status states"""
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    SUBMITTED = "Submitted"
    UNDER_REVIEW = "Under Review"
    COMPLETED = "Completed"
    RETURNED = "Returned"

class UserRole(Enum):
    """User roles"""
    USER = "User"
    ADMIN = "Admin"

class Task:
    """Represents a task in the todo system"""
    def __init__(self, description, owner, deadline, priority=TaskPriority.MEDIUM, created_by=None):
        self.description = description
        self.owner = owner
        self.deadline = deadline
        self.priority = priority
        self.created_by = created_by or owner
        self.creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.last_edited = self.creation_date
        self.status = TaskStatus.NOT_STARTED
        self.reviewer = None
        self.feedback_history = []  # List of {user, timestamp, message}
        self.archived = False
        self.archived_date = None

    def add_feedback(self, user, message):
        """Add feedback with user and timestamp"""
        feedback_entry = {
            'user': user,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'message': message
        }
        self.feedback_history.append(feedback_entry)
        self.last_edited = feedback_entry['timestamp']

    def to_dict(self):
        """Convert task to dictionary for serialization"""
        return {
            "description": self.description,
            "owner": self.owner,
            "deadline": self.deadline,
            "priority": self.priority.value,
            "created_by": self.created_by,
            "creation_date": self.creation_date,
            "last_edited": self.last_edited,
            "status": self.status.value,
            "reviewer": self.reviewer,
            "feedback_history": self.feedback_history,
            "archived": self.archived,
            "archived_date": self.archived_date
        }

    @classmethod
    def from_dict(cls, data):
        """Create task from dictionary"""
        task = cls(
            description=data["description"],
            owner=data["owner"],
            deadline=data["deadline"],
            priority=TaskPriority(data["priority"]),
            created_by=data["created_by"]
        )
        task.creation_date = data["creation_date"]
        task.last_edited = data["last_edited"]
        task.status = TaskStatus(data["status"])
        task.reviewer = data["reviewer"]
        task.feedback_history = data.get("feedback_history", [])
        task.archived = data["archived"]
        task.archived_date = data["archived_date"]
        return task

class TodoManager:
    """Manages tasks in the todo system"""
    def __init__(self):
        self.tasks = []
        self.data_file = Path("todo_data.json")
        self.load_tasks()

    def add_task(self, task):
        """Add a new task"""
        self.tasks.append(task)
        self.save_tasks()

    def get_active_tasks(self):
        """Get all non-archived tasks"""
        return [task for task in self.tasks if not task.archived]

    def get_archived_tasks(self):
        """Get all archived tasks"""
        return [task for task in self.tasks if task.archived]

    def update_task_status(self, task, new_status, user, feedback=None):
        """Update task status with validation"""
        if task not in self.tasks:
            raise ValueError("Task not found")

        # Validate status transition
        if not self._is_valid_status_transition(task, new_status, user):
            raise ValueError(f"Invalid status transition from {task.status.value} to {new_status.value} by {user}")

        task.status = new_status
        task.last_edited = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if feedback is not None:
            task.add_feedback(user, feedback)

        self.save_tasks()

    def assign_reviewer(self, task, reviewer):
        """Assign a reviewer to a task"""
        if task not in self.tasks:
            raise ValueError("Task not found")

        task.reviewer = reviewer
        task.last_edited = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_tasks()

    def archive_task(self, task, user=None):
        """Archive a task. Only task owner, reviewer, or admin can archive."""
        if not task:
            raise ValueError("Task cannot be None")
            
        if user is None:
            raise ValueError("User must be specified for archiving")
            
        # Check permissions
        is_owner = task.owner == user.username
        is_reviewer = task.reviewer == user.username
        is_admin = user.role == UserRole.ADMIN
        
        if not (is_owner or is_reviewer or is_admin):
            raise ValueError("Only task owner, reviewer, or admin can archive tasks")

        task.archived = True
        task.archived_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_tasks()

    def save_tasks(self):
        """Save tasks to file"""
        try:
            data = {
                'tasks': [task.to_dict() for task in self.tasks],
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Ensure parent directory exists
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving tasks: {str(e)}")

    def load_tasks(self):
        """Load tasks from file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'tasks' in data:
                        self.tasks = [Task.from_dict(task_data) for task_data in data['tasks']]
                    else:
                        self.tasks = []
            else:
                self.tasks = []
        except Exception as e:
            print(f"Error loading tasks: {str(e)}")
            self.tasks = []

    def _is_valid_status_transition(self, task, new_status, user):
        """Validate status transition based on current status and user role"""
        is_owner = user == task.owner
        is_reviewer = user == task.reviewer

        # Define valid transitions based on current status and user role
        valid_transitions = {
            TaskStatus.NOT_STARTED: {
                "owner": [TaskStatus.IN_PROGRESS],
                "reviewer": []
            },
            TaskStatus.IN_PROGRESS: {
                "owner": [TaskStatus.SUBMITTED],
                "reviewer": []
            },
            TaskStatus.SUBMITTED: {
                "owner": [],
                "reviewer": [TaskStatus.UNDER_REVIEW, TaskStatus.COMPLETED, TaskStatus.RETURNED]
            },
            TaskStatus.UNDER_REVIEW: {
                "owner": [],
                "reviewer": [TaskStatus.COMPLETED, TaskStatus.RETURNED]
            },
            TaskStatus.COMPLETED: {
                "owner": [],
                "reviewer": []
            },
            TaskStatus.RETURNED: {
                "owner": [TaskStatus.IN_PROGRESS],
                "reviewer": []
            }
        }

        # Get allowed transitions based on user role
        if is_owner:
            allowed_transitions = valid_transitions[task.status]["owner"]
        elif is_reviewer:
            allowed_transitions = valid_transitions[task.status]["reviewer"]
        else:
            allowed_transitions = []

        return new_status in allowed_transitions
