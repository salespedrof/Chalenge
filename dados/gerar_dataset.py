"""
Gerador do dataset SIMULADO de sensores das escadas rolantes da Linha 4 (ViaQuatro).

A Motiva não forneceu leituras reais para as Sprints 1 e 2. Este script cria um
dataset sintético, reprodutível (semente fixa), com as 5 variáveis do enunciado:
vibração, temperatura, corrente/tensão, nível de óleo e velocidade.

O que é real e o que é simulado:
- REAL: os 197 códigos de escada, as 12 estações e o fabricante (Thyssen/ESCAL),
  tirados do histórico SAP fornecido pela Motiva; o volume de falhas real de
  2023-2026 de cada escada (perfil_escadas.csv) é usado só para dar a cada
  escada um "risco" relativo.
- SIMULADO: todas as leituras, os limites de status, os defeitos, as
  manutenções, os técnicos e o grupo crítica / não crítica.

Uso:  python gerar_dataset.py            (gera os CSVs na pasta atual)
"""

import numpy as np
import pandas as pd

SEED = 2026
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------------------
# Parâmetros gerais
# ---------------------------------------------------------------------------
INICIO = "2026-07-01"
DIAS = 90
HORAS_LEITURA = [6, 10, 14, 18, 22]   # metrô fechado de madrugada: sem leitura
VEL_NOMINAL = 0.50                    # m/s, velocidade nominal da escada

# Limites usados para classificar o status (também salvos em limites_status.csv)
LIMITES = {
    #  variável            unidade   alerta        crítico      sentido
    "vibracao_mm_s":     ("mm/s",    4.5,          7.1,         "acima"),
    "temperatura_c":     ("°C",      80.0,         95.0,        "acima"),
    "corrente_a":        ("A",       30.0,         36.0,        "acima"),
    "tensao_v":          ("V",       7.0,          10.0,        "desvio % de 380 V"),
    "nivel_oleo_pct":    ("%",       35.0,         20.0,        "abaixo"),
    "velocidade_m_s":    ("m/s",     3.0,          6.0,         "desvio % de 0,50 m/s"),
}

ESTACOES = {
    "LUZ": "Luz", "REP": "República", "HIG": "Higienópolis-Mackenzie",
    "PTA": "Paulista", "FRE": "Oscar Freire", "FRA": "Fradique Coutinho",
    "FAL": "Faria Lima", "PIN": "Pinheiros", "BUT": "Butantã",
    "MBI": "São Paulo-Morumbi", "VSO": "Vila Sônia", "TVS": "Terminal Vila Sônia",
}
ESCAL = {"FAL-ER09", "PIN-ER09", "PIN-ER14", "PIN-ER15", "PIN-ER20",
         "PIN-ER21", "PIN-ER26", "PIN-ER27", "PIN-ER30"}
TECNICOS = [f"T{i:02d}" for i in range(1, 13)]   # identificadores fictícios


# ---------------------------------------------------------------------------
# 1. Cadastro das escadas
# ---------------------------------------------------------------------------
def montar_escadas():
    perfil = pd.read_csv("perfil_escadas.csv")
    perfil.columns = ["escada_id", "falhas_reais_2023_2026", "horas_paradas_reais"]
    perfil["estacao_cod"] = perfil.escada_id.str[:3]
    perfil["estacao_nome"] = perfil.estacao_cod.map(ESTACOES)
    perfil["fabricante"] = np.where(perfil.escada_id.isin(ESCAL), "ESCAL", "Thyssen")
    # risco relativo 0-1 pelo ranking de falhas reais
    perfil["risco"] = perfil.falhas_reais_2023_2026.rank(pct=True).round(3)
    # grupo crítica / não crítica: HIPÓTESE (a lista real REF-6ECR-0002 não veio)
    perfil["grupo"] = np.where(perfil.risco >= 0.55, "critica", "nao_critica")
    # fluxo relativo da estação (hipótese: estações de integração mais cheias)
    fluxo = {"LUZ": 1.0, "PTA": 1.0, "REP": 0.95, "PIN": 0.95, "BUT": 0.8,
             "FAL": 0.8, "HIG": 0.7, "FRE": 0.6, "FRA": 0.6, "MBI": 0.6,
             "VSO": 0.65, "TVS": 0.45}
    perfil["fluxo_relativo"] = perfil.estacao_cod.map(fluxo)
    return perfil[["escada_id", "estacao_cod", "estacao_nome", "fabricante",
                   "grupo", "fluxo_relativo", "risco"]]


