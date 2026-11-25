# -*- coding: utf-8 -*-
"""Gera o workbook digital do CM4AI.
   python3 build.py            -> site do participante em docs/
   python3 build.py professor  -> arquivo único da versão do professor em professor/
"""
import sys, os, base64, html, json, shutil

RAIZ0 = os.path.dirname(os.path.abspath(__file__))
_c = json.load(open(os.path.join(RAIZ0, "conteudo.json"), encoding="utf-8"))
ENCONTROS, CAMINHO = _c["encontros"], _c["caminho"]
_n = os.path.join(RAIZ0, "professor_notas.json")
if os.path.exists(_n):
    _notas = json.load(open(_n, encoding="utf-8"))
    for _e in ENCONTROS:
        for _b in _e["blocos"]:
            for _i in _b["itens"]:
                _i.update(_notas.get(_i.get("id"), {}))

PROF = len(sys.argv) > 1 and sys.argv[1] == "professor"
REPO = "https://github.com/ginoterentimjr/cm4ai-workbook"
RAIZ = os.path.dirname(os.path.abspath(__file__))
CSS = open(os.path.join(RAIZ, "src", "estilo.css"), encoding="utf-8").read()
JS = "\n".join(open(os.path.join(RAIZ, "src", f), encoding="utf-8").read() for f in ("app.js", "conta.js", "duvidas.js"))
PAINEL_JS = open(os.path.join(RAIZ, "src", "painel.js"), encoding="utf-8").read()
API = open(os.path.join(RAIZ, "api.txt"), encoding="utf-8").read().strip() if os.path.exists(os.path.join(RAIZ, "api.txt")) else ""
ICON_DIR = os.path.join(RAIZ, "src", "icons")

def img_url(nome):
    """Endereço da imagem: arquivo no site, embutida na versão do professor."""
    if PROF:
        return "data:image/jpeg;base64," + base64.b64encode(open(os.path.join(RAIZ, "src", "img", nome), "rb").read()).decode()
    return f"img/{nome}"


def icone(nome, cor="#FFFFFF", tam=28, sw=1.8):
    import re as _re
    t = open(os.path.join(ICON_DIR, nome + ".svg"), encoding="utf-8").read()
    t = _re.sub(r"<!--.*?-->", "", t, flags=_re.S)
    t = t.replace('width="24"', f'width="{tam}"', 1).replace('height="24"', f'height="{tam}"', 1)
    return t.replace('stroke="currentColor"', f'stroke="{cor}"').replace('stroke-width="2"', f'stroke-width="{sw}"').replace("\n", "")

IC_BLOCO = {"Abertura": "door-open", "O paradoxo da IA": "trending-up", "Mudança e transição": "route", "A curva de Satir": "activity", "A curva de Satir e o ciclo": "activity", "Diagnóstico de prontidão": "stethoscope", "Fechamento": "messages-square",
            "Leitura do diagnóstico em grupo": "search", "O mapa de pessoas": "users", "Práticas de geração de insights": "link-2", "Plano de coleta de insights": "clipboard-list",
            "Dos registros aos insights": "lightbulb", "O mapa de forças": "scale", "Opções de mudança": "list-checks", "A próxima aposta": "flag",
            "Da aposta à hipótese": "flask-conical", "A medida e o critério de revisão": "gauge", "O plano do experimento": "calendar-range", "O portfólio de experimentos": "layout-grid",
            "O canvas estratégico da mudança": "layout-grid", "A rede de campeões": "network", "O painel de adoção": "gauge", "O roteiro de sustentabilidade": "waves", "Fechamento e certificação": "award"}
# Materiais de cada encontro: o quadro do Miro e os slides em PDF. O PDF entra só depois do encontro (22h de Brasília).
SLIDES = {1: ("CM4AI-Online_E1_Slides-da-Turma_v4.pdf", "2026-11-18T22:00:00-03:00"),
          2: ("CM4AI-Online_E2_Slides-da-Turma_v4.pdf", "2026-11-19T22:00:00-03:00"),
          3: (None, "2026-11-25T22:00:00-03:00"),
          4: (None, "2026-11-26T22:00:00-03:00"),
          5: (None, "2026-11-27T22:00:00-03:00")}


