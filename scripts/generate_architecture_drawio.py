#!/usr/bin/env python3
"""
Gera draw.io com:
  - 00-Visao-Geral (batch + online na MESMA página — use na apresentação)
  - 01-Batch, 02-Online, 03-Mapa-Nuvem (abas separadas)
+ arquivos individuais .drawio por fluxo
"""
from __future__ import annotations

import html
import uuid
from datetime import datetime, timezone
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "arquitetura"

AZURE, AZURE_BG = "#0078D4", "#E8F4FC"
AWS, AWS_BG = "#232F3E", "#FFF4E5"
LOCAL, LOCAL_BG = "#107C10", "#E8F5E9"
GREEN_STEP = "#107C10"
BATCH_HDR, BATCH_BG, BATCH_BORDER = "#B8860B", "#FFFBEB", "#D4A017"
ONLINE_HDR, ONLINE_BG, ONLINE_BORDER = "#0078D4", "#F0F7FC", "#5EA0EF"
STORE, STORE_BORDER = "#E1DFDD", "#8A8886"
ARROW = "#323130"
FADED = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#F3F2F1;strokeColor=#C8C6C4;"
    "strokeWidth=1;dashed=1;dashPattern=8 6;opacity=40;fontFamily=Segoe UI;"
    "fontSize=11;align=center;verticalAlign=middle;fontColor=#A19F9D;"
)
FADED_EDGE = f"strokeColor=#C8C6C4;strokeWidth=1;dashed=1;dashPattern=8 6;opacity=40;"
DEMO_EDGE = f"strokeColor={LOCAL};strokeWidth=3;endArrow=blockThin;endFill=1;"


def esc(s: str) -> str:
    return html.escape(s, quote=True)


