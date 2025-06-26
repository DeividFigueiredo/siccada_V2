from flask import Blueprint, render_template, request, sessions,session
from ..models.database import query_db
import re
from app.utils import login_required

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
@login_required
def index():
    nome= session.get('id')
    print(nome)
    return render_template('index.html')