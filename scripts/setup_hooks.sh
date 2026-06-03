#!/usr/bin/env sh
set -eu

mkdir -p .git/hooks
cat > .git/hooks/pre-push <<'EOF'
#!/usr/bin/env sh
python scripts/submit_log.py
EOF
chmod +x .git/hooks/pre-push

echo "Installed pre-push AI log hook."
