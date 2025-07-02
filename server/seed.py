from app import app
from models import db, User, Project, Image, Downloads, BlogPost
from datetime import datetime

# It generates a slug from a blogpost title
def generate_slug(title):
    return title.lower().replace(' ', '-').replace(',', '').replace('.', '')

with app.app_context():
    db.session.query(User).delete()
    db.session.query(Project).delete()
    db.session.query(Image).delete()
    db.session.query(Downloads).delete()

    print('\nCYBERSPHERE SEEDING DATA')
    print('________________________________________________________________________________________________')

    print('\nAdding users...')
    users = [
        User(username=f'user{i}', email=f'user{i}@example.com', role='engineer', password='password') for i in range(1, 11)
    ]

    print('\nAdding Projects...')
    projects = [
        Project(title=f'Engineering Project {i}', description=f'Description of project {i}') for i in range(1, 11)
    ]

    print('\nAdding Images...  ')
    images = [
        Image(caption=f'Project {i} Image', url=f'/static/images/project{i}.jpg', is_in_gallery=True, project=projects[i-1]) for i in range(1, 11)
    ]
 
    print('\nAdding Downloads...  ')
    downloads = [
        Downloads(filename=f'File_{i}.pdf', file_url=f'/static/downloads/file_{i}.pdf', description=f'Description for file {i}') for i in range(1, 11)
    ]

    print('\nAdding Blog Posts...')
    blog_posts = [
        BlogPost(
            title=f'Blog Post {i}',
            slug=generate_slug(f'Blog Post {i}'),
            content=f'This is the detailed content of blog post {i}. It talks about engineering topic {i}.',
            author=f'Author {i}',
            image_url=f'/static/images/blog{i}.jpg',
            category='Insights' if i % 2 == 0 else 'News',
            # created_at=datetime.utcnow(),
            # updated_at=datetime.utcnow(),
            is_published=True
        ) for i in range(1, 11)
    ]

    db.session.add_all(users + projects + images + downloads + blog_posts)
    db.session.commit()

    print('________________________________________________________________________________________________')
    print('\nSeeded database with 10 users, projects, images, and downloads.')
    print('\n')
