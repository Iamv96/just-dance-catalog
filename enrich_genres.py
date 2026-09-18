import json
import csv
import re
import os

WORKSPACE_DIR = r"c:\Users\Ignac\Documents\Proyectos IA\Lista canciones Just Dance"
JSON_PATH = os.path.join(WORKSPACE_DIR, "canciones_just_dance.json")
CSV_PATH = os.path.join(WORKSPACE_DIR, "canciones_just_dance.csv")
JS_PATH = os.path.join(WORKSPACE_DIR, "data.js")

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    songs = json.load(f)

# Direct exact & substring rules (Artist or Title or MapName)
RULES = [
    # Infantil / Kids
    (r"(the just dance kids|tom zehnder|kidsabc|kidscrocodile|kidsdayo|kidsfive|kidsfraggle|kidshickory|kidsifyou|kidsilike|kidsjingle|kidsmagic|kidsmary|kidspirate|kidsproblem|kidsthe|kidswego|kidswheels|kidsworking|baby shark|gummy bear|crazy frog|angry birds|alvin|wiggles)", "Infantil"),
    
    # Banda Sonora / Disney / Musical
    (r"(disney|violetta|a\.n\.t\. farm|soundtrack|broadway|musical|camp rock|high school musical|descendants|frozen|moana|encanto|the lion king|aladdin|beauty and the beast|the little mermaid|tangled|tarzan|mulan|hercules|mary poppins|the greatest showman|lalaland|la la land|mamma mia|grease|hairspray|wicked|hamilton|gombault|in the heights|ghostbusters|space jam|footloose|fame|eye of the tiger|rock'n roll - teenage uprising)", "Banda Sonora / Musical"),

    # K-Pop
    (r"(bts|blackpink|twice|psy|2ne1|bigbang|exo|red velvet|aespa|itzy|stray kids|newjeans|le sserafim|super m|momoland|k/da|sunmi|hyuna|clc|everglow|ateez|txt|seventeen|nct|monsta x|got7|shinee|girls' generation|girls generation|boa|wonder girls|gidle|\(g\)i-dle|enhypen|ive|stayc|4 walls|gagnam|gangnam style|gentleman|daddy|kill this love|how you like that|ddu-du|boombayah|as if it's your last|ice cream|dynamite|butter|boy with luv|fancy|feel special|the feels|pop/stars|more|bbtomboy|wannabe|loco|sneakers|god's menu|maniac|thunderous|hype boy|omg|super shy|antifragile|fearless|unforgiven|jopping|bap3|kick it)", "K-Pop"),

    # J-Pop
    (r"(e-girls|akb48|happiness|megumi tatsumi|garnidelia|perfume|kyary pamyu pamyu|babymetal|yoasobi|kenshi yonezu|ado|lisa|utada hikaru|ayumi hamasaki|arashi|official hige dandism|king gnu|wanko ni mero|sokusu|follow me|koi suru|fortune cookie|joyful|we can fly|gokuraku|ponponpon|ninja re bang bang|tsunagaru)", "J-Pop"),

    # C-Pop
    (r"(jolin tsai|jay chou|tfboys|kris wu|phoenix legend|wang rong|chopstick brothers|wanting qu|chris lee|wilber pan|angela chang|shanghai restoration project|namewee|g\.e\.m\.|lexie liu|lay zhang|jackson wang|bailemen|bedtime stories|big bowl|big dreamer|dancing diva|chick chick|coolest ethnic|gee \(哎呀\)|play \(我呸\)|real love|little apple|us under the sunshine|adoration to happiness)", "C-Pop"),

    # Reggaetón & Urbano / Pop Latino
    (r"(daddy yankee|bad bunny|j balvin|maluma|ozuna|anuel|karol g|rosal[ií]a|rauw alejandro|farruko|nicky jam|wisin|yandel|don omar|becky g|natti natasha|sech|myke towers|camilo|sebastian yatra|manuel turizo|feid|bizarrap|quevedo|peso pluma|el alfa|chayanne|luis fonsi|shakira|enrique iglesias|ricky martin|marc anthony|juanes|gloria estefan|pitbull|alvaro soler|cuba club|los del rio|lou bega|selena|thalia|paulina rubio|prince royce|romeo santos|gente de zona|michel tel[oó]|gusttavo lima|anitta|mc fioti|mc zaac|pabllo vittar|lexa|ludmilla|kevinho|aventura|despacito|gasolina|con calma|taki taki|mayores|chantaje|mi gente|durin|bailando|danza kuduro|que tire pa lante|con altura|tusa|dakiti|yonaguni|tit[ií] me pregunt[oó]|calma|echame la culpa|la bicicleta|rabiosa|waka waka|hips don't lie|loca|macarena|mambo no|la bamba|limbo|rompe|que viva la vida|culo|fireball|on the floor|tacata|danza|guaracha)", "Pop Latino / Urbano"),

    # Disco & Funk
    (r"(abba|earth, wind & fire|earth wind & fire|kool & the gang|village people|bee gees|donna summer|gloria gaynor|chic|kc and the sunshine band|kc & the sunshine band|sister sledge|lipps inc|boney m|the trammps|baccara|silver convention|the jacksons|the pointer sisters|heatwave|the whispers|tavares|bonnie m|ami stewart|rose royce|chaka khan|candi staton|the weather girls|anita ward|the gap band|barry white|diana ross|the emotions|wild cherry|carl douglas|rasputin|ymca|in the navy|le freak|good times|stayin' alive|night fever|disco inferno|september|boogie wonderland|celebration|ladies night|ring my bell|born to be alive|funkytown|car wash|gimme! gimme!|dancing queen|mamma mia|waterloo|fernando|voulez-vous|super trouper|take a chance|sos|money, money|knowing me|lay all your|the winner takes)", "Disco / Funk"),

    # Dance / Electrónica / EDM / House / Eurodance
    (r"(calvin harris|david guetta|avicii|ti[eë]sto|marshmello|skrillex|martin garrix|chainsmokers|swedish house mafia|alesso|afrojack|steve aoki|zedd|kygo|alan walker|deadmau5|robin schulz|felix jaehn|lost frequencies|dj snake|major lazer|clean bandit|galantis|disclosure|duke dumont|axwell|ingrosso|armin van buuren|hardwell|eric prydz|fatboy slim|the chemical brothers|the prodigy|faithless|paul van dyk|cascada|basshunter|guru josh|darude|atb|vengaboys|aqua|eiffel 65|scatman|haddaway|snap!|culture beat|2 unlimited|corona|real mccoy|captain hollywood|c&c music factory|technotronic|masterboy|aronchupa|little sis nora|lmfao|redfoo|skyblu|deorro|timmy trumpet|dj antoine|basto|otto knows|klingande|bakermat|mowe|lost frequencies|levels|wake me up|hey brother|titanium|clarity|animals|turn down for what|lean on|light it up|barbie girl|blue \(da ba dee\)|what is love|rhythm is a dancer|be my lover|cotton eye joe|scatman john|sandstorm|satisfaction|blade|pump up the jam|everybody dance now|albatraoz|i'm an albatraoz|saxobeat|mr\. saxobeat|stereolove|stereo love|electronic|techno|dubstep|house|electro|edm|remix|rave)", "Dance / Electrónica"),

    # Rock / Pop Rock / Metal / Punk / Indie Rock
    (r"(queen|bon jovi|kiss|survivor|the rolling stones|the beatles|nirvana|ac/dc|guns n' roses|aerosmith|metallica|iron maiden|scorpions|def leppard|deep purple|led zeppelin|black sabbath|ozzy|alice cooper|europe|van halen|white stripes|greenday|green day|blink-182|the offspring|sum 41|fall out boy|panic! at the disco|my chemical romance|paramore|the clash|ramones|sex pistols|linkin park|evanescence|red hot chili peppers|foo fighters|the killers|muse|franz ferdinand|arctic monkeys|blur|oasis|the white stripes|jet|the darkness|the strokes|radiohead|weezer|the police|u2|the kinks|the who|the guess who|creedence|status quo|twisted sister|poison|motley crue|judas priest|motorhead|lenny kravitz|billy idol|joan jett|pat benatar|blondie|the pretenders|heart|steppenwolf|lynyrd skynyrd|the outlaws|free|bad company|foghat|boston|journey|kansas|foreigner|styx|reospeedwagon|toto|survivor|cheap trick|rick springfield|loverboy|night ranger|huey lewis|bryan adams|bonnie tyler|meat loaf|the cranberries|skunk anansie|guano apes|hole|garbage|no doubt|smash mouth|chumbawamba|third eye blind|goo goo dolls|matchbox 20|sugar ray|spin doctors|4 non blondes|blind melon|candlebox|silverchair|bush|live|collective soul|fuel|tonic|sponge|spacehog|everclear|semisonic|fastball|lit|wheatus|fountains of wayne|bowling for soup|simple plan|good charlotte|new found glory|yellowcard|taking back sunday|the used|story of the year|all time low|mayday parade|boys like girls|the red jumpsuit apparatus|we the kings|metro station|cobra starship|gym class heroes|plain white t's|the fray|the feeling|the automatic|the view|the wombats|the pigeon detectives|the enemy|the courteeners|the vaccines|kaiser chiefs|hard-fi|the ting tings|the subways|maximo park|the rakes|the futureheads|bloc party|editors|white lies|interpol|franz ferdinand|klaxons|hadouken!|late of the pier|foals|the maccabees|bombay bicycle club|two door cinema club|everything everything|django django|alt-j|bastille|kodaline|homburg|cage the elephant|young the giant|grouplove|foster the people|passion pit|mgmt|phoenix|the naked and famous|walk the moon|saint motel|fitz and the tantrums|bleachers|the 1975|twenty one pilots|imagine dragons|x ambassadors|american authors|walk off the earth|sheppard|vance joy|george ezra|james bay|hozier|rag'n'bone man|lewis capaldi|sam fender|yungblud|machine gun kelly|manowar|dragonforce|nightwish|epica|within temptation)", "Rock / Pop Rock"),

    # Hip-Hop / Rap
    (r"(eminem|dr\. dre|snoop dogg|tupac|2pac|notorious b\.i\.g\.|50 cent|jay-z|kanye west|kendrick lamar|drake|travis scott|j\. cole|post malone|lil nas x|nicki minaj|cardi b|megan thee stallion|doja cat|iggy azalea|missy elliott|outkast|macklemore|flo rida|will\.i\.am|black eyed peas|mc hammer|vanilla ice|run d\.m\.c\.|salt-n-pepa|beastie boys|ll cool j|coolio|house of pain|cypress hill|public enemy|wu-tang|busta rhymes|ludacris|nelly|dmx|tyga|migos|future|lil wayne|jack harlow|dababy|24kgoldn|iann dior|chiddy bang|b\.o\.b|lupe fiasco|kid cudi|wiz khalifa|big sean|wale|asap rocky|a\$ap rocky|tyler, the creator|schoolboy q|mac miller|g-eazy|logic|joyner lucas|nf|lil uzi vert|playboi carti|xxxtentacion|juice wrld|roddy ricch|polo g|lil baby|gunna|lil durk|young thug|21 savage|offset|quavo|takeoff|gucci mane|waka flocka|soulja boy|silento|ayo & teo|iheartmemphis|zay hilfigerrr|dlow|dlux|gs boyz|cali swag district|new boyz|young mc|sir mix-a-lot|tone loc|rob base|dj e-z rock|heavy d|naughty by nature|onyx|kriss kross|kris kross|fugees|lauryn hill|pras|wyclef jean|digable planets|arrested development|the pharcyde|a tribe called quest|de la soul|jungle brothers|gang starr|mobb deep|nas|az|kool g rap|big l|big pun|fat joe|terror squad|dmx|the lox|jadakiss|styles p|sheek louch|cam'ron|the diplomats|dipset|fabolous|paul wall|chamillionaire|mike jones|slim thug|bun b|pimp c|ugk|lil' flip|juvenile|bg|mannie fresh|big tymers|trick daddy|trina|yin yang twins|petey pablo|david banner|t\.i\.|young jeezy|jeezy|rick ross|dj khaled|ace hood|plies|boosie|webbie|kevin gates|rich homie quan|fetty wap|desiigner|sheck wes|blueface|nle choppa|coi leray|lorenzo|shiggy|carmine)", "Hip-Hop / Rap"),

    # R&B / Soul / Funk
    (r"(beyonc[eé]|destiny's child|rihanna|alicia keys|usher|chris brown|ne-yo|john legend|amy winehouse|adele|sam smith|sza|the weeknd|frank ocean|daniel caesar|giveon|musiq soulchild|erykah badu|tlc|en vogue|toni braxton|boyz ii men|swv|brandy|monica|aaliyah|ciara|mariah carey|whitney houston|aretha franklin|ray charles|sam cooke|otis redding|marvin gaye|al green|bill withers|smokey robinson|the temptations|the four tops|the supremes|gladys knight|etta james|nina simone|dusty springfield|stevie wonder|james brown|prince|rick james|curtis mayfield|chaka khan|anita baker|sade|luther vandross|teddy pendergrass|barry white|isaac hayes|the isley brothers|the o'jays|harold melvin|the stylistics|the delphonics|the spinners|the chi-lites|earth wind & fire|kool & the gang|commodores|gap band|zapp|roger troutman|bootsy collins|george clinton|parliament|funkadelic|the meters|average white band|tower of power|wild cherry|con funk shun|brass construction|bt express|kleeer|slave|dazz band|the whispers|shalamar|midnight star|lakeside|sos band|mtume|rene & angela|kashif|evelyn king|howard johnson|melba moore|stephanie mills|patti labelle|phyllis hyman|teena marie|angela bofill|miki howard|karyn white|pebbles|jody watley|vanessa williams|shanice|mic'helle|jade|xscape|total|702|kut klose|brownstone|changing faces|allure|blaque|3lw|cherish|danity kane|richgirl|kelly rowland|michelle williams|letoya luckett|amerie|cassie|tamia|deborah cox|mya|faith evans|tamara|monifah|chante moore|ledisi|lalah hathaway|raheem devaughn|anthony hamilton|jaheim|eric benet|maxwell|d'angelo|bilal|musiq|glenn lewis|kem|javier colon|robin thicke|justin timberlake|aloe blacc|leon bridges|anderson \.paak|bruno mars|silk sonic|h\.e\.r\.|summer walker|kehlani|tinashe|jhene aiko|ella mai|snoh aalegra|cleo sol|joy crookes|raye)", "R&B / Soul"),

    # Pop / Dance-Pop
    (r"(lady gaga|dua lipa|katy perry|britney spears|madonna|ariana grande|taylor swift|selena gomez|demi lovato|kesha|halsey|rita ora|ava max|camila cabello|shawn mendes|justin bieber|charlie puth|ed sheeran|harry styles|zayn|niall horan|louis tomlinson|liam payne|one direction|jonas brothers|olivia rodrigo|billie eilish|sabrina carpenter|chappell roan|tate mcrae|charli xcx|troye sivan|lorde|carly rae jepsen|kelly clarkson|p!nk|pink|avril lavigne|christina aguilera|gwen stefani|fergie|nelly furtado|natasha bedingfield|kylie minogue|sophie ellis-bextor|robyn|tove lo|marina|ellie goulding|jessie j|bebe rexha|zara larsson|anne-marie|mabel|sigrid|dagny|astrid s|kim petras|rachel platten|meghan trainor|hilary duff|ashley tisdale|vanessa hudgens|bridgit mendler|victoria justice|miranda cosgrove|cher lloyd|little mix|fifth harmony|the pussycat dolls|girls aloud|sugababes|the saturdays|atomic kitten|spice girls|all saints|bananarama|b*witched|steps|s club 7|vengaboys|aqua|toy-box|daze|hit'n'hide|cartoons|me & my|solid base|smile\.dk|whigfield|gala|alexia|corona|ice mc|dr\. alban|e-rotic|capella|dj bobo|loona|bellini|las ketchupa)", "Pop / Dance-Pop"),

    # Country / Folk
    (r"(country|folk|bluegrass|shania twain|carrie underwood|dolly parton|johnny cash|willie nelson|garth brooks|keith urban|luke bryan|blake shelton|kacey musgraves|billy ray cyrus|miley cyrus|cotton eye joe|rednex|rascal flatts|lady a|lady antebellum|the chicks|dixie chicks|chris stapleton|morgan wallen|zach bryan|florida georgia line|big & rich|brooks & dunn|tim mcgraw|faith hill|kenny chesney|toby keith|alan jackson|george strait|reba mcentire|martina mcbride|trisha yearwood|leann rimes|lee ann womack|sara evans|jo dee messina|deana carter|terri clark|gretchen wilson|miranda lambert)", "Country / Folk"),

    # Clásica / Instrumental / 8-Bit
    (r"(8bit|8-bit|classical|william tell|mountain king|can can|rossini|beethoven|mozart|tchaikovsky|vivaldi|bach|chopin|strauss|offenbach|orchestra|instrumental)", "Clásica / Instrumental"),
]

