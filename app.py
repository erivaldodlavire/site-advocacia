from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, SiteConfig, AreaAtuacao, Depoimento, RedeSocial, Tema, LogAuditoria, ContatoFormulario
from utils import save_upload_file, registrar_auditoria, enviar_para_n8n, ICONES_AREAS, ICONES_REDES_SOCIAIS, TEMAS_PRONTOS
from config_app import config
import os
from datetime import datetime

# Inicializar Flask
app = Flask(__name__)
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Inicializar extensões
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Criar pastas necessárias
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# =============================================
# INICIALIZAR BANCO DE DADOS
# =============================================

with app.app_context():
    db.create_all()

    # Criar usuário admin padrão
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@escritorio.com')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Usuário admin criado!")
        print("📝 Login: admin")
        print("🔐 Senha: admin123")
        print("⚠️  MUDE A SENHA APÓS O PRIMEIRO LOGIN!")

   # ==========================================
# INICIALIZAR BANCO DE DADOS
# ==========================================

def init_db():
    """Inicializa o banco de dados com dados padrão"""
    with app.app_context():
        db.create_all()

        # Criar usuário admin padrão
        if not User.query.first():
            admin = User(username='admin', email='admin@advocacia.com')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuário admin criado!")

        # Criar configuração padrão
        if not SiteConfig.query.first():
            config_site = SiteConfig(
                nome_escritorio="Araujo & Advocacia",
                slogan="Defendendo seus direitos com excelência",
                nome_advogado="Gleyciane Bento de Araújo",
                oab="OAB/SP 123456",
                telefone="(19) 9 7128-4797",
                whatsapp="5519971284797",
                email="contato@araujoadv.com.br",
                endereco="Rua Exemplo, 123",
                cidade="Campinas",
                cep="13000-000",
                horario_atendimento="Segunda a Sexta, 9h às 18h",
                instagram="https://www.instagram.com/gleycianearaujo.adv/",
                facebook="https://www.facebook.com/gleyciane.araujo.2025",
                descricao_sobre="Com mais de 15 anos de experiência em direito civil, criminal e previdenciário, a Dra. Gleyciane Bento de Araújo dedica-se a defender os direitos de seus clientes com excelência e profissionalismo.",
                cor_primaria="#d4af37",
                cor_secundaria="#1a1a2e",
                cor_destaque="#16213e",
                cor_gradiente_1="#667eea",
                cor_gradiente_2="#764ba2",
                foto_perfil="perfil.jpg",
                imagem_fundo_hero="hero-bg.jpg"
            )
            db.session.add(config_site)
            db.session.commit()
            print("✅ Configuração padrão criada!")

        # Criar temas prontos
        for tema_key, tema_data in TEMAS_PRONTOS.items():
            if not Tema.query.filter_by(nome=tema_key).first():
                tema = Tema(
                    nome=tema_key,
                    cor_primaria=tema_data['cor_primaria'],
                    cor_secundaria=tema_data['cor_secundaria'],
                    cor_destaque=tema_data['cor_destaque'],
                    cor_gradiente_1=tema_data['cor_gradiente_1'],
                    cor_gradiente_2=tema_data['cor_gradiente_2']
                )
                db.session.add(tema)
        db.session.commit()
        print("✅ Temas prontos carregados!")

        # Criar áreas de atuação padrão
        if AreaAtuacao.query.count() == 0:
            areas_padrao = [
                {
                    'titulo': 'Direito Civil',
                    'descricao': 'Contratos, indenizações, propriedade e direitos civis em geral.',
                    'icone': '📋'
                },
                {
                    'titulo': 'Direito Criminal',
                    'descricao': 'Defesa em processos criminais e consultoria jurídica penal.',
                    'icone': '⚖️'
                },
                {
                    'titulo': 'Direito Previdenciário',
                    'descricao': 'Aposentadorias, pensões e benefícios do INSS.',
                    'icone': '📊'
                },
                {
                    'titulo': 'Direito de Família',
                    'descricao': 'Divórcio, guarda de filhos, alimentos e pensão alimentícia.',
                    'icone': '👨‍👩‍👧‍👦'
                }
            ]

            for area_data in areas_padrao:
                area = AreaAtuacao(
                    titulo=area_data['titulo'],
                    descricao=area_data['descricao'],
                    icone=area_data['icone'],
                    tipo_icone='emoji',
                    cor_icone='#d4af37',
                    ordem=AreaAtuacao.query.count()
                )
                db.session.add(area)
            db.session.commit()
            print("✅ Áreas de atuação carregadas!")

