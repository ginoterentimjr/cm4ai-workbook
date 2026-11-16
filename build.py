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
JS = open(os.path.join(RAIZ, "src", "app.js"), encoding="utf-8").read()
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
        return f'<div class="campo espelho">{rot}{dica}<div class="espelho__v" data-espelho="{c["de"]}">Ainda sem registro no Encontro 1.</div></div>'
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
        extra = '<div class="mapa" data-mapa="' + k + '"></div>' if c.get("mapa") else ""
        corpo = f'<div class="tabela-w"><table class="tabela" data-tabela="{k}"><thead><tr>{cab}</tr></thead><tbody>{lin}</tbody></table></div>{extra}'
    return f'<div class="campo">{rot}{dica}{corpo}</div>'


def bloco_html(b, enc):
    tom = b["tom"]
    o = f'<section class="bloco" id="{b["id"]}" style="--tom:{tom}">'
    o += f'<div class="eyebrow"><span>{e(b["num"])} · {e(b["nome"].upper())}</span><i></i></div>'
    o += f'<h2>{b["titulo"]}</h2>'
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
                o += f'<p class="mentor"><a class="btn btn--mentor" href="{q}" target="_blank" rel="noopener">Perguntar ao mentor sobre esta atividade</a></p>'
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


def caminho_html(atual):
    o = '<div class="caminho">'
    for n, nome, data, tom, prod, grupo in CAMINHO:
        cls = "feito" if n < atual else ("aqui" if n == atual else "")
        o += (f'<a class="caminho__p {cls}" style="--tom:{tom}" href="{"e%d.html" % n if n <= 2 else "#"}">'
              f'<span class="caminho__g">{e(grupo)}</span><span class="caminho__n">{n}</span>'
              f'<b>{e(nome)}</b><small>{e(data)}</small><em>{e(prod)}</em></a>')
    return o + "</div>"


