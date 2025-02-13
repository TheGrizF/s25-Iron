from backend import create_app
from datetime import timedelta

app = create_app()

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_TYPE'] = 'filesystem'

if __name__ == '__main__':
    app.run(debug=True) 