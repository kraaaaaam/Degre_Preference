from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import json
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/Degre_Preference'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Database Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Enum('student', 'admin', 'counselor'), default='student')
    school_name = db.Column(db.String(100))
    grade_level = db.Column(db.String(20))
    birth_date = db.Column(db.Date)
    gender = db.Column(db.Enum('male', 'female', 'other'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)


class AssessmentDomain(db.Model):
    __tablename__ = 'assessment_domains'
    id = db.Column(db.Integer, primary_key=True)
    domain_name = db.Column(db.String(100), nullable=False)
    domain_code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    weight_percentage = db.Column(db.Numeric(5, 2), default=0.00)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class QuestionCategory(db.Model):
    __tablename__ = 'question_categories'
    id = db.Column(db.Integer, primary_key=True)
    domain_id = db.Column(db.Integer, db.ForeignKey('assessment_domains.id'))
    category_name = db.Column(db.String(100), nullable=False)
    category_code = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    weight_percentage = db.Column(db.Numeric(5, 2), default=0.00)


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('question_categories.id'))
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum('multiple_choice', 'true_false', 'scenario', 'likert_scale'),
                              default='multiple_choice')
    difficulty_level = db.Column(db.Enum('easy', 'medium', 'hard'), default='medium')
    points_value = db.Column(db.Integer, default=1)
    time_limit_seconds = db.Column(db.Integer, default=60)
    explanation = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))


class AnswerOption(db.Model):
    __tablename__ = 'answer_options'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    option_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    option_order = db.Column(db.Integer, default=1)
    points_value = db.Column(db.Integer, default=0)


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(200), nullable=False)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    prerequisites = db.Column(db.Text)
    career_opportunities = db.Column(db.Text)
    average_salary_range = db.Column(db.String(50))
    job_demand_level = db.Column(db.Enum('high', 'medium', 'low'), default='medium')
    required_skills = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AssessmentSession(db.Model):
    __tablename__ = 'assessment_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    session_token = db.Column(db.String(100), unique=True, nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.Enum('started', 'in_progress', 'completed', 'abandoned'), default='started')
    total_questions = db.Column(db.Integer, default=0)
    answered_questions = db.Column(db.Integer, default=0)
    current_question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    time_remaining = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)


class StudentResponse(db.Model):
    __tablename__ = 'student_responses'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('assessment_sessions.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    selected_option_id = db.Column(db.Integer, db.ForeignKey('answer_options.id'))
    response_text = db.Column(db.Text)
    points_earned = db.Column(db.Integer, default=0)
    time_spent_seconds = db.Column(db.Integer, default=0)
    is_correct = db.Column(db.Boolean)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)


class AssessmentResult(db.Model):
    __tablename__ = 'assessment_results'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('assessment_sessions.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    overall_score = db.Column(db.Numeric(5, 2), default=0.00)
    overall_percentile = db.Column(db.Numeric(5, 2), default=0.00)
    completion_time_minutes = db.Column(db.Integer, default=0)
    total_questions_attempted = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    assessment_date = db.Column(db.DateTime, default=datetime.utcnow)


class DomainScore(db.Model):
    __tablename__ = 'domain_scores'
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('assessment_results.id'))
    domain_id = db.Column(db.Integer, db.ForeignKey('assessment_domains.id'))
    raw_score = db.Column(db.Numeric(5, 2), default=0.00)
    scaled_score = db.Column(db.Numeric(5, 2), default=0.00)
    percentile = db.Column(db.Numeric(5, 2), default=0.00)
    performance_level = db.Column(db.Enum('below_average', 'average', 'above_average', 'excellent'), default='average')


class CourseRecommendation(db.Model):
    __tablename__ = 'course_recommendations'
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('assessment_results.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    match_percentage = db.Column(db.Numeric(5, 2), default=0.00)
    confidence_level = db.Column(db.Enum('low', 'medium', 'high'), default='medium')
    recommendation_reason = db.Column(db.Text)
    rank_order = db.Column(db.Integer, default=1)


# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)

    return decorated_function


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()

        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'message': 'Email already registered'})

        if User.query.filter_by(username=data['username']).first():
            return jsonify({'success': False, 'message': 'Username already taken'})

        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            first_name=data['first_name'],
            last_name=data['last_name'],
            school_name=data.get('school_name', ''),
            grade_level=data.get('grade_level', ''),
            birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date() if data.get('birth_date') else None,
            gender=data.get('gender')
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Registration successful'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Registration failed'})

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()

        if user and check_password_hash(user.password_hash, data['password']):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return jsonify({'success': True, 'redirect': url_for('dashboard')})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'})

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)


