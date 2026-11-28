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
            if isinstance(v, ast.Call) and getattr(v.func, "id", "") in ("atividade", "atividade_m"):
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

B4 = "https://miro.com/app/board/uXjVEN1S8z0=/"
LCC = "https://leanchange-mwfk2i9q.manus.space/grupo/"


def _a(href, txt, ext=True): return f'<a href="{href}"' + (' target="_blank" rel="noopener"' if ext else "") + f">{txt}</a>"


LINKS = cards([("Quadros do Miro", " · ".join([_a("https://miro.com/app/board/uXjVENt1lIM=/", "Encontro 1"), _a("https://miro.com/app/board/uXjVENsiEuo=/", "Encontro 2"),
                                                _a("https://miro.com/app/board/uXjVEN1xbkY=/", "Encontro 3"), _a(B4, "Encontros 4 e 5")])),
               ("Atalhos do quadro do Encontro 4", " · ".join([_a(B4 + "?moveToWidget=3458764690548250338", "Área 1"), _a(B4 + "?moveToWidget=3458764690548299604", "Área 2"),
                                                              _a(B4 + "?moveToWidget=3458764690548368631", "Área 3"), _a(B4 + "?moveToWidget=3458764691818150803", "Portfólio"),
                                                              _a(B4 + "?moveToWidget=3458764691736968059", "Área 5")])),
               ("Lean Change Canvas", "O canvas do seu grupo, no computador: " + " · ".join([_a(LCC + "e51781e85c3e", "Grupo 1"), _a(LCC + "c0db4ed9e561", "Grupo 2"), _a(LCC + "582cec32c845", "Grupo 3")])),
               ("Mentores", _a("mentor.html", "Mentor de experimentos", False) + " · " + _a("rede.html", "Mentor da rede de campeões", False) + ". O mesmo e-mail e código do workbook."),
               ("Slides e gravações", "Na página de cada encontro, em Materiais do encontro: " + " · ".join(_a(f"e{n}.html", f"Encontro {n}", False) for n in range(1, 6)) + "."),
               ("Dúvidas", _a("mentoria.html", "Dúvidas para o Gino Terentim", False) + ": a resposta volta para a sua página e para o seu e-mail.")])

# ============================== ENCONTRO 5 ==============================
A5 = atividades(["e5v10_a.py", "e5v10_b.py"])
FRASES = ("<p><b>Frases para o Mentor de experimentos</b> (workbook, Mentor de experimentos):</p><ul>"
          "<li><b>“Continue de onde paramos”</b>: ele diz onde você parou e segue para o próximo campo.</li>"
          "<li><b>“Ainda não tenho aposta”</b>: ele começa pelas opções do Encontro 3.</li>"
          "<li><b>“me ajude a montar o Preparar”</b>: no plano, ele monta cada etapa com você.</li>"
          "<li><b>“teste o meu critério de revisão”</b> e <b>“teste o risco do meu plano”</b>: ele confere e sugere ajustes.</li>"
          "<li><b>“Monte a ficha do meu experimento”</b>: ele reúne tudo numa ficha, com “?” no que faltar.</li>"
          "<li><b>“teste o meu Agora”</b>: no Bloco 3, ele confere se cada ação tem responsável e data e se o seu campeão tem um papel nesta semana.</li></ul>"
          "<p>O Mentor sugere; quem decide e registra no quadro é você.</p>")
