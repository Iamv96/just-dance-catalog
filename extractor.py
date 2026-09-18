import os
import sys
import json
import csv
import re

sys.stdout.reconfigure(encoding='utf-8')

MAPS_DIR = r"C:\Users\Ignac\Documents\Just Dance Legacy\maps"
WORKSPACE_DIR = r"c:\Users\Ignac\Documents\Proyectos IA\Lista canciones Just Dance"
OUTPUT_JSON = os.path.join(WORKSPACE_DIR, "canciones_just_dance.json")
OUTPUT_CSV = os.path.join(WORKSPACE_DIR, "canciones_just_dance.csv")
OUTPUT_JS = os.path.join(WORKSPACE_DIR, "data.js")

FOLDER_EDITIONS = {
    "1": "Just Dance",
    "2": "Just Dance 2",
    "3": "Just Dance 3",
    "4": "Just Dance 4",
    "123": "Just Dance Kids",
    "1928": "Just Dance: Disney Party",
    "1929": "Just Dance: Disney Party 2",
    "2009": "Michael Jackson: The Experience",
    "2014": "Just Dance 2014",
    "2015": "Just Dance 2015",
    "2016": "Just Dance 2016",
    "2017": "Just Dance 2017",
    "2018": "Just Dance 2018",
    "2019": "Just Dance 2019",
    "2020": "Just Dance 2020",
    "2021": "Just Dance 2021",
    "2022": "Just Dance 2022",
    "2023": "Just Dance 2023 Edition",
    "2024": "Just Dance 2024 Edition",
    "2025": "Just Dance 2025 Edition",
    "2026": "Just Dance 2026 Edition",
    "3112": "Just Dance Wii 2 (Japón)",
    "4118": "Just Dance Wii U (Japón)",
    "4514": "Just Dance China",
    "4884": "ABBA: You Can Dance",
}

# 1. Reglas específicas por canción (Género)
SONG_SPECIFIC_GENRES = {
    "timber": "Dance / Electrónica",
    "feel this moment": "Dance / Electrónica",
    "fun": "Dance / Electrónica",
    "give me everything": "Dance / Electrónica",
    "fireball": "Dance / Electrónica",
    "don't stop the party": "Dance / Electrónica",
    "on the floor": "Dance / Electrónica",
    "mr. saxobeat": "Dance / Electrónica",
    "cotton eye joe": "Country / Folk",
    "alexandrie alexandra": "Disco / Funk",
    "miraculous official theme song": "Banda Sonora / Musical",
    "flash (just dance version)": "Pop / Dance-Pop",
    "flash pose": "Dance / Electrónica",
    "same old love": "Pop / Dance-Pop",
    "bad liar": "Pop / Dance-Pop",
    "rare": "Pop / Dance-Pop",
    "love you like a love song": "Pop / Dance-Pop",
    "hit the lights": "Pop / Dance-Pop",
    "oath": "Pop / Dance-Pop",
    "built for this": "Pop / Dance-Pop",
    "mad love": "Dance / Electrónica",
    "calypso": "Pop Latino / Urbano",
    "waka waka (this time for africa)": "Pop / Dance-Pop",
    "hips don't lie": "Pop Latino / Urbano",
    "la bicicleta": "Pop Latino / Urbano",
    "chantaje": "Pop Latino / Urbano",
    "rabiosa": "Pop Latino / Urbano",
    "despacito": "Pop Latino / Urbano",
    "gasolina": "Pop Latino / Urbano",
    "con calma": "Pop Latino / Urbano",
    "taki taki": "Pop Latino / Urbano",
    "tusa": "Pop Latino / Urbano",
    "mayores": "Pop Latino / Urbano",
    "todo de ti": "Pop Latino / Urbano",
    "si antes te hubiera conocido": "Pop Latino / Urbano",
    "mambo no. 5 (a little bit of monika)": "Pop / Dance-Pop",
    "macarena": "Pop Latino / Urbano",
    "bailando": "Pop Latino / Urbano",
    "a little less conversation (jxl radio edit remix)": "Dance / Electrónica",
    "funplex (css remix)": "Dance / Electrónica",
    "barbie girl": "Dance / Electrónica",
    "rasputin": "Disco / Funk",
    "eye of the tiger": "Rock / Pop Rock",
}

