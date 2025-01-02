import os

def create_dirs(base_path, dirs):
    for dir_path in dirs:
        full_path = os.path.join(base_path, dir_path)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            print(f"Created directory: {full_path}")

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    directories = [
        "tests",
        "tests/unit",
        "tests/integration",
        "app/static",
        "app/static/css",
        "app/static/js",
        "app/static/images",
        "docs/api",
        "docs/user_guide",
        "instance",
        "logs"
    ]
    
    create_dirs(base_path, directories)
