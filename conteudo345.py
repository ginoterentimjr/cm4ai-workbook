# -*- coding: utf-8 -*-
"""Encontros 3, 4 e 5 do workbook. Passos, ficha e exemplo de cada atividade vêm dos próprios slides
   (decks em /home/claude/cm4ai), para que o texto seja o mesmo do slide e do quadro do Miro.
   python3 conteudo345.py  -> acrescenta E3, E4 e E5 a conteudo.json e as notas a professor_notas.json"""
import ast, json, re, os
DECK = "/home/claude/cm4ai"


def tb(linhas, cab=None):
    o = '<div class="tabela-w"><table class="tabela tabela--ler">'
    if cab: o += "<thead><tr>" + "".join(f"<th>{c}</th>" for c in cab) + "</tr></thead>"
    return o + "<tbody>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in l) + "</tr>" for l in linhas) + "</tbody></table></div>"


def cards(itens): return '<div class="cards3">' + "".join(f"<div><b>{a}</b><p>{b}</p></div>" for a, b in itens) + "</div>"


def md(s):
    s = re.sub(r"\*\*(\d+ min(?: por pessoa)?)\*\*", r"<i>\1</i>", s)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)


def _val(x):
    try: return ast.literal_eval(x)
    except Exception: return getattr(x, "id", None)


def atividades(arquivos):
    """Lista, na ordem do deck, das atividades: título, minutos, passos, exemplo, ficha e as notas de condução."""
    out = []
    for f in arquivos:
        corpo = ast.parse(open(os.path.join(DECK, f), encoding="utf-8").read()).body
        for i, st in enumerate(corpo):
            v = getattr(st, "value", None)
            if isinstance(v, ast.Call) and getattr(v.func, "id", "") == "atividade":
                a = [_val(x) for x in v.args]
                notas = {}
                if i + 1 < len(corpo) and isinstance(corpo[i + 1], ast.Expr):
                    c = corpo[i + 1].value
                    if getattr(c.func, "attr", "") == "notas":
                        notas = {k.arg: _val(k.value) for k in c.keywords}
                out.append(dict(titulo=f"{a[2]} {a[3]}".replace(", ", ", "), mins=a[4], passos=[md(p) for p in a[6]], exemplo=a[7],
                                ficha=[(k[:1] + k[1:].lower(), v) for k, v in a[8]], fazer=notas.get("fazer", []), contexto=notas.get("contexto", ""), atencao=notas.get("atencao", "")))
    return out


def ativ(id_, a, area, campos, pontos=None, perg=None, extra_cond=(), resposta=None):
    meta = [(k, v) for k, v in a["ficha"] if k not in ("Pergunta",)]
    if perg is None:
        perg = next((v for k, v in a["ficha"] if k == "Pergunta"), None)
    cond = list(a["fazer"]) + ([a["contexto"]] if a["contexto"] else []) + ([a["atencao"]] if a["atencao"] else []) + list(extra_cond)
    d = dict(t="atividade", id=id_, titulo=a["titulo"], tempo=f'{a["mins"]} min', area=area, passos=a["passos"], meta=meta,
             exemplo=f"<p>{a['exemplo']}</p><p><i>Caso fictício da área de compras.</i></p>", campos=campos, conducao=cond)
    if perg: d["perg"] = perg
    if pontos: d["pontos"] = pontos
    if resposta: d["resposta"] = resposta
    return d


def F(k, rot, linhas=3, ph="", **kw): return dict(k=k, rotulo=rot, linhas=linhas, ph=ph, **kw)
def ESP(k, rot, de, enc): return dict(k=k, rotulo=rot, tipo="espelho", de=de, vazio=f"Ainda sem registro no Encontro {enc}.")
UM5 = ["1", "2", "3", "4", "5"]

