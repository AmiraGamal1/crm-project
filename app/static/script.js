document.getElementById('downloadBtn').addEventListener('click', function() {
    document.getElementById('dropdown').classList.toggle('show');
});

document.getElementById('downloadJson').addEventListener('click', function() {
    fetch('/download_sales?format=json')
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'sales.json';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => console.error('Error downloading JSON:', error));
});

document.getElementById('downloadCsv').addEventListener('click', function() {
    fetch('/download_sales?format=csv')
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'sales.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => console.error('Error downloading CSV:', error));
});

window.onclick = function(event) {
    if (!event.target.matches('#downloadBtn')) {
        const dropdowns = document.getElementsByClassName('dropdown-content');
        for (let i = 0; i < dropdowns.length; i++) {
            const openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}