E5 = dict(n=5, tom="#5E7D52", data="27 de novembro de 2026", miro="https://miro.com/app/board/uXjVEN1S8z0=/",
    titulo="Alinhamento <em>e sustentabilidade</em>",
    lede="O experimento completo no quadro do Encontro 4, com o Mentor; o canvas da mudança, em três grupos à sua escolha, no sistema Lean Change Canvas; a rede de campeões de cada pessoa, com o Mentor da rede, a apresentação final em trios e a certificação.",
    capaz=["Completar o experimento: a hipótese, a medida com o critério de revisão e o plano em três etapas.", "Construir em grupo o canvas da mudança, com as perguntas que um plano de adoção precisa responder.",
           "Estruturar a rede de campeões da adoção: quem a maioria observa, quem liga grupos e o papel de cada campeão.", "Apresentar a rede a colegas e ajustar os papéis com o que ouvir."],
    blocos=[
        dict(id="e5-ab", num="00", nome="Abertura", tom="#4A3F37", titulo="Onde paramos <em>e o que fazemos hoje</em>", constroi="Os três endereços abertos",
             itens=[dict(t="conceito", titulo="A mudança se sustenta quando passa a ser o jeito como fazemos as coisas aqui.",
                         html="<p>A frase de John Kotter (Harvard Business Review, 1995) abre o último encontro. No chat: algo que hoje é o jeito de trabalhar e que um dia já foi novidade.</p>"),
                    dict(t="conceito", titulo="Três endereços para hoje",
                         html=cards([("Quadro do Encontro 4", "Áreas 1 a 3, o experimento, na linha com o seu número. Depois da aula, a Área 5, opcional."),
                                     ("Mentor de experimentos", "Neste workbook. Ele já conhece o que você registrou no quadro e onde parou."),
                                     ("Workbook do curso", "Os registros, os materiais e o botão Perguntar ao Gino Terentim.")])
                              + "<p><b>Sistema Lean Change Canvas, no Bloco 2:</b> o link do seu grupo chega no chat às 20h19: abra-o ainda na sala principal, antes de ir para a sala do grupo. Use o computador: arrastar as cartas exige mouse. <b>Mentor da rede de campeões, no Bloco 3:</b> <a href=\"rede.html\">rede.html</a>, com o mesmo e-mail e código.</p>"
                              + "<p>O Encontro 4 terminou na hipótese. Hoje a turma volta ao mesmo quadro, completa o experimento e segue a partir dele.</p>")]),
        dict(id="e5-b1", num="01", nome="O experimento completo", tom="#35608F", titulo="O experimento <em>completo</em>",
             pergunta="O que falta para o seu experimento começar na segunda-feira?", constroi="A hipótese completa, a ficha da medida e o plano, no quadro do Encontro 4",
             capaz=["Completar a hipótese em três partes.", "Definir a linha de base, a meta, o sinal antecipado e o critério de revisão.", "Planejar o experimento em três etapas datadas, com o risco e a forma de desfazê-lo."],
             itens=[dict(t="conceito", titulo="Como seguir a conversa com o Mentor", html=FRASES),
                    dict(t="conceito", titulo="A medida e o critério de revisão",
                         html=cards([("A Linha de Base", "Quanto a medida marca hoje. Exemplo: 2 de 12 cotações sem a planilha refeita."), ("A Meta e A Data de Revisão", "O valor que confirma a hipótese. Exemplo: 6 de 12, em quatro semanas."),
                                     ("O Sinal Antecipado", "O que se observa já na primeira semana.")])
                              + "<p><b>O critério, definido antes dos dados:</b> ampliar se…, ajustar se…, parar se…. E <b>a confiança antes</b>, de 0 a 100%.</p>",
                         fonte="Instrumento do curso, com base em Hubbard, D. How to Measure Anything, 2007."),
                    ativ("e5-a1", A5[0], "Encontro 4, Áreas 1 e 2", [ESP("e5.a1.acao", "A Ação (Encontro 4)", "e4.a1.acao", 4), ESP("e5.a1.comp", "O Comportamento Esperado (Encontro 4)", "e4.a1.comp", 4),
                                                   ESP("e5.a1.medida", "A Medida (Encontro 4)", "e4.a1.medida", 4),
                                                   F("e5.a1.ficha", "A Ficha da Medida, Como Ficou no Quadro", 4, "Linha de base… Meta e data… Confiança… Sinal antecipado… Ampliar se… Ajustar se… Parar se…")],
                         pontos=["<b>Hipótese com as três partes.</b> A ação, o comportamento e a medida, na linha de cada pessoa.", "<b>Linha de base com origem.</b> Sem o dado, uma estimativa marcada com “?”.", "<b>Critério escrito antes.</b> As três faixas, com números."]),
                    dict(t="conceito", titulo="Três etapas: preparar, introduzir e revisar",
                         html=cards([("1 · Preparar", "Combinar com quem participa, avisar quem é afetado e registrar a linha de base."), ("2 · Introduzir", "Executar a ação, pequena, acompanhar o sinal antecipado e anotar o que surpreende."),
                                     ("3 · Revisar", "Ler a medida com o time e decidir entre ampliar, ajustar ou parar.")]),
                         fonte="Little, J. Lean Change Management, 2014."),
                    ativ("e5-a2", A5[1], "Encontro 4, Área 3", [F("e5.a2.plano", "O Plano: Preparar, Introduzir e Revisar", 3, "O que acontece, quem faz e em que data"),
                                                   F("e5.a2.risco", "O Risco, a Proteção e Como Desfazer", 2), F("e5.a2.ficha", "A Ficha do Mentor", 4, "Cole aqui a ficha que o Mentor montou")],
                         pontos=["<b>Três etapas com data.</b> A revisão na data da Área 2.", "<b>Risco com saída.</b> A proteção e a forma de desfazer.", "<b>Nenhum “?” sem resposta prevista.</b> Cada lacuna da ficha tem quem a responda."])]),
        dict(id="e5-b2", num="02", nome="O canvas da mudança", tom="#7A4E6D", titulo="O canvas <em>da mudança</em>",
             pergunta="Que perguntas um plano de adoção de IA não pode deixar de responder?", constroi="Um canvas de até nove cartas por grupo, exportado",
             capaz=["Distinguir campos técnicos e perguntas poderosas.", "Escolher as perguntas que o plano da mudança precisa responder.", "Construir o canvas em grupo, no sistema."],
             itens=[dict(t="conceito", titulo="Construir o instrumento, antes de preenchê-lo",
                         html=cards([("Cartas azuis", "Campos técnicos: o que o plano precisa descrever."), ("Cartas amarelas", "Perguntas poderosas: o que o plano precisa enfrentar."),
                                     ("Até nove cartas", "A escolha é o exercício: o canvas mostra as perguntas que o seu plano ainda não responde.")])
                              + "<p>O canvas de hoje é o instrumento que orienta o plano da mudança. Ele não é preenchido em aula.</p>",
                         fonte="Lean Change Canvas, sistema de Gino Terentim, com base em Little, J. Lean Change Management, 2014."),
                    ativ("e5-a3", A5[2], None, [F("e5.a3.cartas", "As Cartas do Canvas do Meu Grupo", 4, "Uma carta por linha"), F("e5.a3.pergunta", "A Pergunta Que o Meu Plano Ainda Não Responde", 2)],
                         pontos=["<b>Azuis e amarelas.</b> O canvas equilibra o que descrever e o que enfrentar.", "<b>Até nove cartas.</b> A escolha mostra a prioridade.", "<b>Exportado.</b> Cada grupo exporta o canvas e o mostra em um minuto; cada pessoa sai com o próprio canvas."])]),
        dict(id="e5-b3", num="03", nome="A rede de campeões", tom="#35608F", titulo="A rede <em>de campeões</em>",
             pergunta="Quem a sua equipe observa antes de adotar algo novo?", constroi="A rede de campeões da sua adoção, com o Mentor da rede",
             capaz=["Identificar, na rede da adoção, quem a maioria observa e quem liga grupos.", "Escolher de dois a três campeões, cada um com o seu papel até a revisão.", "Apresentar a rede a colegas e ajustá-la com as perguntas deles."],
             itens=[dict(t="conceito", titulo="Quem espalha a adoção: líderes de opinião e pontes",
                         html=cards([("O líder de opinião", "O mais procurado quando há dúvida; em geral, um adotante inicial que a maioria respeita."), ("A ponte", "Liga grupos que pouco se falam: sem ela, a prática para num só grupo."),
                                     ("O quase par de quem resiste", "Parecido com o grupo que mais resiste: a semelhança dá credibilidade.")])
                              + "<p>Na análise de redes, o <b>grau</b> mostra quem é mais procurado, e a <b>intermediação</b>, quem liga grupos. O inovador isolado raramente convence a maioria.</p>"
                              + "<p><a class=\"btn\" href=\"rede.html\">Abrir o Mentor da rede de campeões</a></p>",
                         fonte="Rogers, E. M. Diffusion of Innovations, 5. ed., 2003, cap. 7 a 9; Wasserman, S.; Faust, K. Social Network Analysis, 1994, cap. 5."),
                    ativ("e5-a4", A5[3], None, [F("e5.a4.rede", "As Pessoas e os Laços da Minha Rede", 3, "Quem procura quem quando tem dúvida; quem liga grupos"),
                                                F("e5.a4.campeoes", "Os Meus Campeões e o Papel de Cada Um", 3, "Líder de opinião, ponte, quase par de quem resiste: o papel na semana 1 e até a revisão"),
                                                F("e5.a4.ficha", "A Ficha da Rede de Campeões", 4, "Cole aqui a ficha que o Mentor da rede montou")],
                         pontos=["<b>Campeões que a maioria observa.</b> Nem sempre quem tem o cargo.", "<b>Pontes entre grupos.</b> Sem elas, a prática para num só grupo.", "<b>Papéis com data.</b> A semana 1 e as quatro semanas até a revisão."]),
                    ativ("e5-a5", A5[4], None, [F("e5.a5.ouvi", "O Que Ouvi na Apresentação Final", 3, "O que sustenta isso quando ninguém estiver olhando?"), F("e5.a5.agora", "Os Papéis Ajustados", 3)],
                         pontos=["<b>A pergunta da sustentação.</b> Cada pessoa ouve o que mantém o novo jeito.", "<b>Os papéis ajustados.</b> Registrados aqui e no Mentor da rede."])]),
        dict(id="e5-sus", num="05", nome="Depois do curso: atividade opcional", tom="#8D8377", titulo="Atividade opcional <em>depois do curso</em>",
             pergunta="O que o seu experimento precisa para começar na segunda-feira?",
             constroi="O plano do seu experimento e, se quiser, o Grande, Próximo e Agora, com a devolutiva do Gino Terentim",
             itens=[dict(t="conceito", titulo="Até 12 de dezembro: o passo a passo",
                         html="<p>No último encontro, a turma investigou o plano do experimento e o Grande, Próximo e Agora e trouxe as dúvidas. O preenchimento ficou para depois do curso: <b>opcional, individualmente ou em grupo, até 12 de dezembro de 2026</b>. Quem fizer recebe a devolutiva do Gino Terentim, por escrito ou numa conversa.</p>"
                              "<ol class=\"passos\">"
                              "<li><b>Confira o seu experimento no portfólio da turma.</b> No quadro do Encontro 4, abaixo da Área 3, o <a href=\"" + B4 + "?moveToWidget=3458764691818150803\" target=\"_blank\" rel=\"noopener\">Portfólio de experimentos da turma</a> reúne o experimento de cada pessoa, montado pela IA a partir do que você registrou. Se algo estiver diferente, anote no seu registro, abaixo.</li>"
                              "<li><b>Complete a hipótese e a medida, se ainda faltar algum campo.</b> <a href=\"" + B4 + "?moveToWidget=3458764690548250338\" target=\"_blank\" rel=\"noopener\">Área 1</a>: a ação, o comportamento esperado e a medida. <a href=\"" + B4 + "?moveToWidget=3458764690548299604\" target=\"_blank\" rel=\"noopener\">Área 2</a>: a linha de base, a meta e a data de revisão, a confiança, o sinal antecipado e o critério (ampliar se, ajustar se, parar se).</li>"
                              "<li><b>Monte o plano na <a href=\"" + B4 + "?moveToWidget=3458764690548368631\" target=\"_blank\" rel=\"noopener\">Área 3</a>, na linha com o seu número.</b> O passo a passo está na atividade abaixo.</li>"
                              "<li><b>Se quiser, faça o Grande, Próximo e Agora na <a href=\"" + B4 + "?moveToWidget=3458764691736968059\" target=\"_blank\" rel=\"noopener\">Área 5</a>.</b> Ao terminar, escreva OK no quadradinho ao lado do seu nome.</li>"
                              "<li><b>Marque Finalizado no seu registro.</b> Com dúvida, use o botão Perguntar ao Gino Terentim: a resposta volta para este workbook e para o seu e-mail.</li></ol>"
                              "<p>O Mentor de experimentos e o Mentor da rede continuam disponíveis, com o mesmo e-mail e código.</p>"),
                    dict(t="atividade", id="e5-pos", titulo="O plano do seu experimento", tempo="até 12 de dezembro", area="Encontro 4, Área 3",
                         perg="“O que pode dar errado, e como se desfaz?”",
                         passos=["<b>1 · Preparar, o antes:</b> com quem combinar, quem avisar e a linha de base registrada antes de começar, com quem faz e até quando.",
                                 "<b>2 · Introduzir, o durante:</b> o que acontece em cada semana, até quatro semanas, e como você acompanha o sinal antecipado.",
                                 "<b>3 · Revisar, o depois:</b> como a medida é lida (pelo sistema, por uma contagem semanal ou por uma planilha) e quem decide com você entre ampliar, ajustar ou parar, na data da Área 2.",
                                 "<b>Quem Participa:</b> quem conduz, quem participa, quem ajuda a medir e quem é avisado, sempre pelo papel.",
                                 "<b>O Risco, A Proteção e Como Desfazer:</b> o que pode dar errado, o que reduz a chance ou o impacto, e o botão de emergência que devolve tudo ao jeito de hoje. Sem forma de desfazer, o experimento está grande demais: reduza o público ou o escopo antes de começar.",
                                 "No Mentor de experimentos: <b>“me ajude a montar o Preparar”</b>, <b>“teste o risco do meu plano”</b> e, no fim, <b>“Monte a ficha do meu experimento”</b>.",
                                 "Ao terminar, marque <b>Finalizado</b> no seu registro e escolha como prefere a devolutiva: por escrito ou numa conversa com o Gino Terentim."],
                         meta=[("Com quem", "Individualmente ou em grupo; com o Mentor de experimentos, se quiser."), ("Material", "Quadro do Encontro 4, Área 3, e a sua ficha da Área 2."),
                               ("Prazo", "Até 12 de dezembro de 2026."), ("Devolutiva", "Do Gino Terentim, por escrito ou numa conversa.")],
                         exemplo="<p>“1 · Preparar: a gerente e dois compradores seniores escolhem a primeira cotação e avisam o time na reunião de segunda; a linha de base é conferida: 2 de 12. Risco: aprovar uma cotação com erro do assistente. Proteção: um sênior confere antes da reunião. Como desfazer: a cotação seguinte volta à planilha.”</p><p><i>Caso fictício da área de compras.</i></p>",
                         campos=[F("e5.pos.portfolio", "O Meu Experimento no Portfólio da Turma", 2, "Está correto? Se algo estiver diferente, escreva o que precisa mudar"),
                                 F("e5.pos.plano", "O Plano: Preparar, Introduzir e Revisar", 4, "O que acontece, quem faz e em que data"),
                                 F("e5.pos.risco", "Quem Participa, O Risco, A Proteção e Como Desfazer", 3),
                                 F("e5.pos.situacao", "Situação da Atividade", tipo="escolha", opcoes=["Em andamento", "Finalizado"]),
                                 F("e5.pos.devolutiva", "Como Prefiro a Devolutiva", tipo="escolha", opcoes=["Por escrito, neste workbook", "Numa conversa com o Gino Terentim"])],
                         pontos=["<b>Três etapas com data.</b> A revisão na data da Área 2.", "<b>Risco com saída.</b> A proteção e a forma de desfazer.", "<b>Pequeno e reversível.</b> Sem forma de desfazer, reduza o público ou o escopo."],
                         conducao=["Pós-curso, até 12/12/2026 (combinado em aula, 27/11: 15 dias). Monitoramento diário: planilha da turma, aba Encontro 5 · 27-11 (e5.pos.situacao e e5.pos.devolutiva), aba Dúvidas e quadro do Encontro 4 (Áreas 3 e 5). Devolutiva do Gino Terentim a quem marcar Finalizado."]),
                    dict(t="conceito", titulo="Grande, Próximo e Agora: até 12 de dezembro, com devolutiva",
                         html=cards([("O Grande", "A visão, o propósito e a estratégia da adoção, sem desvio relevante."), ("O Próximo", "O seu experimento até a revisão, com os dois sinais do marco: a meta e o sinal antecipado."),
                                     ("O Agora", "As três coisas mais importantes a fazer nesta semana, cada uma com responsável e data, e o papel do seu campeão.")])
                              + "<p>Na <b>Área 5 do quadro do Encontro 4</b>, um canvas por pessoa. Opcional, até 12 de dezembro, individualmente ou em grupo. Funciona como um quadro Kanban: o Grande é a mudança, o Próximo é o experimento, o Agora é a semana. Ao terminar, escreva <b>OK</b> no quadradinho ao lado do seu nome: o Gino Terentim devolve um comentário a cada pessoa.</p>",
                         fonte="Little, J. Lean Change Management: Big, Next, Now (leanchange.org/elements/bignextnow)."),
                    dict(t="atividade", id="e5-a7", titulo="O seu Grande, Próximo e Agora (opcional)", tempo="até 12 de dezembro", area="Encontro 4, Área 5",
                         perg="“O que você faz na segunda-feira para a mudança chegar ao Grande?”",
                         passos=["No canvas com o seu nome, na Área 5 do quadro do Encontro 4: <b>O Grande</b>, em uma frase.", "<b>O Próximo</b>: o seu experimento até a revisão e os dois <b>sinais</b> do marco.",
                                 "<b>O Agora</b>: três ações desta semana, cada uma com responsável e data, e <b>o seu campeão</b>, escolhido com o Mentor da rede.", "Ao terminar, escreva <b>OK</b> no quadradinho ao lado do seu nome."],
                         meta=[("Com quem", "Individualmente ou em grupo; com o Mentor de experimentos, se quiser."), ("Entrega", "O canvas completo, com o OK."), ("Devolutiva", "Comentário do Gino Terentim a cada pessoa.")],
                         campos=[F("e5.a4.grande", "O Grande", 2, "A visão da adoção, em uma frase"), F("e5.a4.proximo", "O Próximo", 2), F("e5.a4.sinal", "Os Sinais do Marco", 2, "Sinal 1, a meta; sinal 2, o sinal antecipado"),
                                 F("e5.a4.agora", "O Agora: Três Ações Desta Semana", 3, "Ação, responsável e data"), F("e5.a4.campeao", "O Seu Campeão e o Papel Dele Nesta Semana", 2)],
                         conducao=["Atividade opcional depois do curso: devolutiva do Gino Terentim a partir do OK no canvas da Área 5; prazo 12/12/2026."]),
                    dict(t="conceito", titulo="Todos os endereços do curso", html=LINKS)]),
        dict(id="e5-fe", num="04", nome="Fechamento e certificação", tom="#B04A1C", titulo="As margens <em>e a certificação</em>", constroi="A margem que você muda primeiro",
             itens=[dict(t="conceito", titulo="Você não diz à água para onde ir. Você muda as margens.",
                         html="<p>A frase de Dave Snowden, que abriu o curso no Encontro 1, fecha o último encontro. Em cinco encontros, a turma escutou o sistema, escolheu uma aposta, testou e mediu; as margens são a rotina, a regra, o padrão e o reconhecimento que mantêm o novo jeito.</p>"),
                    dict(t="conceito", titulo="A certificação: presença e participação",
                         html=cards([("Presença", "Em pelo menos quatro dos cinco encontros: 80% das 15 horas."), ("Participação", "Os registros das atividades no Miro e neste workbook, com a apresentação final."),
                                     ("Certificado", "Enviado por e-mail ao término da turma, depois da conferência dos dois critérios.")])),
                    dict(t="atividade", id="e5-a6", titulo="A margem que você muda primeiro", tempo="2 min", area=None,
                         perg="“Qual é a margem que você vai mudar primeiro?”",
                         passos=["No chat, escreva <b>a margem que você vai mudar primeiro</b>, em até dez palavras.", "Registre aqui a mesma frase, com a data em que pretende mudá-la."],
                         meta=[("Com quem", "Individual, no chat da turma."), ("Entrega", "A margem e a data."), ("Depois do curso", "Dúvidas pelo botão Perguntar ao Gino Terentim, com a resposta neste workbook.")],
                         campos=[F("e5.a6.margem", "A Margem Que Mudo Primeiro, e Quando", 2), F("e5.a6.curso", "O Que Muda no Meu Trabalho Depois Destes Cinco Encontros", 3)],
                         conducao=["Discussão do encontro e do curso, 20 minutos (21h40 a 22h00)."])]),
    ])

def ajuste_em_aula_27_11(enc):
    """Decisão do Gino Terentim na aula de 27/11 (20h53): o plano do experimento (Área 3) e o Grande, Próximo e Agora (Área 5)
    ficaram para depois do curso, individualmente ou em grupo, até 12/12; na aula, a turma investigou os instrumentos e trouxe dúvidas.
    O plano em aula vira um aviso que aponta para o bloco 05 (atividade opcional depois do curso)."""
    for b in enc["blocos"]:
        for i, it in enumerate(b["itens"]):
            if it.get("id") == "e5-a2":
                b["itens"][i] = dict(t="conceito", titulo="O plano do seu experimento: na aula, investigação e dúvidas",
                                     html="<p>Na aula, a turma investigou o plano do experimento e o exemplo de compras e trouxe as dúvidas. "
                                          "O preenchimento ficou para depois do curso, individualmente ou em grupo, até 12 de dezembro: "
                                          "o passo a passo está em <a href=\"#e5-sus\">Atividade opcional depois do curso</a>, com a devolutiva do Gino Terentim.</p>")


ajuste_em_aula_27_11(E5)


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
