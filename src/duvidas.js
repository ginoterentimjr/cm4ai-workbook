(function(){
"use strict";
var C=window.CM4AI||{},API=C.api,ENC=C.encontro||0;
function $(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))}
function sessao(){try{return JSON.parse(localStorage.getItem("cm4ai:sessao")||"null")}catch(e){return null}}
function chamar(d){return fetch(API,{method:"POST",headers:{"Content-Type":"text/plain;charset=utf-8"},body:JSON.stringify(d),redirect:"follow"}).then(function(r){return r.json()})}
function esc(t){return String(t==null?"":t).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\n/g,"<br>")}
var caixas=$("[data-duvida]"),todas=$("[data-duvidas-todas]");
if(!caixas.length&&!todas.length)return;
var s=sessao(),lista=[];

function desenhar(){
  caixas.forEach(function(cx){
    var at=cx.getAttribute("data-duvida"),alvo=cx.querySelector(".duvidas__lista");
    var minhas=lista.filter(function(d){return d.atividade===at&&(!ENC||+d.encontro===ENC)});
    alvo.innerHTML=minhas.map(function(d){
      var r=d.resposta?'<div class="duvida__r"><span>RESPOSTA DE GINO TERENTIM · '+esc(d.respondida)+'</span>'+esc(d.resposta)+'</div>'
                     :'<div class="duvida__e">Aguardando resposta. Ela aparece aqui e chega no seu e-mail.</div>';
      return '<div class="duvida"><div class="duvida__p"><span>A SUA DÚVIDA · '+esc(d.recebida)+'</span>'+esc(d.pergunta)+'</div>'+r+'</div>';
    }).join("");
  });
}
function desenharTodas(){
  todas.forEach(function(el){
    if(!s){el.innerHTML='<p class="duvidas__msg"><a href="index.html">Entre com o seu e-mail</a> para ver as suas dúvidas e as respostas.</p>';return}
    if(!lista.length){el.innerHTML='<p class="duvidas__msg">Você ainda não enviou dúvidas.</p>';return}
    el.innerHTML=lista.slice().reverse().map(function(d){
      var onde=(d.encontro?"ENCONTRO "+d.encontro+" · ":"")+esc(String(d.atividade||"").toUpperCase());
      var r=d.resposta?'<div class="duvida__r"><span>RESPOSTA DE GINO TERENTIM · '+esc(d.respondida)+'</span>'+esc(d.resposta)+'</div>':'<div class="duvida__e">Aguardando resposta.</div>';
      return '<div class="duvida"><div class="duvida__p"><span>'+onde+' · '+esc(d.recebida)+'</span>'+esc(d.pergunta)+'</div>'+r+'</div>';
    }).join("");
  });
}
function carregar(){
  desenharTodas();
  if(!s)return;
  chamar({acao:"duvidas",email:s.email,token:s.token}).then(function(r){if(r&&r.ok){lista=r.duvidas||[];desenhar();desenharTodas()}}).catch(function(){});
}

caixas.forEach(function(cx){
  var bt=cx.querySelector("[data-duvida-abrir]"),fm=cx.querySelector(".duvidas__form"),tx=fm.querySelector("textarea"),
      env=fm.querySelector("[data-duvida-enviar]"),can=fm.querySelector("[data-duvida-cancelar]"),msg=cx.querySelector(".duvidas__msg");
  bt.addEventListener("click",function(){
    if(!s){msg.innerHTML='Para enviar a dúvida, <a href="index.html">entre com o seu e-mail</a>: a resposta volta para a sua página e para o seu e-mail.';return}
    fm.hidden=false;bt.hidden=true;msg.textContent="";tx.focus();
  });
  can.addEventListener("click",function(){fm.hidden=true;bt.hidden=false});
  env.addEventListener("click",function(){
    var p=tx.value.trim();
    if(p.length<3){msg.textContent="Escreva a sua dúvida antes de enviar.";return}
    env.disabled=true;msg.textContent="Enviando…";
    chamar({acao:"duvida",email:s.email,token:s.token,encontro:ENC,atividade:cx.getAttribute("data-duvida"),pergunta:p}).then(function(r){
      env.disabled=false;
      if(r&&r.ok){tx.value="";fm.hidden=true;bt.hidden=false;msg.textContent="Dúvida enviada ao Gino Terentim. A resposta aparece aqui e chega no seu e-mail.";
        lista.push({id:r.id,recebida:r.recebida,encontro:ENC,atividade:cx.getAttribute("data-duvida"),pergunta:p,situacao:"Aguardando",resposta:"",respondida:""});desenhar();desenharTodas()}
      else if(r&&r.erro==="sessao"){msg.innerHTML='A sua sessão terminou. <a href="index.html">Entre de novo</a> e envie a dúvida.'}
      else{msg.textContent="Não foi possível enviar agora. Tente de novo em alguns segundos."}
    }).catch(function(){env.disabled=false;msg.textContent="Sem conexão com o serviço. Confira a internet e tente de novo."});
  });
});
carregar();
setInterval(function(){if(!document.hidden)carregar()},60000);
})();
