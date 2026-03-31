<?php
/**
 * Lists comparison folders under comparisons/ for the folder browser.
 * GET without parent: { "parents": [ "example", "mybatch", ... ] }
 * GET ?parent=mybatch: { "cases": [ "mybatch/a", "mybatch/b" ] } or single leaf [ "mybatch" ] if no subcases but files exist.
 */
header('Content-Type: application/json; charset=utf-8');

function valid_segment($s) {
    return is_string($s) && preg_match('/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$/', $s);
}

function is_case_dir($dir) {
    return is_file($dir . '/left.json') && is_file($dir . '/right.json');
}

$comparisonsRoot = __DIR__ . '/comparisons';

if (!is_dir($comparisonsRoot)) {
    echo json_encode(['parents' => []]);
    exit;
}

$parent = isset($_GET['parent']) ? $_GET['parent'] : '';

if ($parent === '') {
    $parents = [];
    foreach (scandir($comparisonsRoot) as $f) {
        if ($f === '.' || $f === '..') {
            continue;
        }
        $p = $comparisonsRoot . '/' . $f;
        if (is_dir($p) && valid_segment($f)) {
            $parents[] = $f;
        }
    }
    sort($parents);
    echo json_encode(['parents' => $parents]);
    exit;
}

$segments = explode('/', $parent);
$base = $comparisonsRoot;
foreach ($segments as $seg) {
    if (!valid_segment($seg)) {
        http_response_code(400);
        echo json_encode(['error' => 'Invalid parent']);
        exit;
    }
    $base .= '/' . $seg;
}

if (!is_dir($base)) {
    http_response_code(404);
    echo json_encode(['error' => 'Folder not found']);
    exit;
}

$cases = [];
foreach (scandir($base) as $f) {
    if ($f === '.' || $f === '..') {
        continue;
    }
    $sub = $base . '/' . $f;
    if (!is_dir($sub) || !valid_segment($f)) {
        continue;
    }
    if (is_case_dir($sub)) {
        $cases[] = $parent . '/' . $f;
    }
}

sort($cases);

if (count($cases) === 0 && is_case_dir($base)) {
    $cases = [$parent];
}

echo json_encode(['cases' => $cases]);
