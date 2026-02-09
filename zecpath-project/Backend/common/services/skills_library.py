# Predefined skills library for matching

TECHNICAL_SKILLS = [
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
    'go', 'rust', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash', 'powershell',
    
    # Web Technologies
    'html', 'css', 'react', 'angular', 'vue', 'nodejs', 'express', 'django', 'flask', 'fastapi',
    'spring', 'asp.net', 'laravel', 'rails', 'jquery', 'bootstrap', 'tailwind',
    
    # Databases
    'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'cassandra',
    'dynamodb', 'elasticsearch', 'firebase',
    
    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'github', 'terraform',
    'ansible', 'ci/cd', 'linux', 'unix', 'nginx', 'apache',
    
    # Data Science & ML
    'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras', 'scikit-learn',
    'pandas', 'numpy', 'nlp', 'computer vision', 'data analysis', 'statistics',
    
    # Mobile
    'android', 'ios', 'react native', 'flutter', 'xamarin',
    
    # Tools & Others
    'git', 'jira', 'agile', 'scrum', 'rest api', 'graphql', 'microservices', 'testing',
    'junit', 'selenium', 'postman', 'swagger'
]

SOFT_SKILLS = [
    'leadership', 'communication', 'teamwork', 'problem solving', 'critical thinking',
    'time management', 'project management', 'analytical', 'creative', 'adaptable',
    'collaboration', 'presentation', 'negotiation', 'mentoring', 'strategic planning'
]

CERTIFICATIONS = [
    'aws certified', 'azure certified', 'pmp', 'scrum master', 'cissp', 'comptia',
    'google certified', 'oracle certified', 'microsoft certified', 'cisco certified'
]

# Common job titles for role detection
JOB_TITLES = [
    'software engineer', 'developer', 'programmer', 'architect', 'tech lead', 'team lead',
    'senior developer', 'junior developer', 'full stack', 'frontend', 'backend',
    'data scientist', 'data analyst', 'data engineer', 'ml engineer', 'devops engineer',
    'qa engineer', 'test engineer', 'product manager', 'project manager', 'scrum master',
    'designer', 'ui/ux', 'business analyst', 'consultant', 'intern', 'trainee'
]

# Education degrees
DEGREES = [
    'bachelor', 'master', 'phd', 'doctorate', 'mba', 'btech', 'mtech', 'bsc', 'msc',
    'be', 'me', 'bca', 'mca', 'diploma', 'associate', 'certification'
]

def get_all_skills():
    """Return all skills combined"""
    return TECHNICAL_SKILLS + SOFT_SKILLS

def get_skills_by_category():
    """Return skills organized by category"""
    return {
        'technical': TECHNICAL_SKILLS,
        'soft': SOFT_SKILLS,
        'certifications': CERTIFICATIONS
    }
