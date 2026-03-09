# Chapter 13: Project Management System Development

## 🎯 Learning Objectives

By the end of this chapter, you will master:

- **How** to build a complete project management system using Frappe/ERPNext
- **Why** project management architecture requires specific workflow patterns
- **When** to use custom project features vs standard ERPNext capabilities
- **How** task management, resource allocation, and progress tracking work internally
- **Advanced patterns** for building scalable project management solutions
- **Performance optimization** techniques for complex project operations

## 📚 Chapter Topics

### 13.1 Project Management Architecture Overview

**The Project Management System Architecture**

Building a project management system on Frappe requires understanding how to leverage ERPNext's task, resource, and time tracking capabilities while creating a comprehensive project management platform.

#### Core Project Management Components

```python
# Project management system architecture
class ProjectManagementSystem:
    def __init__(self):
        self.project_manager = ProjectManager()
        self.task_manager = TaskManager()
        self.resource_manager = ResourceManager()
        self.time_tracker = TimeTracker()
        self.budget_manager = BudgetManager()
        self.reporting_engine = ProjectReportingEngine()
        self.workflow_engine = ProjectWorkflowEngine()
        self.notification_engine = ProjectNotificationEngine()
    
    def initialize_pm_system(self):
        """Initialize project management system components"""
        # Setup project management
        self.project_manager.setup_project_types()
        
        # Configure task management
        self.task_manager.setup_task_types()
        
        # Setup resource management
        self.resource_manager.setup_resource_types()
        
        # Configure time tracking
        self.time_tracker.setup_time_tracking()
        
        # Setup budget management
        self.budget_manager.setup_budget_types()
        
        # Initialize reporting
        self.reporting_engine.setup_reporting()
        
        return {
            'status': 'initialized',
            'components': list(self.__dict__.keys())
        }

# Project management system
class ProjectManager:
    def __init__(self):
        self.project_validator = ProjectValidator()
        self.project_planner = ProjectPlanner()
        self.project_scheduler = ProjectScheduler()
        self.project_tracker = ProjectTracker()
        self.project_analyzer = ProjectAnalyzer()
    
    def setup_project_types(self):
        """Setup different project types"""
        project_types = [
            {
                'project_type': 'Software Development',
                'description': 'Software development projects',
                'default_template': 'Software Development Template',
                'task_types': ['Development', 'Testing', 'Documentation', 'Deployment'],
                'milestone_types': ['Sprint Complete', 'Release', 'Milestone']
            },
            {
                'project_type': 'Construction',
                'description': 'Construction and infrastructure projects',
                'default_template': 'Construction Template',
                'task_types': ['Planning', 'Design', 'Construction', 'Inspection'],
                'milestone_types': 'Foundation Complete', 'Structure Complete', 'Project Complete'
            },
            {
                'project_type': 'Marketing Campaign',
                'description': 'Marketing and advertising campaigns',
                'default_template': 'Marketing Template',
                'task_types': ['Planning', 'Content Creation', 'Campaign Execution', 'Analysis'],
                'milestone_types': ['Campaign Launch', 'Mid-Campaign Review', 'Campaign Complete']
            },
            {
                'project_type': 'Consulting',
                'description': 'Consulting and professional services projects',
                'default_template': 'Consulting Template',
                'task_types': ['Analysis', 'Research', 'Recommendations', 'Implementation'],
                'milestone_types': 'Analysis Complete', 'Recommendations Delivered', 'Project Complete'
            }
        ]
        
        for project_type_data in project_types:
            if not frappe.db.exists('Project Type', project_type_data['project_type']):
                project_type = frappe.new_doc('Project Type')
                project_type.project_type = project_type_data['project_type']
                project_type.description = project_type_data['description']
                project_type.default_template = project_type_data['default_template']
                project_type.insert()
                
                # Add task types
                for task_type in project_type_data['task_types']:
                    project_type.append('task_types', {
                        'task_type': task_type
                    })
                
                # Add milestone types
                for milestone_type in project_type_data['milestone_types']:
                    project_type.append('milestone_types', {
                        'milestone_type': milestone_type
                    })
                
                project_type.save()
    
    def create_project(self, project_data):
        """Create new project with validation and planning"""
        # Validate project data
        self.project_validator.validate_project_data(project_data)
        
        # Create project document
        project = frappe.new_doc('Project')
        project.project_name = project_data.get('project_name')
        project.customer = project_data.get('customer')
        project.project_type = project_data.get('project_type')
        project.status = 'Open'
        project.priority = project_data.get('priority', 'Medium')
        project.expected_start_date = project_data.get('expected_start_date')
        project.expected_end_date = project_data.get('expected_end_date')
        project.estimated_cost = project_data.get('estimated_cost')
        project.department = project_data.get('department')
        project.project_manager = project_data.get('project_manager', frappe.session.user)
        
        # Set custom fields
        if project_data.get('custom_fields'):
            for field, value in project_data['custom_fields'].items():
                if hasattr(project, field):
                    setattr(project, field, value)
        
        project.insert()
        
        # Create project plan
        if project_data.get('create_plan', True):
            self.project_planner.create_project_plan(project, project_data)
        
        # Assign resources
        if project_data.get('assign_resources', True):
            self.resource_manager.assign_project_resources(project, project_data.get('resources', []))
        
        # Setup notifications
        self.setup_project_notifications(project)
        
        return project
    
    def update_project_status(self, project_name, new_status, notes=None):
        """Update project status with validation"""
        project = frappe.get_doc('Project', project_name)
        
        # Validate status transition
        if not self.validate_status_transition(project.status, new_status):
            raise Exception(f"Invalid status transition from {project.status} to {new_status}")
        
        old_status = project.status
        project.status = new_status
        project.status_change_date = frappe.utils.now()
        
        if notes:
            project.add_comment(f"Status changed from {old_status} to {new_status}: {notes}")
        
        project.save()
        
        # Trigger notifications
        self.trigger_status_notifications(project, old_status, new_status)
        
        return project
    
    def validate_status_transition(self, current_status, new_status):
        """Validate project status transition"""
        # Define allowed transitions
        allowed_transitions = {
            'Open': ['Planned', 'In Progress', 'On Hold', 'Cancelled'],
            'Planned': ['In Progress', 'On Hold', 'Cancelled'],
            'In Progress': ['Completed', 'On Hold', 'Cancelled'],
            'On Hold': ['In Progress', 'Cancelled'],
            'Completed': [],
            'Cancelled': []
        }
        
        return new_status in allowed_transitions.get(current_status, [])
    
    def get_project_dashboard(self, project_name):
        """Get comprehensive project dashboard"""
        project = frappe.get_doc('Project', project_name)
        
        dashboard_data = {
            'project_info': {
                'name': project.project_name,
                'customer': project.customer,
                'status': project.status,
                'priority': project.priority,
                'progress': self.project_tracker.calculate_project_progress(project_name),
                'completion_percentage': self.project_tracker.calculate_completion_percentage(project_name)
            },
            'task_summary': self.get_project_task_summary(project_name),
            'resource_utilization': self.resource_manager.get_resource_utilization(project_name),
            'budget_status': self.budget_manager.get_budget_status(project_name),
            'timeline_status': self.get_timeline_status(project_name),
            'upcoming_milestones': self.get_upcoming_milestones(project_name),
            'recent_activities': self.get_recent_activities(project_name)
        }
        
        return dashboard_data
    
    def get_project_task_summary(self, project_name):
        """Get project task summary"""
        tasks = frappe.get_all('Task',
                               filters={'project': project_name},
                               fields=['status', 'priority', 'exp_end_date'])
        
        summary = {
            'total_tasks': len(tasks),
            'completed_tasks': len([t for t in tasks if t.status == 'Completed']),
            'in_progress_tasks': len([t for t in tasks if t.status == 'In Progress']),
            'overdue_tasks': len([t for t in tasks if t.status != 'Completed' and t.exp_end_date < frappe.utils.nowdate()]),
            'high_priority_tasks': len([t for t in tasks if t.priority == 'Urgent'])
        }
        
        return summary
    
    def get_timeline_status(self, project_name):
        """Get project timeline status"""
        project = frappe.get_doc('Project', project_name)
        
        today = frappe.utils.today()
        
        return {
            'days_elapsed': (today - project.expected_start_date).days if project.expected_start_date else 0,
            'days_remaining': (project.expected_end_date - today).days if project.expected_end_date else 0,
            'is_on_track': self.project_tracker.is_project_on_track(project_name),
            'timeline_variance': self.project_tracker.calculate_timeline_variance(project_name)
        }
    
    def get_upcoming_milestones(self, project_name):
        """Get upcoming project milestones"""
        milestones = frappe.get_all('Milestone',
                                     filters={'project': project_name, 'status': ['!=', 'Completed']},
                                     fields=['name', 'milestone_title', 'expected_date', 'status'],
                                     order_by='expected_date',
                                     limit=5)
        
        return milestones
    
    def get_recent_activities(self, project_name):
        """Get recent project activities"""
        activities = frappe.get_all('Activity Log',
                                     filters={'reference_type': 'Project', 'reference_name': project_name},
                                     fields=['activity_type', 'activity_date', 'owner', 'comment'],
                                     order_by='activity_date desc',
                                     limit=10)
        
        return activities
    
    def setup_project_notifications(self, project):
        """Setup project notifications"""
        # Create notification preferences
        notification_preferences = frappe.new_doc('Notification Preference')
        notification_preferences.reference_doctype = 'Project'
        notification_preferences.reference_name = project.name
        notification_preferences.enabled = 1
        notification_preferences.insert()
        
        # Add default notification recipients
        if project.project_manager:
            notification_preferences.append('recipients', {
                'user': project.project_manager,
                'notification_type': 'All'
            })
        
        notification_preferences.save()

# Task management system
class TaskManager:
    def __init__(self):
        self.task_validator = TaskValidator()
        self.task_scheduler = TaskScheduler()
        self.dependency_manager = TaskDependencyManager()
        self.task_tracker = TaskTracker()
    
    def setup_task_types(self):
        """Setup different task types"""
        task_types = [
            {
                'task_type': 'Development',
                'description': 'Software development tasks',
                'default_duration': 8,  # hours
                'color': '#3498db'
            },
            {
                'task_type': 'Testing',
                'description': 'Testing and quality assurance tasks',
                'default_duration': 4,
                'color': '#e74c3c'
            },
            {
                'task_type': 'Documentation',
                'description': 'Documentation and writing tasks',
                'default_duration': 2,
                'color': '#f39c12'
            },
            {
                'task_type': 'Meeting',
                'description': 'Meetings and discussions',
                'default_duration': 1,
                'color': '#9b59b6'
            },
            {
                'task_type': 'Research',
                'description': 'Research and analysis tasks',
                'default_duration': 6,
                'color': '#2ecc71'
            }
        ]
        
        for task_type_data in task_types:
            if not frappe.db.exists('Task Type', task_type_data['task_type']):
                task_type = frappe.new_doc('Task Type')
                task_type.task_type = task_type_data['task_type']
                task_type.description = task_type_data['description']
                task_type.default_duration = task_type_data['default_duration']
                task_type.color = task_type_data['color']
                task_type.insert()
    
    def create_task(self, task_data):
        """Create new task with validation"""
        # Validate task data
        self.task_validator.validate_task_data(task_data)
        
        # Create task document
        task = frappe.new_doc('Task')
        task.subject = task_data.get('subject')
        task.project = task_data.get('project')
        task.task_type = task_data.get('task_type')
        task.priority = task_data.get('priority', 'Medium')
        task.status = 'Open'
        task.exp_start_date = task_data.get('exp_start_date')
        task.exp_end_date = task_data.get('exp_end_date')
        task.description = task_data.get('description')
        task.assigned_to = task_data.get('assigned_to')
        
        # Set custom fields
        if task_data.get('custom_fields'):
            for field, value in task_data['custom_fields'].items():
                if hasattr(task, field):
                    setattr(task, field, value)
        
        task.insert()
        
        # Setup task dependencies
        if task_data.get('dependencies'):
            self.dependency_manager.setup_task_dependencies(task.name, task_data['dependencies'])
        
        # Schedule task
        if task_data.get('auto_schedule', True):
            self.task_scheduler.schedule_task(task.name)
        
        # Setup notifications
        self.setup_task_notifications(task)
        
        return task
    
    def update_task_status(self, task_name, new_status, notes=None):
        """Update task status with dependency checking"""
        task = frappe.get_doc('Task', task_name)
        
        # Validate status transition
        if not self.validate_task_status_transition(task.status, new_status):
            raise Exception(f"Invalid status transition from {task.status} to {new_status}")
        
        # Check dependencies if completing task
        if new_status == 'Completed':
            if not self.dependency_manager.can_complete_task(task_name):
                raise Exception("Cannot complete task due to incomplete dependencies")
        
        old_status = task.status
        task.status = new_status
        task.status_change_date = frappe.utils.now()
        
        if new_status == 'Completed':
            task.completed_on = frappe.utils.now()
            task.completion_date = frappe.utils.nowdate()
        
        if notes:
            task.add_comment(f"Status changed from {old_status} to {new_status}: {notes}")
        
        task.save()
        
        # Update dependent tasks
        if new_status == 'Completed':
            self.dependency_manager.update_dependent_tasks(task_name)
        
        # Update project progress
        if task.project:
            project_manager = ProjectManager()
            project_tracker = project_manager.project_tracker
            project_tracker.update_project_progress(task.project)
        
        return task
    
    def validate_task_status_transition(self, current_status, new_status):
        """Validate task status transition"""
        # Define allowed transitions
        allowed_transitions = {
            'Open': ['In Progress', 'On Hold', 'Cancelled'],
            'In Progress': ['Completed', 'On Hold', 'Cancelled'],
            'On Hold': ['In Progress', 'Cancelled'],
            'Completed': [],
            'Cancelled': []
        }
        
        return new_status in allowed_transitions.get(current_status, [])
    
    def get_task_details(self, task_name):
        """Get comprehensive task details"""
        task = frappe.get_doc('Task', task_name)
        
        task_details = {
            'task_info': {
                'name': task.name,
                'subject': task.subject,
                'project': task.project,
                'task_type': task.task_type,
                'status': task.status,
                'priority': task.priority,
                'assigned_to': task.assigned_to,
                'created_by': task.owner,
                'creation': task.creation,
                'modified': task.modified
            },
            'schedule': {
                'expected_start_date': task.exp_start_date,
                'expected_end_date': task.exp_end_date,
                'actual_start_date': task.act_start_date,
                'actual_end_date': task.act_end_date,
                'duration': task.expected_time or 0,
                'progress': self.task_tracker.calculate_task_progress(task_name)
            },
            'dependencies': self.dependency_manager.get_task_dependencies(task_name),
            'dependents': self.dependency_manager.get_task_dependents(task_name),
            'time_logs': self.get_task_time_logs(task_name),
            'comments': self.get_task_comments(task_name),
            'attachments': self.get_task_attachments(task_name)
        }
        
        return task_details
    
    def get_task_time_logs(self, task_name):
        """Get time logs for task"""
        time_logs = frappe.get_all('Time Log',
                                  filters={'task': task_name},
                                  fields=['activity_type', 'from_time', 'hours', 'user', 'description'],
                                  order_by='from_time desc')
        
        return time_logs
    
    def get_task_comments(self, task_name):
        """Get comments for task"""
        comments = frappe.get_all('Comment',
                                 filters={'reference_doctype': 'Task', 'reference_name': task_name},
                                 fields=['comment', 'comment_by', 'creation'],
                                 order_by='creation desc')
        
        return comments
    
    def get_task_attachments(self, task_name):
        """Get attachments for task"""
        attachments = frappe.get_all('File',
                                     filters={'attached_to_doctype': 'Task', 'attached_to_name': task_name},
                                     fields=['file_name', 'file_url', 'file_size', 'creation'],
                                     order_by='creation desc')
        
        return attachments
    
    def get_project_tasks(self, project_name, filters=None):
        """Get all tasks for a project"""
        default_filters = {'project': project_name}
        
        if filters:
            default_filters.update(filters)
        
        tasks = frappe.get_all('Task',
                               filters=default_filters,
                               fields=['name', 'subject', 'status', 'priority', 'assigned_to',
                                      'exp_start_date', 'exp_end_date', 'act_start_date', 'act_end_date'],
                               order_by='exp_end_date')
        
        return tasks
    
    def get_my_tasks(self, user=None, filters=None):
        """Get tasks assigned to user"""
        if not user:
            user = frappe.session.user
        
        default_filters = {'assigned_to': user}
        
        if filters:
            default_filters.update(filters)
        
        tasks = frappe.get_all('Task',
                               filters=default_filters,
                               fields=['name', 'subject', 'project', 'status', 'priority',
                                      'exp_start_date', 'exp_end_date'],
                               order_by='exp_end_date')
        
        return tasks
    
    def get_overdue_tasks(self, project_name=None):
        """Get overdue tasks"""
        today = frappe.utils.today()
        
        filters = {
            'status': ['!=', 'Completed'],
            'exp_end_date': ['<', today]
        }
        
        if project_name:
            filters['project'] = project_name
        
        overdue_tasks = frappe.get_all('Task',
                                       filters=filters,
                                       fields=['name', 'subject', 'project', 'assigned_to',
                                              'exp_end_date', 'priority'],
                                       order_by='exp_end_date')
        
        return overdue_tasks
    
    def get_task_workload(self, user=None, date_range=None):
        """Get workload analysis for user"""
        if not user:
            user = frappe.session.user
        
        filters = {'assigned_to': user}
        
        if date_range:
            filters['exp_start_date'] = ['between', date_range]
        
        tasks = frappe.get_all('Task',
                               filters=filters,
                               fields=['name', 'subject', 'project', 'status',
                                      'exp_start_date', 'exp_end_date', 'expected_time'])
        
        workload = {
            'total_tasks': len(tasks),
            'open_tasks': len([t for t in tasks if t.status in ['Open', 'In Progress']]),
            'completed_tasks': len([t for t in tasks if t.status == 'Completed']),
            'total_hours': sum(t.expected_time or 0 for t in tasks),
            'overdue_tasks': len([t for t in tasks if t.status != 'Completed' and t.exp_end_date < frappe.utils.today()]),
            'upcoming_tasks': len([t for t in tasks if t.exp_start_date >= frappe.utils.today() and t.exp_start_date <= frappe.utils.add_to_date(frappe.utils.today(), days=7)])
        }
        
        return workload
    
    def setup_task_notifications(self, task):
        """Setup task notifications"""
        # Create notification preferences
        notification_preferences = frappe.new_doc('Notification Preference')
        notification_preferences.reference_doctype = 'Task'
        notification_preferences.reference_name = task.name
        notification_preferences.enabled = 1
        notification_preferences.insert()
        
        # Add notification recipients
        if task.assigned_to:
            notification_preferences.append('recipients', {
                'user': task.assigned_to,
                'notification_type': 'All'
            })
        
        if task.project:
            # Add project manager
            project_manager = frappe.db.get_value('Project', task.project, 'project_manager')
            if project_manager and project_manager != task.assigned_to:
                notification_preferences.append('recipients', {
                    'user': project_manager,
                    'notification_type': 'Status Changes'
                })
        
        notification_preferences.save()

# Task dependency manager
class TaskDependencyManager:
    def __init__(self):
        self.dependency_graph = {}
        self.dependency_validator = DependencyValidator()
    
    def setup_task_dependencies(self, task_name, dependencies):
        """Setup task dependencies"""
        for dependency in dependencies:
            self.create_task_dependency(task_name, dependency)
        
        # Validate dependency graph
        if not self.dependency_validator.validate_dependencies(task_name):
            raise Exception("Circular dependency detected")
    
    def create_task_dependency(self, task_name, dependency_task):
        """Create task dependency"""
        dependency = frappe.new_doc('Task Dependency')
        dependency.parent = task_name
        dependency.parenttype = 'Task'
        dependency.parentfield = 'depends_on'
        dependency.task = dependency_task
        dependency.insert()
    
    def get_task_dependencies(self, task_name):
        """Get tasks that current task depends on"""
        dependencies = frappe.get_all('Task Dependency',
                                      filters={'parent': task_name},
                                      fields=['task', 'status'])
        
        return dependencies
    
    def get_task_dependents(self, task_name):
        """Get tasks that depend on current task"""
        dependents = frappe.get_all('Task Dependency',
                                    filters={'task': task_name},
                                    fields=['parent', 'status'])
        
        return dependents
    
    def can_complete_task(self, task_name):
        """Check if task can be completed based on dependencies"""
        dependencies = self.get_task_dependencies(task_name)
        
        for dependency in dependencies:
            if dependency.status != 'Completed':
                return False
        
        return True
    
    def update_dependent_tasks(self, task_name):
        """Update dependent tasks when task is completed"""
        dependents = self.get_task_dependents(task_name)
        
        for dependent in dependents:
            # Check if all dependencies are now complete
            if self.can_complete_task(dependent.parent):
                # Update dependent task status
                task_manager = TaskManager()
                task_manager.update_task_status(dependent.parent, 'Ready', f"Dependencies completed: {task_name}")
    
    def get_critical_path(self, project_name):
        """Calculate critical path for project"""
        # Get all tasks for project
        tasks = frappe.get_all('Task',
                               filters={'project': project_name},
                               fields=['name', 'exp_start_date', 'exp_end_date', 'expected_time'])
        
        # Build dependency graph
        dependency_graph = self.build_dependency_graph(tasks)
        
        # Calculate critical path
        critical_path = self.calculate_critical_path(dependency_graph)
        
        return critical_path
    
    def build_dependency_graph(self, tasks):
        """Build dependency graph from tasks"""
        graph = {}
        
        for task in tasks:
            graph[task.name] = {
                'duration': task.expected_time or 0,
                'dependencies': [],
                'dependents': []
            }
            
            # Get dependencies
            dependencies = frappe.get_all('Task Dependency',
                                          filters={'parent': task.name},
                                          fields=['task'])
            
            graph[task.name]['dependencies'] = [dep.task for dep in dependencies]
            
            # Get dependents
            dependents = frappe.get_all('Task Dependency',
                                        filters={'task': task.name},
                                        fields=['parent'])
            
            graph[task.name]['dependents'] = [dep.parent for dep in dependents]
        
        return graph
    
    def calculate_critical_path(self, dependency_graph):
        """Calculate critical path using longest path algorithm"""
        # This is a simplified implementation
        # In practice, you would use more sophisticated algorithms
        
        critical_path = []
        max_duration = 0
        
        # Find tasks with no dependencies (start tasks)
        start_tasks = [task for task, data in dependency_graph.items() if not data['dependencies']]
        
        for start_task in start_tasks:
            path_duration = self.calculate_path_duration(start_task, dependency_graph, [])
            
            if path_duration > max_duration:
                max_duration = path_duration
                critical_path = self.get_path_tasks(start_task, dependency_graph, [])
        
        return {
            'critical_path': critical_path,
            'total_duration': max_duration
        }
    
    def calculate_path_duration(self, task_name, graph, visited):
        """Calculate duration of path from task"""
        if task_name in visited:
            return 0  # Avoid circular dependencies
        
        visited.append(task_name)
        
        task_data = graph[task_name]
        max_dependent_duration = 0
        
        for dependent in task_data['dependents']:
            dependent_duration = self.calculate_path_duration(dependent, graph, visited)
            max_dependent_duration = max(max_dependent_duration, dependent_duration)
        
        visited.remove(task_name)
        
        return task_data['duration'] + max_dependent_duration
    
    def get_path_tasks(self, task_name, graph, visited):
        """Get all tasks in path"""
        if task_name in visited:
            return []
        
        visited.append(task_name)
        
        task_data = graph[task_name]
        path_tasks = [task_name]
        
        for dependent in task_data['dependents']:
            dependent_tasks = self.get_path_tasks(dependent, graph, visited)
            path_tasks.extend(dependent_tasks)
        
        return path_tasks

# Resource management system
class ResourceManager:
    def __init__(self):
        self.resource_allocator = ResourceAllocator()
        self.resource_tracker = ResourceTracker()
        self.capacity_planner = CapacityPlanner()
        self.skill_matcher = SkillMatcher()
    
    def setup_resource_types(self):
        """Setup different resource types"""
        resource_types = [
            {
                'resource_type': 'Human Resource',
                'description': 'Human resources and personnel',
                'capacity_unit': 'Hours',
                'skills_required': True
            },
            {
                'resource_type': 'Equipment',
                'description': 'Equipment and machinery',
                'capacity_unit': 'Units',
                'skills_required': False
            },
            {
                'resource_type': 'Facility',
                'description': 'Facilities and venues',
                'capacity_unit': 'Days',
                'skills_required': False
            },
            {
                'resource_type': 'Software',
                'description': 'Software and tools',
                'capacity_unit': 'Licenses',
                'skills_required': True
            }
        ]
        
        for resource_type_data in resource_types:
            if not frappe.db.exists('Resource Type', resource_type_data['resource_type']):
                resource_type = frappe.new_doc('Resource Type')
                resource_type.resource_type = resource_type_data['resource_type']
                resource_type.description = resource_type_data['description']
                resource_type.capacity_unit = resource_type_data['capacity_unit']
                resource_type.skills_required = resource_type_data['skills_required']
                resource_type.insert()
    
    def assign_project_resources(self, project, resources):
        """Assign resources to project"""
        for resource_data in resources:
            self.create_project_resource(project, resource_data)
    
    def create_project_resource(self, project, resource_data):
        """Create project resource assignment"""
        project_resource = frappe.new_doc('Project Resource')
        project_resource.parent = project.name
        project_resource.parenttype = 'Project'
        project_resource.parentfield = 'resources'
        project_resource.resource = resource_data.get('resource')
        project_resource.resource_type = resource_data.get('resource_type')
        project_resource.role = resource_data.get('role')
        project_resource.allocation_percentage = resource_data.get('allocation_percentage', 100)
        project_resource.from_date = resource_data.get('from_date', project.expected_start_date)
        project_resource.to_date = resource_data.get('to_date', project.expected_end_date)
        project_resource.insert()
    
    def get_resource_utilization(self, project_name):
        """Get resource utilization for project"""
        resources = frappe.get_all('Project Resource',
                                   filters={'parent': project_name},
                                   fields=['resource', 'resource_type', 'allocation_percentage',
                                          'from_date', 'to_date'])
        
        utilization_data = {}
        
        for resource in resources:
            # Get resource details
            resource_doc = frappe.get_doc('Resource', resource.resource)
            
            # Calculate utilization
            utilization = self.resource_tracker.calculate_resource_utilization(
                resource.resource, 
                resource.from_date, 
                resource.to_date
            )
            
            utilization_data[resource.resource] = {
                'resource_name': resource_doc.resource_name,
                'resource_type': resource.resource_type,
                'role': resource.role,
                'allocation_percentage': resource.allocation_percentage,
                'actual_utilization': utilization,
                'efficiency': utilization / resource.allocation_percentage if resource.allocation_percentage > 0 else 0
            }
        
        return utilization_data
    
    def get_resource_availability(self, resource_type, date_range=None):
        """Get resource availability for type and date range"""
        filters = {'resource_type': resource_type}
        
        if date_range:
            filters['availability_date'] = ['between', date_range]
        
        resources = frappe.get_all('Resource',
                                   filters=filters,
                                   fields=['name', 'resource_name', 'capacity', 'availability_date'])
        
        availability_data = {}
        
        for resource in resources:
            # Calculate availability
            availability = self.capacity_planner.calculate_availability(
                resource.name,
                date_range
            )
            
            availability_data[resource.name] = {
                'resource_name': resource.resource_name,
                'capacity': resource.capacity,
                'availability': availability,
                'utilization_rate': (resource.capacity - availability) / resource.capacity if resource.capacity > 0 else 0
            }
        
        return availability_data
    
    def find_best_resources(self, task_requirements, project_name=None):
        """Find best resources for task based on requirements"""
        required_skills = task_requirements.get('skills', [])
        resource_type = task_requirements.get('resource_type')
        date_range = task_requirements.get('date_range')
        
        # Get available resources
        available_resources = self.get_resource_availability(resource_type, date_range)
        
        # Match skills
        matched_resources = []
        
        for resource_id, resource_data in available_resources.items():
            if resource_data['availability'] > 0:
                # Check skill match
                skill_match = self.skill_matcher.calculate_skill_match(resource_id, required_skills)
                
                matched_resources.append({
                    'resource_id': resource_id,
                    'resource_name': resource_data['resource_name'],
                    'availability': resource_data['availability'],
                    'skill_match': skill_match,
                    'overall_score': skill_match * (1 - resource_data['utilization_rate'])
                })
        
        # Sort by overall score
        matched_resources.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return matched_resources[:5]  # Return top 5 matches
    
    def optimize_resource_allocation(self, project_name):
        """Optimize resource allocation for project"""
        project = frappe.get_doc('Project', project_name)
        
        # Get all tasks for project
        tasks = frappe.get_all('Task',
                               filters={'project': project_name},
                               fields=['name', 'subject', 'task_type', 'assigned_to', 'exp_start_date', 'exp_end_date'])
        
        # Get current resource assignments
        current_assignments = self.get_resource_utilization(project_name)
        
        # Optimization algorithm
        optimized_assignments = self.resource_allocator.optimize_allocation(tasks, current_assignments)
        
        return optimized_assignments
    
    def get_resource_workload(self, user=None, date_range=None):
        """Get workload for resource"""
        if not user:
            user = frappe.session.user
        
        filters = {'user': user}
        
        if date_range:
            filters['date'] = ['between', date_range]
        
        time_logs = frappe.get_all('Time Log',
                                  filters=filters,
                                  fields=['project', 'task', 'hours', 'date'])
        
        workload_data = {
            'total_hours': sum(log.hours for log in time_logs),
            'project_breakdown': {},
            'daily_breakdown': {}
        }
        
        # Break down by project
        for log in time_logs:
            if log.project not in workload_data['project_breakdown']:
                workload_data['project_breakdown'][log.project] = 0
            workload_data['project_breakdown'][log.project] += log.hours
        
        # Break down by day
        for log in time_logs:
            if log.date not in workload_data['daily_breakdown']:
                workload_data['daily_breakdown'][log.date] = 0
            workload_data['daily_breakdown'][log.date] += log.hours
        
        return workload_data

# Time tracking system
class TimeTracker:
    def __init__(self):
        self.time_validator = TimeValidator()
        self.time_analyzer = TimeAnalyzer()
        self.billing_calculator = BillingCalculator()
    
    def setup_time_tracking(self):
        """Setup time tracking configuration"""
        # Create time tracking settings
        if not frappe.db.exists('Time Tracking Settings', 'Time Tracking Settings'):
            settings = frappe.new_doc('Time Tracking Settings')
            settings.name = 'Time Tracking Settings'
            settings.enable_time_tracking = 1
            settings.require_task_for_timesheet = 1
            settings.default_billable_hours = 8
            settings.minimum_log_time = 0.25  # 15 minutes
            settings.maximum_log_time = 24  # 24 hours
            settings.insert()
    
    def log_time(self, time_log_data):
        """Log time for task or project"""
        # Validate time log data
        self.time_validator.validate_time_log(time_log_data)
        
        # Create time log document
        time_log = frappe.new_doc('Time Log')
        time_log.activity_type = time_log_data.get('activity_type', 'Task')
        time_log.from_time = time_log_data.get('from_time')
        time_log.to_time = time_log_data.get('to_time')
        time_log.hours = time_log_data.get('hours')
        time_log.project = time_log_data.get('project')
        time_log.task = time_log_data.get('task')
        time_log.user = time_log_data.get('user', frappe.session.user)
        time_log.description = time_log_data.get('description')
        time_log.billable = time_log_data.get('billable', 1)
        
        # Calculate hours if not provided
        if not time_log.hours and time_log.from_time and time_log.to_time:
            time_log.hours = self.calculate_hours(time_log.from_time, time_log.to_time)
        
        time_log.insert()
        
        # Update task progress
        if time_log.task:
            self.update_task_progress(time_log.task)
        
        # Update project progress
        if time_log.project:
            self.update_project_progress(time_log.project)
        
        return time_log
    
    def calculate_hours(self, from_time, to_time):
        """Calculate hours between two times"""
        from_datetime = frappe.utils.get_datetime(from_time)
        to_datetime = frappe.utils.get_datetime(to_time)
        
        time_diff = to_datetime - from_datetime
        hours = time_diff.total_seconds() / 3600
        
        return round(hours, 2)
    
    def update_task_progress(self, task_name):
        """Update task progress based on time logs"""
        # Get task details
        task = frappe.get_doc('Task', task_name)
        
        # Get total time logged
        total_hours = frappe.db.get_value('Time Log', {'task': task_name}, 'SUM(hours)') or 0
        
        # Get expected hours
        expected_hours = task.expected_time or 8
        
        # Calculate progress
        progress = min((total_hours / expected_hours) * 100, 100)
        
        # Update task progress
        frappe.db.set_value('Task', task_name, 'progress', progress)
    
    def update_project_progress(self, project_name):
        """Update project progress based on time logs"""
        # Get all tasks for project
        tasks = frappe.get_all('Task',
                               filters={'project': project_name},
                               fields=['name', 'expected_time'])
        
        if not tasks:
            return
        
        total_expected = sum(task.expected_time or 0 for task in tasks)
        total_logged = 0
        
        for task in tasks:
            logged_hours = frappe.db.get_value('Time Log', {'task': task.name}, 'SUM(hours)') or 0
            total_logged += logged_hours
        
        # Calculate progress
        progress = min((total_logged / total_expected) * 100, 100) if total_expected > 0 else 0
        
        # Update project progress
        frappe.db.set_value('Project', project_name, 'progress', progress)
    
    def get_time_logs(self, filters=None):
        """Get time logs with filters"""
        default_filters = {}
        
        if filters:
            default_filters.update(filters)
        
        time_logs = frappe.get_all('Time Log',
                                  filters=default_filters,
                                  fields=['name', 'activity_type', 'from_time', 'to_time', 'hours',
                                         'project', 'task', 'user', 'billable', 'description'],
                                  order_by='from_time desc')
        
        return time_logs
    
    def get_user_timesheet(self, user=None, date_range=None):
        """Get timesheet for user"""
        if not user:
            user = frappe.session.user
        
        filters = {'user': user}
        
        if date_range:
            filters['from_time'] = ['between', date_range]
        
        time_logs = self.get_time_logs(filters)
        
        # Calculate totals
        total_hours = sum(log.hours for log in time_logs)
        billable_hours = sum(log.hours for log in time_logs if log.billable)
        non_billable_hours = total_hours - billable_hours
        
        timesheet_data = {
            'time_logs': time_logs,
            'summary': {
                'total_hours': total_hours,
                'billable_hours': billable_hours,
                'non_billable_hours': non_billable_hours,
                'billable_percentage': (billable_hours / total_hours * 100) if total_hours > 0 else 0
            },
            'project_breakdown': self.get_project_breakdown(time_logs),
            'activity_breakdown': self.get_activity_breakdown(time_logs)
        }
        
        return timesheet_data
    
    def get_project_timesheet(self, project_name, date_range=None):
        """Get timesheet for project"""
        filters = {'project': project_name}
        
        if date_range:
            filters['from_time'] = ['between', date_range]
        
        time_logs = self.get_time_logs(filters)
        
        # Calculate totals
        total_hours = sum(log.hours for log in time_logs)
        billable_hours = sum(log.hours for log in time_logs if log.billable)
        
        timesheet_data = {
            'time_logs': time_logs,
            'summary': {
                'total_hours': total_hours,
                'billable_hours': billable_hours,
                'non_billable_hours': total_hours - billable_hours,
                'user_breakdown': self.get_user_breakdown(time_logs)
            }
        }
        
        return timesheet_data
    
    def get_project_breakdown(self, time_logs):
        """Get project breakdown from time logs"""
        breakdown = {}
        
        for log in time_logs:
            if log.project:
                if log.project not in breakdown:
                    breakdown[log.project] = 0
                breakdown[log.project] += log.hours
        
        return breakdown
    
    def get_activity_breakdown(self, time_logs):
        """Get activity breakdown from time logs"""
        breakdown = {}
        
        for log in time_logs:
            if log.activity_type not in breakdown:
                breakdown[log.activity_type] = 0
            breakdown[log.activity_type] += log.hours
        
        return breakdown
    
    def get_user_breakdown(self, time_logs):
        """Get user breakdown from time logs"""
        breakdown = {}
        
        for log in time_logs:
            if log.user not in breakdown:
                breakdown[log.user] = 0
            breakdown[log.user] += log.hours
        
        return breakdown
    
    def generate_timesheet_report(self, user=None, date_range=None):
        """Generate comprehensive timesheet report"""
        if not user:
            user = frappe.session.user
        
        # Get timesheet data
        timesheet_data = self.get_user_timesheet(user, date_range)
        
        # Generate analysis
        analysis = self.time_analyzer.analyze_timesheet(timesheet_data)
        
        # Calculate billing
        billing = self.billing_calculator.calculate_billing(timesheet_data)
        
        report_data = {
            'user': user,
            'date_range': date_range,
            'timesheet_data': timesheet_data,
            'analysis': analysis,
            'billing': billing
        }
        
        return report_data

# Budget management system
class BudgetManager:
    def __init__(self):
        self.budget_tracker = BudgetTracker()
        self.cost_analyzer = CostAnalyzer()
        self.forecasting_engine = BudgetForecastingEngine()
    
    def setup_budget_types(self):
        """Setup different budget types"""
        budget_types = [
            {
                'budget_type': 'Project Budget',
                'description': 'Project-specific budget',
                'default_period': 'Project Duration'
            },
            {
                'budget_type': 'Department Budget',
                'description': 'Department-level budget',
                'default_period': 'Yearly'
            },
            {
                'budget_type': 'Resource Budget',
                'description': 'Resource-specific budget',
                'default_period': 'Monthly'
            }
        ]
        
        for budget_type_data in budget_types:
            if not frappe.db.exists('Budget Type', budget_type_data['budget_type']):
                budget_type = frappe.new_doc('Budget Type')
                budget_type.budget_type = budget_type_data['budget_type']
                budget_type.description = budget_type_data['description']
                budget_type.default_period = budget_type_data['default_period']
                budget_type.insert()
    
    def create_project_budget(self, project_name, budget_data):
        """Create project budget"""
        # Create budget document
        budget = frappe.new_doc('Budget')
        budget.budget_name = f"{project_name} Budget"
        budget.project = project_name
        budget.budget_type = 'Project Budget'
        budget.total_budget = budget_data.get('total_budget')
        budget.budget_start_date = budget_data.get('budget_start_date')
        budget.budget_end_date = budget_data.get('budget_end_date')
        budget.currency = budget_data.get('currency', 'USD')
        
        budget.insert()
        
        # Create budget items
        if budget_data.get('budget_items'):
            for item_data in budget_data['budget_items']:
                budget.append('budget_items', {
                    'item_name': item_data.get('item_name'),
                    'item_group': item_data.get('item_group'),
                    'planned_amount': item_data.get('planned_amount'),
                    'actual_amount': 0,
                    'variance': 0
                })
        
        budget.save()
        
        return budget
    
    def get_budget_status(self, project_name):
        """Get budget status for project"""
        # Get budget
        budget = frappe.get_doc('Budget', {'project': project_name})
        
        # Calculate actual costs
        actual_costs = self.budget_tracker.calculate_actual_costs(project_name)
        
        # Calculate variance
        budget_status = {
            'total_budget': budget.total_budget,
            'actual_costs': actual_costs['total_actual'],
            'remaining_budget': budget.total_budget - actual_costs['total_actual'],
            'budget_utilization': (actual_costs['total_actual'] / budget.total_budget * 100) if budget.total_budget > 0 else 0,
            'items': []
        }
        
        # Calculate item-level variance
        for item in budget.budget_items:
            item_actual = actual_costs['item_costs'].get(item.item_name, 0)
            item_variance = item_actual - item.planned_amount
            
            budget_status['items'].append({
                'item_name': item.item_name,
                'planned_amount': item.planned_amount,
                'actual_amount': item_actual,
                'variance': item_variance,
                'variance_percentage': (item_variance / item.planned_amount * 100) if item.planned_amount > 0 else 0
            })
        
        return budget_status
    
    def track_project_costs(self, project_name):
        """Track actual project costs"""
        # Get time logs for project
        time_logs = frappe.get_all('Time Log',
                                  filters={'project': project_name},
                                  fields=['hours', 'user', 'billable'])
        
        # Get expenses for project
        expenses = frappe.get_all('Expense',
                                 filters={'project': project_name, 'status': 'Submitted'},
                                 fields=['amount', 'expense_type'])
        
        # Calculate costs
        labor_cost = self.calculate_labor_cost(time_logs)
        expense_cost = sum(exp.amount for exp in expenses)
        total_cost = labor_cost + expense_cost
        
        return {
            'labor_cost': labor_cost,
            'expense_cost': expense_cost,
            'total_cost': total_cost,
            'time_logs': time_logs,
            'expenses': expenses
        }
    
    def calculate_labor_cost(self, time_logs):
        """Calculate labor cost from time logs"""
        total_cost = 0
        
        for log in time_logs:
            # Get hourly rate for user
            hourly_rate = frappe.db.get_value('Employee', {'user_id': log.user}, 'hourly_rate') or 50
            cost = log.hours * hourly_rate
            total_cost += cost
        
        return total_cost
    
    def generate_budget_report(self, project_name):
        """Generate comprehensive budget report"""
        # Get budget status
        budget_status = self.get_budget_status(project_name)
        
        # Get cost analysis
        cost_analysis = self.cost_analyzer.analyze_costs(project_name)
        
        # Generate forecast
        forecast = self.forecasting_engine.forecast_budget(project_name)
        
        report_data = {
            'project': project_name,
            'budget_status': budget_status,
            'cost_analysis': cost_analysis,
            'forecast': forecast,
            'recommendations': self.generate_budget_recommendations(budget_status, cost_analysis)
        }
        
        return report_data
    
    def generate_budget_recommendations(self, budget_status, cost_analysis):
        """Generate budget recommendations"""
        recommendations = []
        
        # Check budget utilization
        if budget_status['budget_utilization'] > 90:
            recommendations.append({
                'type': 'warning',
                'message': 'Budget utilization is high. Monitor remaining budget carefully.',
                'priority': 'High'
            })
        elif budget_status['budget_utilization'] < 50:
            recommendations.append({
                'type': 'info',
                'message': 'Budget utilization is low. Consider reallocating resources.',
                'priority': 'Medium'
            })
        
        # Check cost overruns
        for item in budget_status['items']:
            if item['variance_percentage'] > 20:
                recommendations.append({
                    'type': 'warning',
                    'message': f"Cost variance for {item['item_name']} is {item['variance_percentage']:.1f}%",
                    'priority': 'High'
                })
        
        # Check spending trends
        if cost_analysis['spending_trend'] == 'increasing':
            recommendations.append({
                'type': 'warning',
                'message': 'Spending trend is increasing. Review cost controls.',
                'priority': 'Medium'
            })
        
        return recommendations
```