@app.route('/assessment/start', methods=['POST'])
@login_required
def start_assessment():
    # Create new assessment session
    session_token = secrets.token_urlsafe(32)
    new_session = AssessmentSession(
        user_id=session['user_id'],
        session_token=session_token,
        status='started'
    )

    try:
        db.session.add(new_session)
        db.session.commit()
        return jsonify({'success': True, 'session_token': session_token})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to start assessment'})


@app.route('/assessment/questions/<session_token>')
@login_required
def get_assessment_questions(session_token):
    assessment_session = AssessmentSession.query.filter_by(session_token=session_token).first()
    if not assessment_session or assessment_session.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'Invalid session'})

    # Get questions from all categories (simplified for demo)
    questions = db.session.query(Question).join(QuestionCategory).join(AssessmentDomain) \
        .filter(Question.is_active == True) \
        .limit(20).all()  # Limit to 20 questions for demo

    question_data = []
    for question in questions:
        options = AnswerOption.query.filter_by(question_id=question.id).all()
        question_data.append({
            'id': question.id,
            'text': question.question_text,
            'type': question.question_type,
            'time_limit': question.time_limit_seconds,
            'options': [{'id': opt.id, 'text': opt.option_text, 'order': opt.option_order}
                        for opt in options]
        })

    # Update session
    assessment_session.total_questions = len(question_data)
    assessment_session.status = 'in_progress'
    db.session.commit()

    return jsonify({'success': True, 'questions': question_data})


@app.route('/assessment/submit', methods=['POST'])
@login_required
def submit_response():
    data = request.get_json()
    session_token = data['session_token']
    question_id = data['question_id']
    selected_option_id = data['selected_option_id']
    time_spent = data.get('time_spent', 0)

    assessment_session = AssessmentSession.query.filter_by(session_token=session_token).first()
    if not assessment_session or assessment_session.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'Invalid session'})

    # Check if answer is correct
    selected_option = AnswerOption.query.get(selected_option_id)
    is_correct = selected_option.is_correct if selected_option else False
    points_earned = selected_option.points_value if is_correct else 0

    # Save response
    response = StudentResponse(
        session_id=assessment_session.id,
        question_id=question_id,
        selected_option_id=selected_option_id,
        points_earned=points_earned,
        time_spent_seconds=time_spent,
        is_correct=is_correct
    )

    try:
        db.session.add(response)
        assessment_session.answered_questions += 1
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to save response'})


@app.route('/assessment/complete', methods=['POST'])
@login_required
def complete_assessment():
    data = request.get_json()
    session_token = data['session_token']

    assessment_session = AssessmentSession.query.filter_by(session_token=session_token).first()
    if not assessment_session or assessment_session.user_id != session['user_id']:
        return jsonify({'success': False, 'message': 'Invalid session'})

    # Calculate results
    total_responses = StudentResponse.query.filter_by(session_id=assessment_session.id).count()
    correct_responses = StudentResponse.query.filter_by(session_id=assessment_session.id, is_correct=True).count()

    overall_score = (correct_responses / total_responses * 100) if total_responses > 0 else 0
    completion_time = (datetime.utcnow() - assessment_session.start_time).seconds // 60

    # Create assessment result
    result = AssessmentResult(
        session_id=assessment_session.id,
        user_id=session['user_id'],
        overall_score=overall_score,
        completion_time_minutes=completion_time,
        total_questions_attempted=total_responses,
        correct_answers=correct_responses
    )

    try:
        db.session.add(result)
        assessment_session.status = 'completed'
        assessment_session.end_time = datetime.utcnow()
        db.session.commit()

        # Generate course recommendations (simplified algorithm)
        generate_recommendations(result.id, overall_score)

        return jsonify({'success': True, 'result_id': result.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to complete assessment'})


def generate_recommendations(result_id, overall_score):
    """Generate course recommendations based on assessment results"""
    courses = Course.query.filter_by(is_active=True).all()

    for course in courses:
        # Simplified recommendation algorithm
        if overall_score >= 80:
            match_percentage = min(95, overall_score + 10)
            confidence = 'high'
        elif overall_score >= 60:
            match_percentage = overall_score + 5
            confidence = 'medium'
        else:
            match_percentage = max(30, overall_score - 10)
            confidence = 'low'

        if match_percentage >= 50:  # Only recommend courses with decent match
            recommendation = CourseRecommendation(
                result_id=result_id,
                course_id=course.id,
                match_percentage=match_percentage,
                confidence_level=confidence,
                recommendation_reason=f"Based on your overall performance of {overall_score:.1f}%"
            )
            db.session.add(recommendation)

    db.session.commit()


@app.route('/results/<int:result_id>')
@login_required
def view_results(result_id):
    result = AssessmentResult.query.get_or_404(result_id)
    if result.user_id != session['user_id'] and session.get('role') not in ['admin', 'counselor']:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))

    recommendations = db.session.query(CourseRecommendation, Course) \
        .join(Course) \
        .filter(CourseRecommendation.result_id == result_id) \
        .order_by(CourseRecommendation.match_percentage.desc()) \
        .limit(10).all()

    return render_template('results.html', result=result, recommendations=recommendations)