class G:
    def __init__(self) -> None:
        self.n = 0
        self.cells: list[str] = []
        self.ids: dict[str, str] = {}

    def nid(self, key: str | None = None) -> str:
        if key and key in self.ids:
            return self.ids[key]
        self.n += 1
        s = str(self.n)
        if key:
            self.ids[key] = s
        return s

    def c(self, pid: str, val: str, x: float, y: float, w: float, h: float, style: str, key: str | None = None) -> str:
        i = self.nid(key)
        self.cells.append(
            f'        <mxCell id="{i}" value="{esc(val)}" style="{style}" vertex="1" parent="{pid}">\n'
            f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>\n'
            f"        </mxCell>\n"
        )
        return i

    def e(self, pid: str, src: str, tgt: str, label: str = "", dashed: bool = False) -> None:
        dash = "dashed=1;dashPattern=8 6;" if dashed else ""
        lbl = f'value="{esc(label)}" ' if label else ""
        self.cells.append(
            f'        <mxCell id="{self.nid()}" {lbl}style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;'
            f"strokeColor={ARROW};strokeWidth=2;endArrow=blockThin;endFill=1;"
            f'fontFamily=Segoe UI;fontSize=11;fontColor={ARROW};labelBackgroundColor=#FFFFFF;{dash}" '
            f'edge="1" parent="{pid}" source="{src}" target="{tgt}">\n'
            f'          <mxGeometry relative="1" as="geometry"/>\n'
            f"        </mxCell>\n"
        )

    def e_style(
        self,
        pid: str,
        src: str,
        tgt: str,
        label: str = "",
        extra_style: str = "",
        point_xy: tuple[float, float] | None = None,
    ) -> None:
        """Aresta com estilo extra (fecha o atributo style corretamente)."""
        lbl = f'value="{esc(label)}" ' if label else ""
        geom = '          <mxGeometry relative="1" as="geometry"/>'
        if point_xy:
            geom = (
                f'          <mxGeometry relative="1" as="geometry">'
                f'<Array as="points"><mxPoint x="{point_xy[0]}" y="{point_xy[1]}"/></Array></mxGeometry>'
            )
        self.cells.append(
            f'        <mxCell id="{self.nid()}" {lbl}style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;'
            f"{extra_style}"
            f'fontFamily=Segoe UI;labelBackgroundColor=#FFFFFF;" '
            f'edge="1" parent="{pid}" source="{src}" target="{tgt}">\n'
            f"{geom}\n"
            f"        </mxCell>\n"
        )

    def hdr(self, pid: str, title: str, sub: str, x: float, y: float, w: float, color: str) -> None:
        self.c(
            pid,
            f"<b>{title}</b><br><font style=\"font-size:11px\">{sub}</font>",
            x, y, w, 48,
            f"rounded=0;whiteSpace=wrap;html=1;fillColor={color};strokeColor={color};"
            f"fontColor=#FFFFFF;fontFamily=Segoe UI;fontSize=16;align=left;spacingLeft=12;verticalAlign=middle;",
        )

    def step(self, pid: str, num: str, title: str, desc: str, x: float, y: float, w: float, h: float, kind: str = "proc", key: str | None = None) -> str:
        badge = (
            f'<div style="background:{AZURE};color:#fff;border-radius:50%;width:20px;height:20px;'
            f'line-height:20px;text-align:center;font-size:11px;font-weight:bold;display:inline-block;margin-bottom:4px">{num}</div><br>'
        )
        label = f"{badge}<b>{title}</b><br><font style=\"font-size:10px;color:#555\">{desc}</font>"
        if kind == "store":
            st = f"shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=12;fillColor={STORE};strokeColor={STORE_BORDER};strokeWidth=2;whiteSpace=wrap;html=1;"
        elif kind == "start":
            st = "ellipse;whiteSpace=wrap;html=1;fillColor=#F3F2F1;strokeColor=#A19F9D;strokeWidth=2;"
        else:
            st = "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#605E5C;strokeWidth=2;"
        st += "fontFamily=Segoe UI;fontSize=12;align=center;verticalAlign=middle;spacing=6;"
        return self.c(pid, label, x, y, w, h, st, key)

    def step_green(
        self,
        pid: str,
        num: str,
        title: str,
        desc: str,
        x: float,
        y: float,
        w: float,
        h: float,
        kind: str = "proc",
        key: str | None = None,
        stroke: str = "#605E5C",
    ) -> str:
        """Passo numerado verde (referência Azure Data Factory baseline)."""
        badge = ""
        if num:
            badge = (
                f'<div style="background:{GREEN_STEP};color:#fff;border-radius:50%;width:20px;height:20px;'
                f'line-height:20px;text-align:center;font-size:11px;font-weight:bold;display:inline-block;margin-bottom:4px">{num}</div><br>'
            )
        label = f"{badge}<b>{title}</b><br><font style=\"font-size:10px;color:#555\">{desc}</font>"
        if kind == "store":
            st = f"shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=12;fillColor={STORE};strokeColor={STORE_BORDER};strokeWidth=2;whiteSpace=wrap;html=1;"
        elif kind == "start":
            st = "ellipse;whiteSpace=wrap;html=1;fillColor=#F3F2F1;strokeColor=#A19F9D;strokeWidth=2;"
        elif kind == "lake_hdr":
            st = f"rounded=1;whiteSpace=wrap;html=1;fillColor={STORE};strokeColor={STORE_BORDER};strokeWidth=1;"
        elif kind == "landing":
            st = "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF4CE;strokeColor=#D4A017;strokeWidth=1;"
        elif kind == "spark":
            st = "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#FF3621;strokeWidth=2;"
        elif kind == "dataprep":
            st = "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#8764B8;strokeWidth=2;"
        elif kind == "api":
            st = f"rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor={AZURE};strokeWidth=2;"
        elif kind == "dash":
            st = "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#F59E0B;strokeWidth=2;"
        elif kind == "gov":
            st = f"rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor={STORE_BORDER};strokeWidth=1;"
        else:
            st = f"rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor={stroke};strokeWidth=2;"
        st += "fontFamily=Segoe UI;fontSize=12;align=center;verticalAlign=middle;spacing=6;"
        return self.c(pid, label, x, y, w, h, st, key)

    def zone(self, pid: str, label: str, x: float, y: float, w: float, h: float, key: str) -> str:
        zid = self.c(
            pid,
            "",
            x,
            y,
            w,
            h,
            "rounded=0;fillColor=#FAFAFA;strokeColor=#C8C6C4;strokeWidth=1;",
            key,
        )
        self.c(
            zid,
            f"<b>{label}</b>",
            8,
            6,
            w - 16,
            18,
            "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;"
            "fontFamily=Segoe UI;fontSize=11;fontStyle=1;fontColor=#323130;",
            f"{key}_lbl",
        )
        return zid

    def flow_row(self, pid: str, y: float, steps: list[tuple[str, str, str, str]], bw: float = 150, bh: float = 88, gap: float = 24) -> list[str]:
        ids = []
        x0 = 40
        for i, (num, title, desc, kind) in enumerate(steps):
            x = x0 + i * (bw + gap)
            ids.append(self.step(pid, num, title, desc, x, y, bw, bh, kind, f"st_{num}_{y}"))
        for a, b in zip(ids, ids[1:]):
            self.e(pid, a, b)
        return ids

    def online_flow(self, pid: str, y_base: float, pw: float, compact: bool = False) -> tuple[str, str]:
        """Fluxo real da demo: Canal → API (não passa por Kafka). Kafka só como opcional."""
        bw, bh, gap = (150, 82, 22) if compact else (155, 88, 26)
        x0 = 36
        o1 = self.step(pid, "1", "Canal", "Console :3333\nDashboard · Swagger", x0, y_base, bw, bh, "start", "o_canal")
        o2 = self.step(pid, "2", "API Java", "POST /analyze\n:8080", x0 + bw + gap, y_base, bw, bh, "proc", "o_api")
        o3 = self.step(pid, "3", "Decisão", "Score + perfil\nMongoDB", x0 + 2 * (bw + gap), y_base, bw, bh, "proc", "o_score")
        o4 = self.step(pid, "4", "Painel", "Streamlit\n:8501", x0 + 3 * (bw + gap), y_base, bw, bh, "proc", "o_dash")
        o5 = self.step(pid, "5", "Analista", "Liberar · Chat\nDeepSeek", x0 + 4 * (bw + gap), y_base, bw, bh, "proc", "o_anal")
        self.e(pid, o1, o2, "POST /analyze")
        self.e(pid, o2, o3)
        self.e(pid, o3, o4)
        self.e(pid, o4, o5)
        ky = y_base + bh + 18
        kafka = self.c(
            pid,
            "<b>Kafka :9092</b> (opcional)<br><font style=\"font-size:10px\">Streaming Kafka — "
            "<b>não</b> é o caminho do console nem do painel nesta stack</font>",
            x0,
            ky,
            min(520, pw - 72),
            52,
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#F3F2F1;strokeColor=#A19F9D;strokeWidth=1;"
            "dashed=1;dashPattern=6 4;fontSize=11;fontFamily=Segoe UI;align=left;spacingLeft=8;",
            "o_kafka_opt",
        )
        return o2, o3

    def batch_engineering_flow(
        self,
        pid: str,
        y_base: float,
        zone_w: float,
        *,
        compact: bool = False,
        include_serving: bool = True,
    ) -> str:
        """Lake Medalhão: Bronze → Prata → Ouro + perfis Mongo para API."""
        bw = 118 if compact else 138
        bh = 78 if compact else 96
        gap = 14 if compact else 20
        x0 = 28

        # Faixa Medalhão
        med_w = 3 * (bw + gap) + bw
        self.c(
            pid,
            "<b>Medalhão (lake)</b> — camadas de maturidade do dado",
            x0 + bw + gap,
            y_base - 22,
            med_w,
            20,
            "rounded=0;whiteSpace=wrap;html=1;fillColor=#E1DFDD;strokeColor=#8A8886;"
            "fontSize=10;fontFamily=Segoe UI;fontStyle=1;align=center;",
        )

        s1 = self.step(pid, "1", "Fontes", "Core · APIs\nJSON histórico", x0, y_base, bw, bh, "start", "b_fontes")
        s2 = self.step(
            pid, "2", "Bronze", "Bruto · landing\nADLS · MinIO", x0 + bw + gap, y_base, bw, bh, "store", "b_bronze"
        )
        s3 = self.step(
            pid, "3", "Prata", "Limpeza · DQ\ndedup · enrich", x0 + 2 * (bw + gap), y_base, bw, bh, "store", "b_prata"
        )
        s4 = self.step(
            pid, "4", "Ouro", "Features · KPIs\ntabela ML", x0 + 3 * (bw + gap), y_base, bw, bh, "store", "b_ouro"
        )
        self.e(pid, s1, s2)
        self.e(pid, s2, s3)
        self.e(pid, s3, s4)

        x5 = x0 + 4 * (bw + gap)
        s5 = self.step(
            pid, "5", "Dataprep perfis", "Agrega\nuser_id", x5, y_base, bw, bh, "proc", "b_dataprep"
        )
        s6 = self.step(
            pid, "6", "MongoDB", "user_profiles\n(serving)", x5 + bw + gap, y_base, bw, bh, "store", "b_mongo"
        )
        self.e(pid, s4, s5, "derivado")
        self.e(pid, s5, s6)
        self.e(pid, s1, s5, "atalho demo", dashed=True)

        last = s6
        if include_serving:
            s7 = self.step(
                pid, "7", "Pronto", "API online\nconsulta", x5 + 2 * (bw + gap), y_base, bw, bh, "proc", "b_ready"
            )
            self.e(pid, s6, s7)
            last = s7

        note_y = y_base + bh + 14
        self.c(
            pid,
            "<b>Bronze</b> = como veio · <b>Prata</b> = confiável · <b>Ouro</b> = pronto para negócio/ML  ·  "
            "Perfis Mongo também via <code>batch_dataprep_mongo.py</code> (atalho a partir do JSON)",
            x0,
            note_y,
            zone_w - 56,
            36,
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#D4A017;strokeWidth=1;"
            "fontFamily=Segoe UI;fontSize=10;align=left;spacingLeft=6;",
        )
        return last

    def wrap_diagram(self, name: str, pw: int, ph: int) -> str:
        did = str(uuid.uuid4())
        return f"""  <diagram id="{did}" name="{esc(name)}">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{pw}" pageHeight="{ph}" math="0" shadow="0">
      <root>
{"".join(self.cells)}      </root>
    </mxGraphModel>
  </diagram>
"""

    def reset(self) -> None:
        self.n = 0
        self.cells = []
        self.ids = {}