def classify_genre(song):
    folder = song.get("edicion_codigo", "")
    title = song.get("titulo", "")
    artist = song.get("artista", "")
    map_name = song.get("map_name", "")
    current = song.get("genero", "")

    # Specific folder rules
    if folder == "123":
        return "Infantil"
    if folder in ["1928", "1929"] or "disney" in map_name.lower():
        return "Banda Sonora / Disney"
    if folder == "4884" or "abba" in artist.lower():
        return "Disco / Funk"
    if folder == "2009" or "michael jackson" in artist.lower():
        return "R&B / Soul"
    if folder in ["3112", "4118"]:
        return "J-Pop"
    if folder == "4514":
        if "garnidelia" in artist.lower():
            return "J-Pop"
        elif "f(x)" in artist.lower() or "girls generation" in artist.lower():
            return "K-Pop"
        else:
            return "C-Pop"

    text = f"{title} {artist} {map_name}".lower()

    for pattern, genre_name in RULES:
        if re.search(pattern, text, re.IGNORECASE):
            return genre_name

    # If already set to something specific, keep or normalize
    if current in ["Dance / Electrónica", "Rock / Pop Rock", "Hip-Hop / Rap", "R&B / Soul", "K-Pop", "J-Pop", "C-Pop", "Infantil", "Banda Sonora / Musical", "Disco / Funk", "Pop Latino / Urbano", "Country / Folk", "Clásica / Instrumental"]:
        return current
    if current in ["Dance", "Electronic", "Electrónica"]:
        return "Dance / Electrónica"
    if current in ["Rock", "Hard Rock", "Pop/Rock"]:
        return "Rock / Pop Rock"
    if current in ["Hip-Hop/Rap", "Hip-Hop", "Rap"]:
        return "Hip-Hop / Rap"
    if current in ["Latin", "Pop Latino", "Música Latina", "Reggaeton"]:
        return "Pop Latino / Urbano"
    if current in ["Soul", "R&B/Soul"]:
        return "R&B / Soul"

    return "Pop / Dance-Pop"

