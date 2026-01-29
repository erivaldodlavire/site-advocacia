from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Usuário administrador"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class SiteConfig(db.Model):
    __tablename__ = 'site_config'

    # CHAVE PRIMÁRIA (OBRIGATÓRIA!)
    id = db.Column(db.Integer, primary_key=True)

    # Informações básicas
    nome_escritorio = db.Column(db.String(255), default='')
    slogan = db.Column(db.String(255), default='')
    descricao_sobre = db.Column(db.Text, default='')

    # ... resto dos campos ...

    # Redes sociais
    instagram = db.Column(db.String(255), default='')
    facebook = db.Column(db.String(255), default='')
    linkedin = db.Column(db.String(255), default='')
    youtube = db.Column(db.String(255), default='')
    whatsapp_link = db.Column(db.String(255), default='')
    tiktok = db.Column(db.String(255), default='')
    twitter = db.Column(db.String(255), default='')
    pinterest = db.Column(db.String(255), default='')
    telegram = db.Column(db.String(255), default='')
    github = db.Column(db.String(255), default='')
    snapchat = db.Column(db.String(255), default='')
    twitch = db.Column(db.String(255), default='')
    discord = db.Column(db.String(255), default='')
    reddit = db.Column(db.String(255), default='')
    medium = db.Column(db.String(255), default='')

    # Sites customizados
    site_customizado_1_nome = db.Column(db.String(100), default='')
    site_customizado_1_url = db.Column(db.String(255), default='')
    site_customizado_2_nome = db.Column(db.String(100), default='')
    site_customizado_2_url = db.Column(db.String(255), default='')
    site_customizado_3_nome = db.Column(db.String(100), default='')
    site_customizado_3_url = db.Column(db.String(255), default='')

    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



    # Informações do escritório
    nome_escritorio = db.Column(db.String(200), default="Silva & Associados Advocacia")
    slogan = db.Column(db.String(300), default="Defendendo seus direitos com excelência")
    descricao_sobre = db.Column(db.Text, default="")

    # Advogado principal
    nome_advogado = db.Column(db.String(200), default="Dr. João Silva")
    oab = db.Column(db.String(100), default="OAB/SP 123.456")
    foto_perfil = db.Column(db.String(200), default="perfil.jpg")

    # Contato
    telefone = db.Column(db.String(50), default="(11) 98765-4321")
    whatsapp = db.Column(db.String(50), default="5511987654321")
    email = db.Column(db.String(100), default="contato@escritorio.com")
    endereco = db.Column(db.String(300), default="")
    cidade = db.Column(db.String(100), default="São Paulo - SP")
    cep = db.Column(db.String(20), default="")

    # Redes sociais
    instagram = db.Column(db.String(200), default="")
    facebook = db.Column(db.String(200), default="")
    linkedin = db.Column(db.String(200), default="")
    youtube = db.Column(db.String(200), default="")
    whatsapp_link = db.Column(db.String(200), default="")

    # Imagens
    imagem_fundo_hero = db.Column(db.String(200), default="hero-bg.jpg")

    # Cores (com degradês)
    cor_primaria = db.Column(db.String(20), default="#d4af37")
    cor_secundaria = db.Column(db.String(20), default="#1a1a2e")
    cor_destaque = db.Column(db.String(20), default="#16213e")
    cor_gradiente_1 = db.Column(db.String(20), default="#667eea")
    cor_gradiente_2 = db.Column(db.String(20), default="#764ba2")

    # Horário
    horario_atendimento = db.Column(db.String(100), default="Segunda a Sexta: 9h às 18h")

    # Tema ativo
    tema_ativo = db.Column(db.String(50), default="moderno")

    # N8N Webhook
    n8n_webhook_url = db.Column(db.String(500), default="")

    # Timestamps
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AreaAtuacao(db.Model):
    """Áreas de atuação do escritório"""
    id = db.Column(db.Integer, primary_key=True)
    icone = db.Column(db.String(100), default="⚖️")
    tipo_icone = db.Column(db.String(50), default="emoji")  # emoji, fontawesome, material
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    cor_icone = db.Column(db.String(20), default="#d4af37")
    ordem = db.Column(db.Integer, default=0)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class Depoimento(db.Model):
    """Depoimentos de clientes"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    profissao = db.Column(db.String(100), default="")
    texto = db.Column(db.Text, nullable=False)
    avaliacao = db.Column(db.Integer, default=5)
    email = db.Column(db.String(120), default="")
    telefone = db.Column(db.String(50), default="")
    icone = db.Column(db.String(100), default="⭐")
    tipo_icone = db.Column(db.String(50), default="emoji")
    cor_icone = db.Column(db.String(20), default="#FFD700")
    ordem = db.Column(db.Integer, default=0)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class RedeSocial(db.Model):
    """Redes sociais configuráveis"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    url = db.Column(db.String(300), default="")
    icone = db.Column(db.String(100), default="")
    tipo_icone = db.Column(db.String(50), default="fontawesome")
    cor = db.Column(db.String(20), default="#000000")
    ativo = db.Column(db.Boolean, default=True)
    ordem = db.Column(db.Integer, default=0)

class Tema(db.Model):
    """Temas/Templates prontos"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.Text)
    cor_primaria = db.Column(db.String(20))
    cor_secundaria = db.Column(db.String(20))
    cor_destaque = db.Column(db.String(20))
    cor_gradiente_1 = db.Column(db.String(20))
    cor_gradiente_2 = db.Column(db.String(20))
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class ContatoFormulario(db.Model):
    """Formulários de contato enviados"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(50), nullable=False)
    idade = db.Column(db.Integer)
    assunto = db.Column(db.String(200), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    tipo_caso = db.Column(db.String(100))  # Qual área de atuação
    lido = db.Column(db.Boolean, default=False)
    enviado_n8n = db.Column(db.Boolean, default=False)
    resposta_n8n = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class LogAuditoria(db.Model):
    """Log de alterações para auditoria"""
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    acao = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

# Sobre Nós
titulo_sobre = db.Column(db.String(100), default='Sobre Nós')
descricao_sobre_completa = db.Column(db.Text, default='')
anos_experiencia = db.Column(db.String(50), default='20+')
casos_resolvidos = db.Column(db.String(50), default='500+')
taxa_sucesso = db.Column(db.String(50), default='97%')
sobre_nos_ativo = db.Column(db.Boolean, default=True)