# ============================== ENCONTRO 3 ==============================
A3 = atividades(["e3_a.py", "e3_b.py"])
RESIST = json.load(open(os.path.join(DECK, "pendente_wb_e3_resistencia.json"), encoding="utf-8"))
E3 = dict(n=3, tom="#7A4E6D", data="25 de novembro de 2026", miro="https://miro.com/app/board/uXjVEN1xbkY=/",
    titulo="Insights <em>e opções</em>",
    lede="Dos registros das conversas aos insights, o mapa de forças da adoção, as opções de mudança para a força com estrela e a próxima aposta.",
    capaz=["Formular insights a partir dos registros das conversas, separando fato de interpretação.", "Construir o mapa de forças da adoção, com as forças a favor e as contrárias.",
           "Gerar opções de mudança para a força contrária que está ao alcance da área.", "Selecionar a próxima aposta, pelo valor, pelo esforço e pelo alcance."],
    blocos=[
        dict(id="e3-ab", num="00", nome="Abertura", tom="#4A3F37", titulo="A retomada, <em>em salas</em>", constroi="O que se repetiu nas conversas da semana",
             itens=[dict(t="conceito", titulo="Para ter uma boa ideia, tenha muitas ideias.", html="<p>A frase de Linus Pauling abre o encontro: as opções de hoje nascem em quantidade antes de nascer em qualidade.</p>"),
                    ativ("e3-a0", A3[0], None, [F("e3.a0.resp", "A Minha Resposta"), F("e3.a0.rep", "O Que Se Repetiu na Sala", 2)])]),
        dict(id="e3-b1", num="01", nome="Dos registros aos insights", tom="#2F6B6F", titulo="Dos registros <em>aos insights</em>",
             pergunta="O que as conversas explicam sobre a adoção?", constroi="O insight de cada pessoa e o insight mais forte da sala",
             capaz=["Distinguir registro, padrão e insight.", "Separar o fato da interpretação apressada.", "Formular um insight que explica o comportamento das pessoas."],
             itens=[dict(t="conceito", titulo="Três degraus: registro, padrão e insight",
                         html=cards([("Registro", "A frase literal da pessoa, sem adjetivo de quem anotou."), ("Padrão", "O que se repete em pelo menos dois registros."), ("Insight", "A explicação: a razão das pessoas e o efeito sobre a adoção.")])
                         + "<p><b>Como formular:</b> “Observamos que… (o padrão) porque… (a razão das pessoas) e isso… (o efeito sobre a adoção).”</p>"
                         + tb([["“Os seniores são resistentes à IA.”", "Observamos que os seniores refazem a cotação na planilha, porque a reunião de aprovação exige a planilha, e isso dobra o trabalho de quem usa o assistente."],
                               ["“Falta treinamento.”", "Observamos que os juniores conferem todas as respostas, porque não sabem quem responde por um erro do assistente, e isso consome o tempo que a ferramenta economiza."]], ["Interpretação apressada", "Insight"]),
                         fonte="Instrumento do curso. Exemplo do caso fictício da área de compras."),
                    RESIST,
                    ativ("e3-a1", A3[1], "Área 1", [F("e3.a1.reg", "Os Três Registros", 4, "Com as palavras de cada pessoa"), F("e3.a1.padrao", "O Padrão", 2),
                                                   F("e3.a1.insight", "O Insight", 3, "Observamos que… porque… e isso…"), F("e3.a1.forte", "O Insight Mais Forte da Sala", 2)],
                         pontos=["<b>Registro literal.</b> A frase da pessoa, sem adjetivo de quem anotou.", "<b>Padrão com dois apoios.</b> O que se repete em pelo menos dois registros.",
                                 "<b>Insight que explica.</b> Diz a razão das pessoas e o efeito sobre a adoção, sem acusar.", "A pessoa que você ouviu concordaria com o insight que você escreveu?"])]),
        dict(id="e3-b2", num="02", nome="O mapa de forças", tom="#B04A1C", titulo="O mapa de forças <em>da adoção</em>",
             pergunta="O que ajuda e o que impede a adoção hoje?", constroi="O mapa de forças, com a força contrária ao alcance da área",
             capaz=["Descrever o comportamento desejado, com sujeito e verbo.", "Identificar as forças a favor e as contrárias, com a intensidade.", "Escolher a força contrária que está ao alcance da área."],
             itens=[dict(t="conceito", titulo="Reduzir o que segura funciona melhor do que empurrar mais",
                         html="<p>No mapa de forças de Kurt Lewin, o comportamento de hoje é o equilíbrio entre forças a favor e forças contrárias. Quando só as forças a favor aumentam, a resposta contrária cresce junto. Quando uma força contrária diminui, o mesmo avanço acontece com menos tensão.</p>"
                              + cards([("Cada força tem um registro", "Uma força sem frase ou fato que a sustente ainda é hipótese: marque com “?”."), ("A mais intensa nem sempre é a primeira", "Primeiro, a contrária mais intensa que a área reduz com as próprias decisões."),
                                       ("Toda força tem gente", "Atrás de cada força há pessoas do mapa do Encontro 2. Elas participam do desenho das opções.")]),
                         fonte="Lewin, K. Frontiers in Group Dynamics, 1947; Field Theory in Social Science, 1951."),
                    ativ("e3-a2", A3[2], "Área 2", [F("e3.a2.comp", "O Comportamento Desejado", 2, "Com sujeito e verbo"),
                                                   dict(k="e3.a2.forcas", rotulo="As Forças da Minha Adoção", tipo="tabela", n=8,
                                                        colunas=[dict(t="A Força"), dict(t="Lado", opcoes=["A favor", "Contrária"]), dict(t="Intensidade", opcoes=UM5), dict(t="O Registro Que a Sustenta")]),
                                                   F("e3.a2.estrela", "A Força Com Estrela ⭐", 2, "A contrária mais intensa ao alcance da área")],
                         pontos=["<b>Quantas forças têm um registro?</b> Força com ponto de interrogação pede mais uma conversa.", "<b>As contrárias falam de ferramenta ou de regra, exemplo e reconhecimento?</b> Na adoção de IA, as mais intensas costumam estar fora da ferramenta.",
                                 "<b>A estrela está ao alcance da área?</b> Se depende de outra instância, a estrela desce para a próxima força."])]),
        dict(id="e3-b3", num="03", nome="Opções de mudança", tom="#B5781E", titulo="Opções de mudança <em>para a força com estrela</em>",
             pergunta="O que poderíamos fazer para habilitar o comportamento?", constroi="O quadro de opções, com pelo menos cinco opções de três tipos",
             capaz=["Gerar opções em quantidade, antes de avaliar.", "Distinguir cinco tipos de opção.", "Registrar cada opção com quem faz o quê."],
             itens=[dict(t="conceito", titulo="Do insight às opções",
                         html="<p>Três perguntas do método: <b>que comportamento queremos ver?</b> <b>O que o impede hoje?</b> <b>O que poderíamos fazer para habilitá-lo?</b></p>"
                              + tb([["Começar", "Uma prática que ainda não existe."], ["Parar", "Uma exigência que segura o jeito antigo."], ["Mudar", "Um papel, um fluxo ou um ritual."], ["Manter", "O que funciona e precisa continuar."], ["Esperar", "Não fazer nada agora, por decisão."]], ["Tipo de opção", "O que é"])
                              + "<p><b>Quem participa do desenho sustenta a mudança:</b> no estudo de Coch e French (1948), os grupos que participaram do desenho recuperaram a produção; o que só recebeu a decisão resistiu.</p>",
                         fonte="Little, J. Lean Change Management, 2014 (as três perguntas). Os cinco tipos são instrumento do curso. Coch, L.; French, J. Human Relations, 1948."),
                    ativ("e3-a3", A3[3], "Área 3", [ESP("e3.a3.forca", "A Força Com Estrela (do Bloco 2)", "e3.a2.estrela", 3),
                                                   dict(k="e3.a3.opcoes", rotulo="O Meu Quadro de Opções", tipo="tabela", n=6,
                                                        colunas=[dict(t="A Opção", ph="Quem faz o quê"), dict(t="Tipo", opcoes=["Começar", "Parar", "Mudar", "Manter", "Esperar"]), dict(t="Valor", opcoes=UM5), dict(t="Esforço", opcoes=UM5)])],
                         pontos=["<b>Pelo menos cinco opções.</b> A melhor costuma aparecer depois da terceira.", "<b>Ao menos uma do tipo parar.</b> Suspender uma exigência antiga costuma custar menos do que criar uma prática nova.",
                                 "<b>Opções com gente.</b> Cada opção diz quem faz o quê. “Sensibilizar a área” ainda não é opção."])]),
        dict(id="e3-b4", num="04", nome="A próxima aposta", tom="#35608F", titulo="A próxima <em>aposta</em>",
             pergunta="Qual opção vale testar primeiro?", constroi="A sua linha no mural de apostas da turma",
             capaz=["Avaliar as opções por valor e por esforço.", "Usar o alcance como critério de desempate.", "Registrar a próxima aposta com o comportamento esperado e as pessoas do desenho."],
             itens=[dict(t="conceito", titulo="Três critérios: valor, esforço e alcance",
                         html=cards([("Valor · de 1 a 5", "Quanto esta opção reduz a força com estrela e aproxima o comportamento desejado."), ("Esforço · de 1 a 5", "Tempo, dinheiro e desgaste para colocar a opção em prática."),
                                     ("Alcance · o desempate", "Entre duas opções parecidas, a primeira aposta é a que afeta menos pessoas e pode ser desfeita.")]),
                         fonte="Little, J. Lean Change Management, 2014: no método, as opções têm valor, custo e impacto."),
                    ativ("e3-a4", A3[4], "Área 4", [F("e3.a4.aposta", "A Próxima Aposta", 2), F("e3.a4.comp", "O Comportamento Que Quero Ver", 2), F("e3.a4.desenho", "Quem Participa do Desenho", 2), F("e3.a4.porque", "Por Que Esta", 2, "Valor, esforço e alcance")],
                         pontos=["<b>Pequena.</b> Cabe em poucas semanas, com uma equipe, e pode ser desfeita.", "<b>Visível.</b> Diz o comportamento que se passa a ver quando funciona.", "<b>Com gente no desenho.</b> Quem vive a força com estrela ajuda a fechar a aposta."])]),
        dict(id="e3-fe", num="05", nome="Fechamento", tom="#5E7D52", titulo="Até o <em>próximo encontro</em>", constroi="A aposta mostrada a uma pessoa do desenho",
             itens=[dict(t="atividade", id="e3-a5", titulo="Até o próximo encontro", tempo="até 26/11", area=None,
                         passos=["<b>Mostre a aposta a uma pessoa.</b> Se houver oportunidade até amanhã: uma das pessoas do desenho. Pergunte o que ela mudaria.",
                                 "<b>Releia a sua linha.</b> A aposta diz quem faz o quê? O comportamento é algo que se consegue ver?",
                                 "<b>Registre no workbook.</b> O insight, o mapa de forças, as opções e a aposta, nesta página."],
                         meta=[("Próximo encontro", "Quinta-feira, 26 de novembro, às 19h."), ("Tema", "Experimentos de mudança: hipótese, medida, critério de revisão e o portfólio de experimentos.")],
                         campos=[F("e3.a5.reacao", "O Que a Pessoa Mudaria na Aposta", 3)],
                         conducao=["Discussão do encontro, 20 minutos (21h40 a 22h00): que força contrária você só enxergou depois das conversas? Que exigência antiga a sua área poderia suspender ainda neste mês? Quem precisa ver a sua aposta antes de ela começar?"])]),
    ])

