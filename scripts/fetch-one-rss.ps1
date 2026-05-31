param(
  [string]$Url = "https://feeds.bbci.co.uk/news/world/rss.xml",
  [string]$Category = "officials",
  [string]$FeedName = "Test RSS (Tek Kaynak)",
  [int]$MaxItems = 15
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$dataPath = Join-Path $root "data.json"

if (-not (Test-Path $dataPath)) {
  throw "data.json bulunamadi: $dataPath"
}

Write-Host "RSS cekiliyor: $Url"

$resp = Invoke-WebRequest -Uri $Url -Method Get -UseBasicParsing
[xml]$rss = $resp.Content
$items = @()

foreach ($item in $rss.rss.channel.item | Select-Object -First $MaxItems) {
  $title = if ($item.title -and $item.title.InnerText) { [string]$item.title.InnerText } else { [string]$item.title }
  $link = if ($item.link -and $item.link.InnerText) { [string]$item.link.InnerText } else { [string]$item.link }
  $pubDate = if ($item.pubDate -and $item.pubDate.InnerText) { [string]$item.pubDate.InnerText } else { [string]$item.pubDate }

  $iso = $null
  if ($pubDate) {
    try {
      $iso = (Get-Date $pubDate).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    } catch {
      $iso = $null
    }
  }

  if ([string]::IsNullOrWhiteSpace($title) -or [string]::IsNullOrWhiteSpace($link)) {
    continue
  }

  $items += [PSCustomObject]@{
    title = $title
    summary = "Yerel RSS test kaydi (tek kaynak)."
    link = $link
    date = $iso
    source = [string]$rss.rss.channel.title
    feed = $FeedName
  }
}

if ($items.Count -eq 0) {
  throw "RSS'ten item okunamadi."
}

$jsonRaw = Get-Content -Raw -Encoding UTF8 $dataPath
$data = $jsonRaw | ConvertFrom-Json

if (-not $data.data) {
  $data | Add-Member -NotePropertyName data -NotePropertyValue (@{})
}
if (-not $data.data.$Category) {
  $data.data | Add-Member -NotePropertyName $Category -NotePropertyValue (@{})
}

$data.data.$Category | Add-Member -Force -NotePropertyName $FeedName -NotePropertyValue $items

$sorted = $items | Sort-Object { if ($_.date) { [datetime]$_.date } else { [datetime]::MinValue } } -Descending
$data.data.$Category | Add-Member -Force -NotePropertyName "Toplu (Tekrarsiz)" -NotePropertyValue $sorted

$data.updated = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

$out = $data | ConvertTo-Json -Depth 15
Set-Content -Path $dataPath -Value $out -Encoding UTF8

Write-Host "Tamamlandi. $($items.Count) kayit yazildi -> $Category / $FeedName"
