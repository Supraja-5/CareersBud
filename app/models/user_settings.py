# app/models/user_settings.py
from datetime import datetime
from app.extensions import db
import json

class UserSettings(db.Model):
    """Comprehensive user settings model for CareersBud"""
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Career Preferences
    job_search_active = db.Column(db.Boolean, default=False)
    desired_roles = db.Column(db.JSON)  # Array of desired job roles
    preferred_locations = db.Column(db.JSON)  # Array of preferred locations
    work_type_preference = db.Column(db.String(20), default='hybrid')  # remote, hybrid, onsite, flexible
    salary_range_min = db.Column(db.Integer)
    salary_range_max = db.Column(db.Integer)
    salary_currency = db.Column(db.String(10), default='USD')
    career_goal = db.Column(db.String(50))  # find_job, career_change, skill_development, etc.
    career_timeline = db.Column(db.String(20))  # immediate, short_term, medium_term, long_term
    career_interests = db.Column(db.Text)
    
    # Privacy & Visibility Settings
    profile_visibility = db.Column(db.String(20), default='members')  # public, members, connections, recruiters, private
    recruiter_visibility = db.Column(db.Boolean, default=True)
    job_recommendations = db.Column(db.Boolean, default=True)
    salary_insights = db.Column(db.Boolean, default=True)
    show_email = db.Column(db.Boolean, default=True)
    show_phone = db.Column(db.Boolean, default=False)
    show_location = db.Column(db.Boolean, default=True)
    show_current_company = db.Column(db.Boolean, default=True)
    
    # Contact Preferences
    contact_preference = db.Column(db.String(20), default='members')  # everyone, members, recruiters, connections, no_one
    allow_recruiter_messages = db.Column(db.Boolean, default=True)
    allow_networking_requests = db.Column(db.Boolean, default=True)
    
    # Data Sharing Preferences
    analytics_sharing = db.Column(db.Boolean, default=False)
    marketing_communications = db.Column(db.Boolean, default=False)
    third_party_sharing = db.Column(db.Boolean, default=False)
    profile_analytics = db.Column(db.Boolean, default=True)
    
    # Notification Settings - Email
    email_job_alerts = db.Column(db.Boolean, default=True)
    email_application_updates = db.Column(db.Boolean, default=True)
    email_profile_views = db.Column(db.Boolean, default=False)
    email_network_updates = db.Column(db.Boolean, default=False)
    email_messages = db.Column(db.Boolean, default=True)
    email_career_tips = db.Column(db.Boolean, default=False)
    email_weekly_digest = db.Column(db.Boolean, default=False)
    email_product_updates = db.Column(db.Boolean, default=False)
    
    # Notification Settings - Push
    push_messages = db.Column(db.Boolean, default=True)
    push_job_matches = db.Column(db.Boolean, default=True)
    push_application_updates = db.Column(db.Boolean, default=False)
    push_profile_views = db.Column(db.Boolean, default=False)
    push_connection_requests = db.Column(db.Boolean, default=True)
    push_urgent_opportunities = db.Column(db.Boolean, default=False)
    
    # Notification Schedule
    enable_quiet_hours = db.Column(db.Boolean, default=False)
    quiet_hours_start = db.Column(db.Time)
    quiet_hours_end = db.Column(db.Time)
    notification_frequency = db.Column(db.String(20), default='instant')  # instant, hourly, daily, weekly
    
    # Appearance Settings
    theme = db.Column(db.String(20), default='light')  # light, dark, auto
    accent_color = db.Column(db.String(20), default='purple')  # purple, blue, green, orange
    font_size = db.Column(db.String(20), default='medium')  # small, medium, large, xl
    sidebar_behavior = db.Column(db.String(20), default='always_open')  # auto, always_open, always_collapsed
    reduced_motion = db.Column(db.Boolean, default=False)
    compact_view = db.Column(db.Boolean, default=False)
    auto_refresh = db.Column(db.Boolean, default=True)
    
    # Language & Region Settings
    display_language = db.Column(db.String(10), default='en')
    job_listing_languages = db.Column(db.JSON)  # Array of preferred languages
    timezone = db.Column(db.String(50), default='UTC-5')
    date_format = db.Column(db.String(20), default='MM/DD/YYYY')
    time_format = db.Column(db.String(10), default='12')  # 12, 24
    currency = db.Column(db.String(10), default='USD')
    
    # Data Management Settings
    activity_retention_days = db.Column(db.Integer, default=90)
    search_retention_days = db.Column(db.Integer, default=180)
    auto_save_searches = db.Column(db.Boolean, default=True)
    
    # Security Settings
    two_factor_enabled = db.Column(db.Boolean, default=False)
    login_alerts = db.Column(db.Boolean, default=True)
    password_alerts = db.Column(db.Boolean, default=True)
    profile_view_alerts = db.Column(db.Boolean, default=False)
    
    # Advanced Settings
    developer_mode = db.Column(db.Boolean, default=False)
    console_logs = db.Column(db.Boolean, default=False)
    beta_features = db.Column(db.Boolean, default=False)
    job_load_speed = db.Column(db.String(20), default='fast')  # fast, balanced, detailed
    search_results_per_page = db.Column(db.Integer, default=25)
    preload_content = db.Column(db.Boolean, default=True)
    
    # Experimental Features
    ai_resume_builder = db.Column(db.Boolean, default=False)
    smart_job_matching = db.Column(db.Boolean, default=False)
    interview_simulator = db.Column(db.Boolean, default=False)
    
    # Integration Settings (JSON fields for flexibility)
    connected_accounts = db.Column(db.JSON, default=dict)  # {linkedin: {connected: True, data: {}}, etc.}
    api_key = db.Column(db.String(100))
    webhook_url = db.Column(db.String(255))
    webhook_events = db.Column(db.JSON, default=list)  # Array of enabled webhook events
    
    # Relationships
    user = db.relationship('User', backref=db.backref('settings', uselist=False, cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<UserSettings for User {self.user_id}>'
    
    @classmethod
    def get_or_create(cls, user_id):
        """Get existing settings or create new with defaults"""
        settings = cls.query.filter_by(user_id=user_id).first()
        if not settings:
            settings = cls(user_id=user_id)
            db.session.add(settings)
            db.session.commit()
        return settings
    
    def to_dict(self):
        """Convert settings to dictionary for JSON serialization"""
        return {
            'career_preferences': {
                'job_search_active': self.job_search_active,
                'desired_roles': self.desired_roles or [],
                'preferred_locations': self.preferred_locations or [],
                'work_type_preference': self.work_type_preference,
                'salary_range_min': self.salary_range_min,
                'salary_range_max': self.salary_range_max,
                'salary_currency': self.salary_currency,
                'career_goal': self.career_goal,
                'career_timeline': self.career_timeline,
                'career_interests': self.career_interests,
            },
            'privacy': {
                'profile_visibility': self.profile_visibility,
                'recruiter_visibility': self.recruiter_visibility,
                'job_recommendations': self.job_recommendations,
                'salary_insights': self.salary_insights,
                'show_email': self.show_email,
                'show_phone': self.show_phone,
                'show_location': self.show_location,
                'show_current_company': self.show_current_company,
                'contact_preference': self.contact_preference,
                'allow_recruiter_messages': self.allow_recruiter_messages,
                'allow_networking_requests': self.allow_networking_requests,
                'analytics_sharing': self.analytics_sharing,
                'marketing_communications': self.marketing_communications,
                'third_party_sharing': self.third_party_sharing,
                'profile_analytics': self.profile_analytics,
            },
            'notifications': {
                'email': {
                    'job_alerts': self.email_job_alerts,
                    'application_updates': self.email_application_updates,
                    'profile_views': self.email_profile_views,
                    'network_updates': self.email_network_updates,
                    'messages': self.email_messages,
                    'career_tips': self.email_career_tips,
                    'weekly_digest': self.email_weekly_digest,
                    'product_updates': self.email_product_updates,
                },
                'push': {
                    'messages': self.push_messages,
                    'job_matches': self.push_job_matches,
                    'application_updates': self.push_application_updates,
                    'profile_views': self.push_profile_views,
                    'connection_requests': self.push_connection_requests,
                    'urgent_opportunities': self.push_urgent_opportunities,
                },
                'schedule': {
                    'enable_quiet_hours': self.enable_quiet_hours,
                    'quiet_hours_start': self.quiet_hours_start.strftime('%H:%M') if self.quiet_hours_start else None,
                    'quiet_hours_end': self.quiet_hours_end.strftime('%H:%M') if self.quiet_hours_end else None,
                    'notification_frequency': self.notification_frequency,
                }
            },
            'appearance': {
                'theme': self.theme,
                'accent_color': self.accent_color,
                'font_size': self.font_size,
                'sidebar_behavior': self.sidebar_behavior,
                'reduced_motion': self.reduced_motion,
                'compact_view': self.compact_view,
                'auto_refresh': self.auto_refresh,
            },
            'language_region': {
                'display_language': self.display_language,
                'job_listing_languages': self.job_listing_languages or [],
                'timezone': self.timezone,
                'date_format': self.date_format,
                'time_format': self.time_format,
                'currency': self.currency,
            },
            'data_management': {
                'activity_retention_days': self.activity_retention_days,
                'search_retention_days': self.search_retention_days,
                'auto_save_searches': self.auto_save_searches,
            },
            'security': {
                'two_factor_enabled': self.two_factor_enabled,
                'login_alerts': self.login_alerts,
                'password_alerts': self.password_alerts,
                'profile_view_alerts': self.profile_view_alerts,
            },
            'advanced': {
                'developer_mode': self.developer_mode,
                'console_logs': self.console_logs,
                'beta_features': self.beta_features,
                'job_load_speed': self.job_load_speed,
                'search_results_per_page': self.search_results_per_page,
                'preload_content': self.preload_content,
                'experimental': {
                    'ai_resume_builder': self.ai_resume_builder,
                    'smart_job_matching': self.smart_job_matching,
                    'interview_simulator': self.interview_simulator,
                }
            },
            'integrations': {
                'connected_accounts': self.connected_accounts or {},
                'api_key': self.api_key,
                'webhook_url': self.webhook_url,
                'webhook_events': self.webhook_events or [],
            }
        }
    
    def update_from_dict(self, data):
        """Update settings from dictionary"""
        # Career Preferences
        if 'career_preferences' in data:
            cp = data['career_preferences']
            self.job_search_active = cp.get('job_search_active', self.job_search_active)
            self.desired_roles = cp.get('desired_roles', self.desired_roles)
            self.preferred_locations = cp.get('preferred_locations', self.preferred_locations)
            self.work_type_preference = cp.get('work_type_preference', self.work_type_preference)
            self.salary_range_min = cp.get('salary_range_min', self.salary_range_min)
            self.salary_range_max = cp.get('salary_range_max', self.salary_range_max)
            self.salary_currency = cp.get('salary_currency', self.salary_currency)
            self.career_goal = cp.get('career_goal', self.career_goal)
            self.career_timeline = cp.get('career_timeline', self.career_timeline)
            self.career_interests = cp.get('career_interests', self.career_interests)
        
        # Privacy Settings
        if 'privacy' in data:
            p = data['privacy']
            self.profile_visibility = p.get('profile_visibility', self.profile_visibility)
            self.recruiter_visibility = p.get('recruiter_visibility', self.recruiter_visibility)
            self.job_recommendations = p.get('job_recommendations', self.job_recommendations)
            self.salary_insights = p.get('salary_insights', self.salary_insights)
            self.show_email = p.get('show_email', self.show_email)
            self.show_phone = p.get('show_phone', self.show_phone)
            self.show_location = p.get('show_location', self.show_location)
            self.show_current_company = p.get('show_current_company', self.show_current_company)
            self.contact_preference = p.get('contact_preference', self.contact_preference)
            self.allow_recruiter_messages = p.get('allow_recruiter_messages', self.allow_recruiter_messages)
            self.allow_networking_requests = p.get('allow_networking_requests', self.allow_networking_requests)
            self.analytics_sharing = p.get('analytics_sharing', self.analytics_sharing)
            self.marketing_communications = p.get('marketing_communications', self.marketing_communications)
            self.third_party_sharing = p.get('third_party_sharing', self.third_party_sharing)
            self.profile_analytics = p.get('profile_analytics', self.profile_analytics)
        
        # Notification Settings
        if 'notifications' in data:
            n = data['notifications']
            if 'email' in n:
                e = n['email']
                self.email_job_alerts = e.get('job_alerts', self.email_job_alerts)
                self.email_application_updates = e.get('application_updates', self.email_application_updates)
                self.email_profile_views = e.get('profile_views', self.email_profile_views)
                self.email_network_updates = e.get('network_updates', self.email_network_updates)
                self.email_messages = e.get('messages', self.email_messages)
                self.email_career_tips = e.get('career_tips', self.email_career_tips)
                self.email_weekly_digest = e.get('weekly_digest', self.email_weekly_digest)
                self.email_product_updates = e.get('product_updates', self.email_product_updates)
            
            if 'push' in n:
                p = n['push']
                self.push_messages = p.get('messages', self.push_messages)
                self.push_job_matches = p.get('job_matches', self.push_job_matches)
                self.push_application_updates = p.get('application_updates', self.push_application_updates)
                self.push_profile_views = p.get('profile_views', self.push_profile_views)
                self.push_connection_requests = p.get('connection_requests', self.push_connection_requests)
                self.push_urgent_opportunities = p.get('urgent_opportunities', self.push_urgent_opportunities)
            
            if 'schedule' in n:
                s = n['schedule']
                self.enable_quiet_hours = s.get('enable_quiet_hours', self.enable_quiet_hours)
                if s.get('quiet_hours_start'):
                    from datetime import time
                    start_time = s.get('quiet_hours_start').split(':')
                    self.quiet_hours_start = time(int(start_time[0]), int(start_time[1]))
                if s.get('quiet_hours_end'):
                    from datetime import time
                    end_time = s.get('quiet_hours_end').split(':')
                    self.quiet_hours_end = time(int(end_time[0]), int(end_time[1]))
                self.notification_frequency = s.get('notification_frequency', self.notification_frequency)
        
        # Appearance Settings
        if 'appearance' in data:
            a = data['appearance']
            self.theme = a.get('theme', self.theme)
            self.accent_color = a.get('accent_color', self.accent_color)
            self.font_size = a.get('font_size', self.font_size)
            self.sidebar_behavior = a.get('sidebar_behavior', self.sidebar_behavior)
            self.reduced_motion = a.get('reduced_motion', self.reduced_motion)
            self.compact_view = a.get('compact_view', self.compact_view)
            self.auto_refresh = a.get('auto_refresh', self.auto_refresh)
        
        # Language & Region Settings
        if 'language_region' in data:
            lr = data['language_region']
            self.display_language = lr.get('display_language', self.display_language)
            self.job_listing_languages = lr.get('job_listing_languages', self.job_listing_languages)
            self.timezone = lr.get('timezone', self.timezone)
            self.date_format = lr.get('date_format', self.date_format)
            self.time_format = lr.get('time_format', self.time_format)
            self.currency = lr.get('currency', self.currency)
        
        # Data Management Settings
        if 'data_management' in data:
            dm = data['data_management']
            self.activity_retention_days = dm.get('activity_retention_days', self.activity_retention_days)
            self.search_retention_days = dm.get('search_retention_days', self.search_retention_days)
            self.auto_save_searches = dm.get('auto_save_searches', self.auto_save_searches)
        
        # Security Settings
        if 'security' in data:
            s = data['security']
            self.two_factor_enabled = s.get('two_factor_enabled', self.two_factor_enabled)
            self.login_alerts = s.get('login_alerts', self.login_alerts)
            self.password_alerts = s.get('password_alerts', self.password_alerts)
            self.profile_view_alerts = s.get('profile_view_alerts', self.profile_view_alerts)
        
        # Advanced Settings
        if 'advanced' in data:
            a = data['advanced']
            self.developer_mode = a.get('developer_mode', self.developer_mode)
            self.console_logs = a.get('console_logs', self.console_logs)
            self.beta_features = a.get('beta_features', self.beta_features)
            self.job_load_speed = a.get('job_load_speed', self.job_load_speed)
            self.search_results_per_page = a.get('search_results_per_page', self.search_results_per_page)
            self.preload_content = a.get('preload_content', self.preload_content)
            
            if 'experimental' in a:
                exp = a['experimental']
                self.ai_resume_builder = exp.get('ai_resume_builder', self.ai_resume_builder)
                self.smart_job_matching = exp.get('smart_job_matching', self.smart_job_matching)
                self.interview_simulator = exp.get('interview_simulator', self.interview_simulator)
        
        # Integration Settings
        if 'integrations' in data:
            i = data['integrations']
            self.connected_accounts = i.get('connected_accounts', self.connected_accounts)
            self.api_key = i.get('api_key', self.api_key)
            self.webhook_url = i.get('webhook_url', self.webhook_url)
            self.webhook_events = i.get('webhook_events', self.webhook_events)
        
        self.updated_at = datetime.utcnow()
        db.session.commit()


class UserPreference(db.Model):
    """Additional user preferences that don't fit in main settings"""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    preference_key = db.Column(db.String(100), nullable=False)
    preference_value = db.Column(db.Text)
    preference_type = db.Column(db.String(20), default='string')  # string, boolean, integer, json
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint to prevent duplicate preferences per user
    __table_args__ = (db.UniqueConstraint('user_id', 'preference_key'),)
    
    # Relationships
    user = db.relationship('User', backref='preferences')
    
    def __repr__(self):
        return f'<UserPreference {self.preference_key}={self.preference_value}>'
    
    @classmethod
    def get_preference(cls, user_id, key, default=None):
        """Get a specific preference value"""
        pref = cls.query.filter_by(user_id=user_id, preference_key=key).first()
        if not pref:
            return default
        
        # Convert based on type
        if pref.preference_type == 'boolean':
            return pref.preference_value.lower() in ('true', '1', 'yes')
        elif pref.preference_type == 'integer':
            try:
                return int(pref.preference_value)
            except (ValueError, TypeError):
                return default
        elif pref.preference_type == 'json':
            try:
                return json.loads(pref.preference_value)
            except (ValueError, TypeError):
                return default
        else:
            return pref.preference_value
    
    @classmethod
    def set_preference(cls, user_id, key, value, pref_type='string'):
        """Set a preference value"""
        pref = cls.query.filter_by(user_id=user_id, preference_key=key).first()
        
        # Convert value based on type
        if pref_type == 'boolean':
            value = str(bool(value))
        elif pref_type == 'integer':
            value = str(int(value))
        elif pref_type == 'json':
            value = json.dumps(value)
        else:
            value = str(value)
        
        if pref:
            pref.preference_value = value
            pref.preference_type = pref_type
            pref.updated_at = datetime.utcnow()
        else:
            pref = cls(
                user_id=user_id,
                preference_key=key,
                preference_value=value,
                preference_type=pref_type
            )
            db.session.add(pref)
        
        db.session.commit()
        return pref


class UserSession(db.Model):
    """Track user sessions for security monitoring"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    device_info = db.Column(db.Text)  # User agent and device information
    ip_address = db.Column(db.String(45))  # Support IPv6
    location = db.Column(db.String(100))  # Approximate location
    is_active = db.Column(db.Boolean, default=True)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='sessions')
    
    def __repr__(self):
        return f'<UserSession {self.user_id}:{self.device_info[:20]}>'
    
    @classmethod
    def create_session(cls, user_id, session_token, device_info, ip_address, location=None, expires_at=None):
        """Create a new user session"""
        session = cls(
            user_id=user_id,
            session_token=session_token,
            device_info=device_info,
            ip_address=ip_address,
            location=location,
            expires_at=expires_at
        )
        db.session.add(session)
        db.session.commit()
        return session
    
    @classmethod
    def get_active_sessions(cls, user_id):
        """Get all active sessions for a user"""
        return cls.query.filter_by(user_id=user_id, is_active=True).order_by(cls.last_activity.desc()).all()
    
    def terminate_session(self):
        """Terminate this session"""
        self.is_active = False
        db.session.commit()
    
    @classmethod
    def terminate_other_sessions(cls, user_id, current_session_token):
        """Terminate all other sessions for a user"""
        other_sessions = cls.query.filter(
            cls.user_id == user_id,
            cls.session_token != current_session_token,
            cls.is_active == True
        ).all()
        
        for session in other_sessions:
            session.is_active = False
        
        db.session.commit()
        return len(other_sessions)


# Helper functions for settings management
def get_user_settings(user_id):
    """Get comprehensive user settings"""
    return UserSettings.get_or_create(user_id)

def update_user_settings(user_id, settings_data):
    """Update user settings from form data or API request"""
    try:
        settings = UserSettings.get_or_create(user_id)
        settings.update_from_dict(settings_data)
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error updating settings: {e}")
        return False

def reset_user_settings(user_id):
    """Reset user settings to defaults"""
    try:
        settings = UserSettings.query.filter_by(user_id=user_id).first()
        if settings:
            db.session.delete(settings)
            db.session.commit()
        
        # Create new settings with defaults
        new_settings = UserSettings(user_id=user_id)
        db.session.add(new_settings)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error resetting settings: {e}")
        return False

def export_user_data(user_id):
    """Export all user data for GDPR compliance"""
    from app.models import User
    
    user = User.query.get(user_id)
    if not user:
        return None
    
    data = {
        'profile': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'university': user.university,
            'major': user.major,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'subscription_tier': user.subscription_tier,
        },
        'settings': {},
        'preferences': {},
        'activity': {},
        'applications': [],
        'resumes': [],
        'skills': [],
        'achievements': [],
        'connections': [],
        'messages': [],
        'courses': [],
        'goals': [],
        'tasks': []
    }
    
    # Add settings
    settings = UserSettings.query.filter_by(user_id=user_id).first()
    if settings:
        data['settings'] = settings.to_dict()
    
    # Add preferences
    preferences = UserPreference.query.filter_by(user_id=user_id).all()
    data['preferences'] = {pref.preference_key: pref.preference_value for pref in preferences}
    
    # Add job applications
    for app in user.job_applications:
        data['applications'].append({
            'company': app.company,
            'position': app.position,
            'status': app.status,
            'applied_date': app.applied_date.isoformat() if app.applied_date else None,
            'interview_date': app.interview_date.isoformat() if app.interview_date else None,
        })
    
    # Add skills
    for skill in user.skills:
        data['skills'].append({
            'name': skill.name,
            'skill_type': skill.skill_type,
            'level': skill.level,
            'percentage': skill.percentage,
        })
    
    # Add achievements
    for achievement in user.achievements:
        data['achievements'].append({
            'title': achievement.title,
            'date': achievement.date.isoformat() if achievement.date else None,
        })
    
    # Add goals
    for goal in user.goals:
        data['goals'].append({
            'title': goal.title,
            'description': goal.description,
            'goal_type': goal.goal_type,
            'status': goal.status,
            'progress': goal.progress,
            'start_date': goal.start_date.isoformat() if goal.start_date else None,
            'target_date': goal.target_date.isoformat() if goal.target_date else None,
            'completed_at': goal.completed_at.isoformat() if goal.completed_at else None,
        })
    
    return data

def delete_user_account(user_id, confirmation_text):
    """Permanently delete user account and all associated data"""
    if confirmation_text != "DELETE":
        return False, "Invalid confirmation text"
    
    try:
        from app.models import User
        
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        # Delete all related data
        # Settings
        UserSettings.query.filter_by(user_id=user_id).delete()
        UserPreference.query.filter_by(user_id=user_id).delete()
        UserSession.query.filter_by(user_id=user_id).delete()
        
        # This will cascade delete most other related data due to foreign key relationships
        db.session.delete(user)
        db.session.commit()
        
        return True, "Account deleted successfully"
    
    except Exception as e:
        db.session.rollback()
        return False, f"Error deleting account: {str(e)}"

def generate_api_key(user_id):
    """Generate a new API key for the user"""
    import secrets
    import string
    
    # Generate a secure random API key
    alphabet = string.ascii_letters + string.digits
    api_key = 'cb-' + ''.join(secrets.choice(alphabet) for _ in range(32))
    
    # Save to user settings
    settings = UserSettings.get_or_create(user_id)
    settings.api_key = api_key
    db.session.commit()
    
    return api_key

def validate_api_key(api_key):
    """Validate an API key and return associated user"""
    if not api_key or not api_key.startswith('cb-'):
        return None
    
    settings = UserSettings.query.filter_by(api_key=api_key).first()
    return settings.user if settings else None

# Add these imports to your main models.py file
# from app.models.user_settings import UserSettings, UserPreference, UserSession

# Add this to the end of your models.py file to update the User model
def update_user_model():
    """Add settings-related properties to the existing User model"""
    
    def get_settings(self):
        """Get user settings, creating defaults if none exist"""
        return UserSettings.get_or_create(self.id)
    
    def update_profile_extended(self, profile_data):
        """Update extended profile information"""
        # Update basic profile fields
        for key, value in profile_data.items():
            if hasattr(self, key) and key not in ['id', 'password', 'created_at']:
                setattr(self, key, value)
        
        # Update settings if provided
        if 'settings' in profile_data:
            settings = self.get_settings()
            settings.update_from_dict(profile_data['settings'])
        
        db.session.commit()
        return True
    
    def get_career_preferences(self):
        """Get career-related preferences"""
        settings = self.get_settings()
        return {
            'job_search_active': settings.job_search_active,
            'desired_roles': settings.desired_roles or [],
            'preferred_locations': settings.preferred_locations or [],
            'work_type_preference': settings.work_type_preference,
            'salary_range': {
                'min': settings.salary_range_min,
                'max': settings.salary_range_max,
                'currency': settings.salary_currency
            },
            'career_goal': settings.career_goal,
            'career_timeline': settings.career_timeline,
            'career_interests': settings.career_interests,
        }
    
    def is_visible_to_recruiters(self):
        """Check if profile is visible to recruiters"""
        settings = self.get_settings()
        return settings.recruiter_visibility and settings.profile_visibility in ['public', 'recruiters']
    
    def can_be_contacted_by(self, requester_type='member'):
        """Check if user can be contacted by different types of users"""
        settings = self.get_settings()
        
        contact_rules = {
            'everyone': True,
            'members': requester_type in ['member', 'recruiter'],
            'recruiters': requester_type == 'recruiter',
            'connections': requester_type == 'connection',
            'no_one': False
        }
        
        return contact_rules.get(settings.contact_preference, False)
    
    def should_receive_notification(self, notification_type, delivery_method='email'):
        """Check if user should receive a specific type of notification"""
        settings = self.get_settings()
        
        # Check quiet hours
        if settings.enable_quiet_hours and delivery_method == 'push':
            from datetime import datetime, time
            now = datetime.now().time()
            
            if settings.quiet_hours_start and settings.quiet_hours_end:
                start = settings.quiet_hours_start
                end = settings.quiet_hours_end
                
                if start <= end:
                    # Same day range
                    if start <= now <= end:
                        return False
                else:
                    # Overnight range
                    if now >= start or now <= end:
                        return False
        
        # Check specific notification preferences
        notification_key = f"{delivery_method}_{notification_type}"
        return getattr(settings, notification_key, False)
    
    def get_display_preferences(self):
        """Get display/UI preferences"""
        settings = self.get_settings()
        return {
            'theme': settings.theme,
            'accent_color': settings.accent_color,
            'font_size': settings.font_size,
            'sidebar_behavior': settings.sidebar_behavior,
            'reduced_motion': settings.reduced_motion,
            'compact_view': settings.compact_view,
            'language': settings.display_language,
            'timezone': settings.timezone,
            'date_format': settings.date_format,
            'time_format': settings.time_format,
            'currency': settings.currency,
        }
    
    # Add methods to User class
    from app.models import User
    User.get_settings = get_settings
    User.update_profile_extended = update_profile_extended
    User.get_career_preferences = get_career_preferences
    User.is_visible_to_recruiters = is_visible_to_recruiters
    User.can_be_contacted_by = can_be_contacted_by
    User.should_receive_notification = should_receive_notification
    User.get_display_preferences = get_display_preferences

# Call this function after defining your models
update_user_model()