def pagina(titulo, corpo, pg, fontes_css, extra_js=""):
    nav = "" if PROF else ('<nav class="nav"><a href="index.html">Início</a><a href="e1.html">Encontro 1</a>'
                           '<a href="e2.html">Encontro 2</a><a href="mentoria.html">Mentoria</a></nav>')
    selo = '<span class="selo-prof">VERSÃO DO PROFESSOR</span>' if PROF else ""
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(titulo)}</title><meta name="robots" content="noindex">
<style>{fontes_css}{CSS}</style></head>
<body data-pg="{pg}">
<header class="topo"><a class="marca" href="{'#' if PROF else 'index.html'}"><img src="{MARCA}" alt=""><span><b>GINO TERENTIM</b><i>RETHINKING LEARNING</i></span></a>{selo}{nav}</header>
<main>{corpo}</main>
<footer class="rodape"><span>Change Management for AI · Turma on-line · Novembro de 2026</span><span>Rethinking Learning</span></footer>
<script>{JS}{extra_js}</script></body></html>"""


def barra():
    return ('<div class="barra"><span class="barra__s" data-salvo>As respostas ficam gravadas neste navegador.</span>'
            '<button type="button" class="btn btn--sec" data-exportar>Exportar as minhas respostas</button>'
            '<button type="button" class="btn btn--sec" data-imprimir>Imprimir ou salvar em PDF</button></div>')


def encontro_html(enc):
    o = f'<section class="capa" style="--tom:{enc["tom"]}"><p class="capa__k">ENCONTRO {enc["n"]} DE 5 · {e(enc["data"].upper())}</p><h1>{enc["titulo"]}</h1>'
    o += f'<p class="capa__l">{e(enc["lede"])}</p></section>'
    o += '<section class="bloco bloco--abre"><div class="capaz"><b>Ao término deste encontro, os participantes serão capazes de:</b><ol>' + "".join(f"<li>{e(x)}</li>" for x in enc["capaz"]) + "</ol></div>"
    o += "<h3>Onde estamos no caminho</h3>" + caminho_html(enc["n"])
    o += '<h3>Neste encontro</h3><ol class="indice">' + "".join(f'<li style="--tom:{b["tom"]}"><a href="#{b["id"]}"><b>{e(b["num"])}</b> {e(b["nome"])}</a><span>{e(b.get("constroi", ""))}</span></li>' for b in enc["blocos"]) + "</ol>"
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
    corpo = ('<section class="capa" style="--tom:#E5662C"><p class="capa__k">VERSÃO DO PROFESSOR · ENCONTROS 1 E 2</p>'
             '<h1>Change Management <em>for AI</em></h1><p class="capa__l">O mesmo workbook da turma, com a condução, as respostas e as perguntas de fechamento de cada atividade. '
             'Arquivo único, para uso fora da internet. Não publicar.</p></section>')
    for enc in ENCONTROS:
        corpo += encontro_html(enc)
    os.makedirs(os.path.join(RAIZ, "professor"), exist_ok=True)
    open(os.path.join(RAIZ, "professor", "CM4AI-Online_Workbook_Professor_v1.html"), "w", encoding="utf-8").write(
        pagina("CM4AI · Workbook · Versão do professor", corpo, "prof", fontes(True)))
    print("professor ok")
else:
    MARCA = "logo-gt-mark.png"
    D = os.path.join(RAIZ, "docs")
    shutil.rmtree(D, ignore_errors=True); os.makedirs(os.path.join(D, "fonts"))
    for f in os.listdir(os.path.join(RAIZ, "src", "fonts")):
        shutil.copy(os.path.join(RAIZ, "src", "fonts", f), os.path.join(D, "fonts", f))
    shutil.copy(os.path.join(RAIZ, "src", "logo-gt-mark.png"), D)
    open(os.path.join(D, ".nojekyll"), "w").close()
    F = fontes(False)
    for enc in ENCONTROS:
        open(os.path.join(D, f"e{enc['n']}.html"), "w", encoding="utf-8").write(
            pagina(f"CM4AI · Workbook · Encontro {enc['n']}", encontro_html(enc), f"e{enc['n']}", F))
    idx = ('<section class="capa" style="--tom:#E5662C"><p class="capa__k">CERTIFICAÇÃO LEAN CHANGE MANAGEMENT · TURMA ON-LINE · NOVEMBRO DE 2026</p>'
           '<h1>Change Management <em>for AI</em></h1><p class="capa__l">Workbook digital da turma. Cada atividade dos encontros tem aqui as instruções completas, '
           'um exemplo e o espaço para o seu registro, com o mesmo texto dos slides e do quadro do Miro.</p></section>')
    idx += '<section class="bloco bloco--abre"><h2>O caminho dos <em>cinco encontros</em></h2><p>Todos os encontros ao vivo, das 19h às 22h, horário de Brasília. Cada encontro termina com um produto aplicável ao seu contexto.</p>' + caminho_html(0)
    idx += ('<div class="cards3"><div><b>Como usar</b><p>Abra o encontro do dia e registre as suas respostas à medida que a atividade acontece. O registro fica gravado neste navegador, neste aparelho.</p></div>'
            '<div><b>O fio entre os encontros</b><p>A adoção de IA que você escolhe no Encontro 1 acompanha o curso inteiro. O Encontro 2 parte do que você registrou no Encontro 1.</p></div>'
            '<div><b>Reserva dos seus dados</b><p>As respostas não saem do seu navegador. Use o papel das pessoas, e não o nome. Para guardar uma cópia, exporte ou salve em PDF.</p></div></div>')
    idx += ('<div class="cards2"><a class="cartao" href="e1.html" style="--tom:#B04A1C"><span>ENCONTRO 1 · 18/11</span><b>Fundamentos e prontidão</b><i>Diagnóstico 5D e o que termina</i></a>'
            '<a class="cartao" href="e2.html" style="--tom:#2F6B6F"><span>ENCONTRO 2 · 19/11</span><b>Pessoas e coleta de insights</b><i>Mapa de pessoas e plano de coleta</i></a>'
            '<a class="cartao" href="mentoria.html" style="--tom:#2A211C"><span>ENTRE OS ENCONTROS</span><b>Mentoria de Lean Change Management</b><i>Dúvidas respondidas em cerca de um minuto</i></a></div>'
            '<p class="nota-pe">Os Encontros 3, 4 e 5 entram neste workbook na data de cada um.</p></section>')
    open(os.path.join(D, "index.html"), "w", encoding="utf-8").write(pagina("CM4AI · Workbook digital", idx, "index", F))
    m = ('<section class="capa" style="--tom:#E5662C"><p class="capa__k">ENTRE OS ENCONTROS</p><h1>Mentoria de <em>Lean Change Management</em></h1>'
         '<p class="capa__l">Um mentor de inteligência artificial responde às suas dúvidas sobre o método e sobre as atividades do curso, no fórum da turma.</p></section>'
         '<section class="bloco bloco--abre"><h2>Como <em>perguntar</em></h2><ol class="passos">'
         '<li>Entre no GitHub com a sua conta. Quem ainda não tem cria uma, gratuita, em github.com.</li>'
         f'<li>Abra o <a href="{REPO}/discussions/new?category=q-a" target="_blank" rel="noopener">fórum da turma</a> e escreva a sua dúvida, com o contexto da sua adoção.</li>'
         '<li>A resposta do mentor chega na mesma página, em cerca de um minuto. Para continuar a conversa, responda ali mesmo.</li></ol>'
         f'<p><a class="btn btn--mentor" href="{REPO}/discussions/new?category=q-a" target="_blank" rel="noopener">Abrir uma pergunta no fórum</a> '
         f'<a class="btn btn--sec" href="{REPO}/discussions" target="_blank" rel="noopener">Ler as perguntas da turma</a></p>'
         '<div class="cards3"><div><b>O fórum é visível</b><p>As perguntas e as respostas ficam visíveis à turma e a quem tiver o endereço. Use o papel das pessoas, e não o nome, e mantenha fora do texto os dados reservados da sua organização.</p></div>'
         '<div><b>O que o mentor faz</b><p>Ajuda a aplicar o método à sua adoção: ler o diagnóstico, montar o mapa de pessoas, escolher a prática de coleta, redigir perguntas que trazem fatos.</p></div>'
         '<div><b>O limite do mentor</b><p>O mentor é um modelo de IA (GPT-6.1 Sol) e pode errar. Nas questões de certificação e de condução do curso, a palavra final é do Gino Terentim, nos encontros.</p></div></div>'
         '<article class="regua"><h3>Uma boa pergunta ao mentor</h3><p>“Na minha adoção, um assistente de IA para a área de compras, a menor nota do diagnóstico foi Liderança, 2. '
         'A gerente cobra o uso e nunca mostrou um uso próprio. Que pergunta de abertura traz fatos numa conversa individual com ela?”</p></article>'
         '<p class="nota-pe">A mentoria fica aberta até 30 de novembro de 2026.</p></section>')
    open(os.path.join(D, "mentoria.html"), "w", encoding="utf-8").write(pagina("CM4AI · Mentoria", m, "mentoria", F))
    print("site ok")
