import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import dulwich.porcelain as git
from dulwich.repo import Repo

REPO_URL = "https://github.com/asliddintech/telegrambot.git"

def main():
    token = os.getenv("GITHUB_TOKEN")
    if not token and len(sys.argv) > 1:
        token = sys.argv[1].strip()

    project_dir = os.path.dirname(os.path.abspath(__file__))
    git_dir = os.path.join(project_dir, ".git")

    # 1. Git repositoriyasini tekshirish yoki yaratish
    if not os.path.exists(git_dir):
        print("📁 Git repositoriyasi ishga tushirilmoqda (init)...")
        repo = git.init(project_dir)
    else:
        repo = Repo(project_dir)

    # 2. Fayllarni qo'shish (.gitignore avtomatik hisobga olinadi)
    print("📦 Fayllar qo'shilmoqda (git add)...")
    git.add(repo, paths=".")

    # 3. Commit qilish
    try:
        commit_id = git.commit(
            repo,
            message=b"Initial commit: Neon Giveaway Telegram Bot",
            committer=b"asliddintech <asliddintech@users.noreply.github.com>",
            author=b"asliddintech <asliddintech@users.noreply.github.com>"
        )
        print(f"✅ Commit yaratildi: {commit_id.decode() if isinstance(commit_id, bytes) else commit_id}")
    except Exception as e:
        print(f"ℹ️ Commit holati: {e}")

    # 4. GitHub ga push qilish
    if not token:
        print("\n⚠️ DIQQAT: GitHub ga kodlarni yuklash uchun GitHub Personal Access Token (PAT) kerak!")
        print("Foydalanish: python push_to_github.py <GITHUB_TOKEN>")
        return

    # Token bilan to'g'ridan-to'g'ri push qilish
    auth_url = f"https://asliddintech:{token}@github.com/asliddintech/telegrambot.git"
    print(f"🚀 GitHub ga yuklanmoqda ({REPO_URL})...")
    try:
        git.push(repo, remote_location=auth_url, refspecs=[b"refs/heads/main:refs/heads/main"])
        print("\n🎉 MUVAFFAQISATLI PUSH QILINDI!")
        print(f"👉 Havola: {REPO_URL}")
    except Exception as e:
        # Agar default branch master bo'lsa
        try:
            git.push(repo, remote_location=auth_url, refspecs=[b"refs/heads/master:refs/heads/main"])
            print("\n🎉 MUVAFFAQISATLI PUSH QILINDI (master -> main)!")
            print(f"👉 Havola: {REPO_URL}")
        except Exception as e2:
            print(f"\n❌ Push qilishda xatolik yuz berdi: {e2}")

if __name__ == "__main__":
    main()