# Admin Routes
@app.route('/admin')
@admin_required
def admin_dashboard():
    total_users = User.query.count()
    total_assessments = AssessmentResult.query.count()
    total_questions = Question.query.count()
    recent_results = AssessmentResult.query.order_by(AssessmentResult.assessment_date.desc()).limit(5).all()

    stats = {
        'total_users': total_users,
        'total_assessments': total_assessments,
        'total_questions': total_questions,
        'recent_results': recent_results
    }

    return render_template('admin/dashboard.html', stats=stats)


@app.route('/admin/questions')
@admin_required
def manage_questions():
    questions = db.session.query(Question, QuestionCategory, AssessmentDomain) \
        .join(QuestionCategory) \
        .join(AssessmentDomain) \
        .order_by(Question.created_at.desc()).all()

    categories = QuestionCategory.query.all()
    domains = AssessmentDomain.query.all()

    return render_template('admin/questions.html', questions=questions, categories=categories, domains=domains)


@app.route('/admin/questions/add', methods=['POST'])
@admin_required
def add_question():
    data = request.get_json()

    new_question = Question(
        category_id=data['category_id'],
        question_text=data['question_text'],
        question_type=data['question_type'],
        difficulty_level=data['difficulty_level'],
        points_value=data.get('points_value', 1),
        time_limit_seconds=data.get('time_limit_seconds', 60),
        explanation=data.get('explanation', ''),
        created_by=session['user_id']
    )

    try:
        db.session.add(new_question)
        db.session.flush()  # Get the question ID

        # Add answer options
        for i, option_data in enumerate(data['options']):
            option = AnswerOption(
                question_id=new_question.id,
                option_text=option_data['text'],
                is_correct=option_data['is_correct'],
                option_order=i + 1,
                points_value=data.get('points_value', 1) if option_data['is_correct'] else 0
            )
            db.session.add(option)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Question added successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to add question'})


@app.route('/admin/questions/<int:question_id>/edit', methods=['POST'])
@admin_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    data = request.get_json()

    try:
        question.category_id = data['category_id']
        question.question_text = data['question_text']
        question.question_type = data['question_type']
        question.difficulty_level = data['difficulty_level']
        question.points_value = data.get('points_value', 1)
        question.time_limit_seconds = data.get('time_limit_seconds', 60)
        question.explanation = data.get('explanation', '')
        question.updated_at = datetime.utcnow()

        # Update answer options
        AnswerOption.query.filter_by(question_id=question_id).delete()

        for i, option_data in enumerate(data['options']):
            option = AnswerOption(
                question_id=question_id,
                option_text=option_data['text'],
                is_correct=option_data['is_correct'],
                option_order=i + 1,
                points_value=data.get('points_value', 1) if option_data['is_correct'] else 0
            )
            db.session.add(option)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Question updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to update question'})


@app.route('/admin/questions/<int:question_id>/delete', methods=['DELETE'])
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)

    try:
        # Delete associated answer options first
        AnswerOption.query.filter_by(question_id=question_id).delete()
        db.session.delete(question)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Question deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to delete question'})


