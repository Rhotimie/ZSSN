import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


from zombie.app import app

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)


