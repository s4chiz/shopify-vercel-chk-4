import asyncio
import time
import sys
import os
import random
from flask import Flask, request, Response

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sh_checker import process_card, parse_cc_string, extract_clean_response

app = Flask(__name__)

SITES = [
    "caterkids.myshopify.com", "the-nesting-house.myshopify.com", "soloeyeware.myshopify.com",
    "cyclopesco.myshopify.com", "big-little-dogs.myshopify.com", "paper-plane-designs.myshopify.com",
    "chazdean.com", "utsumiamerica.com", "spatty-2.myshopify.com", "chlobo-uk.myshopify.com",
    "blackflys.myshopify.com", "cocofranscais-com.myshopify.com", "mnjohn.com",
    "chunkynz.myshopify.com", "mooala.com", "shorebags.com", "cocomatsnmore.myshopify.com",
    "keukabluegifts.myshopify.com", "renewtronics.myshopify.com", "thestarfishface.com",
    "redpepper-cases.myshopify.com", "chainsofstyle.myshopify.com", "modket.myshopify.com",
    "www.topangascents.com", "scootertrade.myshopify.com", "store.mtjoyband.com",
    "www.momoslimes.com", "wallniture.myshopify.com", "dapper-boi-store.myshopify.com",
    "juliehanandesign.myshopify.com", "legacybikepark.com", "curtainsdirect2u.myshopify.com",
    "rawspicebar1.myshopify.com", "colnart.myshopify.com", "tricer-usa.myshopify.com",
    "thunderthundertea.com", "local-heroes-comics.myshopify.com", "034c76-74-2.myshopify.com",
    "whiteriver-mouldings.myshopify.com", "test-rhf.myshopify.com", "www.storeyfamilyfarm.com",
    "country-creek-llc.myshopify.com", "jadefisher.myshopify.com", "the-extra-detail.myshopify.com",
    "theartofsoccer.shop", "apkbridal.myshopify.com", "peakcocktails.com", "shop.aansw.org.au",
    "squire-locks.myshopify.com", "the-blue-deal.myshopify.com", "the-ruffled-daisy.myshopify.com",
    "amika-1.myshopify.com", "www.artifactpuzzles.com", "emily-mae-creatives.myshopify.com",
    "gonzales-party-store.myshopify.com", "cliphair-uk.myshopify.com", "ne-student-services.myshopify.com",
    "kydexcustoms.myshopify.com", "frame-my-mirror.myshopify.com", "prime-party.myshopify.com",
    "cote-cache.myshopify.com", "dffde8-3.myshopify.com", "cr-hut.myshopify.com",
    "modular-closets.myshopify.com", "questnutrition.myshopify.com", "chapterorganics.myshopify.com",
    "bafd2a.myshopify.com", "dannys-wine-beer-supplies.myshopify.com", "clark-products-nz.myshopify.com",
    "www.4ocean.com", "thelittlerig.myshopify.com", "penboutique.myshopify.com",
    "cotton-bag-co.myshopify.com", "maineventemblems.com", "vintagepostage.myshopify.com",
    "awaydaysfootball.com", "janitorial-superstore.myshopify.com", "bee-keeping-gear.myshopify.com",
    "wagsandwine.myshopify.com", "foreveremdesigns.com", "fragrancelord-com.myshopify.com",
    "permanent-baggage.myshopify.com", "www.moirabeauty.com", "city-mattress.myshopify.com",
    "randall-pich.myshopify.com", "dani-barbe.myshopify.com", "www.pugliepug.com",
    "militadowatch.com", "countrylivingmarketplace.myshopify.com", "danieltaywh.myshopify.com",
    "www.chavibes.com", "vela-scarves.myshopify.com", "daily-stoic-prints.myshopify.com",
    "colorfull-plates-kids-tableware-and-lifestyle.myshopify.com", "www.coleyhome.com",
    "the-swan-princess.myshopify.com", "peaceimagesjewelry.myshopify.com", "relentless-tactical.myshopify.com",
    "vesselbags.myshopify.com", "cheaper-online-co-uk.myshopify.com", "love-sew.com",
    "shoppriorattire.myshopify.com", "crystalum.myshopify.com", "kfcfoundation.myshopify.com",
    "gspawn.com", "kiboubag.com", "cookanyday.myshopify.com", "ctp2.myshopify.com",
    "mod-mex.myshopify.com", "iceshaker.myshopify.com", "nmtcb.myshopify.com",
    "brodandtaylor.com", "katvr.myshopify.com", "cissy-wears.myshopify.com",
    "challengecoinnation.com", "www.materiol.com", "codeword-hats.myshopify.com",
    "cultdesignau.myshopify.com", "skywalker-trampolines.myshopify.com", "crystals-newagestore.myshopify.com",
    "julie-sinden-handmade.myshopify.com", "cycleme-tots.myshopify.com", "d34037.myshopify.com",
    "curoie.com", "cabinetsndoors-dev.myshopify.com", "candy-mail-uk.myshopify.com",
    "craftbuddy-shop.myshopify.com", "eno-nation.myshopify.com", "dreams-and-rainbows.myshopify.com",
    "cosys-castles.myshopify.com", "museum-for-art-in-wood.myshopify.com", "classic-car-performance.myshopify.com",
    "unboxme-dev.myshopify.com", "so-chic-boutique-peoria.myshopify.com", "crockett-and-jones-row.myshopify.com",
    "skateboardingstickers.myshopify.com", "pencilmeinshop.co.uk", "elder-statesman.com",
    "chikahisastudio.myshopify.com", "camilynbeth.com", "132461-96.myshopify.com",
    "d-design-6303.myshopify.com", "smrtft.com", "dyper.com", "d80ca4-5.myshopify.com",
    "danilo-promotions.myshopify.com", "little-lovies-boutique.myshopify.com", "filmneverdie-com.myshopify.com",
    "bryson-city-outdoors.myshopify.com", "coteriebabyinc.myshopify.com", "www.retrowaviest.com",
    "rubber-plates.myshopify.com", "littlestarplans.com", "nettingpros.com",
    "crazyvictor.myshopify.com", "crystals-healing-shop.myshopify.com", "chesterfieldbags.myshopify.com",
    "cjstickershop.com", "uncommon-james.myshopify.com", "melin.com", "rawgeneration.com",
    "hueloco.com", "getpressedbysteph.com", "childperfume.myshopify.com", "levenger.myshopify.com",
    "glass-boards-direct.myshopify.com", "etgb.myshopify.com", "treebicycleco.myshopify.com",
    "bellaandoliversoap.com", "strung-by-stroh.myshopify.com", "chibimikichan.myshopify.com",
    "sunny-health-and-fitness.myshopify.com", "ee8417.myshopify.com", "lust-minerals.myshopify.com",
    "planterhomawholesale.com", "sandiegowavefc.store", "illuminate-vintage.myshopify.com",
    "southern-anchor-ky.myshopify.com", "momoslimes.com", "theshelfshop.com",
    "sunbelt-mfg-co.myshopify.com", "respire.com", "rock-solid-inc.myshopify.com",
    "cluse-store-dev.myshopify.com", "easy-pickins2.myshopify.com", "shiftathleisurewear.com",
    "greenworkstools.myshopify.com", "crushgrind.myshopify.com", "le-mini-macaron-2.myshopify.com",
    "www.bioliteenergy.com", "chandelierslife.myshopify.com", "bethanyjoyart.com",
    "www.rutherfordtrophies.com", "yearpins.myshopify.com", "fomato.myshopify.com",
    "utomic-design.myshopify.com", "sharetea-everett-online.myshopify.com", "vv6kxd-np.myshopify.com",
    "naturebag.myshopify.com", "west3d-printing.myshopify.com", "beastro.myshopify.com",
    "ricketyrose.co.uk", "dalstrong.myshopify.com", "kyndkits.myshopify.com",
    "kmtools.com", "jenn-co.myshopify.com", "rebrandskincare.com",
    "mabelandjess.com", "brunekitchen.com", "cibowares.myshopify.com",
    "deloasquiltshop.com", "trycloudy.com", "recapture-beauty.myshopify.com",
    "d6aa29.myshopify.com", "athrbeauty.com", "florida-sunseeker.myshopify.com",
    "clionadh-cosmetics.myshopify.com", "thefarmersdaughterfibers.com", "clubit-co-uk.myshopify.com",
    "alpartyballoons.com", "crystalbarsoap.com", "concourse-golf.myshopify.com",
    "www.elder-statesman.com", "afsound.myshopify.com", "thefarmstandonrussellroad.myshopify.com",
    "cottonwood-gift-co.myshopify.com", "crane-and-canopy.myshopify.com", "pork-king-good.myshopify.com",
    "corvetteguys.myshopify.com", "container-one.myshopify.com", "rifle-paper.myshopify.com",
    "provencebeauty.com", "alpine-luddites.myshopify.com", "childfund.myshopify.com",
    "custom-cowboy-shop.myshopify.com", "dbs838.myshopify.com", "padawan-outpost.myshopify.com",
    "thac-store.myshopify.com", "www.maltosefalcons.com", "mysuds2go.com",
    "d73906-8c.myshopify.com", "olfactif.myshopify.com", "linenloftlakewood.myshopify.com",
    "www.foreveremdesigns.com", "coveryourwall.myshopify.com", "coucou-boston.myshopify.com",
    "lively-ghosts.myshopify.com", "bungubox.shop", "vilros-com.myshopify.com",
    "coconu.com", "boodywearus.myshopify.com", "vytest.myshopify.com",
    "seek-outdoor.myshopify.com", "boardwalk-numismatics.myshopify.com", "larepublicasuperfoods.com",
    "maximum-crafts.myshopify.com", "shop.windchillultimate.com", "hello-nancy-toys.myshopify.com",
    "geomatters.myshopify.com", "the-parlor-company.myshopify.com", "reaction-tackle.myshopify.com",
    "cleaning-products-uk.myshopify.com", "boujeebloomdesignco.myshopify.com", "qualyair.myshopify.com",
    "bluntpower.myshopify.com", "schaesplace.com", "countryfields.myshopify.com",
    "ecovibestyle.com", "www.johnnysgoods.com", "zenintcg.myshopify.com",
    "onlineliquor.com", "ruthcharlotteclothing.com", "beardsgaard.myshopify.com",
    "clara-and-macy.myshopify.com", "cwmenswear.myshopify.com", "corter.myshopify.com",
    "vka5mx-7x.myshopify.com", "cherry-collectables.myshopify.com", "curlsmith.myshopify.com",
    "comiso-coffee.myshopify.com", "rosecityoriginals.com", "space-bathroom.myshopify.com",
    "hebrew-type.myshopify.com", "daal-furniture.myshopify.com", "spiritsoffrance.com.au",
    "clara-sunwoo.myshopify.com", "curlsmith.com", "divahglaminc.myshopify.com",
    "creating-the-difference.myshopify.com", "choiceflooringllc.myshopify.com", "six-stories.myshopify.com",
    "www.mistolino.com", "chasing-foxes-store.myshopify.com", "louisianatrophies.com",
    "cramilo-sunglasses.myshopify.com", "crafty-kylies-facebook-store.myshopify.com", "cubby-bakehouse.myshopify.com",
    "legitgrails.com", "troyleedesigns.myshopify.com",
    "cookiegood.myshopify.com", "color-cord-dev.myshopify.com", "cowsandcrayons.com",
    "mishahawaii.myshopify.com", "stickii-club.myshopify.com", "kris-nations.myshopify.com",
    "crazy-catch-uk.myshopify.com", "labyrinthos.co", "collectiveminds-uk.myshopify.com",
    "cheapfabricsuk.myshopify.com",
    "charliemckay.myshopify.com", "koreessentials.myshopify.com", "dungeons-by-dan.myshopify.com",
    "ficus-1573.myshopify.com", "eatbobos.myshopify.com", "flush-packaging.myshopify.com",
    "hilary-rhoda.myshopify.com", "simifashions.myshopify.com", "home-county-candle-co.myshopify.com",
    "little-label-co.myshopify.com", "hibiscus-test.myshopify.com", "ninja-outdoorsman.myshopify.com",
    "cibowares.myshopify.com", "packagemint.myshopify.com", "kowtowclothing.myshopify.com",
    "the-london-bee-company.myshopify.com", "french-sweet.myshopify.com", "raise-them-well.myshopify.com",
    "we-go-home.myshopify.com", "high5-store.myshopify.com", "padawan-outpost.myshopify.com",
    "coral-and-ink.myshopify.com", "static-arc.myshopify.com", "creative-paradigm-llc.myshopify.com",
    "lavishshoestring.myshopify.com", "florida-sunseeker.myshopify.com", "crates2u-2.myshopify.com",
    "black-white-coffee.myshopify.com", "poopourri-3.myshopify.com", "pencil-me-in-shop.myshopify.com",
    "spicedivine-2.myshopify.com", "snackboxusa.myshopify.com", "loop-generation.myshopify.com",
    "f606bf-e9.myshopify.com", "anotherseasonwaco.myshopify.com", "lesports.myshopify.com",
    "rawkanvas.myshopify.com", "elegant-lashes.myshopify.com", "twinings-uk.myshopify.com",
    "briogeo-hair-care.myshopify.com", "d8adf0-6.myshopify.com", "gcl-centre.myshopify.com",
    "spyhouse-coffee-roasting-co.myshopify.com", "the-wiltshire-tea-company-3.myshopify.com",
    "c599c0.myshopify.com", "thehouseofemily.myshopify.com", "prime-party.myshopify.com",
    "little-mouse-clothing-and-gifts.myshopify.com", "upfitters-wholesale.myshopify.com",
    "givingtreesnacks.myshopify.com", "glia2.myshopify.com", "hakuhodo-usa.myshopify.com",
    "cluse-store-dev.myshopify.com", "kids-fair-llc.myshopify.com", "papavector.myshopify.com",
    "kodiakcakes.myshopify.com", "iheybikeca.myshopify.com", "madeleineholloway.myshopify.com",
    "we-are-hairy-people.myshopify.com", "profusion-us.myshopify.com", "esavingsblog.myshopify.com",
    "red-paddle-co-en.myshopify.com", "alpine-luddites.myshopify.com", "greenworkstools.myshopify.com",
    "oh-boy-records.myshopify.com", "vela-scarves.myshopify.com", "debeauvoir-deli.myshopify.com",
    "clionadh-cosmetics.myshopify.com", "littlevegpatch.myshopify.com", "groovygolfer.myshopify.com",
    "stream-designz.myshopify.com", "spareshut.myshopify.com", "saar-soleares.myshopify.com",
    "hobby-land-nz.myshopify.com", "flyingeyesoptics.myshopify.com", "what-goes-around-abq.myshopify.com",
    "filteroutlet.myshopify.com", "blubohoo.myshopify.com", "wall-panels-australia.myshopify.com",
    "sunshinemall-k-beauty.myshopify.com", "killstar-eu.myshopify.com", "karla-cosmetics.myshopify.com",
    "shopvolashes.myshopify.com", "designmehair.myshopify.com", "lovetodream-au.myshopify.com",
    "onyx-straps-llc.myshopify.com", "a4y1xd-3e.myshopify.com", "sol-society-scrubs.myshopify.com",
    "life-vac-australia.myshopify.com", "matsuru-canada.myshopify.com", "popbeauty.myshopify.com",
    "project-phoebe.myshopify.com", "cult-glitter.myshopify.com", "43andcompany.myshopify.com",
    "rellery.myshopify.com", "balloons-and-paper-inc-2.myshopify.com", "orvgirlz.myshopify.com",
    "revolution-fibers.myshopify.com", "semen-tanks.myshopify.com", "wani0a-bd.myshopify.com",
    "dirt-cheep-music.myshopify.com", "1thrive.myshopify.com", "addiesdivewatches.myshopify.com",
    "bodybest-ca.myshopify.com", "therapy-fun-store.myshopify.com", "little-prince-london.myshopify.com",
    "playspire.myshopify.com", "makeitlastpatterns.myshopify.com", "the-real-nappy-cafe.myshopify.com",
    "liftglucose.myshopify.com", "ecfc-2.myshopify.com", "jezebel-gallery.myshopify.com",
    "elittledirect.myshopify.com", "d95ccc.myshopify.com", "doctoraromas.myshopify.com",
    "ozark-compost-swap.myshopify.com", "innovativeconcrete.myshopify.com", "yearpins.myshopify.com",
    "chicologyinc.myshopify.com", "hawkwatch-international.myshopify.com", "gregorysgraphics.myshopify.com",
    "filmneverdie-com.myshopify.com", "grey-jam-press.myshopify.com", "hartford-prints-store.myshopify.com",
    "disegno-fine-jewellery.myshopify.com", "getevo.myshopify.com", "amplifycosmetics.myshopify.com",
    "girl-be-brave.myshopify.com", "graftobian-make-up-company.myshopify.com", "crystalynkae.myshopify.com",
    "edo-performance.myshopify.com", "commercial-real-estate-success-strategies.myshopify.com",
    "piotrlife.myshopify.com", "au-vodka.myshopify.com", "evatrends.myshopify.com",
    "alpine-imports.myshopify.com", "shatterproofarchery.myshopify.com", "theorangebuffalo.myshopify.com",
    "waihana.myshopify.com", "mr-mrs-vintage.myshopify.com", "lifespan-kids.myshopify.com",
    "bright-stem.myshopify.com", "fresh-balls.myshopify.com", "longhouse-dev.myshopify.com",
    "wasecabiomes.myshopify.com", "haven-mattress.myshopify.com", "stationery-geek.myshopify.com",
    "sampenny1.myshopify.com", "diapersdirect.myshopify.com", "be-true-western.myshopify.com",
    "pompomz.myshopify.com", "towelwarmers.myshopify.com", "alcove-shop.myshopify.com",
    "biancalorenne-co-nz.myshopify.com",
    "simplyhammocks.myshopify.com", "blanks-blanks-baby.myshopify.com", "wholesome-hub.myshopify.com",
    "davines-usa.myshopify.com", "admiralrow.myshopify.com", "b2976e.myshopify.com",
    "detour-sunglasses.myshopify.com", "word-of-mouth-floors-llc.myshopify.com", "aerogenics.myshopify.com",
    "bentley-jewellery.myshopify.com", "greatbasingraphics.myshopify.com", "thesuspensionexperts.myshopify.com",
    "bfcosmetics.myshopify.com", "repeaterstore.myshopify.com", "moogoo-usa.myshopify.com",
    "nationaltreecompany.myshopify.com", "trubrands.myshopify.com", "medikate-skincare.myshopify.com",
    "so-chic-boutique-peoria.myshopify.com", "by-lohn.myshopify.com", "by-sophia-lee.myshopify.com",
    "jackmason.myshopify.com", "aspenjay.myshopify.com", "stonestreetcoffee.myshopify.com",
    "dopeslimes.myshopify.com", "osp-cases.myshopify.com", "life-of-riley-2.myshopify.com",
    "hma-labs.myshopify.com", "livwatches.myshopify.com", "fcpx-full-access.myshopify.com",
    "beddys.myshopify.com", "info-engraving-keys.myshopify.com", "rebel-nell.myshopify.com",
    "hilltop-packs-llc.myshopify.com", "totyskincare.myshopify.com", "newwebsite2.myshopify.com",
    "knitspot.myshopify.com", "milina-london.myshopify.com", "art-supplies-australia.myshopify.com",
    "complete-unity-yoga.myshopify.com", "denise-albright.myshopify.com", "8bd59e-de.myshopify.com",
]


