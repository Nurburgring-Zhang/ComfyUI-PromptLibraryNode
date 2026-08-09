"""
推送本地 master HEAD 到 GitHub (完整模式: blob → tree → commit → ref)
"""
import os
import sys
import json
import time
import urllib.request
import urllib.error
import subprocess

TOKEN = os.environ.get("GH_TOKEN", "ghp_GITHUB_PERSONAL_ACCESS_TOKEN_HERE")  # 真实 token 留作环境变量
REPO = "Nurburgring-Zhang/ComfyUI-PromptLibraryNode"
REPO_DIR = r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode"

# 跳过调试文件模式 (只跳过临时调试, 保留 tests/ 测试文件)
SKIP_PATTERNS = [
    "_check_", "_audit_", "_sample_", "_verify_",
    "audit.log", "audit.err", "audit_stdout.txt", "audit_stderr.txt",
]
# _test_ 在 tests/ 目录下保留 (正式测试)
# 但根目录的 _test_ 跳过
SKIP_ROOT_PATTERNS = ["_test_"]


def api_request(method, path, data=None):
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }
    if data is not None:
        data = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        data=data, method=method, headers=headers,
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        print(f"ERROR {e.code} {path}: {err_body[:500]}")
        raise


def should_skip(path):
    base = os.path.basename(path)
    # 根目录的 _test_ 跳过, tests/ 下保留
    is_root = "/" not in path.replace("\\", "/")
    if is_root and any(pat in base for pat in SKIP_ROOT_PATTERNS):
        return True
    for pat in SKIP_PATTERNS:
        if pat in base:
            return True
    return False


# 1. 获取 master latest commit
ref = api_request("GET", f"/repos/{REPO}/git/ref/heads/master")
latest_sha = ref["object"]["sha"]
print("Remote master HEAD: " + latest_sha)

# 2. 获取本地 HEAD
local_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_DIR).decode().strip()
print("Local HEAD: " + local_head)

# 3. 获取本地最新 commit 涉及的所有文件 (替代 diff 范围)
# 列出从上一个 commit 到当前的所有变更
# 但因为本地没 fetch 远程, 用 git show HEAD 拿当前 commit 的文件
result = subprocess.run(
    ["git", "show", "--name-only", "--format=", "HEAD"],
    cwd=REPO_DIR, capture_output=True, text=True,
)
diff_files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
print(f"Files to push: {len(diff_files)}")

# 4. 上传每个文件作为 blob
def upload_blob(path):
    full = os.path.join(REPO_DIR, path)
    if not os.path.isfile(full):
        return None
    with open(full, "rb") as f:
        content = f.read()
    # base64 encode
    import base64
    encoded = base64.b64encode(content).decode("ascii")
    blob = api_request("POST", f"/repos/{REPO}/git/blobs", {
        "content": encoded,
        "encoding": "base64",
    })
    return blob["sha"]


blobs = {}
for f in diff_files:
    if should_skip(f):
        print(f"SKIP: {f}")
        continue
    try:
        sha = upload_blob(f)
        if sha:
            blobs[f] = sha
            print(f"  blob: {f} -> {sha[:8]}")
    except Exception as e:
        print(f"  ERROR blob {f}: {e}")
        sys.exit(1)

# 5. 创建新 tree (recursive)
def build_tree(path, blobs):
    """递归构建 tree 结构"""
    items = []
    full = os.path.join(REPO_DIR, path)
    if os.path.isfile(full):
        return None
    for entry in sorted(os.listdir(full)):
        entry_path = os.path.join(path, entry).replace("\\", "/")
        rel_path = entry_path  # 已经是相对路径
        if should_skip(entry):
            continue
        full_entry = os.path.join(REPO_DIR, entry_path)
        if os.path.isfile(full_entry):
            if rel_path in blobs:
                items.append({
                    "path": entry,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blobs[rel_path],
                })
        else:
            sub_tree_sha = build_tree(entry_path, blobs)
            if sub_tree_sha:
                items.append({
                    "path": entry,
                    "mode": "040000",
                    "type": "tree",
                    "sha": sub_tree_sha,
                })
    if not items:
        return None
    tree = api_request("POST", f"/repos/{REPO}/git/trees", {
        "base_tree": api_request("GET", f"/repos/{REPO}/git/commits/{latest_sha}")["tree"]["sha"],
        "tree": items,
    })
    return tree["sha"]


new_tree_sha = build_tree("", blobs)
print(f"New tree SHA: {new_tree_sha}")

# 6. 获取本地 commit message
local_msg = subprocess.check_output(["git", "log", "-1", "--format=%B", local_head], cwd=REPO_DIR).decode().strip()

# 7. 创建 commit
new_commit = api_request("POST", f"/repos/{REPO}/git/commits", {
    "message": local_msg,
    "tree": new_tree_sha,
    "parents": [latest_sha],
})
print(f"New commit SHA: {new_commit['sha']}")

# 8. Update master ref
api_request("PATCH", f"/repos/{REPO}/git/refs/heads/master", {
    "sha": new_commit["sha"],
})
print("master updated!")

# 9. Wait and verify
import time
time.sleep(3)
new_ref = api_request("GET", f"/repos/{REPO}/git/ref/heads/master")
print("master HEAD now: " + new_ref["object"]["sha"])
