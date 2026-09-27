
const hRisk=p=>p>=70?"High":p>=40?"Medium":"Low";
const hEsc=v=>String(v??"").replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
document.addEventListener("DOMContentLoaded",async()=>{
    const msg=document.getElementById("historyMessage"), body=document.getElementById("historyTableBody"), empty=document.getElementById("historyEmpty");
    try{
        const u=await fetch("/me",{credentials:"include"}), ud=await u.json(); if(!u.ok||!ud.success){location.href="/login.html";return;}
        document.getElementById("sideUsername").textContent=ud.user.username; document.getElementById("userAvatar").textContent=(ud.user.username[0]||"U").toUpperCase();
        const res=await fetch("/predictions",{credentials:"include"}), data=await res.json(); if(!res.ok||!data.success)throw new Error(data.message||"Unable to load history");
        const rows=data.predictions||[]; let high=0,medium=0,low=0; body.innerHTML="";
        rows.forEach(p=>{
            const prob=Number(p.probability), r=hRisk(prob); if(r==="High")high++;else if(r==="Medium")medium++;else low++;
            const tr=document.createElement("tr"); const date=p.created_at?new Date(p.created_at).toLocaleString():"-";
            tr.innerHTML=`<td>${hEsc(p.customerID)}</td><td>${hEsc(p.prediction)}</td><td>${prob.toFixed(2)}%</td><td><span class="risk-badge risk-${r.toLowerCase()}">${r}</span></td><td>${hEsc(date)}</td>`; body.appendChild(tr);
        });
        document.getElementById("historyTotal").textContent=rows.length; document.getElementById("historyHigh").textContent=high; document.getElementById("historyMedium").textContent=medium; document.getElementById("historyLow").textContent=low;
        if(!rows.length){empty.style.display="block";msg.textContent="No predictions found for this account.";} else msg.textContent=`${rows.length} prediction${rows.length===1?"":"s"} found.`;
    }catch(err){console.error(err);msg.textContent=err.message;}
});
