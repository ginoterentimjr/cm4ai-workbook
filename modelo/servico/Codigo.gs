/**
 * CM4AI On-line · Workbook da turma
 * Serviço que grava e devolve as respostas de cada participante na planilha da turma.
 * Implantação: Implantar > Nova implantação > App da Web; executar como: eu; acesso: qualquer pessoa.
 * Atualização: Implantar > Gerenciar implantações > editar > Nova versão (o endereço não muda).
 */
var PLANILHA_ID = 'ID_DA_PLANILHA_PRIVADA_DA_TURMA';
var ABA_PART = 'Participantes';
var CAB_PART = ['E-mail', 'Nome', 'Código (protegido)', 'Sessão', 'Primeiro acesso', 'Último acesso', 'Tentativas sem sucesso'];
var ENCONTROS = {1: 'Encontro 1 · dd-mm', 2: 'Encontro 2 · dd-mm'};   // uma aba por encontro
var SAL = 'SAL-PROPRIO-DA-TURMA';

function doGet() { return saida({ok: true, servico: 'cm4ai-workbook'}); }

function doPost(e) {
  var req0 = {};
  try { req0 = JSON.parse(e.postData.contents || '{}'); } catch (x) {}
  // O mentor de experimentos chama a API fora da trava, para não segurar as outras gravações durante a resposta.
  if (req0.acao === 'mentor') {
    try { return saida(mentorConversa(req0)); }
    catch (err) { return saida({ok: false, erro: 'servico', detalhe: String(err).slice(0, 200)}); }
  }
  var trava = LockService.getScriptLock();
  try {
    trava.waitLock(25000);
    var req = req0;
    var ss = SpreadsheetApp.openById(PLANILHA_ID);
    if (req.acao === 'mentor_contexto') return saida(mentorContexto(ss, req));
    if (req.acao === 'entrar') return saida(entrar(ss, req));
    if (req.acao === 'chave') return saida(enviarChave());
    if (req.acao === 'painel' || req.acao === 'responder') {
      if (!admin(req)) return saida({ok: false, erro: 'chave'});
      return saida(req.acao === 'painel' ? painel(ss) : responder(ss, req));
    }
    var p = autenticar(ss, req);
    if (!p) return saida({ok: false, erro: 'sessao'});
    if (req.acao === 'carregar') return saida(carregar(ss, p, req));
    if (req.acao === 'salvar') return saida(salvar(ss, p, req));
    if (req.acao === 'mapa') return saida(mapa(ss, p));
    if (req.acao === 'duvida') return saida(registrarDuvida(ss, p, req));
    if (req.acao === 'duvidas') return saida(minhasDuvidas(ss, p));
    if (req.acao === 'pendentes') return saida(pendentes(ss, p));
    if (req.acao === 'lidas') return saida(marcarLidas(ss, p, req));
    if (req.acao === 'mentor_historico') return saida(mentorHistorico(ss, p));
    return saida({ok: false, erro: 'acao'});
  } catch (err) {
    return saida({ok: false, erro: 'servico', detalhe: String(err).slice(0, 200)});
  } finally {
    try { trava.releaseLock(); } catch (x) {}
  }
}

function saida(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
function agora() { return Utilities.formatDate(new Date(), 'America/Sao_Paulo', 'dd/MM/yyyy HH:mm:ss'); }
function normEmail(s) { return String(s || '').trim().toLowerCase(); }
function hash(email, codigo) {
  var b = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, SAL + '|' + email + '|' + codigo, Utilities.Charset.UTF_8);
  return b.map(function (x) { return ('0' + (x & 255).toString(16)).slice(-2); }).join('');
}
function seguro(v) { v = String(v == null ? '' : v).slice(0, 20000); return /^[=+\-@]/.test(v) ? "'" + v : v; }

function abaPart(ss) {
  var a = ss.getSheetByName(ABA_PART);
  if (!a) {
    var p = ss.getSheets()[0];
    if (p && String(p.getRange(1, 1).getValue()) === 'E-mail') { a = p; a.setName(ABA_PART); }
    else { a = ss.insertSheet(ABA_PART, 0); }
    a.getRange(1, 1, 1, CAB_PART.length).setValues([CAB_PART]).setFontWeight('bold').setBackground('#2A211C').setFontColor('#FBEEE5');
    a.setFrozenRows(1); a.hideColumns(3, 2); a.setColumnWidth(1, 300); a.setColumnWidth(2, 220);
  }
  return a;
}

