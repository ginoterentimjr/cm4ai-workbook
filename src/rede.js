(function(){
"use strict";
// Painel da rede de campeões: desenha a rede enviada pelo Mentor da rede e calcula grau e intermediação (Wasserman e Faust, cap. 5).
var painel=document.querySelector("[data-rede-painel]");if(!painel)return;
var svg=painel.querySelector("[data-rede-svg]"),vazio=painel.querySelector("[data-rede-vazio]"),info=painel.querySelector("[data-rede-info]"),baixar=painel.querySelector("[data-rede-baixar]");
var dica=painel.querySelector("[data-rede-dica]"),cartao=painel.querySelector("[data-rede-pessoa]"),est=null,hist=[],assin="",rodando=null;
var COR={"Inovadores":"#7A4E6D","Adotantes iniciais":"#35608F","Maioria inicial":"#2F6B6F","Maioria tardia":"#B5781E","Últimos adotantes":"#8D8377","Agente de mudança":"#E5662C"};
var W=700,H=540,NS="http://www.w3.org/2000/svg";
function esc(t){return String(t==null?"":t).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;")}
function el(n,a,p){var e=document.createElementNS(NS,n);for(var k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e}
function limpa(d){
  var nos=[],idx={},lacos=[],vistos={};
  (d&&d.nos||[]).forEach(function(n){var id=String(n.id||"").trim();if(!id||idx[id]!=null)return;idx[id]=nos.length;nos.push({id:id,rotulo:String(n.rotulo||id).slice(0,40),categoria:COR[n.categoria]?n.categoria:"Maioria inicial",grupo:String(n.grupo||""),postura:String(n.postura||""),campeao:String(n.campeao||""),papel:String(n.papel||"")})});
  (d&&d.lacos||[]).forEach(function(l){var a=idx[String(l[0])],b=idx[String(l[1])];if(a==null||b==null||a===b)return;var k=Math.min(a,b)+"-"+Math.max(a,b);if(vistos[k])return;vistos[k]=1;lacos.push([a,b])});
  return {nos:nos,lacos:lacos};
}
// Intermediação (algoritmo de Brandes), rede sem direção e sem pesos.
function medidas(r){
  var n=r.nos.length,adj=[],i;for(i=0;i<n;i++)adj.push([]);
  r.lacos.forEach(function(l){adj[l[0]].push(l[1]);adj[l[1]].push(l[0])});
  var grau=adj.map(function(a){return a.length}),cb=new Array(n).fill(0);
  for(var s=0;s<n;s++){
    var S=[],P=[],sig=new Array(n).fill(0),dist=new Array(n).fill(-1),Q=[s];for(i=0;i<n;i++)P.push([]);sig[s]=1;dist[s]=0;
    while(Q.length){var v=Q.shift();S.push(v);adj[v].forEach(function(w){if(dist[w]<0){dist[w]=dist[v]+1;Q.push(w)}if(dist[w]===dist[v]+1){sig[w]+=sig[v];P[w].push(v)}})}
    var del=new Array(n).fill(0);
    while(S.length){var w=S.pop();P[w].forEach(function(v){del[v]+=sig[v]/sig[w]*(1+del[w])});if(w!==s)cb[w]+=del[w]}
  }
  cb=cb.map(function(x){return x/2});
  return {grau:grau,inter:cb,adj:adj};
}
// Posições: forças de atração e repulsão (Fruchterman e Reingold), com semente fixa para o desenho não mudar a cada abertura.
function posicoes(r){
  var n=r.nos.length,p=[],seed=7;function rnd(){seed=(seed*16807)%2147483647;return seed/2147483647}
  var grupos={},gi=0;r.nos.forEach(function(x){if(!(x.grupo in grupos))grupos[x.grupo]=gi++});
  for(var i=0;i<n;i++){var ang=2*Math.PI*(grupos[r.nos[i].grupo]/Math.max(1,gi))+rnd()*0.8;p.push({x:W/2+Math.cos(ang)*200+rnd()*40,y:H/2+Math.sin(ang)*150+rnd()*40})}
  var k=Math.sqrt((W-160)*(H-160)/Math.max(1,n))*1.25,t=60;
  for(var it=0;it<400;it++){
    var d=p.map(function(){return {x:0,y:0}});
    for(i=0;i<n;i++)for(var j=i+1;j<n;j++){var dx=p[i].x-p[j].x,dy=p[i].y-p[j].y,dd=Math.max(1,Math.sqrt(dx*dx+dy*dy)),f=k*k/dd;
      if(r.nos[i].grupo&&r.nos[i].grupo===r.nos[j].grupo)f*=0.7;
      d[i].x+=dx/dd*f;d[i].y+=dy/dd*f;d[j].x-=dx/dd*f;d[j].y-=dy/dd*f}
    r.lacos.forEach(function(l){var a=l[0],b=l[1],dx=p[a].x-p[b].x,dy=p[a].y-p[b].y,dd=Math.max(1,Math.sqrt(dx*dx+dy*dy)),f=dd*dd/k;
      d[a].x-=dx/dd*f;d[a].y-=dy/dd*f;d[b].x+=dx/dd*f;d[b].y+=dy/dd*f});
    for(i=0;i<n;i++){var dl=Math.max(1,Math.sqrt(d[i].x*d[i].x+d[i].y*d[i].y));p[i].x+=d[i].x/dl*Math.min(dl,t);p[i].y+=d[i].y/dl*Math.min(dl,t);
      p[i].x+=(W/2-p[i].x)*0.01;p[i].y+=(H/2-p[i].y)*0.01;p[i].x=Math.max(90,Math.min(W-90,p[i].x));p[i].y=Math.max(60,Math.min(H-70,p[i].y))}
    t=Math.max(2,t*0.985);
  }
  // Ajuste ao quadro: a rede ocupa o espaço disponível.
  var xs=p.map(function(q){return q.x}),ys=p.map(function(q){return q.y}),x0=Math.min.apply(null,xs),x1=Math.max.apply(null,xs),y0=Math.min.apply(null,ys),y1=Math.max.apply(null,ys);
  p.forEach(function(q){q.x=95+(x1>x0?(q.x-x0)/(x1-x0):0.5)*(W-190);q.y=55+(y1>y0?(q.y-y0)/(y1-y0):0.5)*(H-135)});
  return p;
}
function quebra(t,max){var ws=String(t).split(" "),ls=[""];ws.forEach(function(w){var l=ls[ls.length-1];if((l+" "+w).trim().length>max&&l)ls.push(w);else ls[ls.length-1]=(l+" "+w).trim()});return ls.slice(0,3)}
var atual=null;
function desenhar(d){
  var r=limpa(d);if(r.nos.length<2)return;atual=r;
  var m=medidas(r),p=posicoes(r),maxG=Math.max.apply(null,m.grau.concat([1])),maxB=Math.max.apply(null,m.inter.concat([0]));
  vazio.hidden=true;svg.style.display="block";svg.innerHTML="";svg.setAttribute("viewBox","0 0 "+W+" "+H);
  el("rect",{x:0,y:0,width:W,height:H,fill:"#FFFDF9"},svg);
  var gl=el("g",{},svg),gn=el("g",{},svg),gs=[],raios=[];
  r.lacos.forEach(function(l){el("line",{x1:p[l[0]].x,y1:p[l[0]].y,x2:p[l[1]].x,y2:p[l[1]].y,stroke:"#CFC4B6","stroke-width":2.2},gl)});
  var pontes=m.inter.map(function(v,i){return [v,i]}).filter(function(x){return x[0]>0&&r.nos[x[1]].id!=="voce"}).sort(function(a,b){return b[0]-a[0]}).slice(0,2).map(function(x){return x[1]});
  r.nos.forEach(function(no,i){
    var raio=16+16*(m.grau[i]/maxG),g=el("g",{"data-no":i,tabindex:0,role:"button","aria-label":no.rotulo+", "+no.categoria+", "+m.grau[i]+" laços"},gn),cor=COR[no.categoria];gs.push(g);raios.push(raio);
    if(no.campeao)el("circle",{cx:p[i].x,cy:p[i].y,r:raio+8,fill:"none",stroke:"#C9A24D","stroke-width":4},g);
    if(pontes.indexOf(i)>=0)el("circle",{cx:p[i].x,cy:p[i].y,r:raio+(no.campeao?14:6),fill:"none",stroke:"#2A211C","stroke-width":1.6,"stroke-dasharray":"4 3"},g);
    el("circle",{cx:p[i].x,cy:p[i].y,r:raio,fill:cor,stroke:no.postura==="Resiste"?"#B04A1C":"#FFFFFF","stroke-width":no.postura==="Resiste"?3.5:2},g);
    var tn=el("text",{x:p[i].x,y:p[i].y+5,"text-anchor":"middle","font-size":15,"font-weight":700,fill:"#FFFFFF","font-family":"Poppins, sans-serif"},g);tn.textContent=m.grau[i];
    if(no.campeao){var st=el("text",{x:p[i].x+raio+4,y:p[i].y-raio-2,"font-size":22,"font-family":"sans-serif"},g);st.textContent="★";st.setAttribute("fill","#C9A24D")}
    var off=raio+(no.campeao?10:0)+(pontes.indexOf(i)>=0?(no.campeao?8:6):0)+18;
    quebra(no.rotulo,18).forEach(function(l,k){var t=el("text",{x:p[i].x,y:p[i].y+off+k*16,"text-anchor":"middle","font-size":15,"font-weight":no.id==="voce"?700:500,fill:"#2A211C","font-family":"Poppins, sans-serif",stroke:"#FFFDF9","stroke-width":3,"paint-order":"stroke"},g);t.textContent=l});
  });
  // Leitura da rede
  var ord=r.nos.map(function(x,i){return i}).filter(function(i){return r.nos[i].id!=="voce"});
  var proc=ord.slice().sort(function(a,b){return m.grau[b]-m.grau[a]}).slice(0,3),peri=ord.filter(function(i){return m.grau[i]<=1});
  var camp=r.nos.filter(function(x){return x.campeao});
  function nomes(l){return l.length?l.map(function(i){return esc(r.nos[i].rotulo)+" ("+m.grau[i]+")"}).join(", "):"ninguém por enquanto"}
  info.innerHTML='<div class="rede__ler"><p><b>Mais procurados</b> (número de laços): '+nomes(proc)+'</p>'+
    '<p><b>Pontes</b> (ligam pessoas que, sem elas, não se alcançam): '+(pontes.length?pontes.map(function(i){return esc(r.nos[i].rotulo)}).join(", "):"nenhuma ainda")+'</p>'+
    '<p><b>Na periferia</b> (um laço ou nenhum): '+(peri.length?peri.map(function(i){return esc(r.nos[i].rotulo)}).join(", "):"ninguém")+'</p></div>'+
    (camp.length?'<div class="rede__camp"><h4>Os campeões</h4><ul>'+camp.map(function(c){return '<li><b>★ '+esc(c.rotulo)+'</b> · '+esc(c.campeao)+(c.papel?'<br><span>'+esc(c.papel)+'</span>':'')+'</li>'}).join("")+'</ul></div>':'');
  var bp=painel.querySelector("[data-rede-baixar-p]");if(bp)bp.style.display="";
  var sel=el("g",{},svg);
  est={r:r,m:m,p:p,gs:gs,raios:raios,sel:sel};
  var a2=JSON.stringify([r.nos.map(function(x){return x.id+x.categoria+x.postura}),r.lacos]);if(a2!==assin){assin=a2;hist=[]}
  if(rodando){clearTimeout(rodando);rodando=null}
  cartao.hidden=true;cartao.innerHTML="";if(dica)dica.hidden=false;
  gs.forEach(function(g,i){g.addEventListener("click",function(){abrir(i)});g.addEventListener("keydown",function(ev){if(ev.key==="Enter"||ev.key===" "){ev.preventDefault();abrir(i)}})});
  curva(r);
}
// A curva de Rogers da legenda: quantas pessoas da rede estão em cada categoria.
function curva(r){
  var c={};r.nos.forEach(function(x){if(x.categoria!=="Agente de mudança")c[x.categoria]=(c[x.categoria]||0)+1});
  Array.prototype.forEach.call(painel.querySelectorAll("[data-curva-n]"),function(g){var n=c[g.getAttribute("data-curva-n")]||0;g.style.display=n?"":"none";g.querySelector("text").textContent=n});
  var t=painel.querySelector("[data-curva-txt]");if(t)t.textContent="Os números sobre a curva mostram quantas pessoas da sua rede estão em cada categoria.";
}
function iVoce(r){for(var i=0;i<r.nos.length;i++)if(r.nos[i].id==="voce"||r.nos[i].categoria==="Agente de mudança")return i;return -1}
function marcar(i){
  var s=est.sel;s.innerHTML="";if(i==null)return;
  el("circle",{cx:est.p[i].x,cy:est.p[i].y,r:est.raios[i]+22,fill:"none",stroke:"#E5662C","stroke-width":3,"stroke-dasharray":"6 4"},s);
}
function opac(f){est.gs.forEach(function(g,i){g.style.opacity=f?f(i):"";g.style.transition="opacity .35s"})}
// O cartão da pessoa
function abrir(i){
  if(!est)return;if(rodando){clearTimeout(rodando);rodando=null}
  var r=est.r,m=est.m,no=r.nos[i],eu=iVoce(r);opac(null);marcar(i);
  var meta=[no.categoria];if(no.postura)meta.push(no.postura);meta.push(m.grau[i]+(m.grau[i]===1?" laço":" laços"));
  if(no.campeao)meta.push("campeão: "+no.campeao);
  cartao.style.setProperty("--tom",COR[no.categoria]);
  var h='<h4>'+esc(no.rotulo)+'</h4><p class="rede__meta">'+esc(meta.join(" · "))+'</p>'+(no.papel?'<p class="rede__meta"><b>Papel:</b> '+esc(no.papel)+'</p>':'');
  if(i===eu)h+='<p class="rede__meta">Você é o agente de mudança. Clique noutra pessoa para testar quem leva a prática mais longe.</p>';
  h+='<div class="rede__acoes">'+(i===eu?'':'<button type="button" class="prim" data-acao="sim">E se esta pessoa for a campeã?</button><button type="button" data-acao="exp">Proponha um experimento com esta pessoa</button>')+'<button type="button" class="sec" data-acao="fechar">Fechar</button></div><div class="rede__sim" data-sim></div>';
  cartao.innerHTML=h;cartao.hidden=false;
  var bs=cartao.querySelector('[data-acao="sim"]'),be=cartao.querySelector('[data-acao="exp"]');
  if(bs)bs.addEventListener("click",function(){simular(i)});
  if(be)be.addEventListener("click",function(){pedir("Proponha um experimento pequeno com “"+no.rotulo+"” entre os campeões, no formato do Encontro 4: a hipótese, a medida e o critério de revisão, ligado ao meu experimento.")});
  cartao.querySelector('[data-acao="fechar"]').addEventListener("click",function(){if(rodando){clearTimeout(rodando);rodando=null}opac(null);marcar(null);cartao.hidden=true});
  if(hist.length)mostrarHist();
}
// Difusão por limiar: cada pessoa adota quando a parcela dos seus contatos que já adotou alcança o limiar da sua categoria
// (Granovetter, 1978; Valente, 1996, que relaciona os limiares às categorias de Rogers). Modelo simplificado, apenas ilustrativo.
var LIM={"Inovadores":0,"Adotantes iniciais":0.25,"Maioria inicial":0.4,"Maioria tardia":0.6,"Últimos adotantes":0.8,"Agente de mudança":0};
function simular(ini){
  var r=est.r,m=est.m,n=r.nos.length,eu=iVoce(r),ad=new Array(n).fill(0),rod=[],i;
  ad[ini]=1;
  for(var k=1;k<=8;k++){
    var novos=[];
    for(i=0;i<n;i++){if(ad[i]||i===eu)continue;var viz=m.adj[i].filter(function(j){return j!==eu}),g=viz.length,lim=Math.min(1,(LIM[r.nos[i].categoria]||0.4)+(r.nos[i].postura==="Resiste"?0.1:0));
      var f=g?viz.filter(function(j){return ad[j]}).length/g:0;if(lim===0||(g&&f>=lim-1e-9))novos.push(i)}
    if(!novos.length)break;novos.forEach(function(j){ad[j]=k+1});rod.push(novos);
  }
  var tot=r.nos.filter(function(x,j){return j!==eu}).length,adot=ad.filter(function(v,j){return v&&j!==eu}).length;
  var fora=r.nos.map(function(x,j){return j}).filter(function(j){return !ad[j]&&j!==eu});
  var box=cartao.querySelector("[data-sim]"),nome=r.nos[ini].rotulo;
  cartao.querySelectorAll(".rede__acoes button").forEach(function(b){b.disabled=true});
  opac(function(j){return (j===ini||j===eu)?1:0.18});
  box.innerHTML='<p><b>Rodada 0:</b> '+esc(nome)+' começa a usar e a mostrar como usa.</p>';
  var k2=0;
  function passo(){
    if(k2<rod.length){var l=rod[k2];k2++;opac(function(j){return j===eu||(ad[j]&&ad[j]<=k2+1)?1:0.18});
      box.insertAdjacentHTML("beforeend",'<p><b>Rodada '+k2+':</b> '+l.map(function(j){return esc(r.nos[j].rotulo)}).join(", ")+'.</p>');rodando=setTimeout(passo,900);return}
    rodando=null;
    hist=hist.filter(function(h){return h.nome!==nome});hist.push({nome:nome,n:adot,t:tot,r:rod.length});
    box.insertAdjacentHTML("beforeend",'<p><b>Partindo de '+esc(nome)+': '+(rod.length?adot+' de '+tot+' pessoas adotam em '+rod.length+(rod.length===1?' rodada':' rodadas'):'a prática não sai desta pessoa')+'.</b>'+
      (fora.length?' Ficam de fora: '+fora.map(function(j){return esc(r.nos[j].rotulo)}).join(", ")+'.':' Ninguém fica de fora.')+'</p><div data-hist></div>'+
      '<p class="rede__nota">Modelo simplificado, apenas ilustrativo: cada pessoa adota quando a parcela dos seus contatos que já adotou alcança o limiar da sua categoria (inovadores, por conta própria; adotantes iniciais, 1 em 4; maioria inicial, 2 em 5; maioria tardia, 3 em 5; últimos adotantes, 4 em 5; quem resiste, um pouco mais). Você, agente de mudança, fica fora da conta, para comparar só os campeões. Base: Granovetter (1978) e Valente (1996). A rede real é uma hipótese a conferir nas semanas do experimento.</p>');
    mostrarHist();
    cartao.querySelectorAll(".rede__acoes button").forEach(function(b){b.disabled=false});
    var bs=cartao.querySelector('[data-acao="sim"]');if(bs)bs.textContent="Ver de novo";
  }
  rodando=setTimeout(passo,900);
}
function mostrarHist(){
  var d=cartao.querySelector("[data-hist]");if(!d){var bx=cartao.querySelector("[data-sim]");if(!bx)return;d=document.createElement("div");d.setAttribute("data-hist","");bx.appendChild(d)}
  if(hist.length<1){d.innerHTML="";return}
  var o=hist.slice().sort(function(a,b){return b.n-a.n||a.r-b.r});
  d.innerHTML='<p><b>Comparação</b>'+(hist.length<2?' (clique noutra pessoa para comparar)':'')+':</p><ul class="rede__hist">'+o.map(function(h){return '<li>'+esc(h.nome)+': '+(h.r?h.n+' de '+h.t+' em '+h.r+(h.r===1?' rodada':' rodadas'):'não se espalha')+'</li>'}).join("")+'</ul>';
}
// Pedido ao Mentor pela conversa ao lado
function pedir(t){
  var raiz=document.querySelector('[data-mentor-tipo="rede"]');if(!raiz)return;var f=raiz.querySelector("[data-mentor-form]"),c=f&&f.querySelector("textarea");if(!c)return;
  c.value=t;c.dispatchEvent(new Event("input"));if(f.requestSubmit)f.requestSubmit();else f.dispatchEvent(new Event("submit",{cancelable:true}));
  try{raiz.scrollIntoView({behavior:"smooth",block:"start"})}catch(e){}
}
window.addEventListener("cm4ai:rede",function(ev){try{desenhar(ev.detail)}catch(e){}});
baixar.addEventListener("click",function(){
  if(!atual)return;var x=new XMLSerializer().serializeToString(svg),img=new Image(),c=document.createElement("canvas");c.width=W*2;c.height=H*2;
  img.onload=function(){var g=c.getContext("2d");g.fillStyle="#FFFDF9";g.fillRect(0,0,c.width,c.height);g.drawImage(img,0,0,c.width,c.height);
    var a=document.createElement("a");a.download="rede-de-campeoes.png";a.href=c.toDataURL("image/png");document.body.appendChild(a);a.click();a.remove()};
  img.src="data:image/svg+xml;charset=utf-8,"+encodeURIComponent(x.indexOf("xmlns")<0?x.replace("<svg",'<svg xmlns="'+NS+'"'):x);
});
})();
