"""
Guilherme Daher - RM98611
Gabriel Freitas - RM550187
Heitor Nobre - RM551539
Vinicius Yamashita - RM550908
Lucca Alexandre - 99700

╔══════════════════════════════════════════════════════════════╗
║  SKYGUARD — Coletor de Dados NASA FIRMS v2                  ║
║  Disciplina: RPA · FIAP ESW 4º Ano · Global Solution 2026  ║
╚══════════════════════════════════════════════════════════════╝

MUDANÇA v2:
  Trocado endpoint /country/csv/ pelo /area/csv/ com bounding box
  do Brasil. O endpoint de país dá erro 400 para países grandes.
  O endpoint de área é o recomendado pela própria NASA.

COMO USAR:
  1. pip install requests pandas
  2. Cole suas chaves abaixo
  3. python skyguard_coletor.py
"""

import requests
import pandas as pd
import json
import sys
from datetime import datetime
from io import StringIO

# ── CONFIGURAÇÃO ─────────────────────────────────────────────
FIRMS_KEY = "903d136919cea2119b08106b6234ac5f"   # firms.modaps.eosdis.nasa.gov/api/map_key/
OW_KEY    = "fcea61a94fe6d073e2760508832c2b71"  # openweathermap.org/api

# Aceita chaves como argumento: python skyguard_coletor.py FIRMS_KEY OW_KEY
if len(sys.argv) == 3:
    FIRMS_KEY = sys.argv[1]
    OW_KEY    = sys.argv[2]

# Bounding box do Brasil: oeste, sul, leste, norte
# Formato exigido pela Area API: "west,south,east,north"
BRASIL_BBOX = "-74,-34,-28,6"

# Estados para buscar clima
ESTADOS = {
    "MT": (-12.64, -55.42, "Mato Grosso"),
    "PA": (-3.79,  -52.48, "Pará"),
    "AM": (-3.47,  -65.10, "Amazonas"),
    "RO": (-10.83, -63.34, "Rondônia"),
    "TO": (-10.17, -48.33, "Tocantins"),
    "GO": (-15.83, -49.84, "Goiás"),
    "BA": (-12.97, -41.34, "Bahia"),
}


def verificar_chave():
    """Verifica se a MAP_KEY do FIRMS é válida antes de tudo."""
    print("\n[0/3] Verificando MAP_KEY do FIRMS...")
    url = f"https://firms.modaps.eosdis.nasa.gov/mapserver/mapkey_status/?MAP_KEY={FIRMS_KEY}"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        limit = data.get("transaction_limit", 0)
        used  = data.get("current_transactions", 0)
        print(f"  ✓ Chave válida | Limite: {limit} | Usadas: {used}")
        return True
    except Exception as e:
        print(f"  ❌ Chave inválida ou sem conexão: {e}")
        return False


def coletar_firms():
    """
    Etapa 1: Coleta focos via Area API com bounding box do Brasil.
    Mais confiável que a Country API para países grandes.
    Documentação: https://firms.modaps.eosdis.nasa.gov/api/area/
    """
    print("\n[1/3] Coletando dados da NASA FIRMS (Area API)...")

    # Endpoint correto: /api/area/csv/MAP_KEY/DATASET/BBOX/DAYS
    url = (
        f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
        f"{FIRMS_KEY}/MODIS_NRT/{BRASIL_BBOX}/2"
    )

    print(f"  URL: {url[:80]}...")

    try:
        resp = requests.get(url, timeout=60)  # timeout maior — dataset grande

        print(f"  Status HTTP: {resp.status_code}")

        if resp.status_code == 400:
            print("  ❌ Erro 400 — tentando dataset alternativo VIIRS_NOAA20_NRT...")
            url2 = (
                f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
                f"{FIRMS_KEY}/VIIRS_NOAA20_NRT/{BRASIL_BBOX}/1"     #<-- Ajustar o dia caso não tenha dados
            )
            resp = requests.get(url2, timeout=60)
            print(f"  Status HTTP (VIIRS): {resp.status_code}")

        resp.raise_for_status()

        if "latitude" not in resp.text:
            print(f"  Resposta recebida (primeiros 200 chars): {resp.text[:200]}")
            raise ValueError("Resposta não é um CSV válido — verifique a chave")

        df = pd.read_csv(StringIO(resp.text))
        print(f"  ✓ {len(df)} focos recebidos")
        return df

    except requests.exceptions.Timeout:
        print("  ❌ Timeout — servidor demorou demais. Tente novamente.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Erro de conexão: {e}")
        return None
    except ValueError as e:
        print(f"  ❌ {e}")
        return None


