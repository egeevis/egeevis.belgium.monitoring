# Local Test (Deploy'suz)

Bu proje framework gerektirmiyor; en doğru ifade:
- `local dev server`
- `yerel gelistirme ortami`

## Hizli Baslatma

1. `start-local.bat` dosyasini calistirin.
2. Tarayicida `http://127.0.0.1:8080` adresini acin.

## Alternatif (PowerShell)

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-local-server.ps1 -Port 8080
```

## Neden gerekiyor?

`index.html` icinde `fetch("data.json")` var. Bu sebeple dosyayi `file://` ile acmak yerine HTTP sunucu uzerinden acmak gerekir.

## Not

- Sunucuyu kapatmak icin terminalde `Ctrl+C`.
- Guncel veri icin `data.json`'i `fetch_rss.py` uretir. Bu makinede Python yoksa, gecici olarak mevcut `data.json` ile UI test edebilirsiniz.
