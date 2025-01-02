from app import create_app
from app.faq.routes import init_socketio

app = create_app()
socketio = init_socketio(app)

if __name__ == '__main__':
    socketio.run(app, debug=True)