# ============================== ENCONTRO 4 ==============================
A4 = atividades(["e4_a.py", "e4_b.py"])
E4 = dict(n=4, tom="#B5781E", data="26 de novembro de 2026", miro="https://miro.com/app/board/uXjVEN1S8z0=/",
    titulo="Experimentos <em>de mudança</em>",
    lede="Da aposta à hipótese, a medida com o critério de revisão, o plano do experimento em uma página e o portfólio de experimentos da turma.",
    capaz=["Formular a hipótese do experimento, com ação, comportamento esperado e medida.", "Definir a medida de comportamento, com linha de base, meta e critério de revisão.",
           "Planejar o experimento em uma página: preparar, introduzir e revisar.", "Posicionar o experimento no portfólio da turma, com data de início e de revisão."],
    blocos=[
        dict(id="e4-ab", num="00", nome="Abertura", tom="#4A3F37", titulo="A retomada, <em>em grupos</em>", constroi="O comportamento esperado em cada aposta",
             itens=[dict(t="conceito", titulo="Se discorda do experimento, está errado.", html="<p>A frase de Richard Feynman (Cornell, 1964) abre o encontro: quem decide se a aposta funciona é o que as pessoas passam a fazer depois dela, e isso só o experimento mostra.</p>"),
                    ativ("e4-a0", A4[0], None, [F("e4.a0.resp", "A Minha Resposta"), F("e4.a0.comp", "O Que as Pessoas Passam a Fazer", 2)])]),
        dict(id="e4-b1", num="01", nome="Da aposta à hipótese", tom="#7A4E6D", titulo="Da aposta <em>à hipótese</em>",
             pergunta="O que nós acreditamos que vai acontecer?", constroi="A hipótese do seu experimento, em três partes",
             capaz=["Distinguir aposta e hipótese.", "Descrever o comportamento esperado de forma que se consiga ver.", "Formular a hipótese do experimento em três partes."],
             itens=[dict(t="conceito", titulo="A hipótese em três partes",
                         html=cards([("A Ação · “Acreditamos que, se…”", "Quem faz, o quê e com que frequência."), ("O Comportamento Esperado · “então…”", "O que as pessoas afetadas passam a fazer."), ("A Medida · “e mediremos por…”", "A contagem que mostra o comportamento.")])
                              + "<p><b>O teste:</b> “O que nós veríamos as pessoas fazendo?” Se a resposta não vier, a hipótese ainda está vaga.</p>",
                         fonte="Formato do curso, adaptado de Little, J. Lean Change Management, 2014."),
                    ativ("e4-a1", A4[1], "Área 1", [ESP("e4.a1.aposta", "A Aposta (do Encontro 3)", "e3.a4.aposta", 3), F("e4.a1.acao", "A Ação", 2, "Acreditamos que, se…"),
                                                   F("e4.a1.comp", "O Comportamento Esperado", 2, "então…"), F("e4.a1.medida", "A Medida", 2, "e mediremos por…")],
                         pontos=["<b>Ação com sujeito e frequência.</b> Quem faz, o quê e quantas vezes.", "<b>Comportamento das pessoas afetadas.</b> Uma cena que se consegue ver.", "<b>Medida que conta.</b> Uma contagem do comportamento, e não uma opinião sobre ele."])]),
        dict(id="e4-b2", num="02", nome="A medida e o critério de revisão", tom="#2F6B6F", titulo="A medida e o <em>critério de revisão</em>",
             pergunta="Como saberemos, em poucas semanas, se funcionou?", constroi="A ficha da medida, com as três faixas do critério",
             capaz=["Distinguir medidas de acesso, de uso, de comportamento e de resultado.", "Definir a linha de base, a meta e o sinal antecipado da medida.", "Estabelecer, antes dos dados, o critério para ampliar, ajustar ou parar."],
             itens=[dict(t="conceito", titulo="A adoção se mede pelo comportamento",
                         html="<p><b>Mito ou fato?</b> “Se a ferramenta registra muitos acessos, a adoção aconteceu.” Mito. Acesso e uso mostram que a ferramenta foi aberta; a adoção aparece no comportamento.</p>"
                              + cards([("A Linha de Base", "Quanto a medida marca hoje. Exemplo: 2 de 12 cotações sem a planilha refeita."), ("A Meta", "O valor que confirma a hipótese, na data de revisão. Exemplo: 6 de 12, em quatro semanas."),
                                       ("O Sinal Antecipado", "O que se observa já na primeira semana.")])
                              + "<p><b>O critério de revisão, definido antes dos dados:</b> ampliar se…, ajustar se…, parar se…. E <b>a confiança antes</b>, de 0 a 100%.</p>",
                         fonte="Instrumento do curso, com base em Hubbard, D. How to Measure Anything, 2007."),
                    ativ("e4-a2", A4[2], "Área 2", [ESP("e4.a2.medida", "A Medida (do Bloco 1)", "e4.a1.medida", 4), F("e4.a2.base", "A Linha de Base", 2, "Sem o dado, estime e marque com “?”"),
                                                   F("e4.a2.meta", "A Meta e A Data de Revisão", 2), dict(k="e4.a2.conf", rotulo="A Confiança Antes", tipo="texto", ph="De 0 a 100%"),
                                                   F("e4.a2.sinal", "O Sinal Antecipado", 2), F("e4.a2.crit", "O Critério de Revisão", 3, "Ampliar se… Ajustar se… Parar se…")],
                         pontos=["<b>Linha de base com origem.</b> O número de hoje diz de onde veio, ou recebe um ponto de interrogação.", "<b>Meta de comportamento.</b> Conta o que as pessoas fazem, em até quatro semanas.", "<b>Critério com três faixas.</b> Ampliar, ajustar e parar, escritas antes dos dados."])]),
        dict(id="e4-b3", num="03", nome="O plano do experimento", tom="#5E7D52", titulo="O experimento, <em>em uma página</em>",
             pergunta="O que acontece entre hoje e a data de revisão?", constroi="O plano em uma página, com etapas datadas e o risco",
             capaz=["Descrever as três etapas do experimento: preparar, introduzir e revisar.", "Identificar o risco do experimento e a forma de desfazê-lo.", "Planejar o experimento em uma página."],
             itens=[dict(t="conceito", titulo="Três etapas: preparar, introduzir e revisar",
                         html=cards([("Preparar", "Combinar com quem participa, avisar quem é afetado e registrar a linha de base."), ("Introduzir", "Executar a ação, pequena, acompanhar o sinal antecipado e anotar o que surpreende."),
                                     ("Revisar", "Ler a medida com o time, decidir entre ampliar, ajustar ou parar, e registrar o aprendizado.")])
                              + "<p><b>Seguro para falhar:</b> pequeno (uma equipe), curto (até quatro semanas), reversível (pode ser desfeito) e avisado (ninguém é surpreendido).</p>",
                         fonte="Little, J. Lean Change Management, 2014. Snowden, D.; Boone, M. HBR, 2007."),
                    ativ("e4-a3", A4[3], "Área 3", [F("e4.a3.prep", "Preparar", 3, "O que acontece, quem faz e em que data"), F("e4.a3.intro", "Introduzir", 3), F("e4.a3.rev", "Revisar", 2),
                                                   F("e4.a3.quem", "Quem Participa", 2), F("e4.a3.risco", "O Risco e Como Desfazer", 3, "Risco… Proteção… Como desfazer…")],
                         pontos=["<b>Três etapas com data.</b>", "<b>Gente avisada antes.</b> Quem participa foi consultado, e quem é afetado sabe que é um experimento.", "<b>Risco com saída.</b> O que pode dar errado, a proteção e a forma de desfazer."])]),
        dict(id="e4-b4", num="04", nome="O portfólio de experimentos", tom="#35608F", titulo="O portfólio <em>de experimentos</em>",
             pergunta="Onde a área enxerga os experimentos em andamento?", constroi="A sua linha conferida e a sua nota no portfólio da turma",
             capaz=["Organizar os experimentos em um quadro visível, por etapa.", "Avaliar um experimento por quatro critérios: pequeno, visível, medido e reversível.", "Posicionar o seu experimento no portfólio da turma."],
             itens=[dict(t="conceito", titulo="Um quadro para os experimentos da área",
                         html=cards([("Visível para a área", "Quem é afetado consegue ver o que está em teste."), ("Até três em Introduzir", "Um experimento novo começa quando outro chega à revisão."), ("Revisão com data", "Na data, a medida é lida e o cartão muda de coluna.")])
                              + "<p>Quatro colunas: <b>A Seguir</b>, <b>Preparar</b>, <b>Introduzir</b> (limite de três) e <b>Revisar</b>.</p>",
                         fonte="Little, J. Lean Change Management, 2014. Anderson, D. Kanban, 2010."),
                    ativ("e4-a4", A4[4], "Área 4", [F("e4.a4.frase", "O Experimento em Uma Frase", 2), dict(k="e4.a4.ini", rotulo="O Início", tipo="texto"), dict(k="e4.a4.rev", rotulo="A Revisão", tipo="texto"),
                                                   dict(k="e4.a4.crit", rotulo="Os Quatro Critérios, Conferidos pelo Grupo", tipo="tabela", n=1,
                                                        colunas=[dict(t="Pequeno", opcoes=["✔", "?"]), dict(t="Visível", opcoes=["✔", "?"]), dict(t="Medido", opcoes=["✔", "?"]), dict(t="Reversível", opcoes=["✔", "?"])]),
                                                   dict(k="e4.a4.col", rotulo="A Coluna no Portfólio", tipo="escolha", opcoes=["Preparar", "A Seguir"])],
                         pontos=["<b>Onde estão os cartões.</b> A maior parte em Preparar; os que dependem de decisão, em A Seguir.", "<b>Os pontos de interrogação.</b> O critério que mais aparece com “?” indica o ajuste antes de começar.", "<b>As datas de revisão.</b> Todas em até quatro semanas, já na agenda de quem participa."])]),
        dict(id="e4-fe", num="05", nome="Fechamento", tom="#B5781E", titulo="Até o <em>próximo encontro</em>", constroi="A data de revisão na agenda",
             itens=[dict(t="atividade", id="e4-a5", titulo="Até o próximo encontro", tempo="até 27/11", area=None,
                         passos=["<b>Marque a revisão.</b> Coloque a data de revisão na agenda, com as pessoas que participam do experimento.",
                                 "<b>Mostre o plano a uma pessoa.</b> Se houver oportunidade até amanhã: alguém da etapa de preparar. Pergunte o que ela mudaria.",
                                 "<b>Registre no workbook.</b> A hipótese, a medida, o plano e o cartão do portfólio, nesta página."],
                         meta=[("Próximo encontro", "Sexta-feira, 27 de novembro, às 19h."), ("Tema", "Alinhamento e sustentabilidade: estratégia da mudança, rede de campeões e métricas de adoção.")],
                         campos=[F("e4.a5.agenda", "A Revisão na Agenda: Data e Quem Participa", 2), F("e4.a5.reacao", "O Que a Pessoa Mudaria no Plano", 2)],
                         conducao=["Discussão do encontro, 20 minutos (21h40 a 22h00): que mudança da sua organização teria sido diferente se começasse como experimento? Que número faria a sua área parar um experimento, e quem decide isso? Quem precisa saber, antes de segunda-feira, que o seu experimento vai começar?"])]),
    ])

