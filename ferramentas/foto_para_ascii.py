"""Converte uma foto em arte ASCII para o cartão do perfil (uso único, precisa de Pillow).

Uso:
  pip install pillow
  python ferramentas/foto_para_ascii.py foto.jpg ascii.txt --corte 75,55,295,345

--corte x0,y0,x1,y1  recorta a foto antes (deixe a proporção ~3:4)
--piso N             tons abaixo de N viram espaço (limpa fundo escuro)  [20]
--gama G             < 1 clareia os meios-tons, > 1 escurece               [0.45]
"""
import argparse
from PIL import Image, ImageOps, ImageFilter

# do mais "vazio" ao mais "cheio"
RAMPA = " .'`^,:;!i|lj[{kmH%#M@"


def converter(caminho, colunas, linhas, corte, piso, gama):
    img = Image.open(caminho).convert("L")
    if corte:
        img = img.crop(corte)
    img = ImageOps.autocontrast(img, cutoff=1)
    img = img.point(lambda v: 0 if v < piso else int(255 * ((v - piso) / (255 - piso)) ** gama))
    img = img.resize((colunas, linhas), Image.LANCZOS).filter(ImageFilter.SHARPEN)
    px = img.load()
    return "\n".join(
        "".join(RAMPA[px[x, y] * (len(RAMPA) - 1) // 255] for x in range(colunas)).rstrip()
        for y in range(linhas)
    )


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("foto")
    ap.add_argument("saida")
    ap.add_argument("--colunas", type=int, default=40)
    ap.add_argument("--linhas", type=int, default=25)
    ap.add_argument("--corte", type=lambda s: tuple(int(v) for v in s.split(",")))
    ap.add_argument("--piso", type=int, default=20)
    ap.add_argument("--gama", type=float, default=0.45)
    a = ap.parse_args()
    arte = converter(a.foto, a.colunas, a.linhas, a.corte, a.piso, a.gama)
    with open(a.saida, "w", encoding="utf-8") as f:
        f.write(arte + "\n")
    print(arte)
