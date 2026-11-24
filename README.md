# Fjárlög – félags- og húsnæðismál

MCP-þjónn sem gerir Claude kleift að svara spurningum um fjárlög ríkisins beint úr opinberum talnagögnum, ásamt tveimur greiningum í Jupyter um útgjöld til félags- og húsnæðismála (málefnasvið 27–32) árin 2024–2029.

**Markmið:** Að sýna í smækkaðri mynd vinnu greinanda á sviði ríkisfjármála: að sækja og hreinsa fjárlagagögn, bera saman fjárheimildir og útkomu, meta hversu vel áætlanir standast og gera gögnin aðgengileg öðrum með einföldu viðmóti.

---

## Helstu niðurstöður

**Spá vs. útkoma** ([`samanburdur_2027.ipynb`](samanburdur_2027.ipynb))

- **Fjárlög 2025 héldu ekki.** Raunútgjöld ríkisins urðu um **149 ma.kr. (~10%) umfram fjárlög**. Stærsti liðurinn er þó bókhaldsleg breyting á lífeyrisskuldbindingum (málefnasvið 33), ekki útgreiðslur.
- **Húsnæðismál nýttu 22% minna** en fjárlög 2025 heimiluðu, á meðan flest önnur félagsmálasvið fóru fram úr.
- **Áætlanir vanmeta.** Áætlunin fyrir 2027 í fjármálaáætlun gerði ráð fyrir nánast engum vexti, en frumvarpið ári síðar er **~6% (95 ma.kr.) hærra**. Mest er frávikið í vinnumarkaði og atvinnuleysi (+33%).

**Þróun 2024–2028** ([`greining.ipynb`](greining.ipynb))

- Félags- og húsnæðismál eru stöðugt um **25,6% af heildarútgjöldum** ríkisins.
- Mikil hækkun í örorku 2024→2026 (+21,5%) er að hluta **endurflokkun milli málaflokka** vegna nýs örorkulífeyriskerfis, ekki eingöngu raunaukning.
- Húsnæðismál lækka um 18,7% 2024→2026 og halda áfram að lækka í áætlun til 2028.

> Allar upphæðir eru í milljónum króna á **nafnvirði**. Athugið að árin eru ólíkar tegundir talna: ríkisreikningur (raun), fjárlög (samþykkt), frumvarp (tillaga) og áætlun.

---

## Innihald

| Skrá | Lýsing |
|---|---|
| `server.py` | MCP-þjónn með þremur verkfærum (sjá að neðan) |
| `greining.ipynb` | Þróun útgjalda eftir málefnasviðum, málaflokkum og tegundum útgjalda |
| `samanburdur_2027.ipynb` | *Vintage*-samanburður: sama árið í frumvarpi 2026 og 2027 til að meta frávik frá fjárlögum og áætlunum |
| `gogn/` | Talnagögn úr fjárlagafrumvörpum 2026 (CSV) og 2027 (Excel) |

### MCP-verkfærin

[Model Context Protocol](https://modelcontextprotocol.io) er opinn staðall sem leyfir gervigreind eins og Claude að kalla á forrit og gögn. Í stað þess að líma töflur inn í spjall getur notandi spurt *„Hvernig hafa útgjöld til húsnæðismála þróast?“* og Claude sækir svarið sjálft úr gögnunum.

| Verkfæri | Hvað það gerir |
|---|---|
| `listi_malefnasvid` | Listar málefnasvið 27–32 með heildarútgjöldum 2026 |
| `utgjold_eftir_arum` | Útgjöld eins málefnasviðs 2024–2028, merkt eftir tegund (raun/fjárlög/frumvarp/áætlun) |
| `bera_saman_ar` | Ber saman tvö ár, sundurliðað eftir málaflokkum, með breytingu í m.kr. og % |

Málefnasvið er hægt að tilgreina með númeri (`"31"`) eða hluta af nafni (`"húsnæði"`).

---

## Aðferð og fyrirvarar

- **Síað eftir málefnasviði, ekki ráðuneyti.** Félags- og húsnæðismálaráðuneytið var stofnað í mars 2025, og í fjárlögum 2025 voru húsnæðismál enn skráð á innviðaráðuneytið. Síun eftir ráðuneyti myndi því skekkja samanburð milli ára.
- **Aðeins `Heildarútgjöld`.** Sama upphæð birtist í gögnunum undir mörgum mælingum (`Gjöld`, `Greiðsla`, `Fjárhæð` o.fl.). Án síunar tvítelst allt.
- **Rekstrargrunnur.** Ríkisreikningur færir breytingar á lífeyrisskuldbindingum sem gjöld, svo frávik frá fjárlögum eru ekki öll útgreiðslur.
- **Nafnvirði.** Tölur eru ekki staðvirtar. Næsta skref væri að staðvirða með vísitölu neysluverðs.

---

## Uppsetning

Verkefnið notar [uv](https://docs.astral.sh/uv/) og Python 3.14.

```bash
uv sync                 # setur upp pakka
uv run server.py        # ræsir MCP-þjóninn (til prófunar)
```

**Tenging við Claude Desktop:** bættu þessu við `claude_desktop_config.json` og endurræstu Claude Desktop:

```json
{
  "mcpServers": {
    "fjarlog": {
      "command": "uv",
      "args": ["run", "--directory", "C:\\slóð\\að\\fjarlog-mcp", "server.py"]
    }
  }
}
```

**Notebook:** opnaðu möppuna í VS Code og veldu `.venv` sem kernel.

---

## Gögn

Talnagögn sem fylgja fjárlagafrumvörpum 2026 og 2027, birt á [stjornarradid.is](https://www.stjornarradid.is). Opinber gögn.

---

*Gunnar Óli Gunnarsson – MSc í stafrænni stjórnun og gagnagreiningu.*