# ============================== ENCONTRO 5 ==============================
A5 = atividades(["e5_a.py", "e5_b.py"])
E5 = dict(n=5, tom="#5E7D52", data="27 de novembro de 2026", miro="https://miro.com/app/board/uXjVEMMXhv4=/",
    titulo="Alinhamento <em>e sustentabilidade</em>",
    lede="O canvas estratégico da mudança, a rede de campeões, o painel de adoção e o roteiro de sustentabilidade em 90 dias, com a apresentação final e a certificação.",
    capaz=["Relacionar os produtos dos quatro encontros no canvas estratégico da mudança.", "Desenhar a rede de campeões da sua adoção, a partir da curva de Rogers.",
           "Montar o painel de adoção, com medidas por degrau e o sinal de regressão.", "Planejar a sustentabilidade em 90 dias e apresentar a estratégia completa a colegas."],
    blocos=[
        dict(id="e5-ab", num="00", nome="Abertura", tom="#4A3F37", titulo="A retomada, <em>em grupos</em>", constroi="Quem sustenta cada experimento",
             itens=[dict(t="conceito", titulo="A mudança se sustenta quando passa a ser o jeito como fazemos as coisas aqui.",
                         html="<p>A frase de John Kotter (Harvard Business Review, 1995) abre o último encontro. No chat: algo que hoje é o jeito de trabalhar e que já foi novidade.</p>"),
                    ativ("e5-a0", A5[0], None, [F("e5.a0.resp", "A Minha Resposta"), dict(k="e5.a0.quem", rotulo="Quem Sustenta o Meu Experimento Hoje", tipo="escolha", opcoes=["A liderança", "Colegas da equipe", "Ninguém ainda"])])]),
        dict(id="e5-b1", num="01", nome="O canvas estratégico da mudança", tom="#35608F", titulo="O canvas estratégico <em>da mudança</em>",
             pergunta="Como contar a mudança inteira em uma página?", constroi="As duas primeiras faixas do canvas da sua adoção",
             capaz=["Relacionar os produtos dos quatro encontros num só instrumento.", "Formular a visão da adoção como comportamento, em 90 dias.", "Testar o canvas com a pergunta de quem decide."],
             itens=[dict(t="conceito", titulo="O canvas estratégico, em nove campos",
                         html=tb([["<b>Por que e para onde</b>", "A Urgência (Encontro 1) · A Visão (Bloco 1) · O Que Termina (Encontro 1)"], ["<b>O que a turma já construiu</b>", "As Pessoas (Encontro 2) · As Forças (Encontro 3) · O Experimento (Encontro 4)"],
                                  ["<b>O que sustenta</b>", "A Rede (Bloco 2) · O Painel (Bloco 3) · As Margens (Bloco 4)"]], ["Faixa", "Campos"])
                              + "<p><b>O teste da visão:</b> “O que veríamos as pessoas fazendo, em 90 dias?” Exemplo: em 90 dias, os compradores apresentam a cotação pela comparação do assistente, e a planilha refeita passa a ser exceção.</p>",
                         fonte="Instrumento do curso, inspirado no canvas de mudança do Lean Change Management (Little, 2014)."),
                    ativ("e5-a1", A5[1], "Área 1", [ESP("e5.a1.v1", "O Que Termina, no Encontro 1", "e1.a2.termina", 1), ESP("e5.a1.v3", "A Força Com Estrela, no Encontro 3", "e3.a2.estrela", 3), ESP("e5.a1.v4", "O Experimento, no Encontro 4", "e4.a4.frase", 4),
                                                   F("e5.a1.urg", "A Urgência", 2, "Um fato da rotina da área"), F("e5.a1.visao", "A Visão", 2, "Em 90 dias, as pessoas…"), F("e5.a1.termina", "O Que Termina", 2),
                                                   F("e5.a1.pessoas", "As Pessoas", 2), F("e5.a1.forcas", "As Forças", 2), F("e5.a1.exp", "O Experimento", 2)],
                         pontos=["<b>Urgência que se sente.</b> Um fato da rotina da área, e não uma tendência do mercado.", "<b>Visão que se vê.</b> Gente fazendo algo diferente, em 90 dias, com um número.", "<b>Fios entre os campos.</b> O experimento responde a uma força; a visão descreve o fim do que termina."])]),
        dict(id="e5-b2", num="02", nome="A rede de campeões", tom="#7A4E6D", titulo="A rede <em>de campeões</em>",
             pergunta="Quem sustenta a adoção quando a novidade passa?", constroi="O mapa da rede, com o ritual e o primeiro pedido",
             capaz=["Identificar os campeões entre os adotantes iniciais.", "Distinguir os papéis do patrocinador e dos campeões.", "Desenhar a rede de campeões da sua adoção."],
             itens=[dict(t="conceito", titulo="O campeão é quem a maioria observa",
                         html="<p><b>Mito ou fato?</b> “O campeão ideal é a pessoa que mais entende de IA na equipe.” Mito. Os inovadores dominam a ferramenta e costumam ser vistos como diferentes do grupo; a maioria observa os adotantes iniciais: colegas respeitados, parecidos com ela, que adotam com critério.</p>"
                              + cards([("O Patrocinador", "Tem alçada, dá o exemplo em público e remove obstáculos."), ("Os Campeões", "Adotantes iniciais, um por equipe, com tempo reservado: mostram, escutam e devolvem."), ("A Maioria", "Adota ao ver o colega parecido usar com resultado.")])
                              + "<p><b>O ritual da rede:</b> quinze minutos por semana, com o patrocinador. O que vimos, o que impediu e o que apresentamos à diretoria.</p>",
                         fonte="Rogers, E. Diffusion of Innovations, 5ª ed., 2003. Papéis da rede: instrumento do curso."),
                    ativ("e5-a2", A5[2], "Área 2", [F("e5.a2.patro", "O Patrocinador", 2, "Por papel, sem nome"), F("e5.a2.camp", "Os Campeões", 2), F("e5.a2.maioria", "A Maioria Que Cada Um Alcança", 2),
                                                   F("e5.a2.recebe", "O Que Cada Campeão Recebe", 2), F("e5.a2.ritual", "O Ritual da Rede", 2), F("e5.a2.pedido", "O Primeiro Pedido", 2, "O que você pede, e até quando"),
                                                   F("e5.a2.canvas", "A Rede, em Uma Frase, para o Canvas", 2)],
                         pontos=["<b>Campeões entre os pares.</b> Adotantes iniciais da própria equipe, e não a liderança nem o especialista.", "<b>Patrocinador presente.</b> Aparece em público, com frequência, e remove o obstáculo.", "<b>Ritual e pedido com data.</b> Quinze minutos por semana e um primeiro pedido pequeno, datado."])]),
        dict(id="e5-b3", num="03", nome="O painel de adoção", tom="#2F6B6F", titulo="O painel <em>de adoção</em>",
             pergunta="Como a área saberá, em 90 dias, que a adoção se sustenta?", constroi="O painel com quatro degraus e o sinal de regressão",
             capaz=["Escolher uma medida para cada degrau da adoção.", "Definir o valor de hoje e a meta em 90 dias.", "Identificar o sinal de regressão e quem lê o painel."],
             itens=[dict(t="conceito", titulo="O painel de adoção, em quatro degraus",
                         html=tb([["Acesso", "Licenças ativas no time de compras.", "12 de 12", "12 de 12"], ["Uso", "Compradores que abrem o assistente na semana.", "7 de 12", "11 de 12"],
                                  ["Comportamento", "Cotações da semana sem a planilha refeita.", "2 de 12", "8 de 12"], ["Resultado", "Prazo médio da cotação.", "5 dias", "3 dias"]], ["Degrau", "A medida (exemplo)", "Hoje", "Em 90 dias"])
                              + "<p><b>O sinal de regressão</b> é o jeito antigo voltando, definido antes: duas reuniões seguidas com mais de metade das cotações na planilha. <b>A leitura:</b> cada número tem quem o lê e uma data. Kotter (1995) aponta a declaração de vitória precoce entre os erros que mais comprometem uma transformação.</p>",
                         fonte="Escada de medidas do Encontro 4, com base em Hubbard, D., 2007. Kotter, J. HBR, 1995. Caso fictício da área de compras."),
                    ativ("e5-a3", A5[3], "Área 3", [ESP("e5.a3.v4", "A Medida de Comportamento, no Encontro 4", "e4.a1.medida", 4),
                                                   dict(k="e5.a3.painel", rotulo="O Meu Painel de Adoção", tipo="tabela", n=4,
                                                        colunas=[dict(t="Degrau", opcoes=["Acesso", "Uso", "Comportamento", "Resultado"]), dict(t="A Medida"), dict(t="Hoje", ph="Sem o dado: “?”"), dict(t="Em 90 Dias")]),
                                                   F("e5.a3.regr", "O Sinal de Regressão", 2), F("e5.a3.leitura", "Quem Lê e Quando", 2), F("e5.a3.canvas", "O Painel, em Uma Frase, para o Canvas", 2)],
                         pontos=["<b>Comportamento no centro.</b> O degrau da adoção é a medida do experimento, com meta em 90 dias.", "<b>Regressão nomeada.</b> O sinal do jeito antigo voltando, escrito antes de aparecer.", "<b>Leitura com data.</b> Quem lê cada número, quando, e o que pode decidir."])]),
        dict(id="e5-b4", num="04", nome="O roteiro de sustentabilidade", tom="#5E7D52", titulo="O roteiro <em>de sustentabilidade</em>",
             pergunta="O que mantém o novo jeito quando ninguém estiver olhando?", constroi="O roteiro de 90 dias, a margem a mudar e a apresentação final",
             capaz=["Planejar a sustentação da adoção em 30, 60 e 90 dias.", "Identificar a margem a mudar: a rotina, a regra, o padrão ou o reconhecimento.", "Apresentar a estratégia da mudança a colegas e incorporar a devolutiva."],
             itens=[dict(t="conceito", titulo="O roteiro em 30, 60 e 90 dias, até as margens",
                         html=cards([("30 dias · revisar e decidir", "A revisão do experimento, com o critério escrito antes. A rede se reúne toda semana."), ("60 dias · ampliar com a rede", "O que funcionou chega a outras equipes, pelos campeões, com o painel lido."),
                                     ("90 dias · mudar as margens", "A rotina, a regra ou o padrão mudam para o novo jeito ser o caminho natural.")])
                              + "<p><b>As margens que sustentam o novo jeito:</b> a rotina (a reunião abre pela tela), a regra (o que pode ir ao assistente), o padrão (o modelo oficial de cotação) e o reconhecimento (o que a avaliação valoriza).</p>",
                         fonte="Roteiro de sustentabilidade: instrumento do curso. Kotter, J. HBR, 1995. Snowden, D.; Rancati, A. Cynefin Field Guide, 2021."),
                    ativ("e5-a4", A5[4], "Área 4", [F("e5.a4.d30", "30 Dias", 2, "O que acontece e quem faz"), F("e5.a4.d60", "60 Dias", 2), F("e5.a4.d90", "90 Dias", 2),
                                                   F("e5.a4.margem", "A Margem a Mudar", 2, "A rotina, a regra, o padrão ou o reconhecimento"), dict(k="e5.a4.decide", rotulo="Quem Decide", tipo="texto"),
                                                   F("e5.a4.devol", "O Que Ouvi na Apresentação Final", 3, "A resposta dos colegas: o que sustenta isso quando ninguém estiver olhando?"),
                                                   F("e5.a4.canvas", "As Margens, em Uma Frase, para o Canvas", 2)],
                         pontos=["<b>Margem com responsável.</b> A rotina, a regra, o padrão ou o reconhecimento, com quem decide.", "<b>Roteiro que passa pela rede.</b> Os 60 dias ampliam pelos campeões, e não por comunicado.", "<b>Painel na agenda.</b> A leitura de cada número já tem data e pessoa."])]),
        dict(id="e5-fe", num="05", nome="Fechamento e certificação", tom="#B04A1C", titulo="As margens <em>e a certificação</em>", constroi="A margem que você muda primeiro",
             itens=[dict(t="conceito", titulo="Você não diz à água para onde ir. Você muda as margens.",
                         html="<p>A frase de Dave Snowden, que abriu o curso no Encontro 1, fecha o último encontro. Em cinco encontros, a turma escutou o sistema, escolheu uma aposta, testou, mediu e desenhou as margens.</p>"),
                    dict(t="conceito", titulo="A certificação: presença e participação",
                         html=cards([("Presença", "Em pelo menos quatro dos cinco encontros: 80% das 15 horas."), ("Participação", "Os registros das atividades no Miro e neste workbook, com a apresentação final entre pares."),
                                     ("Certificado", "Enviado por e-mail ao término da turma, depois da conferência dos dois critérios.")])),
                    dict(t="atividade", id="e5-a5", titulo="A margem que você muda primeiro", tempo="2 min", area=None,
                         perg="“Qual é a margem que você vai mudar primeiro?”",
                         passos=["No chat, escreva <b>a margem que você vai mudar primeiro</b>, em até dez palavras.", "Registre aqui a mesma frase, com a data em que pretende mudá-la."],
                         meta=[("Com quem", "Individual, no chat da turma."), ("Entrega", "A margem e a data."), ("Depois do curso", "Dúvidas pelo botão Perguntar ao mentor, que chega ao Gino Terentim.")],
                         campos=[F("e5.a5.margem", "A Margem Que Mudo Primeiro, e Quando", 2), F("e5.a5.curso", "O Que Muda no Meu Trabalho Depois Destes Cinco Encontros", 3)],
                         conducao=["Discussão do encontro e do curso, 20 minutos (21h40 a 22h00): que margem da sua organização mais protege o jeito antigo? Quem seria o primeiro campeão da sua área, e o que essa pessoa precisaria receber? O que você faz na segunda-feira, com a estratégia que construiu?"])]),
    ])

if __name__ == "__main__":
    import copy
    base = os.path.dirname(os.path.abspath(__file__))
    c = json.load(open(os.path.join(base, "conteudo.json"), encoding="utf-8"))
    notas = json.load(open(os.path.join(base, "professor_notas.json"), encoding="utf-8"))
    c["encontros"] = [e for e in c["encontros"] if e["n"] in (1, 2)]
    for enc in (E3, E4, E5):
        pub = copy.deepcopy(enc)
        for b in pub["blocos"]:
            for it in b["itens"]:
                if it["t"] == "atividade":
                    notas[it["id"]] = {k: it.pop(k) for k in ("conducao", "resposta", "debrief") if k in it}
        c["encontros"].append(pub)
    json.dump(c, open(os.path.join(base, "conteudo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(notas, open(os.path.join(base, "professor_notas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("ok", [e["n"] for e in c["encontros"]], len(notas))
    for a in A3 + A4 + A5: print(a["titulo"], a["mins"], len(a["passos"]), [k for k, _ in a["ficha"]])