def materiais_html(enc):
    n = enc["n"]
    arq = SLIDES[n][0]
    miro = (f'<a class="mat" href="{enc["miro"]}" target="_blank" rel="noopener">'
            f'<span class="disco" style="--tom:{enc["tom"]}">{icone("layout-grid")}</span>'
            f'<span><span class="mat__k">QUADRO DO ENCONTRO {n}</span><b>Abrir o quadro do Miro</b><i>Todas as áreas do encontro, com as instruções de cada atividade</i></span></a>')
    if PROF:
        return f'<h3>Materiais do encontro</h3><div class="mats">{miro}</div>'
    if arq:
        sl = (f'<a class="mat" href="materiais/{arq}" download>'
              f'<span class="disco" style="--tom:{enc["tom"]}">{icone("presentation")}</span>'
              f'<span><span class="mat__k">SLIDES DO ENCONTRO {n} · PDF</span><b>Baixar os slides</b><i>O arquivo completo do encontro, para consulta e estudo</i></span></a>')
    else:
        sl = (f'<div class="mat mat--espera">'
              f'<span class="disco" style="--tom:#9A8F86">{icone("presentation")}</span>'
              f'<span><span class="mat__k">SLIDES DO ENCONTRO {n} · PDF</span><b>Disponíveis ao fim do encontro</b><i>O arquivo entra aqui depois das 22h de {e(enc["data"])}</i></span></div>')
    return f'<h3>Materiais do encontro</h3><div class="mats">{miro}{sl}</div>'


IC_ENC = {1: "compass", 2: "users", 3: "lightbulb", 4: "flask-conical", 5: "flag"}
FOTO_ENC = {1: "e1.jpg", 2: "e2.jpg", 3: "e3.jpg", 4: "e4.jpg", 5: "e5.jpg"}
e = html.escape


def campo(c):
    """c = dict(k, rotulo, tipo, dica, ...) -> html do campo."""
    k, tipo = c["k"], c.get("tipo", "area")
    rot = f'<label for="{k}"><b>{e(c["rotulo"])}</b></label>' if c.get("rotulo") else ""
    dica = f'<p class="dica">{e(c["dica"])}</p>' if c.get("dica") else ""
    if tipo == "area":
        corpo = f'<textarea id="{k}" data-k="{k}" rows="{c.get("linhas", 3)}" placeholder="{e(c.get("ph", ""))}"></textarea>'
    elif tipo == "texto":
        corpo = f'<input type="text" id="{k}" data-k="{k}" placeholder="{e(c.get("ph", ""))}">'
    elif tipo == "escolha":
        ops = "".join(f"<option>{e(o)}</option>" for o in [""] + c["opcoes"])
        corpo = f'<select id="{k}" data-k="{k}">{ops}</select>'
    elif tipo == "espelho":
        vz = c.get("vazio", "Ainda sem registro no Encontro 1.")
        return f'<div class="campo espelho">{rot}{dica}<div class="espelho__v" data-espelho="{c["de"]}" data-vazio="{e(vz)}">{e(vz)}</div></div>'
    elif tipo == "notas":  # cinco dimensões, nota de 1 a 5
        cels = "".join(
            f'<div class="nota"><label for="{k}.{d}"><b>{e(n)}</b></label><select id="{k}.{d}" data-k="{k}.{d}">'
            + "".join(f"<option>{o}</option>" for o in ["", "1", "2", "3", "4", "5"]) + "</select></div>"
            for d, n in c["dims"])
        corpo = f'<div class="notas">{cels}</div>'
    elif tipo == "lacunas":  # frases com lacuna e banco de números
        linhas = "".join(
            f'<li><input class="lacuna" type="text" inputmode="numeric" data-k="{k}.{i}" data-gab="{e(g)}" aria-label="lacuna {i + 1}"> <span>{e(fr)}</span></li>'
            for i, (g, fr) in enumerate(c["frases"]))
        corpo = (f'<p class="banco"><b>Banco de Números:</b> {e(c["banco"])}. Cada número entra uma vez, e três sobram.</p>'
                 f'<ol class="lacunas">{linhas}</ol>'
                 f'<button type="button" class="btn btn--sec" data-conferir>Conferir as respostas</button>')
    elif tipo == "associar":
        linhas = "".join(
            f'<li><span>{e(s)}</span><select data-k="{k}.{i}" data-gab="{e(g)}">'
            + "".join(f"<option>{e(o)}</option>" for o in [""] + c["opcoes"]) + "</select></li>"
            for i, (s, g) in enumerate(c["pares"]))
        corpo = f'<ol class="associar">{linhas}</ol><button type="button" class="btn btn--sec" data-conferir>Conferir as respostas</button>'
    elif tipo == "tabela":
        cab = "".join(f"<th>{e(h['t'])}</th>" for h in c["colunas"])
        lin = ""
        for r in range(c["n"]):
            tds = ""
            for j, h in enumerate(c["colunas"]):
                kk = f"{k}.{r}.{j}"
                if h.get("opcoes"):
                    inp = f'<select data-k="{kk}" aria-label="{e(h["t"])}">' + "".join(f"<option>{e(o)}</option>" for o in [""] + h["opcoes"]) + "</select>"
                else:
                    inp = f'<textarea data-k="{kk}" rows="2" aria-label="{e(h["t"])}" placeholder="{e(h.get("ph", ""))}"></textarea>'
                tds += f'<td data-th="{e(h["t"])}">{inp}</td>'
            lin += f"<tr>{tds}</tr>"
        extra = ('<div class="mapa" data-mapa="' + k + '"></div>' if c.get("mapa") else "") + ('<div class="curva" data-curva="' + k + '"></div>' if c.get("curva") else "")
        corpo = f'<div class="tabela-w"><table class="tabela" data-tabela="{k}"><thead><tr>{cab}</tr></thead><tbody>{lin}</tbody></table></div>{extra}'
    return f'<div class="campo">{rot}{dica}{corpo}</div>'


