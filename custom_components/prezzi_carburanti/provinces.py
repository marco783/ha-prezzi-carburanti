"""The 107 provinces: slug (same as the old mappacarburanti slugs) -> name, MIMIT sigle, region.

The city scope is the provincial capital: same slug, matched on Comune + sigla.
"""
# slug|Name|sigle (comma, incl. legacy Sardinian ones)|Region
_RAW = """
agrigento|Agrigento|AG|Sicilia
alessandria|Alessandria|AL|Piemonte
ancona|Ancona|AN|Marche
aosta|Aosta|AO|Valle d'Aosta
arezzo|Arezzo|AR|Toscana
ascoli-piceno|Ascoli Piceno|AP|Marche
asti|Asti|AT|Piemonte
avellino|Avellino|AV|Campania
bari|Bari|BA|Puglia
barletta|Barletta|BT|Puglia
belluno|Belluno|BL|Veneto
benevento|Benevento|BN|Campania
bergamo|Bergamo|BG|Lombardia
biella|Biella|BI|Piemonte
bologna|Bologna|BO|Emilia-Romagna
bolzano|Bolzano|BZ|Trentino-Alto Adige
brescia|Brescia|BS|Lombardia
brindisi|Brindisi|BR|Puglia
cagliari|Cagliari|CA|Sardegna
caltanissetta|Caltanissetta|CL|Sicilia
campobasso|Campobasso|CB|Molise
carbonia|Carbonia|SU,CI|Sardegna
caserta|Caserta|CE|Campania
catania|Catania|CT|Sicilia
catanzaro|Catanzaro|CZ|Calabria
chieti|Chieti|CH|Abruzzo
como|Como|CO|Lombardia
cosenza|Cosenza|CS|Calabria
cremona|Cremona|CR|Lombardia
crotone|Crotone|KR|Calabria
cuneo|Cuneo|CN|Piemonte
enna|Enna|EN|Sicilia
fermo|Fermo|FM|Marche
ferrara|Ferrara|FE|Emilia-Romagna
firenze|Firenze|FI|Toscana
foggia|Foggia|FG|Puglia
forli|Forlì|FC|Emilia-Romagna
frosinone|Frosinone|FR|Lazio
genova|Genova|GE|Liguria
gorizia|Gorizia|GO|Friuli-Venezia Giulia
grosseto|Grosseto|GR|Toscana
imperia|Imperia|IM|Liguria
isernia|Isernia|IS|Molise
la-spezia|La Spezia|SP|Liguria
laquila|L'Aquila|AQ|Abruzzo
latina|Latina|LT|Lazio
lecce|Lecce|LE|Puglia
lecco|Lecco|LC|Lombardia
livorno|Livorno|LI|Toscana
lodi|Lodi|LO|Lombardia
lucca|Lucca|LU|Toscana
macerata|Macerata|MC|Marche
mantova|Mantova|MN|Lombardia
massa|Massa|MS|Toscana
matera|Matera|MT|Basilicata
messina|Messina|ME|Sicilia
milano|Milano|MI|Lombardia
modena|Modena|MO|Emilia-Romagna
monza|Monza|MB|Lombardia
napoli|Napoli|NA|Campania
novara|Novara|NO|Piemonte
nuoro|Nuoro|NU,OG|Sardegna
oristano|Oristano|OR|Sardegna
padova|Padova|PD|Veneto
palermo|Palermo|PA|Sicilia
parma|Parma|PR|Emilia-Romagna
pavia|Pavia|PV|Lombardia
perugia|Perugia|PG|Umbria
pesaro|Pesaro|PU|Marche
pescara|Pescara|PE|Abruzzo
piacenza|Piacenza|PC|Emilia-Romagna
pisa|Pisa|PI|Toscana
pistoia|Pistoia|PT|Toscana
pordenone|Pordenone|PN|Friuli-Venezia Giulia
potenza|Potenza|PZ|Basilicata
prato|Prato|PO|Toscana
ragusa|Ragusa|RG|Sicilia
ravenna|Ravenna|RA|Emilia-Romagna
reggio-calabria|Reggio Calabria|RC|Calabria
reggio-emilia|Reggio Emilia|RE|Emilia-Romagna
rieti|Rieti|RI|Lazio
rimini|Rimini|RN|Emilia-Romagna
roma|Roma|RM|Lazio
rovigo|Rovigo|RO|Veneto
salerno|Salerno|SA|Campania
sassari|Sassari|SS,OT|Sardegna
savona|Savona|SV|Liguria
siena|Siena|SI|Toscana
siracusa|Siracusa|SR|Sicilia
sondrio|Sondrio|SO|Lombardia
taranto|Taranto|TA|Puglia
teramo|Teramo|TE|Abruzzo
terni|Terni|TR|Umbria
torino|Torino|TO|Piemonte
trapani|Trapani|TP|Sicilia
trento|Trento|TN|Trentino-Alto Adige
treviso|Treviso|TV|Veneto
trieste|Trieste|TS|Friuli-Venezia Giulia
udine|Udine|UD|Friuli-Venezia Giulia
varese|Varese|VA|Lombardia
venezia|Venezia|VE|Veneto
verbania|Verbania|VB|Piemonte
vercelli|Vercelli|VC|Piemonte
verona|Verona|VR|Veneto
vibo-valentia|Vibo Valentia|VV|Calabria
vicenza|Vicenza|VI|Veneto
viterbo|Viterbo|VT|Lazio
"""

PROVINCES = {}
for _line in _RAW.strip().splitlines():
    _slug, _name, _sigle, _region = _line.split("|")
    PROVINCES[_slug] = {"name": _name, "sigle": frozenset(_sigle.split(",")), "region": _region}