def transformar(df):
    """Etapa 2: Limpa, enriquece e classifica os dados."""
    print("\n[2/3] Transformando dados...")

    df = df.dropna(subset=["latitude", "longitude"])

    for col in ["latitude", "longitude", "brightness", "frp", "confidence"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    def nivel(frp):
        if frp > 200: return "CRÍTICO"
        if frp > 100: return "ALTO"
        if frp > 50:  return "MÉDIO"
        return "BAIXO"

    df["nivel_risco"]  = df["frp"].apply(nivel)
    df["is_alerta"]    = (df["frp"] > 50) & (df["confidence"] > 60)
    df["is_critico"]   = df["frp"] > 200

    print(f"  ✓ {len(df)} focos | {df['is_alerta'].sum()} alertas | {df['is_critico'].sum()} críticos")
    print(f"  ✓ FRP máximo: {df['frp'].max():.1f} MW | Confiança média: {df['confidence'].mean():.1f}%")

    return df


def coletar_clima():
    """Etapa 3: Clima via OpenWeather para estados prioritários."""
    print("\n[3/3] Coletando clima (OpenWeather)...")

    clima = {}
    for sigla, (lat, lon, nome) in ESTADOS.items():
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?lat={lat}&lon={lon}&appid={OW_KEY}&units=metric&lang=pt_br"
        )
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 401:
                print("  ❌ Chave OpenWeather inválida.")
                return {}
            resp.raise_for_status()
            d = resp.json()
            clima[sigla] = {
                "nome":     d.get("name", nome),
                "temp":     round(d["main"]["temp"]),
                "umidade":  d["main"]["humidity"],
                "sensacao": round(d["main"].get("feels_like", d["main"]["temp"])),
                "vento":    round(d["wind"].get("speed", 0) * 3.6, 1),
                "descricao": d["weather"][0]["description"] if d.get("weather") else "",
            }
            print(f"  ✓ {nome}: {clima[sigla]['temp']}°C / {clima[sigla]['umidade']}% umidade")
        except Exception as e:
            print(f"  ⚠ {nome}: {e}")

    return clima


def salvar(df, clima):
    """Salva JSON para o dashboard e CSV para evidência."""
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Colunas que existem no dataset
    colunas = [c for c in ["latitude","longitude","brightness","frp","confidence",
                            "acq_date","acq_time","daynight","satellite",
                            "nivel_risco","is_alerta","is_critico"] if c in df.columns]

    payload = {
        "coletado_em": agora,
        "fonte":       "NASA FIRMS MODIS_NRT · Area API",
        "metricas": {
            "total":      int(len(df)),
            "criticos":   int(df["is_critico"].sum()),
            "alertas":    int(df["is_alerta"].sum()),
            "frp_max":    round(float(df["frp"].max()), 1),
            "conf_media": round(float(df["confidence"].mean()), 1),
        },
        "focos": df[colunas].to_dict(orient="records"),
        "clima": clima,
    }

    with open("dados_firms.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    df.to_csv("dados_firms.csv", index=False, encoding="utf-8")

    print(f"\n{'='*45}")
    print(f"  ✅ dados_firms.json  → use no dashboard HTML")
    print(f"  ✅ dados_firms.csv   → evidência para o relatório")
    print(f"  Coletado em: {agora}")
    print(f"  Total: {payload['metricas']['total']} focos")
    print(f"  Críticos: {payload['metricas']['criticos']}")
    print(f"  FRP máximo: {payload['metricas']['frp_max']} MW")
    print(f"{'='*45}")
    print(f"\n  ➡  Abra o skyguard_final.html no Chrome")


def main():
    print("╔══════════════════════════════════════╗")
    print("║  SKYGUARD · Coletor NASA FIRMS v2    ║")
    print("╚══════════════════════════════════════╝")

    if "COLOQUE" in FIRMS_KEY:
        print("\n❌ Insira suas chaves no início do arquivo!")
        print("   Ou execute: python skyguard_coletor.py SUA_FIRMS_KEY SUA_OW_KEY")
        sys.exit(1)

    if not verificar_chave():
        sys.exit(1)

    df = coletar_firms()
    if df is None:
        sys.exit(1)

    df  = transformar(df)
    clm = coletar_clima()
    salvar(df, clm)


if __name__ == "__main__":
    main()