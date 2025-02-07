# app/routes/index.py
from flask import Blueprint, redirect, url_for

index_bp = Blueprint('index', __name__)

@index_bp.route('/')
def index():
    # 重定向到聊天页面
    return redirect(url_for('chat.index'))