function linhaDe(aba, email, primeira) {
  var n = aba.getLastRow();
  if (n < primeira) return 0;
  var col = aba.getRange(primeira, 1, n - primeira + 1, 1).getValues();
  for (var i = 0; i < col.length; i++) if (normEmail(col[i][0]) === email) return primeira + i;
  return 0;
}

function entrar(ss, req) {
  var email = normEmail(req.email), codigo = String(req.codigo || '').trim(), nome = String(req.nome || '').trim().slice(0, 120);
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return {ok: false, erro: 'email'};
  if (!/^\d{4}$/.test(codigo)) return {ok: false, erro: 'codigo_formato'};
  var a = abaPart(ss), r = linhaDe(a, email, 2), h = hash(email, codigo);
  if (!r) {
    var tk = Utilities.getUuid();
    a.appendRow([email, seguro(nome), h, tk, agora(), agora(), 0]);
    return {ok: true, token: tk, nome: nome, novo: true, instrutor: email === normEmail(AVISO)};
  }
  var v = a.getRange(r, 1, 1, CAB_PART.length).getValues()[0];
  var falhas = Number(v[6] || 0);
  if (falhas >= 8) return {ok: false, erro: 'bloqueado'};
  if (!v[2]) { a.getRange(r, 3).setValue(h); v[2] = h; }
  if (v[2] !== h) { a.getRange(r, 7).setValue(falhas + 1); return {ok: false, erro: 'codigo'}; }
  var token = v[3] || Utilities.getUuid();
  if (nome && !v[1]) a.getRange(r, 2).setValue(seguro(nome));
  a.getRange(r, 4, 1, 4).setValues([[token, v[4] || agora(), agora(), 0]]);
  return {ok: true, token: token, nome: v[1] || nome, novo: false, instrutor: email === normEmail(AVISO)};
}

function autenticar(ss, req) {
  var email = normEmail(req.email), tk = String(req.token || '');
  if (!email || !tk) return null;
  var a = abaPart(ss), r = linhaDe(a, email, 2);
  if (!r) return null;
  var v = a.getRange(r, 1, 1, 4).getValues()[0];
  if (v[3] !== tk) return null;
  a.getRange(r, 6).setValue(agora());
  return {email: email, nome: v[1], linha: r};
}

function abaEnc(ss, n) {
  var nome = ENCONTROS[n];
  if (!nome) throw new Error('encontro');
  var a = ss.getSheetByName(nome);
  if (!a) {
    a = ss.insertSheet(nome);
    a.getRange(1, 1, 2, 3).setValues([['E-mail', 'Nome', 'Atualizado em'], ['email', 'nome', 'atualizado']]);
    a.getRange(1, 1, 1, 3).setFontWeight('bold').setBackground('#2A211C').setFontColor('#FBEEE5');
    a.setFrozenRows(2); a.setFrozenColumns(2); a.hideRows(2);
  }
  return a;
}

function chaves(a) {
  var c = a.getLastColumn();
  var k = a.getRange(2, 1, 1, c).getValues()[0], m = {};
  for (var i = 0; i < k.length; i++) if (k[i]) m[k[i]] = i + 1;
  return m;
}

