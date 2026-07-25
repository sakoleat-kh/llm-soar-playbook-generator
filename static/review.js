const alertId = new URLSearchParams(window.location.search).get("id");

console.log("Alert ID =", alertId);

if (alertId) {
    console.log("Calling loadExistingPlaybook()");
    loadExistingPlaybook(alertId);
} else {
    console.log("No alert ID found in URL");
}


async function loadExistingPlaybook(alertId) {

    console.log("loadExistingPlaybook started");
    
    document.getElementById("status").innerHTML =
    "Loading playbook...";

    const alertResponse = 
        await fetch(`/alerts/${alertId}`);

    console.log("Alert response:", alertResponse.status);

    if (!alertResponse.ok) {
        document.getElementById("status").innerHTML = 
            "Alert not found.";
        return;
    }

    const alertData =
        await alertResponse.json();
    
    const playbookResponse = 
        await fetch(`/playbooks/${alertId}`);

    console.log("Playbook response:", playbookResponse.status);

    if (!playbookResponse.ok) {
        document.getElementById("status").innerHTML =
            "Playbook not found.";
        return
    }

    const playbook = 
        await playbookResponse.json();
    
        displayPlaybook(alertData, playbook, alertId);

}

function displayPlaybook(alertData, playbook, alertId){

    const workflow = 
        JSON.parse(playbook.playbook_json);

    const sigmaRules = 
        workflow.sigma_rules || [];
    
    const actions = 
        workflow.actions || [];
    
    let stepsHtml = "<ol>";

    actions.forEach(action => {
        stepsHtml += `
        <li>
            <strong>${action.label}</strong><br>
            ${action.description || ""}
        </li>
        `;
    });

    stepsHtml += "</ol>";

    let sigmaHtml = "<h3>Sigma Rules</h3>";

    sigmaRules.forEach(rule => {
        sigmaHtml += `
        <p>
            <a href="${rule.raw_url}" target="_blank">
                ${rule.title}
            </a>
        </p>
        `;
    });

    document.getElementById("result").innerHTML = `
    <h2>${alertData.technique_name}</h2>

    <p><b>Technique:</b>
    ${alertData.technique_id}</p>

    <p><b>Confidence:</b>
    ${alertData.confidence}</p>

    ${stepsHtml}

    ${sigmaHtml}

    <br>

    <button id="approveBtn">
        Approve
    </button>

    <button id="rejectBtn">
        Reject
    </button>

    <div id="actionStatus"></div>
    
    `;

    document.getElementById("approveBtn").addEventListener("click", async () => {

    const response = await fetch(
        `/playbooks/${alertId}/approve`,
        {
            method: "POST"
        }
    );

    if (!response.ok) {

        document.getElementById("actionStatus").innerHTML =
        `<p style="color:red">Approve failed.</p>`;

        return;
    }

    const result = await response.json();

    document.getElementById("actionStatus").innerHTML =
    `<p style="color:green">${result.message}</p>`;

});


document.getElementById("rejectBtn").addEventListener("click", async () => {

    const reason = prompt("Enter rejection reason (optional):");

    const response = await fetch(
        `/playbooks/${alertId}/reject`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                reason
            })
        }
    );

    if (!response.ok) {

        document.getElementById("actionStatus").innerHTML =
        `<p style="color:red">Reject failed.</p>`;

        return;
    }

    const result = await response.json();

    document.getElementById("actionStatus").innerHTML =
    `<p style="color:green">${result.message}</p>`;

});
    }

const submitBtn = document.getElementById("submitBtn");

submitBtn.onclick = async () => {

    const text = document.getElementById("alertText").value.trim();

    if (!text) {
        alert("Please paste an alert.");
        return;
    }

    document.getElementById("status").innerHTML = "Submitting alert...";

    const response = await fetch("/webhook/alert", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            sender: "analyst@example.com",
            subject: "Manual Alert Review",
            body_text: text,
            severity: 5,
            source_system: "Review Page"
        })
    });

    if (!response.ok) {
        document.getElementById("status").innerHTML = "Submission failed!";
        console.error(await response.text());
        return;
    }

    const data = await response.json();

    console.log(data);

    document.getElementById("status").innerHTML =
        `Alert submitted! ID: ${data.alert_id}`;

    window.alertId = data.alert_id;

    const interval = setInterval(async () => {

        const response = await fetch(`/alerts/${data.alert_id}`);

        if (!response.ok) {
            return;
        }

        const alertData = await response.json();

        console.log(alertData);

        if (alertData.technique_id) {

            clearInterval(interval);

            let playbook = null;

            while (true) {

                const playbookResponse = await fetch(
                    `/playbooks/${data.alert_id}`
                );

                if (playbookResponse.ok) {
                    playbook = await playbookResponse.json();                    
                    break;
                }

                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            displayPlaybook(
                alertData,
                playbook,
                data.alert_id
            );

        }

    }, 2000);

};