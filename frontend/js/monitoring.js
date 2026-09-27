
document.addEventListener("DOMContentLoaded",async()=>{
    const msg=document.getElementById("monitorMessage");
    try{
        const u=await fetch("/me",{credentials:"include"}),ud=await u.json();if(!u.ok||!ud.success){location.href="/login.html";return;}
        const res=await fetch("/predictions",{credentials:"include"}),data=await res.json();if(!res.ok||!data.success)throw new Error(data.message||"Unable to load monitoring data");
        const rows=data.predictions||[],total=rows.length;let high=0,medium=0,low=0;
        rows.forEach(p=>{const n=Number(p.probability);if(n>=70)high++;else if(n>=40)medium++;else low++;});
        [["monitorHigh", "monitorHighBar", high],["monitorMedium","monitorMediumBar",medium],["monitorLow","monitorLowBar",low]].forEach(([id,bar,n])=>{document.getElementById(id).textContent=n;document.getElementById(bar).style.width=(total?n/total*100:0)+"%";});
        msg.textContent=total?`Live distribution calculated from ${total} saved predictions.`:"No live prediction data available yet.";
    }catch(err){console.error(err);msg.textContent=err.message;}
});