# =============================================
# ROTAS PÚBLICAS (SITE)
# =============================================


@app.route('/')
def index():
    config_site = SiteConfig.query.first()
    areas = AreaAtuacao.query.order_by(AreaAtuacao.ordem).all()
    depoimentos = Depoimento.query.order_by(Depoimento.ordem).all()
    redes = RedeSocial.query.filter_by(ativo=True).order_by(RedeSocial.ordem).all()
    return render_template('index.html', config=config_site, areas=areas, 
                           depoimentos=depoimentos, redes=redes)

@app.route('/contato', methods=['POST'])
def contato():
    """Recebe dados do formulário de contato"""
    try:
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        telefone = request.form.get('telefone', '').strip()
        idade = request.form.get('idade', type=int, default=None)
        assunto = request.form.get('assunto', '').strip()
        mensagem = request.form.get('mensagem', '').strip()
        tipo_caso = request.form.get('tipo_caso', '').strip()

        # Validar campos obrigatórios
        if not all([nome, email, telefone, assunto, mensagem]):
            flash('❌ Preencha todos os campos obrigatórios!', 'danger')
            return redirect(url_for('index'))

        # Salvar no banco de dados
        contato = ContatoFormulario(
            nome=nome,
            email=email,
            telefone=telefone,
            idade=idade,
            assunto=assunto,
            mensagem=mensagem,
            tipo_caso=tipo_caso
        )
        db.session.add(contato)
        db.session.commit()

        # Preparar dados para N8N
        config_site = SiteConfig.query.first()
        dados_n8n = {
            'nome': nome,
            'email': email,
            'telefone': telefone,
            'idade': idade,
            'assunto': assunto,
            'mensagem': mensagem,
            'tipo_caso': tipo_caso,
            'data_envio': datetime.utcnow().isoformat()
        }

        # Enviar para N8N se configurado
        if config_site.n8n_webhook_url:
            sucesso_n8n, msg_n8n = enviar_para_n8n(dados_n8n, config_site.n8n_webhook_url)
            contato.enviado_n8n = sucesso_n8n
            contato.resposta_n8n = msg_n8n
            db.session.commit()
            print(f"📤 N8N: {msg_n8n}")

        flash('✅ Mensagem enviada com sucesso! Entraremos em contato em breve.', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        print(f"❌ Erro ao processar contato: {e}")
        flash('❌ Erro ao enviar mensagem. Tente novamente.', 'danger')
        return redirect(url_for('index'))

# =============================================
# ROTAS DE AUTENTICAÇÃO
# =============================================


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=request.form.get('remember'))
            registrar_auditoria(user.id, 'LOGIN', f'Usuário {username} realizou login')
            flash('✅ Login realizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('❌ Usuário ou senha incorretos!', 'danger')

    return render_template('admin/login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    registrar_auditoria(current_user.id, 'LOGOUT', f'Usuário {current_user.username} realizou logout')
    logout_user()
    flash('✅ Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

# =============================================
# ROTAS DO PAINEL ADMIN
# =============================================

@app.route('/admin')
@login_required
def admin_dashboard():
    config_site = SiteConfig.query.first()
    areas_count = AreaAtuacao.query.count()
    depoimentos_count = Depoimento.query.count()
    contatos_count = ContatoFormulario.query.count()
    contatos_nao_lidos = ContatoFormulario.query.filter_by(lido=False).count()
    logs_recentes = LogAuditoria.query.order_by(LogAuditoria.criado_em.desc()).limit(5).all()

    return render_template('admin/dashboard.html', 
                         config=config_site,
                         areas_count=areas_count,
                         depoimentos_count=depoimentos_count,
                         contatos_count=contatos_count,
                         contatos_nao_lidos=contatos_nao_lidos,
                         logs_recentes=logs_recentes)

@app.route('/admin/configuracoes', methods=['GET', 'POST'])
@login_required
def admin_config():
    config_site = SiteConfig.query.first()
    temas = Tema.query.filter_by(ativo=True).all()
    icones_areas = ICONES_AREAS
    icones_redes = ICONES_REDES_SOCIAIS

    if request.method == 'POST':
        # Informações básicas
        config_site.nome_escritorio = request.form.get('nome_escritorio')
        config_site.slogan = request.form.get('slogan')
        config_site.descricao_sobre = request.form.get('descricao_sobre')
        

        # Advogado
        config_site.nome_advogado = request.form.get('nome_advogado')
        config_site.oab = request.form.get('oab')

        # Contato
        config_site.telefone = request.form.get('telefone')
        config_site.whatsapp = request.form.get('whatsapp')
        config_site.email = request.form.get('email')
        config_site.endereco = request.form.get('endereco')
        config_site.cidade = request.form.get('cidade')
        config_site.cep = request.form.get('cep')
        config_site.horario_atendimento = request.form.get('horario_atendimento')

        # Redes sociais
        config_site.instagram = request.form.get('instagram')
        config_site.facebook = request.form.get('facebook')
        config_site.linkedin = request.form.get('linkedin')
        config_site.youtube = request.form.get('youtube')
        config_site.whatsapp_link = request.form.get('whatsapp_link')

        # Cores
        config_site.cor_primaria = request.form.get('cor_primaria', '#d4af37')
        config_site.cor_secundaria = request.form.get('cor_secundaria', '#1a1a2e')
        config_site.cor_destaque = request.form.get('cor_destaque', '#16213e')
        config_site.cor_gradiente_1 = request.form.get('cor_gradiente_1', '#667eea')
        config_site.cor_gradiente_2 = request.form.get('cor_gradiente_2', '#764ba2')

        # N8N Webhook
        config_site.n8n_webhook_url = request.form.get('n8n_webhook_url', '')

        config_site.atualizado_em = datetime.utcnow()
        db.session.commit()

        registrar_auditoria(current_user.id, 'ATUALIZAR_CONFIG', 'Configurações do site atualizadas')
        flash('✅ Configurações atualizadas com sucesso!', 'success')
        return redirect(url_for('admin_config'))

    return render_template('admin/configuracoes.html', 
                         config=config_site, 
                         temas=temas,
                         icones_areas=icones_areas,
                         icones_redes=icones_redes)

@app.route('/admin/upload-imagem', methods=['POST'])
@login_required
def admin_upload_imagem():
    config_site = SiteConfig.query.first()
    tipo = request.form.get('tipo')

    if 'file' not in request.files:
        return jsonify({'sucesso': False, 'mensagem': '❌ Nenhum arquivo selecionado'}), 400

    file = request.files['file']
    filename, mensagem, sucesso = save_upload_file(file, tipo)

    if sucesso:
        if tipo == 'perfil':
            config_site.foto_perfil = filename
        elif tipo == 'hero':
            config_site.imagem_fundo_hero = filename

        config_site.atualizado_em = datetime.utcnow()
        db.session.commit()

        registrar_auditoria(current_user.id, 'UPLOAD_IMAGEM', f'Imagem {tipo} enviada')
        return jsonify({'sucesso': True, 'mensagem': mensagem, 'arquivo': filename})
    else:
        return jsonify({'sucesso': False, 'mensagem': mensagem}), 400

@app.route('/admin/aplicar-tema/<int:tema_id>', methods=['POST'])
@login_required
def admin_aplicar_tema(tema_id):
    tema = Tema.query.get_or_404(tema_id)
    config_site = SiteConfig.query.first()

    config_site.cor_primaria = tema.cor_primaria
    config_site.cor_secundaria = tema.cor_secundaria
    config_site.cor_destaque = tema.cor_destaque
    config_site.cor_gradiente_1 = tema.cor_gradiente_1
    config_site.cor_gradiente_2 = tema.cor_gradiente_2
    config_site.tema_ativo = tema.nome
    config_site.atualizado_em = datetime.utcnow()

    db.session.commit()

    registrar_auditoria(current_user.id, 'APLICAR_TEMA', f'Tema {tema.nome} aplicado')
    flash(f'✅ Tema "{tema.nome}" aplicado com sucesso!', 'success')
    return redirect(url_for('admin_config'))

# =============================================
# ROTAS DE ÁREAS DE ATUAÇÃO
# =============================================

@app.route('/admin/areas', methods=['GET', 'POST'])
@login_required
def admin_areas():
    icones = ICONES_AREAS

    if request.method == 'POST':
        area = AreaAtuacao(
            icone=request.form.get('icone', '⚖️'),
            tipo_icone=request.form.get('tipo_icone', 'emoji'),
            titulo=request.form.get('titulo'),
            descricao=request.form.get('descricao'),
            cor_icone=request.form.get('cor_icone', '#d4af37'),
            ordem=AreaAtuacao.query.count()
        )
        db.session.add(area)
        db.session.commit()

        registrar_auditoria(current_user.id, 'CRIAR_AREA', f'Área {area.titulo} criada')
        flash(f'✅ Área "{area.titulo}" adicionada!', 'success')
        return redirect(url_for('admin_areas'))

    areas = AreaAtuacao.query.order_by(AreaAtuacao.ordem).all()
    return render_template('admin/areas.html', areas=areas, icones=icones)

@app.route('/admin/areas/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def admin_editar_area(id):
    area = AreaAtuacao.query.get_or_404(id)
    icones = ICONES_AREAS

    if request.method == 'POST':
        area.icone = request.form.get('icone')
        area.tipo_icone = request.form.get('tipo_icone')
        area.titulo = request.form.get('titulo')
        area.descricao = request.form.get('descricao')
        area.cor_icone = request.form.get('cor_icone')

        db.session.commit()
        registrar_auditoria(current_user.id, 'EDITAR_AREA', f'Área {area.titulo} editada')
        flash(f'✅ Área "{area.titulo}" atualizada!', 'success')
        return redirect(url_for('admin_areas'))

    return render_template('admin/editar_area.html', area=area, icones=icones)

@app.route('/admin/areas/<int:id>/deletar', methods=['POST'])
@login_required
def admin_deletar_area(id):
    area = AreaAtuacao.query.get_or_404(id)
    titulo = area.titulo
    db.session.delete(area)
    db.session.commit()

    registrar_auditoria(current_user.id, 'DELETAR_AREA', f'Área {titulo} deletada')
    flash(f'✅ Área "{titulo}" removida!', 'success')
    return redirect(url_for('admin_areas'))

# =============================================
# ROTAS DE DEPOIMENTOS
# =============================================

@app.route('/admin/depoimentos', methods=['GET', 'POST'])
@login_required
def admin_depoimentos():
    if request.method == 'POST':
        depoimento = Depoimento(
            nome=request.form.get('nome'),
            profissao=request.form.get('profissao'),
            texto=request.form.get('texto'),
            email=request.form.get('email'),
            telefone=request.form.get('telefone'),
            avaliacao=int(request.form.get('avaliacao', 5)),
            icone=request.form.get('icone', '⭐'),
            tipo_icone=request.form.get('tipo_icone', 'emoji'),
            cor_icone=request.form.get('cor_icone', '#FFD700'),
            ordem=Depoimento.query.count()
        )
        db.session.add(depoimento)
        db.session.commit()

        registrar_auditoria(current_user.id, 'CRIAR_DEPOIMENTO', f'Depoimento de {depoimento.nome} criado')
        flash(f'✅ Depoimento de "{depoimento.nome}" adicionado!', 'success')
        return redirect(url_for('admin_depoimentos'))

    depoimentos = Depoimento.query.order_by(Depoimento.ordem).all()
    return render_template('admin/depoimentos.html', depoimentos=depoimentos)

@app.route('/admin/depoimentos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def admin_editar_depoimento(id):
    depoimento = Depoimento.query.get_or_404(id)

    if request.method == 'POST':
        depoimento.nome = request.form.get('nome')
        depoimento.profissao = request.form.get('profissao')
        depoimento.texto = request.form.get('texto')
        depoimento.email = request.form.get('email')
        depoimento.telefone = request.form.get('telefone')
        depoimento.avaliacao = int(request.form.get('avaliacao', 5))
        depoimento.icone = request.form.get('icone')
        depoimento.tipo_icone = request.form.get('tipo_icone')
        depoimento.cor_icone = request.form.get('cor_icone')

        db.session.commit()
        registrar_auditoria(current_user.id, 'EDITAR_DEPOIMENTO', f'Depoimento de {depoimento.nome} editado')
        flash(f'✅ Depoimento de "{depoimento.nome}" atualizado!', 'success')
        return redirect(url_for('admin_depoimentos'))

    return render_template('admin/editar_depoimento.html', depoimento=depoimento)

@app.route('/admin/depoimentos/<int:id>/deletar', methods=['POST'])
@login_required
def admin_deletar_depoimento(id):
    depoimento = Depoimento.query.get_or_404(id)
    nome = depoimento.nome
    db.session.delete(depoimento)
    db.session.commit()

    registrar_auditoria(current_user.id, 'DELETAR_DEPOIMENTO', f'Depoimento de {nome} deletado')
    flash(f'✅ Depoimento de "{nome}" removido!', 'success')
    return redirect(url_for('admin_depoimentos'))

# =============================================
# ROTAS DE REDES SOCIAIS
# =============================================

@app.route('/admin/redes-sociais', methods=['GET', 'POST'])
@login_required
def admin_redes_sociais():
    config_site = SiteConfig.query.first()
    icones = ICONES_REDES_SOCIAIS

    if request.method == 'POST':
        # Redes sociais principais
        config_site.instagram = request.form.get('instagram', '')
        config_site.facebook = request.form.get('facebook', '')
        config_site.linkedin = request.form.get('linkedin', '')
        config_site.youtube = request.form.get('youtube', '')
        config_site.whatsapp_link = request.form.get('whatsapp_link', '')
        config_site.tiktok = request.form.get('tiktok', '')
        config_site.twitter = request.form.get('twitter', '')
        config_site.pinterest = request.form.get('pinterest', '')
        config_site.telegram = request.form.get('telegram', '')
        config_site.github = request.form.get('github', '')

        # Mais 5 redes sociais
        config_site.snapchat = request.form.get('snapchat', '')
        config_site.twitch = request.form.get('twitch', '')
        config_site.discord = request.form.get('discord', '')
        config_site.reddit = request.form.get('reddit', '')
        config_site.medium = request.form.get('medium', '')

        # Sites customizados
        config_site.site_customizado_1_nome = request.form.get('site_customizado_1_nome', '')
        config_site.site_customizado_1_url = request.form.get('site_customizado_1_url', '')
        config_site.site_customizado_2_nome = request.form.get('site_customizado_2_nome', '')
        config_site.site_customizado_2_url = request.form.get('site_customizado_2_url', '')
        config_site.site_customizado_3_nome = request.form.get('site_customizado_3_nome', '')
        config_site.site_customizado_3_url = request.form.get('site_customizado_3_url', '')

        config_site.atualizado_em = datetime.utcnow()
        db.session.commit()
        registrar_auditoria(current_user.id, 'ATUALIZAR_REDES', 'Redes sociais e sites atualizados')
        flash('✅ Redes sociais e sites atualizados com sucesso!', 'success')
        return redirect(url_for('admin_redes_sociais'))

    return render_template('admin/redes_sociais.html', 
                         config=config_site, 
                         icones=icones)


# =============================================
# ROTAS DE CONTATOS
# =============================================

@app.route('/admin/contatos')
@login_required
def admin_contatos():
    contatos = ContatoFormulario.query.order_by(ContatoFormulario.criado_em.desc()).all()
    return render_template('admin/contatos.html', contatos=contatos)

@app.route('/admin/contatos/<int:id>')
@login_required
def admin_ver_contato(id):
    contato = ContatoFormulario.query.get_or_404(id)
    contato.lido = True
    db.session.commit()
    return render_template('admin/ver_contato.html', contato=contato)

@app.route('/admin/contatos/<int:id>/deletar', methods=['POST'])
@login_required
def admin_deletar_contato(id):
    contato = ContatoFormulario.query.get_or_404(id)
    db.session.delete(contato)
    db.session.commit()

    registrar_auditoria(current_user.id, 'DELETAR_CONTATO', f'Contato de {contato.nome} deletado')
    flash('✅ Contato removido!', 'success')
    return redirect(url_for('admin_contatos'))

# =============================================
# ROTAS DE AUDITORIA
# =============================================

@app.route('/admin/auditoria')
@login_required
def admin_auditoria():
    logs = LogAuditoria.query.order_by(LogAuditoria.criado_em.desc()).all()
    return render_template('admin/auditoria.html', logs=logs)

# ==========================================
# TRATAMENTO DE ERROS
# ==========================================

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
# Inicializar banco de dados
init_db()





if __name__ == '__main__':
    app.run(debug=True)
