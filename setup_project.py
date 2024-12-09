import os

# Create project structure
directories = ['src', 'tests', 'docs', 'config']
for dir_name in directories:
    os.makedirs(os.path.join('f:/testepanilha', dir_name), exist_ok=True)
