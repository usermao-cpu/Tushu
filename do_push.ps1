$git = "D:\Git\bin\git.exe"
$envPath = "$env:USERPROFILE\.git-credentials"
if (-not (Test-Path $envPath)) {
    Set-Content -Path $envPath -Value "https://usermao-cpu:asd09800980@github.com" -Force
}
& $git config credential.helper store
& $git pull origin main --allow-unrelated-histories
if ($?) {
    & $git push -u origin main
}
