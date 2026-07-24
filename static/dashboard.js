async function loadDashboard(){

    const response = await fetch("/dashboard");

    const data = await response.json();
    
    const table = document.getElementById("tableBody");

    table.innerHTML="";

    data.forEach(alert => {

        let row=document.createElement("tr");

        row.innerHTML=`
        <td>${alert.timestamp}</td>
        <td>${alert.alert_type}</td>
        <td>${alert.technique}</td>
        <td>${alert.confidence}%</td>
        <td class="${alert.status}">
            ${alert.status}
        </td>

        <td>
        <a href="review.html?id=${alert.id}">

        Review
        </a>
        </td>
        `;

        table.appendChild(row);
    });
    
}
    loadDashboard();
    setInterval(loadDashboard, 10000);