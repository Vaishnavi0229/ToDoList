from datetime import datetime
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

class ToDoList:
    def __init__(self):
        self.tasks = []
        self.history = []  # For undo functionality
    
    def _add_to_history(self, action, task_data):
        """Record actions for undo functionality"""
        self.history.append((action, task_data))
        # Keep only the last 10 actions in history
        if len(self.history) > 10:
            self.history.pop(0)
    
    def _get_priority_color(self, priority):
        """Return color based on priority"""
        colors = {
            'High': Fore.RED + Style.BRIGHT,
            'Medium': Fore.YELLOW,
            'Low': Fore.GREEN
        }
        return colors.get(priority, Fore.WHITE)
    
    def add_task(self, description, category="General", priority="Medium", due_date=None):
        """Add a new task to the list"""
        task_id = len(self.tasks) + 1
        task = {
            'id': task_id,
            'description': description,
            'category': category,
            'priority': priority,
            'due_date': due_date,
            'completed': False,
            'created_at': datetime.now()
        }
        self.tasks.append(task)
        self._add_to_history('add', task.copy())
        print(f"\n{Fore.GREEN}Task '{description}' added successfully!{Style.RESET_ALL}")
    
    def view_tasks(self, filter_by=None, filter_value=None, sort_by=None):
        """View tasks with filtering and sorting options"""
        if not self.tasks:
            print(f"{Fore.YELLOW}\nNo tasks in the list!{Style.RESET_ALL}")
            return
        
        # Filter tasks
        filtered_tasks = self.tasks
        if filter_by and filter_value:
            filtered_tasks = [t for t in self.tasks 
                            if str(t.get(filter_by.lower(), '')).lower() == filter_value.lower()]
        
        # Sort tasks
        if sort_by:
            reverse_sort = False
            if sort_by.startswith('-'):
                sort_by = sort_by[1:]
                reverse_sort = True
            
            if sort_by == 'priority':
                priority_order = {'High': 1, 'Medium': 2, 'Low': 3}
                filtered_tasks.sort(key=lambda x: priority_order.get(x['priority'], 4), 
                                  reverse=reverse_sort)
            elif sort_by == 'due_date':
                filtered_tasks.sort(key=lambda x: x['due_date'] or datetime.max, 
                                  reverse=reverse_sort)
            else:
                filtered_tasks.sort(key=lambda x: x.get(sort_by, ''), 
                                  reverse=reverse_sort)
        
        # Display tasks
        print(f"\n{Back.BLUE}{Fore.WHITE}--- TO-DO LIST ---{Style.RESET_ALL}")
        print(f"{Fore.CYAN}ID  Description        Category    Priority   Due Date       Status{Style.RESET_ALL}")
        print("-" * 70)
        
        for task in filtered_tasks:
            priority_color = self._get_priority_color(task['priority'])
            status = f"{Fore.GREEN}✓" if task['completed'] else f"{Fore.RED} "
            due_date = task['due_date'].strftime("%Y-%m-%d") if task['due_date'] else "No date"
            
            print(f"{task['id']:2} {task['description'][:18]:18} {task['category'][:10]:10} "
                  f"{priority_color}{task['priority'][:7]:7}{Style.RESET_ALL} "
                  f"{due_date:13} [{status}{Style.RESET_ALL}]")
    
    def mark_complete(self, task_id):
        """Mark a task as complete"""
        for task in self.tasks:
            if task['id'] == task_id:
                original_status = task['completed']
                task['completed'] = True
                self._add_to_history('complete', {'id': task_id, 'original_status': original_status})
                print(f"\n{Fore.GREEN}Task '{task['description']}' marked as complete!{Style.RESET_ALL}")
                return
        print(f"{Fore.RED}\nTask not found!{Style.RESET_ALL}")
    
    def edit_task(self, task_id, **kwargs):
        """Edit task details"""
        for task in self.tasks:
            if task['id'] == task_id:
                original_task = task.copy()
                for key, value in kwargs.items():
                    if value is not None and key in task:
                        task[key] = value
                self._add_to_history('edit', {'id': task_id, 'original_data': original_task})
                print(f"\n{Fore.GREEN}Task updated successfully!{Style.RESET_ALL}")
                return
        print(f"{Fore.RED}\nTask not found!{Style.RESET_ALL}")
    
    def delete_task(self, task_id):
        """Delete a task from the list"""
        for i, task in enumerate(self.tasks):
            if task['id'] == task_id:
                deleted_task = self.tasks.pop(i)
                self._add_to_history('delete', deleted_task.copy())
                print(f"\n{Fore.GREEN}Task '{deleted_task['description']}' deleted!{Style.RESET_ALL}")
                # Reassign IDs to maintain order
                for j, t in enumerate(self.tasks[i:], start=i):
                    t['id'] = j + 1
                return
        print(f"{Fore.RED}\nTask not found!{Style.RESET_ALL}")
    
    def undo_last_action(self):
        """Undo the last performed action"""
        if not self.history:
            print(f"{Fore.YELLOW}\nNo actions to undo!{Style.RESET_ALL}")
            return
        
        action, task_data = self.history.pop()
        
        if action == 'add':
            # Remove the added task
            self.tasks = [t for t in self.tasks if t['id'] != task_data['id']]
        elif action == 'delete':
            # Restore the deleted task
            self.tasks.insert(task_data['id'] - 1, task_data)
            # Reassign IDs to maintain order
            for i, t in enumerate(self.tasks):
                t['id'] = i + 1
        elif action == 'edit':
            # Restore original task data
            for task in self.tasks:
                if task['id'] == task_data['id']:
                    task.update(task_data['original_data'])
                    break
        elif action == 'complete':
            # Revert completion status
            for task in self.tasks:
                if task['id'] == task_data['id']:
                    task['completed'] = task_data['original_status']
                    break
        
        print(f"\n{Fore.GREEN}Last action undone successfully!{Style.RESET_ALL}")

