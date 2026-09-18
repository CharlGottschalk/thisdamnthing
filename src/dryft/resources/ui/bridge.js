window.dui=Object.freeze({submit:(data,answers={})=>parent.postMessage({dui:1,key,round,action:'submit',data,answers},'*'),action:(action,data,answers={})=>parent.postMessage({dui:1,key,round,action,data,answers},'*')});
document.addEventListener('click',e=>{if(e.target.closest('a'))e.preventDefault()},true);
document.addEventListener('submit',e=>e.preventDefault(),true);
