"""Cursor の beforeShellExecution フック: temp 以外のファイルへのシェル書き込みを拒否する。

方針（myrules「ファイル修正と差分確認」）: temp/ と FishTrack の temp-spec-crawl/ 以外への作成・更新・削除は、
シェルやスクリプトで行わず StrReplace / Write / Delete で行う。シェル経由の変更は Cursor の Review（差分）に
載らないことがあるため（Obsidian は git 管理外）。

判定（書き込みの意図があるコマンドだけを対象にする）:
- markdownlint の --fix、markdownlint-all.ps1 -Fix は場所を問わず拒否する。
- リダイレクト（> / >>）の先が temp 配下でも $null でもなければ拒否する。
- 書き込みを示す語（Set-Content・Copy-Item・WriteAllText・write_text・sed -i 等）を含み、書き込み先パスが
  temp 配下だけでない（または特定できない）場合は拒否する。cwd が temp 配下なら相対パスは temp として扱う。
- 読み取りだけのコマンド、テスト実行（pytest のキャッシュ生成）、git・docker の操作は対象外。
- 解析できない入力は許可する（フック自体の失敗で作業を止めない）。
- 限界: スクリプトファイルの中身（例: python scripts/x.py が内部で書くファイル）は検査しない。

使い方:
- フック本体: stdin の JSON（command・cwd）を読み、stdout へ JSON を返す。拒否時は終了コード 2。
- 自己テスト: python guard_obsidian_shell_write.py --self-test
"""

from __future__ import annotations

import json
import re
import sys

WRITE_TOKEN_PATTERNS = (
    r"\bset-content\b",
    r"\badd-content\b",
    r"\bout-file\b",
    r"\btee-object\b",
    r"\bcopy-item\b",
    r"\bmove-item\b",
    r"\bremove-item\b",
    r"\brename-item\b",
    r"\bnew-item\b",
    r"\bclear-content\b",
    r"\bset-item\b",
    r"\bwriteall(?:text|bytes|lines)\b",
    r"\bappendall(?:text|bytes|lines)\b",
    r"\bwrite_text\b",
    r"\bwrite_bytes\b",
    r"\bshutil\.(?:copy|copy2|copyfile|move)\b",
    r"\bos\.(?:replace|remove|rename)\b",
    r"\bopen\([^)]*['\"][wa]",
    r"(?<![\w-])--?fix\b",
    r"\bsed\s+-i\b",
    r"\btee\b",
    r"\b(?:rm|del|erase|mv|cp|touch|ren)\s",
    r"(?<![\w-])(?:copy|move)\s",
)
WRITE_TOKEN_RE = re.compile("|".join(WRITE_TOKEN_PATTERNS), re.IGNORECASE)

# 区切り（&& || ; | 改行）。引用符の外だけで分割し、区切りごとに判定する。
SEGMENT_SEPARATOR_RE = re.compile(r"&&|\|\||;|\||\r?\n")
# git の操作（区切りの先頭が git）は対象外。docstring の「git・docker の操作は対象外」に従う。
GIT_SEGMENT_RE = re.compile(r"^\s*git\s", re.IGNORECASE)

# 2>&1 のような fd 複製（&）は除外する。
REDIRECT_TARGET_RE = re.compile(r"(?<![\d&])>>?(?!&)\s*(\"[^\"]+\"|'[^']+'|[^\s|;&]+)")

# markdownlint の --fix はファイルをシェルから直接書き換えるため、場所を問わず拒否する。
MARKDOWNLINT_FIX_RE = re.compile(
    r"(?:markdownlint\S*.*(?<![\w-])--fix\b)|(?:markdownlint-all\.ps1.*-fix\b)",
    re.IGNORECASE,
)