def get_valid_date(prompt):
    """Get a valid date input from user"""
    while True:
        date_str = input(prompt + " (YYYY-MM-DD, leave blank if none): ").strip()
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print(f"{Fore.RED}Invalid date format. Please use YYYY-MM-DD.{Style.RESET_ALL}")

def main():
    todo = ToDoList()
    
    while True:
        print(f"\n{Back.BLUE}{Fore.WHITE}===== TO-DO LIST MENU ====={Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. Add Task")
        print("2. View All Tasks")
        print("3. View Tasks by Category")
        print("4. View Tasks by Priority")
        print("5. Mark Task as Complete")
        print("6. Edit Task")
        print("7. Delete Task")
        print("8. Sort Tasks")
        print("9. Undo Last Action")
        print(f"10. Exit{Style.RESET_ALL}")
        
        choice = input(f"{Fore.YELLOW}\nEnter your choice (1-10): {Style.RESET_ALL}")
        
        if choice == '1':
            task = input("Enter task description: ")
            category = input("Enter category (default: General): ") or "General"
            priority = input("Enter priority (High/Medium/Low, default: Medium): ").capitalize() or "Medium"
            due_date = get_valid_date("Enter due date")
            todo.add_task(task, category, priority, due_date)
        
        elif choice == '2':
            todo.view_tasks()
        
        elif choice == '3':
            category = input("Enter category to filter by: ")
            todo.view_tasks(filter_by="category", filter_value=category)
        
        elif choice == '4':
            priority = input("Enter priority to filter by (High/Medium/Low): ").capitalize()
            todo.view_tasks(filter_by="priority", filter_value=priority)
        
        elif choice == '5':
            task_id = int(input("Enter task ID to mark as complete: "))
            todo.mark_complete(task_id)
        
        elif choice == '6':
            task_id = int(input("Enter task ID to edit: "))
            new_desc = input("Enter new description (leave blank to keep current): ")
            new_cat = input("Enter new category (leave blank to keep current): ")
            new_pri = input("Enter new priority (leave blank to keep current): ").capitalize()
            new_date = get_valid_date("Enter new due date")
            
            kwargs = {}
            if new_desc: kwargs['description'] = new_desc
            if new_cat: kwargs['category'] = new_cat
            if new_pri: kwargs['priority'] = new_pri
            if new_date is not None: kwargs['due_date'] = new_date
            
            todo.edit_task(task_id, **kwargs)
        
        elif choice == '7':
            task_id = int(input("Enter task ID to delete: "))
            todo.delete_task(task_id)
        
        elif choice == '8':
            print("\nSort by:")
            print("1. Priority (High to Low)")
            print("2. Priority (Low to High)")
            print("3. Due Date (Earliest first)")
            print("4. Due Date (Latest first)")
            print("5. Category")
            print("6. Creation Date (Newest first)")
            print("7. Creation Date (Oldest first)")
            
            sort_choice = input("Enter sort option (1-7): ")
            sort_options = {
                '1': '-priority',
                '2': 'priority',
                '3': 'due_date',
                '4': '-due_date',
                '5': 'category',
                '6': '-created_at',
                '7': 'created_at'
            }
            todo.view_tasks(sort_by=sort_options.get(sort_choice))
        
        elif choice == '9':
            todo.undo_last_action()
        
        elif choice == '10':
            print(f"\n{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
            break
        
        else:
            print(f"{Fore.RED}\nInvalid choice. Please try again.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()