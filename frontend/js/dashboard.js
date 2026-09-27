
const riskLevel = p => p >= 70 ? "High" : p >= 40 ? "Medium" : "Low";
const esc = v => String(v ?? "").replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
async function getCurrentData(){
    const userRes = await fetch("/me",{credentials:"include"});
    const user = await userRes.json();
    if(!userRes.ok || !user.success){ window.location.href="/login.html"; return null; }
    const predRes = await fetch("/predictions",{credentials:"include"});
    const data = await predRes.json();
    if(!predRes.ok || !data.success) throw new Error(data.message || "Unable to load predictions");
    return {user:user.user,predictions:data.predictions || []};
}
document.addEventListener("DOMContentLoaded", async ()=>{
    try{
        const data = await getCurrentData(); if(!data) return;
        const {user,predictions} = data;
        document.getElementById("username").textContent=user.username;
        document.getElementById("sideUsername").textContent=user.username;
        document.getElementById("userAvatar").textContent=(user.username[0]||"U").toUpperCase();

        const total=predictions.length;
        const high=predictions.filter(p=>Number(p.probability)>=70).length;
        const medium=predictions.filter(p=>Number(p.probability)>=40 && Number(p.probability)<70).length;
        const low=total-high-medium;
        const avg=total ? predictions.reduce((s,p)=>s+Number(p.probability||0),0)/total : 0;
        document.getElementById("totalPredictions").textContent=total;
        document.getElementById("highRisk").textContent=high;
        document.getElementById("mediumRisk").textContent=medium;
        document.getElementById("averageRisk").textContent=avg.toFixed(1)+"%";
        document.getElementById("highCount").textContent=high;
        document.getElementById("mediumCount").textContent=medium;
        document.getElementById("lowCount").textContent=low;
        document.getElementById("highProgress").style.width=total?`${high/total*100}%`:"0%";
        document.getElementById("mediumProgress").style.width=total?`${medium/total*100}%`:"0%";
        document.getElementById("lowProgress").style.width=total?`${low/total*100}%`:"0%";

        const recent=document.getElementById("recentPredictions");
        recent.innerHTML="";
        predictions.slice(0,5).forEach(p=>{
            const risk=riskLevel(Number(p.probability));
            const row=document.createElement("div"); row.className="monitor-item";
            row.innerHTML=`<span><strong>${esc(p.customerID)}</strong><br><span class="muted">${esc(p.created_at||"")}</span></span><strong><span class="risk-badge risk-${risk.toLowerCase()}">${risk}</span> ${Number(p.probability).toFixed(1)}%</strong>`;
            recent.appendChild(row);
        });
        if(!predictions.length) recent.innerHTML='<div class="empty-state"><div class="empty-icon">◌</div><h3>No predictions yet</h3><p>Upload a CSV to start your customer risk analysis.</p></div>';
        document.getElementById("dashboardMessage").textContent=total?`${total} saved prediction${total===1?"":"s"} available.`:"No predictions yet. Start with a CSV prediction.";
    }catch(err){
        console.error(err);
        document.getElementById("dashboardMessage").textContent="Unable to load dashboard data.";
    }
});