TEMP_SEGMENT_RE = re.compile(r"(?:^|[\\/])temp(?:-spec-crawl)?(?:[\\/]|$)", re.IGNORECASE)
ABSOLUTE_PATH_RE = re.compile(r"^(?:[A-Za-z]:[\\/]|[\\/])")
NULL_TARGETS = frozenset({"$null", "nul", "/dev/null", "&1", "&2"})
TOKEN_RE = re.compile(r"'([^']*)'|\"([^\"]*)\"|([^\s'\"|;()]+)")
PATH_EXTENSION_RE = re.compile(r"\.[A-Za-z0-9]{1,5}$")
OPENCLAW_CRON_RM_RE = re.compile(
    r"""^\s*ssh\s+(?:-[^\s]+\s+\S+\s+)*pi@192\.168\.68\.71\s+["']openclaw\s+cron\s+rm\s+
    [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\s*["']\s*$""",
    re.IGNORECASE | re.VERBOSE,
)
# 空の .md の新規作成だけを許可する。-Force（既存ファイルを空にする）・内容指定・リダイレクト・後続コマンドは不可。
EMPTY_MARKDOWN_CREATE_RE = re.compile(
    r"^\s*New-Item\s+-ItemType\s+File\s+-Path\s+(?P<quote>['\"]?)"
    r"(?P<path>[^'\"|;&<>]+?\.md)(?P=quote)\s*(?:\|\s*Out-Null\s*)?$",
    re.IGNORECASE,
)
FISHTRACK_TRIP_MEMO_CP_RE = re.compile(
    r'^ssh -i "[^"]*fishtrack_ec2_key" -o StrictHostKeyChecking=no '
    r'ec2-user@52\.197\.69\.195 "cd /home/ec2-user/FishTrack && '
    r'docker cp temp/trip_memo\.md fishtrack-app-1:/app/temp/trip_memo\.md"$',
    re.IGNORECASE,
)

DENY_MESSAGE = (
    "temp/ 以外のファイルへのシェル書き込みを検出したため、コマンドを拒否しました。"
    "変更は StrReplace / Write / Delete で行ってください（シェル経由の変更は Cursor の Review に載らないため）。"
    "一時出力が必要な場合は temp/ へ書いてください。"
)


def is_temp_path(path: str) -> bool:
    return bool(TEMP_SEGMENT_RE.search(path))


def is_absolute_path(path: str) -> bool:
    return bool(ABSOLUTE_PATH_RE.match(path))


def _quoted_mask(command: str) -> list[bool]:
    """引用符の内側（開き・閉じ引用符を含む）を True にした配列を返す。閉じていない引用符は無効として全て False（安全側）。"""
    mask = [False] * len(command)
    quote: str | None = None
    for index, char in enumerate(command):
        if quote is None:
            if char in "\"'":
                quote = char
                mask[index] = True
        else:
            mask[index] = True
            if char == quote:
                quote = None
    if quote is not None:
        return [False] * len(command)
    return mask


def redirect_targets(command: str) -> list[str]:
    """引用符の外にあるリダイレクト（> / >>）の書き込み先だけを返す。引用符内の > は文字列の一部（例: <a@b.com>）なので対象外。"""
    quoted = _quoted_mask(command)
    return [
        match.group(1).strip("\"'")
        for match in REDIRECT_TARGET_RE.finditer(command)
        if not quoted[match.start()]
    ]


def write_path_tokens(command: str) -> list[str]:
    """書き込み先の候補（区切り文字を含む、または拡張子付きのトークン）を返す。"""
    paths: list[str] = []
    for match in TOKEN_RE.finditer(command):
        token = next(group for group in match.groups() if group is not None)
        if not token or token.startswith("-"):
            continue
        if "\\" in token or "/" in token or PATH_EXTENSION_RE.search(token):
            paths.append(token)
    return paths


def is_allowed_remote_openclaw_cron_rm(command: str) -> bool:
    """指定ラズパイ上の OpenClaw cron 削除だけを許可する。"""
    return bool(OPENCLAW_CRON_RM_RE.fullmatch(command))


def is_allowed_fishtrack_trip_memo_cp(command: str) -> bool:
    """FishTrack 本番EC2の一時Tripメモをアプリコンテナへ渡す操作だけを許可する。"""
    return bool(FISHTRACK_TRIP_MEMO_CP_RE.fullmatch(command))


def is_allowed_empty_markdown_create(command: str) -> bool:
    """空の .md を新規作成するだけのコマンドを許可する（既存ファイルは New-Item が失敗する）。"""
    match = EMPTY_MARKDOWN_CREATE_RE.fullmatch(command)
    return bool(match) and ".." not in match.group("path")


