<?php
/**
 * Shared rules for comparison paths under comparisons/<caseId>/.
 * Segments may include spaces and most Unicode; / and \ are forbidden; . and .. are not allowed as names.
 */

function valid_case_segment($s) {
    if (!is_string($s) || $s === '' || strlen($s) > 255) {
        return false;
    }
    if ($s === '.' || $s === '..') {
        return false;
    }
    if (preg_match('/[\x00\/\\\\]/u', $s)) {
        return false;
    }
    if (preg_match('/[\x00-\x1f\x7f]/', $s)) {
        return false;
    }
    return true;
}

function valid_case_id($id) {
    if (!is_string($id) || strlen($id) > 2048) {
        return false;
    }
    $parts = explode('/', $id);
    foreach ($parts as $p) {
        if ($p === '' || !valid_case_segment($p)) {
            return false;
        }
    }
    return count($parts) >= 1;
}
