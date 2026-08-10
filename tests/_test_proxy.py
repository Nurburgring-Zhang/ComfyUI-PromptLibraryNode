import subprocess
# 1. 测代理本身
r = subprocess.run(
    ['powershell', '-NoProfile', '-NonInteractive', '-Command',
     'Write-Output (Test-NetConnection -ComputerName 127.0.0.1 -Port 31181 -WarningAction SilentlyContinue).TcpTestSucceeded'],
    capture_output=True, text=True
)
print(f'代理端口 31181 测试: {r.stdout.strip()}')

# 2. 测代理连 GitHub
ps_test = '''
try {
    $r = Invoke-WebRequest -Uri "https://api.github.com" -Proxy "http://127.0.0.1:31181" -UseBasicParsing -TimeoutSec 15
    Write-Output $r.StatusCode
} catch {
    Write-Output "FAIL: $($_.Exception.Message)"
}
'''
r = subprocess.run(
    ['powershell', '-NoProfile', '-NonInteractive', '-Command', ps_test],
    capture_output=True, text=True
)
print(f'代理连 GitHub: {r.stdout.strip()[:200]}')

# 3. 不走代理直连
ps_test2 = '''
try {
    $r = Invoke-WebRequest -Uri "https://api.github.com" -UseBasicParsing -TimeoutSec 15
    Write-Output $r.StatusCode
} catch {
    Write-Output "FAIL: $($_.Exception.Message)"
}
'''
r = subprocess.run(
    ['powershell', '-NoProfile', '-NonInteractive', '-Command', ps_test2],
    capture_output=True, text=True
)
print(f'直连 GitHub: {r.stdout.strip()[:200]}')
