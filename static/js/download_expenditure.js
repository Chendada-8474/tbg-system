const expTable = document.querySelector('#expenditure')

var hideNote = expTable.getElementsByClassName("hide-note")
while (hideNote[0]) {
    hideNote[0].parentNode.removeChild(hideNote[0])
}

var editExp = expTable.getElementsByClassName("edit-exp")
while (editExp[0]) {
    editExp[0].parentNode.removeChild(editExp[0])
}

var expIndex = expTable.getElementsByClassName("exp-index")
while (expIndex[0]) {
    expIndex[0].parentNode.removeChild(expIndex[0])
}

const headRow = [...expTable.querySelectorAll('table thead tr th')]
    .map(column => column.textContent.trim());

const rows = [...expTable.querySelectorAll('table tbody tr')]
    .map(tr => [...tr.querySelectorAll('td')]
        .map(td => td.textContent.trim())
    );

const content = [headRow, ...rows]
    .map(row => row.map(str => '"' + (str ? str.replace(/"/g, '""') : '') + '"'))
    .map(row => row.join(','))
    .join('\n');

const BOM = '\uFEFF'; // utf-8 byte-order-mark
const csvBlob = new Blob([BOM + content], { type: 'text/csv;charset=utf-8' });

const tripDate = document.getElementById("start_date").textContent
const tripName = document.getElementById("trip_name").textContent.replace(" ", "_")
const fileName = tripDate + "_" + tripName

function download() {
    if (window.navigator.msSaveOrOpenBlob) {
        navigator.msSaveBlob(csvBlob, `${fileName}.csv`);
    } else {
        const objectUrl = URL.createObjectURL(csvBlob);
        const a = document.createElement('a');
        a.setAttribute('href', objectUrl);
        a.setAttribute('download', `${fileName}.csv`);

        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
}