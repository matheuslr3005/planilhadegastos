"""Renderiza o xlsx em PDF/PNG (LibreOffice) para conferência visual.
Uso: python gen/tools/preview.py arquivo.xlsx "texto do título da aba" [dpi]  -> imprime caminho do PNG"""
import sys, os, subprocess, shutil, tempfile
src, needle = sys.argv[1], sys.argv[2]
dpi = sys.argv[3] if len(sys.argv) > 3 else "75"
out = os.environ.get("PREVIEW_DIR", "/tmp/preview")
os.makedirs(out, exist_ok=True)
base = os.path.splitext(os.path.basename(src))[0]
shutil.copy(src, f"{out}/{base}.xlsx")
env = dict(os.environ, SAL_USE_VCLPLUGIN="svp")
subprocess.run(["soffice", "--headless", "--norestore", "-env:UserInstallation=file:///tmp/lo_prof_prev",
                "--convert-to", "pdf", "--outdir", out, f"{out}/{base}.xlsx"], env=env, capture_output=True, timeout=170)
pdf = f"{out}/{base}.pdf"
n = int([l for l in subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout.splitlines() if l.startswith("Pages")][0].split()[1])
pages = []
for p in range(1, n + 1):
    t = subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), "-layout", pdf, "-"], capture_output=True, text=True).stdout
    if needle.lower() in t.lower():
        pages.append(p)
if not pages:
    print("não achei", needle, "em", n, "páginas"); sys.exit(1)
p = pages[0]
tag = needle.replace(" ", "_")[:20]
subprocess.run(["pdftoppm", "-r", dpi, "-f", str(p), "-l", str(p + int(os.environ.get('NPAGES', '0'))), "-png", pdf, f"{out}/{base}_{tag}"])
print([f for f in sorted(os.listdir(out)) if f.startswith(f"{base}_{tag}")], "páginas:", pages[:5])
