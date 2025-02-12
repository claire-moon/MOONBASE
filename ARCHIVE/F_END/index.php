<?php
// formatting le byterinos into "human-readable" also you're gay
function formatBytes($bytes, $precision = 2) {
    $units = ['B', 'KB', 'MB', 'GB', 'TB'];
    $bytes = max($bytes, 0);
    $pow = floor(($bytes ? log($bytes) : 0) / log(1024));
    $pow = min($pow, count($units) - 1);
    $bytes /= (1 << (10 * $pow));
    return round($bytes, $precision) . ' ' . $units[$pow];
}

// directory size fetch (bigger than ur dick usually)
function getDirectorySize($path) {
    $size = 0;
    foreach (new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path)) as $file) {
        $size += $file->getSize();
    }
    return $size;
}

// calculate the storage shit
$totalSpace = disk_total_space('/');
$freeSpace = disk_free_space('/');
$usedSpace = $totalSpace - $freeSpace;

// download handler
if (isset($_GET['file'])) {
    $filePath = $_GET['file'];
    if (file_exists($filePath)) {
        header('Content-Description: File Transfer');
        header('Content-Type: ' . mime_content_type($filePath));
        header('Content-Disposition: attachment; filename="' . basename($filePath) . '"');
        header('Expires: 0');
        header('Cache-Control: must-revalidate');
        header('Pragma: public');
        header('Content-Length: ' . filesize($filePath));
        readfile($filePath);
        exit;
    } else {
        echo "<p>File not found.</p>";
    }
}

// here be html
echo "<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>MOONBASE</title>
    <style>
    body {
        font-family: "Courier New", Courier, monospace;
        margin: 20px;
        background-color: black;
        color: white;
    }
    h1 {
        color: white;
        font-size: 3em;
        text-align: center;
    }
    .stats {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: black;
        padding: 20px;
        width: 250px;
        z-index: 1000;
    }
    .stats h2 {
        margin-top: 0;
    }
    .progress-bar {
        background-color: gray;
        border-radius: 5px;
        overflow: hidden;
        margin: 10px 0;
    }
    .progress-bar div {
        background-color: white;
        height: 10px;
    }
    .file-list {
        background-color: black;
        padding: 20px;
        margin-bottom: 20px;
    }
    .file-list a {
        display: block;
        padding: 10px;
        color: white;
        text-decoration: none;
    }
    .file-list a:hover {
        background-color: gray;
    }
    .upload-form {
        background-color: black;
        padding: 20px;
    }
    .upload-form input[type='file'] {
        display: none;
    }
    .upload-form label {
        color: white;
        text-decoration: underline;
        cursor: pointer;
    }
    .upload-form input[type='submit'] {
        display: none;
    }
    .upload-form .upload-link {
        color: white;
        text-decoration: underline;
        cursor: pointer;
    }
        </style>
</head>
<body>
    <div class='stats'>
        <h2>STORAGE LEFT</h2>
        <p>Free: " . formatBytes($freeSpace) . "</p>
        <p>Total: " . formatBytes($totalSpace) . "</p>
        <div class='progress-bar'>
            <div style='width: " . ($usedSpace / $totalSpace * 100) . "%'></div>
        </div>
    </div>
    <h1>MOONBASE FILES</h1>
    <div class='file-list'>
        <h2>FILES</h2>";

// list files in directory
function listFiles($dir) {
    $files = scandir($dir);
    foreach ($files as $file) {
        if ($file != "." && $file != "..") {
            $filePath = $dir . '/' . $file;
            if (is_dir($filePath)) {
                echo "<a href='?dir=" . urlencode($filePath) . "'>[DIR] $file</a>";
            } else {
                echo "<a href='?file=" . urlencode($filePath) . "'>$file</a>";
            }
        }
    }
}

// directory nav handler
$currentDir = isset($_GET['dir']) ? $_GET['dir'] : 'uploads';
if (!is_dir($currentDir)) {
    $currentDir = 'uploads';
}

listFiles($currentDir);

echo "</div>
    <div class='upload-form'>
        <h2>UPLOAD THAT SHIT</h2>
        <form action='' method='post' enctype='multipart/form-data'>
            <label for='fileToUpload'>Choose File</label>
            <input type='file' name='fileToUpload' id='fileToUpload'>
            <span class='upload-link' onclick="document.querySelector('input[type=submit]').click();">Upload File</span>
            <input type='submit' value='Upload File' name='submit'>
        </form>
    </div>";

// file upload handler
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['fileToUpload'])) {
    $targetDir = $currentDir . '/';
    if (!is_dir($targetDir)) {
        mkdir($targetDir, 0755, true);
    }
    $targetFile = $targetDir . basename($_FILES['fileToUpload']['name']);
    if (move_uploaded_file($_FILES['fileToUpload']['tmp_name'], $targetFile)) {
        echo "<p>It worked! Upload successful.</p>";
    } else {
        echo "<p>The upload fucked up. Try again.</p>";
    }
}

echo "</body>
</html>";
?>