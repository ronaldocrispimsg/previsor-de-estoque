#!/usr/bin/env python3
"""
scripts/backup_chat.py
Sincroniza e preserva o histórico de conversas brutas (transcript.jsonl e transcript_full.jsonl)
em .agents/historico_chat/ com manifesto de sessões.
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime

WORKSPACE_DIR = Path(__file__).resolve().parent.parent
BRAIN_DIR = Path.home() / ".gemini" / "antigravity" / "brain"
BACKUP_DIR = WORKSPACE_DIR / ".agents" / "historico_chat"
MANIFEST_FILE = BACKUP_DIR / "manifesto_sessoes.json"


def sync_chat_history():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    if not BRAIN_DIR.exists():
        print(f"Diretório de transcrições não encontrado: {BRAIN_DIR}")
        return

    sessions = []

    # Procura por pastas de conversa com logs
    for conv_dir in sorted(BRAIN_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if not conv_dir.is_dir():
            continue

        logs_dir = conv_dir / ".system_generated" / "logs"
        t_compact = logs_dir / "transcript.jsonl"
        t_full = logs_dir / "transcript_full.jsonl"

        if not t_compact.exists() and not t_full.exists():
            continue

        conv_id = conv_dir.name
        dest_conv_dir = BACKUP_DIR / conv_id
        dest_conv_dir.mkdir(parents=True, exist_ok=True)

        copied = False
        mtime = 0

        if t_compact.exists():
            shutil.copy2(t_compact, dest_conv_dir / "transcript.jsonl")
            mtime = max(mtime, t_compact.stat().st_mtime)
            copied = True

        if t_full.exists():
            shutil.copy2(t_full, dest_conv_dir / "transcript_full.jsonl")
            mtime = max(mtime, t_full.stat().st_mtime)
            copied = True

        if copied:
            sessions.append({
                "conversation_id": conv_id,
                "last_modified": datetime.fromtimestamp(mtime).isoformat(),
                "has_compact": (dest_conv_dir / "transcript.jsonl").exists(),
                "has_full": (dest_conv_dir / "transcript_full.jsonl").exists(),
                "size_compact_bytes": (dest_conv_dir / "transcript.jsonl").stat().st_size if (dest_conv_dir / "transcript.jsonl").exists() else 0,
                "size_full_bytes": (dest_conv_dir / "transcript_full.jsonl").stat().st_size if (dest_conv_dir / "transcript_full.jsonl").exists() else 0,
            })

    if sessions:
        # Copia a sessão mais recente para a raiz de .agents/historico_chat para acesso rápido
        latest_id = sessions[0]["conversation_id"]
        latest_dir = BACKUP_DIR / latest_id
        if (latest_dir / "transcript.jsonl").exists():
            shutil.copy2(latest_dir / "transcript.jsonl", BACKUP_DIR / "transcript.jsonl")
        if (latest_dir / "transcript_full.jsonl").exists():
            shutil.copy2(latest_dir / "transcript_full.jsonl", BACKUP_DIR / "transcript_full.jsonl")

    # Salva o manifesto atualizado
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "total_sessions": len(sessions),
            "updated_at": datetime.now().isoformat(),
            "sessions": sessions
        }, f, indent=2, ensure_ascii=False)

    print(f"Sincronização concluída: {len(sessions)} sessões preservadas em {BACKUP_DIR}")


if __name__ == "__main__":
    sync_chat_history()
