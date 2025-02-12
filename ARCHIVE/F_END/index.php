<?php
// Function to format bytes into a human-readable format
function formatBytes($bytes, $precision = 2) {
    $units = ['B', 'KB', 'MB', 'GB', 'TB'];
    $bytes = max($bytes, 0);
    $pow = floor(($bytes ? log($bytes) : 0) / log(1024));
    $pow = min($pow, count($units) - 1);
    $bytes /= (1 << (10 * $pow));
    return round($bytes, $precision) . ' ' . $units[$pow];
}

// Function to get directory size
function getDirectorySize($path) {
    $size = 0;
    foreach (new RecursiveIteratorIterator(new RecursiveDirectoryIterator($path)) as $file) {
        $size += $file->getSize();
    }
    return $size;
}

// Get storage stats
$totalSpace = disk_total_space('/');
$freeSpace = disk_free_space('/');
$usedSpace = $totalSpace - $freeSpace;

// Handle file download
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
        .stats {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: white;
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 5px;
            width: 250px;
            z-index: 1000;
        }
        .stats h2 {
            margin-top: 0;
        }
        .progress-bar {
            background-color: #e1e1e1;
            border-radius: 5px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-bar div {
            background-color: #007bff;
            height: 10px;
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
    <div class='stats'>
        <h2>Storage Stats</h2>
        <p>Free: " . formatBytes($freeSpace) . "</p>
        <p>Total: " . formatBytes($totalSpace) . "</p>
        <div class='progress-bar'>
            <div style='width: " . ($usedSpace / $totalSpace * 100) . "%'></div>
        </div>
    </div>
    <h1>MOONBASE FILES</h1>
    <div class='file-list'>
        <h2>FILES</h2>";

// Function to list files in the directory
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

// Handle directory navigation
$currentDir = isset($_GET['dir']) ? $_GET['dir'] : 'uploads';
if (!is_dir($currentDir)) {
    $currentDir = 'uploads';
}

listFiles($currentDir);

echo "</div>
    <div class='upload-form'>
        <h2>UPLOAD THAT SHIT</h2>
        <form action='' method='post' enctype='multipart/form-data'>
            <input type='file' name='fileToUpload' id='fileToUpload'>
            <input type='submit' value='Upload File' name='submit'>
        </form>
    </div>";

// Handle file upload
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