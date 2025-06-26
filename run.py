from app import create_app

from flask import redirect,url_for


app = create_app()

@app.route('/')
def redirect_login():
    return redirect(url_for('auth.login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
