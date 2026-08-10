# -*- coding: utf-8 -*-
"""
GitHub 推送 - urllib 直连, 稳健
"""
import urllib.request, json, base64, subprocess
from pathlib import Path

ROOT = Path(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")
TOKEN = "GITHUB_PAT_PLACEHOLDER_3HiLNCBmRVPmA0WNQvHjy04AZ6f"
REPO = "Nurburgring-Zhang/ComfyUI-PromptLibraryNode"
BRANCH = "master"
REMOTE_HEAD = "880afe4fa134e78373e1248d214f34f0d729b2e1"


def gh(method, path, body=None):
    url = f"https://api.github.com{path}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "User-Agent": "Mavis",
        "Accept": "application/vnd.github.v3+json",
    }
    data = json.dumps(body).encode("utf-8") if body else None
    if body:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


# 拿本地 master 实际 SHA
LOCAL_HEAD = subprocess.run(
    ["git", "rev-parse", "HEAD"],
    capture_output=True, cwd=str(ROOT)
).stdout.decode("utf-8").strip()
print(f"本地 HEAD: {LOCAL_HEAD}")

# Step 1: 拿远端
print("\nStep 1: 拿远端 commit")
remote_commit = gh("GET", f"/repos/{REPO}/git/commits/{REMOTE_HEAD}")
remote_tree = remote_commit["tree"]["sha"]
print(f"  远端 tree: {remote_tree}")

# Step 2: 远端 tree
print("\nStep 2: 拿远端 tree")
tree_resp = gh("GET", f"/repos/{REPO}/git/trees/{remote_tree}?recursive=1")
remote_files = {item["path"]: item["sha"] for item in tree_resp.get("tree", []) if item.get("type") == "blob"}
print(f"  远端文件: {len(remote_files)}")

# Step 3: 本地文件
print("\nStep 3: 拿本地文件")
local_files_raw = subprocess.run(
    ["git", "ls-tree", "-r", "--name-only", "-z", LOCAL_HEAD],
    capture_output=True, cwd=str(ROOT)
).stdout.decode("utf-8")
local_files = [f for f in local_files_raw.split("\x00") if f]
print(f"  本地文件: {len(local_files)}")

# Step 4: 差异
print("\nStep 4: 差异")
# 跳过所有调试/临时文件 - 只推核心生产代码
SKIP_PATTERNS = ["_check", "_test_", "_sample", "_verify", "_inspect",
                 "_show", "_push_", "_e2e_", "_diff", "_find", "_list",
                 "_count", "_gen_simple", "_add", "_phase_a", "_phase_b",
                 "_rebuild", "_ast", "_append", "_update",
                 "_v9", "_v8", "_v7", "_v6", "_v5", "_v10",
                 "_dump", "_batch", "_gen_workflows_v2", "_gen_all_nodes",
                 "_audit_director", "_audit_nodes", "_audit_runtime",
                 "_audit_signature", "_audit_field", "_audit_quality"]
diff_files = []
for f in local_files:
    skip = False
    for p in SKIP_PATTERNS:
        if p in f:
            skip = True
            break
    if skip:
        continue
    blob_sha = subprocess.run(
        ["git", "hash-object", f],
        capture_output=True, cwd=str(ROOT)
    ).stdout.decode("utf-8").strip()
    if remote_files.get(f) != blob_sha:
        diff_files.append(f)
print(f"  差异 (跳过调试文件后): {len(diff_files)}")
for f in diff_files:
    print(f"    {f}")

# Step 5: 创建 blob
print("\nStep 5: 创建 blob")
blob_map = {}
for i, f in enumerate(diff_files):
    full_path = ROOT / f
    content = full_path.read_bytes()
    if len(content) > 50 * 1024 * 1024:
        print(f"  [{i+1}/{len(diff_files)}] {f} SKIP (>{50}MB)")
        continue
    content_b64 = base64.b64encode(content).decode("ascii")
    try:
        blob_data = gh("POST", f"/repos/{REPO}/git/blobs", {
            "content": content_b64,
            "encoding": "base64"
        })
        blob_map[f] = blob_data["sha"]
        print(f"  [{i+1}/{len(diff_files)}] {f} -> {blob_data['sha'][:12]}")
    except urllib.error.HTTPError as e:
        print(f"  [{i+1}/{len(diff_files)}] {f} FAIL: HTTP {e.code}")
        # 试 utf-8 raw
        try:
            text_content = content.decode("utf-8", errors="replace")
            blob_data = gh("POST", f"/repos/{REPO}/git/blobs", {
                "content": text_content,
                "encoding": "utf-8"
            })
            blob_map[f] = blob_data["sha"]
            print(f"    [retry utf-8 OK] {f} -> {blob_data['sha'][:12]}")
        except Exception as e2:
            print(f"    [retry FAIL] {f}: {e2}")
            raise

# Step 6: 新 tree
print("\nStep 6: 创建新 tree")
new_tree_items = []
for item in tree_resp.get("tree", []):
    path = item["path"]
    if path in blob_map:
        new_tree_items.append({
            "path": path,
            "mode": item.get("mode", "100644"),
            "type": "blob",
            "sha": blob_map[path]
        })
    else:
        new_tree_items.append({
            "path": path,
            "mode": item.get("mode", "100644"),
            "type": item.get("type", "blob"),
            "sha": item["sha"]
        })
for f in diff_files:
    if f not in remote_files:
        new_tree_items.append({
            "path": f,
            "mode": "100644",
            "type": "blob",
            "sha": blob_map[f]
        })
new_tree = gh("POST", f"/repos/{REPO}/git/trees", {
    "base_tree": remote_tree,
    "tree": new_tree_items
})
print(f"  新 tree: {new_tree['sha']}")

# Step 7: commit
print("\nStep 7: 创建 commit")
commit_msg = subprocess.run(
    ["git", "log", "-1", "--format=%B", LOCAL_HEAD],
    capture_output=True, cwd=str(ROOT)
).stdout.decode("utf-8").strip()
new_commit = gh("POST", f"/repos/{REPO}/git/commits", {
    "message": commit_msg,
    "tree": new_tree["sha"],
    "parents": [REMOTE_HEAD],
    "author": {"name": "Mavis", "email": "Mavis@minimax.local"}
})
print(f"  新 commit: {new_commit['sha']}")

# Step 8: patch ref
print("\nStep 8: 更新 master ref")
ref_data = gh("PATCH", f"/repos/{REPO}/git/refs/heads/{BRANCH}", {
    "sha": new_commit["sha"],
    "force": True
})
print(f"\n✅ 推送成功! master HEAD: {ref_data['object']['sha']}")