# 2. Reglas generales por Artista / Frase para Géneros
GENRE_RULES = [
    (r"(the just dance kids|tom zehnder|kidsabc|kidscrocodile|kidsdayo|kidsfive|kidsfraggle|kidshickory|kidsifyou|kidsilike|kidsjingle|kidsmagic|kidsmary|kidspirate|kidsproblem|kidsthe|kidswego|kidswheels|kidsworking|baby shark|gummy bear|crazy frog|angry birds|alvin|wiggles)", "Infantil"),
    (r"(disney|violetta|a\.n\.t\. farm|soundtrack|broadway|musical|camp rock|high school musical|descendants|frozen|moana|encanto|the lion king|aladdin|beauty and the beast|the little mermaid|tangled|tarzan|mulan|hercules|mary poppins|the greatest showman|lalaland|la la land|mamma mia|grease|hairspray|wicked|hamilton|gombault|in the heights|ghostbusters|space jam|footloose|fame|rock'n roll - teenage uprising)", "Banda Sonora / Musical"),
    (r"(bts|blackpink|twice|psy|2ne1|bigbang|exo|red velvet|aespa|itzy|stray kids|newjeans|le sserafim|super m|momoland|k/da|sunmi|hyuna|clc|everglow|ateez|txt|seventeen|nct|monsta x|got7|shinee|girls' generation|girls generation|boa|wonder girls|gidle|\(g\)i-dle|enhypen|ive|stayc|4 walls|gagnam|gangnam style|gentleman|daddy|kill this love|how you like that|ddu-du|boombayah|as if it's your last|ice cream|dynamite|butter|boy with luv|fancy|feel special|the feels|pop/stars|more|bbtomboy|wannabe|loco|sneakers|god's menu|maniac|thunderous|hype boy|omg|super shy|antifragile|fearless|unforgiven|jopping|bap3|kick it)", "K-Pop"),
    (r"(e-girls|akb48|happiness|megumi tatsumi|garnidelia|perfume|kyary pamyu pamyu|babymetal|yoasobi|kenshi yonezu|ado|lisa|utada hikaru|ayumi hamasaki|arashi|official hige dandism|king gnu|wanko ni mero|sokusu|follow me|koi suru|fortune cookie|joyful|we can fly|gokuraku|ponponpon|ninja re bang bang|tsunagaru)", "J-Pop"),
    (r"(jolin tsai|jay chou|tfboys|kris wu|phoenix legend|wang rong|chopstick brothers|wanting qu|chris lee|wilber pan|angela chang|shanghai restoration project|namewee|g\.e\.m\.|lexie liu|lay zhang|jackson wang|bailemen|bedtime stories|big bowl|big dreamer|dancing diva|chick chick|coolest ethnic|gee \(哎呀\)|play \(我呸\)|real love|little apple|us under the sunshine|adoration to happiness)", "C-Pop"),
    (r"(daddy yankee|bad bunny|j balvin|maluma|ozuna|anuel|karol g|rosal[ií]a|rauw alejandro|farruko|nicky jam|wisin|yandel|don omar|natti natasha|sech|myke towers|camilo|sebastian yatra|manuel turizo|feid|bizarrap|quevedo|peso pluma|el alfa|chayanne|luis fonsi|ricky martin|marc anthony|juanes|gloria estefan|alvaro soler|cuba club|los del rio|selena quintanilla|thalia|paulina rubio|prince royce|romeo santos|gente de zona|michel tel[oó]|gusttavo lima|anitta|mc fioti|mc zaac|pabllo vittar|lexa|ludmilla|kevinho|aventura|danza kuduro|que tire pa lante|con altura|dakiti|yonaguni|tit[ií] me pregunt[oó]|calma|echame la culpa|limbo|rompe|que viva la vida|culo|tacata|guaracha)", "Pop Latino / Urbano"),
    (r"(abba|earth, wind & fire|earth wind & fire|kool & the gang|village people|bee gees|donna summer|gloria gaynor|chic|kc and the sunshine band|kc & the sunshine band|sister sledge|lipps inc|boney m|the trammps|baccara|silver convention|the jacksons|the pointer sisters|heatwave|the whispers|tavares|bonnie m|ami stewart|rose royce|chaka khan|candi staton|the weather girls|anita ward|the gap band|barry white|diana ross|the emotions|wild cherry|carl douglas|ymca|in the navy|le freak|good times|stayin' alive|night fever|disco inferno|september|boogie wonderland|celebration|ladies night|ring my bell|born to be alive|funkytown|car wash|gimme! gimme!|dancing queen|mamma mia|waterloo|fernando|voulez-vous|super trouper|take a chance|sos|money, money|knowing me|lay all your|the winner takes)", "Disco / Funk"),
    (r"(calvin harris|david guetta|avicii|ti[eë]sto|marshmello|skrillex|martin garrix|chainsmokers|swedish house mafia|alesso|afrojack|steve aoki|zedd|kygo|alan walker|deadmau5|robin schulz|felix jaehn|lost frequencies|dj snake|major lazer|clean bandit|galantis|disclosure|duke dumont|axwell|ingrosso|armin van buuren|hardwell|eric prydz|fatboy slim|the chemical brothers|the prodigy|faithless|paul van dyk|cascada|basshunter|guru josh|darude|atb|vengaboys|aqua|eiffel 65|scatman|haddaway|snap!|culture beat|2 unlimited|corona|real mccoy|captain hollywood|c&c music factory|technotronic|masterboy|aronchupa|little sis nora|lmfao|redfoo|skyblu|deorro|timmy trumpet|dj antoine|basto|otto knows|klingande|bakermat|mowe|levels|wake me up|hey brother|titanium|clarity|animals|turn down for what|lean on|light it up|barbie girl|blue \(da ba dee\)|what is love|rhythm is a dancer|be my lover|scatman john|sandstorm|satisfaction|blade|pump up the jam|everybody dance now|albatraoz|i'm an albatraoz|saxobeat|stereolove|stereo love|electronic|techno|dubstep|house|electro|edm|rave)", "Dance / Electrónica"),
    (r"(queen|bon jovi|kiss|survivor|the rolling stones|the beatles|nirvana|ac/dc|guns n' roses|aerosmith|metallica|iron maiden|scorpions|def leppard|deep purple|led zeppelin|black sabbath|ozzy|alice cooper|europe|van halen|white stripes|greenday|green day|blink-182|the offspring|sum 41|fall out boy|panic! at the disco|my chemical romance|paramore|the clash|ramones|sex pistols|linkin park|evanescence|red hot chili peppers|foo fighters|the killers|muse|franz ferdinand|arctic monkeys|blur|oasis|the white stripes|jet|the darkness|the strokes|radiohead|weezer|the police|u2|the kinks|the who|the guess who|creedence|status quo|twisted sister|poison|motley crue|judas priest|motorhead|lenny kravitz|billy idol|joan jett|pat benatar|blondie|the pretenders|heart|steppenwolf|lynyrd skynyrd|the outlaws|free|bad company|foghat|boston|journey|kansas|foreigner|styx|reospeedwagon|toto|cheap trick|rick springfield|loverboy|night ranger|huey lewis|bryan adams|bonnie tyler|meat loaf|the cranberries|skunk anansie|guano apes|hole|garbage|no doubt|smash mouth|chumbawamba|third eye blind|goo goo dolls|matchbox 20|sugar ray|spin doctors|4 non blondes|blind melon|candlebox|silverchair|bush|live|collective soul|fuel|tonic|sponge|spacehog|everclear|semisonic|fastball|lit|wheatus|fountains of wayne|bowling for soup|simple plan|good charlotte|new found glory|yellowcard|taking back sunday|the used|story of the year|all time low|mayday parade|boys like girls|the red jumpsuit apparatus|we the kings|metro station|cobra starship|gym class heroes|plain white t's|the fray|the feeling|the automatic|the view|the wombats|the pigeon detectives|the enemy|the courteeners|the vaccines|kaiser chiefs|hard-fi|the ting tings|the subways|maximo park|the rakes|the futureheads|bloc party|editors|white lies|interpol|klaxons|hadouken!|late of the pier|foals|the maccabees|bombay bicycle club|two door cinema club|everything everything|django django|alt-j|bastille|kodaline|homburg|cage the elephant|young the giant|grouplove|foster the people|passion pit|mgmt|phoenix|the naked and famous|walk the moon|saint motel|fitz and the tantrums|bleachers|the 1975|twenty one pilots|imagine dragons|x ambassadors|american authors|walk off the earth|sheppard|vance joy|george ezra|james bay|hozier|rag'n'bone man|lewis capaldi|sam fender|yungblud|machine gun kelly|manowar|dragonforce|nightwish|epica|within temptation)", "Rock / Pop Rock"),
    (r"(eminem|dr\. dre|snoop dogg|tupac|2pac|notorious b\.i\.g\.|50 cent|jay-z|kanye west|kendrick lamar|drake|travis scott|j\. cole|post malone|lil nas x|nicki minaj|cardi b|megan thee stallion|doja cat|iggy azalea|missy elliott|outkast|macklemore|flo rida|will\.i\.am|black eyed peas|mc hammer|vanilla ice|run d\.m\.c\.|salt-n-pepa|beastie boys|ll cool j|coolio|house of pain|cypress hill|public enemy|wu-tang|busta rhymes|ludacris|nelly|dmx|tyga|migos|future|lil wayne|jack harlow|dababy|24kgoldn|iann dior|chiddy bang|b\.o\.b|lupe fiasco|kid cudi|wiz khalifa|big sean|wale|asap rocky|a\$ap rocky|tyler, the creator|schoolboy q|mac miller|g-eazy|logic|joyner lucas|nf|lil uzi vert|playboi carti|xxxtentacion|juice wrld|roddy ricch|polo g|lil baby|gunna|lil durk|young thug|21 savage|offset|quavo|takeoff|gucci mane|waka flocka|soulja boy|silento|ayo & teo|iheartmemphis|zay hilfigerrr|dlow|dlux|gs boyz|cali swag district|new boyz|young mc|sir mix-a-lot|tone loc|rob base|dj e-z rock|heavy d|naughty by nature|onyx|kriss kross|kris kross|fugees|lauryn hill|pras|wyclef jean|digable planets|arrested development|the pharcyde|a tribe called quest|de la soul|jungle brothers|gang starr|mobb deep|nas|az|kool g rap|big l|big pun|fat joe|terror squad|dmx|the lox|jadakiss|styles p|sheek louch|cam'ron|the diplomats|dipset|fabolous|paul wall|chamillionaire|mike jones|slim thug|bun b|pimp c|ugk|lil' flip|juvenile|bg|mannie fresh|big tymers|trick daddy|trina|yin yang twins|petey pablo|david banner|t\.i\.|young jeezy|jeezy|rick ross|dj khaled|ace hood|plies|boosie|webbie|kevin gates|rich homie quan|fetty wap|desiigner|sheck wes|blueface|nle choppa|coi leray|lorenzo|shiggy|carmine)", "Hip-Hop / Rap"),
    (r"(beyonc[eé]|destiny's child|rihanna|alicia keys|usher|chris brown|ne-yo|john legend|amy winehouse|adele|sam smith|sza|the weeknd|frank ocean|daniel caesar|giveon|musiq soulchild|erykah badu|tlc|en vogue|toni braxton|boyz ii men|swv|brandy|monica|aaliyah|ciara|mariah carey|whitney houston|aretha franklin|ray charles|sam cooke|otis redding|marvin gaye|al green|bill withers|smokey robinson|the temptations|the four tops|the supremes|gladys knight|etta james|nina simone|dusty springfield|stevie wonder|james brown|prince|rick james|curtis mayfield|chaka khan|anita baker|sade|luther vandross|teddy pendergrass|barry white|isaac hayes|the isley brothers|the o'jays|harold melvin|the stylistics|the delphonics|the spinners|the chi-lites|commodores|gap band|zapp|roger troutman|bootsy collins|george clinton|parliament|funkadelic|the meters|average white band|tower of power|con funk shun|brass construction|bt express|kleeer|slave|dazz band|the whispers|shalamar|midnight star|lakeside|sos band|mtume|rene & angela|kashif|evelyn king|howard johnson|melba moore|stephanie mills|patti labelle|phyllis hyman|teena marie|angela bofill|miki howard|karyn white|pebbles|jody watley|vanessa williams|shanice|mic'helle|jade|xscape|total|702|kut klose|brownstone|changing faces|allure|blaque|3lw|cherish|danity kane|richgirl|kelly rowland|michelle williams|letoya luckett|amerie|cassie|tamia|deborah cox|mya|faith evans|tamara|monifah|chante moore|ledisi|lalah hathaway|raheem devaughn|anthony hamilton|jaheim|eric benet|maxwell|d'angelo|bilal|musiq|glenn lewis|kem|javier colon|robin thicke|justin timberlake|aloe blacc|leon bridges|anderson \.paak|bruno mars|silk sonic|h\.e\.r\.|summer walker|kehlani|tinashe|jhene aiko|ella mai|snoh aalegra|cleo sol|joy crookes|raye)", "R&B / Soul"),
    (r"(lady gaga|dua lipa|katy perry|britney spears|madonna|ariana grande|taylor swift|selena gomez|demi lovato|kesha|ke\$ha|halsey|rita ora|ava max|camila cabello|shawn mendes|justin bieber|charlie puth|ed sheeran|harry styles|zayn|niall horan|louis tomlinson|liam payne|one direction|jonas brothers|olivia rodrigo|billie eilish|sabrina carpenter|chappell roan|tate mcrae|charli xcx|troye sivan|lorde|carly rae jepsen|kelly clarkson|p!nk|pink|avril lavigne|christina aguilera|gwen stefani|fergie|nelly furtado|natasha bedingfield|kylie minogue|sophie ellis-bextor|robyn|tove lo|marina|ellie goulding|jessie j|bebe rexha|zara larsson|anne-marie|mabel|sigrid|dagny|astrid s|kim petras|rachel platten|meghan trainor|hilary duff|ashley tisdale|vanessa hudgens|bridgit mendler|victoria justice|miranda cosgrove|cher lloyd|little mix|fifth harmony|the pussycat dolls|girls aloud|sugababes|the saturdays|atomic kitten|spice girls|all saints|bananarama|b*witched|steps|s club 7|toy-box|daze|hit'n'hide|cartoons|me & my|solid base|smile\.dk|whigfield|gala|alexia|ice mc|dr\. alban|e-rotic|capella|dj bobo|loona|bellini|las ketchupa)", "Pop / Dance-Pop"),
    (r"(country|folk|bluegrass|shania twain|carrie underwood|dolly parton|johnny cash|willie nelson|garth brooks|keith urban|luke bryan|blake shelton|kacey musgraves|billy ray cyrus|miley cyrus|rascal flatts|lady a|lady antebellum|the chicks|dixie chicks|chris stapleton|morgan wallen|zach bryan|florida georgia line)", "Country / Folk"),
    (r"(8bit|8-bit|classical|william tell|mountain king|can can|rossini|beethoven|mozart|tchaikovsky|vivaldi|bach|chopin|strauss|offenbach|orchestra|instrumental)", "Clásica / Instrumental"),
]

