(function(){
"use strict";
var C=window.CM4AI||{},API=C.api;
function $(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))}
var raiz=document.querySelector("[data-mentor]");if(!raiz)return;
var TIPO=raiz.getAttribute("data-mentor-tipo")||"",STATUS=raiz.getAttribute("data-mentor-on")||"on-line · CM4AI";
// Mentor da rede: o bloco ```rede {...}``` sai do balão e vai para o painel da rede.
var BLOCO=/```rede\s*([\s\S]*?)```/;
function separar(t){var m=BLOCO.exec(t||"");if(!m)return {texto:t,rede:null};var r=null;try{r=JSON.parse(m[1])}catch(e){}return {texto:String(t).replace(BLOCO,"").trim(),rede:r}}
function avisarRede(r){if(r)try{window.dispatchEvent(new CustomEvent("cm4ai:rede",{detail:r}))}catch(e){}}
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
    botao=form.querySelector("button[type=submit]"),chips=raiz.querySelector("[data-mentor-chips]"),status=raiz.querySelector("[data-mentor-status]");
var s=sessao(),hist=[],ocupado=false;
var CHAVE_LIMPO="cm4ai:mentor_limpo:"+(TIPO?TIPO+":":"")+((s&&s.email)||""),limpar=raiz.querySelector("[data-mentor-limpar]");
var AVISO_LIMPO="A tela foi limpa. O mentor continua lembrando da conversa.";
function marca(m){return (m.papel||"")+"|"+String(m.texto||"").slice(0,120)}
var ERRO={mentor_config:"O mentor ainda está sendo configurado. Tente de novo em alguns minutos.",
  mentor_limite:"Você chegou ao limite de mensagens de hoje. A conversa continua amanhã, e as dúvidas sobre o método podem ir para a Mentoria.",
  mentor_api:"O mentor não respondeu agora. Tente de novo em alguns segundos.",sessao:"A sua sessão terminou. Entre de novo no Meu mapa para continuar.",
  servico:"O serviço não respondeu. Tente de novo em alguns segundos.",rede:"Sem conexão com o serviço. Confira a internet e tente de novo.",
  audio_config:"As mensagens de voz ainda estão sendo configuradas. Por enquanto, escreva a mensagem.",
  audio_api:"Não foi possível transcrever o áudio agora. Tente de novo ou escreva a mensagem.",
  audio_vazio:"Não foi possível entender o áudio. Grave de novo, mais perto do microfone.",
  audio_tamanho:"O áudio ficou longo demais. Grave mensagens de até dois minutos."};
