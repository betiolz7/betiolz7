"""Gera dark_mode.svg e light_mode.svg no estilo "neofetch" para o README do perfil.

Só usa a biblioteca padrão do Python. Roda no GitHub Actions todo dia
(.github/workflows/perfil.yml) para atualizar idade e estatísticas.

Local:  GITHUB_TOKEN=<token> python gerar_perfil.py
"""
import datetime as dt
import json
import os
import time
import urllib.error
import urllib.request
from html import escape

# ───────────────────────── edite aqui ─────────────────────────
USUARIO = "betiolz7"
TITULO = "gabriel@betiol"

# Sua data de nascimento (AAAA, MM, DD) para o "Uptime" mostrar sua idade.
# Deixe None para mostrar há quanto tempo você tem conta no GitHub.
NASCIMENTO = dt.date(2008, 5, 12)  # 12/05/2008

INFO = [
    (["OS"], "Windows 10, Linux (Docker)"),
    (["Uptime"], "{uptime}"),
    (["Host"], "Krolik"),
    (["Kernel"], "Full-Stack Developer"),
    (["IDE"], "VSCode, Visual Studio"),
    None,
    (["Languages", "Programming"], "C#, Python, TypeScript, JS"),
    (["Languages", "Computer"], "HTML, CSS, SQL, JSON, YAML"),
    (["Languages", "Real"], "Português, English"),
    None,
    (["Quests", "Main"], "Full-Stack & SaaS"),
    (["Quests", "Side"], "Achar o ; que dropou o banco"),
]

CONTATO = [
    (["Location"], "Ribeirão Preto - SP, Brasil"),
    (["Founder"], "Koda Labs, Grid Company"),
    (["Instagram", "Koda"], "@kodalabs.solutions"),
    (["Instagram", "Grid"], "@grid.companybr"),
    (["GitHub"], "betiolz7"),
]
# ──────────────────────────────────────────────────────────────

LARGURA = 58          # caracteres por linha da coluna da direita
API = "https://api.github.com"
TEMAS = {
    "dark_mode.svg": dict(bg="#161b22", txt="#c9d1d9", key="#ffa657", value="#a5d6ff",
                          add="#3fb950", dele="#f85149", cc="#616e7f"),
    "light_mode.svg": dict(bg="#f6f8fa", txt="#24292f", key="#953800", value="#0a3069",
                           add="#1a7f37", dele="#cf222e", cc="#c2cfde"),
}