def bloco_html(b, enc):
    tom = b["tom"]
    o = f'<section class="bloco" id="{b["id"]}" style="--tom:{tom}">'
    o += f'<div class="eyebrow"><span>{e(b["num"])} · {e(b["nome"].upper())}</span><i></i></div>'
    ic = IC_BLOCO.get(b["nome"])
    o += (f'<div class="bloco__t"><span class="disco">{icone(ic)}</span><h2>{b["titulo"]}</h2></div>' if ic else f'<h2>{b["titulo"]}</h2>')
    if b.get("pergunta"):
        o += f'<p class="pergunta">{e(b["pergunta"])}</p>'
    if b.get("capaz"):
        o += '<div class="capaz"><b>Ao término deste bloco, você será capaz de:</b><ol>' + "".join(f"<li>{e(x)}</li>" for x in b["capaz"]) + "</ol></div>"
    for it in b["itens"]:
        t = it["t"]
        if t == "conceito":
            o += f'<article class="conceito"><h3>{e(it["titulo"])}</h3>{it["html"]}'
            if it.get("fonte"):
                o += f'<p class="fonte">Fonte: {e(it["fonte"])}</p>'
            o += "</article>"
        elif t == "regua":
            o += f'<article class="regua"><h3>{e(it["titulo"])}</h3>{it["html"]}</article>'
        elif t == "atividade":
            meta = "".join(f"<div><span>{e(a)}</span><b>{e(v)}</b></div>" for a, v in it["meta"])
            passos = "".join(f"<li>{p}</li>" for p in it["passos"])
            titq = it["titulo"].replace('"', "")
            q = f'{REPO}/discussions/new?category=q-a&title=' + html.escape(f"[E{enc['n']}] {titq}".replace(" ", "+"))
            o += f'<article class="atividade" id="{it["id"]}">'
            o += f'<div class="atividade__cab"><span class="selo">ATIVIDADE · {e(it["tempo"])}</span>'
            if it.get("area"):
                o += f'<a class="selo selo--miro" href="{enc["miro"]}" target="_blank" rel="noopener">Miro · {e(it["area"])}</a>'
            if it.get("mentor") and not PROF:
                o += '<a class="selo selo--mentor" href="mentor.html">Mentor de experimentos</a>'
            o += f'</div><h3>{e(it["titulo"])}</h3>'
            if it.get("perg"):
                o += f'<p class="pergunta pergunta--at">{e(it["perg"])}</p>'
            o += f'<ol class="passos">{passos}</ol><div class="meta">{meta}</div>'
            if it.get("exemplo"):
                o += f'<div class="exemplo"><span>EXEMPLO, APENAS ILUSTRATIVO</span>{it["exemplo"]}</div>'
            o += '<div class="registro"><span class="registro__t">O SEU REGISTRO</span>' + "".join(campo(c) for c in it["campos"]) + "</div>"
            if it.get("pontos"):
                o += '<details class="pontos"><summary>Os pontos que não podem faltar</summary><ul>' + "".join(f"<li>{p}</li>" for p in it["pontos"]) + "</ul></details>"
            if not PROF:
                o += caixa_duvida(titq)
            if PROF:
                o += '<div class="prof"><span>VERSÃO DO PROFESSOR · CONDUÇÃO</span>'
                o += "<ul>" + "".join(f"<li>{p}</li>" for p in it.get("conducao", [])) + "</ul>"
                if it.get("resposta"):
                    o += f'<div class="prof__resp"><b>Resposta</b>{it["resposta"]}</div>'
                if it.get("debrief"):
                    o += '<div class="prof__resp"><b>Perguntas de fechamento da atividade</b><ul>' + "".join(f"<li>{p}</li>" for p in it["debrief"]) + "</ul></div>"
                o += "</div>"
            o += "</article>"
    o += "</section>"
    return o


PUBLICADOS = {1, 2}
ABRE = {3: "25/11", 4: "26/11", 5: "27/11"}
ABRE_ISO = {3: "2026-11-25", 4: "2026-11-26", 5: "2026-11-27"}   # a parada vira link no dia do encontro (no navegador)
FASES = (("Escutar o sistema", 2), ("Escolher a próxima aposta", 1), ("Testar, medir e sustentar", 2))


