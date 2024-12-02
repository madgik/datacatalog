function displayError(message) {
    const errorMessage = document.getElementById('error-message');
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

async function convertExcelToJson() {
    const excelFile = document.getElementById('excelFile').files[0];
    if (!excelFile) {
        displayError("Please select an Excel file first.");
        return;
    }

    const formData = new FormData();
    formData.append('file', excelFile);

    try {
        const response = await fetch('http://127.0.0.1:8000/excel-to-json', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const downloadLink = document.getElementById('downloadJson');
            downloadLink.href = url;
            downloadLink.download = 'data.json';
            downloadLink.style.display = 'block';
            downloadLink.textContent = 'Download JSON';
            displayError("");  // Clear previous error message
        } else {
            const errorData = await response.json();
            displayError(`Failed to convert Excel to JSON: ${errorData.error}`);
        }
    } catch (error) {
        displayError(`An error occurred: ${error.message}`);
    }
}

async function convertJsonToExcel() {
    const jsonFile = document.getElementById('jsonFile').files[0];
    if (!jsonFile) {
        displayError("Please select a JSON file first.");
        return;
    }

    const fileContent = await jsonFile.text();

    try {
        const response = await fetch('http://127.0.0.1:8000/json-to-excel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: fileContent
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const downloadLink = document.getElementById('downloadExcel');
            downloadLink.href = url;
            downloadLink.download = 'data.xlsx';
            downloadLink.style.display = 'block';
            downloadLink.textContent = 'Download Excel';
            displayError("");  // Clear previous error message
        } else {
            const errorData = await response.json();
            displayError(`Failed to convert JSON to Excel: ${errorData.error}`);
        }
    } catch (error) {
        displayError(`An error occurred: ${error.message}`);
    }
}
