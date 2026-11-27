(function(){
"use strict";
// Painel da rede de campeões: desenha a rede enviada pelo Mentor da rede e calcula grau e intermediação (Wasserman e Faust, cap. 5).
var painel=document.querySelector("[data-rede-painel]");if(!painel)return;
var svg=painel.querySelector("[data-rede-svg]"),vazio=painel.querySelector("[data-rede-vazio]"),info=painel.querySelector("[data-rede-info]"),baixar=painel.querySelector("[data-rede-baixar]");
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
  var k=Math.sqrt((W-160)*(H-160)/Math.max(1,n))*0.9,t=60;
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
  vazio.hidden=true;svg.innerHTML="";svg.setAttribute("viewBox","0 0 "+W+" "+H);
  el("rect",{x:0,y:0,width:W,height:H,fill:"#FFFDF9"},svg);
  var gl=el("g",{},svg),gn=el("g",{},svg);
  r.lacos.forEach(function(l){el("line",{x1:p[l[0]].x,y1:p[l[0]].y,x2:p[l[1]].x,y2:p[l[1]].y,stroke:"#CFC4B6","stroke-width":2.2},gl)});
  var pontes=m.inter.map(function(v,i){return [v,i]}).filter(function(x){return x[0]>0&&r.nos[x[1]].id!=="voce"}).sort(function(a,b){return b[0]-a[0]}).slice(0,2).map(function(x){return x[1]});
  r.nos.forEach(function(no,i){
    var raio=16+16*(m.grau[i]/maxG),g=el("g",{},gn),cor=COR[no.categoria];
    if(no.campeao)el("circle",{cx:p[i].x,cy:p[i].y,r:raio+8,fill:"none",stroke:"#C9A24D","stroke-width":4},g);
    if(pontes.indexOf(i)>=0)el("circle",{cx:p[i].x,cy:p[i].y,r:raio+(no.campeao?14:6),fill:"none",stroke:"#2A211C","stroke-width":1.6,"stroke-dasharray":"4 3"},g);
    el("circle",{cx:p[i].x,cy:p[i].y,r:raio,fill:cor,stroke:no.postura==="Resiste"?"#B04A1C":"#FFFFFF","stroke-width":no.postura==="Resiste"?3.5:2},g);
    var tn=el("text",{x:p[i].x,y:p[i].y+5,"text-anchor":"middle","font-size":15,"font-weight":700,fill:"#FFFFFF","font-family":"Poppins, sans-serif"},g);tn.textContent=m.grau[i];
    if(no.campeao){var st=el("text",{x:p[i].x+raio+4,y:p[i].y-raio-2,"font-size":22,"font-family":"sans-serif"},g);st.textContent="★";st.setAttribute("fill","#C9A24D")}
    quebra(no.rotulo,18).forEach(function(l,k){var t=el("text",{x:p[i].x,y:p[i].y+raio+18+k*16,"text-anchor":"middle","font-size":15,"font-weight":no.id==="voce"?700:500,fill:"#2A211C","font-family":"Poppins, sans-serif",stroke:"#FFFDF9","stroke-width":3,"paint-order":"stroke"},g);t.textContent=l});
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
  baixar.hidden=false;
}
window.addEventListener("cm4ai:rede",function(ev){try{desenhar(ev.detail)}catch(e){}});
baixar.addEventListener("click",function(){
  if(!atual)return;var x=new XMLSerializer().serializeToString(svg),img=new Image(),c=document.createElement("canvas");c.width=W*2;c.height=H*2;
  img.onload=function(){var g=c.getContext("2d");g.fillStyle="#FFFDF9";g.fillRect(0,0,c.width,c.height);g.drawImage(img,0,0,c.width,c.height);
    var a=document.createElement("a");a.download="rede-de-campeoes.png";a.href=c.toDataURL("image/png");document.body.appendChild(a);a.click();a.remove()};
  img.src="data:image/svg+xml;charset=utf-8,"+encodeURIComponent(x.indexOf("xmlns")<0?x.replace("<svg",'<svg xmlns="'+NS+'"'):x);
});
})();