def caminho_html(atual, grande=False):
    """Mapa do caminho: cinco paradas ligadas por uma rota, com foto, ícone e fase."""
    o = f'<div class="rota{" rota--grande" if grande else ""}">'
    o += ('<svg class="rota__linha" viewBox="0 0 1000 200" preserveAspectRatio="none" aria-hidden="true">'
          '<path d="M100,62 C170,62 220,138 300,138 S430,62 500,62 S630,138 700,138 S830,62 900,62"/></svg>')
    for n, nome, data, tom, prod, grupo in CAMINHO:
        cls = "feito" if 0 < n < atual else ("aqui" if n == atual else "")
        pub = n in PUBLICADOS or n in ABRE_ISO
        tag = "a" if pub and not PROF else "span"
        href = f' href="e{n}.html"' if tag == "a" else ""
        if n in ABRE_ISO and not PROF:
            href += f' data-abre="{ABRE_ISO[n]}" data-abre-txt="Abre em {ABRE[n]}"'
        foto = f'background-image:url({img_url(f"p{n}.jpg")})'
        rodape = (f'<small class="parada__c" data-cont>{"Você está aqui" if n == atual else ""}</small>' if pub
                  else f'<small class="parada__c">Abre em {ABRE.get(n, "")}</small>')
        o += (f'<{tag} class="parada {cls}{"" if pub else " parada--breve"}" data-parada="{n}" style="--tom:{tom}"{href}>'
              f'<span class="parada__foto" style="{foto}"><span class="parada__n">{n}</span><span class="parada__ic">{icone(IC_ENC[n], tam=22)}</span></span>'
              f'<span class="parada__k">ENCONTRO {n} · {e(data.split(" · ")[0])}</span>'
              f'<b>{e(nome)}</b><em>{e(prod)}</em>{rodape}</{tag}>')
    o += '<div class="rota__fases">' + "".join(f'<span style="grid-column:span {c}">{e(f)}</span>' for f, c in FASES) + "</div>"
    return o + "</div>"


