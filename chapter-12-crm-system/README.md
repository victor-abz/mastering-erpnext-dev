# Chapter 12: CRM System Development

## 🎯 Learning Objectives

By the end of this chapter, you will master:

- **How** to build a complete CRM system using Frappe/ERPNext
- **Why** CRM architecture requires specific customer relationship patterns
- **When** to use custom CRM features vs standard ERPNext capabilities
- **How** lead management, opportunity tracking, and customer communication work internally
- **Advanced patterns** for building scalable CRM solutions
- **Performance optimization** techniques for high-volume CRM operations

## 📚 Chapter Topics

### 12.1 CRM Architecture Overview

**The CRM System Architecture**

Building a CRM system on Frappe requires understanding how to leverage ERPNext's customer, sales, and communication capabilities while creating a comprehensive customer relationship management platform.

#### Core CRM Components

```python
# CRM system architecture
class CRMSystem:
    def __init__(self):
        self.lead_manager = LeadManager()
        self.opportunity_manager = OpportunityManager()
        self.customer_manager = CRMCustomerManager()
        self.communication_manager = CommunicationManager()
        self.activity_tracker = ActivityTracker()
        self.automation_engine = CRMAutomationEngine()
        self.analytics_engine = CRMAnalyticsEngine()
        self.performance_monitor = CRMPerformanceMonitor()
    
    def initialize_crm(self):
        """Initialize CRM system components"""
        # Setup lead management
        self.lead_manager.setup_lead_workflow()
        
        # Configure opportunity tracking
        self.opportunity_manager.setup_opportunity_stages()
        
        # Setup customer management
        self.customer_manager.setup_customer_lifecycle()
        
        # Configure communication channels
        self.communication_manager.setup_channels()
        
        # Setup automation rules
        self.automation_engine.setup_automation_rules()
        
        # Initialize analytics
        self.analytics_engine.setup_tracking()
        
        return {
            'status': 'initialized',
            'components': list(self.__dict__.keys())
        }

# Lead management system
class LeadManager:
    def __init__(self):
        self.lead_scoring = LeadScoringEngine()
        self.lead_routing = LeadRoutingEngine()
        self.duplicate_detector = LeadDuplicateDetector()
        self.lead_converter = LeadConverter()
        self.communication_tracker = LeadCommunicationTracker()
    
    def setup_lead_workflow(self):
        """Setup lead management workflow"""
        # Create lead stages
        self.create_lead_stages()
        
        # Setup lead assignment rules
        self.setup_lead_assignment()
        
        # Configure lead scoring
        self.lead_scoring.setup_scoring_rules()
        
        # Setup duplicate detection
        self.duplicate_detector.setup_duplicate_rules()
    
    def create_lead_stages(self):
        """Create lead management stages"""
        stages = [
            {
                'stage_name': 'New',
                'description': 'Newly created lead',
                'probability': 10,
                'expected_duration': 1
            },
            {
                'stage_name': 'Contacted',
                'description': 'Initial contact made',
                'probability': 25,
                'expected_duration': 3
            },
            {
                'stage_name': 'Qualified',
                'description': 'Lead qualified for follow-up',
                'probability': 50,
                'expected_duration': 7
            },
            {
                'stage_name': 'Proposal',
                'description': 'Proposal sent to lead',
                'probability': 75,
                'expected_duration': 14
            },
            {
                'stage_name': 'Negotiation',
                'description': 'Negotiation in progress',
                'probability': 90,
                'expected_duration': 21
            },
            {
                'stage_name': 'Converted',
                'description': 'Lead converted to customer',
                'probability': 100,
                'expected_duration': 30
            },
            {
                'stage_name': 'Lost',
                'description': 'Lead lost',
                'probability': 0,
                'expected_duration': 0
            }
        ]
        
        for stage_data in stages:
            if not frappe.db.exists('Lead Stage', stage_data['stage_name']):
                stage = frappe.new_doc('Lead Stage')
                stage.stage_name = stage_data['stage_name']
                stage.description = stage_data['description']
                stage.probability = stage_data['probability']
                stage.expected_duration = stage_data['expected_duration']
                stage.insert()
    
    def create_lead(self, lead_data):
        """Create new lead with validation and processing"""
        # Validate lead data
        self.validate_lead_data(lead_data)
        
        # Check for duplicates
        duplicate_check = self.duplicate_detector.check_duplicates(lead_data)
        if duplicate_check['has_duplicates']:
            return self.handle_duplicate_lead(lead_data, duplicate_check['duplicates'])
        
        # Create lead document
        lead = frappe.new_doc('Lead')
        lead.lead_name = lead_data.get('lead_name')
        lead.company_name = lead_data.get('company_name')
        lead.email_id = lead_data.get('email_id')
        lead.phone = lead_data.get('phone')
        lead.mobile_no = lead_data.get('mobile_no')
        lead.lead_owner = lead_data.get('lead_owner', frappe.session.user)
        lead.source = lead_data.get('source', 'Website')
        lead.status = 'Lead'
        lead.lead_stage = 'New'
        
        # Set custom fields
        if lead_data.get('custom_fields'):
            for field, value in lead_data['custom_fields'].items():
                if hasattr(lead, field):
                    setattr(lead, field, value)
        
        lead.insert()
        
        # Calculate lead score
        lead_score = self.lead_scoring.calculate_lead_score(lead)
        frappe.db.set_value('Lead', lead.name, 'lead_score', lead_score)
        
        # Route lead to appropriate owner
        if lead_data.get('auto_assign', True):
            self.lead_routing.route_lead(lead.name)
        
        # Trigger automation
        self.trigger_lead_automation(lead.name, 'created')
        
        return lead
    
    def validate_lead_data(self, lead_data):
        """Validate lead data"""
        required_fields = ['lead_name']
        
        for field in required_fields:
            if not lead_data.get(field):
                raise Exception(f"Required field {field} is missing")
        
        # Validate email format
        if lead_data.get('email_id'):
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, lead_data['email_id']):
                raise Exception("Invalid email format")
        
        # Validate phone format
        if lead_data.get('phone'):
            phone = re.sub(r'[^\d]', '', lead_data['phone'])
            if len(phone) < 10:
                raise Exception("Invalid phone number")
    
    def handle_duplicate_lead(self, lead_data, duplicates):
        """Handle duplicate lead detection"""
        # Create duplicate lead record
        duplicate_lead = frappe.new_doc('Duplicate Lead')
        duplicate_lead.lead_name = lead_data.get('lead_name')
        duplicate_lead.email_id = lead_data.get('email_id')
        duplicate_lead.phone = lead_data.get('phone')
        duplicate_lead.source = lead_data.get('source')
        duplicate_lead.status = 'Duplicate'
        duplicate_lead.duplicate_of = duplicates[0]['name']
        duplicate_lead.insert()
        
        return {
            'status': 'duplicate_detected',
            'duplicate_lead': duplicate_lead.name,
            'existing_leads': duplicates
        }
    
    def update_lead_stage(self, lead_name, new_stage, notes=None):
        """Update lead stage with validation"""
        lead = frappe.get_doc('Lead', lead_name)
        
        if lead.lead_stage == new_stage:
            return lead  # No change needed
        
        # Validate stage transition
        if not self.validate_stage_transition(lead.lead_stage, new_stage):
            raise Exception(f"Invalid stage transition from {lead.lead_stage} to {new_stage}")
        
        old_stage = lead.lead_stage
        lead.lead_stage = new_stage
        
        # Update stage change date
        lead.stage_change_date = frappe.utils.now()
        
        # Add stage change note
        if notes:
            lead.add_comment(f"Stage changed from {old_stage} to {new_stage}: {notes}")
        
        lead.save()
        
        # Trigger automation
        self.trigger_lead_automation(lead_name, 'stage_changed', {
            'old_stage': old_stage,
            'new_stage': new_stage
        })
        
        return lead
    
    def validate_stage_transition(self, current_stage, new_stage):
        """Validate lead stage transition"""
        # Define allowed transitions
        allowed_transitions = {
            'New': ['Contacted', 'Qualified', 'Lost'],
            'Contacted': ['Qualified', 'Lost'],
            'Qualified': ['Proposal', 'Lost'],
            'Proposal': ['Negotiation', 'Lost'],
            'Negotiation': ['Converted', 'Lost'],
            'Converted': [],
            'Lost': []
        }
        
        return new_stage in allowed_transitions.get(current_stage, [])
    
    def convert_lead_to_customer(self, lead_name, customer_data=None):
        """Convert lead to customer"""
        lead = frappe.get_doc('Lead', lead_name)
        
        if lead.status != 'Lead':
            raise Exception("Only leads can be converted to customers")
        
        # Create customer from lead
        customer = self.lead_converter.convert_to_customer(lead, customer_data)
        
        # Update lead status
        lead.status = 'Converted'
        lead.converted_date = frappe.utils.now()
        lead.customer = customer.name
        lead.save()
        
        # Create opportunity if needed
        if customer_data and customer_data.get('create_opportunity'):
            opportunity = self.create_opportunity_from_lead(lead, customer)
        
        # Trigger automation
        self.trigger_lead_automation(lead_name, 'converted', {
            'customer': customer.name
        })
        
        return {
            'customer': customer,
            'lead': lead
        }
    
    def create_opportunity_from_lead(self, lead, customer):
        """Create opportunity from lead"""
        opportunity = frappe.new_doc('Opportunity')
        opportunity.opportunity_name = f"Opp-{lead.lead_name}"
        opportunity.customer = customer.name
        opportunity.lead = lead.name
        opportunity.opportunity_amount = lead.lead_score * 100  # Example calculation
        opportunity.status = 'Open'
        opportunity.insert()
        
        return opportunity
    
    def trigger_lead_automation(self, lead_name, event, context=None):
        """Trigger automation rules for lead events"""
        automation_rules = frappe.get_all('Lead Automation Rule',
                                          filters={'event': event, 'enabled': 1},
                                          fields=['name', 'action_type', 'action_data'])
        
        for rule in automation_rules:
            try:
                self.execute_automation_rule(lead_name, rule, context)
            except Exception as e:
                frappe.log_error(f"Failed to execute automation rule {rule.name}: {str(e)}")
    
    def execute_automation_rule(self, lead_name, rule, context):
        """Execute individual automation rule"""
        action_type = rule.action_type
        action_data = json.loads(rule.action_data or '{}')
        
        if action_type == 'Send Email':
            self.send_automation_email(lead_name, action_data)
        elif action_type == 'Create Task':
            self.create_automation_task(lead_name, action_data)
        elif action_type == 'Assign Owner':
            self.assign_lead_owner(lead_name, action_data)
        elif action_type == 'Update Field':
            self.update_lead_field(lead_name, action_data)
        elif action_type == 'Create Note':
            self.create_lead_note(lead_name, action_data)
    
    def send_automation_email(self, lead_name, action_data):
        """Send automated email to lead"""
        lead = frappe.get_doc('Lead', lead_name)
        
        template = action_data.get('template')
        recipients = action_data.get('recipients', [lead.email_id])
        
        if template and recipients:
            frappe.sendmail(
                recipients=recipients,
                template=template,
                reference_doctype=lead.doctype,
                reference_name=lead.name,
                args=lead.as_dict()
            )
    
    def create_automation_task(self, lead_name, action_data):
        """Create automated task"""
        task = frappe.new_doc('Task')
        task.subject = action_data.get('subject', f"Follow up with {lead.lead_name}")
        task.description = action_data.get('description', '')
        task.status = 'Open'
        task.priority = action_data.get('priority', 'Medium')
        task.reference_doctype = 'Lead'
        task.reference_name = lead_name
        task.assigned_to = action_data.get('assigned_to', frappe.session.user)
        task.due_date = frappe.utils.add_to_date(frappe.utils.now(), days=action_data.get('due_days', 7))
        task.insert()

# Lead scoring engine
class LeadScoringEngine:
    def __init__(self):
        self.scoring_rules = []
        self.load_scoring_rules()
    
    def load_scoring_rules(self):
        """Load lead scoring rules"""
        self.scoring_rules = frappe.get_all('Lead Scoring Rule',
                                          filters={'enabled': 1},
                                          fields=['rule_name', 'condition', 'points', 'rule_type'])
    
    def calculate_lead_score(self, lead):
        """Calculate lead score based on rules"""
        total_score = 0
        applied_rules = []
        
        for rule in self.scoring_rules:
            if self.evaluate_rule_condition(lead, rule):
                total_score += rule.points
                applied_rules.append(rule.rule_name)
        
        # Store scoring details
        scoring_details = {
            'total_score': total_score,
            'applied_rules': applied_rules,
            'scoring_date': frappe.utils.now()
        }
        
        return total_score
    
    def evaluate_rule_condition(self, lead, rule):
        """Evaluate rule condition for lead"""
        condition = rule.condition
        rule_type = rule.rule_type
        
        if rule_type == 'Field Based':
            return self.evaluate_field_condition(lead, condition)
        elif rule_type == 'Activity Based':
            return self.evaluate_activity_condition(lead, condition)
        elif rule_type == 'Demographic Based':
            return self.evaluate_demographic_condition(lead, condition)
        
        return False
    
    def evaluate_field_condition(self, lead, condition):
        """Evaluate field-based condition"""
        try:
            # Parse condition (simplified example)
            field, operator, value = condition.split('|')
            
            lead_value = getattr(lead, field, None)
            
            if operator == 'equals':
                return str(lead_value) == value
            elif operator == 'contains':
                return value in str(lead_value)
            elif operator == 'greater_than':
                return float(lead_value) > float(value)
            elif operator == 'less_than':
                return float(lead_value) < float(value)
            
        except Exception:
            pass
        
        return False
    
    def evaluate_activity_condition(self, lead, condition):
        """Evaluate activity-based condition"""
        # Check recent activities
        activities = frappe.get_all('Communication',
                                   filters={'reference_doctype': 'Lead', 'reference_name': lead.name,
                                           'communication_date': ['>=', frappe.utils.add_to_date(frappe.utils.now(), days=-30)]},
                                   fields=['communication_type'])
        
        activity_types = [act.communication_type for act in activities]
        
        return condition in activity_types
    
    def evaluate_demographic_condition(self, lead, condition):
        """Evaluate demographic-based condition"""
        # This would involve more complex demographic analysis
        return False

# Opportunity management system
class OpportunityManager:
    def __init__(self):
        self.opportunity_scoring = OpportunityScoringEngine()
        self.forecasting_engine = OpportunityForecastingEngine()
        self.competition_tracker = CompetitionTracker()
    
    def setup_opportunity_stages(self):
        """Setup opportunity management stages"""
        stages = [
            {
                'stage_name': 'Qualification',
                'description': 'Initial qualification stage',
                'probability': 20,
                'duration': 7
            },
            {
                'stage_name': 'Needs Analysis',
                'description': 'Analyzing customer needs',
                'probability': 40,
                'duration': 14
            },
            {
                'stage_name': 'Value Proposition',
                'description': 'Presenting value proposition',
                'probability': 60,
                'duration': 21
            },
            {
                'stage_name': 'Proposal/Price Quote',
                'description': 'Proposal and pricing stage',
                'probability': 75,
                'duration': 30
            },
            {
                'stage_name': 'Negotiation/Review',
                'description': 'Negotiation and review stage',
                'probability': 90,
                'duration': 45
            },
            {
                'stage_name': 'Closed Won',
                'description': 'Opportunity won',
                'probability': 100,
                'duration': 60
            },
            {
                'stage_name': 'Closed Lost',
                'description': 'Opportunity lost',
                'probability': 0,
                'duration': 0
            }
        ]
        
        for stage_data in stages:
            if not frappe.db.exists('Opportunity Stage', stage_data['stage_name']):
                stage = frappe.new_doc('Opportunity Stage')
                stage.stage_name = stage_data['stage_name']
                stage.description = stage_data['description']
                stage.probability = stage_data['probability']
                stage.duration = stage_data['duration']
                stage.insert()
    
    def create_opportunity(self, opportunity_data):
        """Create new opportunity"""
        # Validate opportunity data
        self.validate_opportunity_data(opportunity_data)
        
        # Create opportunity document
        opportunity = frappe.new_doc('Opportunity')
        opportunity.opportunity_name = opportunity_data.get('opportunity_name')
        opportunity.customer = opportunity_data.get('customer')
        opportunity.lead = opportunity_data.get('lead')
        opportunity.opportunity_amount = opportunity_data.get('opportunity_amount')
        opportunity.closing_date = opportunity_data.get('closing_date')
        opportunity.opportunity_stage = 'Qualification'
        opportunity.status = 'Open'
        opportunity.opportunity_owner = opportunity_data.get('opportunity_owner', frappe.session.user)
        opportunity.source = opportunity_data.get('source')
        
        # Add team members
        if opportunity_data.get('team_members'):
            for member in opportunity_data['team_members']:
                opportunity.append('team_members', {
                    'user': member['user'],
                    'role': member.get('role', 'Team Member')
                })
        
        opportunity.insert()
        
        # Calculate opportunity score
        opportunity_score = self.opportunity_scoring.calculate_opportunity_score(opportunity)
        frappe.db.set_value('Opportunity', opportunity.name, 'opportunity_score', opportunity_score)
        
        return opportunity
    
    def validate_opportunity_data(self, opportunity_data):
        """Validate opportunity data"""
        required_fields = ['customer', 'opportunity_amount', 'closing_date']
        
        for field in required_fields:
            if not opportunity_data.get(field):
                raise Exception(f"Required field {field} is missing")
        
        # Validate customer exists
        if not frappe.db.exists('Customer', opportunity_data['customer']):
            raise Exception("Customer does not exist")
        
        # Validate closing date
        closing_date = frappe.utils.getdate(opportunity_data['closing_date'])
        if closing_date < frappe.utils.getdate():
            raise Exception("Closing date cannot be in the past")
    
    def update_opportunity_stage(self, opportunity_name, new_stage, notes=None):
        """Update opportunity stage"""
        opportunity = frappe.get_doc('Opportunity', opportunity_name)
        
        old_stage = opportunity.opportunity_stage
        opportunity.opportunity_stage = new_stage
        opportunity.stage_change_date = frappe.utils.now()
        
        if notes:
            opportunity.add_comment(f"Stage changed from {old_stage} to {new_stage}: {notes}")
        
        opportunity.save()
        
        # Update probability based on stage
        stage_probability = frappe.db.get_value('Opportunity Stage', new_stage, 'probability')
        if stage_probability:
            frappe.db.set_value('Opportunity', opportunity_name, 'probability', stage_probability)
        
        return opportunity
    
    def close_opportunity(self, opportunity_name, status, closing_notes=None):
        """Close opportunity as won or lost"""
        opportunity = frappe.get_doc('Opportunity', opportunity_name)
        
        if opportunity.status != 'Open':
            raise Exception("Only open opportunities can be closed")
        
        opportunity.status = status
        opportunity.closing_date = frappe.utils.now()
        
        if closing_notes:
            opportunity.closing_notes = closing_notes
        
        if status == 'Closed Won':
            opportunity.opportunity_stage = 'Closed Won'
            # Create sales order if needed
            self.create_sales_order_from_opportunity(opportunity)
        elif status == 'Closed Lost':
            opportunity.opportunity_stage = 'Closed Lost'
            # Record loss reason
            opportunity.loss_reason = closing_notes
        
        opportunity.save()
        
        return opportunity
    
    def create_sales_order_from_opportunity(self, opportunity):
        """Create sales order from won opportunity"""
        # Get opportunity items or create from customer
        items = self.get_opportunity_items(opportunity)
        
        if not items:
            return None
        
        # Create sales order
        sales_order = frappe.new_doc('Sales Order')
        sales_order.customer = opportunity.customer
        sales_order.opportunity = opportunity.name
        sales_order.transaction_date = frappe.utils.nowdate()
        sales_order.delivery_date = frappe.utils.add_to_date(frappe.utils.nowdate(), days=30)
        
        # Add items
        for item in items:
            sales_order.append('items', {
                'item_code': item['item_code'],
                'qty': item['qty'],
                'rate': item['rate'],
                'delivery_date': sales_order.delivery_date
            })
        
        sales_order.insert()
        
        return sales_order
    
    def get_opportunity_items(self, opportunity):
        """Get items for opportunity"""
        # Check if opportunity has items
        opportunity_items = frappe.get_all('Opportunity Item',
                                           filters={'parent': opportunity.name},
                                           fields=['item_code', 'qty', 'rate'])
        
        if opportunity_items:
            return opportunity_items
        
        # Get customer's frequently purchased items
        customer_items = frappe.get_all('Sales Order Item',
                                        filters={'customer': opportunity.customer, 'docstatus': 1},
                                        fields=['item_code', 'qty', 'rate'],
                                        limit=10,
                                        order_by='creation desc')
        
        return customer_items

# CRM automation engine
class CRMAutomationEngine:
    def __init__(self):
        self.rule_engine = AutomationRuleEngine()
        self.workflow_engine = WorkflowEngine()
        self.notification_engine = NotificationEngine()
        self.task_scheduler = TaskScheduler()
    
    def setup_automation_rules(self):
        """Setup CRM automation rules"""
        # Create default automation rules
        self.create_default_automation_rules()
        
        # Setup rule execution engine
        self.rule_engine.setup_execution_engine()
        
        # Configure workflows
        self.workflow_engine.setup_workflows()
        
        # Setup notifications
        self.notification_engine.setup_notifications()
    
    def create_default_automation_rules(self):
        """Create default CRM automation rules"""
        rules = [
            {
                'rule_name': 'Lead Assignment',
                'event': 'Lead Created',
                'condition': 'lead_score > 50',
                'action': 'Assign to Sales Manager',
                'enabled': 1
            },
            {
                'rule_name': 'Follow Up Reminder',
                'event': 'Lead Stage Changed',
                'condition': 'new_stage = Contacted',
                'action': 'Create Follow Up Task',
                'enabled': 1
            },
            {
                'rule_name': 'Opportunity Alert',
                'event': 'Opportunity Stage Changed',
                'condition': 'new_stage = Proposal/Price Quote',
                'action': 'Send Email Alert',
                'enabled': 1
            },
            {
                'rule_name': 'Customer Welcome',
                'event': 'Customer Created',
                'condition': 'customer_type = Individual',
                'action': 'Send Welcome Email',
                'enabled': 1
            }
        ]
        
        for rule_data in rules:
            if not frappe.db.exists('CRM Automation Rule', rule_data['rule_name']):
                rule = frappe.new_doc('CRM Automation Rule')
                rule.rule_name = rule_data['rule_name']
                rule.event = rule_data['event']
                rule.condition = rule_data['condition']
                rule.action = rule_data['action']
                rule.enabled = rule_data['enabled']
                rule.insert()
    
    def execute_automation_rules(self, doctype, docname, event):
        """Execute automation rules for event"""
        rules = frappe.get_all('CRM Automation Rule',
                               filters={'event': event, 'enabled': 1},
                               fields=['name', 'condition', 'action', 'action_data'])
        
        doc = frappe.get_doc(doctype, docname)
        
        for rule in rules:
            try:
                if self.evaluate_rule_condition(doc, rule.condition):
                    self.execute_automation_action(doc, rule)
            except Exception as e:
                frappe.log_error(f"Failed to execute automation rule {rule.name}: {str(e)}")
    
    def evaluate_rule_condition(self, doc, condition):
        """Evaluate automation rule condition"""
        # Simplified condition evaluation
        try:
            # Parse condition (example: "lead_score > 50")
            if '>' in condition:
                field, value = condition.split('>')
                field = field.strip()
                value = value.strip()
                
                doc_value = getattr(doc, field, None)
                if doc_value is not None:
                    return float(doc_value) > float(value)
            
            elif '=' in condition:
                field, value = condition.split('=')
                field = field.strip()
                value = value.strip()
                
                doc_value = getattr(doc, field, None)
                return str(doc_value) == value
            
        except Exception:
            pass
        
        return False
    
    def execute_automation_action(self, doc, rule):
        """Execute automation action"""
        action = rule.action
        action_data = json.loads(rule.action_data or '{}')
        
        if action == 'Assign to Sales Manager':
            self.assign_to_sales_manager(doc, action_data)
        elif action == 'Create Follow Up Task':
            self.create_follow_up_task(doc, action_data)
        elif action == 'Send Email Alert':
            self.send_email_alert(doc, action_data)
        elif action == 'Send Welcome Email':
            self.send_welcome_email(doc, action_data)
    
    def assign_to_sales_manager(self, doc, action_data):
        """Assign document to sales manager"""
        sales_manager = action_data.get('sales_manager', 'sales@example.com')
        
        if doc.doctype == 'Lead':
            frappe.db.set_value('Lead', doc.name, 'lead_owner', sales_manager)
        elif doc.doctype == 'Opportunity':
            frappe.db.set_value('Opportunity', doc.name, 'opportunity_owner', sales_manager)
    
    def create_follow_up_task(self, doc, action_data):
        """Create follow up task"""
        task = frappe.new_doc('Task')
        task.subject = f"Follow up with {doc.lead_name or doc.customer}"
        task.description = action_data.get('description', 'Follow up required')
        task.status = 'Open'
        task.priority = action_data.get('priority', 'High')
        task.reference_doctype = doc.doctype
        task.reference_name = doc.name
        task.assigned_to = action_data.get('assigned_to', frappe.session.user)
        task.due_date = frappe.utils.add_to_date(frappe.utils.now(), days=action_data.get('due_days', 3))
        task.insert()
    
    def send_email_alert(self, doc, action_data):
        """Send email alert"""
        recipients = action_data.get('recipients', [frappe.session.user])
        template = action_data.get('template', 'CRM Alert')
        
        frappe.sendmail(
            recipients=recipients,
            template=template,
            reference_doctype=doc.doctype,
            reference_name=doc.name,
            args=doc.as_dict()
        )
    
    def send_welcome_email(self, doc, action_data):
        """Send welcome email to customer"""
        if doc.email_id:
            template = action_data.get('template', 'Welcome Email')
            
            frappe.sendmail(
                recipients=[doc.email_id],
                template=template,
                reference_doctype=doc.doctype,
                reference_name=doc.name,
                args=doc.as_dict()
            )

# CRM analytics engine
class CRMAnalyticsEngine:
    def __init__(self):
        self.lead_analytics = LeadAnalytics()
        self.opportunity_analytics = OpportunityAnalytics()
        self.customer_analytics = CustomerAnalytics()
        self.sales_analytics = SalesAnalytics()
        self.performance_analytics = PerformanceAnalytics()
    
    def setup_tracking(self):
        """Setup CRM analytics tracking"""
        # Setup lead tracking
        self.lead_analytics.setup_tracking()
        
        # Setup opportunity tracking
        self.opportunity_analytics.setup_tracking()
        
        # Setup customer tracking
        self.customer_analytics.setup_tracking()
        
        # Setup sales tracking
        self.sales_analytics.setup_tracking()
    
    def get_crm_dashboard_data(self, date_range=None):
        """Get comprehensive CRM dashboard data"""
        return {
            'lead_metrics': self.lead_analytics.get_lead_metrics(date_range),
            'opportunity_metrics': self.opportunity_analytics.get_opportunity_metrics(date_range),
            'customer_metrics': self.customer_analytics.get_customer_metrics(date_range),
            'sales_metrics': self.sales_analytics.get_sales_metrics(date_range),
            'performance_metrics': self.performance_analytics.get_performance_metrics(date_range)
        }
    
    def get_conversion_funnel(self, date_range=None):
        """Get CRM conversion funnel"""
        funnel_data = {
            'leads': self.get_leads_count(date_range),
            'qualified_leads': self.get_qualified_leads_count(date_range),
            'opportunities': self.get_opportunities_count(date_range),
            'proposals': self.get_proposals_count(date_range),
            'closed_won': self.get_closed_won_count(date_range),
            'customers': self.get_new_customers_count(date_range)
        }
        
        # Calculate conversion rates
        total_leads = funnel_data['leads']
        if total_leads > 0:
            funnel_data['conversion_rates'] = {
                'lead_to_qualified': (funnel_data['qualified_leads'] / total_leads) * 100,
                'qualified_to_opportunity': (funnel_data['opportunities'] / funnel_data['qualified_leads']) * 100 if funnel_data['qualified_leads'] > 0 else 0,
                'opportunity_to_proposal': (funnel_data['proposals'] / funnel_data['opportunities']) * 100 if funnel_data['opportunities'] > 0 else 0,
                'proposal_to_close': (funnel_data['closed_won'] / funnel_data['proposals']) * 100 if funnel_data['proposals'] > 0 else 0,
                'overall_conversion': (funnel_data['customers'] / total_leads) * 100
            }
        
        return funnel_data
    
    def get_leads_count(self, date_range=None):
        """Get leads count"""
        filters = {'status': 'Lead'}
        if date_range:
            filters['creation'] = ['between', date_range]
        
        return frappe.db.count('Lead', filters)
    
    def get_qualified_leads_count(self, date_range=None):
        """Get qualified leads count"""
        filters = {'status': 'Lead', 'lead_stage': 'Qualified'}
        if date_range:
            filters['creation'] = ['between', date_range]
        
        return frappe.db.count('Lead', filters)
    
    def get_opportunities_count(self, date_range=None):
        """Get opportunities count"""
        filters = {'status': 'Open'}
        if date_range:
            filters['creation'] = ['between', date_range]
        
        return frappe.db.count('Opportunity', filters)
    
    def get_proposals_count(self, date_range=None):
        """Get proposals count"""
        filters = {'docstatus': 0, 'status': 'Submitted'}
        if date_range:
            filters['creation'] = ['between', date_range]
        
        return frappe.db.count('Quotation', filters)
    
    def get_closed_won_count(self, date_range=None):
        """Get closed won opportunities count"""
        filters = {'status': 'Closed Won'}
        if date_range:
            filters['creation'] = ['between', date_range]
        
        return frappe.db.count('Opportunity', filters)
    
    def get_new_customers_count(self, date_range=None):
        """Get new customers count"""
        filters = {}
        if date_range:
            filters['creation'] = ['between', date_range]
        
        return frappe.db.count('Customer', filters)

# Lead analytics
class LeadAnalytics:
    def __init__(self):
        self.tracker = LeadTracker()
    
    def setup_tracking(self):
        """Setup lead analytics tracking"""
        # Track lead creation
        self.track_lead_creation()
        
        # Track lead conversion
        self.track_lead_conversion()
        
        # Track lead source effectiveness
        self.track_source_effectiveness()
    
    def get_lead_metrics(self, date_range=None):
        """Get lead analytics metrics"""
        return {
            'total_leads': self.get_total_leads(date_range),
            'new_leads': self.get_new_leads(date_range),
            'conversion_rate': self.get_lead_conversion_rate(date_range),
            'average_lead_score': self.get_average_lead_score(date_range),
            'lead_sources': self.get_lead_sources_breakdown(date_range),
            'lead_stages': self.get_lead_stages_breakdown(date_range),
            'lead_owner_performance': self.get_lead_owner_performance(date_range)
        }
    
    def get_total_leads(self, date_range=None):
        """Get total leads count"""
        filters = {}
        if date_range:
            filters['creation'] = ['between', date_range]
        
        return frappe.db.count('Lead', filters)
    
    def get_new_leads(self, date_range=None):
        """Get new leads count"""
        filters = {'status': 'Lead'}
        if date_range:
            filters['creation'] = ['between', date_range]
        
        return frappe.db.count('Lead', filters)
    
    def get_lead_conversion_rate(self, date_range=None):
        """Get lead conversion rate"""
        total_leads = self.get_total_leads(date_range)
        converted_leads = self.get_converted_leads_count(date_range)
        
        if total_leads > 0:
            return (converted_leads / total_leads) * 100
        
        return 0
    
    def get_converted_leads_count(self, date_range=None):
        """Get converted leads count"""
        filters = {'status': 'Converted'}
        if date_range:
            filters['conversion_date'] = ['between', date_range]
        
        return frappe.db.count('Lead', filters)
    
    def get_average_lead_score(self, date_range=None):
        """Get average lead score"""
        filters = {}
        if date_range:
            filters['creation'] = ['between', date_range]
        
        result = frappe.db.get_value('Lead', filters, 'AVG(lead_score)')
        return result or 0
    
    def get_lead_sources_breakdown(self, date_range=None):
        """Get lead sources breakdown"""
        filters = {}
        if date_range:
            filters['creation'] = ['between', date_range]
        
        sources = frappe.get_all('Lead',
                                 filters=filters,
                                 fields=['source', 'COUNT(*) as count'],
                                 group_by='source')
        
        return {source.source: source.count for source in sources}
    
    def get_lead_stages_breakdown(self, date_range=None):
        """Get lead stages breakdown"""
        filters = {}
        if date_range:
            filters['creation'] = ['between', date_range]
        
        stages = frappe.get_all('Lead',
                                filters=filters,
                                fields=['lead_stage', 'COUNT(*) as count'],
                                group_by='lead_stage')
        
        return {stage.lead_stage: stage.count for stage in stages}
    
    def get_lead_owner_performance(self, date_range=None):
        """Get lead owner performance"""
        filters = {}
        if date_range:
            filters['creation'] = ['between', date_range]
        
        owners = frappe.get_all('Lead',
                                filters=filters,
                                fields=['lead_owner', 'COUNT(*) as total_leads', 'AVG(lead_score) as avg_score'],
                                group_by='lead_owner')
        
        return {owner.lead_owner: {
            'total_leads': owner.total_leads,
            'average_score': owner.avg_score
        } for owner in owners}
```

