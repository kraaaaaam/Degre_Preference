"""
Sample data insertion script for Course Preference Advisor
Run this script to populate the database with sample questions and data
"""

from app import app, db
from app import Question, AnswerOption, QuestionCategory, Course, User
from werkzeug.security import generate_password_hash


def create_sample_questions():
    """Create sample questions for each domain"""

    sample_questions_data = [
        # Verbal Reasoning Questions
        {
            'category_id': 1,  # Vocabulary
            'question_text': 'Choose the word that is most similar in meaning to "ABUNDANT":',
            'question_type': 'multiple_choice',
            'difficulty_level': 'medium',
            'points_value': 1,
            'options': [
                {'text': 'Scarce', 'is_correct': False},
                {'text': 'Plentiful', 'is_correct': True},
                {'text': 'Limited', 'is_correct': False},
                {'text': 'Rare', 'is_correct': False}
            ]
        },
        {
            'category_id': 1,  # Vocabulary
            'question_text': 'What is the meaning of "METICULOUS"?',
            'question_type': 'multiple_choice',
            'difficulty_level': 'medium',
            'points_value': 1,
            'options': [
                {'text': 'Careless', 'is_correct': False},
                {'text': 'Quick', 'is_correct': False},
                {'text': 'Very careful and precise', 'is_correct': True},
                {'text': 'Lazy', 'is_correct': False}
            ]
        },
        {
            'category_id': 2,  # Reading Comprehension
            'question_text': 'Climate change refers to long-term shifts in global temperatures and weather patterns. While climate variations occur naturally, scientific evidence shows that human activities have been the main driver since the 1800s. What is the main idea of this passage?',
            'question_type': 'multiple_choice',
            'difficulty_level': 'medium',
            'points_value': 2,
            'options': [
                {'text': 'Climate has always been changing naturally', 'is_correct': False},
                {'text': 'Human activities are the primary cause of recent climate change', 'is_correct': True},
                {'text': 'Climate change started in the 1800s', 'is_correct': False},
                {'text': 'Weather patterns never change', 'is_correct': False}
            ]
        },

        # Mathematical Reasoning Questions
        {
            'category_id': 4,  # Arithmetic
            'question_text': 'If a shirt originally costs ₱800 and is on sale for 25% off, what is the sale price?',
            'question_type': 'multiple_choice',
            'difficulty_level': 'easy',
            'points_value': 1,
            'options': [
                {'text': '₱200', 'is_correct': False},
                {'text': '₱600', 'is_correct': True},
                {'text': '₱700', 'is_correct': False},
                {'text': '₱750', 'is_correct': False}
            ]
        },
        {
            'category_id': 5,  # Algebra
            'question_text': 'Solve for x: 2x + 5 = 15',
            'question_type': 'multiple_choice',
            'difficulty_level': 'easy',
            'points_value': 1,
            'options': [
                {'text': 'x = 5', 'is_correct': True},
                {'text': 'x = 10', 'is_correct': False},
                {'text': 'x = 7', 'is_correct': False},
                {'text': 'x = 3', 'is_correct': False}
            ]
        },
        {
            'category_id': 6,  # Geometry
            'question_text': 'What is the area of a rectangle with length 8 cm and width 5 cm?',
            'question_type': 'multiple_choice',
            'difficulty_level': 'easy',
            'points_value': 1,
            'options': [
                {'text': '13 cm²', 'is_correct': False},
                {'text': '26 cm²', 'is_correct': False},
                {'text': '40 cm²', 'is_correct': True},
                {'text': '80 cm²', 'is_correct': False}
            ]
        },

        # Scientific Reasoning Questions
        {
            'category_id': 8,  # Biology
            'question_text': 'What is the basic unit of life?',
            'question_type': 'multiple_choice',
            'difficulty_level': 'easy',
            'points_value': 1,
            'options': [
                {'text': 'Atom', 'is_correct': False},
                {'text': 'Molecule', 'is_correct': False},
                {'text': 'Cell', 'is_correct': True},
                {'text': 'Organ', 'is_correct': False}
            ]
        },
        {
            'category_id': 9,  # Chemistry
            'question_text': 'What is the chemical symbol for water?',
            'question_type': 'multiple_choice',
            'difficulty_level': 'easy',
            'points_value': 1,
            'options': [
                {'text': 'H2O', 'is_correct': True},
                {'text': 'CO2', 'is_correct': False},
                {'text': 'O2', 'is_correct': False},
                {'text': 'NaCl', 'is_correct': False}
            ]
        },
        {
            'category_id': 10,  # Physics
            'question_text': 'What is the unit of force in the International System of Units (SI)?',
            'question_type': 'multiple_choice',
            'difficulty_level': 'medium',
            'points_value': 1,
            'options': [
                {'text': 'Joule', 'is_correct': False},
                {'text': 'Newton', 'is_correct': True},
                {'text': 'Pascal', 'is_correct': False},
                {'text': 'Watt', 'is_correct': False}
            ]
        },

        # Logical Reasoning Questions
        {
            'category_id': 3,  # Logical (assuming category 3 exists)
            'question_text': 'All roses are flowers. Some flowers are red. Therefore:',
            'question_type': 'multiple_choice',
            'difficulty_level': 'medium',
            'points_value': 2,
            'options': [
                {'text': 'All roses are red', 'is_correct': False},
                {'text': 'Some roses may be red', 'is_correct': True},
                {'text': 'No roses are red', 'is_correct': False},
                {'text': 'All flowers are roses', 'is_correct': False}
            ]
        },

        # Interest and Values Questions
        {
            'category_id': 1,
            'question_text': 'Which activity would you most enjoy?',
            'question_type': 'multiple_choice',
            'difficulty_level': 'easy',
            'points_value': 1,
            'options': [
                {'text': 'Solving mathematical problems', 'is_correct': False},
                {'text': 'Writing stories or articles', 'is_correct': False},
                {'text': 'Building or fixing things', 'is_correct': False},
                {'text': 'All options are valid based on interests', 'is_correct': True}
            ]
        }
    ]

    for q_data in sample_questions_data:
        # Check if question already exists
        existing_q = Question.query.filter_by(question_text=q_data['question_text']).first()
        if existing_q:
            continue

        # Create question
        question = Question(
            category_id=q_data['category_id'],
            question_text=q_data['question_text'],
            question_type=q_data['question_type'],
            difficulty_level=q_data['difficulty_level'],
            points_value=q_data['points_value'],
            created_by=1  # Assume admin user ID is 1
        )

        db.session.add(question)
        db.session.flush()  # Get the question ID

        # Create answer options
        for opt_data in q_data['options']:
            option = AnswerOption(
                question_id=question.id,
                option_text=opt_data['text'],
                is_correct=opt_data['is_correct'],
                points_value=q_data['points_value'] if opt_data['is_correct'] else 0
            )
            db.session.add(option)

    db.session.commit()
    print(f"Created {len(sample_questions_data)} sample questions")


