import subprocess
from pathlib import Path
ROOT = Path(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")
# Check current remote HEAD
ps_script = '''
$headers = @{ 'Authorization' = 'token GITHUB_PAT_PLACEHOLDER_3HiLNCBmRVPmA0WNQvHjy04AZ6f'; 'User-Agent' = 'Mavis' }

# Get master ref
try {
    $r = Invoke-RestMethod -Uri "https://api.github.com/repos/Nurburgring-Zhang/ComfyUI-PromptLibraryNode/git/refs/heads/master" -Headers $headers -UseBasicParsing
    Write-Output "MASTER_REF: $($r.object.sha)"
} catch {
    Write-Output "MASTER_FAIL: $($_.Exception.Message)"
}

# Get main ref
try {
    $r = Invoke-RestMethod -Uri "https://api.github.com/repos/Nurburgring-Zhang/ComfyUI-PromptLibraryNode/git/refs/heads/main" -Headers $headers -UseBasicParsing
    Write-Output "MAIN_REF: $($r.object.sha)"
} catch {
    Write-Output "MAIN_FAIL: $($_.Exception.Message)"
}
'''
ps_file = ROOT / "_check_remote.ps1"
ps_file.write_text(ps_script, encoding="utf-8")
result = subprocess.run(
    ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(ps_file)],
    capture_output=True
)
print(result.stdout.decode("utf-8", errors="replace").strip())
print(result.stderr.decode("utf-8", errors="replace").strip()[:200])
ps_file.unlink()