@app.route("/chk", methods=["GET"])
@app.route("/", methods=["GET"])
def chk():
    cc_raw = request.args.get("cc", "").strip()
    site   = request.args.get("site", "").strip()
    proxy  = request.args.get("proxy", "").strip()

    if not cc_raw:
        return Response("Error: missing 'cc' parameter (format: num|mm|yy|cvv)", status=400, mimetype="text/plain")

    # Pick a random site from the hardcoded pool if none supplied
    if not site:
        site = "https://" + random.choice(SITES)
    elif not site.startswith("http"):
        site = "https://" + site

    try:
        parts = parse_cc_string(cc_raw)
        cc  = parts["cc"]
        mes = parts["mes"]
        ano = parts["ano"]
        cvv = parts["cvv"]
    except Exception as e:
        return Response(f"Error: invalid cc format — {e}\nExpected: num|mm|yy|cvv", status=400, mimetype="text/plain")

    t0 = time.time()
    success = False
    message = "ERROR"
    gateway = "Shopify Payments"
    total_price = "0"
    currency = "USD"

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            success, message, gateway, total_price, currency = loop.run_until_complete(
                asyncio.wait_for(
                    process_card(cc, mes, ano, cvv, site, proxy_str=proxy or None),
                    timeout=55,
                )
            )
        finally:
            loop.close()
    except asyncio.TimeoutError:
        message = "TIMEOUT"
    except Exception as e:
        message = str(e) or type(e).__name__

    elapsed = round(time.time() - t0, 2)
    clean_msg = extract_clean_response(message)
    amount_str = (
        f"{total_price} {currency.upper()}"
        if total_price and str(total_price) not in ("0", "0.0", "0.00")
        else total_price or "0"
    )
    gateway_str = gateway if gateway and gateway not in ("", "UNKNOWN") else "Shopify Payments"

    body = (
        f"Cc: {cc_raw}\n"
        f"Response: {clean_msg}\n"
        f"Gateway: {gateway_str}\n"
        f"Amount: {amount_str}\n"
        f"Site: {site}\n"
        f"Proxy: {proxy or 'None'}\n"
        f"Time: {elapsed}s"
    )
    return Response(body, status=200, mimetype="text/plain")