def create_sample_users():
    """Create sample users for testing"""

    sample_users = [
        {
            'username': 'student_demo',
            'email': 'student@demo.com',
            'password': 'student123',
            'first_name': 'Demo',
            'last_name': 'Student',
            'role': 'student',
            'school_name': 'Demo High School',
            'grade_level': 'Grade 12'
        },
        {
            'username': 'counselor_demo',
            'email': 'counselor@demo.com',
            'password': 'counselor123',
            'first_name': 'Demo',
            'last_name': 'Counselor',
            'role': 'counselor',
            'school_name': 'Demo High School'
        }
    ]

    for user_data in sample_users:
        # Check if user already exists
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if existing_user:
            continue

        user = User(
            username=user_data['username'],
            email=user_data['email'],
            password_hash=generate_password_hash(user_data['password']),
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data['role'],
            school_name=user_data.get('school_name'),
            grade_level=user_data.get('grade_level')
        )

        db.session.add(user)

    db.session.commit()
    print(f"Created {len(sample_users)} sample users")


def create_additional_courses():
    """Add more sample courses"""

    additional_courses = [
        {
            'course_name': 'Bachelor of Science in Accountancy',
            'course_code': 'BSA',
            'description': 'Study of accounting principles, financial management, and business operations',
            'category': 'ABM',
            'job_demand_level': 'high',
            'career_opportunities': 'Certified Public Accountant, Financial Analyst, Auditor, Tax Consultant',
            'average_salary_range': '₱25,000 - ₱80,000'
        },
        {
            'course_name': 'Bachelor of Arts in Communication',
            'course_code': 'BAC',
            'description': 'Media studies, journalism, public relations, and digital communication',
            'category': 'HUMSS',
            'job_demand_level': 'medium',
            'career_opportunities': 'Journalist, PR Specialist, Content Creator, Media Producer',
            'average_salary_range': '₱20,000 - ₱60,000'
        },
        {
            'course_name': 'Bachelor of Science in Tourism Management',
            'course_code': 'BSTM',
            'description': 'Hospitality, travel, and tourism industry management',
            'category': 'ABM',
            'job_demand_level': 'medium',
            'career_opportunities': 'Travel Agent, Hotel Manager, Tour Guide, Event Coordinator',
            'average_salary_range': '₱18,000 - ₱50,000'
        },
        {
            'course_name': 'Bachelor of Science in Architecture',
            'course_code': 'BS_ARCH',
            'description': 'Building design, construction, and architectural planning',
            'category': 'STEM',
            'job_demand_level': 'medium',
            'career_opportunities': 'Architect, Urban Planner, Interior Designer, Construction Manager',
            'average_salary_range': '₱30,000 - ₱100,000'
        },
        {
            'course_name': 'Bachelor of Science in Environmental Science',
            'course_code': 'BS_ENVSCI',
            'description': 'Environmental protection, sustainability, and natural resource management',
            'category': 'STEM',
            'job_demand_level': 'high',
            'career_opportunities': 'Environmental Consultant, Conservation Scientist, Environmental Engineer',
            'average_salary_range': '₱25,000 - ₱70,000'
        }
    ]

    for course_data in additional_courses:
        # Check if course already exists
        existing_course = Course.query.filter_by(course_code=course_data['course_code']).first()
        if existing_course:
            continue

        course = Course(
            course_name=course_data['course_name'],
            course_code=course_data['course_code'],
            description=course_data['description'],
            category=course_data['category'],
            job_demand_level=course_data['job_demand_level'],
            career_opportunities=course_data['career_opportunities'],
            average_salary_range=course_data['average_salary_range']
        )

        db.session.add(course)

    db.session.commit()
    print(f"Created {len(additional_courses)} additional courses")


def main():
    """Main function to run all sample data creation"""
    with app.app_context():
        print("Creating sample data...")

        # Create sample questions
        create_sample_questions()

        # Create sample users
        create_sample_users()

        # Create additional courses
        create_additional_courses()

        print("Sample data creation completed!")
        print("\nDemo Login Credentials:")
        print("Admin: admin@system.com / admin123")
        print("Student: student@demo.com / student123")
        print("Counselor: counselor@demo.com / counselor123")


if __name__ == '__main__':
    main()