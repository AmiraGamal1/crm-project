document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('downloadBtn').addEventListener('click', function() {
    document.getElementById('dropdown').classList.toggle('show');
});

function downloadFile(format, table){
    console.log(`Fetching /download_${table}?format=${format}`);
    fetch(`/download_${table}?format=${format}`)
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `${table}.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => console.error(`Error downloading ${format.toUpperCase()}:`, error));
}

document.querySelectorAll('.download-link').forEach(function(element) {
    element.addEventListener('click', function(event) {
        event.preventDefault();
        const format = this.getAttribute('data-format');
        const table = this.getAttribute('data-table');
        downloadFile(format, table);
    });
});


document.getElementById('openModalBtn').onclick = function() {
    document.getElementById('uploadModal').style.display = 'block';
}

document.getElementsByClassName('close')[0].onclick = function() {
    document.getElementById('uploadModal').style.display = 'none';
}
window.addEventListener('click', function(event) {
    if (!event.target.closest('#downloadBtn') && !event.target.closest('.dropdown-content')) {
        const dropdowns = document.getElementsByClassName('dropdown-content');
        for (let i = 0; i < dropdowns.length; i++) {
            const openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
    if (event.target == document.getElementById('uploadModal')) {
        document.getElementById('uploadModal').style.display = 'none';
    }
});

document.getElementById('uploadForm').addEventListener('submit', async function (event) {
    event.preventDefault();
    const fileInput = document.getElementById('fileInput');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const isProductPage = window.location.pathname.includes('view_product');
    const actionUrl = isProductPage ? '/upload_products' : '/upload_sales';
    console.log('Action URL:', actionUrl);
        
    try {
        const response = await fetch(actionUrl, {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        if (response.ok) {
            alert('File uploaded successfully');
            // Redirect based on the current page
            const redirectUrl = window.location.pathname.includes('view_product') ? '/view_product' : '/view_sale';
            window.location.href = redirectUrl;
        } else {
            alert(result.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while uploading the file.');
    }

    document.getElementById('uploadModal').style.display = 'none';

});

const popup = document.getElementById('popup');
fetch('/get_messages')
    .then(response => response.json())
    .then(data => {
        if (data.messages.length > 0) {
            data.messages.forEach(msg => {
                popup.textContent = msg.message;
                popup.classList.add(msg.category);
                popup.style.display = 'block';
                setTimeout(() => {
                    popup.style.display = 'none';
                }, 100000);
            });
        }
    });
});