def build_overview() -> str:
    """Uma página: batch em cima + online embaixo (apresentação)."""
    g = G()
    pw, ph = 1600, 1180
    root, layer = g.nid(), g.nid()
    g.cells = [
        '        <mxCell id="0"/>\n',
        f'        <mxCell id="{root}" parent="0"/>\n',
        f'        <mxCell id="{layer}" parent="{root}"/>\n',
    ]

    g.c(
        layer,
        "<b>DataMaster — Arquitetura completa</b><br><font style=\"font-size:11px\">Batch (engenharia de dados) separado do Online (tempo real)</font>",
        0, 0, pw, 44,
        f"rounded=0;whiteSpace=wrap;html=1;fillColor=#323130;strokeColor=none;fontColor=#FFFFFF;"
        f"fontFamily=Segoe UI;fontSize=15;align=center;verticalAlign=middle;",
    )

    # --- BATCH ZONE ---
    g.hdr(layer, "BATCH — Engenharia de dados", "Medalhão Bronze → Prata → Ouro + perfis Mongo", 24, 56, pw - 48, BATCH_HDR)
    bz = g.c(layer, "", 24, 108, pw - 48, 248, f"rounded=0;fillColor={BATCH_BG};strokeColor={BATCH_BORDER};strokeWidth=3;", "batch_z")
    g.batch_engineering_flow(bz, 52, pw - 96, compact=True, include_serving=False)

    g.c(bz, "<b>Azure:</b> ADLS bronze/silver/gold  ·  <b>AWS:</b> S3 prefixos  ·  "
              "<b>Local:</b> data/lake/ · MinIO · Spark · batch_dataprep_mongo.py",
        20, 200, pw - 88, 32,
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#D4A017;fontFamily=Segoe UI;fontSize=10;align=center;")

    # --- BRIDGE ---
    g.c(
        layer,
        "<b>↓ MongoDB user_profiles</b><br><font style=\"font-size:10px\">A API online consulta o perfil preparado no batch</font>",
        24, 368, pw - 48, 56,
        f"rounded=1;whiteSpace=wrap;html=1;fillColor={LOCAL_BG};strokeColor={LOCAL};strokeWidth=3;"
        f"fontFamily=Segoe UI;fontSize=12;align=center;",
        "bridge",
    )

    # --- ONLINE ZONE ---
    g.hdr(layer, "ONLINE — Tempo real", "Cada transação · decisão em menos de 2 segundos", 24, 438, pw - 48, ONLINE_HDR)
    oz = g.c(layer, "", 24, 490, pw - 48, 270, f"rounded=0;fillColor={ONLINE_BG};strokeColor={ONLINE_BORDER};strokeWidth=3;", "online_z")

    mongo = g.c(oz, "<b>← Batch</b><br>MongoDB", 24, 12, 92, 52,
        f"rounded=1;fillColor={BATCH_BG};strokeColor={BATCH_BORDER};strokeWidth=2;dashed=1;dashPattern=6 4;"
        f"fontFamily=Segoe UI;fontSize=10;align=center;", "mongo")

    api_id, score_id = g.online_flow(oz, 44, pw - 96, compact=True)
    g.e(oz, mongo, api_id, "consulta perfil", dashed=True)

    g.c(oz, "<b>Demo real:</b> Console/Dashboard chamam a API direto  ·  Kafka = narrativa Azure (opcional)", 20, 195, pw - 88, 28,
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#5EA0EF;fontFamily=Segoe UI;fontSize=10;align=center;")

    g.c(layer, "Apresentação: use esta aba · Detalhes: abas 01-Batch e 02-Online · Mapa: aba 03",
        24, ph - 48, pw - 48, 32,
        "rounded=0;fillColor=#F3F2F1;strokeColor=none;fontFamily=Segoe UI;fontSize=11;align=center;fontColor=#666;")

    return g.wrap_diagram("00-Visao-Geral", pw, ph)


def build_batch_medallion() -> str:
    """Estilo Azure: Ingest · Store · Process · Serve · Monitor and govern."""
    g = G()
    pw, ph = 1200, 680
    root, layer = g.nid(), g.nid()
    g.cells = [
        '        <mxCell id="0"/>\n',
        f'        <mxCell id="{root}" parent="0"/>\n',
        f'        <mxCell id="{layer}" parent="{root}"/>\n',
    ]

    g.c(
        layer,
        "<b>DataMaster</b> · processamento batch (local · Azure · AWS)",
        16,
        12,
        pw - 32,
        32,
        "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;"
        "fontFamily=Segoe UI;fontSize=14;fontStyle=1;fontColor=#323130;",
        "title",
    )
    g.c(
        layer,
        "",
        12,
        8,
        pw - 24,
        ph - 16,
        "rounded=0;fillColor=none;strokeColor=#605E5C;strokeWidth=2;dashed=1;dashPattern=10 6;",
        "outer",
    )

    # --- INGEST ---
    iz = g.zone(layer, "Ingest", 24, 52, 180, 420, "ingest")
    src = g.step_green(iz, "1", "Fonte histórica", "Core · APIs\narquivos", 22, 36, 136, 72, "start", "ing_src")
    orch = g.step_green(
        iz,
        "",
        "Orquestração",
        "ADF · Glue\nConsole :3333\ngenerate_data.py",
        22,
        128,
        136,
        80,
        "proc",
        "ing_orch",
        stroke=AZURE,
    )
    json_l = g.step_green(
        iz,
        "",
        "data/transactions.json",
        "landing · export batch",
        22,
        228,
        136,
        56,
        "landing",
        "ing_json",
    )
    g.e(iz, src, orch)
    g.e(iz, orch, json_l)

    # --- STORE ---
    sz = g.zone(layer, "Store", 220, 52, 540, 288, "store")
    g.c(
        sz,
        "<b>Data Lake Storage</b><br><font style=\"font-size:10px;color:#555\">ADLS Gen2 · S3 · data/lake/ · MinIO</font>"
        "<br><font style=\"font-size:9px;color:#0078D4\">Delta Lake / Parquet · Medallion Architecture</font>",
        16,
        28,
        508,
        52,
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#E1DFDD;strokeColor=#8A8886;strokeWidth=1;"
        "fontFamily=Segoe UI;fontSize=11;align=center;verticalAlign=middle;",
        "lake_hdr",
    )
    bronze = g.step_green(
        sz, "2", "Bronze", "bruto · JSON", 36, 96, 130, 80, "store", "st_bronze"
    )
    silver = g.step_green(
        sz, "3", "Silver", "harmonizado · DQ", 196, 96, 130, 80, "store", "st_silver"
    )
    gold = g.step_green(
        sz, "4", "Gold", "features ML", 356, 96, 130, 80, "store", "st_gold"
    )
    g.e(sz, bronze, silver)
    g.e(sz, silver, gold)

    # --- PROCESS ---
    pz = g.zone(layer, "Process", 220, 352, 540, 120, "process")
    spark = g.step_green(
        pz,
        "",
        "Apache Spark",
        "Databricks · EMR · Glue\nspark_local_pipeline.py",
        20,
        32,
        220,
        72,
        "spark",
        "proc_spark",
    )
    dataprep = g.step_green(
        pz,
        "4",
        "Dataprep perfis",
        "batch_dataprep_mongo.py\nmédia · P95 · user_id",
        280,
        32,
        240,
        72,
        "dataprep",
        "proc_dataprep",
    )
    g.e(layer, spark, bronze, "", dashed=True)
    g.e(layer, spark, silver, "", dashed=True)
    g.e(layer, spark, gold, "", dashed=True)

    # --- SERVE ---
    vz = g.zone(layer, "Serve", 780, 52, 396, 420, "serve")
    mongo = g.step_green(
        vz, "5", "MongoDB", "user_profiles\nMongoDB", 118, 36, 160, 80, "store", "srv_mongo"
    )
    api = g.step_green(
        vz,
        "",
        "API Java",
        "POST /analyze · profile boost\n:8080 · Container Apps / EKS",
        118,
        136,
        160,
        72,
        "api",
        "srv_api",
    )
    dash = g.step_green(
        vz,
        "",
        "Dashboard",
        "Streamlit :8501 · Power BI\nfiltro · liberar · IA",
        118,
        228,
        160,
        72,
        "dash",
        "srv_dash",
    )
    g.e(vz, mongo, api)
    g.e(vz, api, dash)

    # --- CROSS ZONE ---
    g.e(layer, json_l, bronze)
    g.e(layer, dataprep, mongo)
    g.e(layer, gold, mongo, "", dashed=True)

    # --- MONITOR AND GOVERN ---
    gz = g.zone(layer, "Monitor and govern", 24, 488, pw - 48, 120, "govern")
    gov_items = [
        ("6", "Data Quality", "dq_latest.json\nGreat Expectations"),
        ("", "Monitor", "Prometheus · Grafana\nAzure Monitor · CW"),
        ("", "Key Vault", "Secrets Manager\nKMS · strings lake"),
        ("", "Purview", "linhagem · catálogo\nLake Formation · Glue"),
        ("", "DevOps", "CI/CD · GitHub Actions\nTerraform apply"),
        ("", "Entra ID", "RBAC · IAM\nmanaged identity"),
        ("", "FinOps", "Cost Management\ncusto por camada"),
    ]
    gx = 16
    for i, (num, title, desc) in enumerate(gov_items):
        g.step_green(gz, num, title, desc, gx + i * 148, 28, 132, 72, "gov", f"gov_{i}")
        gx += 0

    g.c(
        layer,
        "Demo: bash scripts/run_demo.sh · portal :8880 · slide 7 banca.html",
        24,
        ph - 36,
        pw - 48,
        24,
        "text;html=1;strokeColor=none;fillColor=none;align=left;fontFamily=Segoe UI;fontSize=9;fontColor=#605E5C;",
    )

    return g.wrap_diagram("01-Batch-Medallion-Azure", pw, ph)


def build_online_gateway() -> str:
    """Estilo microserviços: LB + API Gateway apagados; demo = HTTP direto na API."""
    g = G()
    pw, ph = 1280, 760
    root, layer = g.nid(), g.nid()
    g.cells = [
        '        <mxCell id="0"/>\n',
        f'        <mxCell id="{root}" parent="0"/>\n',
        f'        <mxCell id="{layer}" parent="{root}"/>\n',
    ]

    g.c(
        layer,
        "<b>DataMaster</b> · arquitetura online (tempo real · antifraude)",
        16,
        12,
        pw - 32,
        28,
        "text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;"
        "fontFamily=Segoe UI;fontSize=14;fontStyle=1;fontColor=#323130;",
        "title",
    )

    # --- CLIENT ---
    client = g.c(
        layer,
        "<b>Clientes / Canais</b><br><font style=\"font-size:10px;color:#555\">Console :3333 · Dashboard :8501<br>Swagger · curl · mobile/web</font>",
        24,
        200,
        120,
        100,
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#E8F5E9;strokeColor=#107C10;strokeWidth=2;"
        "fontFamily=Segoe UI;fontSize=11;align=center;verticalAlign=middle;",
        "client",
    )

    # Proxy line
    g.c(
        layer,
        "<b>Proxy</b><br><font style=\"font-size:9px;color:#888\">Internet · DMZ</font>",
        156,
        180,
        24,
        140,
        "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;"
        "fontFamily=Segoe UI;fontSize=10;fontColor=#605E5C;rotation=-90;",
        "proxy_lbl",
    )
    g.c(
        layer,
        "",
        168,
        160,
        4,
        180,
        "line;strokeWidth=2;strokeColor=#605E5C;dashed=1;dashPattern=8 6;",
        "proxy_line",
    )

    # --- PRIVATE NETWORK ---
    pn = g.c(
        layer,
        "",
        188,
        72,
        880,
        560,
        "rounded=0;fillColor=#FAFAFA;strokeColor=#605E5C;strokeWidth=2;dashed=1;dashPattern=10 6;",
        "private_net",
    )
    g.c(
        pn,
        "<b>— Private Network —</b>",
        300,
        8,
        280,
        20,
        "text;html=1;strokeColor=none;fillColor=none;align=center;fontFamily=Segoe UI;fontSize=11;fontStyle=1;",
        "pn_lbl",
    )

    # Load Balancer (faded)
    lb = g.c(
        pn,
        "<b>Load Balancer</b><br><font style=\"font-size:9px\">Azure LB · ALB · NGINX</font>"
        "<br><br><font style=\"font-size:9px;color:#888\"><i>Não implementado</i></font>",
        36,
        200,
        120,
        88,
        FADED,
        "lb",
    )

    # API Gateway (faded)
    gw = g.c(
        pn,
        "<b>API Gateway</b><br><font style=\"font-size:9px\">APIM · AWS API GW<br>Kong · Azure Front Door</font>"
        "<br><font style=\"font-size:9px;color:#888\"><i>Não implementado</i></font>",
        176,
        200,
        130,
        88,
        FADED,
        "gw",
    )

    # Callout — importância API Gateway
    g.c(
        pn,
        "<b>⚠ Por que API Gateway em produção?</b><br><font style=\"font-size:9px\">"
        "• Autenticação OAuth/JWT · rate limit · WAF<br>"
        "• Roteamento versionado (/v1/analyze)<br>"
        "• Throttling por parceiro · quota<br>"
        "• Observabilidade centralizada · correlation-id<br>"
        "• Desacopla canal do microserviço interno</font>",
        160,
        72,
        260,
        108,
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF4CE;strokeColor=#D4A017;strokeWidth=2;"
        "fontFamily=Segoe UI;fontSize=10;align=left;spacingLeft=8;verticalAlign=top;",
        "gw_callout",
    )

    # Demo path label
    g.c(
        pn,
        "<b>Caminho da demo</b> (HTTP direto)",
        320,
        168,
        160,
        24,
        "text;html=1;strokeColor=none;fillColor=none;align=center;fontFamily=Segoe UI;fontSize=10;fontStyle=1;fontColor=#107C10;",
        "demo_lbl",
    )

    # API Java — implementado
    api = g.c(
        pn,
        "<b>API Java</b><br><font style=\"font-size:10px;color:#555\">Spring Boot · :8080<br>POST /analyze · /batch</font>",
        340,
        200,
        140,
        88,
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#107C10;strokeWidth=3;"
        "fontFamily=Segoe UI;fontSize=12;align=center;verticalAlign=middle;",
        "api",
    )

    # Microservices cluster
    ms = g.c(
        pn,
        "",
        500,
        120,
        360,
        400,
        "rounded=0;fillColor=none;strokeColor=#0078D4;strokeWidth=1;dashed=1;dashPattern=4 4;",
        "ms_zone",
    )
    g.c(
        ms,
        "<b>Microserviços (monólito modular na demo)</b>",
        60,
        4,
        240,
        18,
        "text;html=1;strokeColor=none;fillColor=none;align=center;fontFamily=Segoe UI;fontSize=10;fontStyle=1;",
        "ms_lbl",
    )

    ms1 = g.c(
        ms,
        "<b>Scoring</b><br><font style=\"font-size:9px\">fraud_score<br>60% / 75% policy</font>",
        24,
        36,
        140,
        64,
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0078D4;strokeWidth=2;"
        "fontFamily=Segoe UI;fontSize=10;align=center;",
        "ms_score",
    )
    ms2 = g.c(
        ms,
        "<b>Perfil</b><br><font style=\"font-size:9px\">anomaly_boost<br>MongoDB lookup</font>",
        196,
        36,
        140,
        64,
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0078D4;strokeWidth=2;"
        "fontFamily=Segoe UI;fontSize=10;align=center;",
        "ms_profile",
    )
    ms3 = g.c(
        ms,
        "<b>LGPD</b><br><font style=\"font-size:9px\">CPF · cartão<br>mascaramento</font>",
        24,
        120,
        140,
        64,
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0078D4;strokeWidth=2;"
        "fontFamily=Segoe UI;fontSize=10;align=center;",
        "ms_lgpd",
    )
    ms4 = g.c(
        ms,
        "<b>Evento</b><br><font style=\"font-size:9px\">Kafka<br>transaction-analyzed</font>",
        196,
        120,
        140,
        64,
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#0078D4;strokeWidth=2;"
        "fontFamily=Segoe UI;fontSize=10;align=center;",
        "ms_alert",
    )
    route = g.c(
        ms,
        "<b>Internal<br>Routing</b>",
        130,
        220,
        100,
        56,
        "shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;fixedSize=1;"
        "fillColor=#E8F4FC;strokeColor=#0078D4;strokeWidth=2;fontFamily=Segoe UI;fontSize=10;align=center;",
        "ms_route",
    )
    g.e(ms, route, ms1, "", dashed=True)
    g.e(ms, route, ms2, "", dashed=True)
    g.e(ms, route, ms3, "", dashed=True)
    g.e(ms, route, ms4, "", dashed=True)

    # Supporting — MongoDB
    mongo = g.c(
        pn,
        "<b>MongoDB</b><br><font style=\"font-size:9px\">user_profiles<br>← batch</font>",
        520,
        36,
        110,
        56,
        f"shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=10;fillColor={STORE};"
        f"strokeColor={STORE_BORDER};strokeWidth=2;whiteSpace=wrap;html=1;fontFamily=Segoe UI;fontSize=10;align=center;",
        "mongo",
    )

    # Logging / observability
    log = g.c(
        pn,
        "<b>Observabilidade</b><br><font style=\"font-size:9px\">Prometheus · Grafana<br>/health · métricas</font>",
        36,
        420,
        150,
        64,
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#605E5C;strokeWidth=1;"
        "fontFamily=Segoe UI;fontSize=10;align=center;",
        "obs",
    )

    # Dashboard analyst
    dash = g.c(
        pn,
        "<b>Dashboard</b><br><font style=\"font-size:9px\">Streamlit :8501<br>liberar · IA DeepSeek</font>",
        220,
        420,
        140,
        64,
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#F59E0B;strokeWidth=2;"
        "fontFamily=Segoe UI;fontSize=10;align=center;",
        "dash",
    )

    # --- RELATED SERVICES (outside) ---
    rel = g.c(
        layer,
        "<b>Related Services</b><br><font style=\"font-size:9px;color:#555\">DeepSeek API<br>Azure Container Apps<br>Kafka</font>",
        1100,
        240,
        140,
        100,
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#E8F4FC;strokeColor=#0078D4;strokeWidth=2;"
        "fontFamily=Segoe UI;fontSize=11;align=center;verticalAlign=middle;",
        "related",
    )

    # --- EDGES ---
    # Faded path client -> LB -> GW (não usado)
    g.e_style(
        layer,
        client,
        lb,
        "produção",
        f"{FADED_EDGE}endArrow=blockThin;endFill=1;fontSize=9;fontColor=#A19F9D;",
    )
    g.e_style(pn, lb, gw, "", f"{FADED_EDGE}endArrow=blockThin;endFill=1;")

    # Demo path — bold green
    g.e_style(
        layer,
        client,
        api,
        "demo · HTTP direto",
        f"{DEMO_EDGE}fontSize=10;fontColor={LOCAL};",
        point_xy=(300, 250),
    )

    g.e(pn, api, ms, "roteamento interno")
    g.e(pn, mongo, ms2, "consulta", dashed=True)
    g.e(pn, api, log, "telemetria", dashed=True)
    g.e(pn, ms4, log, "", dashed=True)
    g.e(pn, dash, api, "GET/POST", dashed=True)
    g.e(layer, api, rel, "DeepSeek · cloud", dashed=True)

    g.c(
        layer,
        "<b>Na banca:</b> canal chama API :8080 direto · LB e API Gateway são <i>roadmap produção</i> (Terraform apresentacao / APIM) · "
        "destaque verbal: gateway = segurança, quota e contrato único para parceiros",
        24,
        ph - 48,
        pw - 48,
        36,
        "rounded=1;whiteSpace=wrap;html=1;fillColor=#F3F2F1;strokeColor=#C8C6C4;fontFamily=Segoe UI;fontSize=9;align=left;spacingLeft=8;",
    )

    return g.wrap_diagram("02-Online-Gateway", pw, ph)


def build_map() -> str:
    g = G()
    pw, ph = 1200, 480
    root, layer = g.nid(), g.nid()
    g.cells = ['        <mxCell id="0"/>\n', f'        <mxCell id="{root}" parent="0"/>\n', f'        <mxCell id="{layer}" parent="{root}"/>\n']
    g.hdr(layer, "03 — MAPA NUVEM", "Referência rápida", 20, 12, pw - 40, "#605E5C")
    rows = [
        ("Batch", "Airflow + Spark", "Airflow + Spark", "Airflow + Spark"),
        ("Stream", "Kafka", "Kafka", "Kafka"),
        ("Lake Medalhão", "ADLS bronze/silver/gold", "S3 B/S/G", "MinIO · data/lake/"),
        ("Perfis", "MongoDB", "MongoDB", "MongoDB"),
        ("API", "Container Apps", "ECS/EKS", ":8080"),
        ("Painel", "Power BI", "QuickSight", "Streamlit"),
    ]
    x0, cw_fn, cw = 20, 140, (pw - 160) / 3
    g.c(layer, "<b>Função</b>", x0, 68, cw_fn, 36, "rounded=0;fillColor=#EDEBE9;fontFamily=Segoe UI;fontSize=12;fontStyle=1;align=center;")
    for i, (lb, col) in enumerate([("Azure", AZURE), ("AWS", AWS), ("Local", LOCAL)]):
        g.c(layer, f"<b>{lb}</b>", x0 + cw_fn + 8 + i * (cw + 8), 68, cw, 36,
            f"rounded=0;fillColor={col};strokeColor={col};fontColor=#FFF;fontFamily=Segoe UI;fontSize=12;align=center;")
    for ri, (fn, az, aws, loc) in enumerate(rows):
        y = 110 + ri * 52
        g.c(layer, fn, x0, y, cw_fn, 48, "rounded=0;fillColor=#FFF;fontFamily=Segoe UI;fontSize=11;align=left;spacingLeft=6;")
        for ci, (t, bg) in enumerate([(az, AZURE_BG), (aws, AWS_BG), (loc, LOCAL_BG)]):
            g.c(layer, t, x0 + cw_fn + 8 + ci * (cw + 8), y, cw, 48,
                f"rounded=0;fillColor={bg};fontFamily=Segoe UI;fontSize=10;align=center;")
    return g.wrap_diagram("03-Mapa-Nuvem", pw, ph)


def write_file(path: Path, diagrams: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    n_pages = diagrams.count("<diagram ")
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="{ts}" agent="DataMaster" version="22.1.0" type="device" pages="{n_pages}">
{diagrams}
</mxfile>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(xml, encoding="utf-8")


def main() -> None:
    write_file(OUT_DIR / "datamaster-01-batch-medallion.drawio", build_batch_medallion())
    write_file(OUT_DIR / "datamaster-02-online-gateway.drawio", build_online_gateway())
    write_file(OUT_DIR / "datamaster-03-mapa.drawio", build_map())

    print(f"✅ Diagramas gerados em {OUT_DIR}/")
    print("   - datamaster-01-batch-medallion.drawio  ← estilo Medallion (Bronze → Silver → Gold)")
    print("   - datamaster-02-online-gateway.drawio  ← serving online (API + Kafka + Mongo)")
    print("   - datamaster-03-mapa.drawio")
    print()
    print("⚠  datamaster-00-visao-geral.drawio NÃO é regenerado: é editado manualmente (apresentação ponta-a-ponta).")
    print("Exportar SVG/PNG para portal/banca.html:")
    print("   bash scripts/export_portal_diagrams.sh")


if __name__ == "__main__":
    main()
