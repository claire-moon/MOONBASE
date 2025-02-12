<?php
// HTML start
echo "<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>MOONBASE</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f4f4f4;
        }
        h1 {
            color: #333;
        }
        .file-list {
            background-color: white;
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .file-list a {
            display: block;
            padding: 10px;
            color: #007bff;
            text-decoration: none;
        }
        .file-list a:hover {
            background-color: #f1f1f1;
        }
        .upload-form {
            background-color: white;
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        .upload-form input[type='file'] {
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <h1>File Server</h1>
    <div class='file-list'>
        <h2>Files</h2>";

// list files function
function listFiles($dir) {
    $files = scandir($dir);
    foreach ($files as $file) {
        if ($file != "." && $file != "..") {
            $filePath = $dir . '/' . $file;
            echo "<a href='$filePath'>$file</a>";
        }
    }
}

// run the function
listFiles('.');

echo "</div>
    <div class='upload-form'>
        <h2>Upload File</h2>
        <form action='' method='post' enctype='multipart/form-data'>
            <input type='file' name='fileToUpload' id='fileToUpload'>
            <input type='submit' value='Upload File' name='submit'>
        </form>
    </div>";

// file upload handlerf
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['fileToUpload'])) {
    $targetDir = "uploads/";
    if (!is_dir($targetDir)) {
        mkdir($targetDir, 0755, true);
    }
    $targetFile = $targetDir . basename($_FILES['fileToUpload']['name']);
    if (move_uploaded_file($_FILES['fileToUpload']['tmp_name'], $targetFile)) {
        echo "<p>File uploaded successfully.</p>";
    } else {
        echo "<p>Sorry, there was an error uploading your file.</p>";
    }
}

echo "</body>
</html>";
?>