# 3. Clasificación Exhaustiva de Idiomas
SPANGLISH_EXACT_TITLES = {
    "despacito",
    "bailando",
    "taki taki",
    "hips don't lie",
    "con calma",
    "mayores",
    "on the floor",
    "chantaje",
    "calypso",
    "mad love",
    "girl like me",
    "macarena",
    "mambo no. 5 (a little bit of monika)",
    "echame la culpa",
    "la respuesta",
    "can't get enough",
    "bailar",
    "subeme la radio",
    "havana",
    "señorita",
    "senorita",
    "un poco loco",
    "dakiti",
    "tusa",
    "la gozadera",
    "con altura",
    "gasolina",
    "rabiosa",
    "loca",
    "waka waka (this time for africa)",
    "i like it",
    "livin' la vida loca",
    "fireball",
    "culo",
    "tacata",
    "guaracha",
    "rompe"
}

SPANISH_EXACT_TITLES = {
    "todo de ti",
    "si antes te hubiera conocido",
    "obsesión",
    "obsesion",
    "el tiki",
    "la bicicleta",
    "limbo",
    "que viva la vida",
    "en mi mundo",
    "me rehúso",
    "me rehuso",
    "titi me pregunto",
    "tití me preguntó",
    "la bamba",
    "maria",
    "maría",
    "danza kuduro",
    "criminal",
    "que tire pa lante",
    "yo le llego",
    "china",
    "x (equis)",
    "familiar",
    "cola song",
    "stuck on a feeling",
    "follow the leader"
}

