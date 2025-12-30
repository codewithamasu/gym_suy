#!/usr/bin/env bash
# tools/compare_sqlite_conflicts.sh
# Usage:
#   ./tools/compare_sqlite_conflicts.sh [path/to/file.db] [base_ref] [ours_ref] [theirs_ref]
# Examples:
#   ./tools/compare_sqlite_conflicts.sh database/gym.db
#   ./tools/compare_sqlite_conflicts.sh database/gym.db origin/main BranchYohanes origin/main
set -euo pipefail

FILE="${1:-database/gym.db}"
BASE_REF="${2:-origin/main}"
OURS_REF="${3:-HEAD}"
THEIRS_REF="${4:-origin/main}"

TMPDIR="$(mktemp -d)"
cleanup() { rm -rf "$TMPDIR"; }
trap cleanup EXIT

echo "File        : $FILE"
echo "Base ref    : $BASE_REF"
echo "Ours ref    : $OURS_REF"
echo "Theirs ref  : $THEIRS_REF"
echo "Work dir    : $TMPDIR"
echo

# Helpers
extract_index_stage() {
  stage=$1; out=$2
  if git show ":${stage}:${FILE}" > "$out" 2>/dev/null; then
    echo "Extracted index stage $stage -> $out"
    return 0
  fi
  return 1
}

extract_ref() {
  ref=$1; out=$2
  if git show "${ref}:${FILE}" > "$out" 2>/dev/null; then
    echo "Extracted ${ref} -> $out"
    return 0
  fi
  return 1
}

# Try to extract index stages first (useful during an ongoing merge conflict)
base_db="$TMPDIR/gym-base.db"
ours_db="$TMPDIR/gym-ours.db"
theirs_db="$TMPDIR/gym-theirs.db"

if extract_index_stage 1 "$base_db" && extract_index_stage 2 "$ours_db" && extract_index_stage 3 "$theirs_db"; then
  echo "Found staged conflict versions in index."
else
  echo "No index stages for file (not in conflicted index) or partial. Falling back to refs."
  rm -f "$base_db" "$ours_db" "$theirs_db"
  # Try to extract using provided refs
  extract_ref "$BASE_REF" "$base_db" || echo "Warning: could not extract $BASE_REF:$FILE"
  extract_ref "$OURS_REF" "$ours_db" || echo "Warning: could not extract $OURS_REF:$FILE"
  extract_ref "$THEIRS_REF" "$theirs_db" || echo "Warning: could not extract $THEIRS_REF:$FILE"
fi

# Function to dump DB -> SQL if file exists and is a valid SQLite DB
dump_sql() {
  dbfile=$1; sqlout=$2
  if [ -f "$dbfile" ]; then
    if sqlite3 "$dbfile" "PRAGMA quick_check;" > /dev/null 2>&1; then
      echo "Dumping $dbfile -> $sqlout"
      sqlite3 "$dbfile" .dump > "$sqlout"
    else
      echo "Warning: $dbfile exists but is not a valid sqlite DB (skipping dump)"
    fi
  else
    echo "No file $dbfile (skipping)"
  fi
}

dump_sql "$base_db" "$TMPDIR/gym-base.sql"
dump_sql "$ours_db" "$TMPDIR/gym-ours.sql"
dump_sql "$theirs_db" "$TMPDIR/gym-theirs.sql"

# Run sqldiff if available (shows SQL patch to convert A -> B)
if command -v sqldiff > /dev/null 2>&1; then
  if [ -f "$base_db" ] && [ -f "$ours_db" ]; then
    echo "Running sqldiff base -> ours -> $TMPDIR/sqldiff-base-to-ours.sql"
    sqldiff "$base_db" "$ours_db" > "$TMPDIR/sqldiff-base-to-ours.sql" || true
  fi
  if [ -f "$base_db" ] && [ -f "$theirs_db" ]; then
    echo "Running sqldiff base -> theirs -> $TMPDIR/sqldiff-base-to-theirs.sql"
    sqldiff "$base_db" "$theirs_db" > "$TMPDIR/sqldiff-base-to-theirs.sql" || true
  fi
else
  echo "sqldiff not found (install sqlite3's sqldiff for SQL patch output)."
fi

# Run text diffs on SQL dumps if available
if [ -f "$TMPDIR/gym-base.sql" ] && [ -f "$TMPDIR/gym-ours.sql" ]; then
  echo
  echo "Diff base.sql -> ours.sql:"
  diff -u "$TMPDIR/gym-base.sql" "$TMPDIR/gym-ours.sql" | sed -n '1,200p' || true
  echo "Saved full diff -> $TMPDIR/diff-base-to-ours.patch"
  diff -u "$TMPDIR/gym-base.sql" "$TMPDIR/gym-ours.sql" > "$TMPDIR/diff-base-to-ours.patch" || true
fi

if [ -f "$TMPDIR/gym-base.sql" ] && [ -f "$TMPDIR/gym-theirs.sql" ]; then
  echo
  echo "Diff base.sql -> theirs.sql:"
  diff -u "$TMPDIR/gym-base.sql" "$TMPDIR/gym-theirs.sql" | sed -n '1,200p' || true
  echo "Saved full diff -> $TMPDIR/diff-base-to-theirs.patch"
  diff -u "$TMPDIR/gym-base.sql" "$TMPDIR/gym-theirs.sql" > "$TMPDIR/diff-base-to-theirs.patch" || true
fi

# Offer to launch visual merge tool if available
if command -v meld > /dev/null 2>&1 && [ -f "$TMPDIR/gym-ours.sql" ] && [ -f "$TMPDIR/gym-theirs.sql" ]; then
  echo
  echo "Launching meld for visual comparison of ours vs theirs (SQL dumps)..."
  meld "$TMPDIR/gym-ours.sql" "$TMPDIR/gym-theirs.sql" &
fi

echo
echo "All outputs are in: $TMPDIR"
echo "Files produced (if present):"
ls -la "$TMPDIR" || true
echo
echo "When you have a merged SQL you like, create a new sqlite DB and replace:"
echo "  sqlite3 new.db < merged.sql"
echo "  cp new.db $FILE"
echo "  git add $FILE && git commit -m 'Resolve DB conflict: merged changes' && git push"