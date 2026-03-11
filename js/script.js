// 1. CONEXÃO COM SUPABASE
const SUPABASE_URL = 'https://ueduzgoewlivkluiyqql.supabase.co';
const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVlZHV6Z29ld2xpdmtsdWl5cXFsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMxODAxMzAsImV4cCI6MjA4ODc1NjEzMH0.EM2s38El81fZYT-WVrxa7P_xX0e58EHQxdwreVgQecA';
const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

// 2. FUNÇÃO PRINCIPAL QUE APLICA OS DADOS NO HTML
function aplicarDadosNoSite(data) {
    if (!data) return;
    console.log("Aplicando dados no site...", data);

    // Aplicar Tema e Cabeçalho
    document.body.className = data.tema || 'tema-advogado';
    if(data.nome) {
        if(document.getElementById('edit-nome')) document.getElementById('edit-nome').innerText = data.nome;
        if(document.getElementById('edit-header-nome')) document.getElementById('edit-header-nome').innerText = data.nome;
    }
    if(data.oab && document.getElementById('edit-oab')) document.getElementById('edit-oab').innerText = data.oab;
    if(data.slogan && document.getElementById('edit-slogan')) document.getElementById('edit-slogan').innerText = data.slogan;
    if(data.sobre && document.getElementById('edit-sobre-texto')) document.getElementById('edit-sobre-texto').innerText = data.sobre;

    // Aplicar Contatos e Rodapé
    if(data.endereco && document.getElementById('edit-endereco')) document.getElementById('edit-endereco').innerText = data.endereco;
    if(data.tel && document.getElementById('edit-telefone')) document.getElementById('edit-telefone').innerText = data.tel;
    if(data.email && document.getElementById('edit-email')) document.getElementById('edit-email').innerText = data.email;
    if(data.horario && document.getElementById('edit-horario')) document.getElementById('edit-horario').innerText = data.horario;
    if(data.copy && document.getElementById('edit-copyright')) document.getElementById('edit-copyright').innerText = data.copy;

    // Fotos do Espaço
    if (data.fotos) {
        for(let i=1; i<=3; i++) {
            const img = document.getElementById(`img-espaco-${i}`);
            if(img && data.fotos[`f${i}`]) img.src = data.fotos[`f${i}`];
        }
    }

    // Áreas de Atuação Dinâmicas
    if(data.areas && data.areas.length > 0) {
        const container = document.getElementById('container-servicos');
        if(container) {
            container.innerHTML = data.areas.map(a => `
                <div class="card">
                    <i class="${a.i} gold-3d"></i>
                    <h3>${a.t}</h3>
                    <p>${a.d}</p>
                </div>`).join('');
        }
    }

    // Lógica de Ícones das Redes Sociais
    const getIcon = (u) => {
        if(u.includes('instagram')) return 'fab fa-instagram';
        if(u.includes('youtube')) return 'fab fa-youtube';
        if(u.includes('whatsapp') || u.includes('wa.me')) return 'fab fa-whatsapp';
        if(u.includes('linkedin')) return 'fab fa-linkedin';
        if(u.includes('facebook')) return 'fab fa-facebook';
        if(u.includes('x.com') || u.includes('twitter')) return 'fab fa-x-twitter';
        return 'fas fa-link';
    };

    const redesArea = document.getElementById('edit-redes-sociais-icones');
    const footerRedes = document.getElementById('edit-social-links-footer');
    
    if (data.redes) {
        const redesHTML = data.redes.filter(l => l && l.trim() !== '').map(l => `
            <a href="${l}" target="_blank" class="icon-3d"><i class="${getIcon(l)}"></i></a>`).join('');
        if(redesArea && redesHTML) redesArea.innerHTML = redesHTML;
        if(footerRedes && redesHTML) footerRedes.innerHTML = redesHTML;
    }

    // Publicações YT / Insta
    const pubArea = document.getElementById('container-publicacoes');
    if(pubArea && data.pubs) {
        const pubsValidos = data.pubs.filter(p => p.l && p.l.trim() !== '');
        
        if (pubsValidos.length > 0) {
            pubArea.innerHTML = pubsValidos.map(p => {
                let thumbContent = "";
                if (p.l.includes('instagram.com')) {
                    thumbContent = `<div class="insta-placeholder"><i class="fab fa-instagram"></i> Ver no Instagram</div>`;
                } else {
                    let videoId = "";
                    if (p.l.includes('shorts/')) {
                        videoId = p.l.split('shorts/')[1].split(/[?#]/)[0];
                    } else if (p.l.includes('v=')) {
                        videoId = p.l.split('v=')[1].split('&')[0];
                    } else if (p.l.includes('youtu.be/')) {
                        videoId = p.l.split('youtu.be/')[1].split(/[?#]/)[0];
                    }
                    thumbContent = `<img src="https://img.youtube.com/vi/${videoId}/hqdefault.jpg"><div class="play-overlay"><i class="fab fa-youtube"></i></div>`;
                }
                return `<div class="pub-container"><p class="pub-desc">${p.d}</p><div class="pub-item"><a href="${p.l}" target="_blank">${thumbContent}</a></div></div>`;
            }).join('');
        }
    }
}

// 3. FUNÇÃO PARA ENVIAR CONTATO (SALVA NO BANCO + ABRE WHATSAPP)
async function enviarLead(event) {
    event.preventDefault();
    const btn = event.target.querySelector('button');
    const originalText = btn.innerText;
    btn.innerText = "Enviando...";
    btn.disabled = true;

    // Captura dos dados
    const nome = document.getElementById('nome').value;
    const email = document.getElementById('email').value;
    const whatsapp = document.getElementById('telefone').value;
    const assunto = document.getElementById('titulo').value;
    const mensagem = document.getElementById('mensagem').value;

    const novoLead = { nome, email, whatsapp, assunto, mensagem };

    // 1. Salva no Supabase (Tabela site_leads)
    const { error } = await supabaseClient.from('site_leads').insert([novoLead]);

    if (!error) {
        // 2. Prepara e abre o WhatsApp da Dra. Gleyciane automaticamente
        const foneGley = "5519971284797"; 
        const textoMsg = `*Novo Contato pelo Site*\n\n*Nome:* ${nome}\n*Assunto:* ${assunto}\n*Mensagem:* ${mensagem}`;
        const urlWhatsApp = `https://api.whatsapp.com/send?phone=${foneGley}&text=${encodeURIComponent(textoMsg)}`;

        alert("Mensagem registrada com sucesso! Abrindo o WhatsApp para falar com a Dra...");
        window.open(urlWhatsApp, '_blank');
        event.target.reset();
    } else {
        console.error("Erro Supabase:", error.message);
        alert("Ocorreu um erro ao salvar sua mensagem. Por favor, utilize o botão flutuante do WhatsApp.");
    }
    
    btn.innerText = originalText;
    btn.disabled = false;
}

// 4. INICIALIZAÇÃO REFORÇADA E REGISTRO DE VISITA
async function inicializarSite() {
    console.log("Buscando dados no Supabase...");
    
    // Tenta buscar da nuvem (ID 1)
    const { data, error } = await supabaseClient
        .from('site_config')
        .select('*')
        .eq('id', 1)
        .single();

    if (data) {
        console.log("Dados da nuvem carregados!", data);
        aplicarDadosNoSite(data);
    } else {
        console.error("Falha ao carregar nuvem:", error);
        // Fallback local se a nuvem falhar
        const localData = JSON.parse(localStorage.getItem('siteData'));
        if (localData) aplicarDadosNoSite(localData);
    }

    // Registrar Analytics (Tabela site_visitas) - Garantindo que a RLS permita inserção
    supabaseClient.from('site_visitas').insert([{ 
        pagina: window.location.pathname, 
        origem: document.referrer || "Direto",
        dispositivo: window.innerWidth < 768 ? "Celular" : "Desktop"
    }]).then(({ error }) => {
        if (error) console.error("Erro ao registrar visita:", error.message);
        else console.log("Visita registrada com sucesso.");
    });
}

// Evento de carregamento robusto
window.addEventListener('load', inicializarSite);