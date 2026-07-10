from dotenv import load_dotenv
load_dotenv()

from pkg import app

if __name__ == '__main__':
    app.run(debug=True, port=3000)