def pagina(titulo, corpo, pg, fontes_css, extra_js=""):
    nav = "" if PROF else ('<nav class="nav"><a href="index.html">Meu mapa</a><a href="e1.html">Encontro 1</a>'
                           '<a href="e2.html">Encontro 2</a><a href="mentoria.html">Mentoria</a></nav><span class="conta" data-conta></span>')
    n_enc = int(pg[1:]) if pg.startswith("e") and pg[1:].isdigit() else 0
    cfg = "" if PROF else f'<script>window.CM4AI={{api:{json.dumps(API)},encontro:{n_enc}}};</script>'
    selo = '<span class="selo-prof">VERSÃO DO PROFESSOR</span>' if PROF else ""
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(titulo)}</title><meta name="robots" content="noindex">
<style>{fontes_css}{CSS}</style></head>
<body data-pg="{pg}">
<header class="topo"><a class="marca" href="{'#' if PROF else 'index.html'}"><img src="{MARCA}" alt=""><span><b>GINO TERENTIM</b><i>RETHINKING LEARNING</i></span></a>{selo}{nav}</header>
<main>{corpo}</main>
<footer class="rodape"><span>Change Management for AI · Turma on-line · Novembro de 2026</span><span>Rethinking Learning</span></footer>
{cfg}<script>{JS}{extra_js}</script></body></html>"""


def caixa_duvida(atividade, rotulo="Perguntar ao Gino Terentim sobre esta atividade"):
    return (f'<div class="duvidas" data-duvida="{e(atividade)}"><p class="mentor"><button type="button" class="btn btn--mentor" data-duvida-abrir>{rotulo}</button></p>'
            '<div class="duvidas__form" hidden><label class="duvidas__l">A sua dúvida para o Gino Terentim<textarea rows="4" placeholder="Escreva a dúvida com o contexto da sua adoção. Use o papel das pessoas, e não o nome."></textarea></label>'
            '<div class="duvidas__acoes"><button type="button" class="btn" data-duvida-enviar>Enviar a dúvida</button><button type="button" class="btn btn--sec" data-duvida-cancelar>Cancelar</button></div></div>'
            '<p class="duvidas__msg" aria-live="polite"></p><div class="duvidas__lista"></div></div>')


def barra():
    return ('<div class="aviso-conta" data-aviso-conta hidden><b>Entre com o seu e-mail para gravar as respostas na sua página do curso.</b> Sem entrar, elas ficam só neste navegador. <a class="btn" href="index.html">Entrar</a></div>'
            '<div class="barra"><span class="barra__s" data-salvo>As respostas ficam gravadas na sua página do curso.</span>'
            '<button type="button" class="btn btn--sec" data-exportar>Exportar as minhas respostas</button>'
            '<button type="button" class="btn btn--sec" data-imprimir>Imprimir ou salvar em PDF</button></div>')


def encontro_html(enc):
    foto = FOTO_ENC.get(enc["n"])
    fst = f';--foto:url({img_url(foto)})' if foto else ""
    o = f'<section class="capa capa--foto" style="--tom:{enc["tom"]}{fst}"><p class="capa__k">ENCONTRO {enc["n"]} DE 5 · {e(enc["data"].upper())}</p><h1>{enc["titulo"]}</h1>'
    o += f'<p class="capa__l">{e(enc["lede"])}</p></section>'
    o += '<section class="bloco bloco--abre">' + materiais_html(enc) + '<div class="capaz"><b>Ao término deste encontro, os participantes serão capazes de:</b><ol>' + "".join(f"<li>{e(x)}</li>" for x in enc["capaz"]) + "</ol></div>"
    o += "<h3>Onde estamos no caminho</h3>" + caminho_html(enc["n"])
    o += '<h3>Neste encontro</h3><ol class="indice">' + "".join(f'<li style="--tom:{b["tom"]}"><a href="#{b["id"]}"><b>{e(b["num"])}</b> {e(b["nome"])}</a><span>{e(b.get("constroi", ""))}</span></li>' for b in enc["blocos"]) + "</ol>"
    if enc["n"] == 4 and not PROF:
        o += (f'<a class="cartao cartao--mentor" href="mentor.html" style="--tom:#2F6B6F"><span class="disco" style="--tom:#1F4E51">{icone("flask-conical")}</span>'
              '<span><span class="cartao__k">NESTE ENCONTRO E DEPOIS DELE</span><b>Mentor de experimentos</b>'
              '<i>Converse sobre a sua aposta e desenhe o experimento a partir do que você registrou no workbook e nos quadros do Miro</i></span></a>')
    if not PROF:
        o += barra()
    o += "</section>"
    for b in enc["blocos"]:
        o += bloco_html(b, enc)
    if not PROF:
        o += '<section class="bloco">' + barra() + "</section>"
    return o


def fontes(inline):
    o = ""
    for peso, arq in ((400, "Poppins-Regular.ttf"), (500, "Poppins-Medium.ttf"), (700, "Poppins-Bold.ttf")):
        if inline:
            b = base64.b64encode(open(os.path.join(RAIZ, "src", "fonts", arq), "rb").read()).decode()
            src = f"url(data:font/ttf;base64,{b})"
        else:
            src = f"url(fonts/{arq})"
        o += f"@font-face{{font-family:Poppins;font-weight:{peso};src:{src} format('truetype');font-display:swap}}"
    return o


if PROF:
    MARCA = "data:image/png;base64," + base64.b64encode(open(os.path.join(RAIZ, "src", "logo-gt-mark.png"), "rb").read()).decode()
    corpo = ('<section class="capa" style="--tom:#E5662C"><p class="capa__k">VERSÃO DO PROFESSOR · ENCONTROS 1 A 5</p>'
             '<h1>Change Management <em>for AI</em></h1><p class="capa__l">O mesmo workbook da turma, com a condução, as respostas e as perguntas de fechamento de cada atividade. '
             'Arquivo único, para uso fora da internet. Não publicar.</p></section>')
    for enc in ENCONTROS:
        corpo += encontro_html(enc)
    os.makedirs(os.path.join(RAIZ, "professor"), exist_ok=True)
    open(os.path.join(RAIZ, "professor", "CM4AI-Online_Workbook_Professor_v16.html"), "w", encoding="utf-8").write(
        pagina("CM4AI · Workbook · Versão do professor", corpo, "prof", fontes(True)))
    print("professor ok")
else:
    MARCA = "logo-gt-mark.png"
    D = os.path.join(RAIZ, "docs")
    shutil.rmtree(D, ignore_errors=True); os.makedirs(os.path.join(D, "fonts"))
    for f in os.listdir(os.path.join(RAIZ, "src", "fonts")):
        shutil.copy(os.path.join(RAIZ, "src", "fonts", f), os.path.join(D, "fonts", f))
    shutil.copy(os.path.join(RAIZ, "src", "logo-gt-mark.png"), D)
    shutil.copytree(os.path.join(RAIZ, "src", "img"), os.path.join(D, "img"))
    open(os.path.join(D, ".nojekyll"), "w").close()
    shutil.copytree(os.path.join(RAIZ, "src", "materiais"), os.path.join(D, "materiais"))
    F = fontes(False)
    for enc in ENCONTROS:
        open(os.path.join(D, f"e{enc['n']}.html"), "w", encoding="utf-8").write(
            pagina(f"CM4AI · Workbook · Encontro {enc['n']}", encontro_html(enc), f"e{enc['n']}", F))
    idx = ('<section class="capa capa--foto" style="--tom:#E5662C;--foto:url(img/capa.jpg)"><p class="capa__k">CHANGE MANAGEMENT FOR AI · TURMA ON-LINE · NOVEMBRO DE 2026</p>'
           '<h1>O seu mapa de <em>navegação</em></h1><p class="capa__l">A página de cada participante no curso. Aqui ficam as instruções de cada atividade, '
           'com o mesmo texto dos slides e do quadro do Miro, e o registro das suas respostas nos cinco encontros.</p></section>')
    idx += ('<section class="entrada" data-entrada hidden><div class="entrada__f"><div class="eyebrow" style="--tom:#E5662C"><span>ACESSO · A SUA PÁGINA DO CURSO</span><i></i></div>'
            '<h2>Entre com o seu <em>e-mail</em></h2>'
            '<form novalidate><label for="f-email"><b>E-mail de inscrição</b></label><input id="f-email" name="email" type="email" autocomplete="email" required placeholder="nome@empresa.com.br">'
            '<label for="f-codigo"><b>Código de quatro números</b></label><input id="f-codigo" name="codigo" type="password" inputmode="numeric" pattern="[0-9]{4}" maxlength="4" autocomplete="current-password" required placeholder="••••">'
            '<label for="f-nome"><b>Nome, no primeiro acesso</b></label><input id="f-nome" name="nome" type="text" autocomplete="name" placeholder="Nome e sobrenome">'
            '<button class="btn btn--grande" type="submit">Abrir a minha página</button><p class="entrada__aviso" data-aviso aria-live="polite"></p></form></div>'
            '<ol class="entrada__passos">'
            f'<li><span class="disco" style="--tom:#B04A1C">{icone("mail")}</span><div><b>O e-mail da inscrição</b><p>O mesmo endereço informado na matrícula da turma.</p></div></li>'
            f'<li><span class="disco" style="--tom:#2F6B6F">{icone("key-round")}</span><div><b>Um código seu</b><p>No primeiro acesso, você escolhe quatro números. Nos acessos seguintes, o mesmo código abre a sua página, em qualquer aparelho.</p></div></li>'
            f'<li><span class="disco" style="--tom:#5E7D52">{icone("map-pin")}</span><div><b>O seu registro, encontro a encontro</b><p>Cada resposta é gravada na sua página assim que você escreve, e volta inteira no encontro seguinte.</p></div></li></ol></section>')
    idx += ('<section class="mapa-curso" data-mapa-curso><div class="mapa-curso__cab"><div><div class="eyebrow" style="--tom:#E5662C"><span>O CAMINHO DOS CINCO ENCONTROS</span><i></i></div>'
            '<h2><span data-ola-bloco hidden>Olá, <span data-ola></span>. </span>O seu <em>caminho</em></h2>'
            '<p>Encontros ao vivo das 19h às 22h, horário de Brasília. Cada encontro termina com um produto aplicável ao seu contexto, e cada parada do mapa abre o workbook do encontro.</p></div>'
            f'<span class="rosa" aria-hidden="true">{icone("compass", "#C9A24D", 120, 1.1)}</span></div>' + caminho_html(0, True) +
            '<div class="cards3 cards3--claro"><div><b>Como usar</b><p>Abra o encontro do dia e registre as suas respostas à medida que cada atividade acontece. Sem conexão, o registro fica neste navegador e segue para a sua página na alteração seguinte.</p></div>'
            '<div><b>O fio entre os encontros</b><p>A adoção de IA que você escolhe no Encontro 1 acompanha o curso inteiro. Cada encontro parte do que você registrou no anterior.</p></div>'
            '<div><b>Reserva dos seus dados</b><p>As respostas ficam na planilha privada da turma, aberta apenas ao Gino Terentim, e na sua página, protegida pelo seu código. Use o papel das pessoas, e não o nome.</p></div></div>'
            f'<a class="cartao cartao--mentor" href="mentoria.html" style="--tom:#2A211C"><span class="disco" style="--tom:#E5662C">{icone("messages-square")}</span><span><span class="cartao__k">ENTRE OS ENCONTROS</span><b>Dúvidas para o Gino Terentim</b><i>Pergunte sobre o método e as atividades; a resposta volta para a sua página e para o seu e-mail</i></span></a></section>')
    open(os.path.join(D, "index.html"), "w", encoding="utf-8").write(pagina("CM4AI · Workbook digital", idx, "index", F))
    m = ('<section class="capa" style="--tom:#E5662C"><p class="capa__k">ENTRE OS ENCONTROS</p><h1>Dúvidas para o <em>Gino Terentim</em></h1>'
         '<p class="capa__l">Pergunte sobre o método e sobre as atividades do curso. A dúvida chega ao Gino Terentim, e a resposta volta para a sua página do workbook e para o seu e-mail.</p></section>'
         '<section class="bloco bloco--abre"><div class="abas" role="tablist" aria-label="Dúvidas para o Gino Terentim">'
         f'<button type="button" class="aba" role="tab" id="aba-nova" aria-controls="painel-nova" aria-selected="true" data-aba="nova">{icone("message-square-plus", "currentColor", 22, 2)}Nova dúvida</button>'
         f'<button type="button" class="aba" role="tab" id="aba-enviadas" aria-controls="painel-enviadas" aria-selected="false" tabindex="-1" data-aba="enviadas">{icone("inbox", "currentColor", 22, 2)}Dúvidas enviadas<span class="selo-n" data-naolidas-aba hidden></span></button></div>'
         '<div class="aba__painel" role="tabpanel" id="painel-nova" aria-labelledby="aba-nova" data-painel-aba="nova">'
         '<h2>Como <em>perguntar</em></h2><ol class="passos">'
         '<li>Entre no workbook com o e-mail da inscrição e o seu código de quatro números.</li>'
         '<li>Em cada atividade, use o botão <b>Perguntar ao Gino Terentim sobre esta atividade</b>. Para uma dúvida geral, use o botão abaixo.</li>'
         '<li>A resposta aparece na aba <b>Dúvidas enviadas</b> e junto da atividade, e chega no seu e-mail. No menu, o item Mentoria mostra quantas respostas você ainda não leu.</li></ol>'
         + caixa_duvida("Dúvida geral", "Escrever uma dúvida geral") +
         '<div class="cards3"><div><b>Reserva</b><p>As dúvidas ficam na planilha privada da turma, aberta apenas ao Gino Terentim. Use o papel das pessoas, e não o nome, e mantenha fora do texto os dados reservados da sua organização.</p></div>'
         '<div><b>Uma boa pergunta</b><p>Traz o contexto da sua adoção, o que você já tentou e o ponto exato da dúvida.</p></div>'
         '<div><b>Prazo</b><p>As dúvidas ficam abertas até 30 de novembro de 2026.</p></div></div>'
         '<article class="regua"><h3>Exemplo de pergunta, apenas ilustrativo</h3><p>“Na minha adoção, um assistente de IA para a área de compras, a menor nota do diagnóstico foi Liderança, 2. '
         'A gerente cobra o uso e nunca mostrou um uso próprio. Que pergunta de abertura traz fatos numa conversa individual com ela?”</p></article></div>'
         '<div class="aba__painel" role="tabpanel" id="painel-enviadas" aria-labelledby="aba-enviadas" data-painel-aba="enviadas" hidden>'
         '<h2>As suas <em>dúvidas</em></h2><p class="aba__nota">Cada resposta nova chega com o selo <b>Nova</b> e passa a constar como lida quando você abre esta aba.</p>'
         '<div class="duvidas__todas" data-duvidas-todas></div></div></section>')
    pn = ('<section class="capa" style="--tom:#2A211C"><p class="capa__k">ÁREA DO PROFESSOR</p><h1>Painel de <em>dúvidas</em></h1>'
          '<p class="capa__l">As dúvidas da turma chegam aqui em tempo real. A resposta aparece no workbook do participante e vai para o e-mail dele.</p></section>'
          '<section class="bloco bloco--abre painel">'
          '<div class="painel__entrada" data-p-entrada><label class="duvidas__l">Chave do painel<input type="password" autocomplete="current-password" data-p-chave></label>'
          '<div class="duvidas__acoes"><button type="button" class="btn" data-p-entrar>Abrir o painel</button><button type="button" class="btn btn--sec" data-p-enviar-chave>Receber a chave no e-mail</button></div></div>'
          '<p class="duvidas__msg" data-p-msg aria-live="polite"></p>'
          '<div data-p-quadro hidden><div class="painel__topo"><div class="painel__n"><b data-p-ag>0</b><span>aguardando</span></div><div class="painel__n painel__n--ok"><b data-p-rp>0</b><span>respondidas</span></div>'
          '<div class="painel__f"><button type="button" class="chip-f" data-p-filtro="aguardando">Aguardando</button><button type="button" class="chip-f" data-p-filtro="respondidas">Respondidas</button><button type="button" class="chip-f" data-p-filtro="todas">Todas</button>'
          '<select data-p-enc><option value="0">Todos os encontros</option>' + "".join(f'<option value="{k}">Encontro {k}</option>' for k in range(1, 6)) + '</select></div>'
          '<div class="painel__h"><span data-p-hora></span><button type="button" class="btn btn--sec" data-p-sair>Sair</button></div></div>'
          '<div data-p-lista></div></div></section>')
    open(os.path.join(D, "painel.html"), "w", encoding="utf-8").write(pagina("Painel de dúvidas · CM4AI", pn, "painel", F, PAINEL_JS))
    open(os.path.join(D, "mentoria.html"), "w", encoding="utf-8").write(pagina("CM4AI · Mentoria", m, "mentoria", F))
    # Mentor de experimentos: conversa com a IA, a partir do que a pessoa registrou no curso.
    chips = ["Quero formular a minha hipótese", "Me ajude a definir a medida", "Vamos planejar o experimento", "Monte a ficha do meu experimento"]
    passos_m = [("lightbulb", "#2F6B6F", "O que você já registrou", "O mentor lê o seu workbook e as suas áreas nos quadros do Miro."),
                ("flask-conical", "#7A4E6D", "A hipótese", "Ação, comportamento esperado e medida, em três partes."),
                ("gauge", "#2F6B6F", "A medida", "Linha de base, meta, data de revisão e critério com três faixas."),
                ("calendar-range", "#5E7D52", "O plano", "Preparar, introduzir e revisar, com risco e forma de desfazer.")]
    mt = ('<section class="capa" style="--tom:#B04A1C"><p class="capa__k">ENCONTRO 4 · EXPERIMENTOS DE MUDANÇA</p><h1>Mentor de <em>experimentos</em></h1>'
          '<p class="capa__l">Uma conversa para pensar o experimento da sua adoção, com perguntas que partem do que você já registrou no curso.</p></section>'
          '<div class="mentorx"><div class="zap" data-mentor>'
          f'<header class="zap__topo"><span class="zap__av">{icone("flask-conical", "#FFFFFF", 24)}</span><div><b>Mentor de experimentos</b><i data-mentor-status>on-line · CM4AI</i></div></header>'
          '<div class="zap__fundo" data-mentor-lista aria-live="polite"></div>'
          '<div class="zap__chips" data-mentor-chips>' + "".join(f'<button type="button" data-chip="{e(c)}">{e(c)}</button>' for c in chips) + '</div>'
          f'<form class="zap__barra" data-mentor-form><div class="zap__grava" data-mentor-grava hidden><button type="button" class="zap__grava-x" data-grava-cancelar aria-label="Cancelar o áudio">{icone("trash-2", "#6E6259", 22)}</button>'
          '<span class="zap__ponto" aria-hidden="true"></span><span class="zap__grava-t" data-grava-tempo>0:00</span><span class="zap__grava-dica" data-grava-dica>Solte para enviar</span>'
          f'<button type="button" class="zap__grava-ok" data-grava-enviar aria-label="Enviar o áudio" hidden>{icone("send-horizontal", "#FFFFFF", 20)}</button></div>'
          '<textarea rows="1" placeholder="Escreva uma mensagem" aria-label="A sua mensagem"></textarea>'
          f'<button type="button" class="zap__mic" data-mentor-mic aria-label="Segure para gravar uma mensagem de voz" hidden>{icone("mic", "#FFFFFF", 22)}</button>'
          f'<button type="submit" aria-label="Enviar">{icone("send-horizontal", "#FFFFFF", 22)}</button></form></div>'
          '<aside class="mentorx__lado"><div class="mentorx__card"><h3>Como o mentor ajuda</h3><ul class="mentorx__passos">'
          + "".join(f'<li><span class="disco" style="--tom:{t}">{icone(ic, "#FFFFFF", 20)}</span><span><b>{e(ti)}</b>{e(tx)}</span></li>' for ic, t, ti, tx in passos_m) +
          '</ul></div><div class="mentorx__card"><h3>Reserva</h3><p>As mensagens são processadas pela API da Anthropic e ficam registradas na planilha privada da turma, aberta apenas ao Gino Terentim. As mensagens de voz são transcritas pela OpenAI: na planilha fica só o texto, e o áudio não é guardado. Use o papel das pessoas, e não o nome, e mantenha fora da conversa os dados reservados da sua organização.</p></div>'
          '<div class="mentorx__card"><h3>Dúvidas sobre o método</h3><p>O mentor conversa sobre o seu experimento. Para uma dúvida que precisa da resposta do Gino Terentim, use a <a href="mentoria.html">Mentoria</a>.</p></div></aside></div>')
    MJS = open(os.path.join(RAIZ, "src", "mentor.js"), encoding="utf-8").read()
    open(os.path.join(D, "mentor.html"), "w", encoding="utf-8").write(pagina("CM4AI · Mentor de experimentos", mt, "mentor", F, MJS))
    print("site ok")
