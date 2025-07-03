from flask import Blueprint, render_template, request, redirect, current_app, flash, url_for, session
import sqlite3
from app.models.database import query_db
from app.utils import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        # Verifica se os campos foram preenchidos
        if not email or not senha:
            flash('Por favor, preencha todos os campos.')
            return redirect(url_for('auth.login'))

        # Consulta ao banco de dados
        usuario = query_db(
            "SELECT * FROM usuarios WHERE email = ? AND senha = ?", 
            (email, senha), 
            one=True
        )

        if usuario:
            # Salva informações do usuário na sessão
            session['user_id'] = usuario['id']
            session['tipo_usuario'] = usuario['tipo_usuario']
            session['user_nome']= usuario['nome']
            session['classe_usuario'] = usuario['classe_usuario']
            
            classe_usuario= session.get('classe_usuario')
            session.permanent = True
            print (classe_usuario)
            return redirect(url_for('auth.login_redir'))

        # Verifica se o usuário foi encontrado
        else:
            flash('Credenciais inválidas.')
            return redirect(url_for('auth.login'))

        
    return render_template('login.html')


@auth_bp.route('/cadastrar', methods=['GET','POST'])
def cadastrar():
    if request.method=='POST':
        nome = request.form['nome']
        nome_format = nome.strip()  # Remove espaços em branco extras
        nome = nome_format  # Formata o nome para ter a primeira letra maiúscula
        cpf= request.form['cpf']
        email = request.form['email']
        senha = request.form['senha']
        tipo_usuario = request.form['tipo_usuario']
        classe_usuario = request.form['classe_usuario']

        exist = query_db("SELECT * FROM usuarios WHERE email = ?", (email,))
   

        if exist:
            flash("Este email já possui cadastro")

        else:

           
            # Insere o novo usuário no banco de dados
            conn = sqlite3.connect(current_app.config['DATABASE'])
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO usuarios (nome, cpf, email, senha, tipo_usuario, classe_usuario) VALUES (?, ?, ?, ?, ?, ?)",
                (nome,cpf, email, senha, tipo_usuario, classe_usuario)
            )
            conn.commit()
            conn.close()

            flash('Usuário cadastrado com sucesso! Faça login.')
            return redirect(url_for('auth.login'))

    return render_template('cadastrar.html')
    

@auth_bp.route('/logoff')
def logoff():
    session.clear()
    flash ('Desconectado com sucesso!')
    return redirect(url_for('auth.login'))


@auth_bp.route('/redirect')
def redirecionar_usuario():

    return render_template('generic/errata.html')



@auth_bp.route('/mudar_senha', methods=['GET', 'POST'])
def mudar_senha():
    if request.method == 'POST':
        email = request.form['email']
        novasenha = request.form['novasenha']
        
        usuario = query_db(
            "SELECT * FROM usuarios WHERE email = ?", 
            (email,), 
            one=True
        )

        if usuario:
           conn = sqlite3.connect(current_app.config['DATABASE'])
           cur = conn.cursor()
           cur.execute(
               "UPDATE USUARIOS SET senha = ? WHERE email = ?",
               (novasenha, email),
           )
           
        conn.commit()
        conn.close()
        
        flash('senha alterada!')
        
     
    return render_template('generic/mudar_senha.html')


@auth_bp.route('/auten_redir', methods=['GET', 'POST'])
@login_required
def redir_atent():
    
    tipo_usuario= session.get('tipo_usuario')
    classe_usuario= session.get('classe_usuario')

    if tipo_usuario == 'vendas':
        if classe_usuario == 'vendedor':
            corretor_resp= session.get('user_nome')
            print(corretor_resp)
            return redirect(url_for('cad.acompanhar_cnt',resp=corretor_resp))
        elif classe_usuario == 'supervisor':
            resp= None
            print(resp)
            return redirect(url_for('cad.acompanhar_cnt',resp=resp))
    elif tipo_usuario == 'cadastro':
        resp= None
        print(resp)
        return redirect(url_for('cad.acompanhar_cnt',resp=resp))
    elif tipo_usuario == 'administrativo':
        resp= None
        print(resp)
        return redirect(url_for('cad.acompanhar_cnt',resp=resp))
    elif tipo_usuario == 'financeiro':
        resp= None
        print(resp)
        return redirect(url_for('cad.acompanhar_cnt',resp=resp))
    
    else:
        flash('Tipo de usuário inválido.')
        print(tipo_usuario)
        return redirect(url_for('generic.home'))
    

@auth_bp.route('/login_redir')
def login_redir():
    tipo_usuario = session.get('tipo_usuario')
    classe_usuario= session.get("classe_usuario")
    if tipo_usuario == 'vendas':
        if classe_usuario == 'vendedor':
            return redirect(url_for('generic.home'))
        elif classe_usuario == 'supervisor':
            return redirect(url_for('gerencial.dashboard'))
    elif tipo_usuario == 'cadastro':
        return redirect(url_for('generic.home'))
    elif tipo_usuario == 'administrativo':
        return redirect(url_for('generic.home'))
    elif tipo_usuario == 'financeiro':
        return redirect(url_for('financeiro.home'))
    
    else:
        flash('Tipo de usuário inválido.')
        return redirect(url_for('generic.home'))