for s in songs:
    s["genero"] = classify_genre(s)

# Save JSON
with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(songs, f, ensure_ascii=False, indent=2)

# Save CSV
with open(CSV_PATH, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        "titulo", "artista", "edicion", "genero", "dificultad", "coaches", "archivo", "edicion_codigo", "map_name"
    ])
    writer.writeheader()
    for s in songs:
        writer.writerow({
            "titulo": s["titulo"],
            "artista": s["artista"],
            "edicion": s["edicion"],
            "genero": s["genero"],
            "dificultad": s["dificultad"],
            "coaches": s["coaches"],
            "archivo": s["archivo"],
            "edicion_codigo": s["edicion_codigo"],
            "map_name": s["map_name"]
        })

# Save JS
with open(JS_PATH, 'w', encoding='utf-8') as f:
    f.write("const JUST_DANCE_SONGS = ")
    json.dump(songs, f, ensure_ascii=False, indent=2)
    f.write(";\n")

# Distribution
counts = {}
for s in songs:
    g = s["genero"]
    counts[g] = counts.get(g, 0) + 1

print("\n--- DISTRIBUCIÓN FINAL COMPLETA DE GÉNEROS ---")
for g, c in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {g:<26}: {c:>4} canciones ({c/len(songs)*100:.1f}%)")
