$filePath = "C:\Users\DELL\OneDrive\Escritorio\Proyecto\proyecto\static\uploads\Setter2.mp4"
$boundary = [System.Guid]::NewGuid().ToString()
$fileBytes = [System.IO.File]::ReadAllBytes($filePath)
$contentType = "multipart/form-data; boundary=$boundary"

# Construye el cuerpo manualmente
$body = @"
--$boundary
Content-Disposition: form-data; name="video"; filename="Setter2.mp4"
Content-Type: video/mp4

"@ + [System.Text.Encoding]::UTF8.GetString($fileBytes) + @"
--$boundary--
"@

# Envía la petición
Invoke-WebRequest -Uri "http://localhost:5000/analisis/video/Colocador" -Method Post -Body $body -ContentType $contentType