# ---------------------------------------------------------------------------
# 2. Linha do tempo de leituras
# ---------------------------------------------------------------------------
def montar_tempos():
    dias = pd.date_range(INICIO, periods=DIAS, freq="D")
    return pd.DatetimeIndex([d + pd.Timedelta(hours=h) for d in dias for h in HORAS_LEITURA])


def carga(tempos, fluxo):
    """Fator de carga 0-1 conforme hora e dia da semana (picos 6-9h e 17-19h)."""
    h = tempos.hour.values
    pico = np.select([h == 6, h == 18, h == 10, h == 14, h == 22],
                     [0.85, 1.0, 0.55, 0.6, 0.35], 0.5)
    fds = tempos.dayofweek.values >= 5
    pico = np.where(fds, pico * 0.6, pico)
    return np.clip(pico * fluxo + rng.normal(0, 0.05, len(h)), 0.05, 1.1)


# ---------------------------------------------------------------------------
# 3. Defeitos simulados
# ---------------------------------------------------------------------------
DEFEITOS = ["rolamento", "atrito", "vazamento_oleo", "eletrico", "sensor_mudo"]


def sortear_defeitos(esc, n_leituras):
    """Sorteia de 0 a 3 defeitos por escada, mais prováveis nas de maior risco."""
    eventos = []
    p_base = 0.5 + 1.6 * esc.risco + (0.6 if esc.fabricante == "ESCAL" else 0)
    n = rng.poisson(p_base)
    for _ in range(min(n, 3)):
        tipo = rng.choice(DEFEITOS, p=[0.3, 0.15, 0.2, 0.2, 0.15])
        inicio = int(rng.integers(0, n_leituras - 20))
        dur = {"rolamento": rng.integers(60, 180), "atrito": rng.integers(40, 120),
               "vazamento_oleo": rng.integers(60, 200), "eletrico": rng.integers(30, 120),
               "sensor_mudo": rng.integers(2, 10)}[tipo]
        eventos.append((tipo, inicio, int(dur)))
    return eventos


# ---------------------------------------------------------------------------
# 4. Classificação de status (mesma regra do dashboard)
# ---------------------------------------------------------------------------
def classificar(df):
    vals = df[list(LIMITES)]
    sem_resposta = vals.isna().all(axis=1)
    dev_v = (df.tensao_v - 380).abs() / 380 * 100
    dev_vel = (df.velocidade_m_s - VEL_NOMINAL).abs() / VEL_NOMINAL * 100
    crit = (sem_resposta | (df.velocidade_m_s == 0) |
            (df.vibracao_mm_s >= 7.1) | (df.temperatura_c >= 95) |
            (df.corrente_a >= 36) | (dev_v >= 10) | (df.nivel_oleo_pct <= 20) |
            (dev_vel >= 6))
    alerta = ((df.vibracao_mm_s >= 4.5) | (df.temperatura_c >= 80) |
              (df.corrente_a >= 30) | (dev_v >= 7) | (df.nivel_oleo_pct <= 35) |
              (dev_vel >= 3))
    return np.select([crit, alerta], ["CRITICO", "ALERTA"], "BOM")