# ───────────────────────── GitHub ─────────────────────────
def get(caminho):
    req = urllib.request.Request(API + caminho, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        corpo = r.read()
        return r.status, (json.loads(corpo) if corpo else None)


def estatisticas():
    _, user = get(f"/users/{USUARIO}")
    repos, pagina = [], 1
    while True:
        _, lote = get(f"/users/{USUARIO}/repos?per_page=100&type=owner&page={pagina}")
        repos += [r for r in lote if not r["fork"]]
        if len(lote) < 100:
            break
        pagina += 1

    commits = adicoes = remocoes = 0
    pendentes = [r["full_name"] for r in repos]
    for tentativa in range(8):  # a API responde 202 enquanto calcula
        faltando = []
        for nome in pendentes:
            try:
                status, dados = get(f"/repos/{nome}/stats/contributors")
            except urllib.error.HTTPError:
                continue
            if status == 202:
                faltando.append(nome)
                continue
            for autor in dados or []:
                if (autor.get("author") or {}).get("login", "").lower() == USUARIO.lower():
                    commits += autor["total"]
                    adicoes += sum(w["a"] for w in autor["weeks"])
                    remocoes += sum(w["d"] for w in autor["weeks"])
        pendentes = faltando
        if not pendentes:
            break
        time.sleep(3 + tentativa * 2)
    if pendentes:
        print("Sem estatística ainda (rode de novo depois):", ", ".join(pendentes))

    return dict(
        repos=user["public_repos"],
        stars=sum(r["stargazers_count"] for r in repos),
        followers=user["followers"],
        commits=commits,
        add=adicoes,
        dele=remocoes,
        criado=dt.date.fromisoformat(user["created_at"][:10]),
    )


def tempo_desde(inicio, hoje):
    anos = hoje.year - inicio.year
    meses = hoje.month - inicio.month
    dias = hoje.day - inicio.day
    if dias < 0:
        meses -= 1
        mes_ant = (hoje.replace(day=1) - dt.timedelta(days=1))
        dias += mes_ant.day
    if meses < 0:
        anos -= 1
        meses += 12
    p = lambda n, s, pl: f"{n} {s if n == 1 else pl}"
    return f"{p(anos, 'ano', 'anos')}, {p(meses, 'mês', 'meses')}, {p(dias, 'dia', 'dias')}"


# ───────────────────────── SVG ─────────────────────────
def chave(keys):
    """Renderiza Chave.Sub: e devolve (svg, comprimento)."""
    svg = '<tspan class="cc">.</tspan>'.join(f'<tspan class="key">{escape(k)}</tspan>' for k in keys)
    return svg + ":", len(".".join(keys)) + 1


def campo(keys, valor, largura, classe="value"):
    k_svg, k_len = chave(keys)
    pontos = max(1, largura - k_len - len(valor) - 2)
    return (k_svg + f'<tspan class="cc"> {"." * pontos} </tspan>'
            + f'<tspan class="{classe}">{escape(valor)}</tspan>')


def linha_info(keys, valor):
    return '<tspan class="cc">. </tspan>' + campo(keys, valor, LARGURA - 2)


def cabecalho(texto):
    return f"{escape(texto)}" + f' -{"—" * (LARGURA - len(texto) - 7)}-—-'


def svg(tema, arte, s, uptime):
    c = TEMAS[tema]
    fmt = lambda n: f"{n:,}".replace(",", ".")
    loc = s["add"] - s["dele"]

    direita = [cabecalho(TITULO)]
    for item in INFO:
        direita.append('<tspan class="cc">. </tspan>' if item is None
                       else linha_info(item[0], item[1].format(uptime=uptime)))
    direita += ["", cabecalho("- Contact")]
    direita += [linha_info(k, v) for k, v in CONTATO]
    direita += ["", cabecalho("- GitHub Stats")]

    meia = (LARGURA - 5) // 2
    direita.append('<tspan class="cc">. </tspan>' + campo(["Repos"], fmt(s["repos"]), meia)
                   + '<tspan class="cc"> | </tspan>' + campo(["Stars"], fmt(s["stars"]), LARGURA - 5 - meia))
    direita.append('<tspan class="cc">. </tspan>' + campo(["Commits"], fmt(s["commits"]), meia)
                   + '<tspan class="cc"> | </tspan>' + campo(["Followers"], fmt(s["followers"]), LARGURA - 5 - meia))
    extra = f' ( +{fmt(s["add"])}, -{fmt(s["dele"])} )'
    k_svg, k_len = chave(["Lines of Code on GitHub"])
    pontos = max(1, LARGURA - 2 - k_len - len(fmt(loc)) - len(extra) - 2)
    direita.append('<tspan class="cc">. </tspan>' + k_svg
                   + f'<tspan class="cc"> {"." * pontos} </tspan><tspan class="value">{fmt(loc)}</tspan>'
                   + f' ( <tspan class="addColor">+{fmt(s["add"])}</tspan>, '
                   + f'<tspan class="delColor">-{fmt(s["dele"])}</tspan> )')

    linhas_arte = "\n".join(
        f'<tspan x="15" y="{30 + i * 20}">{escape(l)}</tspan>' for i, l in enumerate(arte)
    )
    linhas_dir = "\n".join(
        f'<tspan x="390" y="{30 + i * 20}">{l}</tspan>' for i, l in enumerate(direita) if l
    )
    altura = 30 + max(len(arte), len(direita)) * 20
    return f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="985px" height="{altura}px" font-size="16px">
<style>
@font-face {{ src: local('Consolas'), local('Consolas Bold'); font-family: 'ConsolasFallback'; font-display: swap; -webkit-size-adjust: 109%; size-adjust: 109%; }}
.key {{fill: {c['key']};}}
.value {{fill: {c['value']};}}
.addColor {{fill: {c['add']};}}
.delColor {{fill: {c['dele']};}}
.cc {{fill: {c['cc']};}}
text, tspan {{white-space: pre;}}
</style>
<rect width="985px" height="{altura}px" fill="{c['bg']}" rx="15"/>
<text x="15" y="30" fill="{c['txt']}" class="ascii">
{linhas_arte}
</text>
<text x="390" y="30" fill="{c['txt']}">
{linhas_dir}
</text>
</svg>
"""


def main():
    pasta = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(pasta, "ascii.txt"), encoding="utf-8") as f:
        arte = f.read().rstrip("\n").split("\n")
    s = estatisticas()
    hoje = dt.date.today()
    uptime = tempo_desde(NASCIMENTO or s["criado"], hoje)
    for tema in TEMAS:
        with open(os.path.join(pasta, tema), "w", encoding="utf-8") as f:
            f.write(svg(tema, arte, s, uptime))
    print("OK:", {k: v for k, v in s.items() if k != "criado"}, "| uptime:", uptime)


if __name__ == "__main__":
    main()
