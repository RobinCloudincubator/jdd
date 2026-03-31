<?php
/**
 * Renames comparisons/<fromCaseId>/ to comparisons/<toCaseId>/ (same parent, new leaf name).
 * POST JSON: { "fromCaseId": "parent/run_a", "newLeafName": "run_alpha" }
 */
header('Content-Type: application/json; charset=utf-8');

require_once __DIR__ . '/case-path-validation.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

$raw = file_get_contents('php://input');
$data = json_decode($raw, true);

if (!is_array($data) || !isset($data['fromCaseId']) || !isset($data['newLeafName'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid JSON']);
    exit;
}

$fromCaseId = $data['fromCaseId'];
$newLeaf = isset($data['newLeafName']) ? trim($data['newLeafName']) : '';

if (!valid_case_id($fromCaseId)) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid fromCaseId']);
    exit;
}

if (!valid_case_segment($newLeaf)) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid new name (no slashes, no . or .., max 255 characters per segment)']);
    exit;
}

$segs = explode('/', $fromCaseId);
$oldLeaf = array_pop($segs);

if ($oldLeaf === null || $oldLeaf === '') {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid fromCaseId']);
    exit;
}

if ($newLeaf === $oldLeaf) {
    echo json_encode(['ok' => true, 'toCaseId' => $fromCaseId]);
    exit;
}

$toCaseId = count($segs) ? implode('/', $segs) . '/' . $newLeaf : $newLeaf;

if (!valid_case_id($toCaseId)) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid target path']);
    exit;
}

$root = __DIR__ . '/comparisons';

$fromDir = $root;
foreach (explode('/', $fromCaseId) as $seg) {
    $fromDir .= '/' . $seg;
}

$toDir = $root;
foreach (explode('/', $toCaseId) as $seg) {
    $toDir .= '/' . $seg;
}

if (!is_dir($fromDir)) {
    http_response_code(404);
    echo json_encode(['error' => 'Source folder not found']);
    exit;
}

if (file_exists($toDir)) {
    http_response_code(409);
    echo json_encode(['error' => 'A folder with that name already exists']);
    exit;
}

if (!@rename($fromDir, $toDir)) {
    http_response_code(500);
    echo json_encode(['error' => 'Could not rename folder']);
    exit;
}

echo json_encode(['ok' => true, 'toCaseId' => $toCaseId]);