FRENCH_EXACT_TITLES = {
    "alexandrie alexandra",
    "djadja",
    "dormir dehors",
    "je sais pas danser",
    "à la folie",
    "a la folie",
    "alane",
    "flash (just dance version)",
    "cendrillon",
    "le banana split",
    "elle me dit",
    "ça plane pour moi",
    "ca plane pour moi",
    "papaoutai",
    "carmen",
    "danser",
    "la grenouille",
    "mon précieux",
    "mon precieux",
    "tout oublier",
    "chanson sur ma drole de vie",
    "la kiffance",
    "resiste",
    "miraculous official theme song",
    "le festin"
}

PORTUGUESE_EXACT_TITLES = {
    "ai se eu te pego",
    "balada",
    "bang",
    "medicina",
    "bum bum tam tam",
    "só depois do carnaval",
    "so depois do carnaval",
    "sua cara",
    "flash pose",
    "baianá",
    "baiana",
    "a queda",
    "aqueda",
    "dança do quadrado",
    "danca do quadrado",
    "menina solta"
}

DUTCH_EXACT_TITLES = {
    "10.000 luchtballonnen",
    "10000lucht",
    "oya lélé",
    "oya lele"
}

INSTRUMENTAL_EXACT = {
    "8bit",
    "8-bit classical",
    "william tell overture",
    "in the hall of the mountain king",
    "can can",
    "the master",
    "tetris",
    "radetzky march",
    "slavic march"
}

