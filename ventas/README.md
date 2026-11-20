# Material de ventas — BimBam Buy AI Agent

Kit comercial genérico para vender el agente de soporte y ventas. Contiene el
presupuesto, el sustento técnico/de costos, una presentación y el PDF.

## Archivos

| Archivo | Uso |
|---|---|
| `index.html` | Documento maestro (página web + base del PDF). Editar Aquí el contenido. |
| `presentacion.html` | Deck de reveal.js para pitch (se abre en el navegador). |
| `propuesta.pdf` | PDF listo para enviar, generado desde `index.html`. |
| `build_pdf.ps1` | Regenera `propuesta.pdf` con Chrome/Edge headless. |

## Personalizar por cliente

1. Abrir `ventas/index.html`.
2. Reemplazar los placeholders:
   - `[Nombre del cliente / comercio]`
   - `[DD/MM/AAAA]`
   - `[URL de la tienda]`, `[Logo]`, `[Datos de contacto]`
3. Ajustar precios/costos si el cliente negocia (buscar `USD` en el archivo).
4. Regenerar el PDF (ver abajo).
5. La página se publica sola en GitHub Pages al hacer push a `main` (ver
   `.github/workflows/pages.yml`).

## Regenerar el PDF

Requiere Chrome o Edge instalado.

```powershell
powershell -ExecutionPolicy Bypass -File ventas\build_pdf.ps1
```

Salida: `ventas/propuesta.pdf`.

## Ver la presentación

Abrir `ventas/presentacion.html` en el navegador. Controles: flechas para
navegar, `F` pantalla completa, `P` modo presentador. Con `?print-pdf` en la URL
se puede imprimir/exportar a PDF.

## Deploy en GitHub Pages

El workflow `pages.yml` publica la carpeta `ventas/` como sitio estático. La URL
del sitio es `https://<organizacion>.github.io/<repo>/`.

Requisitos: Pages habilitado en *Settings → Pages* con origen **GitHub Actions**.
