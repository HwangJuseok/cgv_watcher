# 🚀 GitHub 업로드 가이드

이 문서는 수정된 코드를 GitHub에 안전하게 올리는 방법을 단계별로 안내합니다. **저장소가 이미 GitHub에 존재하는지(과거에 push한 적이 있는지) 여부에 따라 순서가 크게 달라지므로**, 아래에서 본인의 상황에 맞는 시나리오를 먼저 선택하세요.

> 압축 파일 이름(`cgv_watcher-main.zip`)이 GitHub의 "Download ZIP" 버튼으로 받은 형태와 동일하므로, **이미 GitHub 저장소가 존재할 가능성이 높다고 가정**하고 시나리오 B를 기본으로 설명합니다. 처음 올리는 것이라면 시나리오 A만 보시면 됩니다.

---

## 0단계. 무엇보다 먼저 — 노출된 시크릿부터 폐기하세요

**코드를 고치는 것과 별개로, 이미 유출된 값 자체를 무효화하는 작업은 반드시 먼저(또는 최대한 빨리) 해야 합니다.** 히스토리를 아무리 깨끗하게 지워도, 이미 누군가 값을 복사해 갔다면 지우는 것만으로는 막을 수 없기 때문입니다.

1. **텔레그램 봇 토큰 폐기 및 재발급**
   - 텔레그램에서 [@BotFather](https://t.me/BotFather)와 대화 시작
   - `/mybots` → 해당 봇 선택 → `API Token` → `Revoke current token`
   - 새로 발급된 토큰을 복사해 둡니다 (잠시 후 `.env`에 입력).

2. **RSA 개인키(`ssh-key-2026-08-27.key`) 폐기**
   - 이 키로 접속하던 서버(오라클 클라우드 등)에 **다른 방법**(클라우드 콘솔의 웹 터미널, 복구용 키 등)으로 접속
   - `~/.ssh/authorized_keys` 파일에서 해당 공개키 항목을 삭제
   - 새 SSH 키 페어를 생성해서 교체 (`ssh-keygen -t ed25519`), **새 키는 프로젝트 폴더 밖의 `~/.ssh/` 등에 보관하고 절대 git 저장소 안에 두지 않습니다.**

이 두 가지를 끝내야 아래 단계들이 의미가 있습니다.

---

## 시나리오 A. 아직 GitHub에 올린 적이 없는 경우

가장 간단한 경로입니다. 민감한 파일이 애초에 커밋된 적이 없으므로 히스토리 정리가 필요 없습니다.

```bash
# 1) 기존 코드 위에 수정된 파일들을 덮어씁니다.
#    (main.py, config.py, requirements.txt, .gitignore, crawler.py,
#     ContentView.swift, TargetListView.swift, NetworkManager.swift, MainTabView.swift,
#     그리고 새 파일 AppSettings.swift, SettingsView.swift 추가)

cd cgv_watcher-main

# 2) .env 파일 생성 (git에 올라가지 않음)
cp .env.example .env
# .env 파일을 열어 TELEGRAM_BOT_TOKEN 값을 새로 발급받은 토큰으로 채워 넣으세요.

# 3) ssh-key-2026-08-27.key 파일은 완전히 삭제합니다. (프로젝트와 무관, 절대 포함하지 않기)
rm -f ssh-key-2026-08-27.key

# 4) 로컬에서 정상 동작하는지 확인
pip install -r requirements.txt
python main.py
# 다른 터미널에서 Ctrl+C로 종료 후 문제 없으면 다음 단계로

# 5) git 초기화 및 첫 커밋
git init
git add .
git status   # config.py, .env, ssh-key*.key 가 목록에 없는지(=ignore 되는지) 꼭 확인!
git commit -m "Initial commit: CGV Watcher (secrets excluded)"

# 6) GitHub에서 새 저장소 생성 후 연결
git branch -M main
git remote add origin https://github.com/<본인계정>/<저장소이름>.git
git push -u origin main
```

`git status` 출력에 `config.py`, `.env`, `ssh-key-2026-08-27.key`가 **절대 나타나지 않아야** 합니다. 나타난다면 `.gitignore` 파일이 제대로 적용되지 않은 것이니 다시 확인하세요.

---

## 시나리오 B. 이미 GitHub에 올린 적이 있는 경우 (히스토리에 시크릿이 남아있음)

이 경우 `.gitignore`에 파일을 추가하는 것만으로는 **과거 커밋 기록에 남아있는 토큰/개인키를 지울 수 없습니다.** git은 이미 추적 중이던 파일을 `.gitignore`가 생겼다고 해서 자동으로 추적 해제하지 않고, 과거 커밋의 스냅샷은 그대로 남아있기 때문입니다. 따라서 **히스토리 자체를 다시 작성(rewrite)**해야 합니다.

### 1) 작업 전 백업

```bash
cp -r cgv_watcher-main cgv_watcher-main-backup
cd cgv_watcher-main
```

### 2) 수정된 코드 적용

제공된 수정 파일들(`main.py`, `config.py`, `requirements.txt`, `.gitignore`, `crawler.py`, iOS `.swift` 파일들, `AppSettings.swift`, `SettingsView.swift`)을 기존 파일 위에 덮어씁니다.

```bash
cp .env.example .env
# .env 파일을 열어 새로 발급받은 TELEGRAM_BOT_TOKEN 입력
```

### 3) git-filter-repo 설치

GitHub 공식 문서에서도 권장하는 도구입니다. (`git filter-branch`보다 빠르고 안전합니다.)

```bash
pip install git-filter-repo
```

### 4) 히스토리 전체에서 민감 파일 완전 삭제

```bash
# ssh 개인키 파일을 모든 커밋 히스토리에서 제거
git filter-repo --path ssh-key-2026-08-27.key --invert-paths

# config.py를 모든 커밋 히스토리에서 제거
#  (앞으로는 .gitignore로 관리되고, git 추적에서는 완전히 빠지게 됩니다)
git filter-repo --path config.py --invert-paths
```

### 5) (선택, 권장) 코드 안에 텍스트로 남아있던 토큰 문자열 자체도 치환

`main.py`의 과거 커밋들 안에는 여전히 텍스트로 토큰 문자열이 남아있습니다. 파일 자체는 남겨야 하므로, 문자열만 치환합니다.

```bash
cat > /tmp/replacements.txt << 'EOF'
8809083346:AAHuuw11BUjbEkI7dnF8yVkSe2RPy7fOC3A==>***TELEGRAM_TOKEN_REMOVED***
EOF

git filter-repo --replace-text /tmp/replacements.txt
```

### 6) 원격 저장소 다시 연결 (filter-repo가 자동으로 origin을 제거합니다)

```bash
git remote add origin https://github.com/<본인계정>/<저장소이름>.git
```

### 7) 강제 푸시로 정리된 히스토리를 GitHub에 반영

> ⚠️ **주의**: 이 작업은 원격 저장소의 커밋 히스토리를 되돌릴 수 없게 덮어씁니다. 이 저장소를 다른 사람과 함께 쓰고 있다면(협업 중이라면) 반드시 사전에 공지하세요. force push 이후에는 **모든 협업자가 기존 로컬 클론을 버리고 다시 clone 받아야** 합니다.

```bash
git push origin --force --all
git push origin --force --tags
```

### 8) 새로운 수정 사항 커밋

히스토리 정리와는 별개로, 이번에 고친 코드(설정 분리, iOS 설정 화면 추가 등)를 새 커밋으로 올립니다.

```bash
git add .
git status   # config.py, .env, ssh-key*.key 가 없는지 다시 한번 확인!
git commit -m "fix: 시크릿 하드코딩 제거, 환경변수 기반 설정 분리, iOS 앱에 설정 화면 추가"
git push
```

### 9) GitHub 저장소에서 최종 확인

- GitHub 저장소 페이지에서 코드 검색(`/`)으로 `AAHuuw11` 같은 토큰 일부 문자열을 검색해 **결과가 없는지** 확인합니다.
- 저장소가 **Public**이라면 Settings → Code security and analysis에서 **Push protection / Secret scanning**을 활성화해 두면, 앞으로 실수로라도 비슷한 시크릿을 커밋했을 때 GitHub가 push 자체를 막아줍니다.
- 저장소 Settings → General → Danger Zone에서 필요하다면 **Private으로 전환**하는 것도 고려하세요.

---

## 공통 체크리스트 (커밋 전 항상 확인)

```bash
git status
```

아래 파일들이 **목록에 절대 나타나지 않아야** 합니다.

- [ ] `config.py`
- [ ] `.env`
- [ ] `ssh-key-2026-08-27.key` (또는 어떤 `*.key`, `*.pem` 파일도)
- [ ] `data/` 폴더 (사용자 텔레그램 ID가 담긴 SQLite DB)

나타난다면 `git rm --cached <파일명>` 으로 추적을 해제한 뒤 다시 확인하세요.

```bash
git rm --cached config.py
git rm --cached .env
git rm --cached ssh-key-2026-08-27.key
```
