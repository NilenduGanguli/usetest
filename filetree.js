<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>File Viewer</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        .file-container {
            border: 1px solid #ccc;
            padding: 15px;
            margin: 10px;
        }
        .thumbnail {
            max-width: 150px;
            max-height: 150px;
        }
        pre {
            background-color: #f4f4f4;
            padding: 10px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <h1>Files</h1>
    <div id="files"></div>

    <script>
        async function fetchFiles() {
            try {
                const response = await fetch('/api/files');
                const data = await response.json();
                const filesDiv = document.getElementById('files');

                for (const [key, file] of Object.entries(data)) {
                    const container = document.createElement('div');
                    container.className = 'file-container';

                    const title = document.createElement('h2');
                    title.textContent = file.filename;
                    container.appendChild(title);

                    const pathPara = document.createElement('p');
                    pathPara.textContent = `Relative Path: ${file.file_relative_path}`;
                    container.appendChild(pathPara);

                    if (file.file_thumbnail) {
                        const img = document.createElement('img');
                        img.src = `data:image/jpeg;base64,${file.file_thumbnail}`;
                        img.alt = 'Thumbnail';
                        img.className = 'thumbnail';
                        container.appendChild(img);
                    }

                    const binaryPre = document.createElement('pre');
                    binaryPre.textContent = file.file_binary;
                    container.appendChild(binaryPre);

                    filesDiv.appendChild(container);
                }
            } catch (error) {
                console.error('Error fetching files:', error);
            }
        }

        // Fetch files on page load
        window.onload = fetchFiles;
    </script>
</body>
</html>