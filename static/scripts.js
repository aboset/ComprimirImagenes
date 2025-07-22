const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const results = document.getElementById('results');

dropZone.addEventListener('dragover', e => {
  e.preventDefault();
  dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('dragover');
  handleFiles([...e.dataTransfer.files]);
});

fileInput.addEventListener('change', () => {
  handleFiles([...fileInput.files]);
});

function handleFiles(files) {
  files.forEach((file, index) => {
    const formData = new FormData();
    formData.append('images', file);

    const itemId = `upload-${Date.now()}-${index}`;
    const div = document.createElement('div');
    div.className = 'result-item';
    div.innerHTML = `
      <p><strong>${file.name}</strong></p>
      <div class="progress-bar-container">
        <div class="progress-bar" id="${itemId}-bar" style="width: 0%;"></div>
      </div>
      <p id="${itemId}-status">Subiendo...</p>
    `;
    results.appendChild(div);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload', true);

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        const percent = Math.round((e.loaded / e.total) * 100);
        document.getElementById(`${itemId}-bar`).style.width = `${percent}%`;
      }
    };

    xhr.onload = function () {
      if (xhr.status === 200) {
        const data = JSON.parse(xhr.responseText);
        document.getElementById(`${itemId}-status`).innerHTML = `
          Reducción: ${data.original}MB → ${data.compressed}MB<br>
          <a href="/download/${data.name}" download>Descargar</a>
        `;
        document.getElementById(`${itemId}-bar`).style.backgroundColor = '#28a745';
      } else {
        document.getElementById(`${itemId}-status`).textContent = 'Error al subir.';
        document.getElementById(`${itemId}-bar`).style.backgroundColor = '#dc3545';
      }
    };

    xhr.onerror = function () {
      document.getElementById(`${itemId}-status`).textContent = 'Error de red.';
      document.getElementById(`${itemId}-bar`).style.backgroundColor = '#dc3545';
    };

    xhr.send(formData);
  });
}