function carregar(ss, p, req) {
  var a = abaEnc(ss, Number(req.encontro)), r = linhaDe(a, p.email, 3), out = {};
  if (r) {
    var c = a.getLastColumn(), k = a.getRange(2, 1, 1, c).getValues()[0], v = a.getRange(r, 1, 1, c).getValues()[0];
    for (var i = 3; i < c; i++) if (k[i] && v[i] !== '') out[k[i]] = String(v[i]).replace(/^'/, '');
  }
  return {ok: true, respostas: out, nome: p.nome};
}

function salvar(ss, p, req) {
  var a = abaEnc(ss, Number(req.encontro)), resp = req.respostas || {}, rot = req.rotulos || {};
  var m = chaves(a), c = a.getLastColumn(), novas = [];
  Object.keys(resp).forEach(function (k) {
    if (!/^[\w.\-:]{1,80}$/.test(k)) return;
    if (!m[k]) { c += 1; m[k] = c; novas.push([c, k, String(rot[k] || k).slice(0, 200)]); }
  });
  novas.forEach(function (x) {
    a.getRange(1, x[0]).setValue(x[2]).setFontWeight('bold').setBackground('#2A211C').setFontColor('#FBEEE5').setWrap(true);
    a.getRange(2, x[0]).setValue(x[1]);
    a.setColumnWidth(x[0], 260);
  });
  var r = linhaDe(a, p.email, 3);
  if (!r) { r = Math.max(a.getLastRow() + 1, 3); a.getRange(r, 1, 1, 2).setValues([[p.email, p.nome || '']]); }
  Object.keys(resp).forEach(function (k) { if (m[k]) a.getRange(r, m[k]).setValue(seguro(resp[k])); });
  a.getRange(r, 3).setValue(agora());
  return {ok: true, gravado: agora()};
}

function mapa(ss, p) {
  var out = {};
  Object.keys(ENCONTROS).forEach(function (n) {
    var a = ss.getSheetByName(ENCONTROS[n]);
    if (!a) { out[n] = 0; return; }
    var r = linhaDe(a, p.email, 3);
    if (!r) { out[n] = 0; return; }
    var v = a.getRange(r, 4, 1, Math.max(a.getLastColumn() - 3, 1)).getValues()[0];
    out[n] = v.filter(function (x) { return String(x).trim() !== ''; }).length;
  });
  return {ok: true, mapa: out, nome: p.nome};
}

/** Executar uma vez, pelo editor, para criar as abas e autorizar o acesso à planilha. */
function preparar() {
  var ss = SpreadsheetApp.openById(PLANILHA_ID);
  abaPart(ss);
  Object.keys(ENCONTROS).forEach(function (n) { abaEnc(ss, Number(n)); });
  var s1 = ss.getSheetByName('Página1') || ss.getSheetByName('Sheet1');
  if (s1 && ss.getSheets().length > 1) ss.deleteSheet(s1);
}


// ---------- Dúvidas: o participante pergunta, o mentor responde no painel ----------
var ABA_DUV = 'Dúvidas';
var CAB_DUV = ['ID', 'Recebida em', 'E-mail', 'Nome', 'Encontro', 'Atividade', 'Pergunta', 'Situação', 'Resposta', 'Respondida em', 'Lida em'];
var AVISO = 'EMAIL_DO_INSTRUTOR';   // recebe o aviso de cada dúvida e a chave do painel
var SITE = 'https://USUARIO.github.io/REPOSITORIO/';

function abaDuv(ss) {
  var a = ss.getSheetByName(ABA_DUV);
  if (!a) {
    a = ss.insertSheet(ABA_DUV);
    a.getRange(1, 1, 1, CAB_DUV.length).setValues([CAB_DUV]).setFontWeight('bold').setBackground('#2A211C').setFontColor('#FBEEE5');
    a.setFrozenRows(1); a.setColumnWidth(6, 260); a.setColumnWidth(7, 420); a.setColumnWidth(9, 420);
  } else if (String(a.getRange(1, CAB_DUV.length).getValue()) !== CAB_DUV[CAB_DUV.length - 1]) {
    a.getRange(1, CAB_DUV.length).setValue(CAB_DUV[CAB_DUV.length - 1]).setFontWeight('bold').setBackground('#2A211C').setFontColor('#FBEEE5');
  }
  return a;
}
// A planilha converte o texto 'dd/MM/yyyy HH:mm:ss' em data no fuso dela; a leitura devolve o mesmo horário, sem os segundos.
var FUSO_PLAN = null;
function dataTxt(x) {
  if (x instanceof Date) return Utilities.formatDate(x, FUSO_PLAN || 'America/Sao_Paulo', 'dd/MM/yyyy HH:mm');
  return String(x == null ? '' : x).replace(/^(\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}):\d{2}$/, '$1');
}
function linhasDuv(a) {
  var n = a.getLastRow();
  if (n < 2) return [];
  if (!FUSO_PLAN) FUSO_PLAN = a.getParent().getSpreadsheetTimeZone();
  return a.getRange(2, 1, n - 1, CAB_DUV.length).getValues().map(function (v, i) {
    return {linha: i + 2, id: String(v[0]), recebida: dataTxt(v[1]), email: String(v[2]), nome: String(v[3]).replace(/^'/, ''), encontro: Number(v[4]),
            atividade: String(v[5]).replace(/^'/, ''), pergunta: String(v[6]).replace(/^'/, ''), situacao: String(v[7]),
            resposta: String(v[8]).replace(/^'/, ''), respondida: dataTxt(v[9]), lida: dataTxt(v[10])};
  });
}
function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>'); }

function registrarDuvida(ss, p, req) {
  var perg = String(req.pergunta || '').trim().slice(0, 3000), ativ = String(req.atividade || '').trim().slice(0, 200), enc = Number(req.encontro) || 0;
  if (perg.length < 3) return {ok: false, erro: 'pergunta'};
  var id = 'D' + Utilities.formatDate(new Date(), 'America/Sao_Paulo', 'yyMMddHHmmss') + Math.floor(Math.random() * 90 + 10);
  var a = abaDuv(ss), quando = agora();
  a.appendRow([id, quando, p.email, seguro(p.nome || ''), enc, seguro(ativ), seguro(perg), 'Aguardando', '', '']);
  try {
    MailApp.sendEmail({to: AVISO, name: 'Workbook CM4AI',
      subject: 'CM4AI · Nova dúvida de ' + (p.nome || p.email) + (ativ ? ' · ' + ativ : ''),
      htmlBody: '<p><b>' + esc(p.nome || p.email) + '</b> enviou uma dúvida' + (enc ? ' no Encontro ' + enc : '') + (ativ ? ', na atividade <b>' + esc(ativ) + '</b>' : '') + ', às ' + quando + '.</p>' +
        '<blockquote style="border-left:4px solid #E5662C;margin:0;padding:8px 14px;background:#FBEFE4">' + esc(perg) + '</blockquote>' +
        '<p><a href="' + SITE + 'painel.html">Responder no painel de dúvidas</a></p>'});
  } catch (x) {}
  return {ok: true, id: id, recebida: quando};
}

function minhasDuvidas(ss, p) {
  var l = linhasDuv(abaDuv(ss)).filter(function (d) { return normEmail(d.email) === p.email; }).map(function (d) {
    return {id: d.id, recebida: d.recebida, encontro: d.encontro, atividade: d.atividade, pergunta: d.pergunta, situacao: d.situacao, resposta: d.resposta, respondida: d.respondida,
            lida: d.lida, nova: d.situacao === 'Respondida' && !d.lida};
  });
  return {ok: true, duvidas: l, naoLidas: l.filter(function (d) { return d.nova; }).length};
}

function chavePainel() {
  var pr = PropertiesService.getScriptProperties(), k = pr.getProperty('CHAVE_PAINEL');
  if (!k) {
    var abc = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789', s = '';
    for (var i = 0; i < 12; i++) s += abc.charAt(Math.floor(Math.random() * abc.length));
    k = s.slice(0, 4) + '-' + s.slice(4, 8) + '-' + s.slice(8);
    pr.setProperty('CHAVE_PAINEL', k);
  }
  return k;
}
function admin(req) {
  var cache = CacheService.getScriptCache(), f = Number(cache.get('falhas_painel') || 0);
  if (f >= 20) return false;
  var ok = String(req.chave || '').trim().toUpperCase() === chavePainel();
  if (!ok) cache.put('falhas_painel', String(f + 1), 900);
  return ok;
}
function enviarChave() {
  var cache = CacheService.getScriptCache();
  if (cache.get('chave_enviada')) return {ok: true, enviada: false, espera: true};
  var k = chavePainel();
  MailApp.sendEmail({to: AVISO, name: 'Workbook CM4AI', subject: 'CM4AI · Chave do painel de dúvidas',
    htmlBody: '<p>A chave do painel de dúvidas do workbook é <b style="font-size:18px;letter-spacing:2px">' + k + '</b>.</p><p><a href="' + SITE + 'painel.html">Abrir o painel</a></p>'});
  cache.put('chave_enviada', '1', 600);
  return {ok: true, enviada: true};
}

// Avisos do menu. Participante: respostas ainda não lidas. Instrutor: também a contagem de dúvidas aguardando.
// Ler e responder as dúvidas da turma continua exigindo a chave do painel.
function pendentes(ss, p) {
  var l = linhasDuv(abaDuv(ss));
  var nl = l.filter(function (d) { return normEmail(d.email) === p.email && d.situacao === 'Respondida' && !d.lida; }).length;
  if (p.email !== normEmail(AVISO)) return {ok: true, instrutor: false, naoLidas: nl};
  return {ok: true, instrutor: true, n: l.filter(function (d) { return d.situacao !== 'Respondida'; }).length, naoLidas: nl};
}

// Leitura: o participante registra como lidas as respostas que apareceram na aba Dúvidas enviadas.
function marcarLidas(ss, p, req) {
  var ids = (req.ids || []).slice(0, 200).map(String), a = abaDuv(ss), quando = agora(), n = 0;
  linhasDuv(a).forEach(function (d) {
    if (ids.indexOf(d.id) >= 0 && normEmail(d.email) === p.email && d.situacao === 'Respondida' && !d.lida) {
      a.getRange(d.linha, CAB_DUV.length).setValue(quando); n++;
    }
  });
  return {ok: true, marcadas: n, lida: quando};
}

function painel(ss) {
  var l = linhasDuv(abaDuv(ss)).reverse();
  return {ok: true, duvidas: l.map(function (d) { delete d.linha; return d; }), agora: agora()};
}

function responder(ss, req) {
  var id = String(req.id || ''), resp = String(req.resposta || '').trim().slice(0, 6000);
  if (!id || resp.length < 2) return {ok: false, erro: 'resposta'};
  var a = abaDuv(ss), d = linhasDuv(a).filter(function (x) { return x.id === id; })[0];
  if (!d) return {ok: false, erro: 'id'};
  var quando = agora();
  a.getRange(d.linha, 8, 1, 4).setValues([['Respondida', seguro(resp), quando, '']]);
  var enviado = false;
  try {
    var nome1 = (d.nome || '').split(' ')[0] || 'Olá';
    MailApp.sendEmail({to: d.email, name: 'Gino Terentim', replyTo: AVISO,
      subject: 'CM4AI · Resposta à sua dúvida' + (d.atividade ? ': ' + d.atividade : ''),
      htmlBody: '<p>' + esc(nome1) + ',</p><p>Esta é a resposta à dúvida que você enviou' + (d.encontro ? ' no Encontro ' + d.encontro : '') + (d.atividade ? ', na atividade <b>' + esc(d.atividade) + '</b>' : '') + '.</p>' +
        '<p style="color:#6E6259"><b>A sua dúvida</b><br>' + esc(d.pergunta) + '</p>' +
        '<div style="border-left:4px solid #E5662C;padding:8px 14px;background:#FBEFE4">' + esc(resp) + '</div>' +
        '<p>A resposta também está no seu workbook, junto da atividade: <a href="' + SITE + (d.encontro ? 'e' + d.encontro + '.html' : '') + '">abrir o workbook</a>.</p>' +
        '<p>Um abraço,<br>Gino Terentim</p>'});
    enviado = true;
  } catch (x) {}
  return {ok: true, respondida: quando, email: enviado};
}


// ---------- Mentor de experimentos: conversa com a API da Anthropic ----------
// A chave da API fica na propriedade do script ANTHROPIC_API_KEY. O modelo pode ser trocado na propriedade MENTOR_MODELO.
var ABA_MCTX = 'Mentor · Quadros', ABA_MCUR = 'Mentor · Curso', ABA_MLOG = 'Mentor · Conversas';
var CAB_MCTX = ['Chave', 'Número', 'Nome', 'Encontro', 'Área', 'Registros', 'Atualizado em'];
var CAB_MLOG = ['Data', 'E-mail', 'Nome', 'Quem', 'Mensagem', 'Modelo', 'Tokens de entrada', 'Tokens de saída'];
var CHAVE_CONTEXTO = '';
var MENTOR_MODELO_PADRAO = 'claude-sonnet-5-5', MENTOR_LIMITE_DIA = 80, MENTOR_MAX_TOKENS = 1100;

function abaMentor(ss, nome, cab) {
  var a = ss.getSheetByName(nome);
  if (!a) {
    a = ss.insertSheet(nome);
    a.getRange(1, 1, 1, cab.length).setValues([cab]).setFontWeight('bold').setBackground('#2A211C').setFontColor('#FBEEE5');
    a.setFrozenRows(1);
  }
  return a;
}
function chaveNome(s) {
  return String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z ]/g, ' ').replace(/\s+/g, ' ').trim();
}
function casaNome(a, b) {
  if (!a || !b) return false;
  if (a === b) return true;
  var x = a.split(' '), y = b.split(' ');
  return x[0] === y[0] && x[x.length - 1] === y[y.length - 1];
}

// O que a pessoa registrou no workbook, encontro por encontro, com o rótulo de cada campo.
function mentorWorkbook(ss, p) {
  var partes = [];
  Object.keys(ENCONTROS).forEach(function (n) {
    var a = ss.getSheetByName(ENCONTROS[n]);
    if (!a) return;
    var r = linhaDe(a, p.email, 3), c = a.getLastColumn();
    if (!r || c < 4) return;
    var rot = a.getRange(1, 1, 1, c).getValues()[0], v = a.getRange(r, 1, 1, c).getValues()[0], l = [];
    for (var i = 3; i < c; i++) {
      var t = String(v[i] == null ? '' : v[i]).replace(/^'/, '').trim();
      if (t) l.push('- ' + String(rot[i] || '').trim() + ': ' + t.slice(0, 1500));
    }
    if (l.length) partes.push('Encontro ' + n + ', no workbook:\n' + l.join('\n'));
  });
  return partes.join('\n\n');
}

// O que a pessoa registrou nos quadros do Miro (cópia gravada na aba Mentor · Quadros).
function mentorQuadros(ss, p) {
  var a = ss.getSheetByName(ABA_MCTX);
  if (!a || a.getLastRow() < 2) return '';
  var k = chaveNome(p.nome);
  if (!k) return '';
  var v = a.getRange(2, 1, a.getLastRow() - 1, CAB_MCTX.length).getValues(), por = {}, ordem = [];
  v.forEach(function (x) {
    if (!casaNome(String(x[0]), k)) return;
    var cab = String(x[3]) + ' · ' + String(x[4]);
    if (!por[cab]) { por[cab] = []; ordem.push(cab); }
    String(x[5]).split('\n').forEach(function (t) { if (t.trim()) por[cab].push('- ' + t.trim()); });
  });
  return ordem.map(function (c) { return c + ', no quadro do Miro:\n' + por[c].join('\n'); }).join('\n\n');
}
function mentorCurso(ss) {
  var a = ss.getSheetByName(ABA_MCUR);
  if (!a || a.getLastRow() < 1) return '';
  return a.getRange(1, 1, a.getLastRow(), 1).getValues().map(function (x) { return String(x[0]); }).join('\n');
}

// Duas partes: a fixa (método e curso), igual para a turma e guardada em cache pela API, e a da pessoa.
function mentorSistema(p, wb, quadros, curso) {
  var nome = String(p.nome || '').trim();
  var fixo = [
    'Você é o Mentor de Experimentos do curso Change Management for AI (CM4AI), turma on-line de novembro de 2026, conduzida por Gino Terentim (Rethinking Learning).',
    'Você conversa por mensagens, no estilo de um aplicativo de conversa, com uma pessoa da turma.',
    '',
    'PROPÓSITO',
    'Ajudar a pessoa a pensar e desenhar um experimento pequeno de mudança para a adoção da IA na área dela, a partir do que ela já registrou no curso. O experimento segue o método do curso:',
    '1. A hipótese em três partes: "Acreditamos que, se [ação, com sujeito e frequência], então [comportamento esperado das pessoas afetadas, uma cena que se consegue ver], e mediremos por [contagem do comportamento]".',
    '2. A medida: linha de base (quanto marca hoje, ou "?" se for estimativa), meta de comportamento, data de revisão em até quatro semanas, confiança antes (0 a 100%), sinal antecipado e critério de revisão com três faixas, escritas antes dos dados: ampliar, ajustar ou parar.',
    '3. O plano em uma página: preparar (quem é consultado e quem é avisado), introduzir (o que acontece e quando) e revisar (quando, com quem). Risco, proteção e forma de desfazer.',
    '4. O portfólio: o experimento em uma frase, início e revisão, e os quatro critérios: pequeno, visível, medido e reversível.',
    '',
    'COMO VOCÊ CONVERSA',
    '- Português do Brasil, tratamento por "você", registro executivo, elegante e acolhedor. Mensagens curtas: de duas a cinco frases. Uma pergunta por vez.',
    '- Você provoca o raciocínio: faz perguntas e reflexões que ajudam a pessoa a pensar. Só sugere uma redação pronta quando ela pedir ou depois de duas tentativas dela; nesse caso, apresenta como sugestão para ela ajustar.',
    '- Use o que a pessoa registrou: cite com as palavras dela o que escreveu no workbook e nos quadros ("No Encontro 1, você escreveu que...") e ligue isso ao experimento. Não invente fatos sobre a organização dela; quando faltar um dado, pergunte.',
    '- Quando a pessoa pedir a ficha do experimento, entregue um resumo organizado com os títulos: Hipótese, Linha de base, Meta, Data de revisão, Confiança antes, Sinal antecipado, Critério de revisão, Preparar, Introduzir, Revisar, Risco e forma de desfazer. Marque com "?" o que ainda falta e diga qual é a próxima pergunta. Lembre que a ficha pode ser copiada para o workbook e para o quadro do Miro.',
    '- Formatação: texto simples; use **negrito** só para destacar um termo; listas curtas com hífen quando ajudar.',
    '- Nunca use travessão; use vírgula, dois-pontos ou parênteses. Evite a construção "não é X, é Y". Evite as palavras: levar, virar, travar, rodar, puxar, dono, zona, cruzar, retardar, ensaio, mindset, "dá para", sentar, botar, fatiar, chato. Diga "framework Cynefin", nunca "matriz".',
    '',
    'LIMITES',
    '- Fale apenas dos registros desta pessoa. Os quadros do Miro são da turma inteira: nunca cite o que outro participante escreveu.',
    '- Peça que a pessoa use papéis ("a gerente da área", "um analista sênior"), e não nomes de colegas ou clientes, e que mantenha fora da conversa dados reservados da organização.',
    '- Assuntos fora do curso: responda em uma frase e volte ao experimento. Questões jurídicas, trabalhistas ou de saúde: diga que não é a sua função e sugira o especialista.',
    '- Dúvidas sobre o método que você não souber responder com segurança: sugira a aba Mentoria do workbook, em que o Gino Terentim responde.',
    '',
    'O CURSO',
    curso || '(Sem resumo do curso.)'
  ].join('\n');
  var pessoal = [
    'A PESSOA DESTA CONVERSA: ' + (nome || 'participante da turma') + '.',
    '',
    'O QUE ESTA PESSOA REGISTROU NO WORKBOOK',
    wb || '(Ainda sem registros no workbook.)',
    '',
    'O QUE ESTA PESSOA REGISTROU NOS QUADROS DO MIRO',
    quadros || '(Nenhum registro encontrado nos quadros com o nome desta pessoa.)'
  ].join('\n');
  return [{type: 'text', text: fixo, cache_control: {type: 'ephemeral'}}, {type: 'text', text: pessoal}];
}

function mentorMensagens(req) {
  var l = (req.mensagens || []).slice(-30).map(function (m) {
    return {role: m.papel === 'mentor' ? 'assistant' : 'user', content: String(m.texto || '').slice(0, 4000)};
  }).filter(function (m) { return m.content.trim(); });
  var out = [];
  if (l.length && l[0].role !== 'user') out.push({role: 'user', content: '(A pessoa abriu a conversa.)'});
  l.forEach(function (m) {
    if (out.length && out[out.length - 1].role === m.role) out[out.length - 1].content += '\n\n' + m.content;
    else out.push(m);
  });
  return out;
}

function mentorHoje(a, email) {
  var n = a.getLastRow();
  if (n < 2) return 0;
  var hoje = Utilities.formatDate(new Date(), 'America/Sao_Paulo', 'dd/MM/yyyy');
  var v = a.getRange(Math.max(2, n - 3000), 1, Math.min(n - 1, 3001), 4).getValues();
  return v.filter(function (x) { return normEmail(x[1]) === email && x[3] === 'Participante' && dataTxt(x[0]).indexOf(hoje) === 0; }).length;
}

function mentorConversa(req) {
  var ss = SpreadsheetApp.openById(PLANILHA_ID), trava = LockService.getScriptLock(), p, ctx, log;
  trava.waitLock(25000);
  try {
    p = autenticar(ss, req);
    if (!p) return {ok: false, erro: 'sessao'};
    log = abaMentor(ss, ABA_MLOG, CAB_MLOG);
    if (!FUSO_PLAN) FUSO_PLAN = ss.getSpreadsheetTimeZone();
    if (mentorHoje(log, p.email) >= MENTOR_LIMITE_DIA) return {ok: false, erro: 'mentor_limite'};
    ctx = {wb: mentorWorkbook(ss, p), quadros: mentorQuadros(ss, p), curso: mentorCurso(ss)};
  } finally { trava.releaseLock(); }
  var pr = PropertiesService.getScriptProperties(), chave = pr.getProperty('ANTHROPIC_API_KEY');
  if (!chave) return {ok: false, erro: 'mentor_config'};
  var modelo = pr.getProperty('MENTOR_MODELO') || MENTOR_MODELO_PADRAO;
  var msgs = mentorMensagens(req), abertura = !msgs.length;
  if (abertura) msgs = [{role: 'user', content: '(A pessoa acabou de abrir a conversa. Cumprimente pelo primeiro nome, mostre em uma ou duas frases que você conhece o que ela já registrou no curso, e faça a primeira pergunta para começar o experimento. Se não houver registros, pergunte qual é a adoção de IA em que ela trabalha.)'}];
  var r = UrlFetchApp.fetch('https://api.anthropic.com/v1/messages', {
    method: 'post', contentType: 'application/json', muteHttpExceptions: true,
    headers: {'x-api-key': chave, 'anthropic-version': '2023-06-01'},
    payload: JSON.stringify({model: modelo, max_tokens: MENTOR_MAX_TOKENS, system: mentorSistema(p, ctx.wb, ctx.quadros, ctx.curso), messages: msgs})
  });
  var cod = r.getResponseCode(), corpo = {};
  try { corpo = JSON.parse(r.getContentText()); } catch (x) {}
  if (cod !== 200) return {ok: false, erro: 'mentor_api', detalhe: (corpo.error && corpo.error.type) || String(cod)};
  var texto = (corpo.content || []).filter(function (c) { return c.type === 'text'; }).map(function (c) { return c.text; }).join('\n').trim();
  texto = texto.replace(/\s*—\s*/g, ', ').replace(/\s*–\s*/g, ', ');
  if (!texto) return {ok: false, erro: 'mentor_api', detalhe: 'vazio'};
  var uso = corpo.usage || {}, quando = agora();
  trava.waitLock(25000);
  try {
    var ult = abertura ? null : msgs[msgs.length - 1].content;
    if (ult) log.appendRow([quando, p.email, seguro(p.nome || ''), 'Participante', seguro(ult), modelo, '', '']);
    log.appendRow([quando, p.email, seguro(p.nome || ''), 'Mentor', seguro(texto), modelo, uso.input_tokens || '', uso.output_tokens || '']);
  } finally { trava.releaseLock(); }
  return {ok: true, resposta: texto, hora: quando};
}

function mentorHistorico(ss, p) {
  var a = ss.getSheetByName(ABA_MLOG);
  if (!a || a.getLastRow() < 2) return {ok: true, mensagens: []};
  if (!FUSO_PLAN) FUSO_PLAN = ss.getSpreadsheetTimeZone();
  var v = a.getRange(2, 1, a.getLastRow() - 1, 5).getValues();
  var l = v.filter(function (x) { return normEmail(x[1]) === p.email; }).slice(-60).map(function (x) {
    return {papel: x[3] === 'Mentor' ? 'mentor' : 'pessoa', texto: String(x[4]).replace(/^'/, ''), hora: dataTxt(x[0])};
  });
  return {ok: true, mensagens: l};
}

// Atualização do contexto: linhas dos quadros do Miro e resumo do curso, enviados com a chave de contexto.
function mentorContexto(ss, req) {
  if (!CHAVE_CONTEXTO || String(req.chave_contexto || '') !== CHAVE_CONTEXTO) return {ok: false, erro: 'chave'};
  var out = {ok: true};
  if (req.linhas) {
    var a = abaMentor(ss, ABA_MCTX, CAB_MCTX), quando = agora();
    if (a.getLastRow() > 1) a.getRange(2, 1, a.getLastRow() - 1, CAB_MCTX.length).clearContent();
    var l = req.linhas.slice(0, 3000).map(function (x) { return [chaveNome(x.nome), Number(x.numero) || '', seguro(x.nome), seguro(x.encontro), seguro(x.area), seguro(x.registros), quando]; });
    if (l.length) a.getRange(2, 1, l.length, CAB_MCTX.length).setValues(l);
    out.linhas = l.length;
  }
  if (req.curso) {
    var c = ss.getSheetByName(ABA_MCUR) || ss.insertSheet(ABA_MCUR);
    c.clear();
    var t = String(req.curso).split('\n').map(function (x) { return [seguro(x)]; });
    c.getRange(1, 1, t.length, 1).setValues(t);
    out.curso = t.length;
  }
  return out;
}
