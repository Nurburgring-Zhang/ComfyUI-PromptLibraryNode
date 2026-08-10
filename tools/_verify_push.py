import subprocess
from pathlib import Path
ROOT = Path(r"D:\minimax\comfyui-prompt-node-extracted\ComfyUI-PromptLibraryNode")

ps = '''
$h = @{ 'Authorization' = 'token GITHUB_PAT_PLACEHOLDER_3HiLNCBmRVPmA0WNQvHjy04AZ6f'; 'User-Agent' = 'Mavis' }
$r = Invoke-RestMethod -Uri "https://api.github.com/repos/Nurburgring-Zhang/ComfyUI-PromptLibraryNode/git/refs/heads/master" -Headers $h -UseBasicParsing
Write-Output "MASTER_SHA: $($r.object.sha)"
Write-Output "MASTER_URL: $($r.object.url)"

# Get the commit details
$c = Invoke-RestMethod -Uri "https://api.github.com/repos/Nurburgring-Zhang/ComfyUI-PromptLibraryNode/git/commits/$($r.object.sha)" -Headers $h -UseBasicParsing
Write-Output "MESSAGE: $($c.message.Substring(0, [Math]::Min(200, $c.message.Length)))"
Write-Output "FILES_CHANGED: $($c.files.Count)"
foreach ($f in $c.files) {
    Write-Output "  $($f.status): $($f.filename) ($($f.additions)+$($f.deletions)-)"
}
'''
ps_file = ROOT / "_verify.ps1"
ps_file.write_text(ps, encoding="utf-8")
r = subprocess.run(
    ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(ps_file)],
    capture_output=True
)
print(r.stdout.decode("utf-8", errors="replace").strip())
ps_file.unlink()
