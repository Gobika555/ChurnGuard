
const risk = p => p >= 70 ? "High" : p >= 40 ? "Medium" : "Low";
const esc2 = v => String(v ?? "").replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
document.addEventListener("DOMContentLoaded", async ()=>{
    const form=document.getElementById("predictionForm"), file=document.getElementById("csvFile");
    const zone=document.getElementById("uploadZone"), name=document.getElementById("fileName");
    const msg=document.getElementById("predictionMessage"), button=document.getElementById("predictButton");
    const section=document.getElementById("predictionResultsSection"), body=document.getElementById("predictionTableBody"), summary=document.getElementById("predictionSummary");
    const userRes=await fetch("/me",{credentials:"include"}); const user=await userRes.json();
    if(!userRes.ok || !user.success){window.location.href="/login.html";return;}
    document.getElementById("sideUsername").textContent=user.user.username; document.getElementById("userAvatar").textContent=(user.user.username[0]||"U").toUpperCase();

    file.addEventListener("change",()=>{name.textContent=file.files[0]?file.files[0].name:"No file selected";});
    ["dragenter","dragover"].forEach(ev=>zone.addEventListener(ev,e=>{e.preventDefault();zone.classList.add("dragover");}));
    ["dragleave","drop"].forEach(ev=>zone.addEventListener(ev,e=>{e.preventDefault();zone.classList.remove("dragover");}));
    zone.addEventListener("drop",e=>{if(e.dataTransfer.files.length){file.files=e.dataTransfer.files;name.textContent=file.files[0].name;}});

    form.addEventListener("submit",async e=>{
        e.preventDefault();
        if(!file.files.length){msg.textContent="Please select a CSV file.";return;}
        const fd=new FormData(); fd.append("file",file.files[0]);
        button.disabled=true; button.textContent="Running model..."; msg.textContent="Validating data and generating predictions...";
        try{
            const res=await fetch("/predict",{method:"POST",body:fd,credentials:"include"}); const data=await res.json();
            if(!res.ok || !data.success) throw new Error(data.message || "Prediction failed");
            const rows=data.predictions||[];
            let high=0,medium=0,low=0;
            body.innerHTML="";
            rows.forEach(p=>{
                const prob=Number(p.Churn_Probability); const r=risk(prob);
                if(r==="High")high++; else if(r==="Medium")medium++; else low++;
                const tr=document.createElement("tr");
                tr.innerHTML=`<td>${esc2(p.customerID)}</td><td>${esc2(p.Predicted_Churn)}</td><td>${prob.toFixed(2)}%</td><td><span class="risk-badge risk-${r.toLowerCase()}">${r}</span></td>`;
                body.appendChild(tr);
            });
            const avg=rows.length?rows.reduce((s,p)=>s+Number(p.Churn_Probability),0)/rows.length:0;
            summary.innerHTML=`<div class="result-box"><span>Total records</span><strong>${rows.length}</strong></div><div class="result-box"><span>High risk</span><strong>${high}</strong></div><div class="result-box"><span>Medium risk</span><strong>${medium}</strong></div><div class="result-box"><span>Average risk</span><strong>${avg.toFixed(1)}%</strong></div>`;
            document.getElementById("resultsSubtitle").textContent=`${rows.length} customer prediction${rows.length===1?"":"s"} generated and saved.`;
            section.style.display="block"; msg.textContent="Prediction completed successfully."; section.scrollIntoView({behavior:"smooth"});
        }catch(err){console.error(err);msg.textContent=err.message;}
        finally{button.disabled=false;button.textContent="Run churn prediction";}
    });
});