def _is_temp_target(target: str, *, cwd_is_temp: bool) -> bool:
    if target.lower() in NULL_TARGETS:
        return True
    if is_temp_path(target):
        return True
    return cwd_is_temp and not is_absolute_path(target)


def should_deny(command: str, cwd: str) -> bool:
    """temp 以外へのシェル書き込み（および markdownlint --fix）なら True を返す。"""
    text = command or ""
    if (
        is_allowed_remote_openclaw_cron_rm(text)
        or is_allowed_fishtrack_trip_memo_cp(text)
        or is_allowed_empty_markdown_create(text)
    ):
        return False
    if MARKDOWNLINT_FIX_RE.search(text):
        return True
    cwd_is_temp = is_temp_path(cwd or "")
    return any(
        _segment_denied(segment, cwd_is_temp=cwd_is_temp)
        for segment in command_segments(text)
        if not is_exempt_git_segment(segment)
    )


def command_segments(command: str) -> list[str]:
    """引用符の外にある区切り（; && || | 改行）でコマンドを分割する。"""
    quoted = _quoted_mask(command)
    segments: list[str] = []
    start = 0
    for match in SEGMENT_SEPARATOR_RE.finditer(command):
        if quoted[match.start()]:
            continue
        segments.append(command[start : match.start()])
        start = match.end()
    segments.append(command[start:])
    return segments


def is_exempt_git_segment(segment: str) -> bool:
    """git の操作は対象外。リダイレクトを含む git 行は通常どおり判定する。"""
    return bool(GIT_SEGMENT_RE.match(segment)) and not redirect_targets(segment)


def _segment_denied(segment: str, *, cwd_is_temp: bool) -> bool:
    if any(not _is_temp_target(target, cwd_is_temp=cwd_is_temp) for target in redirect_targets(segment)):
        return True
    if not WRITE_TOKEN_RE.search(segment):
        return False
    paths = write_path_tokens(segment)
    if not paths:
        return not cwd_is_temp
    return any(not _is_temp_target(path, cwd_is_temp=cwd_is_temp) for path in paths)


def decide(raw_input: str) -> tuple[bool, str]:
    """stdin の JSON 文字列から (拒否するか, コマンド) を返す。解析できなければ許可する。"""
    try:
        payload = json.loads(raw_input)
    except (json.JSONDecodeError, TypeError):
        return False, ""
    if not isinstance(payload, dict):
        return False, ""
    command = payload.get("command")
    cwd = payload.get("cwd") or payload.get("working_directory") or ""
    command_text = command if isinstance(command, str) else ""
    cwd_text = cwd if isinstance(cwd, str) else ""
    return should_deny(command_text, cwd_text), command_text


def _emit(permission: str, user_message: str = "") -> None:
    body: dict[str, str] = {"permission": permission}
    if user_message:
        body["user_message"] = user_message
        body["agent_message"] = user_message
    sys.stdout.buffer.write(json.dumps(body, ensure_ascii=False).encode("utf-8"))


def _run_hook() -> int:
    raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    denied, command = decide(raw)
    if not denied:
        _emit("allow")
        return 0
    _emit("deny", user_message=DENY_MESSAGE)
    sys.stderr.write(f"blocked: {command}\n")
    return 2