def clean_text(text):
    if not text:
        return ""
    t = text
    t = t.replace('\ufffd', "'")
    t = t.replace('’', "'").replace('‘', "'")
    t = t.replace('“', '"').replace('”', '"')
    t = t.replace('\u00a0', ' ')
    t = t.replace('\x00', '')
    t = t.strip()
    return t

def extract_songdesc(ipk_path):
    with open(ipk_path, 'rb') as f:
        data = f.read(2 * 1024 * 1024)
    idx = data.find(b'JD_SongDescTemplate')
    if idx == -1:
        with open(ipk_path, 'rb') as f:
            data = f.read()
        idx = data.find(b'JD_SongDescTemplate')
        if idx == -1:
            return None
    
    start = data.rfind(b'{', 0, idx)
    if start == -1:
        return None
    
    count = 0
    end = -1
    for i in range(start, min(len(data), start + 32768)):
        if data[i:i+1] == b'{':
            count += 1
        elif data[i:i+1] == b'}':
            count -= 1
            if count == 0:
                end = i + 1
                break
    if end != -1:
        try:
            chunk = data[start:end].decode('utf-8', errors='ignore').strip('\x00\r\n\t ')
            return json.loads(chunk)
        except Exception:
            chunk = data[start:end].decode('latin1', errors='ignore')
            return parse_fields_fallback(chunk)
    return None

