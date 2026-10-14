import re
from flask import Flask, request, render_template
import ply.lex as lex
import ply.yacc as yacc
from difflib import get_close_matches
from datetime import datetime

app = Flask(__name__)

# Path to the error log file
ERROR_LOG_FILE = "quran_analysis_log.txt"

def log_errors(input_text, errors, solutions):
    """Logs only error-related details to a file."""
    if errors:  # Log only if there are errors
        with open(ERROR_LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(f"=== Error Entry ===\n")
            log_file.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_file.write(f"Input: {input_text}\n")
            log_file.write(f"Errors: {errors}\n")
            if solutions:
                log_file.write(f"Solutions: {solutions}\n")
            log_file.write("\n")  # Add a blank line for readability


versets_corrects = [
    "بسم الله الرحمن الرحيم", 
    "الحمد لله رب العالمين", 
    "الرحمن الرحيم",
    "ملك يوم الدين",
    "إياك نعبد وإياك نستعين",
    "اهدنا الصراط المستقيم",
    "صراط الذين أنعمت عليهم ",  
    "غير المغضوب عليهم ولا الضالين"  
]

# Définition des tokens pour chaque mot de la sourate Al-Fatiha
# Liste des tokens
tokens = (
    'BISM', 'ALLAH', 'ALRAHMAN', 'ALRAHEEM', 
    'ALHAMDU', 'LILLAH', 'RABB', 'ALALAMEEN',
    'MALIKI', 'YAUM', 'ALDEEN', 'IYYAKA', 
    'NABUDU', 'WA', 'NAASTA3EEN', 'IHDINA', 
    'ALSIRAT', 'ALMOSTAQEEM', 'SIRAT', 'ALLATHEEN', 
    'AN3AMTA', 'ALAYHIM', 'GHAYR', 'ALMAGHDOUBI', 
    'WALA', 'ALDAALEEN'
)

# Expressions régulières pour chaque mot
t_BISM = r'بسم'
t_ALLAH = r'الله'
t_ALRAHMAN = r'الرحمن'
t_ALRAHEEM = r'الرحيم'
t_ALHAMDU = r'الحمد'
t_LILLAH = r'لله'
t_RABB = r'رب'
t_ALALAMEEN = r'العالمين'
t_MALIKI = r'ملك'
t_YAUM = r'يوم'
t_ALDEEN = r'الدين'
t_IYYAKA = r'إياك'
t_NABUDU = r'نعبد'
t_WA = r'و'
t_NAASTA3EEN = r'نستعين'
t_IHDINA = r'اهدنا'
t_ALSIRAT = r'الصراط'
t_ALMOSTAQEEM = r'المستقيم'
t_SIRAT = r'صراط'
t_ALLATHEEN = r'الذين'
t_AN3AMTA = r'أنعمت'
t_ALAYHIM = r'عليهم'
t_GHAYR = r'غير'
t_ALMAGHDOUBI = r'المغضوب'
t_WALA = r'ولا'
t_ALDAALEEN = r'الضالين'

# Ignorer les espaces et les diacritiques
t_ignore = ' \t\n'

# Fonction pour ignorer les diacritiques arabes
def t_ignore_TASHKEEL(t):
    r'[ًٌٍَُِّْ]'  # Regex pour les voyelles courtes
    t.lexer.skip(1)  # Ignore un caractère correspondant à l'expression régulière

# Suppression des espaces et caractères invisibles supplémentaires
def t_ignore_WHITESPACE(t):
    r'\s+'  # Ignore les espaces, tabulations et nouvelles lignes
    t.lexer.skip(len(t.value))  # Ignore ces caractères


# Gestion des erreurs lexicales
def t_error(t):
    raise Exception(f"⛔ لديك خطأ لغوي في النص.\n")

# Construire le lexer
lexer = lex.lex()


# Règles syntaxiques pour la sourate Al-Fatiha
def p_phrase(p):
    '''phrase : BISM ALLAH ALRAHMAN ALRAHEEM ALHAMDU LILLAH RABB ALALAMEEN ALRAHMAN ALRAHEEM MALIKI YAUM ALDEEN IYYAKA NABUDU WA IYYAKA NAASTA3EEN IHDINA ALSIRAT ALMOSTAQEEM SIRAT ALLATHEEN AN3AMTA ALAYHIM GHAYR ALMAGHDOUBI ALAYHIM WALA ALDAALEEN'''
    p[0] = f"✅ النص صحيح: السورة مكتوبة بشكل صحيح!"


# Règles syntaxiques pour une phrase (p_phrase)
def p_aya1(p):
    '''aya1 : BISM ALLAH ALRAHMAN ALRAHEEM '''
    # Règles syntaxiques pour la sourate Al-Fatiha
    p[0] = f"✅ النص صحيح: السورة مكتوبة بشكل صحيح!"

def p_aya2(p):
    '''aya2 : ALHAMDU LILLAH RABB ALALAMEEN '''
    p[0] = "✅ الآية صحيحة"

def p_aya3(p):
    '''aya3 : ALRAHMAN ALRAHEEM'''
    p[0] = "✅ الآية صحيحة"

def p_aya4(p):
    '''aya4 : MALIKI YAUM ALDEEN'''
    p[0] = "✅ الآية صحيحة"

def p_aya5(p):
    '''aya5 : IYYAKA NABUDU WA IYYAKA NAASTA3EEN'''
    p[0] = "✅ الآية صحيحة"

def p_aya6(p):
    '''aya6 : IHDINA ALSIRAT ALMOSTAQEEM'''
    p[0] = "✅ الآية صحيحة"

def p_aya7(p):
    '''aya7 : SIRAT ALLATHEEN AN3AMTA ALAYHIM'''
    p[0] = "✅ الآية صحيحة"

def p_aya8(p):
    '''aya8 : GHAYR ALMAGHDOUBI ALAYHIM WALA ALDAALEEN'''
    p[0] = "✅ الآية صحيحة"



# Gestion des erreurs syntaxiques
def p_error(p):
    if p:
        raise Exception(f"⛔ خطأ نحوي: الكلمة '{p.value}' في الموضع {p.lexpos} غير صحيحة. \n")
    raise Exception(f"⛔ العبارة غير مكتملة أو تحتوي على خطأ! \n")

# Construire le parser
parser = yacc.yacc()##parser.parse()

# Liste des mots corrects dans la sourate Al-Fatiha
mots_corrects = [##Action sematique verification  
    "بسم", "الله", "الرحمن", "الرحيم", "الحمد", "لله", "رب", "العالمين",
    "الرحمن", "الرحيم", "ملك", "يوم", "الدين", "إياك", "نعبد", "وإياك", "نستعين",
    "اهدنا", "الصراط", "المستقيم", "صراط", "الذين", "أنعمت", "عليهم", "غير",
    "المغضوب", "عليهم", "ولا", "الضالين"
]
# اقتراحات موسعة للكلمات الخاطئة
def generer_suggestions(mot):
    suggestions = get_close_matches(mot, mots_corrects, n=3, cutoff=0.6)
    if suggestions:
        return f"⛔ خطأ في الكلمة '{mot}'. هل كنت تقصد: {', '.join(suggestions)}؟\n"
    return f"⛔ خطأ في الكلمة '{mot}'. هذه الكلمة غير صحيحة ولا توجد اقتراحات متاحة.\n"

# التحقق من الكلمات المفقودة
def verifier_mots_manquants(mots_entree):
    index_correct = 0
    for mot in mots_corrects:
        if index_correct < len(mots_entree) and mots_entree[index_correct] == mot:
            index_correct += 1
        else:
            return f"⛔ الكلمة '{mot}' متوقعة بعد '{mots_entree[index_correct - 1]}'." if index_correct > 0 else f"⛔ يجب أن تبدأ السورة بـ '{mots_corrects[0]}'.\n"
    return None

# التحقق من التكرار أو الكلمات الزائدة
def verifier_doublons_ou_mots_en_trop(mots_entree):
    mots_verifies = []
    for mot in mots_entree:
        if mot in mots_verifies:
            return f"⛔ الكلمة '{mot}' مكررة بشكل غير ضروري.\n"
        if mot not in mots_corrects:
            return f"⛔ الكلمة '{mot}' زائدة ولا تنتمي إلى السورة.\n"
        mots_verifies.append(mot)
    return None

# التحقق من ترتيب الكلمات
def verifier_ordre(mots_entree):
    sourate_reduite = " ".join(mots_corrects)
    texte_reduit = " ".join(mots_entree)
    if sourate_reduite != texte_reduit:
        return f"⛔ الكلمات ليست بالترتيب الصحيح أو هناك أخطاء في العبارة.\n"
    return None

# عرض الكلمات الصحيحة المتبقية
def mots_restants(mots_entree):
    index_correct = len(mots_entree)
    return f" الكلمات المتبقية هي: {' '.join(mots_corrects[index_correct:])} \n"

def est_arabe(texte):
    #  Hna kt verifie ana koula 7aref f text rah kintami majmou3at 7rouf logha l3aribiya code ascci
    return all('\u0600' <= char <= '\u06FF' or char.isspace() for char in texte)

def verifier_mot_par_mot(text):
    for i in range(len(text.split())):  # Utilisation de range() et len()
        mot = text.split()[i]
        if mot not in mots_corrects:
            return False
    return True  # Correction de l'indentation du return


def analyse_lexical(texte):
    try:#########################lex*###############################
        # Analyse lexicale du texte
        lexer.input(texte)
        while True:
            tok = lexer.token()  # Prendre un token
            if not tok:
                break  # Terminer lorsqu'il n'y a plus de tokens

    except Exception as e:
        # Retourner False en cas d'erreur, et afficher un message d'erreur
        return f"⛔ لديك خطأ لغوي في النص. \n Erreur lexical ⚠ " # Indiquer qu'il y a une erreur dans l'analyse lexicale   

    return f"✅ lexicalement النص  لا يحتوي على أخطاء لغوية \n"  # Retourner True si l'analyse s'est bien passée

# تحليل النص
def analyser_chaine(texte):#### ici ou on commence l'explication  cette anlyse est seulement syntaxique 
    # تنظيف النص من التشكيل
    texte = re.sub(r'[ًٌٍَُِّْ]', '', texte)
    mots_entree = texte.split()

    erreurs = []

    # التحقق من الكلمات المفقودة
    erreur_manquante = verifier_mots_manquants(mots_entree)
    if erreur_manquante:
        erreurs.append(erreur_manquante)

    # التحقق من الكلمات الخاطئة
    for i, mot in enumerate(mots_entree):
        if mot not in mots_corrects:
            erreurs.append(generer_suggestions(mot))

    # التحقق من ترتيب الكلمات
    # erreur_ordre = verifier_ordre(mots_entree)
        #if erreur_ordre:
        # erreurs.append(erreur_ordre)

    # في حالة وجود أخطاء، عرض الكلمات المتبقية
    if erreurs:
        erreurs.append(mots_restants(mots_entree))
        return f"\n".join(erreurs)

    # التحقق إذا كانت جميع الكلمات بالترتيب الصحيح
    try:#########################yacc#####################
        
        result = parser.parse(texte)## il va allez directement ver p_phrase et p_aya1..
        if result:
            return result
    except Exception as e:
        erreurs.append(str(e))

    return f"\n".join(erreurs) if erreurs else f"✅ السورة صحيحة!\n"


##verifier les caracteres en francais 
def is_lettrre_francais(mot):
    # Vérifier si le mot contient uniquement des lettres françaises (y compris les lettres accentuées)
    return bool(re.match(r'^[a-zA-ZéèàâêîôûçœÉÈÀÂÊÎÔÛÇŒ]+$', mot))



####Translation
def translate_to_english(text):
    translations = {
        "بسم الله الرحمن الرحيم": "In the name of Allah, the Most Gracious, the Most Merciful",
        "الحمد لله رب العالمين": "Praise be to Allah, Lord of the Worlds",
        "الرحمن الرحيم": "The Most Gracious, the Most Merciful",
        "ملك يوم الدين": "Master of the Day of Judgment",
        "إياك نعبد وإياك نستعين": "You alone we worship, and You alone we ask for help",
        "اهدنا الصراط المستقيم": "Guide us to the straight path",
        "صراط الذين أنعمت عليهم": "The path of those upon whom You have bestowed favor",
        "غير المغضوب عليهم ولا الضالين": "Not of those who have evoked Your anger or of those who are astray"
    }
    return translations.get(text, text)

def translate_to_french(text):
    translations = {
        "بسم الله الرحمن الرحيم": "Au nom d'Allah, le Tout Miséricordieux, le Très Miséricordieux",
        "الحمد لله رب العالمين": "Louange à Allah, Seigneur des mondes",
        "الرحمن الرحيم": "Le Tout Miséricordieux, le Très Miséricordieux",
        "ملك يوم الدين": "Maître du Jour du Jugement",
        "إياك نعبد وإياك نستعين": "C'est Toi seul que nous adorons, et c'est Toi seul dont nous demandons l'aide",
        "اهدنا الصراط المستقيم": "Guide-nous vers le droit chemin",
        "صراط الذين أنعمت عليهم": "Le chemin de ceux que Tu as comblés de bienfaits",
        "غير المغضوب عليهم ولا الضالين": "Non pas ceux qui ont encouru Ta colère, ni ceux qui sont égarés"
    }
    return translations.get(text, text)



def translate_to_spanish(text):
    translations = {
        "بسم الله الرحمن الرحيم": "En el nombre de Allah, el Más Misericordioso, el Más Compasivo",
        "الحمد لله رب العالمين": "Alabado sea Allah, Señor de los Mundos",
        "الرحمن الرحيم": "El Más Misericordioso, el Más Compasivo",
        "ملك يوم الدين": "Soberano del Día del Juicio",
        "إياك نعبد وإياك نستعين": "A Ti solo adoramos, y a Ti solo pedimos ayuda",
        "اهدنا الصراط المستقيم": "Guíanos por el camino recto",
        "صراط الذين أنعمت عليهم": "El camino de aquellos sobre quienes has otorgado Tu favor",
        "غير المغضوب عليهم ولا الضالين": "No de aquellos que han incurrido en Tu ira ni de los extraviados"
    }
    return translations.get(text, text)



# Interface web avec Flask
@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    texte = ""
    errors = []
    solutions = []
    translations = {"English": "", "French": "", "Spanish": ""}
    
    if request.method == "POST":
        texte = request.form.get("texte")
  
        if texte in versets_corrects:  # Vérifier si le texte est un verset correct
            result = "✅ الآية صحيحة"
            translations["English"] = translate_to_english(texte)
            translations["French"] = translate_to_french(texte)
            translations["Spanish"] = translate_to_spanish(texte)
        elif verifier_mot_par_mot(texte):  # Utilisation correcte de 'texte' au lieu de 'text'
            result = f"✅ الكلمة او الكلمات صحيحة وتنتمي إلى كلمات السورة \n" + analyser_chaine(texte)
        elif est_arabe(texte):
            result = analyser_chaine(texte)  # fait appel au yacc
        else:
            # Si le texte n'est ni un verset ni un mot correct, analyser davantage
            result = analyse_lexical(texte)

        # Extract errors and solutions
        if "⛔" in result:  # If the result contains errors
            errors = [line for line in result.split("\n") if line.startswith("⛔")]
            solutions = [line for line in result.split("\n") if "هل كنت تقصد" in line or "المتوقعة" in line]
            
            # Log errors only
            log_errors(texte, "\n".join(errors), "\n".join(solutions))
   
    return render_template('main.html', texte=texte, result=result,translations=translations)



if __name__ == "__main__":
    app.run(debug=True)