# ---------------------------------------------------------------------------
# 5. Simulação de uma escada
# ---------------------------------------------------------------------------
def simular_escada(esc, tempos):
    n = len(tempos)
    ld = carga(tempos, esc.fluxo_relativo)
    t_dias = (tempos - tempos[0]).total_seconds().values / 86400

    # --- comportamento normal (base)
    vib_base = rng.uniform(1.2, 2.2) * (1.15 if esc.fabricante == "ESCAL" else 1)
    base = {
        "vibracao_mm_s": vib_base * (1 + 0.25 * ld) + rng.normal(0, 0.15, n),
        "temperatura_c": 34 + 20 * ld + 3 * (t_dias / DIAS) + rng.normal(0, 1.5, n),  # ago/set mais quente
        "corrente_a": 11 + 12 * ld + rng.normal(0, 0.8, n),
        "tensao_v": 380 + rng.normal(0, 4, n),
        "velocidade_m_s": VEL_NOMINAL * (1 - 0.012 * ld) + rng.normal(0, 0.002, n),
    }

    # óleo: consumo contínuo, reposto na P1 mensal (e em cada manutenção corretiva)
    consumo = rng.uniform(0.35, 0.75) * (1 + 0.3 * esc.fluxo_relativo) / len(HORAS_LEITURA)
    dia_p1 = int(rng.integers(1, 29))
    reposicao = np.array([t.day == dia_p1 and t.hour == HORAS_LEITURA[0] for t in tempos])

    def curva_oleo(reposicoes, inicio):
        nivel, out = inicio, np.empty(n)
        for i in range(n):
            if reposicoes[i]:
                nivel = 100.0
            nivel -= consumo
            out[i] = nivel
        return out

    nivel_inicial = rng.uniform(70, 100)

    # --- defeitos: cada um tem sua própria contribuição, para o reparo zerar só ele
    eventos = []
    for tipo, ini, dur in sortear_defeitos(esc, n):
        fim = min(n, ini + dur)
        c = {k: np.zeros(n) for k in list(base) + ["nivel_oleo_pct"]}
        mudo = np.zeros(n, bool)
        rampa = np.linspace(0, 1, fim - ini)
        if tipo == "rolamento":
            c["vibracao_mm_s"][ini:] = np.r_[rampa ** 1.6, np.ones(n - fim)] * rng.uniform(5, 9)
            c["temperatura_c"][ini:] = np.r_[rampa, np.ones(n - fim)] * rng.uniform(4, 12)
        elif tipo == "atrito":
            c["temperatura_c"][ini:] = np.r_[rampa ** 1.3, np.ones(n - fim)] * rng.uniform(30, 55)
            c["velocidade_m_s"][ini:] = -np.r_[rampa, np.ones(n - fim)] * VEL_NOMINAL * rng.uniform(0.03, 0.08)
            c["corrente_a"][ini:] = np.r_[rampa, np.ones(n - fim)] * rng.uniform(4, 10)
        elif tipo == "vazamento_oleo":
            c["nivel_oleo_pct"][ini:] = -np.cumsum(np.full(n - ini, rng.uniform(1.0, 2.5) / len(HORAS_LEITURA)))
        elif tipo == "eletrico":
            picos = rng.random(n - ini) < 0.12
            c["corrente_a"][ini:] = picos * rng.uniform(10, 18, n - ini)
            c["tensao_v"][ini:] = -(picos * rng.uniform(15, 45, n - ini))
        elif tipo == "sensor_mudo":
            mudo[ini:fim] = True
        eventos.append({"tipo": tipo, "ini": ini, "c": c, "mudo": mudo})

    # paradas curtas por dispositivo de segurança: a falha mais comum no histórico SAP real
    # (resolvidas com reset). Frequência proporcional ao risco real da escada.
    parada = np.zeros(n, bool)
    k = rng.poisson(2 + 8 * esc.risco)
    parada[rng.choice(n, min(k, n), replace=False)] = True

    def montar():
        df = pd.DataFrame({"escada_id": esc.escada_id, "data_hora": tempos})
        for k_, v in base.items():
            df[k_] = v + sum(e["c"][k_] for e in eventos)
        df["nivel_oleo_pct"] = np.clip(curva_oleo(reposicao, nivel_inicial)
                                       + sum(e["c"]["nivel_oleo_pct"] for e in eventos)
                                       + rng_oleo, 0, 100)
        df.loc[parada, ["velocidade_m_s"]] = 0.0
        df.loc[parada, "corrente_a"] = corr_parada
        df.loc[parada, "vibracao_mm_s"] = vib_parada
        mudo = np.zeros(n, bool)
        for e in eventos:
            mudo |= e["mudo"]
        df.loc[mudo, list(LIMITES)] = np.nan
        return df, mudo

    rng_oleo = rng.normal(0, 0.4, n)
    corr_parada = rng.uniform(0, 1.5, parada.sum())
    vib_parada = rng.uniform(0.1, 0.4, parada.sum())

    df, mudo = montar()
    status = classificar(df)
    em_manut = np.zeros(n, bool)
    atend = []
    i, alerta_seguidos = 0, 0
    limiar_alerta = int(rng.integers(20, 50))   # leituras em alerta até o técnico agir (4 a 10 dias)
    while i < n:
        if parada[i]:
            entrada = tempos[i] + pd.Timedelta(minutes=int(rng.integers(5, 30)))
            atend.append({"escada_id": esc.escada_id, "tecnico_id": rng.choice(TECNICOS),
                          "tipo": "corretiva", "motivo": "parada de seguranca (reset)",
                          "entrada": entrada,
                          "saida": entrada + pd.Timedelta(minutes=int(rng.integers(10, 45)))})
            i += 1
            continue
        alerta_seguidos = alerta_seguidos + 1 if status[i] == "ALERTA" else 0
        if status[i] == "CRITICO" or alerta_seguidos >= limiar_alerta:
            motivo = ("sem resposta do sensor" if mudo[i] else
                      "status critico" if status[i] == "CRITICO" else "alerta prolongado")
            atraso = int(rng.integers(1, 6)) if status[i] == "CRITICO" else 0
            dur = int(rng.integers(1, 4)) * (3 if esc.fabricante == "ESCAL" else 1)
            ini, fim = min(n - 1, i + atraso), min(n, i + atraso + dur)
            em_manut[ini:fim] = True
            entrada = tempos[ini] + pd.Timedelta(minutes=int(rng.integers(5, 120)))
            atend.append({"escada_id": esc.escada_id, "tecnico_id": rng.choice(TECNICOS),
                          "tipo": "corretiva", "motivo": motivo, "entrada": entrada,
                          "saida": entrada + pd.Timedelta(hours=round(float(rng.uniform(0.5, 3.5)) * dur * (1 if dur == 1 else 3), 2))})
            # reparo: zera, a partir do fim da manutenção, os defeitos já iniciados
            for e in eventos:
                if e["ini"] <= i:
                    for arr in e["c"].values():
                        arr[fim:] = 0
                    e["mudo"][fim:] = False
            if fim < n:
                reposicao[fim] = True        # técnico completa o óleo
            df, mudo = montar()
            status = classificar(df)
            i, alerta_seguidos = fim, 0
            continue
        i += 1

    # preventivas P1 mensais (cerca de 2 h, técnico dá entrada e saída)
    for d in pd.date_range(INICIO, periods=DIAS, freq="D"):
        if d.day == dia_p1:
            entrada = d + pd.Timedelta(hours=int(rng.integers(0, 4)), minutes=int(rng.integers(0, 60)))
            atend.append({"escada_id": esc.escada_id, "tecnico_id": rng.choice(TECNICOS),
                          "tipo": "preventiva", "motivo": "P1 mensal", "entrada": entrada,
                          "saida": entrada + pd.Timedelta(hours=round(float(rng.uniform(1.5, 2.8)), 2))})

    df["status"] = classificar(df)
    # escada desligada durante a manutenção
    df.loc[em_manut, ["velocidade_m_s", "corrente_a"]] = 0.0
    df.loc[em_manut, "vibracao_mm_s"] = rng.uniform(0.1, 0.3, em_manut.sum())
    df.loc[em_manut, "status"] = "EM_MANUTENCAO"
    return df, atend