### 13.2 Building the Project Management Frontend

#### PM Dashboard and User Interface

```javascript
// Project management frontend application
class ProjectManagementFrontend {
    constructor() {
        this.dashboard = new ProjectDashboard();
        this.project_manager = new ProjectManagerUI();
        this.task_manager = new TaskManagerUI();
        this.resource_manager = new ResourceManagerUI();
        this.time_tracker = new TimeTrackerUI();
        this.analytics = new ProjectAnalyticsUI();
        this.reports = new ProjectReportsUI();
        
        this.initialize_app();
    }
    
    initialize_app() {
        // Setup routing
        this.setup_routing();
        
        // Initialize components
        this.initialize_components();
        
        // Setup event listeners
        this.setup_event_listeners();
        
        // Load user data
        this.load_user_data();
    }
    
    setup_routing() {
        this.routes = {
            '/': 'dashboard',
            '/projects': 'projects',
            '/project/:id': 'project_detail',
            '/tasks': 'tasks',
            '/task/:id': 'task_detail',
            '/resources': 'resources',
            '/time-tracking': 'time_tracking',
            '/reports': 'reports',
            '/analytics': 'analytics'
        };
        
        this.router = new Router(this.routes);
        this.router.init();
    }
    
    initialize_components() {
        this.components = {
            sidebar: new PMSidebar(),
            header: new PMHeader(),
            dashboard: new ProjectDashboard(),
            project_list: new ProjectList(),
            project_detail: new ProjectDetail(),
            task_list: new TaskList(),
            task_detail: new TaskDetail(),
            resource_calendar: new ResourceCalendar(),
            time_tracker: new TimeTracker(),
            analytics: new ProjectAnalytics()
        };
        
        this.mount_components();
    }
    
    mount_components() {
        // Mount sidebar
        this.components.sidebar.mount('#sidebar');
        
        // Mount header
        this.components.header.mount('#header');
        
        // Setup main content area
        this.router.on('route:changed', (route) => {
            this.render_page(route);
        });
    }
    
    render_page(route) {
        const content_area = document.getElementById('main-content');
        
        switch(route.name) {
            case 'dashboard':
                this.render_dashboard_page(content_area);
                break;
            case 'projects':
                this.render_projects_page(content_area);
                break;
            case 'project_detail':
                this.render_project_detail_page(content_area, route.params);
                break;
            case 'tasks':
                this.render_tasks_page(content_area);
                break;
            case 'task_detail':
                this.render_task_detail_page(content_area, route.params);
                break;
            case 'resources':
                this.render_resources_page(content_area);
                break;
            case 'time-tracking':
                this.render_time_tracking_page(content_area);
                break;
            case 'reports':
                this.render_reports_page(content_area);
                break;
            case 'analytics':
                this.render_analytics_page(content_area);
                break;
            default:
                this.render_404_page(content_area);
        }
    }
    
    render_dashboard_page(container) {
        container.innerHTML = `
            <div class="pm-dashboard">
                <div class="dashboard-header">
                    <h1>Project Management Dashboard</h1>
                    <div class="date-filter">
                        <select id="date-range" onchange="pm.analytics.update_dashboard(this.value)">
                            <option value="7">Last 7 Days</option>
                            <option value="30" selected>Last 30 Days</option>
                            <option value="90">Last 90 Days</option>
                            <option value="365">Last Year</option>
                        </select>
                    </div>
                </div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-project-diagram"></i>
                        </div>
                        <div class="metric-content">
                            <h3 id="total-projects">0</h3>
                            <p>Total Projects</p>
                            <span class="metric-change positive">+3</span>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-tasks"></i>
                        </div>
                        <div class="metric-content">
                            <h3 id="active-tasks">0</h3>
                            <p>Active Tasks</p>
                            <span class="metric-change positive">+12</span>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-users"></i>
                        </div>
                        <div class="metric-content">
                            <h3 id="team-members">0</h3>
                            <p>Team Members</p>
                            <span class="metric-change positive">+2</span>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-clock"></i>
                        </div>
                        <div class="metric-content">
                            <h3 id="hours-logged">0</h3>
                            <p>Hours Logged</p>
                            <span class="metric-change negative">-5</span>
                        </div>
                    </div>
                </div>
                
                <div class="dashboard-charts">
                    <div class="chart-container">
                        <h3>Project Status Overview</h3>
                        <div id="project-status-chart"></div>
                    </div>
                    
                    <div class="chart-container">
                        <h3>Task Completion Trend</h3>
                        <div id="task-completion-chart"></div>
                    </div>
                </div>
                
                <div class="dashboard-tables">
                    <div class="table-container">
                        <h3>Active Projects</h3>
                        <div id="active-projects-table"></div>
                    </div>
                    
                    <div class="table-container">
                        <h3>My Tasks</h3>
                        <div id="my-tasks-table"></div>
                    </div>
                </div>
            </div>
        `;
        
        // Load dashboard data
        this.load_dashboard_data();
    }
    
    async load_dashboard_data() {
        try {
            const response = await fetch('/api/method/pm.api.get_dashboard_data');
            const data = await response.json();
            
            if (data.message) {
                this.update_dashboard_metrics(data.message);
                this.render_dashboard_charts(data.message);
                this.render_dashboard_tables(data.message);
            }
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }
    
    update_dashboard_metrics(data) {
        document.getElementById('total-projects').textContent = data.project_metrics.total_projects;
        document.getElementById('active-tasks').textContent = data.task_metrics.active_tasks;
        document.getElementById('team-members').textContent = data.resource_metrics.total_resources;
        document.getElementById('hours-logged').textContent = data.time_metrics.total_hours;
    }
    
    render_dashboard_charts(data) {
        // Render project status chart
        this.render_project_status_chart(data.project_metrics.status_breakdown);
        
        // Render task completion trend
        this.render_task_completion_chart(data.task_metrics.completion_trend);
    }
    
    render_project_status_chart(status_data) {
        const container = document.getElementById('project-status-chart');
        
        const chart_data = {
            labels: Object.keys(status_data),
            datasets: [{
                data: Object.values(status_data),
                backgroundColor: [
                    '#2ecc71',  // Open
                    '#3498db',  # In Progress
                    '#f39c12',  # On Hold
                    '#e74c3c',  # Completed
                    '#95a5a6'   // Cancelled
                ]
            }]
        };
        
        container.innerHTML = `
            <div class="status-chart">
                ${chart_data.labels.map((label, index) => `
                    <div class="status-item">
                        <div class="status-bar" style="background-color: ${chart_data.datasets[0].backgroundColor[index]}">
                            <span class="status-label">${label}</span>
                            <span class="status-count">${chart_data.datasets[0].data[index]}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    render_task_completion_chart(trend_data) {
        const container = document.getElementById('task-completion-chart');
        
        container.innerHTML = `
            <div class="trend-chart">
                <div class="trend-line">
                    ${trend_data.map((data, index) => `
                        <div class="trend-point" style="left: ${(index / (trend_data.length - 1)) * 100}%">
                            <div class="trend-value">${data.completed}</div>
                            <div class="trend-date">${data.date}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    render_dashboard_tables(data) {
        // Render active projects table
        this.render_active_projects_table(data.active_projects);
        
        // Render my tasks table
        this.render_my_tasks_table(data.my_tasks);
    }
    
    render_active_projects_table(projects) {
        const container = document.getElementById('active-projects-table');
        
        if (projects && projects.length > 0) {
            container.innerHTML = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Project</th>
                            <th>Status</th>
                            <th>Progress</th>
                            <th>Due Date</th>
                            <th>Manager</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${projects.map(project => `
                            <tr onclick="pm.project_manager.view_project('${project.name}')">
                                <td>${project.project_name}</td>
                                <td><span class="status-badge ${project.status.toLowerCase()}">${project.status}</span></td>
                                <td>
                                    <div class="progress-bar">
                                        <div class="progress-fill" style="width: ${project.progress}%"></div>
                                        <span class="progress-text">${project.progress}%</span>
                                    </div>
                                </td>
                                <td>${this.format_date(project.expected_end_date)}</td>
                                <td>${project.project_manager}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = '<p>No active projects found</p>';
        }
    }
    
    render_my_tasks_table(tasks) {
        const container = document.getElementById('my-tasks-table');
        
        if (tasks && tasks.length > 0) {
            container.innerHTML = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Task</th>
                            <th>Project</th>
                            <th>Status</th>
                            <th>Priority</th>
                            <th>Due Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tasks.map(task => `
                            <tr onclick="pm.task_manager.view_task('${task.name}')">
                                <td>${task.subject}</td>
                                <td>${task.project}</td>
                                <td><span class="status-badge ${task.status.toLowerCase()}">${task.status}</span></td>
                                <td><span class="priority-badge ${task.priority.toLowerCase()}">${task.priority}</span></td>
                                <td>${this.format_date(task.exp_end_date)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = '<p>No tasks assigned</p>';
        }
    }
    
    render_projects_page(container) {
        container.innerHTML = `
            <div class="projects-page">
                <div class="page-header">
                    <h1>Projects</h1>
                    <div class="page-actions">
                        <button class="btn btn-primary" onclick="pm.project_manager.create_project()">
                            <i class="fas fa-plus"></i> New Project
                        </button>
                        <button class="btn btn-secondary" onclick="pm.project_manager.import_projects()">
                            <i class="fas fa-upload"></i> Import Projects
                        </button>
                    </div>
                </div>
                
                <div class="filters-bar">
                    <div class="filter-group">
                        <select id="status-filter" onchange="pm.project_manager.filter_projects()">
                            <option value="">All Status</option>
                            <option value="Open">Open</option>
                            <option value="Planned">Planned</option>
                            <option value="In Progress">In Progress</option>
                            <option value="On Hold">On Hold</option>
                            <option value="Completed">Completed</option>
                            <option value="Cancelled">Cancelled</option>
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <select id="type-filter" onchange="pm.project_manager.filter_projects()">
                            <option value="">All Types</option>
                            <option value="Software Development">Software Development</option>
                            <option value="Construction">Construction</option>
                            <option value="Marketing Campaign">Marketing Campaign</option>
                            <option value="Consulting">Consulting</option>
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <select id="priority-filter" onchange="pm.project_manager.filter_projects()">
                            <option value="">All Priorities</option>
                            <option value="Low">Low</option>
                            <option value="Medium">Medium</option>
                            <option value="High">High</option>
                            <option value="Urgent">Urgent</option>
                        </select>
                    </div>
                    
                    <div class="filter-group search-group">
                        <input type="text" placeholder="Search projects..." 
                               onkeyup="pm.project_manager.search_projects(this.value)">
                        <button onclick="pm.project_manager.search_projects(document.getElementById('search-input').value)">
                            <i class="fas fa-search"></i>
                        </button>
                    </div>
                </div>
                
                <div class="projects-list" id="projects-list">
                    <!-- Projects will be loaded here -->
                </div>
                
                <div class="pagination" id="projects-pagination">
                    <!-- Pagination will be loaded here -->
                </div>
            </div>
        `;
        
        // Load projects
        this.load_projects();
    }
    
    async load_projects(filters = {}) {
        try {
            const params = new URLSearchParams(filters);
            const response = await fetch(`/api/method/pm.api.get_projects?${params}`);
            const data = await response.json();
            
            if (data.message) {
                this.render_projects_list(data.message.projects);
                this.setup_pagination(data.message.total_count, data.message.page, data.message.per_page);
            }
            
        } catch (error) {
            console.error('Error loading projects:', error);
        }
    }
    
    render_projects_list(projects) {
        const container = document.getElementById('projects-list');
        
        if (projects && projects.length > 0) {
            container.innerHTML = `
                <div class="projects-grid">
                    ${projects.map(project => `
                        <div class="project-card" onclick="pm.project_manager.view_project('${project.name}')">
                            <div class="project-header">
                                <h3>${project.project_name}</h3>
                                <span class="status-badge ${project.status.toLowerCase()}">${project.status}</span>
                            </div>
                            
                            <div class="project-info">
                                <p><strong>Customer:</strong> ${project.customer || '-'}</p>
                                <p><strong>Type:</strong> ${project.project_type}</p>
                                <p><strong>Manager:</strong> ${project.project_manager}</p>
                                <p><strong>Due Date:</strong> ${this.format_date(project.expected_end_date)}</p>
                            </div>
                            
                            <div class="project-progress">
                                <div class="progress-info">
                                    <span class="progress-label">Progress</span>
                                    <span class="progress-percentage">${project.progress}%</span>
                                </div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${project.progress}%"></div>
                                </div>
                            </div>
                            
                            <div class="project-metrics">
                                <div class="metric">
                                    <span class="metric-label">Tasks</span>
                                    <span class="metric-value">${project.total_tasks}</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Budget</span>
                                    <span class="metric-value">${this.format_currency(project.estimated_cost)}</span>
                                </div>
                            </div>
                            
                            <div class="project-actions">
                                <button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); pm.project_manager.edit_project('${project.name}')">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-secondary" onclick="event.stopPropagation(); pm.project_manager.view_tasks('${project.name}')">
                                    <i class="fas fa-tasks"></i>
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            container.innerHTML = '<div class="empty-state"><p>No projects found</p></div>';
        }
    }
    
    render_project_detail_page(container, params) {
        const project_id = params.id;
        
        container.innerHTML = `
            <div class="project-detail-page">
                <div class="detail-header">
                    <div class="header-left">
                        <button class="btn btn-secondary" onclick="pm.router.navigate('/projects')">
                            <i class="fas fa-arrow-left"></i> Back to Projects
                        </button>
                    </div>
                    <div class="header-right">
                        <button class="btn btn-primary" onclick="pm.project_manager.edit_project('${project_id}')">
                            <i class="fas fa-edit"></i> Edit Project
                        </button>
                        <button class="btn btn-secondary" onclick="pm.project_manager.create_task('${project_id}')">
                            <i class="fas fa-plus"></i> Add Task
                        </button>
                    </div>
                </div>
                
                <div class="project-content">
                    <div class="project-main-info">
                        <div class="project-basic-info">
                            <h1 id="project-name"></h1>
                            <div class="project-meta">
                                <span class="status-badge" id="project-status"></span>
                                <span class="priority-badge" id="project-priority"></span>
                                <span class="project-type" id="project-type"></span>
                            </div>
                        </div>
                        
                        <div class="project-details">
                            <div class="detail-item">
                                <i class="fas fa-user"></i>
                                <span id="project-manager"></span>
                            </div>
                            <div class="detail-item">
                                <i class="fas fa-building"></i>
                                <span id="project-customer"></span>
                            </div>
                            <div class="detail-item">
                                <i class="fas fa-calendar"></i>
                                <span id="project-dates"></span>
                            </div>
                            <div class="detail-item">
                                <i class="fas fa-dollar-sign"></i>
                                <span id="project-budget"></span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="project-tabs">
                        <div class="tab-nav">
                            <button class="tab-btn active" onclick="pm.project_manager.show_tab('overview')">
                                Overview
                            </button>
                            <button class="tab-btn" onclick="pm.project_manager.show_tab('tasks')">
                                Tasks
                            </button>
                            <button class="tab-btn" onclick="pm.project_manager.show_tab('resources')">
                                Resources
                            </button>
                            <button class="tab-btn" onclick="pm.project_manager.show_tab('timeline')">
                                Timeline
                            </button>
                            <button class="tab-btn" onclick="pm.project_manager.show_tab('budget')">
                                Budget
                            </button>
                            <button class="tab-btn" onclick="pm.project_manager.show_tab('reports')">
                                Reports
                            </button>
                        </div>
                        
                        <div class="tab-content">
                            <div class="tab-pane active" id="overview-tab">
                                <div class="overview-content">
                                    <!-- Overview content will be loaded here -->
                                </div>
                            </div>
                            <div class="tab-pane" id="tasks-tab">
                                <div class="tasks-content">
                                    <!-- Tasks will be loaded here -->
                                </div>
                            </div>
                            <div class="tab-pane" id="resources-tab">
                                <div class="resources-content">
                                    <!-- Resources will be loaded here -->
                                </div>
                            </div>
                            <div class="tab-pane" id="timeline-tab">
                                <div class="timeline-content">
                                    <!-- Timeline will be loaded here -->
                                </div>
                            </div>
                            <div class="tab-pane" id="budget-tab">
                                <div class="budget-content">
                                    <!-- Budget will be loaded here -->
                                </div>
                            </div>
                            <div class="tab-pane" id="reports-tab">
                                <div class="reports-content">
                                    <!-- Reports will be loaded here -->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Load project details
        this.load_project_detail(project_id);
    }
    
    async load_project_detail(project_id) {
        try {
            const response = await fetch(`/api/method/pm.api.get_project_details?project_id=${project_id}`);
            const data = await response.json();
            
            if (data.message) {
                this.update_project_detail(data.message);
                this.load_project_tasks(project_id);
                this.load_project_resources(project_id);
                this.load_project_timeline(project_id);
                this.load_project_budget(project_id);
                this.load_project_reports(project_id);
            }
            
        } catch (error) {
            console.error('Error loading project details:', error);
        }
    }
    
    update_project_detail(project) {
        // Update basic information
        document.getElementById('project-name').textContent = project.project_name;
        document.getElementById('project-status').textContent = project.status;
        document.getElementById('project-priority').textContent = project.priority;
        document.getElementById('project-type').textContent = project.project_type;
        
        // Update project details
        document.getElementById('project-manager').textContent = project.project_manager;
        document.getElementById('project-customer').textContent = project.customer || '-';
        document.getElementById('project-dates').textContent = `${this.format_date(project.expected_start_date)} - ${this.format_date(project.expected_end_date)}`;
        document.getElementById('project-budget').textContent = this.format_currency(project.estimated_cost);
        
        // Update overview tab
        const overview_content = document.querySelector('#overview-tab .overview-content');
        overview_content.innerHTML = `
            <div class="overview-grid">
                <div class="overview-section">
                    <h3>Project Progress</h3>
                    <div class="progress-overview">
                        <div class="progress-bar-large">
                            <div class="progress-fill" style="width: ${project.progress}%"></div>
                            <span class="progress-text">${project.progress}%</span>
                        </div>
                        <div class="progress-details">
                            <p><strong>Completed Tasks:</strong> ${project.task_summary.completed_tasks}</p>
                            <p><strong>Total Tasks:</strong> ${project.task_summary.total_tasks}</p>
                            <p><strong>Overdue Tasks:</strong> ${project.task_summary.overdue_tasks}</p>
                        </div>
                    </div>
                </div>
                
                <div class="overview-section">
                    <h3>Timeline Status</h3>
                    <div class="timeline-status">
                        <div class="timeline-item">
                            <span class="timeline-label">Days Elapsed:</span>
                            <span class="timeline-value">${project.timeline_status.days_elapsed}</span>
                        </div>
                        <div class="timeline-item">
                            <span class="timeline-label">Days Remaining:</span>
                            <span class="timeline-value">${project.timeline_status.days_remaining}</span>
                        </div>
                        <div class="timeline-item">
                            <span class="timeline-label">Status:</span>
                            <span class="timeline-value">${project.timeline_status.is_on_track ? 'On Track' : 'Behind Schedule'}</span>
                        </div>
                    </div>
                </div>
                
                <div class="overview-section">
                    <h3>Resource Utilization</h3>
                    <div class="resource-utilization">
                        ${Object.entries(project.resource_utilization).map(([resource_id, data]) => `
                            <div class="resource-item">
                                <div class="resource-name">${data.resource_name}</div>
                                <div class="resource-role">${data.role}</div>
                                <div class="resource-efficiency">
                                    <span>Efficiency: ${data.efficiency.toFixed(1)}%</span>
                                    <div class="efficiency-bar">
                                        <div class="efficiency-fill" style="width: ${data.efficiency}%"></div>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="overview-section">
                    <h3>Budget Status</h3>
                    <div class="budget-status">
                        <div class="budget-item">
                            <span class="budget-label">Total Budget:</span>
                            <span class="budget-value">${this.format_currency(project.budget_status.total_budget)}</span>
                        </div>
                        <div class="budget-item">
                            <span class="budget-label">Spent:</span>
                            <span class="budget-value">${this.format_currency(project.budget_status.actual_costs)}</span>
                        </div>
                        <div class="budget-item">
                            <span class="budget-label">Remaining:</span>
                            <span class="budget-value">${this.format_currency(project.budget_status.remaining_budget)}</span>
                        </div>
                        <div class="budget-item">
                            <span class="budget-label">Utilization:</span>
                            <span class="budget-value">${project.budget_status.budget_utilization.toFixed(1)}%</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    format_currency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    }
    
    format_date(date_string) {
        return new Date(date_string).toLocaleDateString();
    }
    
    setup_event_listeners() {
        // Setup global event listeners
        document.addEventListener('project:updated', (event) => {
            this.handle_project_update(event.detail);
        });
        
        document.addEventListener('task:updated', (event) => {
            this.handle_task_update(event.detail);
        });
        
        document.addEventListener('resource:updated', (event) => {
            this.handle_resource_update(event.detail);
        });
    }
    
    handle_project_update(project_data) {
        // Update UI when project is updated
        if (this.current_page === 'projects') {
            this.load_projects();
        } else if (this.current_page === 'project_detail' && this.current_project_id === project_data.name) {
            this.load_project_detail(project_data.name);
        }
    }
    
    handle_task_update(task_data) {
        // Update UI when task is updated
        if (this.current_page === 'tasks') {
            this.load_tasks();
        } else if (this.current_page === 'project_detail') {
            this.load_project_tasks(this.current_project_id);
        }
    }
    
    handle_resource_update(resource_data) {
        // Update UI when resource is updated
        if (this.current_page === 'resources') {
            this.load_resources();
        } else if (this.current_page === 'project_detail') {
            this.load_project_resources(this.current_project_id);
        }
    }
}

// Initialize project management application
let pm;

document.addEventListener('DOMContentLoaded', () => {
    pm = new ProjectManagementFrontend();
});
```

### 13.3 Performance Optimization and Analytics

#### High-Performance PM Patterns

```python
# Project management performance optimization
class PMPerformanceOptimizer:
    def __init__(self):
        self.cache_manager = PMCacheManager()
        self.query_optimizer = PMQueryOptimizer()
        self.index_manager = PMIndexManager()
        self.batch_processor = PMBatchProcessor()
        self.analytics_optimizer = PMAnalyticsOptimizer()
    
    def optimize_pm_performance(self):
        """Optimize overall project management performance"""
        # Optimize database queries
        self.query_optimizer.optimize_project_queries()
        self.query_optimizer.optimize_task_queries()
        self.query_optimizer.optimize_resource_queries()
        
        # Setup caching
        self.cache_manager.setup_pm_cache()
        
        # Optimize indexes
        self.index_manager.optimize_database_indexes()
        
        # Setup batch processing
        self.batch_processor.setup_batch_operations()
        
        # Optimize analytics
        self.analytics_optimizer.optimize_analytics_queries()
    
    def optimize_project_performance(self):
        """Optimize project-specific performance"""
        # Cache project data
        self.cache_manager.setup_project_cache()
        
        # Optimize project calculations
        self.optimize_project_calculations()
        
        # Optimize project reporting
        self.optimize_project_reporting()
    
    def optimize_task_performance(self):
        """Optimize task-specific performance"""
        # Cache task data
        self.cache_manager.setup_task_cache()
        
        # Optimize task dependencies
        self.optimize_task_dependencies()
        
        # Optimize task scheduling
        self.optimize_task_scheduling()
    
    def optimize_resource_performance(self):
        """Optimize resource-specific performance"""
        # Cache resource data
        self.cache_manager.setup_resource_cache()
        
        # Optimize resource allocation
        self.optimize_resource_allocation()
        
        # Optimize capacity planning
        self.optimize_capacity_planning()

# Advanced project analytics
class AdvancedPMAnalytics:
    def __init__(self):
        self.predictive_analytics = PredictiveAnalytics()
        self.risk_analyzer = ProjectRiskAnalyzer()
        self.performance_analyzer = ProjectPerformanceAnalyzer()
        self.resource_analyzer = ResourcePerformanceAnalyzer()
        self.forecasting_engine = PMForecastingEngine()
    
    def get_project_insights(self, project_name):
        """Get comprehensive project insights"""
        return {
            'health_score': self.calculate_project_health_score(project_name),
            'risk_assessment': self.risk_analyzer.assess_project_risks(project_name),
            'performance_metrics': self.performance_analyzer.get_performance_metrics(project_name),
            'resource_efficiency': self.resource_analyzer.get_resource_efficiency(project_name),
            'completion_prediction': self.predictive_analytics.predict_completion(project_name)
        }
    
    def get_portfolio_analytics(self, filters=None):
        """Get portfolio-level analytics"""
        return {
            'portfolio_health': self.calculate_portfolio_health(filters),
            'resource_utilization': self.get_portfolio_resource_utilization(filters),
            'budget_performance': self.get_portfolio_budget_performance(filters),
            'timeline_analysis': self.get_portfolio_timeline_analysis(filters),
            'risk_distribution': self.get_portfolio_risk_distribution(filters)
        }
    
    def get_team_analytics(self, team_id=None, date_range=None):
        """Get team performance analytics"""
        return {
            'team_productivity': self.calculate_team_productivity(team_id, date_range),
            'skill_utilization': self.calculate_skill_utilization(team_id, date_range),
            'workload_balance': self.calculate_workload_balance(team_id, date_range),
            'performance_trends': self.get_performance_trends(team_id, date_range),
            'training_needs': self.identify_training_needs(team_id, date_range)
        }
    
    def get_predictive_insights(self, date_range=None):
        """Get predictive analytics insights"""
        return {
            'project_completion_forecast': self.forecast_project_completions(date_range),
            'resource_demand_forecast': self.forecast_resource_demand(date_range),
            'budget_variance_forecast': self.forecast_budget_variances(date_range),
            'risk_probability_forecast': self.forecast_risk_probabilities(date_range)
        }

# Project risk analyzer
class ProjectRiskAnalyzer:
    def __init__(self):
        self.risk_factors = {}
        self.risk_matrix = RiskMatrix()
        self.mitigation_strategies = MitigationStrategies()
    
    def assess_project_risks(self, project_name):
        """Assess project risks"""
        project = frappe.get_doc('Project', project_name)
        
        # Calculate risk factors
        risk_factors = self.calculate_risk_factors(project)
        
        # Calculate risk scores
        risk_scores = self.calculate_risk_scores(risk_factors)
        
        # Generate risk assessment
        risk_assessment = {
            'overall_risk_score': sum(risk_scores.values()) / len(risk_scores),
            'risk_categories': {
                'schedule_risk': risk_scores.get('schedule', 0),
                'budget_risk': risk_scores.get('budget', 0),
                'resource_risk': risk_scores.get('resource', 0),
                'technical_risk': risk_scores.get('technical', 0),
                'stakeholder_risk': risk_scores.get('stakeholder', 0)
            },
            'high_risk_items': self.identify_high_risk_items(risk_factors),
            'mitigation_recommendations': self.generate_mitigation_recommendations(risk_factors)
        }
        
        return risk_assessment
    
    def calculate_risk_factors(self, project):
        """Calculate risk factors for project"""
        risk_factors = {}
        
        # Schedule risk factors
        risk_factors['schedule'] = {
            'tight_timeline': self.assess_timeline_tightness(project),
            'complex_dependencies': self.assess_dependency_complexity(project),
            'resource_availability': self.assess_resource_availability(project),
            'external_dependencies': self.assess_external_dependencies(project)
        }
        
        # Budget risk factors
        risk_factors['budget'] = {
            'budget_adequacy': self.assess_budget_adequacy(project),
            'cost_estimation_accuracy': self.assess_cost_estimation_accuracy(project),
            'financial_stability': self.assess_financial_stability(project),
            'scope_creep': self.assess_scope_creep(project)
        }
        
        # Resource risk factors
        risk_factors['resource'] = {
            'skill_availability': self.assess_skill_availability(project),
            'team_stability': self.assess_team_stability(project),
            'workload_balance': self.assess_workload_balance(project),
            'resource_conflicts': self.assess_resource_conflicts(project)
        }
        
        # Technical risk factors
        risk_factors['technical'] = {
            'technical_complexity': self.assess_technical_complexity(project),
            'technology_maturity': self.assess_technology_maturity(project),
            'integration_complexity': self.assess_integration_complexity(project),
            'quality_requirements': self.assess_quality_requirements(project)
        }
        
        # Stakeholder risk factors
        risk_factors['stakeholder'] = {
            'stakeholder_alignment': self.assess_stakeholder_alignment(project),
            'communication_effectiveness': self.assess_communication_effectiveness(project),
            'requirement_clarity': self.assess_requirement_clarity(project),
            'change_management': self.assess_change_management(project)
        }
        
        return risk_factors
    
    def assess_timeline_tightness(self, project):
        """Assess timeline tightness"""
        if not project.expected_start_date or not project.expected_end_date:
            return 0.5  # Medium risk if no dates
        
        duration = (project.expected_end_date - project.expected_start_date).days
        
        # Get similar projects
        similar_projects = frappe.get_all('Project',
                                         filters={'project_type': project.project_type, 'status': 'Completed'},
                                         fields=['expected_start_date', 'expected_end_date'])
        
        if not similar_projects:
            return 0.5  # Medium risk if no similar projects
        
        # Calculate average duration for similar projects
        durations = []
        for similar_project in similar_projects:
            if similar_project.expected_start_date and similar_project.expected_end_date:
                proj_duration = (similar_project.expected_end_date - similar_project.expected_start_date).days
                durations.append(proj_duration)
        
        if not durations:
            return 0.5
        
        avg_duration = sum(durations) / len(durations)
        
        # Calculate risk based on deviation from average
        if duration < avg_duration * 0.8:
            return 0.8  # High risk - timeline too tight
        elif duration < avg_duration * 0.9:
            return 0.6  # Medium-high risk
        elif duration > avg_duration * 1.2:
            return 0.3  # Low risk - timeline generous
        else:
            return 0.4  # Medium risk
    
    def assess_budget_adequacy(self, project):
        """Assess budget adequacy"""
        if not project.estimated_cost:
            return 0.5  # Medium risk if no budget
        
        # Get cost history for similar projects
        similar_projects = frappe.get_all('Project',
                                         filters={'project_type': project.project_type, 'status': 'Completed'},
                                         fields=['estimated_cost'])
        
        if not similar_projects:
            return 0.5
        
        # Calculate average cost for similar projects
        costs = [proj.estimated_cost for proj in similar_projects if proj.estimated_cost]
        
        if not costs:
            return 0.5
        
        avg_cost = sum(costs) / len(costs)
        
        # Calculate risk based on budget adequacy
        if project.estimated_cost < avg_cost * 0.8:
            return 0.8  # High risk - budget too low
        elif project.estimated_cost < avg_cost * 0.9:
            return 0.6  # Medium-high risk
        elif project.estimated_cost > avg_cost * 1.2:
            return 0.2  # Low risk - budget generous
        else:
            return 0.4  # Medium risk
    
    def calculate_risk_scores(self, risk_factors):
        """Calculate risk scores from risk factors"""
        risk_scores = {}
        
        for category, factors in risk_factors.items():
            category_score = 0
            factor_count = len(factors)
            
            for factor_name, factor_score in factors.items():
                category_score += factor_score
            
            risk_scores[category] = category_score / factor_count if factor_count > 0 else 0
        
        return risk_scores
    
    def identify_high_risk_items(self, risk_factors):
        """Identify high-risk items"""
        high_risk_items = []
        
        for category, factors in risk_factors.items():
            for factor_name, factor_score in factors.items():
                if factor_score > 0.7:  # High risk threshold
                    high_risk_items.append({
                        'category': category,
                        'factor': factor_name,
                        'score': factor_score,
                        'description': self.get_risk_description(category, factor_name)
                    })
        
        # Sort by score
        high_risk_items.sort(key=lambda x: x['score'], reverse=True)
        
        return high_risk_items
    
    def get_risk_description(self, category, factor_name):
        """Get description for risk factor"""
        descriptions = {
            'schedule': {
                'tight_timeline': 'Project timeline is very tight with little buffer for delays',
                'complex_dependencies': 'Complex task dependencies increase risk of delays',
                'resource_availability': 'Limited resource availability may impact schedule',
                'external_dependencies': 'External dependencies may cause delays'
            },
            'budget': {
                'budget_adequacy': 'Budget may be inadequate for project scope',
                'cost_estimation_accuracy': 'Cost estimation accuracy may be poor',
                'financial_stability': 'Financial stability concerns may impact project',
                'scope_creep': 'High risk of scope creep affecting budget'
            },
            'resource': {
                'skill_availability': 'Required skills may not be readily available',
                'team_stability': 'Team stability concerns may impact project',
                'workload_balance': 'Imbalanced workload may affect performance',
                'resource_conflicts': 'Resource conflicts may impact project progress'
            },
            'technical': {
                'technical_complexity': 'High technical complexity increases implementation risk',
                'technology_maturity': 'Immature technology may cause issues',
                'integration_complexity': 'Complex integrations may be challenging',
                'quality_requirements': 'Stringent quality requirements may increase risk'
            },
            'stakeholder': {
                'stakeholder_alignment': 'Poor stakeholder alignment may cause issues',
                'communication_effectiveness': 'Communication issues may impact project',
                'requirement_clarity': 'Unclear requirements may cause problems',
                'change_management': 'Poor change management may impact project'
            }
        }
        
        return descriptions.get(category, {}).get(factor_name, 'Risk factor description not available')
    
    def generate_mitigation_recommendations(self, risk_factors):
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        for category, factors in risk_factors.items():
            for factor_name, factor_score in factors.items():
                if factor_score > 0.5:  # Only recommend for medium+ risk
                    recommendation = self.get_mitigation_recommendation(category, factor_name)
                    if recommendation:
                        recommendations.append(recommendation)
        
        return recommendations
    
    def get_mitigation_recommendation(self, category, factor_name):
        """Get mitigation recommendation for risk factor"""
        recommendations = {
            'schedule': {
                'tight_timeline': 'Add buffer time to critical path, prioritize essential features',
                'complex_dependencies': 'Simplify dependencies, use parallel processing where possible',
                'resource_availability': 'Secure resources early, have backup resources available',
                'external_dependencies': 'Plan for delays, have contingency plans'
            },
            'budget': {
                'budget_adequacy': 'Review scope, add contingency budget, monitor costs closely',
                'cost_estimation_accuracy': 'Use detailed estimation, get expert review, add buffer',
                'financial_stability': 'Monitor financial health, have backup funding options',
                'scope_creep': 'Implement change control process, define scope clearly'
            },
            'resource': {
                'skill_availability': 'Plan training, hire contractors, cross-train team members',
                'team_stability': 'Improve team morale, provide good working conditions',
                'workload_balance': 'Redistribute work, hire additional resources',
                'resource_conflicts': 'Use resource scheduling, clear priorities'
            },
            'technical': {
                'technical_complexity': 'Use proven technologies, phased implementation',
                'technology_maturity': 'Choose mature technologies, have fallback options',
                'integration_complexity': 'Simplify integrations, use standard interfaces',
                'quality_requirements': 'Implement quality processes, continuous testing'
            },
            'stakeholder': {
                'stakeholder_alignment': 'Regular communication, stakeholder workshops',
                'communication_effectiveness': 'Clear communication plan, regular updates',
                'requirement_clarity': 'Detailed requirements, sign-off process',
                'change_management': 'Change management plan, stakeholder involvement'
            }
        }
        
        return recommendations.get(category, {}).get(factor_name)

# Project performance analyzer
class ProjectPerformanceAnalyzer:
    def __init__(self):
        self.metrics_calculator = MetricsCalculator()
        self.benchmark_comparator = BenchmarkComparator()
        self.trend_analyzer = TrendAnalyzer()
    
    def get_performance_metrics(self, project_name):
        """Get comprehensive project performance metrics"""
        project = frappe.get_doc('Project', project_name)
        
        metrics = {
            'schedule_performance': self.calculate_schedule_performance(project),
            'budget_performance': self.calculate_budget_performance(project),
            'quality_performance': self.calculate_quality_performance(project),
            'resource_performance': self.calculate_resource_performance(project),
            'stakeholder_satisfaction': self.calculate_stakeholder_satisfaction(project)
        }
        
        # Calculate overall performance score
        metrics['overall_score'] = self.calculate_overall_performance_score(metrics)
        
        return metrics
    
    def calculate_schedule_performance(self, project):
        """Calculate schedule performance metrics"""
        today = frappe.utils.today()
        
        # Calculate schedule variance
        if project.expected_end_date:
            days_remaining = (project.expected_end_date - today).days
            planned_duration = (project.expected_end_date - project.expected_start_date).days
            elapsed_days = (today - project.expected_start_date).days
            
            if planned_duration > 0:
                progress_percentage = (elapsed_days / planned_duration) * 100
                schedule_variance = abs(progress_percentage - (project.progress or 0))
            else:
                schedule_variance = 0
        else:
            schedule_variance = 0
        
        # Calculate on-time completion probability
        on_time_probability = self.calculate_on_time_probability(project)
        
        return {
            'schedule_variance': schedule_variance,
            'on_time_probability': on_time_probability,
            'days_behind_schedule': max(0, -days_remaining) if days_remaining else 0,
            'critical_path_performance': self.calculate_critical_path_performance(project)
        }
    
    def calculate_budget_performance(self, project):
        """Calculate budget performance metrics"""
        # Get actual costs
        cost_data = self.get_project_costs(project.name)
        
        if project.estimated_cost:
            budget_variance = cost_data['total_cost'] - project.estimated_cost
            budget_variance_percentage = (budget_variance / project.estimated_cost * 100) if project.estimated_cost > 0 else 0
            
            budget_utilization = (cost_data['total_cost'] / project.estimated_cost * 100) if project.estimated_cost > 0 else 0
        else:
            budget_variance = 0
            budget_variance_percentage = 0
            budget_utilization = 0
        
        return {
            'budget_variance': budget_variance,
            'budget_variance_percentage': budget_variance_percentage,
            'budget_utilization': budget_utilization,
            'cost_efficiency': self.calculate_cost_efficiency(project.name, cost_data)
        }
    
    def calculate_quality_performance(self, project):
        """Calculate quality performance metrics"""
        # Get quality metrics
        quality_metrics = self.get_quality_metrics(project.name)
        
        return {
            'defect_rate': quality_metrics.get('defect_rate', 0),
            'rework_rate': quality_metrics.get('rework_rate', 0),
            'customer_satisfaction': quality_metrics.get('customer_satisfaction', 0),
            'quality_score': self.calculate_quality_score(quality_metrics)
        }
    
    def calculate_resource_performance(self, project):
        """Calculate resource performance metrics"""
        # Get resource metrics
        resource_metrics = self.get_resource_metrics(project.name)
        
        return {
            'resource_utilization': resource_metrics.get('utilization', 0),
            'resource_efficiency': resource_metrics.get('efficiency', 0),
            'team_productivity': resource_metrics.get('productivity', 0),
            'skill_utilization': resource_metrics.get('skill_utilization', 0)
        }
    
    def calculate_stakeholder_satisfaction(self, project):
        """Calculate stakeholder satisfaction metrics"""
        # Get stakeholder feedback
        stakeholder_feedback = self.get_stakeholder_feedback(project.name)
        
        return {
            'overall_satisfaction': stakeholder_feedback.get('overall_satisfaction', 0),
            'communication_satisfaction': stakeholder_feedback.get('communication_satisfaction', 0),
            'deliverable_satisfaction': stakeholder_feedback.get('deliverable_satisfaction', 0),
            'engagement_level': stakeholder_feedback.get('engagement_level', 0)
        }
    
    def calculate_overall_performance_score(self, metrics):
        """Calculate overall project performance score"""
        weights = {
            'schedule_performance': 0.3,
            'budget_performance': 0.25,
            'quality_performance': 0.2,
            'resource_performance': 0.15,
            'stakeholder_satisfaction': 0.1
        }
        
        overall_score = 0
        
        for metric_name, weight in weights.items():
            metric_data = metrics.get(metric_name, {})
            
            if metric_name == 'schedule_performance':
                metric_score = 100 - (metric_data.get('schedule_variance', 0) * 10)  # Convert variance to score
            elif metric_name == 'budget_performance':
                metric_score = 100 - abs(metric_data.get('budget_variance_percentage', 0))
            elif metric_name == 'quality_performance':
                metric_score = metric_data.get('quality_score', 50)
            elif metric_name == 'resource_performance':
                metric_score = metric_data.get('resource_efficiency', 50)
            elif metric_name == 'stakeholder_satisfaction':
                metric_score = metric_data.get('overall_satisfaction', 50)
            else:
                metric_score = 50
            
            overall_score += metric_score * weight
        
        return max(0, min(100, overall_score))  # Clamp between 0 and 100
    
    def get_project_costs(self, project_name):
        """Get project cost data"""
        # Get time logs
        time_logs = frappe.get_all('Time Log',
                                  filters={'project': project_name},
                                  fields=['hours', 'user'])
        
        # Calculate labor cost
        labor_cost = 0
        for log in time_logs:
            hourly_rate = frappe.db.get_value('Employee', {'user_id': log.user}, 'hourly_rate') or 50
            labor_cost += log.hours * hourly_rate
        
        # Get expenses
        expenses = frappe.get_all('Expense',
                                 filters={'project': project_name, 'status': 'Submitted'},
                                 fields=['amount'])
        
        expense_cost = sum(exp.amount for exp in expenses)
        
        return {
            'labor_cost': labor_cost,
            'expense_cost': expense_cost,
            'total_cost': labor_cost + expense_cost
        }
    
    def get_quality_metrics(self, project_name):
        """Get quality metrics"""
        # Get quality issues
        quality_issues = frappe.get_all('Quality Issue',
                                       filters={'project': project_name},
                                       fields=['severity', 'resolution_time'])
        
        total_issues = len(quality_issues)
        critical_issues = len([issue for issue in quality_issues if issue.severity == 'Critical'])
        
        # Calculate defect rate (simplified)
        total_tasks = frappe.db.count('Task', {'project': project_name})
        defect_rate = (total_issues / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate rework rate (simplified)
        rework_tasks = frappe.db.count('Task', {'project': project_name, 'status': 'Rework'})
        rework_rate = (rework_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            'defect_rate': defect_rate,
            'rework_rate': rework_rate,
            'critical_issues': critical_issues,
            'total_issues': total_issues
        }
    
    def calculate_quality_score(self, quality_metrics):
        """Calculate quality score from metrics"""
        # Simple quality score calculation
        defect_penalty = quality_metrics.get('defect_rate', 0) * 0.5
        rework_penalty = quality_metrics.get('rework_rate', 0) * 0.3
        critical_penalty = quality_metrics.get('critical_issues', 0) * 2
        
        quality_score = max(0, 100 - defect_penalty - rework_penalty - critical_penalty)
        
        return quality_score
```

## 🛠️ Practical Exercises

### Exercise 13.1: Build a Complete Project Management System

Create a full project management system with:
- Project creation and management
- Task tracking with dependencies
- Resource allocation and scheduling
- Time tracking and billing
- Budget management and reporting

### Exercise 13.2: Implement Advanced PM Features

Add advanced project management features:
- Gantt chart visualization
- Critical path analysis
- Risk assessment and mitigation
- Resource optimization algorithms
- Predictive analytics for project outcomes

### Exercise 13.3: Optimize PM Performance

Implement performance optimizations:
- Database query optimization for large projects
- Caching strategies for project data
- Batch processing for time logs and expenses
- Real-time project progress tracking
- Mobile-responsive PM interface

## 🚀 Best Practices

### Project Management Architecture

- **Use ERPNext as foundation** for project and task management
- **Implement proper data modeling** for project hierarchies
- **Design for scalability** with microservices architecture
- **Use role-based access** for project security
- **Implement audit trails** for compliance

### Performance Optimization

- **Cache project data** for frequently accessed projects
- **Optimize dependency calculations** with graph algorithms
- **Use batch processing** for time log and expense data
- **Implement real-time updates** for critical project data
- **Monitor performance** with project analytics

### User Experience

- **Design intuitive interfaces** for project managers
- **Provide visual project tracking** with charts and Gantt charts
- **Implement mobile access** for field teams
- **Use automation** to reduce manual project management
- **Provide training and support** for user adoption

## 📖 Further Reading

- [ERPNext Project Management Documentation](https://erpnext.com/docs/user/en/project-management)
- [Project Management Best Practices](https://www.pmi.org/)
- [Agile Project Management](https://agilemanifesto.org/)
- [Gantt Chart Visualization](https://www.gantt.com/)

## 🎯 Chapter Summary

Building a complete project management system requires:

- **PM Architecture** provides the foundation for effective project management
- **Project Management** enables comprehensive project tracking and control
- **Task Management** creates detailed task and dependency management
- **Resource Management** ensures optimal resource allocation and utilization
- **Time & Budget Tracking** delivers accurate project cost and progress monitoring

---

**Book Conclusion**: You've now mastered the complete ERPNext development ecosystem from architecture to advanced applications.
