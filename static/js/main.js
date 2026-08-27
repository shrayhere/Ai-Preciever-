document.addEventListener('DOMContentLoaded', () => {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');
  const previewContainer = document.getElementById('previewContainer');
  const previewImg = document.getElementById('previewImg');
  const previewFilename = document.getElementById('previewFilename');
  const previewMeta = document.getElementById('previewMeta');
  const btnRemove = document.getElementById('btnRemove');
  const btnAnalyze = document.getElementById('btnAnalyze');
  const loadingOverlay = document.getElementById('loadingOverlay');
  const errorBanner = document.getElementById('errorBanner');

  if (!dropzone || !fileInput) return;

  let selectedFile = null;

  // Trigger file browser on click
  dropzone.addEventListener('click', (e) => {
    if (e.target.closest('#previewContainer')) return;
    fileInput.click();
  });

  // Drag & drop handlers
  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('dragover');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('dragover');
    }, false);
  });

  dropzone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelection(files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (fileInput.files.length > 0) {
      handleFileSelection(fileInput.files[0]);
    }
  });

  function showError(msg) {
    errorBanner.textContent = msg;
    errorBanner.style.display = 'block';
  }

  function hideError() {
    errorBanner.style.display = 'none';
  }

  function handleFileSelection(file) {
    hideError();
    const validTypes = ['image/jpeg', 'image/png', 'image/pjpeg', 'image/x-png'];
    const validExts = ['jpg', 'jpeg', 'png'];
    const ext = file.name.rsplit ? file.name.rsplit('.').pop().toLowerCase() : file.name.split('.').pop().toLowerCase();

    if (!validExts.includes(ext)) {
      showError(`Unsupported file extension '.${ext}'. Please upload a JPG or PNG image.`);
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      showError('File size exceeds 10MB limit.');
      return;
    }

    selectedFile = file;

    // Show Preview
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      previewFilename.textContent = file.name;
      previewMeta.textContent = `${(file.size / (1024 * 1024)).toFixed(2)} MB • ${file.type || 'Image'}`;
      previewContainer.style.display = 'block';
    };
    reader.readAsDataURL(file);
  }

  if (btnRemove) {
    btnRemove.addEventListener('click', (e) => {
      e.stopPropagation();
      selectedFile = null;
      fileInput.value = '';
      previewContainer.style.display = 'none';
      hideError();
    });
  }

  if (btnAnalyze) {
    btnAnalyze.addEventListener('click', (e) => {
      e.stopPropagation();
      if (!selectedFile) {
        showError('Please select or drop an image first.');
        return;
      }

      hideError();
      loadingOverlay.style.display = 'block';
      btnAnalyze.disabled = true;

      const formData = new FormData();
      formData.append('image', selectedFile);

      fetch('/analyze', {
        method: 'POST',
        body: formData
      })
      .then(async res => {
        const isJson = res.headers.get('content-type')?.includes('application/json');
        const data = isJson ? await res.json() : null;
        if (!res.ok) {
          const errMsg = (data && data.error) ? data.error : `Server response error (${res.status})`;
          throw new Error(errMsg);
        }
        return data;
      })
      .then(data => {
        if (data && data.success) {
          window.location.href = data.redirect_url;
        } else {
          loadingOverlay.style.display = 'none';
          btnAnalyze.disabled = false;
          showError((data && data.error) || 'Analysis failed.');
        }
      })
      .catch(err => {
        loadingOverlay.style.display = 'none';
        btnAnalyze.disabled = false;
        showError(err.message || 'Server error during analysis. Please try again.');
        console.error(err);
      });
    });
  }
});


window.clearAuditLog = function() {
  if (confirm("Are you sure you want to clear all recent scan audit logs and permanently delete all past saved image data?")) {
    fetch('/clear_history', {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        window.location.reload();
      } else {
        alert("Failed to clear history: " + (data.error || "Unknown error"));
      }
    })
    .catch(err => {
      console.error(err);
      alert("Error clearing audit log history.");
    });
  }
};