@app.route('/admin/courses')
@admin_required
def manage_courses():
    courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template('admin/courses.html', courses=courses)


@app.route('/admin/courses/add', methods=['POST'])
@admin_required
def add_course():
    data = request.get_json()

    new_course = Course(
        course_name=data['course_name'],
        course_code=data['course_code'],
        description=data.get('description', ''),
        category=data.get('category', ''),
        prerequisites=data.get('prerequisites', ''),
        career_opportunities=data.get('career_opportunities', ''),
        average_salary_range=data.get('average_salary_range', ''),
        job_demand_level=data.get('job_demand_level', 'medium'),
        required_skills=data.get('required_skills', '')
    )

    try:
        db.session.add(new_course)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Course added successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to add course'})


@app.route('/admin/courses/<int:course_id>/edit', methods=['POST'])
@admin_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    data = request.get_json()

    try:
        course.course_name = data['course_name']
        course.course_code = data['course_code']
        course.description = data.get('description', '')
        course.category = data.get('category', '')
        course.prerequisites = data.get('prerequisites', '')
        course.career_opportunities = data.get('career_opportunities', '')
        course.average_salary_range = data.get('average_salary_range', '')
        course.job_demand_level = data.get('job_demand_level', 'medium')
        course.required_skills = data.get('required_skills', '')

        db.session.commit()
        return jsonify({'success': True, 'message': 'Course updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to update course'})


@app.route('/admin/courses/<int:course_id>/delete', methods=['DELETE'])
@admin_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)

    try:
        db.session.delete(course)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Course deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Failed to delete course'})


@app.route('/admin/users')
@admin_required
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/reports')
@admin_required
def view_reports():
    # Assessment statistics
    total_assessments = AssessmentResult.query.count()
    avg_score = db.session.query(db.func.avg(AssessmentResult.overall_score)).scalar() or 0

    # Performance by domain (simplified)
    domain_stats = db.session.query(AssessmentDomain.domain_name,
                                    db.func.count(DomainScore.id).label('count'),
                                    db.func.avg(DomainScore.scaled_score).label('avg_score')) \
        .join(DomainScore) \
        .group_by(AssessmentDomain.domain_name).all()

    # Course recommendation stats
    course_stats = db.session.query(Course.course_name,
                                    db.func.count(CourseRecommendation.id).label('recommendation_count')) \
        .join(CourseRecommendation) \
        .group_by(Course.course_name) \
        .order_by(db.func.count(CourseRecommendation.id).desc()) \
        .limit(10).all()

    stats = {
        'total_assessments': total_assessments,
        'average_score': round(float(avg_score), 2),
        'domain_stats': domain_stats,
        'course_stats': course_stats
    }

    return render_template('admin/reports.html', stats=stats)


# API Routes
@app.route('/api/domains')
def get_domains():
    domains = AssessmentDomain.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': d.id,
        'name': d.domain_name,
        'code': d.domain_code,
        'description': d.description,
        'weight': float(d.weight_percentage)
    } for d in domains])


@app.route('/api/categories/<int:domain_id>')
def get_categories(domain_id):
    categories = QuestionCategory.query.filter_by(domain_id=domain_id).all()
    return jsonify([{
        'id': c.id,
        'name': c.category_name,
        'code': c.category_code,
        'description': c.description
    } for c in categories])


@app.route('/api/question/<int:question_id>')
def get_question(question_id):
    question = Question.query.get_or_404(question_id)
    options = AnswerOption.query.filter_by(question_id=question_id).order_by(AnswerOption.option_order).all()

    return jsonify({
        'id': question.id,
        'text': question.question_text,
        'type': question.question_type,
        'difficulty': question.difficulty_level,
        'time_limit': question.time_limit_seconds,
        'explanation': question.explanation,
        'options': [{
            'id': opt.id,
            'text': opt.option_text,
            'order': opt.option_order
        } for opt in options]
    })


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Create default admin user if doesn't exist
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@system.com',
                password_hash=generate_password_hash('admin123'),
                first_name='System',
                last_name='Administrator',
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created: admin/admin123")

    app.run(debug=True, host='0.0.0.0', port=5000)