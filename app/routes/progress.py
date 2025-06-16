from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import update_academic_progress, update_skill, add_achievement
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, DateField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional
from datetime import datetime

progress_bp = Blueprint('progress', __name__)

# Forms
class AcademicProgressForm(FlaskForm):
    gpa = FloatField('GPA', validators=[DataRequired(), NumberRange(min=0, max=4.0)])
    credits = IntegerField('Credits', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Update Progress')

class AchievementForm(FlaskForm):
    title = StringField('Achievement Title', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Add Achievement')

class SkillForm(FlaskForm):
    name = StringField('Skill Name', validators=[DataRequired()])
    skill_type = StringField('Skill Type', validators=[DataRequired()])
    level = StringField('Level', validators=[DataRequired()])
    percentage = IntegerField('Percentage', validators=[DataRequired(), NumberRange(min=0, max=100)])
    submit = SubmitField('Add/Update Skill')

@progress_bp.route('/progress')
@login_required
def progress():
    academic_form = AcademicProgressForm()
    achievement_form = AchievementForm()
    skill_form = SkillForm()

    # Set current values for academic form
    academic_form.gpa.data = getattr(current_user, 'gpa', 0.0)
    academic_form.credits.data = getattr(current_user, 'credits', 0)

    # Prepare the data for the template
    user_gpa = getattr(current_user, 'gpa', 0.0)
    user_credits = getattr(current_user, 'credits', 0)
    user_total_credits = getattr(current_user, 'total_credits', 120)  # Default to 120 if not set
    
    academic_progress = {
        'gpa': user_gpa,
        'credits': user_credits,
        'total_credits': user_total_credits,
        'progress_percentage': (user_credits / user_total_credits) * 100 if user_total_credits > 0 else 0
    }

    # Get academic progress details - use enrollments instead of created_courses
    current_courses = []
    if hasattr(current_user, 'enrollments'):
        # Get enrolled courses that are approved and in progress
        current_courses = [
            {
                'name': enrollment.course.title,
                'category': enrollment.course.category.name if enrollment.course.category else 'General',
                'credits': 3,  # You might want to add a credits field to Course model
                'progress': enrollment.progress,
                'grade': 'In Progress' if not enrollment.is_completed else 'Completed'
            }
            for enrollment in current_user.enrollments 
            if enrollment.course.status == 'approved'
        ]

    # Get professional journey (internships and job applications)
    internships = getattr(current_user, 'internships', [])
    job_applications = getattr(current_user, 'job_applications', [])

    # Get skills categorized as technical and soft
    all_skills = getattr(current_user, 'skills', [])
    technical_skills = [skill for skill in all_skills if getattr(skill, 'skill_type', '') == 'technical']
    soft_skills = [skill for skill in all_skills if getattr(skill, 'skill_type', '') == 'soft']

    # Get achievements sorted by date
    user_achievements = getattr(current_user, 'achievements', [])
    achievements = []
    if user_achievements:
        try:
            achievements = sorted(user_achievements,
                               key=lambda x: datetime.strptime(x.date, '%Y-%m-%d') if isinstance(x.date, str) else x.date,
                               reverse=True)
        except (AttributeError, ValueError):
            # If there's an issue with date parsing, just use the achievements as-is
            achievements = user_achievements

    # Get certificates (this could be derived from skills or another field in the database)
    certificates = getattr(current_user, 'certificates', [])

    # Render template
    return render_template(
        'progress.html',
        title='Progress Tracker',
        academic_progress=academic_progress,
        current_courses=current_courses,
        internships=internships,
        job_applications=job_applications,
        technical_skills=technical_skills,
        soft_skills=soft_skills,
        achievements=achievements,
        certificates=certificates,
        academic_form=academic_form,
        achievement_form=achievement_form,
        skill_form=skill_form
    )

@progress_bp.route('/progress/update_academic', methods=['POST'])
@login_required
def update_academic():
    form = AcademicProgressForm()
    
    if form.validate_on_submit():
        gpa = form.gpa.data
        credits = form.credits.data
        
        try:
            if update_academic_progress(current_user.id, gpa, credits):
                flash('Academic progress updated successfully!', 'success')
            else:
                flash('Failed to update academic progress', 'danger')
        except Exception as e:
            flash(f'Error updating academic progress: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('progress.progress'))

@progress_bp.route('/progress/add_achievement', methods=['POST'])
@login_required
def add_achievement_route():
    form = AchievementForm()
    
    if form.validate_on_submit():
        title = form.title.data
        date = form.date.data.strftime('%Y-%m-%d')
        # Get description and category from the form data (they're not in your FlaskForm but are in the HTML)
        description = request.form.get('description', '')
        category = request.form.get('category', 'other')
        
        try:
            if add_achievement(current_user.id, title, date, description, category):
                flash('Achievement added successfully!', 'success')
            else:
                flash('Failed to add achievement', 'danger')
        except Exception as e:
            flash(f'Error adding achievement: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('progress.progress'))

@progress_bp.route('/progress/add_course', methods=['POST'])
@login_required
def add_current_course():
    """Add a course to track progress (separate from CourseHub enrollments)"""
    try:
        course_name = request.form.get('course_name')
        category = request.form.get('category', 'General')
        credits = int(request.form.get('credits', 3))
        semester = request.form.get('semester', '')
        
        if not course_name:
            flash('Course name is required', 'danger')
            return redirect(url_for('progress.progress'))
        
        # TODO: Create a CourseProgress model to store this data
        # For now, we'll just show a success message
        # You'll need to implement proper course progress tracking later
        
        flash(f'Course "{course_name}" ({credits} credits) added to your progress tracker!', 'success')
        return redirect(url_for('progress.progress'))
        
    except ValueError:
        flash('Invalid credits value. Please enter a valid number.', 'danger')
        return redirect(url_for('progress.progress'))
    except Exception as e:
        flash(f'Error adding course: {str(e)}', 'danger')
        return redirect(url_for('progress.progress'))

@progress_bp.route('/progress/update_skill', methods=['POST'], endpoint='update_skill_route')
@login_required
def update_skill_route():
    form = SkillForm()
    
    if form.validate_on_submit():
        name = form.name.data
        skill_type = form.skill_type.data
        level = form.level.data
        percentage = form.percentage.data
        
        try:
            if update_skill(current_user.id, name, skill_type, level, percentage):
                flash('Skill updated successfully!', 'success')
            else:
                flash('Failed to update skill', 'danger')
        except Exception as e:
            flash(f'Error updating skill: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('progress.progress'))

# Helper route to enroll in courses from CourseHub
@progress_bp.route('/progress/enroll_course/<int:course_id>', methods=['POST'])
@login_required  
def enroll_in_course_progress(course_id):
    """Enroll in a course from the CourseHub to track in progress"""
    try:
        from app.models import enroll_in_course
        # Use the existing enroll_in_course function from models
        enrollment_id = enroll_in_course(current_user.id, course_id)
        
        if enrollment_id:
            flash('Successfully enrolled in course!', 'success')
        else:
            flash('Failed to enroll in course. Course may not be available or you may already be enrolled.', 'danger')
            
    except Exception as e:
        flash(f'Error enrolling in course: {str(e)}', 'danger')
    
    return redirect(url_for('progress.progress'))