def parse_fields_fallback(text):
    res = {}
    for key in ['Title', 'Artist', 'MapName', 'JDVersion', 'OriginalJDVersion', 'Difficulty', 'SweatDifficulty', 'NumCoach', 'Tags']:
        m = re.search(r'"' + key + r'"\s*:\s*"([^"]*)"', text)
        if m:
            res[key] = m.group(1)
        else:
            m_num = re.search(r'"' + key + r'"\s*:\s*([0-9]+)', text)
            if m_num:
                res[key] = int(m_num.group(1))
    return res

def classify_genre(folder, title, artist, map_name):
    title_lower = title.lower().strip()
    if title_lower in SONG_SPECIFIC_GENRES:
        return SONG_SPECIFIC_GENRES[title_lower]

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

    for pattern, genre_name in GENRE_RULES:
        if re.search(pattern, text, re.IGNORECASE):
            return genre_name

    return "Pop / Dance-Pop"

def classify_language(folder, title, artist, map_name, genre):
    title_lower = title.lower().strip()
    artist_lower = artist.lower().strip()
    map_lower = map_name.lower().strip()
    combined = f"{title_lower} {artist_lower} {map_lower}"

    # 1. Instrumental
    for item in INSTRUMENTAL_EXACT:
        if item in title_lower or item in map_lower:
            return "Instrumental"

    # 2. Spanglish
    if title_lower in SPANGLISH_EXACT_TITLES or any(item in title_lower for item in ["despacito", "taki taki", "mayores", "chantaje", "con calma", "girl like me", "un poco loco", "con altura"]):
        # Special check to avoid false positives like "That's The Way (I Like It)"
        if "i like it" in title_lower and "kc" in artist_lower:
            return "Inglés"
        return "Spanglish"

    # 3. Español
    if title_lower in SPANISH_EXACT_TITLES:
        return "Español"

    # 4. Francés
    if title_lower in FRENCH_EXACT_TITLES or "claude françois" in artist_lower or "bilal hassani" in artist_lower:
        return "Francés"

    # 5. Portugués
    if title_lower in PORTUGUESE_EXACT_TITLES or any(k in artist_lower for k in ["anitta", "mc fioti", "michel teló", "gusttavo lima", "lexa", "pabllo vittar"]):
        # Anitta songs in English
        if title_lower in ["boys don't cry"]:
            return "Inglés"
        return "Portugués"

    # 6. Holandés
    if title_lower in DUTCH_EXACT_TITLES or "k3" in artist_lower:
        return "Holandés"

    # 7. Coreano (K-Pop)
    if genre == "K-Pop" or any(k in artist_lower for k in ["bts", "blackpink", "twice", "psy", "2ne1", "bigbang", "exo", "red velvet", "aespa", "itzy", "stray kids", "newjeans", "le sserafim", "super m", "momoland", "k/da", "sunmi", "hyuna", "clc", "everglow", "ateez", "txt", "seventeen", "nct", "girls generation", "girls' generation"]):
        return "Coreano"

    # 8. Japonés (J-Pop)
    if genre == "J-Pop" or folder in ["3112", "4118"] or any(k in combined for k in ["akb48", "e-girls", "happiness", "megumi tatsumi", "garnidelia", "perfume", "kyary", "babymetal", "yoasobi", "koi suru", "fortune cookie", "joyful", "we can fly", "gokuraku", "sokusu", "恋するフォーチュンクッキー", "達見恵"]):
        return "Japonés"

    # 9. Chino (Mandarín / C-Pop)
    if genre == "C-Pop" or folder == "4514" or any(k in combined for k in ["chopstick brothers", "jolin tsai", "jay chou", "tfboys", "kris wu", "wang rong", "phoenix legend", "wanting qu", "chris lee", "wilber pan", "angela chang", "shanghai restoration project", "小苹果", "舞娘", "大梦想家", "床边故事", "百乐门"]):
        return "Chino"

    # 10. Italiano
    if any(k in combined for k in ["bella ciao", "sara perche ti amo", "sarà perché ti amo", "l'italiano", "mambo italiano"]):
        return "Italiano"

    # 11. Alemán
    if any(k in combined for k in ["99 luftballons", "moskau"]):
        return "Alemán"

    # 12. Latino restante
    if genre == "Pop Latino / Urbano":
        return "Español"

    # 13. Default
    return "Inglés"