SELF_TEST_CASES: tuple[tuple[str, str, bool], ...] = (
    # Obsidian（temp 以外）への書き込みは拒否
    ("Set-Content -Path 'd:\\OneDrive\\アプリ\\remotely-save\\Obsidian\\x.md' -Value a", "", True),
    ("[System.IO.File]::WriteAllText('d:\\OneDrive\\アプリ\\remotely-save\\Obsidian\\x.md', 'a')", "", True),
    ("Copy-Item a.md 'd:\\OneDrive\\アプリ\\remotely-save\\Obsidian\\b.md'", "", True),
    ("echo a > 'd:\\OneDrive\\アプリ\\remotely-save\\Obsidian\\x.md'", "", True),
    # 引用符の外のリダイレクトは、引用符付きの書き込み先でも拒否する
    ("echo a > \"d:\\OneDrive\\アプリ\\remotely-save\\Obsidian\\x.md\"", "", True),
    # 閉じていない引用符は無効扱い（安全側）。引用符の後ろに隠れた書き込みを見逃さない
    ("echo it's > d:\\OneDrive\\アプリ\\remotely-save\\Obsidian\\x.md", "", True),
    # リポジトリ内（temp 以外）への書き込みも拒否
    ("Set-Content -Path src\\x.py -Value a", "d:\\OneDrive\\git_work\\FishTrack", True),
    ("Copy-Item temp\\a.md CursorLog\\x.md", "d:\\OneDrive\\アプリ\\remotely-save\\Obsidian", True),
    ("echo a > scripts\\foo.py", "d:\\OneDrive\\git_work\\dev-workspace", True),
    ("python -c \"open('src/x.py','w').write('a')\"", "d:\\OneDrive\\git_work\\FishTrack", True),
    ("Set-Content -Value a", "d:\\OneDrive\\git_work\\FishTrack", True),
    ("sed -i 's/a/b/' scripts/x.py", "d:\\OneDrive\\git_work\\FishTrack", True),
    # markdownlint --fix は場所を問わず拒否
    ("npx markdownlint-cli2 --fix docs/a.md", "d:\\OneDrive\\git_work\\FishTrack", True),
    ("d:\\OneDrive\\git_work\\dev-workspace\\scripts\\markdownlint-all.ps1 -Fix", "", True),
    # temp 配下への書き込みは許可
    ("python temp\\check.py > temp\\out.txt", "d:\\OneDrive\\git_work\\FishTrack", False),
    ("Set-Content -Path temp\\a.txt -Value b", "d:\\OneDrive\\git_work\\FishTrack", False),
    ("Remove-Item temp\\x.json", "d:\\OneDrive\\git_work\\FishTrack", False),
    ("Set-Content -Path a.txt -Value b", "d:\\OneDrive\\git_work\\FishTrack\\temp", False),
    ("Get-Content x.md > temp\\y.md", "d:\\OneDrive\\git_work\\dev-workspace", False),
    ("python scripts/x.py > $null 2>&1", "d:\\OneDrive\\git_work\\FishTrack", False),
    ("python scripts/x.py 2>&1", "d:\\OneDrive\\git_work\\FishTrack", False),
    # 読み取り・検証・git・docker は許可
    (
        'ssh pi@192.168.68.71 "openclaw cron rm '
        "303bd249-730f-49fb-ae67-dea44bed9cf2"
        '"',
        "d:\\OneDrive\\git_work\\dev-workspace",
        False,
    ),
    (
        'ssh -o BatchMode=yes -o ConnectTimeout=10 pi@192.168.68.71 '
        '"openclaw cron rm c863a9dc-d355-4c0b-bf1b-54ee01ab595f"',
        "d:\\OneDrive\\git_work\\dev-workspace",
        False,
    ),
    (
        'ssh pi@192.168.68.72 "openclaw cron rm '
        "303bd249-730f-49fb-ae67-dea44bed9cf2"
        '"',
        "d:\\OneDrive\\git_work\\dev-workspace",
        True,
    ),
    (
        "openclaw cron rm 303bd249-730f-49fb-ae67-dea44bed9cf2",
        "d:\\OneDrive\\git_work\\dev-workspace",
        True,
    ),
    (
        'ssh -i "C:\\Users\\Akihide\\.ssh\\fishtrack_ec2_key" '
        '-o StrictHostKeyChecking=no ec2-user@52.197.69.195 '
        '"cd /home/ec2-user/FishTrack && docker cp temp/trip_memo.md '
        'fishtrack-app-1:/app/temp/trip_memo.md"',
        "d:\\OneDrive\\git_work\\dev-workspace",
        False,
    ),
    (
        'ssh -i "C:\\Users\\Akihide\\.ssh\\fishtrack_ec2_key" '
        '-o StrictHostKeyChecking=no ec2-user@52.197.69.196 '
        '"cd /home/ec2-user/FishTrack && docker cp temp/trip_memo.md '
        'fishtrack-app-1:/app/temp/trip_memo.md"',
        "d:\\OneDrive\\git_work\\dev-workspace",
        True,
    ),
    ("Get-Content -Raw 'd:\\OneDrive\\アプリ\\remotely-save\\Obsidian\\x.md'", "", False),
    ("npx markdownlint-cli2 CursorLog/2026-10/2026-10-22.md", "d:\\OneDrive\\アプリ\\remotely-save\\Obsidian", False),
    ("git status --short", "d:\\OneDrive\\git_work\\FishTrack", False),
    ("git commit -F temp\\commit_msg.txt", "d:\\OneDrive\\git_work\\FishTrack", False),
    # Cursor が付与する Co-authored-by トレーラの <...> 内の > は引用符内なので誤検知しない
    ("git commit --trailer \"Co-authored-by: Cursor <cursoragent@cursor.com>\" -F temp\\commit_msg.txt", "d:\\OneDrive\\git_work\\FishTrack", False),
    ("npx markdownlint-cli2 docs/a.md", "d:\\OneDrive\\git_work\\FishTrack", False),
    ("docker compose -f docker-compose.yml restart app", "d:\\OneDrive\\git_work\\FishTrack", False),
    # 空の .md の新規作成は許可（-Force・内容指定・リダイレクト・後続コマンドは拒否）
    (
        "New-Item -ItemType File -Path 'd:\\OneDrive\\git_work\\Obsidian\\DevProject\\FishTrack\\spec-crawl\\manufacturers\\deps-rod.md'",
        "d:\\OneDrive\\git_work\\Obsidian",
        False,
    ),
    ("New-Item -ItemType File -Path x.md | Out-Null", "d:\\OneDrive\\git_work\\Obsidian", False),
    ("New-Item -ItemType File -Path x.md -Force", "d:\\OneDrive\\git_work\\Obsidian", True),
    ("New-Item -ItemType File -Path x.md -Value a", "d:\\OneDrive\\git_work\\Obsidian", True),
    ("New-Item -ItemType File -Path x.txt", "d:\\OneDrive\\git_work\\Obsidian", True),
    ("New-Item -ItemType File -Path ..\\..\\x.md", "d:\\OneDrive\\git_work\\Obsidian", True),
    ("New-Item -ItemType File -Path a.md; Set-Content -Path b.md -Value x", "d:\\OneDrive\\git_work\\Obsidian", True),
    ("New-Item -ItemType File -Path a.md > out.txt", "d:\\OneDrive\\git_work\\Obsidian", True),
    # git の操作は対象外（区切りごとに判定。git 行はリダイレクトがなければ除外）
    (
        "cd d:\\OneDrive\\git_work\\dev-workspace; git add -A; git commit -F temp/commit_msg.txt; git push origin main",
        "d:\\OneDrive\\git_work\\dev-workspace",
        False,
    ),
    (
        "cd d:\\OneDrive\\git_work\\dev-workspace; New-Item -ItemType Directory -Force -Path temp/ | Out-Null; git commit -F temp/commit_msg.txt",
        "d:\\OneDrive\\git_work\\dev-workspace",
        False,
    ),
    ("git -C d:\\OneDrive\\git_work\\Obsidian commit -F temp\\x.txt", "d:\\OneDrive\\git_work\\dev-workspace", False),
    ("git status > d:\\OneDrive\\アプリ\\remotely-save\\Obsidian\\x.md", "", True),
    ("git status; Set-Content -Path d:\\OneDrive\\git_work\\Obsidian\\a.md -Value x", "", True),
    ("Set-Content -Value \"x;git status\" d:\\OneDrive\\git_work\\Obsidian\\a.md", "", True),
)


def _self_test() -> int:
    failures: list[str] = []
    for command, cwd, expected in SELF_TEST_CASES:
        actual = should_deny(command, cwd)
        if actual != expected:
            failures.append(f"expected={expected} actual={actual} command={command}")
    for line in failures:
        sys.stdout.write(line + "\n")
    sys.stdout.write(f"self-test: {len(SELF_TEST_CASES) - len(failures)}/{len(SELF_TEST_CASES)} passed\n")
    return 1 if failures else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(_self_test())
    raise SystemExit(_run_hook())
