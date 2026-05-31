param(
  [int]$Port = 8080,
  [string]$HostName = "127.0.0.1"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$ip = [System.Net.IPAddress]::Parse($HostName)
$listener = [System.Net.Sockets.TcpListener]::new($ip, $Port)
$listener.Start()

Write-Host "Belcika Izleme local server basladi: http://${HostName}:${Port}/"
Write-Host "Kapatmak icin Ctrl+C"

$mimeMap = @{
  ".html" = "text/html; charset=utf-8"
  ".css"  = "text/css; charset=utf-8"
  ".js"   = "application/javascript; charset=utf-8"
  ".json" = "application/json; charset=utf-8"
  ".txt"  = "text/plain; charset=utf-8"
  ".svg"  = "image/svg+xml"
  ".png"  = "image/png"
  ".jpg"  = "image/jpeg"
  ".jpeg" = "image/jpeg"
  ".ico"  = "image/x-icon"
}

function Send-Response($stream, [int]$statusCode, [string]$statusText, [byte[]]$body, [string]$contentType) {
  $headers = @(
    "HTTP/1.1 $statusCode $statusText",
    "Content-Type: $contentType",
    "Content-Length: $($body.Length)",
    "Connection: close",
    "Cache-Control: no-cache",
    ""
    ""
  ) -join "`r`n"

  $headerBytes = [System.Text.Encoding]::ASCII.GetBytes($headers)
  $stream.Write($headerBytes, 0, $headerBytes.Length)
  if ($body.Length -gt 0) {
    $stream.Write($body, 0, $body.Length)
  }
}

try {
  while ($true) {
    $client = $listener.AcceptTcpClient()
    try {
      $stream = $client.GetStream()
      $reader = New-Object System.IO.StreamReader($stream, [System.Text.Encoding]::ASCII, $false, 1024, $true)

      $requestLine = $reader.ReadLine()
      if ([string]::IsNullOrWhiteSpace($requestLine)) {
        $empty = [byte[]]::new(0)
        Send-Response $stream 400 "Bad Request" $empty "text/plain; charset=utf-8"
        continue
      }

      # Read and ignore the rest of headers
      while (($line = $reader.ReadLine()) -ne "") { }

      $parts = $requestLine.Split(' ')
      if ($parts.Length -lt 2 -or $parts[0] -ne "GET") {
        $msg = [System.Text.Encoding]::UTF8.GetBytes("Only GET supported")
        Send-Response $stream 405 "Method Not Allowed" $msg "text/plain; charset=utf-8"
        continue
      }

      $rawPath = $parts[1]
      $pathOnly = $rawPath.Split('?')[0]
      $path = [System.Uri]::UnescapeDataString($pathOnly.TrimStart('/'))
      if ([string]::IsNullOrWhiteSpace($path)) {
        $path = "index.html"
      }

      $fullPath = [System.IO.Path]::GetFullPath((Join-Path $root $path))
      $rootFull = [System.IO.Path]::GetFullPath($root)

      if (-not $fullPath.StartsWith($rootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        $msg = [System.Text.Encoding]::UTF8.GetBytes("403 Forbidden")
        Send-Response $stream 403 "Forbidden" $msg "text/plain; charset=utf-8"
        continue
      }

      if (Test-Path $fullPath -PathType Leaf) {
        $ext = [System.IO.Path]::GetExtension($fullPath).ToLowerInvariant()
        $contentType = if ($mimeMap.ContainsKey($ext)) { $mimeMap[$ext] } else { "application/octet-stream" }
        $bytes = [System.IO.File]::ReadAllBytes($fullPath)
        Send-Response $stream 200 "OK" $bytes $contentType
      } else {
        $msg = [System.Text.Encoding]::UTF8.GetBytes("404 Not Found")
        Send-Response $stream 404 "Not Found" $msg "text/plain; charset=utf-8"
      }
    }
    finally {
      $client.Close()
    }
  }
}
finally {
  $listener.Stop()
}
