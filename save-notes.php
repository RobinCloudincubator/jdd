<?php
/**
 * Writes comparisons/<caseId>/notes.txt (for repo-backed notes).
 * Requires PHP (e.g. php-fpm behind nginx, or: php -S localhost:8080 -t . from project root).
 */
header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

require_once __DIR__ . '/case-path-validation.php';

$raw = file_get_contents('php://input');
$data = json_decode($raw, true);

if (!is_array($data) || !isset($data['caseId'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid JSON']);
    exit;
}

$caseId = $data['caseId'];
$content = isset($data['content']) ? $data['content'] : '';

if (!valid_case_id($caseId)) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid caseId']);
    exit;
}

if (!is_string($content)) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid content']);
    exit;
}

if (strlen($content) > 2 * 1024 * 1024) {
    http_response_code(413);
    echo json_encode(['error' => 'Content too large']);
    exit;
}

$dir = __DIR__ . '/comparisons';
foreach (explode('/', $caseId) as $seg) {
    $dir .= '/' . $seg;
}
$notesPath = $dir . '/notes.txt';

if (!is_dir($dir)) {
    if (!mkdir($dir, 0755, true)) {
        http_response_code(500);
        echo json_encode(['error' => 'Could not create directory']);
        exit;
    }
}

$bytes = @file_put_contents($notesPath, $content);
if ($bytes === false) {
    http_response_code(500);
    echo json_encode(['error' => 'Could not write notes.txt']);
    exit;
}

echo json_encode(['ok' => true, 'bytes' => $bytes]);