def process_all():
    print(f"Escaneando carpetas en: {MAPS_DIR} ...")
    songs = []
    folders = sorted(os.listdir(MAPS_DIR))
    
    for folder in folders:
        fdir = os.path.join(MAPS_DIR, folder)
        if not os.path.isdir(fdir):
            continue
        ipks = [f for f in os.listdir(fdir) if f.endswith('.ipk')]
        edition_name = FOLDER_EDITIONS.get(folder, f"Just Dance ({folder})")
        print(f"Carpeta [{folder:>4}] -> {edition_name:<32} ({len(ipks)} canciones)")
        
        for ipk in ipks:
            ipk_path = os.path.join(fdir, ipk)
            desc = extract_songdesc(ipk_path)
            if not desc:
                print(f"  [ERROR] No se pudo leer {ipk}")
                continue
            
            comp = desc.get('COMPONENTS', [{}])[0] if 'COMPONENTS' in desc else desc
            title = clean_text(comp.get('Title') or ipk.replace('_pc.ipk', '').title())
            artist = clean_text(comp.get('Artist') or 'Artista Desconocido')
            map_name = comp.get('MapName') or ipk.replace('_pc.ipk', '')
            num_coach = comp.get('NumCoach', 1)
            difficulty = comp.get('Difficulty', 1)
            sweat = comp.get('SweatDifficulty', 1)
            
            is_alternate = False
            if "alt" in ipk.lower() or "alternate" in title.lower() or "version" in title.lower() or "vip" in ipk.lower():
                is_alternate = True

            genre = classify_genre(folder, title, artist, map_name)
            language = classify_language(folder, title, artist, map_name, genre)
            
            song_item = {
                "id": f"{folder}_{map_name}",
                "titulo": title,
                "artista": artist,
                "edicion": edition_name,
                "edicion_codigo": folder,
                "genero": genre,
                "idioma": language,
                "dificultad": difficulty,
                "sweat": sweat,
                "coaches": num_coach,
                "map_name": map_name,
                "archivo": ipk,
                "es_alternativa": is_alternate
            }
            songs.append(song_item)

    # Sort by edition name, then title
    songs.sort(key=lambda x: (x["edicion"], x["titulo"].lower()))

    # Export JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(songs, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] Guardado JSON: {OUTPUT_JSON}")

    # Export CSV
    with open(OUTPUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "titulo", "artista", "edicion", "genero", "idioma", "dificultad", "coaches", "archivo", "edicion_codigo", "map_name"
        ])
        writer.writeheader()
        for s in songs:
            writer.writerow({
                "titulo": s["titulo"],
                "artista": s["artista"],
                "edicion": s["edicion"],
                "genero": s["genero"],
                "idioma": s["idioma"],
                "dificultad": s["dificultad"],
                "coaches": s["coaches"],
                "archivo": s["archivo"],
                "edicion_codigo": s["edicion_codigo"],
                "map_name": s["map_name"]
            })
    print(f"[OK] Guardado CSV: {OUTPUT_CSV}")

    # Export JS
    with open(OUTPUT_JS, 'w', encoding='utf-8') as f:
        f.write("const JUST_DANCE_SONGS = ")
        json.dump(songs, f, ensure_ascii=False, indent=2)
        f.write(";\n")
    print(f"[OK] Guardado JS: {OUTPUT_JS}")

    # Language Stats
    idiomas_count = {}
    for s in songs:
        lang = s["idioma"]
        idiomas_count[lang] = idiomas_count.get(lang, 0) + 1

    print("\n--- RESUMEN POR IDIOMA ---")
    for lang, cnt in sorted(idiomas_count.items(), key=lambda x: -x[1]):
        print(f"  {lang:<18}: {cnt:>4} canciones ({cnt/len(songs)*100:.1f}%)")

if __name__ == "__main__":
    process_all()
