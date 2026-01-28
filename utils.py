import os
import requests
from werkzeug.utils import secure_filename
from PIL import Image
from config_app import Config

ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS
UPLOAD_FOLDER = Config.UPLOAD_FOLDER

# Ícones para áreas de atuação
ICONES_AREAS = {
    "emoji": {
        "Direito Civil": "⚖️",
        "Direito Trabalhista": "👔",
        "Direito de Família": "👨‍👩‍👧",
        "Direito Criminal": "🏛️",
        "Direito Empresarial": "🏢",
        "Direito Imobiliário": "🏠",
        "Direito Tributário": "💰",
        "Direito Ambiental": "🌍",
        "Direito do Consumidor": "🛍️",
        "Direito Administrativo": "📋"
    },
    "fontawesome": {
        "Direito Civil": "fas fa-balance-scale",
        "Direito Trabalhista": "fas fa-briefcase",
        "Direito de Família": "fas fa-home",
        "Direito Criminal": "fas fa-gavel",
        "Direito Empresarial": "fas fa-building",
        "Direito Imobiliário": "fas fa-house-damage",
        "Direito Tributário": "fas fa-money-bill-wave",
        "Direito Ambiental": "fas fa-leaf",
        "Direito do Consumidor": "fas fa-shopping-cart",
        "Direito Administrativo": "fas fa-file-alt"
    }
}

# Ícones para redes sociais
ICONES_REDES_SOCIAIS = {
    "instagram": {
        "emoji": "📸",
        "fontawesome": "fab fa-instagram",
        "material": "photo_camera"
    },
    "facebook": {
        "emoji": "f",
        "fontawesome": "fab fa-facebook",
        "material": "facebook"
    },
    "linkedin": {
        "emoji": "💼",
        "fontawesome": "fab fa-linkedin",
        "material": "business"
    },
    "youtube": {
        "emoji": "📺",
        "fontawesome": "fab fa-youtube",
        "material": "video_library"
    },
    "whatsapp": {
        "emoji": "💬",
        "fontawesome": "fab fa-whatsapp",
        "material": "chat"
    }
}

# Temas prontos
TEMAS_PRONTOS = {
    "moderno": {
        "nome": "Moderno",
        "descricao": "Design moderno com cores vibrantes",
        "cor_primaria": "#667eea",
        "cor_secundaria": "#1a1a2e",
        "cor_destaque": "#16213e",
        "cor_gradiente_1": "#667eea",
        "cor_gradiente_2": "#764ba2"
    },
    "classico": {
        "nome": "Clássico",
        "descricao": "Design clássico e profissional",
        "cor_primaria": "#d4af37",
        "cor_secundaria": "#1a1a2e",
        "cor_destaque": "#16213e",
        "cor_gradiente_1": "#d4af37",
        "cor_gradiente_2": "#c9a227"
    },
    "minimalista": {
        "nome": "Minimalista",
        "descricao": "Design limpo e minimalista",
        "cor_primaria": "#000000",
        "cor_secundaria": "#ffffff",
        "cor_destaque": "#f0f0f0",
        "cor_gradiente_1": "#ffffff",
        "cor_gradiente_2": "#f0f0f0"
    },
    "vibrante": {
        "nome": "Vibrante",
        "descricao": "Cores vibrantes e modernas",
        "cor_primaria": "#ff6b6b",
        "cor_secundaria": "#1e1e2e",
        "cor_destaque": "#2d2d44",
        "cor_gradiente_1": "#ff6b6b",
        "cor_gradiente_2": "#ee5a6f"
    },
    "azul": {
        "nome": "Azul Profissional",
        "descricao": "Tons de azul para profissionalismo",
        "cor_primaria": "#0066cc",
        "cor_secundaria": "#003366",
        "cor_destaque": "#004d99",
        "cor_gradiente_1": "#0066cc",
        "cor_gradiente_2": "#0052a3"
    }
}

def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_extension(filename):
    """Pega a extensão do arquivo"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def save_upload_file(file, tipo_arquivo):
    """
    Salva arquivo de upload com validação
    tipo_arquivo: 'perfil' ou 'hero'
    Retorna: (filename, mensagem, sucesso)
    """
    if not file or file.filename == '':
        return None, "Nenhum arquivo selecionado", False

    if not allowed_file(file.filename):
        extensoes = ', '.join(ALLOWED_EXTENSIONS)
        return None, f"❌ Formato não permitido! Aceitos: {extensoes}", False

    try:
        filename = secure_filename(file.filename)
        ext = get_file_extension(filename)

        if tipo_arquivo == 'perfil':
            new_filename = f'perfil.{ext}'
        elif tipo_arquivo == 'hero':
            new_filename = f'hero-bg.{ext}'
        else:
            return None, "Tipo de arquivo inválido", False

        filepath = os.path.join(UPLOAD_FOLDER, new_filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        file.save(filepath)

        # Redimensionar e otimizar
        img = Image.open(filepath)
        if tipo_arquivo == 'perfil':
            img.thumbnail((500, 500), Image.Resampling.LANCZOS)
        else:
            img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)

        img.save(filepath, optimize=True, quality=85)

        return new_filename, "✅ Arquivo enviado com sucesso!", True

    except Exception as e:
        return None, f"❌ Erro ao processar imagem: {str(e)}", False

def enviar_para_n8n(dados_contato, webhook_url):
    """
    Envia dados de contato para N8N via webhook

    Args:
        dados_contato: dict com dados do formulário
        webhook_url: URL do webhook N8N

    Returns:
        (sucesso: bool, resposta: str)
    """
    if not webhook_url:
        return False, "Webhook N8N não configurado"

    try:
        payload = {
            "nome": dados_contato.get('nome'),
            "email": dados_contato.get('email'),
            "telefone": dados_contato.get('telefone'),
            "idade": dados_contato.get('idade'),
            "assunto": dados_contato.get('assunto'),
            "mensagem": dados_contato.get('mensagem'),
            "tipo_caso": dados_contato.get('tipo_caso'),
            "data_envio": dados_contato.get('data_envio'),
            "origem": "site_advocacia"
        }

        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10
        )

        if response.status_code in [200, 201]:
            return True, "Dados enviados para N8N com sucesso"
        else:
            return False, f"Erro N8N: {response.status_code}"

    except requests.exceptions.Timeout:
        return False, "Timeout ao conectar com N8N"
    except requests.exceptions.RequestException as e:
        return False, f"Erro ao conectar com N8N: {str(e)}"
    except Exception as e:
        return False, f"Erro desconhecido: {str(e)}"

def registrar_auditoria(usuario_id, acao, descricao=""):
    """Registra ações do admin para auditoria"""
    from models import LogAuditoria, db
    try:
        log = LogAuditoria(
            usuario_id=usuario_id,
            acao=acao,
            descricao=descricao
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Erro ao registrar auditoria: {e}")
