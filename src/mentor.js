(function(){
"use strict";
var C=window.CM4AI||{},API=C.api;
function $(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))}
var raiz=document.querySelector("[data-mentor]");if(!raiz)return;
function sessao(){try{return JSON.parse(localStorage.getItem("cm4ai:sessao")||"null")}catch(e){return null}}
function chamar(d){return fetch(API,{method:"POST",headers:{"Content-Type":"text/plain;charset=utf-8"},body:JSON.stringify(d),redirect:"follow"}).then(function(r){return r.json()})}
function esc(t){return String(t==null?"":t).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")}
// Texto do mentor: negrito com **, listas com hífen, parágrafos por linha em branco.
function formatar(t){
  var blocos=esc(t).split(/\n{2,}/),out=[],li=/^\s*([-•]|\d+[.)])\s+/;
  blocos.forEach(function(b){
    var ls=b.split("\n"),txt=[],itens=[],ord=false;
    function fechaTxt(){if(txt.length){out.push("<p>"+txt.join("<br>")+"</p>");txt=[]}}
    function fechaLista(){if(itens.length){out.push((ord?"<ol>":"<ul>")+itens.map(function(x){return "<li>"+x+"</li>"}).join("")+(ord?"</ol>":"</ul>"));itens=[]}}
    ls.forEach(function(l){
      if(li.test(l)){fechaTxt();if(!itens.length)ord=/^\s*\d/.test(l);itens.push(l.replace(li,""))}
      else{fechaLista();txt.push(l)}
    });
    fechaTxt();fechaLista();
  });
  return out.join("").replace(/\*\*(.+?)\*\*/g,"<b>$1</b>");
}
var lista=raiz.querySelector("[data-mentor-lista]"),form=raiz.querySelector("[data-mentor-form]"),campo=form.querySelector("textarea"),
    botao=form.querySelector("button"),chips=raiz.querySelector("[data-mentor-chips]"),status=raiz.querySelector("[data-mentor-status]");
var s=sessao(),hist=[],ocupado=false;
var ERRO={mentor_config:"O mentor ainda está sendo configurado. Tente de novo em alguns minutos.",
  mentor_limite:"Você chegou ao limite de mensagens de hoje. A conversa continua amanhã, e as dúvidas sobre o método podem ir para a Mentoria.",
  mentor_api:"O mentor não respondeu agora. Tente de novo em alguns segundos.",sessao:"A sua sessão terminou. Entre de novo no Meu mapa para continuar.",
  servico:"O serviço não respondeu. Tente de novo em alguns segundos.",rede:"Sem conexão com o serviço. Confira a internet e tente de novo."};
function horaAgora(){return new Date().toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"})}
function hhmm(h){var m=/(\d{2}:\d{2})/.exec(h||"");return m?m[1]:horaAgora()}
function rolar(){lista.scrollTop=lista.scrollHeight}
function balao(papel,texto,hora,extra){
  var d=document.createElement("div");d.className="zap__msg zap__msg--"+(papel==="mentor"?"mentor":"pessoa")+(extra?" "+extra:"");
  d.innerHTML='<div class="zap__txt">'+(papel==="mentor"?formatar(texto):"<p>"+esc(texto).replace(/\n/g,"<br>")+"</p>")+'</div>'+
    '<div class="zap__meta">'+(papel==="mentor"?'<button type="button" class="zap__copiar" data-copiar>Copiar</button>':'')+'<span>'+esc(hora||horaAgora())+'</span>'+
    (papel!=="mentor"?'<span class="zap__visto" aria-label="enviada">✓✓</span>':'')+'</div>';
  if(papel==="mentor"){d.querySelector("[data-copiar]").addEventListener("click",function(ev){
    var b=ev.currentTarget;try{navigator.clipboard.writeText(texto).then(function(){b.textContent="Copiado";setTimeout(function(){b.textContent="Copiar"},1800)})}catch(e){}})}
  lista.appendChild(d);rolar();return d;
}
function aviso(t){var d=document.createElement("div");d.className="zap__aviso";d.innerHTML=t;lista.appendChild(d);rolar();return d}
function digitando(on){
  var el=lista.querySelector(".zap__digitando");
  if(on&&!el){el=document.createElement("div");el.className="zap__msg zap__msg--mentor zap__digitando";el.innerHTML='<span></span><span></span><span></span>';lista.appendChild(el);rolar()}
  if(!on&&el)el.remove();
  status.textContent=on?"digitando…":"on-line · CM4AI";
}
function travar(on){ocupado=on;botao.disabled=on;$("button",chips).forEach(function(b){b.disabled=on})}
function falar(texto,abrindo){
  if(ocupado)return;
  if(!abrindo){hist.push({papel:"pessoa",texto:texto});balao("pessoa",texto)}
  travar(true);digitando(true);
  chamar({acao:"mentor",email:s.email,token:s.token,mensagens:hist.slice(-30)})
    .then(function(r){
      digitando(false);travar(false);
      if(!r||!r.ok){aviso(ERRO[(r&&r.erro)||"servico"]||ERRO.servico);if(!abrindo)hist.pop();return}
      hist.push({papel:"mentor",texto:r.resposta});balao("mentor",r.resposta,hhmm(r.hora));
    })
    .catch(function(){digitando(false);travar(false);aviso(ERRO.rede);if(!abrindo)hist.pop()});
}
if(!s){
  aviso('Para conversar com o mentor, entre com o seu e-mail e o seu código de quatro números. <a class="btn" href="index.html">Entrar no Meu mapa</a>');
  form.hidden=true;chips.hidden=true;return;
}
// Histórico: a conversa continua de onde parou, em qualquer dispositivo.
aviso("Carregando a conversa…");
chamar({acao:"mentor_historico",email:s.email,token:s.token}).then(function(r){
  lista.innerHTML="";
  if(r&&r.ok&&r.mensagens&&r.mensagens.length){
    r.mensagens.forEach(function(m){hist.push({papel:m.papel,texto:m.texto});balao(m.papel,m.texto,hhmm(m.hora))});
  }else if(r&&r.erro==="sessao"){aviso(ERRO.sessao);form.hidden=true;chips.hidden=true}
  else falar("",true);
}).catch(function(){lista.innerHTML="";aviso(ERRO.rede)});
form.addEventListener("submit",function(ev){ev.preventDefault();var t=campo.value.trim();if(!t||ocupado)return;campo.value="";ajustar();falar(t)});
campo.addEventListener("keydown",function(ev){if(ev.key==="Enter"&&!ev.shiftKey){ev.preventDefault();form.requestSubmit?form.requestSubmit():form.dispatchEvent(new Event("submit"))}});
function ajustar(){campo.style.height="auto";campo.style.height=Math.min(campo.scrollHeight,140)+"px"}
campo.addEventListener("input",ajustar);
$("[data-chip]",chips).forEach(function(b){b.addEventListener("click",function(){falar(b.getAttribute("data-chip"))})});
})();