function horaAgora(){return new Date().toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"})}
function hhmm(h){var m=/(\d{2}:\d{2})/.exec(h||"");return m?m[1]:horaAgora()}
function rolar(){lista.scrollTop=lista.scrollHeight}
var AUD=/^🎤 Áudio · (\d+:\d{2})\n([\s\S]*)$/,MIC='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19v3"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><rect x="9" y="2" width="6" height="13" rx="3"/></svg>';
function corpoAudio(dur,transc){
  return '<div class="zap__audio"><span class="zap__audio-ic">'+MIC+'</span><span class="zap__onda" aria-hidden="true">'+new Array(23).join("<i></i>")+'</span><span class="zap__audio-dur">'+esc(dur)+'</span></div>'+
    '<p class="zap__transc">'+(transc?esc(transc).replace(/\n/g,"<br>"):'<em>Transcrevendo…</em>')+'</p>';
}
function balao(papel,texto,hora,extra){
  if(papel==="mentor"){var sp=separar(texto);if(sp.rede){avisarRede(sp.rede);texto=sp.texto+(sp.texto.indexOf("painel")>=0?"":"\n\n**A rede está desenhada no painel.**")}}
  var d=document.createElement("div"),au=papel!=="mentor"&&AUD.exec(texto||"");d.className="zap__msg zap__msg--"+(papel==="mentor"?"mentor":"pessoa")+(au?" zap__msg--audio":"")+(extra?" "+extra:"");
  d.innerHTML='<div class="zap__txt">'+(papel==="mentor"?formatar(texto):(au?corpoAudio(au[1],au[2]):"<p>"+esc(texto).replace(/\n/g,"<br>")+"</p>"))+'</div>'+
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
  status.textContent=on?"digitando…":STATUS;
}
function travar(on){ocupado=on;botao.disabled=on;if(mic)mic.disabled=on;$("button",chips).forEach(function(b){b.disabled=on})}
function falar(texto,abrindo){
  if(ocupado)return;
  if(!abrindo){hist.push({papel:"pessoa",texto:texto});balao("pessoa",texto)}
  travar(true);digitando(true);
  chamar({acao:"mentor",tipo:TIPO||undefined,email:s.email,token:s.token,mensagens:hist.slice(-30)})
    .then(function(r){
      digitando(false);travar(false);
      if(!r||!r.ok){aviso(ERRO[(r&&r.erro)||"servico"]||ERRO.servico);if(!abrindo)hist.pop();return}
      hist.push({papel:"mentor",texto:r.resposta});balao("mentor",r.resposta,hhmm(r.hora));
    })
    .catch(function(){digitando(false);travar(false);aviso(ERRO.rede);if(!abrindo)hist.pop()});
}
// ---------- Mensagem de voz: segure o microfone para gravar e solte para enviar; um toque rápido grava até tocar em Enviar ----------
var mic=form.querySelector("[data-mentor-mic]"),grava=form.querySelector("[data-mentor-grava]"),
    gTempo=grava&&grava.querySelector("[data-grava-tempo]"),gDica=grava&&grava.querySelector("[data-grava-dica]"),
    gCancelar=grava&&grava.querySelector("[data-grava-cancelar]"),gEnviar=grava&&grava.querySelector("[data-grava-enviar]");
var podeGravar=!!(mic&&navigator.mediaDevices&&navigator.mediaDevices.getUserMedia&&window.MediaRecorder);
var vozAtiva=false,rec=null,fluxo=null,partes=[],inicio=0,relogio=null,cancelar=false,segurando=false,t0=0,MAXSEG=120;
function mmss(x){x=Math.max(0,Math.round(x));return Math.floor(x/60)+":"+("0"+(x%60)).slice(-2)}
function alternar(){if(!podeGravar||!vozAtiva){if(mic)mic.hidden=true;botao.hidden=false;return}var vazio=!campo.value.trim();mic.hidden=!vazio;botao.hidden=vazio}
function tipoAudio(){var t=["audio/webm;codecs=opus","audio/mp4","audio/webm","audio/ogg;codecs=opus"];
  for(var i=0;i<t.length;i++){try{if(MediaRecorder.isTypeSupported(t[i]))return t[i]}catch(e){}}return ""}
function travadoUI(trav){gDica.textContent=trav?"Toque em enviar ao terminar":"Solte para enviar";gEnviar.hidden=!trav;mic.hidden=trav}
function modoGravando(on,travado){
  form.classList.toggle("zap__barra--gravando",on);grava.hidden=!on;campo.hidden=on;botao.hidden=true;
  if(on){gTempo.textContent="0:00";travadoUI(travado)}else{mic.hidden=false;alternar()}
}
function comecar(){
  if(ocupado||rec)return Promise.resolve(false);
  return navigator.mediaDevices.getUserMedia({audio:true}).then(function(st){
    fluxo=st;partes=[];cancelar=false;var mt=tipoAudio();
    try{rec=mt?new MediaRecorder(st,{mimeType:mt}):new MediaRecorder(st)}catch(e){rec=new MediaRecorder(st)}
    rec.ondataavailable=function(ev){if(ev.data&&ev.data.size)partes.push(ev.data)};
    rec.onstop=terminar;rec.start(250);inicio=Date.now();
    modoGravando(true,!segurando);
    relogio=setInterval(function(){var x=(Date.now()-inicio)/1000;gTempo.textContent=mmss(x);if(x>=MAXSEG)parar(false)},250);
    return true;
  }).catch(function(){aviso("Para gravar, permita o uso do microfone no navegador. Se preferir, escreva a mensagem.");return false});
}
function parar(cancela){if(!rec||rec.state==="inactive")return;cancelar=!!cancela;try{rec.stop()}catch(e){}}
function terminar(){
  clearInterval(relogio);var dur=(Date.now()-inicio)/1000,mt=(rec&&rec.mimeType)||"audio/webm";
  if(fluxo)fluxo.getTracks().forEach(function(t){t.stop()});rec=null;fluxo=null;modoGravando(false);
  if(cancelar)return;
  if(dur<1){aviso("Áudio muito curto. Segure o microfone enquanto fala.");return}
  var fr=new FileReader();fr.onload=function(){falarAudio(String(fr.result).split(",")[1],mt,dur)};fr.readAsDataURL(new Blob(partes,{type:mt}));
}
function falarAudio(b64,mt,dur){
  if(ocupado)return;
  var rot="🎤 Áudio · "+mmss(dur),bal=balao("pessoa",rot+"\n");
  travar(true);digitando(true);status.textContent="ouvindo o áudio…";
  chamar({acao:"mentor",tipo:TIPO||undefined,email:s.email,token:s.token,mensagens:hist.slice(-30),audio:{b64:b64,mime:mt,dur:Math.round(dur)}})
    .then(function(r){
      digitando(false);travar(false);
      if(!r||!r.ok){bal.remove();aviso(ERRO[(r&&r.erro)||"servico"]||ERRO.servico);return}
      var t=(r.rotulo||rot)+"\n"+r.transcricao;hist.push({papel:"pessoa",texto:t});
      bal.querySelector(".zap__txt").innerHTML=corpoAudio((r.rotulo||rot).split(" · ")[1],r.transcricao);
      hist.push({papel:"mentor",texto:r.resposta});balao("mentor",r.resposta,hhmm(r.hora));
    })
    .catch(function(){digitando(false);travar(false);bal.remove();aviso(ERRO.rede)});
}
if(mic){
  alternar();campo.addEventListener("input",alternar);
  mic.addEventListener("contextmenu",function(ev){ev.preventDefault()});
  mic.addEventListener("pointerdown",function(ev){
    ev.preventDefault();if(ocupado||rec)return;segurando=true;t0=Date.now();
    try{mic.setPointerCapture(ev.pointerId)}catch(e){}
    comecar().then(function(ok){if(ok&&!segurando)travadoUI(true)});
  });
  function soltar(){
    if(!segurando)return;segurando=false;
    if(!rec)return;                       // a permissão ainda estava sendo pedida: a gravação segue até tocar em Enviar
    if(Date.now()-t0<600){travadoUI(true);return}
    parar(false);
  }
  mic.addEventListener("pointerup",soltar);mic.addEventListener("pointercancel",soltar);window.addEventListener("pointerup",soltar);
  gCancelar.addEventListener("click",function(){parar(true)});
  gEnviar.addEventListener("click",function(){parar(false)});
}
if(!s){
  aviso('Para conversar com o mentor, entre com o seu e-mail e o seu código de quatro números. <a class="btn" href="index.html">Entrar no Meu mapa</a>');
  form.hidden=true;chips.hidden=true;return;
}
// Histórico: a conversa continua de onde parou, em qualquer dispositivo.
aviso("Carregando a conversa…");
chamar({acao:"mentor_historico",tipo:TIPO||undefined,email:s.email,token:s.token}).then(function(r){
  lista.innerHTML="";
  if(r&&r.ok&&r.voz){vozAtiva=true;if(mic)alternar()}
  if(r&&r.ok&&r.mensagens&&r.mensagens.length){
    // Limpar conversa: some só da tela; o mentor continua recebendo o histórico como contexto.
    var mk=null,desde=-1;try{mk=localStorage.getItem(CHAVE_LIMPO)}catch(e){}
    if(mk){for(var i=r.mensagens.length-1;i>=0;i--){if(marca(r.mensagens[i])===mk){desde=i;break}}}
    if(desde>=0)aviso(AVISO_LIMPO);
    r.mensagens.forEach(function(m,i){hist.push({papel:m.papel,texto:m.texto});if(i>desde)balao(m.papel,m.texto,hhmm(m.hora));else if(m.papel==="mentor")avisarRede(separar(m.texto).rede)});
  }else if(r&&r.erro==="sessao"){aviso(ERRO.sessao);form.hidden=true;chips.hidden=true}
  else falar("",true);
}).catch(function(){lista.innerHTML="";aviso(ERRO.rede)});
if(limpar)limpar.addEventListener("click",function(){
  if(!hist.length||ocupado)return;
  if(!window.confirm("Limpar a conversa da tela? O mentor continua lembrando do que vocês conversaram."))return;
  try{localStorage.setItem(CHAVE_LIMPO,marca(hist[hist.length-1]))}catch(e){}
  lista.innerHTML="";aviso(AVISO_LIMPO);
});
form.addEventListener("submit",function(ev){ev.preventDefault();var t=campo.value.trim();if(!t||ocupado)return;campo.value="";ajustar();falar(t)});
campo.addEventListener("keydown",function(ev){if(ev.key==="Enter"&&!ev.shiftKey){ev.preventDefault();form.requestSubmit?form.requestSubmit():form.dispatchEvent(new Event("submit"))}});
function ajustar(){campo.style.height="auto";campo.style.height=Math.min(campo.scrollHeight,140)+"px";if(mic)alternar()}
campo.addEventListener("input",ajustar);
$("[data-chip]",chips).forEach(function(b){b.addEventListener("click",function(){falar(b.getAttribute("data-chip"))})});
})();
