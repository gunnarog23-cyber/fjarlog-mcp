"""MCP-þjónn sem svarar spurningum um fjárlög á sviði félags- og húsnæðismála.

Gögn: Talnagögn úr fjárlagafrumvarpi 2026 (stjornarradid.is), CSV-skrá í möppunni gogn/.
Upphæðir eru í milljónum króna.
"""

from pathlib import Path

import pandas as pd
from mcp.server import MCPServer

# --- 1. Lesa gögnin einu sinni þegar þjónninn ræsist -------------------------
# Slóðin er reiknuð út frá staðsetningu þessarar skrár, ekki vinnumöppunni,
# því Claude Desktop ræsir þjóninn úr óskilgreindri möppu.
GOGN_MAPPA = Path(__file__).parent / "gogn"
CSV_SKRA = next(GOGN_MAPPA.glob("fjarlog_2026*.csv"))  # skráin úr frumvarpi 2026

# Málefnasviðin sem félags- og húsnæðismálaráðuneytið ber aðalábyrgð á.
# Síað er eftir málefnasviði en EKKI ráðuneyti, því ráðuneytið varð til í mars 2025
# og í fjárlögum 2025 voru húsnæðismál (31) enn skráð á innviðaráðuneytið.
MALEFNASVID = ["27", "28", "29", "30", "31", "32"]
MAELING = "Heildarútgjöld"  # Ein lína á hvert viðfang og ár; summan gefur heildina

_allt = pd.read_csv(CSV_SKRA, sep=";", decimal=",", encoding="utf-8-sig")
df = _allt[
    _allt["Málefnasvið"].str[:2].isin(MALEFNASVID) & (_allt["TegundNota"] == MAELING)
]

# Hvaða tegund af tölu er hvert ár (raun, samþykkt, tillaga eða áætlun)
AFURD_EFTIR_ARI = df.groupby("Ár")["Afurð"].first().to_dict()

mcp = MCPServer("fjarlog")


def _finna_malefnasvid(malefnasvid: str) -> str:
    """Tekur við númeri ('31') eða hluta af nafni ('húsnæði') og skilar fullu nafni."""
    leit = malefnasvid.strip().lower()
    oll = sorted(df["Málefnasvið"].unique())
    for nafn in oll:
        if nafn.split(" ")[0] == leit or leit in nafn.lower():
            return nafn
    raise ValueError(f"Fann ekki málefnasvið '{malefnasvid}'. Í boði: {oll}")


# --- 2. Verkfærin -------------------------------------------------------------
@mcp.tool()
def listi_malefnasvid() -> list[dict]:
    """Skilar lista yfir málefnasvið félags- og húsnæðismála (27–32) í fjárlögum,
    ásamt heildarútgjöldum hvers sviðs árið 2026 (frumvarp) í milljónum króna.
    Upphæðir eru fyrir málefnasviðið í heild, óháð ráðuneyti.
    Notaðu þetta fyrst til að sjá hvaða málefnasvið eru til."""
    ar_2026 = df[df["Ár"] == 2026].groupby("Málefnasvið")["Upphæð"].sum()
    return [
        {"malefnasvid": nafn, "heildarutgjold_2026_mkr": round(upphaed, 1)}
        for nafn, upphaed in ar_2026.sort_values(ascending=False).items()
    ]


@mcp.tool()
def utgjold_eftir_arum(malefnasvid: str) -> dict:
    """Skilar heildarútgjöldum eins málefnasviðs fyrir hvert ár 2024–2028 í milljónum króna.

    malefnasvid: númer (t.d. '31') eða hluti af nafni (t.d. 'húsnæði').

    Athugið hvaðan hver tala kemur (dálkurinn 'tegund'):
    2024 = Ríkisreikningur (raunveruleg útgjöld), 2025 = Fjárlög (samþykkt),
    2026 = Frumvarp (tillaga), 2027–2028 = Áætlun."""
    nafn = _finna_malefnasvid(malefnasvid)
    eftir_arum = df[df["Málefnasvið"] == nafn].groupby("Ár")["Upphæð"].sum()
    return {
        "malefnasvid": nafn,
        "eining": "milljónir króna",
        "ar": [
            {"ar": int(ar), "tegund": AFURD_EFTIR_ARI[ar], "upphaed_mkr": round(u, 1)}
            for ar, u in eftir_arum.items()
        ],
    }


@mcp.tool()
def bera_saman_ar(malefnasvid: str, fra_ar: int = 2024, til_ar: int = 2026) -> dict:
    """Ber saman útgjöld málefnasviðs milli tveggja ára, sundurliðað eftir málaflokkum,
    með breytingu í milljónum króna og prósentum.

    Sjálfgefið er 2024 (raunveruleg útgjöld skv. ríkisreikningi) borið saman við
    2026 (fjárheimildir skv. frumvarpi). Ár í boði: 2024–2028.
    Ath: málaflokkar geta færst milli málefnasviða milli ára, sem getur skýrt stórar breytingar."""
    nafn = _finna_malefnasvid(malefnasvid)
    gogn = df[(df["Málefnasvið"] == nafn) & (df["Ár"].isin([fra_ar, til_ar]))]
    tafla = gogn.pivot_table(
        index="Málaflokkur", columns="Ár", values="Upphæð", aggfunc="sum", fill_value=0
    )
    nidurstada = []
    for flokkur, rod in tafla.iterrows():
        fra, til = rod.get(fra_ar, 0), rod.get(til_ar, 0)
        nidurstada.append(
            {
                "malaflokkur": flokkur,
                f"{fra_ar}_mkr": round(fra, 1),
                f"{til_ar}_mkr": round(til, 1),
                "breyting_mkr": round(til - fra, 1),
                "breyting_pct": round((til - fra) / fra * 100, 1) if fra else None,
            }
        )
    return {
        "malefnasvid": nafn,
        "fra": f"{fra_ar} ({AFURD_EFTIR_ARI.get(fra_ar)})",
        "til": f"{til_ar} ({AFURD_EFTIR_ARI.get(til_ar)})",
        "malaflokkar": nidurstada,
    }


if __name__ == "__main__":
    mcp.run()
