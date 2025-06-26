from flask import Blueprint, render_template, session, redirect, url_for

generic_bp = Blueprint('generic', __name__, template_folder='../templates/generic')

@generic_bp.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('base1.html', usuario=session,usuario_nome=session.get('user_nome'))

@generic_bp.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('profile.html', usuario_nome=session.get('user_nome'),usuario_tipo=session.get('tipo_usuario'))

@generic_bp.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('settings.html', usuario=session)