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

            document.getElementById("result").innerHTML = `
                <h2>${alertData.technique_name}</h2>

                <p><strong>Technique ID:</strong> ${alertData.technique_id}</p>

                <p><strong>Confidence:</strong> ${alertData.confidence}</p>

                <h3>Generated Playbook</h3>

                <pre>${playbook.playbook_json}</pre>

                <br>

                <button id="approveBtn">Approve</button>
                <button id="rejectBtn">Reject</button>
            `;

            document.getElementById("approveBtn").addEventListener("click", async () => {

                const response = await fetch(
                    `/playbooks/${data.alert_id}/approve`,
                    {
                        method: "POST"
                    }
                );

                if (!response.ok) {
                    console.error(await response.text());
                    alert("Approve failed.");
                    return;
                }

                const result = await response.json();

                alert(result.message);

            });


            document.getElementById("rejectBtn").addEventListener("click", async () => {

                const response = await fetch(
                    `/playbooks/${data.alert_id}/reject`,
                    {
                        method: "POST"
                    }
                );

                if (!response.ok) {
                    console.error(await response.text());
                    alert("Reject failed.");
                    return;
                }

                const result = await response.json();

                alert(result.message);

            });

        }

    }, 2000);

};