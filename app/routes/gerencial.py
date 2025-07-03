from flask import Blueprint, render_template, request, session,redirect,url_for, jsonify, current_app, flash
from ..models.database import query_db
from datetime import datetime
import re
import sqlite3
import csv
import io
from flask import Response, request

from app.utils import login_required, acesso

gerencial_bp = Blueprint('gerencial', __name__)

@gerencial_bp.route('/dashboard')
def dashboard():
    # Supondo que a coluna 2 é data_venda (ajuste se necessário)
    dados_tipo_plano = query_db("SELECT tipo_produto, COUNT(*) FROM venda GROUP BY tipo_produto")
    labels_tipo_plano = [row[0] for row in dados_tipo_plano]
    valores_tipo_plano = [row[1] for row in dados_tipo_plano]

    dados_corretor = query_db("SELECT corretor_resp, COUNT(*) FROM venda GROUP BY corretor_resp")
    labels_corretor = [row[0] for row in dados_corretor]
    valores_corretor = [row[1] for row in dados_corretor]

    dados_evolucao = query_db("SELECT strftime('%Y-%m', data_venda), SUM(valor_venda) FROM venda GROUP BY 1 ORDER BY 1")
    labels_evolucao = [row[0] for row in dados_evolucao]
    valores_evolucao = [row[1] for row in dados_evolucao]

    ultimas_vendas = query_db("SELECT * FROM venda ORDER BY data_venda DESC LIMIT 10")

    return render_template(
        'gerencial/dashboard.html',
        labels_tipo_plano=labels_tipo_plano,
        valores_tipo_plano=valores_tipo_plano,
        labels_corretor=labels_corretor,
        valores_corretor=valores_corretor,
        labels_evolucao=labels_evolucao,
        valores_evolucao=valores_evolucao,
        ultimas_vendas=ultimas_vendas
    )