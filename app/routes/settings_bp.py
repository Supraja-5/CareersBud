# app/routes/settings_bp.py - Simplified for Modal Use

from flask import Blueprint, request, jsonify, current_app, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import os
from datetime import datetime

from app.extensions import db, csrf
from app.models import (
    User, UserSettings, UserSession, get_user_settings, 
    update_user_settings, reset_user_settings, export_user_data, 
    delete_user_account, generate_api_key, validate_api_key
)

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

# API Routes for AJAX updates from modal
@settings_bp.route('/api/update', methods=['POST'])
@login_required
def api_update():
    """API endpoint for updating settings via AJAX"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        if update_user_settings(current_user.id, data):
            return jsonify({'success': True, 'message': 'Settings updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update settings'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/api/get')
@login_required
def api_get():
    """API endpoint for getting current settings"""
    try:
        user_settings = get_user_settings(current_user.id)
        return jsonify({
            'success': True,
            'settings': user_settings.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/api/save-all', methods=['POST'])
@login_required
def api_save_all():
    """API endpoint for saving all settings from the modal"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # Get current settings
        settings = get_user_settings(current_user.id)
        
        # Update user profile fields if provided
        if 'profile' in data:
            profile_data = data['profile']
            if 'first_name' in profile_data:
                current_user.first_name = profile_data['first_name']
            if 'last_name' in profile_data:
                current_user.last_name = profile_data['last_name']
            if 'email' in profile_data:
                current_user.email = profile_data['email']
            if 'university' in profile_data:
                current_user.university = profile_data['university']
            if 'major' in profile_data:
                current_user.major = profile_data['major']
        
        # Update settings using the comprehensive update method
        if update_user_settings(current_user.id, data):
            db.session.commit()
            return jsonify({'success': True, 'message': 'All settings saved successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save settings'}), 500
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/api/reset', methods=['POST'])
@login_required
def api_reset():
    """API endpoint for resetting settings to defaults"""
    try:
        if reset_user_settings(current_user.id):
            return jsonify({'success': True, 'message': 'Settings reset to defaults'})
        else:
            return jsonify({'success': False, 'message': 'Failed to reset settings'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/api/export')
@login_required
def api_export():
    """API endpoint for exporting user data"""
    try:
        data = export_user_data(current_user.id)
        if data:
            return jsonify({
                'success': True,
                'data': data,
                'exported_at': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to export data'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/api/delete-account', methods=['POST'])
@login_required
def api_delete_account():
    """API endpoint for deleting user account"""
    try:
        data = request.get_json()
        confirmation = data.get('confirmation', '')
        
        success, message = delete_user_account(current_user.id, confirmation)
        
        if success:
            # Logout user before deleting
            from flask_login import logout_user
            logout_user()
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/api/change-password', methods=['POST'])
@login_required
def api_change_password():
    """API endpoint for changing password"""
    try:
        data = request.get_json()
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Verify current password
        if not check_password_hash(current_user.password, current_password):
            return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400
        
        # Check if new passwords match
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'New passwords do not match'}), 400
        
        # Check password length
        if len(new_password) < 8:
            return jsonify({'success': False, 'message': 'Password must be at least 8 characters long'}), 400
        
        # Update password
        current_user.password = generate_password_hash(new_password)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Password updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/api/generate-api-key', methods=['POST'])
@login_required
def api_generate_key():
    """Generate a new API key for the user"""
    try:
        api_key = generate_api_key(current_user.id)
        return jsonify({
            'success': True,
            'api_key': api_key,
            'message': 'New API key generated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Skills management endpoints
@settings_bp.route('/api/skills/add', methods=['POST'])
@login_required
def add_skill():
    """Add a new skill"""
    try:
        data = request.get_json()
        skill_name = data.get('skill_name', '').strip()
        skill_type = data.get('skill_type', 'technical')
        proficiency = data.get('proficiency', 3)
        
        if not skill_name:
            return jsonify({'success': False, 'message': 'Skill name is required'}), 400
        
        from app.models import Skill
        
        # Check if skill already exists
        existing = Skill.query.filter_by(
            user_id=current_user.id,
            name=skill_name,
            skill_type=skill_type
        ).first()
        
        if existing:
            return jsonify({'success': False, 'message': 'Skill already exists'}), 400
        
        # Create new skill
        skill = Skill(
            user_id=current_user.id,
            name=skill_name,
            skill_type=skill_type,
            level='beginner' if proficiency <= 2 else 'intermediate' if proficiency <= 4 else 'advanced',
            percentage=proficiency * 20  # Convert 1-5 scale to percentage
        )
        
        db.session.add(skill)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Skill added successfully',
            'skill': {
                'id': skill.id,
                'name': skill.name,
                'skill_type': skill.skill_type,
                'level': skill.level,
                'percentage': skill.percentage
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/api/skills/remove/<int:skill_id>', methods=['DELETE'])
@login_required
def remove_skill(skill_id):
    """Remove a skill"""
    try:
        from app.models import Skill
        
        skill = Skill.query.filter_by(id=skill_id, user_id=current_user.id).first()
        if not skill:
            return jsonify({'success': False, 'message': 'Skill not found'}), 404
        
        db.session.delete(skill)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Skill removed successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Profile picture management
@settings_bp.route('/api/profile-picture/upload', methods=['POST'])
@login_required
def upload_profile_picture():
    """Upload a new profile picture"""
    try:
        if 'profile_picture' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['profile_picture']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            filename = f"profile_{current_user.id}_{int(datetime.utcnow().timestamp())}{ext}"
            
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles')
            os.makedirs(upload_path, exist_ok=True)
            
            file_path = os.path.join(upload_path, filename)
            file.save(file_path)
            
            # Update user profile picture
            current_user.profile_picture = filename
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Profile picture updated successfully',
                'filename': filename,
                'url': url_for('static', filename=f'uploads/profiles/{filename}')
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid file type'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/api/profile-picture/remove', methods=['POST'])
@login_required
def remove_profile_picture():
    """Remove the current profile picture"""
    try:
        # Remove file if not default
        if current_user.profile_picture and current_user.profile_picture != 'default_profile.jpg':
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profiles', current_user.profile_picture)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Reset to default
        current_user.profile_picture = 'default_profile.jpg'
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Profile picture removed successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Session management
@settings_bp.route('/api/sessions/get', methods=['GET'])
@login_required
def api_get_sessions():
    """Get active sessions for user"""
    try:
        active_sessions = UserSession.get_active_sessions(current_user.id)
        sessions_data = []
        
        for session in active_sessions:
            sessions_data.append({
                'id': session.id,
                'device_info': session.device_info,
                'ip_address': session.ip_address,
                'location': session.location,
                'last_activity': session.last_activity.isoformat() if session.last_activity else None,
                'created_at': session.created_at.isoformat() if session.created_at else None,
            })
        
        return jsonify({
            'success': True,
            'sessions': sessions_data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/api/sessions/terminate/<int:session_id>', methods=['POST'])
@login_required
def api_terminate_session(session_id):
    """Terminate a specific session"""
    try:
        session = UserSession.query.filter_by(id=session_id, user_id=current_user.id).first()
        if session:
            session.terminate_session()
            return jsonify({'success': True, 'message': 'Session terminated'})
        else:
            return jsonify({'success': False, 'message': 'Session not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/api/sessions/terminate-others', methods=['POST'])
@login_required
def api_terminate_other_sessions():
    """Terminate all other sessions except current"""
    try:
        current_token = request.headers.get('Session-Token', 'current')
        terminated = UserSession.terminate_other_sessions(current_user.id, current_token)
        return jsonify({
            'success': True,
            'message': f'Terminated {terminated} other sessions'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Integration endpoints
@settings_bp.route('/api/integrations/linkedin/connect', methods=['POST'])
@login_required
def connect_linkedin():
    """Connect LinkedIn account (placeholder for OAuth implementation)"""
    try:
        settings = get_user_settings(current_user.id)
        
        connected_accounts = settings.connected_accounts or {}
        connected_accounts['linkedin'] = {
            'connected': True,
            'connected_at': datetime.utcnow().isoformat(),
            'profile_url': None  # Would be populated from OAuth
        }
        
        settings.connected_accounts = connected_accounts
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'LinkedIn account connected successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/api/integrations/linkedin/disconnect', methods=['POST'])
@login_required
def disconnect_linkedin():
    """Disconnect LinkedIn account"""
    try:
        settings = get_user_settings(current_user.id)
        
        connected_accounts = settings.connected_accounts or {}
        if 'linkedin' in connected_accounts:
            del connected_accounts['linkedin']
            settings.connected_accounts = connected_accounts
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'LinkedIn account disconnected successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/api/integrations/github/connect', methods=['POST'])
@login_required
def connect_github():
    """Connect GitHub account"""
    try:
        settings = get_user_settings(current_user.id)
        
        connected_accounts = settings.connected_accounts or {}
        connected_accounts['github'] = {
            'connected': True,
            'connected_at': datetime.utcnow().isoformat(),
            'username': None  # Would be populated from OAuth
        }
        
        settings.connected_accounts = connected_accounts
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'GitHub account connected successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/api/integrations/github/disconnect', methods=['POST'])
@login_required
def disconnect_github():
    """Disconnect GitHub account"""
    try:
        settings = get_user_settings(current_user.id)
        
        connected_accounts = settings.connected_accounts or {}
        if 'github' in connected_accounts:
            del connected_accounts['github']
            settings.connected_accounts = connected_accounts
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'GitHub account disconnected successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/api/integrations/indeed/connect', methods=['POST'])
@login_required
def connect_indeed():
    """Connect Indeed account"""
    try:
        settings = get_user_settings(current_user.id)
        
        connected_accounts = settings.connected_accounts or {}
        connected_accounts['indeed'] = {
            'connected': True,
            'connected_at': datetime.utcnow().isoformat(),
        }
        
        settings.connected_accounts = connected_accounts
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Indeed account connected successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/api/integrations/indeed/disconnect', methods=['POST'])
@login_required
def disconnect_indeed():
    """Disconnect Indeed account"""
    try:
        settings = get_user_settings(current_user.id)
        
        connected_accounts = settings.connected_accounts or {}
        if 'indeed' in connected_accounts:
            del connected_accounts['indeed']
            settings.connected_accounts = connected_accounts
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Indeed account disconnected successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/api/integrations/google-drive/connect', methods=['POST'])
@login_required
def connect_google_drive():
    """Connect Google Drive account"""
    try:
        settings = get_user_settings(current_user.id)
        
        connected_accounts = settings.connected_accounts or {}
        connected_accounts['google_drive'] = {
            'connected': True,
            'connected_at': datetime.utcnow().isoformat(),
        }
        
        settings.connected_accounts = connected_accounts
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Google Drive connected successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/api/integrations/google-drive/disconnect', methods=['POST'])
@login_required
def disconnect_google_drive():
    """Disconnect Google Drive account"""
    try:
        settings = get_user_settings(current_user.id)
        
        connected_accounts = settings.connected_accounts or {}
        if 'google_drive' in connected_accounts:
            del connected_accounts['google_drive']
            settings.connected_accounts = connected_accounts
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Google Drive disconnected successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Webhook management
@settings_bp.route('/api/webhooks/save', methods=['POST'])
@login_required
def save_webhook():
    """Save webhook configuration"""
    try:
        data = request.get_json()
        webhook_url = data.get('webhook_url', '')
        webhook_events = data.get('webhook_events', [])
        
        settings = get_user_settings(current_user.id)
        settings.webhook_url = webhook_url if webhook_url else None
        settings.webhook_events = webhook_events
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Webhook configuration saved successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Data management endpoints
@settings_bp.route('/api/data/clear-cache', methods=['POST'])
@login_required
def clear_cache():
    """Clear browser cache (placeholder - actual implementation would be browser-side)"""
    try:
        # This is mostly a placeholder since cache clearing is done browser-side
        # You could log this action or clear server-side cached data here
        
        return jsonify({
            'success': True,
            'message': 'Cache clear request processed'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/api/data/clear-activity', methods=['POST'])
@login_required
def clear_activity_history():
    """Clear user activity history"""
    try:
        # Clear activity-related data
        # You could implement specific activity clearing logic here
        # For example, clearing old job searches, application history, etc.
        
        return jsonify({
            'success': True,
            'message': 'Activity history cleared successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Feedback endpoint
@settings_bp.route('/api/feedback/send', methods=['POST'])
@login_required
def send_feedback():
    """Send user feedback"""
    try:
        data = request.get_json()
        feedback_type = data.get('feedback_type', 'general')
        feedback_message = data.get('feedback_message', '')
        
        if not feedback_message.strip():
            return jsonify({'success': False, 'message': 'Feedback message is required'}), 400
        
        # Here you would typically:
        # 1. Save feedback to database
        # 2. Send email notification to admin
        # 3. Create a support ticket
        
        # For now, we'll just log it
        print(f"Feedback from user {current_user.id}: [{feedback_type}] {feedback_message}")
        
        return jsonify({
            'success': True,
            'message': 'Feedback sent successfully. Thank you!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# System info endpoint
@settings_bp.route('/api/system/info', methods=['GET'])
@login_required
def get_system_info():
    """Get system information for the help section"""
    try:
        return jsonify({
            'success': True,
            'system_info': {
                'app_version': '3.2.1',
                'account_id': f'CB{current_user.id:06d}',
                'last_login': current_user.created_at.isoformat() if current_user.created_at else None,
                'member_since': current_user.created_at.strftime('%B %Y') if current_user.created_at else 'Unknown',
                'subscription_tier': current_user.subscription_tier,
                'total_applications': len(current_user.job_applications),
                'total_skills': len(current_user.skills),
                'total_achievements': len(current_user.achievements),
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Two-factor authentication endpoints (placeholders)
@settings_bp.route('/api/security/2fa/enable', methods=['POST'])
@login_required
def enable_2fa():
    """Enable two-factor authentication (placeholder)"""
    try:
        # This would typically:
        # 1. Generate QR code for authenticator app
        # 2. Provide backup codes
        # 3. Verify initial setup
        
        settings = get_user_settings(current_user.id)
        settings.two_factor_enabled = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Two-factor authentication enabled successfully',
            'qr_code': 'placeholder_qr_code_data',  # Would be actual QR code
            'backup_codes': ['123456', '789012', '345678']  # Would be actual backup codes
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/api/security/2fa/disable', methods=['POST'])
@login_required
def disable_2fa():
    """Disable two-factor authentication"""
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        # Verify password before disabling 2FA
        if not check_password_hash(current_user.password, password):
            return jsonify({'success': False, 'message': 'Invalid password'}), 400
        
        settings = get_user_settings(current_user.id)
        settings.two_factor_enabled = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Two-factor authentication disabled successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Storage management endpoints
@settings_bp.route('/api/storage/usage', methods=['GET'])
@login_required
def get_storage_usage():
    """Get storage usage information"""
    try:
        # Calculate storage usage
        # This would typically calculate actual file sizes
        resume_files_size = 900  # MB - placeholder
        cover_letters_size = 600  # MB - placeholder  
        portfolio_size = 300  # MB - placeholder
        total_used = resume_files_size + cover_letters_size + portfolio_size
        total_available = 5000  # 5GB in MB
        
        return jsonify({
            'success': True,
            'storage': {
                'total_used_mb': total_used,
                'total_available_mb': total_available,
                'usage_percentage': (total_used / total_available) * 100,
                'breakdown': {
                    'resume_files': resume_files_size,
                    'cover_letters': cover_letters_size,
                    'portfolio': portfolio_size
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@settings_bp.route('/api/storage/manage-downloads', methods=['POST'])
@login_required
def manage_downloads():
    """Manage offline downloads"""
    try:
        # This would manage offline download settings
        # Clear old downloads, manage download preferences, etc.
        
        return jsonify({
            'success': True,
            'message': 'Download preferences updated successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Context processor to inject settings into all templates
@settings_bp.app_context_processor
def inject_user_settings():
    """Inject user settings into all templates"""
    if current_user.is_authenticated:
        try:
            settings = get_user_settings(current_user.id)
            return {
                'user_settings': settings,
                'user_display_preferences': {
                    'theme': settings.theme,
                    'accent_color': settings.accent_color,
                    'font_size': settings.font_size,
                    'language': settings.display_language,
                    'currency': settings.currency,
                }
            }
        except:
            return {
                'user_settings': None,
                'user_display_preferences': {}
            }
    return {
        'user_settings': None,
        'user_display_preferences': {}
    }

# Utility functions
def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Error handlers for settings blueprint
@settings_bp.errorhandler(404)
def settings_not_found(error):
    return jsonify({'success': False, 'message': 'Settings endpoint not found'}), 404

@settings_bp.errorhandler(500)
def settings_server_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500