# ---------------------------------------------------------------------------
# 6. Problemas de qualidade inseridos de propósito (para a etapa de EDA)
# ---------------------------------------------------------------------------
def sujar(df):
    df = df.copy()
    n = len(df)
    # falha de transmissão: uma variável vazia isolada (~0,5%)
    for col in ["vibracao_mm_s", "temperatura_c", "corrente_a", "nivel_oleo_pct"]:
        idx = rng.choice(n, int(n * 0.0015), replace=False)
        df.loc[idx, col] = np.nan
    # picos espúrios de leitura (glitch do sensor, ~0,05%)
    idx = rng.choice(n, int(n * 0.0005), replace=False)
    df.loc[idx, "vibracao_mm_s"] = rng.uniform(18, 30, len(idx))
    # registros duplicados (~0,2%)
    dup = df.sample(frac=0.002, random_state=SEED)
    df = pd.concat([df, dup]).sort_values(["escada_id", "data_hora"]).reset_index(drop=True)
    return df


def main():
    escadas = montar_escadas()
    tempos = montar_tempos()
    leituras, atendimentos = [], []
    for esc in escadas.itertuples(index=False):
        df, at = simular_escada(esc, tempos)
        leituras.append(df)
        atendimentos.extend(at)

    leit = pd.concat(leituras, ignore_index=True)
    num = ["vibracao_mm_s", "temperatura_c", "corrente_a", "tensao_v", "nivel_oleo_pct"]
    leit[num] = leit[num].round(2)
    leit["velocidade_m_s"] = leit["velocidade_m_s"].round(4)
    leit = sujar(leit)
    leit.insert(0, "leitura_id", range(1, len(leit) + 1))

    man = pd.DataFrame(atendimentos).sort_values(["entrada", "escada_id"]).reset_index(drop=True)
    man.insert(0, "atendimento_id", range(1, len(man) + 1))
    man["duracao_min"] = ((man.saida - man.entrada).dt.total_seconds() / 60).round(0).astype(int)

    lim = pd.DataFrame([{"variavel": k, "unidade": u, "limite_alerta": a,
                         "limite_critico": c, "regra": s} for k, (u, a, c, s) in LIMITES.items()])

    escadas.drop(columns="risco").to_csv("escadas.csv", index=False)
    leit.to_csv("leituras_sensores.csv", index=False, date_format="%Y-%m-%d %H:%M")
    man.to_csv("atendimentos.csv", index=False, date_format="%Y-%m-%d %H:%M")
    lim.to_csv("limites_status.csv", index=False)
    print(f"escadas: {len(escadas)} | leituras: {len(leit)} | atendimentos: {len(man)}")
    print(leit.status.value_counts(normalize=True).round(3).to_string())


if __name__ == "__main__":
    main()
