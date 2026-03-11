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
        const url = u.toLowerCase();
        if(url.includes('instagram')) return 'fab fa-instagram';
        if(url.includes('youtube')) return 'fab fa-youtube';
        if(url.includes('tiktok')) return 'fab fa-tiktok';
        if(url.includes('whatsapp') || url.includes('wa.me')) return 'fab fa-whatsapp';
        if(url.includes('linkedin')) return 'fab fa-linkedin';
        if(url.includes('facebook')) return 'fab fa-facebook';
        if(url.includes('x.com') || url.includes('twitter')) return 'fab fa-x-twitter';
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

    // Publicações YT / Insta / TikTok
    const pubArea = document.getElementById('container-publicacoes');
    if(pubArea && data.pubs) {
        const pubsValidos = data.pubs.filter(p => p.l && p.l.trim() !== '');
        
        if (pubsValidos.length > 0) {
            pubArea.innerHTML = pubsValidos.map(p => {
                let thumbContent = "";
                const link = p.l.toLowerCase();

                if (link.includes('instagram.com')) {
                    // Card Personalizado Instagram
                    thumbContent = `
                        <div class="insta-placeholder" style="background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%); height: 180px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; border-radius: 8px;">
                            <i class="fab fa-instagram" style="font-size: 2.5rem; margin-bottom: 10px;"></i>
                            <span style="font-weight: bold;">Ver no Instagram</span>
                        </div>`;
                } else if (link.includes('tiktok.com')) {
                    // Card Personalizado TikTok
                    thumbContent = `
                        <div class="tiktok-placeholder" style="background: #000; height: 180px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: white; border-radius: 8px; border: 1px solid #fe2c55;">
                            <i class="fab fa-tiktok" style="font-size: 2.5rem; margin-bottom: 10px; color: #25f4ee; text-shadow: 2px 0 #fe2c55;"></i>
                            <span style="font-weight: bold;">Ver no TikTok</span>
                        </div>`;
                } else if (link.includes('youtube.com') || link.includes('youtu.be')) {
                    // Thumbnail YouTube
                    let videoId = "";
                    if (link.includes('shorts/')) {
                        videoId = p.l.split('shorts/')[1].split(/[?#]/)[0];
                    } else if (link.includes('v=')) {
                        videoId = p.l.split('v=')[1].split('&')[0];
                    } else if (link.includes('youtu.be/')) {
                        videoId = p.l.split('youtu.be/')[1].split(/[?#]/)[0];
                    }
                    thumbContent = `
                        <div style="position: relative;">
                            <img src="https://img.youtube.com/vi/${videoId}/hqdefault.jpg" style="width: 100%; border-radius: 8px; display: block;">
                            <div class="play-overlay"><i class="fab fa-youtube"></i></div>
                        </div>`;
                } else {
                    // Link Genérico
                    thumbContent = `
                        <div style="background: #333; height: 180px; display: flex; align-items: center; justify-content: center; color: white; border-radius: 8px;">
                            <i class="fas fa-link" style="font-size: 2rem;"></i>
                        </div>`;
                }

                return `
                    <div class="pub-container">
                        <p class="pub-desc">${p.d}</p>
                        <div class="pub-item">
                            <a href="${p.l}" target="_blank">${thumbContent}</a>
                        </div>
                    </div>`;
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