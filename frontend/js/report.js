
const rLevel=p=>p>=70?"High":p>=40?"Medium":"Low";
document.addEventListener("DOMContentLoaded",async()=>{
    const msg=document.getElementById("reportMessage");
    try{
        const u=await fetch("/me",{credentials:"include"}),ud=await u.json();if(!u.ok||!ud.success){location.href="/login.html";return;}
        const res=await fetch("/predictions",{credentials:"include"}),data=await res.json();if(!res.ok||!data.success)throw new Error(data.message||"Unable to load report");
        const rows=data.predictions||[],total=rows.length;let high=0,medium=0,low=0;
        rows.forEach(p=>{const r=rLevel(Number(p.probability));if(r==="High")high++;else if(r==="Medium")medium++;else low++;});
        const avg=total?rows.reduce((s,p)=>s+Number(p.probability||0),0)/total:0;
        document.getElementById("reportTotal").textContent=total;document.getElementById("reportHigh").textContent=high;document.getElementById("reportMedium").textContent=medium;document.getElementById("reportAverage").textContent=avg.toFixed(1)+"%";
        [[high,"reportHighBar","reportHighPct"],[medium,"reportMediumBar","reportMediumPct"],[low,"reportLowBar","reportLowPct"]].forEach(([n,b,p])=>{const pct=total?n/total*100:0;document.getElementById(b).style.width=pct+"%";document.getElementById(p).textContent=pct.toFixed(1)+"%";});
        document.getElementById("reportInsight").innerHTML=total?`<strong>${high} high-risk customer${high===1?"":"s"}</strong><p class="muted">The current history contains ${medium} medium-risk and ${low} low-risk predictions. Average churn probability is ${avg.toFixed(1)}%.</p>`:"<strong>No prediction data yet.</strong><p class='muted'>Run a prediction first, then return here for a report generated from your saved history.</p>";
        msg.textContent="Report generated from live prediction history.";
        document.getElementById("printReport").addEventListener("click",()=>window.print());
    }catch(err){console.error(err);msg.textContent=err.message;}
});