### 12.2 Building the CRM Frontend

#### CRM Dashboard and User Interface

```javascript
// CRM frontend application
class CRMFrontend {
    constructor() {
        this.dashboard = new CRMDashboard();
        this.lead_manager = new LeadManagerUI();
        this.opportunity_manager = new OpportunityManagerUI();
        this.customer_manager = new CustomerManagerUI();
        this.communication_center = new CommunicationCenter();
        this.analytics = new CRMAnalyticsUI();
        this.automation = new CRMAutomationUI();
        
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
            '/leads': 'leads',
            '/lead/:id': 'lead_detail',
            '/opportunities': 'opportunities',
            '/opportunity/:id': 'opportunity_detail',
            '/customers': 'customers',
            '/customer/:id': 'customer_detail',
            '/communications': 'communications',
            '/analytics': 'analytics',
            '/automation': 'automation'
        };
        
        this.router = new Router(this.routes);
        this.router.init();
    }
    
    initialize_components() {
        this.components = {
            sidebar: new CRMSidebar(),
            header: new CRMHeader(),
            dashboard: new CRMDashboard(),
            lead_list: new LeadList(),
            lead_detail: new LeadDetail(),
            opportunity_list: new OpportunityList(),
            customer_list: new CustomerList(),
            communication_center: new CommunicationCenter(),
            analytics: new CRMAnalytics()
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
            case 'leads':
                this.render_leads_page(content_area);
                break;
            case 'lead_detail':
                this.render_lead_detail_page(content_area, route.params);
                break;
            case 'opportunities':
                this.render_opportunities_page(content_area);
                break;
            case 'customers':
                this.render_customers_page(content_area);
                break;
            case 'communications':
                this.render_communications_page(content_area);
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
            <div class="crm-dashboard">
                <div class="dashboard-header">
                    <h1>CRM Dashboard</h1>
                    <div class="date-filter">
                        <select id="date-range" onchange="crm.analytics.update_dashboard(this.value)">
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
                            <i class="fas fa-users"></i>
                        </div>
                        <div class="metric-content">
                            <h3 id="total-leads">0</h3>
                            <p>Total Leads</p>
                            <span class="metric-change positive">+12%</span>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-handshake"></i>
                        </div>
                        <div class="metric-content">
                            <h3 id="total-opportunities">0</h3>
                            <p>Opportunities</p>
                            <span class="metric-change positive">+8%</span>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-chart-line"></i>
                        </div>
                        <div class="metric-content">
                            <h3 id="conversion-rate">0%</h3>
                            <p>Conversion Rate</p>
                            <span class="metric-change negative">-2%</span>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-dollar-sign"></i>
                        </div>
                        <div class="metric-content">
                            <h3 id="pipeline-value">$0</h3>
                            <p>Pipeline Value</p>
                            <span class="metric-change positive">+15%</span>
                        </div>
                    </div>
                </div>
                
                <div class="dashboard-charts">
                    <div class="chart-container">
                        <h3>Lead Conversion Funnel</h3>
                        <div id="conversion-funnel-chart"></div>
                    </div>
                    
                    <div class="chart-container">
                        <h3>Sales Pipeline</h3>
                        <div id="sales-pipeline-chart"></div>
                    </div>
                </div>
                
                <div class="dashboard-tables">
                    <div class="table-container">
                        <h3>Recent Leads</h3>
                        <div id="recent-leads-table"></div>
                    </div>
                    
                    <div class="table-container">
                        <h3>Upcoming Tasks</h3>
                        <div id="upcoming-tasks-table"></div>
                    </div>
                </div>
            </div>
        `;
        
        // Load dashboard data
        this.load_dashboard_data();
    }
    
    async load_dashboard_data() {
        try {
            const response = await fetch('/api/method/crm.api.get_dashboard_data');
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
        document.getElementById('total-leads').textContent = data.lead_metrics.total_leads;
        document.getElementById('total-opportunities').textContent = data.opportunity_metrics.total_opportunities;
        document.getElementById('conversion-rate').textContent = data.lead_metrics.conversion_rate.toFixed(1) + '%';
        document.getElementById('pipeline-value').textContent = this.format_currency(data.opportunity_metrics.pipeline_value);
    }
    
    render_dashboard_charts(data) {
        // Render conversion funnel chart
        this.render_conversion_funnel(data.conversion_funnel);
        
        // Render sales pipeline chart
        this.render_sales_pipeline(data.opportunity_metrics.stages);
    }
    
    render_conversion_funnel(funnel_data) {
        const container = document.getElementById('conversion-funnel-chart');
        
        const chart_data = {
            labels: ['Leads', 'Qualified', 'Opportunities', 'Proposals', 'Closed Won'],
            datasets: [{
                data: [
                    funnel_data.leads,
                    funnel_data.qualified_leads,
                    funnel_data.opportunities,
                    funnel_data.proposals,
                    funnel_data.closed_won
                ],
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF'
                ]
            }]
        };
        
        // Create funnel chart (simplified example)
        container.innerHTML = `
            <div class="funnel-chart">
                ${chart_data.labels.map((label, index) => `
                    <div class="funnel-step" style="width: ${100 - (index * 15)}%">
                        <div class="funnel-bar" style="background-color: ${chart_data.datasets[0].backgroundColor[index]}">
                            <span class="funnel-label">${label}</span>
                            <span class="funnel-value">${chart_data.datasets[0].data[index]}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    render_sales_pipeline(stages) {
        const container = document.getElementById('sales-pipeline-chart');
        
        container.innerHTML = `
            <div class="pipeline-chart">
                ${stages.map(stage => `
                    <div class="pipeline-stage">
                        <div class="stage-header">
                            <h4>${stage.stage_name}</h4>
                            <span class="stage-count">${stage.count}</span>
                        </div>
                        <div class="stage-value">
                            ${this.format_currency(stage.total_value)}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    render_dashboard_tables(data) {
        // Render recent leads table
        this.render_recent_leads_table(data.recent_leads);
        
        // Render upcoming tasks table
        this.render_upcoming_tasks_table(data.upcoming_tasks);
    }
    
    render_recent_leads_table(leads) {
        const container = document.getElementById('recent-leads-table');
        
        if (leads && leads.length > 0) {
            container.innerHTML = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Company</th>
                            <th>Stage</th>
                            <th>Score</th>
                            <th>Created</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${leads.map(lead => `
                            <tr onclick="crm.lead_manager.view_lead('${lead.name}')">
                                <td>${lead.lead_name}</td>
                                <td>${lead.company_name || '-'}</td>
                                <td><span class="stage-badge ${lead.lead_stage.toLowerCase()}">${lead.lead_stage}</span></td>
                                <td>${lead.lead_score}</td>
                                <td>${this.format_date(lead.creation)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = '<p>No recent leads found</p>';
        }
    }
    
    render_upcoming_tasks_table(tasks) {
        const container = document.getElementById('upcoming-tasks-table');
        
        if (tasks && tasks.length > 0) {
            container.innerHTML = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Task</th>
                            <th>Related To</th>
                            <th>Assigned To</th>
                            <th>Due Date</th>
                            <th>Priority</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tasks.map(task => `
                            <tr>
                                <td>${task.subject}</td>
                                <td>${task.reference_doctype}: ${task.reference_name}</td>
                                <td>${task.assigned_to}</td>
                                <td>${this.format_date(task.due_date)}</td>
                                <td><span class="priority-badge ${task.priority.toLowerCase()}">${task.priority}</span></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        } else {
            container.innerHTML = '<p>No upcoming tasks found</p>';
        }
    }
    
    render_leads_page(container) {
        container.innerHTML = `
            <div class="leads-page">
                <div class="page-header">
                    <h1>Leads</h1>
                    <div class="page-actions">
                        <button class="btn btn-primary" onclick="crm.lead_manager.create_lead()">
                            <i class="fas fa-plus"></i> New Lead
                        </button>
                        <button class="btn btn-secondary" onclick="crm.lead_manager.import_leads()">
                            <i class="fas fa-upload"></i> Import Leads
                        </button>
                    </div>
                </div>
                
                <div class="filters-bar">
                    <div class="filter-group">
                        <select id="stage-filter" onchange="crm.lead_manager.filter_leads()">
                            <option value="">All Stages</option>
                            <option value="New">New</option>
                            <option value="Contacted">Contacted</option>
                            <option value="Qualified">Qualified</option>
                            <option value="Proposal">Proposal</option>
                            <option value="Negotiation">Negotiation</option>
                            <option value="Converted">Converted</option>
                            <option value="Lost">Lost</option>
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <select id="owner-filter" onchange="crm.lead_manager.filter_leads()">
                            <option value="">All Owners</option>
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <select id="source-filter" onchange="crm.lead_manager.filter_leads()">
                            <option value="">All Sources</option>
                            <option value="Website">Website</option>
                            <option value="Email">Email</option>
                            <option value="Phone">Phone</option>
                            <option value="Referral">Referral</option>
                            <option value="Advertisement">Advertisement</option>
                        </select>
                    </div>
                    
                    <div class="filter-group search-group">
                        <input type="text" placeholder="Search leads..." 
                               onkeyup="crm.lead_manager.search_leads(this.value)">
                        <button onclick="crm.lead_manager.search_leads(document.getElementById('search-input').value)">
                            <i class="fas fa-search"></i>
                        </button>
                    </div>
                </div>
                
                <div class="leads-list" id="leads-list">
                    <!-- Leads will be loaded here -->
                </div>
                
                <div class="pagination" id="leads-pagination">
                    <!-- Pagination will be loaded here -->
                </div>
            </div>
        `;
        
        // Load leads
        this.load_leads();
    }
    
    async load_leads(filters = {}) {
        try {
            const params = new URLSearchParams(filters);
            const response = await fetch(`/api/method/crm.api.get_leads?${params}`);
            const data = await response.json();
            
            if (data.message) {
                this.render_leads_list(data.message.leads);
                this.setup_pagination(data.message.total_count, data.message.page, data.message.per_page);
            }
            
        } catch (error) {
            console.error('Error loading leads:', error);
        }
    }
    
    render_leads_list(leads) {
        const container = document.getElementById('leads-list');
        
        if (leads && leads.length > 0) {
            container.innerHTML = `
                <div class="leads-grid">
                    ${leads.map(lead => `
                        <div class="lead-card" onclick="crm.lead_manager.view_lead('${lead.name}')">
                            <div class="lead-header">
                                <h3>${lead.lead_name}</h3>
                                <span class="stage-badge ${lead.lead_stage.toLowerCase()}">${lead.lead_stage}</span>
                            </div>
                            
                            <div class="lead-info">
                                <p><strong>Company:</strong> ${lead.company_name || '-'}</p>
                                <p><strong>Email:</strong> ${lead.email_id || '-'}</p>
                                <p><strong>Phone:</strong> ${lead.phone || '-'}</p>
                                <p><strong>Source:</strong> ${lead.source}</p>
                            </div>
                            
                            <div class="lead-metrics">
                                <div class="metric">
                                    <span class="metric-label">Score</span>
                                    <span class="metric-value">${lead.lead_score}</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Owner</span>
                                    <span class="metric-value">${lead.lead_owner}</span>
                                </div>
                            </div>
                            
                            <div class="lead-actions">
                                <button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); crm.lead_manager.edit_lead('${lead.name}')">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-secondary" onclick="event.stopPropagation(); crm.communication_center.send_email('${lead.name}')">
                                    <i class="fas fa-envelope"></i>
                                </button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            container.innerHTML = '<div class="empty-state"><p>No leads found</p></div>';
        }
    }
    
    render_lead_detail_page(container, params) {
        const lead_id = params.id;
        
        container.innerHTML = `
            <div class="lead-detail-page">
                <div class="detail-header">
                    <div class="header-left">
                        <button class="btn btn-secondary" onclick="crm.router.navigate('/leads')">
                            <i class="fas fa-arrow-left"></i> Back to Leads
                        </button>
                    </div>
                    <div class="header-right">
                        <button class="btn btn-primary" onclick="crm.lead_manager.convert_lead('${lead_id}')">
                            <i class="fas fa-check"></i> Convert to Customer
                        </button>
                        <button class="btn btn-secondary" onclick="crm.lead_manager.edit_lead('${lead_id}')">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                    </div>
                </div>
                
                <div class="lead-content">
                    <div class="lead-main-info">
                        <div class="lead-basic-info">
                            <h1 id="lead-name"></h1>
                            <div class="lead-meta">
                                <span class="stage-badge" id="lead-stage"></span>
                                <span class="lead-score" id="lead-score"></span>
                                <span class="lead-owner" id="lead-owner"></span>
                            </div>
                        </div>
                        
                        <div class="lead-contact-info">
                            <div class="contact-item">
                                <i class="fas fa-building"></i>
                                <span id="company-name"></span>
                            </div>
                            <div class="contact-item">
                                <i class="fas fa-envelope"></i>
                                <span id="email-id"></span>
                            </div>
                            <div class="contact-item">
                                <i class="fas fa-phone"></i>
                                <span id="phone"></span>
                            </div>
                            <div class="contact-item">
                                <i class="fas fa-globe"></i>
                                <span id="website"></span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="lead-tabs">
                        <div class="tab-nav">
                            <button class="tab-btn active" onclick="crm.lead_manager.show_tab('details')">
                                Details
                            </button>
                            <button class="tab-btn" onclick="crm.lead_manager.show_tab('activities')">
                                Activities
                            </button>
                            <button class="tab-btn" onclick="crm.lead_manager.show_tab('communications')">
                                Communications
                            </button>
                            <button class="tab-btn" onclick="crm.lead_manager.show_tab('tasks')">
                                Tasks
                            </button>
                            <button class="tab-btn" onclick="crm.lead_manager.show_tab('notes')">
                                Notes
                            </button>
                        </div>
                        
                        <div class="tab-content">
                            <div class="tab-pane active" id="details-tab">
                                <div class="lead-details-content">
                                    <!-- Lead details will be loaded here -->
                                </div>
                            </div>
                            <div class="tab-pane" id="activities-tab">
                                <div class="activities-content">
                                    <!-- Activities will be loaded here -->
                                </div>
                            </div>
                            <div class="tab-pane" id="communications-tab">
                                <div class="communications-content">
                                    <!-- Communications will be loaded here -->
                                </div>
                            </div>
                            <div class="tab-pane" id="tasks-tab">
                                <div class="tasks-content">
                                    <!-- Tasks will be loaded here -->
                                </div>
                            </div>
                            <div class="tab-pane" id="notes-tab">
                                <div class="notes-content">
                                    <!-- Notes will be loaded here -->
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Load lead details
        this.load_lead_detail(lead_id);
    }
    
    async load_lead_detail(lead_id) {
        try {
            const response = await fetch(`/api/method/crm.api.get_lead_details?lead_id=${lead_id}`);
            const data = await response.json();
            
            if (data.message) {
                this.update_lead_detail(data.message);
                this.load_lead_activities(lead_id);
                this.load_lead_communications(lead_id);
                this.load_lead_tasks(lead_id);
                this.load_lead_notes(lead_id);
            }
            
        } catch (error) {
            console.error('Error loading lead details:', error);
        }
    }
    
    update_lead_detail(lead) {
        // Update basic information
        document.getElementById('lead-name').textContent = lead.lead_name;
        document.getElementById('lead-stage').textContent = lead.lead_stage;
        document.getElementById('lead-score').textContent = `Score: ${lead.lead_score}`;
        document.getElementById('lead-owner').textContent = lead.lead_owner;
        
        // Update contact information
        document.getElementById('company-name').textContent = lead.company_name || '-';
        document.getElementById('email-id').textContent = lead.email_id || '-';
        document.getElementById('phone').textContent = lead.phone || '-';
        document.getElementById('website').textContent = lead.website || '-';
        
        // Update details tab
        const details_content = document.querySelector('#details-tab .lead-details-content');
        details_content.innerHTML = `
            <div class="details-grid">
                <div class="detail-group">
                    <h3>Basic Information</h3>
                    <div class="detail-item">
                        <label>Status</label>
                        <span>${lead.status}</span>
                    </div>
                    <div class="detail-item">
                        <label>Source</label>
                        <span>${lead.source}</span>
                    </div>
                    <div class="detail-item">
                        <label>Created</label>
                        <span>${this.format_date(lead.creation)}</span>
                    </div>
                    <div class="detail-item">
                        <label>Modified</label>
                        <span>${this.format_date(lead.modified)}</span>
                    </div>
                </div>
                
                <div class="detail-group">
                    <h3>Address Information</h3>
                    <div class="detail-item">
                        <label>Address Line 1</label>
                        <span>${lead.address_line1 || '-'}</span>
                    </div>
                    <div class="detail-item">
                        <label>City</label>
                        <span>${lead.city || '-'}</span>
                    </div>
                    <div class="detail-item">
                        <label>State</label>
                        <span>${lead.state || '-'}</span>
                    </div>
                    <div class="detail-item">
                        <label>Country</label>
                        <span>${lead.country || '-'}</span>
                    </div>
                </div>
                
                <div class="detail-group">
                    <h3>Additional Information</h3>
                    <div class="detail-item">
                        <label>Industry</label>
                        <span>${lead.industry || '-'}</span>
                    </div>
                    <div class="detail-item">
                        <label>Annual Revenue</label>
                        <span>${lead.annual_revenue ? this.format_currency(lead.annual_revenue) : '-'}</span>
                    </div>
                    <div class="detail-item">
                        <label>Employees</label>
                        <span>${lead.employees || '-'}</span>
                    </div>
                    <div class="detail-item">
                        <label>Notes</label>
                        <span>${lead.notes || '-'}</span>
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
        document.addEventListener('lead:updated', (event) => {
            this.handle_lead_update(event.detail);
        });
        
        document.addEventListener('opportunity:updated', (event) => {
            this.handle_opportunity_update(event.detail);
        });
        
        document.addEventListener('customer:updated', (event) => {
            this.handle_customer_update(event.detail);
        });
    }
    
    handle_lead_update(lead_data) {
        // Update UI when lead is updated
        if (this.current_page === 'leads') {
            this.load_leads();
        } else if (this.current_page === 'lead_detail' && this.current_lead_id === lead_data.name) {
            this.load_lead_detail(lead_data.name);
        }
    }
    
    handle_opportunity_update(opportunity_data) {
        // Update UI when opportunity is updated
        if (this.current_page === 'opportunities') {
            this.load_opportunities();
        }
    }
    
    handle_customer_update(customer_data) {
        // Update UI when customer is updated
        if (this.current_page === 'customers') {
            this.load_customers();
        }
    }
}

// Initialize CRM application
let crm;

document.addEventListener('DOMContentLoaded', () => {
    crm = new CRMFrontend();
});
```

### 12.3 Performance Optimization and Analytics

#### High-Performance CRM Patterns

```python
# CRM performance optimization
class CRMPerformanceOptimizer:
    def __init__(self):
        self.cache_manager = CRMCacheManager()
        self.query_optimizer = CRMQueryOptimizer()
        self.index_manager = CRMIndexManager()
        self.batch_processor = CRMBatchProcessor()
        self.analytics_optimizer = CRMAnalyticsOptimizer()
    
    def optimize_crm_performance(self):
        """Optimize overall CRM performance"""
        # Optimize database queries
        self.query_optimizer.optimize_lead_queries()
        self.query_optimizer.optimize_opportunity_queries()
        self.query_optimizer.optimize_customer_queries()
        
        # Setup caching
        self.cache_manager.setup_crm_cache()
        
        # Optimize indexes
        self.index_manager.optimize_database_indexes()
        
        # Setup batch processing
        self.batch_processor.setup_batch_operations()
        
        # Optimize analytics
        self.analytics_optimizer.optimize_analytics_queries()
    
    def optimize_lead_performance(self):
        """Optimize lead-specific performance"""
        # Cache lead data
        self.cache_manager.setup_lead_cache()
        
        # Optimize lead scoring
        self.optimize_lead_scoring()
        
        # Optimize lead routing
        self.optimize_lead_routing()
    
    def optimize_opportunity_performance(self):
        """Optimize opportunity-specific performance"""
        # Cache opportunity data
        self.cache_manager.setup_opportunity_cache()
        
        # Optimize forecasting
        self.optimize_opportunity_forecasting()
        
        # Optimize competition tracking
        self.optimize_competition_tracking()
    
    def optimize_communication_performance(self):
        """Optimize communication performance"""
        # Cache communication templates
        self.cache_manager.setup_communication_cache()
        
        # Optimize email sending
        self.optimize_email_delivery()
        
        # Optimize activity tracking
        self.optimize_activity_tracking()

# Advanced CRM analytics
class AdvancedCRMAnalytics:
    def __init__(self):
        self.predictive_analytics = PredictiveAnalytics()
        self.customer_segmentation = CustomerSegmentation()
        self.churn_prediction = ChurnPrediction()
        self.sentiment_analysis = SentimentAnalysis()
        self.revenue_attribution = RevenueAttribution()
    
    def get_predictive_insights(self, date_range=None):
        """Get predictive analytics insights"""
        return {
            'lead_conversion_probability': self.predictive_analytics.predict_lead_conversion(date_range),
            'opportunity_win_probability': self.predictive_analytics.predict_opportunity_win(date_range),
            'customer_churn_risk': self.churn_prediction.predict_churn_risk(date_range),
            'revenue_forecast': self.predictive_analytics.forecast_revenue(date_range)
        }
    
    def get_customer_segments(self):
        """Get customer segmentation analysis"""
        segments = self.customer_segmentation.segment_customers()
        
        return {
            'segments': segments,
            'segment_sizes': self.get_segment_sizes(segments),
            'segment_characteristics': self.get_segment_characteristics(segments),
            'segment_recommendations': self.get_segment_recommendations(segments)
        }
    
    def get_communication_effectiveness(self, date_range=None):
        """Get communication effectiveness analytics"""
        return {
            'email_open_rates': self.get_email_open_rates(date_range),
            'email_click_rates': self.get_email_click_rates(date_range),
            'call_effectiveness': self.get_call_effectiveness(date_range),
            'meeting_conversion_rates': self.get_meeting_conversion_rates(date_range),
            'best_performing_channels': self.get_best_performing_channels(date_range)
        }
    
    def get_sales_team_performance(self, date_range=None):
        """Get sales team performance analytics"""
        return {
            'individual_performance': self.get_individual_performance(date_range),
            'team_comparison': self.get_team_comparison(date_range),
            'performance_trends': self.get_performance_trends(date_range),
            'coaching_opportunities': self.get_coaching_opportunities(date_range),
            'top_performers': self.get_top_performers(date_range)
        }

# Predictive analytics engine
class PredictiveAnalytics:
    def __init__(self):
        self.ml_models = {}
        self.feature_extractor = FeatureExtractor()
        self.model_trainer = ModelTrainer()
        self.model_evaluator = ModelEvaluator()
    
    def predict_lead_conversion(self, date_range=None):
        """Predict lead conversion probability"""
        # Get historical lead data
        leads_data = self.get_historical_leads_data(date_range)
        
        # Extract features
        features = self.feature_extractor.extract_lead_features(leads_data)
        
        # Load or train model
        model = self.get_or_train_conversion_model(features)
        
        # Make predictions
        predictions = model.predict_proba(features)
        
        return {
            'predictions': predictions,
            'confidence_scores': self.calculate_confidence_scores(predictions),
            'feature_importance': model.feature_importances_,
            'model_accuracy': self.model_evaluator.evaluate_model(model, features)
        }
    
    def predict_opportunity_win(self, date_range=None):
        """Predict opportunity win probability"""
        # Get historical opportunity data
        opportunities_data = self.get_historical_opportunities_data(date_range)
        
        # Extract features
        features = self.feature_extractor.extract_opportunity_features(opportunities_data)
        
        # Load or train model
        model = self.get_or_train_win_model(features)
        
        # Make predictions
        predictions = model.predict_proba(features)
        
        return {
            'predictions': predictions,
            'confidence_scores': self.calculate_confidence_scores(predictions),
            'key_factors': self.get_key_opportunity_factors(model),
            'model_accuracy': self.model_evaluator.evaluate_model(model, features)
        }
    
    def forecast_revenue(self, date_range=None):
        """Forecast revenue based on pipeline"""
        # Get current pipeline data
        pipeline_data = self.get_current_pipeline_data()
        
        # Get historical conversion rates
        conversion_rates = self.get_historical_conversion_rates(date_range)
        
        # Apply time series forecasting
        forecast = self.apply_time_series_forecasting(pipeline_data, conversion_rates)
        
        return {
            'forecast': forecast,
            'confidence_intervals': self.calculate_confidence_intervals(forecast),
            'seasonal_factors': self.get_seasonal_factors(),
            'trend_analysis': self.get_trend_analysis()
        }
    
    def get_historical_leads_data(self, date_range=None):
        """Get historical leads data for training"""
        filters = {}
        if date_range:
            filters['creation'] = ['between', date_range]
        
        leads = frappe.get_all('Lead',
                               filters=filters,
                               fields=['name', 'lead_name', 'email_id', 'phone', 'source', 
                                      'lead_stage', 'lead_score', 'status', 'creation',
                                      'company_name', 'industry', 'annual_revenue'])
        
        return leads
    
    def get_historical_opportunities_data(self, date_range=None):
        """Get historical opportunities data for training"""
        filters = {}
        if date_range:
            filters['creation'] = ['between', date_range]
        
        opportunities = frappe.get_all('Opportunity',
                                       filters=filters,
                                       fields=['name', 'customer', 'opportunity_amount', 
                                              'opportunity_stage', 'status', 'creation',
                                              'probability', 'closing_date'])
        
        return opportunities
    
    def get_current_pipeline_data(self):
        """Get current sales pipeline data"""
        opportunities = frappe.get_all('Opportunity',
                                       filters={'status': 'Open'},
                                       fields=['name', 'opportunity_amount', 'opportunity_stage', 
                                              'probability', 'closing_date'])
        
        return opportunities
    
    def extract_lead_features(self, leads_data):
        """Extract features from leads data"""
        features = []
        
        for lead in leads_data:
            feature_vector = {
                'lead_score': lead.lead_score or 0,
                'source_encoded': self.encode_categorical(lead.source),
                'has_email': 1 if lead.email_id else 0,
                'has_phone': 1 if lead.phone else 0,
                'has_company': 1 if lead.company_name else 0,
                'days_since_creation': self.calculate_days_since(lead.creation),
                'industry_encoded': self.encode_categorical(lead.industry),
                'revenue_range': self.categorize_revenue(lead.annual_revenue)
            }
            
            features.append(feature_vector)
        
        return features
    
    def extract_opportunity_features(self, opportunities_data):
        """Extract features from opportunities data"""
        features = []
        
        for opp in opportunities_data:
            feature_vector = {
                'opportunity_amount': opp.opportunity_amount or 0,
                'probability': opp.probability or 0,
                'days_to_close': self.calculate_days_to_close(opp.closing_date),
                'stage_encoded': self.encode_categorical(opp.opportunity_stage),
                'amount_range': self.categorize_amount(opp.opportunity_amount),
                'quarter_created': self.get_quarter(opp.creation)
            }
            
            features.append(feature_vector)
        
        return features
    
    def encode_categorical(self, value):
        """Encode categorical variables"""
        if not value:
            return 0
        
        # Simple encoding - in practice, use more sophisticated encoding
        encoding_map = {
            'Website': 1,
            'Email': 2,
            'Phone': 3,
            'Referral': 4,
            'Advertisement': 5
        }
        
        return encoding_map.get(value, 0)
    
    def calculate_days_since(self, date_string):
        """Calculate days since given date"""
        if not date_string:
            return 0
        
        date = frappe.utils.getdate(date_string)
        today = frappe.utils.today()
        
        return (today - date).days
    
    def calculate_days_to_close(self, closing_date):
        """Calculate days until closing date"""
        if not closing_date:
            return 0
        
        date = frappe.utils.getdate(closing_date)
        today = frappe.utils.today()
        
        return (date - today).days
    
    def categorize_revenue(self, revenue):
        """Categorize annual revenue"""
        if not revenue:
            return 0
        
        revenue = float(revenue)
        
        if revenue < 100000:
            return 1  # Small
        elif revenue < 1000000:
            return 2  # Medium
        elif revenue < 10000000:
            return 3  # Large
        else:
            return 4  # Enterprise
    
    def categorize_amount(self, amount):
        """Categorize opportunity amount"""
        if not amount:
            return 0
        
        amount = float(amount)
        
        if amount < 1000:
            return 1  # Small
        elif amount < 10000:
            return 2  # Medium
        elif amount < 100000:
            return 3  # Large
        else:
            return 4  # Enterprise
    
    def get_quarter(self, date_string):
        """Get quarter from date"""
        if not date_string:
            return 0
        
        date = frappe.utils.getdate(date_string)
        month = date.month
        
        if month <= 3:
            return 1  # Q1
        elif month <= 6:
            return 2  # Q2
        elif month <= 9:
            return 3  # Q3
        else:
            return 4  # Q4

# Customer segmentation engine
class CustomerSegmentation:
    def __init__(self):
        self.clustering_algorithms = ClusteringAlgorithms()
        self.segment_analyzer = SegmentAnalyzer()
        self.personalization_engine = PersonalizationEngine()
    
    def segment_customers(self):
        """Segment customers using various criteria"""
        # Get customer data
        customers_data = self.get_customers_data()
        
        # Extract features for clustering
        features = self.extract_customer_features(customers_data)
        
        # Apply clustering algorithms
        segments = self.clustering_algorithms.cluster_customers(features)
        
        # Analyze segments
        segment_analysis = self.segment_analyzer.analyze_segments(segments, customers_data)
        
        return {
            'segments': segments,
            'analysis': segment_analysis,
            'recommendations': self.get_segment_recommendations(segments)
        }
    
    def get_customers_data(self):
        """Get customer data for segmentation"""
        customers = frappe.get_all('Customer',
                                   fields=['name', 'customer_name', 'customer_group', 'territory',
                                          'total_billing', 'total_unpaid', 'creation',
                                          'email_id', 'phone'])
        
        # Get additional data
        for customer in customers:
            # Get order history
            customer['order_count'] = frappe.db.count('Sales Order', {'customer': customer.name})
            
            # Get average order value
            if customer['total_billing'] and customer['order_count'] > 0:
                customer['avg_order_value'] = customer['total_billing'] / customer['order_count']
            else:
                customer['avg_order_value'] = 0
            
            # Get days since first order
            customer['days_as_customer'] = self.calculate_days_since(customer['creation'])
        
        return customers
    
    def extract_customer_features(self, customers_data):
        """Extract features for customer segmentation"""
        features = []
        
        for customer in customers_data:
            feature_vector = {
                'total_revenue': customer['total_billing'] or 0,
                'order_frequency': customer['order_count'] or 0,
                'avg_order_value': customer['avg_order_value'] or 0,
                'days_as_customer': customer['days_as_customer'] or 0,
                'has_email': 1 if customer['email_id'] else 0,
                'has_phone': 1 if customer['phone'] else 0,
                'territory_encoded': self.encode_territory(customer['territory']),
                'customer_group_encoded': self.encode_customer_group(customer['customer_group'])
            }
            
            features.append(feature_vector)
        
        return features
    
    def encode_territory(self, territory):
        """Encode territory for segmentation"""
        if not territory:
            return 0
        
        # Simple encoding - in practice, use more sophisticated encoding
        encoding_map = {
            'North': 1,
            'South': 2,
            'East': 3,
            'West': 4,
            'Central': 5
        }
        
        return encoding_map.get(territory, 0)
    
    def encode_customer_group(self, customer_group):
        """Encode customer group for segmentation"""
        if not customer_group:
            return 0
        
        # Simple encoding - in practice, use more sophisticated encoding
        encoding_map = {
            'Individual': 1,
            'Company': 2,
            'Government': 3,
            'Non-Profit': 4
        }
        
        return encoding_map.get(customer_group, 0)
    
    def get_segment_recommendations(self, segments):
        """Get recommendations for each customer segment"""
        recommendations = {}
        
        for segment_id, segment_data in segments.items():
            segment_characteristics = segment_data['characteristics']
            
            recommendations[segment_id] = {
                'marketing_strategy': self.get_marketing_strategy(segment_characteristics),
                'product_recommendations': self.get_product_recommendations(segment_characteristics),
                'communication_preferences': self.get_communication_preferences(segment_characteristics),
                'pricing_strategy': self.get_pricing_strategy(segment_characteristics)
            }
        
        return recommendations
    
    def get_marketing_strategy(self, characteristics):
        """Get marketing strategy for segment"""
        if characteristics['high_value'] and characteristics['frequent_buyer']:
            return 'VIP treatment with exclusive offers'
        elif characteristics['high_value'] and characteristics['infrequent_buyer']:
            return 'Re-engagement campaigns with personalized offers'
        elif characteristics['low_value'] and characteristics['frequent_buyer']:
            return 'Upselling and cross-selling campaigns'
        else:
            return 'Standard marketing campaigns'
    
    def get_product_recommendations(self, characteristics):
        """Get product recommendations for segment"""
        if characteristics['high_value']:
            return 'Premium products and services'
        elif characteristics['price_sensitive']:
            return 'Value-oriented products and discounts'
        else:
            return 'Standard product catalog'
    
    def get_communication_preferences(self, characteristics):
        """Get communication preferences for segment"""
        if characteristics['tech_savvy']:
            return 'Email and social media campaigns'
        elif characteristics['traditional']:
            return 'Phone and direct mail campaigns'
        else:
            return 'Multi-channel communication approach'
    
    def get_pricing_strategy(self, characteristics):
        """Get pricing strategy for segment"""
        if characteristics['price_insensitive']:
            return 'Premium pricing strategy'
        elif characteristics['price_sensitive']:
            return 'Competitive pricing with discounts'
        else:
            return 'Value-based pricing strategy'
```

## 🛠️ Practical Exercises

### Exercise 12.1: Build a Complete CRM System

Create a full CRM system with:
- Lead management with scoring and routing
- Opportunity tracking with forecasting
- Customer relationship management
- Communication center with email integration
- Task management and automation

### Exercise 12.2: Implement Advanced CRM Features

Add advanced CRM features:
- Predictive analytics for lead conversion
- Customer segmentation and personalization
- Sales team performance tracking
- Automated workflow rules
- Advanced reporting and dashboards

### Exercise 12.3: Optimize CRM Performance

Implement performance optimizations:
- Database query optimization
- Caching strategies for CRM data
- Batch processing for large datasets
- Real-time analytics and reporting
- Mobile-responsive CRM interface

## 🚀 Best Practices

### CRM Architecture

- **Use ERPNext as foundation** for customer and order management
- **Implement proper data modeling** for relationships and hierarchies
- **Design for scalability** with microservices architecture
- **Use role-based access** for data security
- **Implement audit trails** for compliance

### Performance Optimization

- **Cache frequently accessed data** like customer information
- **Optimize database queries** with proper indexing
- **Use batch processing** for large data operations
- **Implement real-time updates** for critical data
- **Monitor performance** with analytics and alerts

### User Experience

- **Design intuitive interfaces** for sales teams
- **Provide mobile access** for field sales
- **Implement automation** to reduce manual work
- **Use visual dashboards** for quick insights
- **Provide training and support** for user adoption

## 📖 Further Reading

- [ERPNext CRM Documentation](https://erpnext.com/docs/user/en/crm)
- [CRM Best Practices](https://www.hubspot.com/crm-best-practices)
- [Sales Analytics](https://www.salesforce.com/products/analytics/)
- [Customer Relationship Management](https://en.wikipedia.org/wiki/Customer_relationship_management)

## 🎯 Chapter Summary

Building a complete CRM system requires:

- **CRM Architecture** provides the foundation for customer relationship management
- **Lead Management** enables effective lead tracking and conversion
- **Opportunity Tracking** creates comprehensive sales pipeline management
- **Communication Center** ensures consistent customer interactions
- **Analytics & Automation** delivers insights and efficiency improvements

---

**Next Chapter**: Project management system with task automation and reporting.
