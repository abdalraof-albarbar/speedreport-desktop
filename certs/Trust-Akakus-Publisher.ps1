# Run once per PC (right-click -> Run with PowerShell, as Administrator).
# Tells Windows to trust the Akakus company code-signing certificate, so SpeedReport.exe shows
# "Akakus Oil Operations - Communications Department" as a verified publisher instead of "Unknown publisher".
# For many PCs: deploy certs\AkakusSpeedReport.cer with Group Policy instead
#   (Computer Configuration > Windows Settings > Security Settings > Public Key Policies >
#    Trusted Publishers and Trusted Root Certification Authorities > Import).
$cer = Join-Path $PSScriptRoot 'AkakusSpeedReport.cer'
if (-not (Test-Path $cer)) { $cer = Join-Path $PSScriptRoot '..\certs\AkakusSpeedReport.cer' }
foreach ($store in 'TrustedPublisher', 'Root') {
  Import-Certificate -FilePath $cer -CertStoreLocation "Cert:\LocalMachine\$store" | Out-Null
}
Write-Host "Done. SpeedReport.exe is now trusted on this PC." -ForegroundColor Green
