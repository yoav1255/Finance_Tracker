from website import create_app
from dotenv import load_dotenv
import os

load_dotenv()
FMP_API_KEY = os.getenv('FMP_API_KEY')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
