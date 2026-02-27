import io

import os

import re

import json

import uuid 

import http.cookies

from PIL import Image

import pytesseract

import pypdf

import docx

from wsgiref.simple_server import make_server

from urllib.parse import parse_qs, urlparse 

from datetime import datetime, timedelta

from email.message import Message

from email.policy import HTTP

from email import message_from_bytes



import google.generativeai as genai



# --- AI CONFIGURATION ---

genai.configure(api_key="AIzaSyDbBfERpdBfHOaPpi4rlO6GavbGNJohdPo")



# --- AI RESPONSE FUNCTION ---

def get_ai_response(prompt):

    try:

        model = genai.GenerativeModel('gemini-2.5-flash') 

        response = model.generate_content(prompt)

        return response.text

    except Exception as e:

        print(f"AI ERROR (Terminal): {e}") 

        return "Sorry, I am having trouble connecting to the AI server right now."



HERBAL_DB = {

    "moringa": {

        "title": "Moringa oleifera (முருங் வைக்)",

        "desc": "Moringa oleifera, also known as the 'tree of life', is classified as an important herbal plant. Traditionally used to cure wounds, pain, ulcers, liver disease, heart disease, cancer, and inflammation.",

        "usage": "The pharmacological studies confirm the hepatoprotective, cardioprotective, and anti-inflammatory potential.",

        "ref": ["Fuglie, L.J. (1998)", "Gandji, K. et al. Afr. Crop Sci. J. (2018)"]

    },

    "cumin": {

        "title": "Cumin (சீரகம் )",

        "desc": "Attempts to evaluate the lipid-lowering, antioxidant and hepatoprotective effects of cumin supplementation. Oxidative stress-related biomarkers were reduced by cumin.",

        "usage": "Cumin powder supplementation ameliorates dyslipidemia, oxidative stress and hepatic damage.",

        "ref": ["J. Transcult. Nurs. (2018)", "T. Bhurosy, R. Jeewon Sci. World J. (2014)"]

    },

    "fenugreek": {

        "title": "Fenugreek (வெ ந் தய )",

        "desc": "Fenugreek is a legume used as a spice. It is known for its medicinal qualities such as antidiabetic, anticarcinogenic, hypocholesterolemic, antioxidant, and immunological activities.",

        "usage": "Used as a food stabilizer, adhesive, and emulsifying agent.",

        "ref": ["Abdelgawad et al. Arab J. Nucl. Sci. Appl. (2012)"]

    },

    "mint": {

        "title": "Mint (புதினான்)",

        "desc": "Mint oil and its main constituent l-menthol is extensively used in cuisines, foods, flavours and pharmaceuticals. It belongs to the family Lamiaceae.",

        "usage": "Menthol crystals are obtained directly from mint oil and used in commercial preparations.",

        "ref": ["Sustainable Chemistry and Pharmacy (2023)"]

    },

    "keezhanelli": {

        "title": "Phyllanthus amarus (கீழாநெ \nலி)",

        "desc": "Globally distributed herb known for therapeutic potentials: hepatoprotective, antioxidant, antiviral, antimicrobial, antidiabetic, anti-inflammatory, and nephroprotective.",

        "usage": "Used in the traditional system of medicine for over 2000 years.",

        "ref": ["Abankwa JK et al. HSI J. (2020)"]

    },

    "neem": {

        "title": "Azadirachta indica (வே ப்ப்பிவை\n)",

        "desc": "Called 'The village pharmacy'. Neem-derived extracts work as insect repellent, supplements to lower inflammation, and diabetic control.",

        "usage": "Used to combat cancer and for diverse health benefits.",

        "ref": ["Abdel-Moneim et al. BioMed Research International (2014)"]

    },

    "wonder-berry": {

        "title": "Sea buckthorn ( மணத்தாதக்க்ளி Family)",

        "desc": "Contains vitamins, carotenoids, polyphenols, fatty acids. Has antioxidant, anticancer, anti-hyperlipidemic, anti-obesity, and hepatoprotective effects.",

        "usage": "Functional food or dietary supplement for chronic diseases.",

        "ref": ["S.K. Lee et al. Nutr Res Prac (2009)"]

    },

    "hibiscus": {

        "title": "Hibiscus (செ ம்பருதாதி)",

        "desc": "Ingestion of infusions of Roselle may help reduce chronic diseases such as diabetes mellitus, dyslipidemia, hypertension, and cancer.",

        "usage": "Used in foods and drinks for tart, refreshing flavor.",

        "ref": ["Ali et al. (2005)", "Morton (1987)"]

    },

    "asafoetida": {

        "title": "Asafoetida (பெ ருங்ங்க்ய)",

        "desc": "Source of oleo-gum resin. Recent studies show relaxant, neuroprotective, memory enhancing, digestive enzyme, and antioxidant activities.",

        "usage": "Consumed as a spice and a folk medicine for centuries.",

        "ref": ["J.S. Pruthi Academic Press (1980)"]

    },

    "turmeric": {

        "title": "Turmeric (மஞ்ஞ்சள்)",

        "desc": "Vital culinary spice with health benefits. Shows protective efficacy against several liver diseases. Contains essential oils and curcumin.",

        "usage": "Protective efficacy against oxidative damage of the liver.",

        "ref": ["Indian spices and their bioactives in neurological disorders 2023"]

    },

    "ginger": {

        "title": "Ginger (இஞ்ஞ்சி)",

        "desc": "Contains chemicals responsible for antiarthritis, antiinflammatory, antidiabetic, antibacterial, antifungal, and anticancer effects.",

        "usage": "Used in the management of several human ailments.",

        "ref": ["The anti-oxidative potential of ginger extract 2022"]

    },

    "cloves": {

        "title": "Clove (கிராரபு)",

        "desc": "Rich in essential oils. See references for detailed quality specifications and indices for spice essential oils.",

        "usage": "Applications in herbs and spices trade and toothache relief.",

        "ref": ["K.V. Peter and M.R. Shylaja Volume 1 Pages 1-24"]

    },

    "rose-petals": {

        "title": "Rose (ரோபோரஜா )",

        "desc": "Medical benefits include treatment of inflammation, diabetes, dysmenorrhea, depression, stress, seizures, and aging.",

        "usage": "Rose water for skin care. Petals are excellent biomimetic material.",

        "ref": ["D. Gu et al. Phytochem. Anal. (2013)"]

    },

    "aloevera": {

        "title": "Aloe Vera (கற்ற்றா வை)",

        "desc": "Used for skin conditions and digestive health. Contains vitamins, enzymes, minerals, sugars, lignin, saponins, salicylic acids and amino acids.",

        "usage": "Topical application for skin, oral for digestion.",

        "ref": ["E.J. Buenz Toxicol. In Vitro (2008)"]

    },

    "cinnamon": {

        "title": "Cinnamon (இலவங்ங்கப்படவைட)",

        "desc": "Used as a carminative, antiseptic, and astringent. Increasingly popular for its benefits in glycemic control.",

        "usage": "Treatment of coronary risk factors, hypertension, diabetes mellitus.",

        "ref": ["Abraham et al. Mol. Nutr. Food Res. (2010)"]

    },

    "shangupuspham": {

        "title": "Shankhpushpi ( சங்ங்குபுஷ்ப)",

        "desc": "Effective to improve memory and intelligence. Useful in cold, cough, headaches. Considered anti-ageing.",

        "usage": "Improve memory, intelligence, and skin quality.",

        "ref": ["Abdulla et al. J. Med. Plants Res. (2010)"]

    },

    "thulasi": {

        "title": "Ocimum tenuiflorum (துளசி)",

        "desc": "Queen of herbs. Used for respiratory tract infections, immune boosting, and stress relief.",

        "usage": "Consumed as tea or raw leaves.",

        "ref": ["C. Gopi et al. J. Biotechnol. (2006)"]

    },

    "indigo-leaf": {

        "title": "Indigo naturalis ( அவுரிரஇவை\n)",

        "desc": "Historical application as a dye. Used for various ailments including hemoptysis, epistaxis, chest discomfort.",

        "usage": "Treatment of various ailments and hair dye.",

        "ref": ["Adachi et al. Circ. J. (2020)"]

    },

    "bhringraj": {

        "title": "Bringharaj (கரிரச\nங்கண்ண்)",

        "desc": "Famous herb for hair growth and liver disorders. Effective for skin diseases, cough, asthma, eye disorders.",

        "usage": "Improves hair growth, prevents hair fall and treats premature graying.",

        "ref": ["E.S. Pôças et al. Bioorg. Med. Chem. (2006)"]

    },

    "black-sesame-seeds": {

        "title": "Black sesame seeds ( கருப்ப்புஎள்)",

        "desc": "Traditional health food with notable nutritional value and pharmacological properties. Rich in calcium.",

        "usage": "Traditional health food and oil extraction.",

        "ref": ["A.M. Al-Attar et al. Saudi Journal of Biological Sciences (2017)"]

    },

    "haritaki": {

        "title": "Haritaki (கடுக்க்க்யா)",

        "desc": "Possesses great therapeutic value. Cleanses the digestive tract and is part of Triphala.",

        "usage": "Therapeutic uses described in Ayurvedic classics.",

        "ref": ["Chopra RN et al. Glossary of Indian medicinal plants (1956)"]

    },

    "coconut": {

        "title": "Coconut (தே ங்ங்க்யா)",

        "desc": "Coconut is classified as a saturated fat but contains medium-chain triglycerides which act differently metabolically.",

        "usage": "Source of healthful saturated fats and hydration.",

        "ref": ["Keys A. et al. Lancet (1957)"]

    },

    "garlic": {

        "title": "Garlic (பூண்ண்டு)",

        "desc": "Polyphenolic and organosulfur enriched. Excellent health-promoting effects on cancer, cardiovascular and metabolic disorders.",

        "usage": "Antioxidant, anti-inflammatory, and lipid-lowering properties.",

        "ref": ["Jiang T.A. J. AOAC Int. (2019)"]

    },

    "jojoba": {

        "title": "Jojoba (ஜோ ஜோ பா )",

        "desc": "Source of golden oil, structurally similar to spermaceti wax. Traditionally used for skin and scalp disorders.",

        "usage": "Skin/scalp disorders, anti-inflammatory, analgesic.",

        "ref": ["G.S. Dodos et al. Ind. Crops Prod. (2015)"]

    },

    "jatamansi": {

        "title": "Nardostachys jatamansi (ஜடாடமஞ்சி)",

        "desc": "Ayurvedic herb used for reducing stress and anxiety, improving sleep, and boosting memory.",

        "usage": "Root extract used in oils and capsules.",

        "ref": ["Seshadri TR et al. Tetrahedron (1967)"]

    },

    "curry-leaves": {

        "title": "Murraya koenigii (கருவே ப்ப்பிவை\n)",

        "desc": "Revitalizing molecules that can stop or reduce pathology of diseases. Rich source of carbazole alkaloids.",

        "usage": "Leaves, roots, and bark used in cooking and medicine.",

        "ref": ["Handral H.K. et al. Asian J. Pharm. Clin. Res. (2012)"]

    },

    "reetha": {

        "title": "Acacia concinna (சிகைவைக்க்க்யா)",

        "desc": "Natural hair cleanser. Shampoos with botanical extracts are well-known for their perceived health benefits.",

        "usage": "Natural active ingredients in shampoo formulations.",

        "ref": ["E. Guzmán, A. Lucia Cosmetics (2021)"]

    },

    "eucalyptus": {

        "title": "Eucalyptus (யூகலிப்ப்டஸ்)",

        "desc": "Essential oils have strong antibacterial properties against a variety of bacteria, fungi, and viruses.",

        "usage": "Combating infections, inhalation therapies.",

        "ref": ["Abbass HS J Pharm Res (2020)"]

    },

    "elaichi": {

        "title": "Cardamom (ஏலக்க்க்யா)",

        "desc": "Rich source of phenolic compounds. Shows antihypertensive, anti-oxidant, lipid-modifying, anti-inflammatory activities.",

        "usage": "Management of Metabolic Syndrome.",

        "ref": ["Mollazadeh H et al. Iran J Basic Med Sci. (2016)"]

    },

    "green-tea": {

        "title": "Green Tea ( கிரீர2ன்டீ)",

        "desc": "Health benefits for cancer, heart disease, and liver disease. Related to catechin content.",

        "usage": "Treat metabolic syndrome, obesity, type II diabetes.",

        "ref": ["McKay DL, Blumberg JB. J Am Coll Nutr. (2002)"]

    }

}



# ---------------------------------------------------------

# 2. ALLOPATHIC DATABASE (30 Items with Images)

# ---------------------------------------------------------

ALLOPATHY_DB = {

    "acetaminophen": {

        "title": "ACETAMINOPHEN (Paracetamol)",

        "desc": "Effective and safe pain management. Minimizes acute distress. Neonates are susceptible to long-term neurodevelopmental changes.",

        "usage": "Neonate PO/PR/IV based on weight.",

        "ref": ["B.J. Anderson et al. Expert Opin Drug Metab Toxicol (2015)"],

        "image": "/static/acetaminophen.jpg"

    },

    # ALLOPATHY_DB-il Ibuprofen section-ai indha maathiri update pannunga

    "ibuprofen": {

        "title": "IBUPROFEN",

        "iupac": "2-(4-Isobutylphenyl)propanoic acid",

        "formula": "C₁₃H₁₈O₂", # Standard formula for Ibuprofen

        "weight": "206.29 g/mol",

        "structure_desc": "A propionic acid group attached to a phenyl ring, with an isobutyl group (2-methylpropyl) at the 4-position.",

        "alt_names": "-2-(p-isobutylphenyl)propionic acid, 4-isobutyl-α-methylphenylacetic acid.",

        "desc": "Nonsteroidal anti-inflammatory drug (NSAID) used for treating pain, fever, and inflammation.",

        "usage": "Commonly used for relief of symptoms of arthritis, fever, and primary dysmenorrhea.",

        "image": "/static/Ibuprofen.jpg" # Indha image path-ai ungaloda actual structure image-kku maathikkunga

    },

    

    "aspirin": {

        "title": "ASPIRIN",

        "desc": "Anti-inflammatory and blood thinner. Affects pharmacokinetic parameters.",

        "usage": "3g orally per day in divided doses (Pain) or 75mg (Heart).",

        "ref": ["K. Akiyama et al. Cell Stem Cell (2012)"],

        "image": "/static/aspirin.jpg"

    },

    "diclofenac": {

        "title": "DICLOFENAC",

        "desc": "NSAID with analgesic, anti-inflammatory, and antipyretic effects.",

        "usage": "50 mg orally 2 or 3 times a day. Max 150 mg daily.",

        "ref": ["N. Deutsch et al. Anesthesiol Clin North America (2003)"],

        "image": "/static/diclofenac.jpg"

    },

    "morphine": {

        "title": "MORPHINE",

        "desc": "Opioid analgesic for visceral and somatic pain. Gold standard for severe pain.",

        "usage": "15 to 30 mg every 4 hours as needed.",

        "ref": ["Comparison of analgesic efficacy of tramadol (2024)"],

        "image": "/static/morphine.jpg"

    },

    "amoxicillin": {

        "title": "AMOXICILLIN",

        "desc": "Wide spectrum beta-lactam antibiotic. Effective against Gram-positive organisms.",

        "usage": "250 mg to 500 mg every 8 hours.",

        "ref": ["125l-Amoxicillin preparation (2021)"],

        "image": "/static/amoxicillin.jpg"

    },

    "azithromycin": {

        "title": "AZITHROMYCIN",

        "desc": "Macrolide antibiotic for respiratory bacterial infections. Inhibits viral load.",

        "usage": "500 mg Day 1, then 250 mg once daily for Days 2-5.",

        "ref": ["Abouhashem et al. Antioxidants Redox Signal. (2020)"],

        "image": "/static/azithromycin.jpg"

    },

    "ciprofloxacin": {

        "title": "CIPROFLOXACIN",

        "desc": "Fluoroquinolone antibiotic. Broad spectrum against Gram(-) aerobic bacilli.",

        "usage": "250-500 mg every 12 hours (UTI).",

        "ref": ["F. Panico et al. Adv Cancer Res (2009)"],

        "image": "/static/ciprofloxacin.jpg"

    },

    "doxycycline": {

        "title": "DOXYCYCLINE",

        "desc": "Tetracycline derivative with anti-inflammatory and neuroprotective actions.",

        "usage": "200 mg Day 1, then 100 mg daily.",

        "ref": ["L.M. Acevedo et al. Blood (2008)"],

        "image": "/static/doxycycline.jpg"

    },

    "metronidazole": {

        "title": "METRONIDAZOLE",

        "desc": "Nitroimidazole antibiotic active against anaerobic bacteria and protozoa.",

        "usage": "500 mg twice daily for 7 days (Bacterial Vaginosis).",

        "ref": ["Antimicrobial Resistance (2023)"],

        "image": "/static/metronidazole.jpg"

    },

    "fluconazole": {

        "title": "FLUCONAZOLE",

        "desc": "Antifungal. Penetrates well into CSF and brain parenchyma.",

        "usage": "150 mg single oral dose (Vaginal Candidiasis).",

        "ref": ["M.A. Pfaller et al. Diagn Microbiol Infect Dis (2010)"],

        "image": "/static/fluconazole.jpg"

    },

    "lisinopril": {

        "title": "LISINOPRIL",

        "desc": "ACE inhibitor. Reduces blood pressure by modulating renin-angiotensin-aldosterone system.",

        "usage": "Start 10 mg daily. Maintenance 20-40 mg daily.",

        "ref": ["A. Pinto et al. J Am Dent Assoc (2002)"],

        "image": "/static/lisinopril.jpg"

    },

    "amlodipine": {

        "title": "AMLODIPINE",

        "desc": "Calcium channel blocker. Does not cause reflex heart rate increase.",

        "usage": "5 mg to 10 mg once daily.",

        "ref": ["An Efficient Route to Annulated Pyrrolo (2025)"],

        "image": "/static/amlodipine.jpg"

    },

    "metoprolol": {

        "title": "METOPROLOL",

        "desc": "Beta-blocker. Extended-release matrix tablet formulations available.",

        "usage": "Immediate: 100 mg daily. Extended: 25-100 mg daily.",

        "ref": ["J Ford et al. Int. J. Pharm. (1985)"],

        "image": "/static/metoprolol.jpg"

    },

    "atorvastatin": {

        "title": "ATORVASTATIN",

        "desc": "Lipid-lowering drug. Stabilizes coronary atherosclerotic plaques.",

        "usage": "10 mg to 40 mg once daily.",

        "ref": ["Biochanin-A as SIRT-1 modulator 2025"],

        "image": "/static/atorvastatin.jpg"

    },

    "simvastatin": {

        "title": "SIMVASTATIN",

        "desc": "Targeting mTOR signaling has beneficial effects on spinal cord injury.",

        "usage": "20 mg to 40 mg once daily in the evening.",

        "ref": ["V.E. Bianchi Curr. Probl. Cardiol. (2020)"],

        "image": "/static/simvastatin.jpg"

    },

    "clopidogrel": {

        "title": "CLOPIDOGREL",

        "desc": "Inhibits ADP-induced platelet aggregation. Used in stroke and MI prevention.",

        "usage": "75 mg once daily.",

        "ref": ["An Overview of Vascular Dysfunction 2021"],

        "image": "/static/clopidogrel.jpg"

    },

    "metformin": {

        "title": "METFORMIN",

        "desc": "Fast onset of action. Management of type 2 diabetes.",

        "usage": "Start 500 mg once/twice daily. Max 2550 mg.",

        "ref": ["Formulation of vildagliptin and metformin 2024"],

        "image": "/static/metformin.jpg"

    },

    "levothyroxine": {

        "title": "LEVOTHYROXINE",

        "desc": "Thyroid hormone replacement.",

        "usage": "1.6 mcg/kg daily.",

        "ref": ["L. Schalliol et al. Chapter 33"],

        "image": "/static/levothyroxine.jpg"

    },

    "insulin": {

        "title": "INSULIN TABLET",

        "desc": "Oral insulin mimics natural release. Fragile in stomach acid.",

        "usage": "0.4 to 1.0 units/kg/day.",

        "ref": ["NCD Risk Factor Collaboration Lancet (2024)"],

        "image": "/static/insulin.jpg"

    },

    "zymoral": {

        "title": "ZYMORAL TABLET",

        "desc": "Enzyme supplement. Sublingual delivery overcomes first-pass metabolism.",

        "usage": "Swallow whole on empty stomach.",

        "ref": ["S. Bredenberg et al. Eur. J. Pharm. Sci. (2003)"],

        "image": "/static/zymoral.jpg"

    },

    "cetirizine": {

        "title": "CETIRIZINE",

        "desc": "Antihistamine. Stereoselectivity influences pharmacokinetics.",

        "usage": "10 mg tablet once daily.",

        "ref": ["Optimization of a portable ligand-free optical spectroscopy (2025)"],

        "image": "/static/cetirizine.jpg"

    },

    "montelukast": {

        "title": "MONTELUKAST",

        "desc": "Leukotriene receptor antagonist. Prevention of asthma attacks.",

        "usage": "One tablet daily evening.",

        "ref": ["F. Bertoldo et al. Chest (2005)"],

        "image": "/static/montelukast.jpg"

    },

    "sertraline": {

        "title": "SERTRALINE",

        "desc": "SSRI antidepressant. Effective for depressive symptoms.",

        "usage": "See physician instructions.",

        "ref": ["Mathers CD, Loncar D. PLoS Med. (2006)"],

        "image": "/static/sertraline.jpg"

    },

    "fluoxetine": {

        "title": "FLUOXETINE",

        "desc": "First generation SSRI. Favorable safety/efficacy ratio.",

        "usage": "Dosage dependent on condition.",

        "ref": ["Wong DT et al. Life Sci. (1995)"],

        "image": "/static/fluoxetine.jpg"

    },

    "alprazolam": {

        "title": "ALPRAZOLAM",

        "desc": "Triazolobenzodiazepine for anxiety and panic disorders.",

        "usage": "Bioavailability averages 80-100%.",

        "ref": ["Abernethy DR et al. Psychopharmacology (1983)"],

        "image": "/static/alprazolam.jpg"

    },

    "gabapentin": {

        "title": "GABAPENTIN",

        "desc": "Binds to voltage-gated calcium channels. Treats seizures and neuralgia.",

        "usage": "Initially for seizures, now broadly used.",

        "ref": ["Goudet, C. et al. Brain Res. Rev. (2009)"],

        "image": "/static/gabapentin.jpg"

    },

    "omeprazole": {

        "title": "OMEPRAZOLE",

        "desc": "Proton pump inhibitor for GERD management.",

        "usage": "20 mg daily for 4 weeks.",

        "ref": ["Aslam N et al. Frontline Gastroenterol (2023)"],

        "image": "/static/omeprazole.jpg"

    },

    "furosemide": {

        "title": "FUROSEMIDE",

        "desc": "Diuretic. Prevents fluid overload and acute kidney injury.",

        "usage": "Start 2 mg/kg orally.",

        "ref": ["Ronco C et al. Lancet (2019)"],

        "image": "/static/furosemide.jpg"

    },

    "prednisone": {

        "title": "PREDNISONE",

        "desc": "Glucocorticoid. Cornerstone treatment for nephrotic syndrome.",

        "usage": "Induces remission in children.",

        "ref": ["El Bakkali L et al. Pediatr Nephrol. (2011)"],

        "image": "/static/prednisone.jpg"

    }

}



# ---------------------------------------------------------

# 3. HOMEOPATHY DATABASE (From your original list)

# ---------------------------------------------------------

HOMEOPATHY_DB = {

    "arnica": {

        "title": "Arnica Montana",

        "desc": "For muscle pain & bruises",

        "price": "150",

        "type": "Homeopathy",

        "image": "https://placehold.co/200?text=Arnica"

    },

    "nux_vomica": {

        "title": "Nux Vomica",

        "desc": "For digestive issues",

        "price": "120",

        "type": "Homeopathy",

        "image": "https://placehold.co/200?text=Nux+Vomica"

    },

    "oscillo": {

        "title": "Oscillococcinum",

        "desc": "Flu relief",

        "price": "850",

        "type": "Homeopathy",

        "image": "https://placehold.co/200?text=Oscillo"

    },

    "rhus_tox": {

        "title": "Rhus Tox",

        "desc": "Joint pain relief",

        "price": "140",

        "type": "Homeopathy",

        "image": "https://placehold.co/200?text=Rhus+Tox"

    },

    "belladonna": {

        "title": "Belladonna",

        "desc": "For fever & inflammation",

        "price": "130",

        "type": "Homeopathy",

        "image": "https://placehold.co/200?text=Belladonna"

    },

    "arsenicum": {

        "title": "Arsenicum Album",

        "desc": "Food poisoning relief",

        "price": "160",

        "type": "Homeopathy",

        "image": "https://placehold.co/200?text=Arsenicum"

    }

}



# ---------------------------------------------------------

# 4. MEDICAL DEVICES DATABASE (From your original list)

# ---------------------------------------------------------

DEVICES_DB = {

    "thermometer": {

        "title": "Digital Thermometer",

        "desc": "Accurate fever check",

        "price": "250",

        "type": "Device",

        "image": "https://placehold.co/200?text=Thermometer"

    },

    "oximeter": {

        "title": "Pulse Oximeter",

        "desc": "Check oxygen levels",

        "price": "800",

        "type": "Device",

        "image": "https://placehold.co/200?text=Oximeter"

    },

    "bp_monitor": {

        "title": "BP Monitor (Digital)",

        "desc": "Automatic BP Check",

        "price": "1500",

        "type": "Device",

        "image": "https://placehold.co/200?text=BP+Monitor"

    },

    "glucometer": {

        "title": "Glucometer Kit",

        "desc": "Blood sugar test",

        "price": "1200",

        "type": "Device",

        "image": "https://placehold.co/200?text=Glucometer"

    },

    "nebulizer": {

        "title": "Nebulizer",

        "desc": "For respiratory relief",

        "price": "1800",

        "type": "Device",

        "image": "https://placehold.co/200?text=Nebulizer"

    }

}



# ---------------------------------------------------------

# 5. VITAMINS & SUPPLEMENTS DATABASE (From your original list)

# ---------------------------------------------------------

VITAMINS_DB = {

    "vit_c": {

        "title": "Vitamin C (500mg)",

        "desc": "Immunity Booster",

        "price": "300",

        "type": "Supplement",

        "image": "https://placehold.co/200?text=Vit+C"

    },

    "multivit": {

        "title": "Multivitamin Tablets",

        "desc": "Daily supplement",

        "price": "450",

        "type": "Supplement",

        "image": "https://placehold.co/200?text=Multivit"

    },

    "vit_d3": {

        "title": "Vitamin D3",

        "desc": "For bone health",

        "price": "120",

        "type": "Supplement",

        "image": "https://placehold.co/200?text=Vit+D3"

    },

    "fish_oil": {

        "title": "Fish Oil (Omega-3)",

        "desc": "Heart health",

        "price": "600",

        "type": "Supplement",

        "image": "https://placehold.co/200?text=Fish+Oil"

    },

    "calcium": {

        "title": "Calcium + Magnesium",

        "desc": "Strong bones",

        "price": "350",

        "type": "Supplement",

        "image": "https://placehold.co/200?text=Calcium"

    }

}



# --- DATA SETUP ---

MEDICAL_SHOPS = [

    {"id": "shop1", "name": "Apollo Pharmacy", "area": "Anna Nagar", "img": "https://placehold.co/100?text=Apollo"},

    {"id": "shop2", "name": "MedPlus", "area": "T. Nagar", "img": "https://placehold.co/100?text=MedPlus"},

    {"id": "shop3", "name": "NetMeds Local", "area": "Velachery", "img": "https://placehold.co/100?text=NetMeds"},

    {"id": "shop4", "name": "Thulasi Pharmacy", "area": "Tambaram", "img": "https://placehold.co/100?text=Thulasi"},

]



# --- INDEPENDENT SHOP MEDICINES (No Connection to Drugs Store) ---

SHOP_SPECIFIC_STOCK = [

    {"id": "s1", "name": "Dolo 650", "price": "30"},

    {"id": "s2", "name": "Saridon", "price": "45"},

    {"id": "s3", "name": "Vicks Action 500", "price": "50"},

    {"id": "s4", "name": "Benadryl Syrup", "price": "110"},

    {"id": "s5", "name": "Digene Gel", "price": "140"},

    {"id": "s6", "name": "Citrizine", "price": "35"},

    {"id": "s7", "name": "Paracetamol 500mg", "price": "20"},

    {"id": "s8", "name": "Volini Spray", "price": "180"},

    {"id": "s9", "name": "Crocin Advance", "price": "35"},

    {"id": "s10", "name": "Zandu Balm", "price": "40"}

]



# --- NURSE SERVICES DATA ---

NURSE_SERVICE_DETAILS = {

    'en': {

        'home-visit': {'title': 'Home Visit', 'description': 'Nurse will visit your home for checkups.'},

        'vitals': {'title': 'Vitals Checkup', 'description': 'BP, Sugar, and Pulse monitoring.'},

        'injection': {'title': 'Injection Service', 'description': 'IM/IV injections at home.'},

        'dressing': {'title': 'Wound Dressing', 'description': 'Post-surgical or injury dressing.'},

        'elderly': {'title': 'Elderly Care', 'description': 'Full day assistance for seniors.'}

    },

    'ta': {

        'home-visit': {'title': 'வீட்டு வருகை', 'description': 'செவிலியர் உங்கள் வீட்டிற்கே வருவார்.'},

        'vitals': {'title': 'உடல் பரிசோதனை', 'description': 'BP, சர்க்கரை அளவு சரிபார்ப்பு.'},

        'injection': {'title': 'ஊசி போடுதல்', 'description': 'வீட்டிலேயே ஊசி போடும் வசதி.'},

        'dressing': {'title': 'காயம் கட்டுதல்', 'description': 'அறுவை சிகிச்சை ரணங்களுக்கு கட்டு போடுதல்.'},

        'elderly': {'title': 'முதியோர் பராமரிப்பு', 'description': 'முதியவர்களுக்கான முழு நேர உதவி.'}

    }

}



# Helper: மருந்து கடையில் இருக்கா என்று பார்க்க

def check_shop_stock(medicine_name):

    # சும்மா ஒரு லாஜிக்: Shop 1 & 3 ல எல்லாம் இருக்கும், Shop 2 & 4 ல பாதிதான் இருக்கும்னு வச்சுப்போம்.

    # ரியல் டைம்ல Database Query வரும்.

    available_shops = []

    for shop in MEDICAL_SHOPS:

        # டம்மி லாஜிக்: எல்லா கடையிலும் இருக்குனு வைப்போம் (Demo காக)

        available_shops.append(shop['name'])

    return available_shops

# =========================================================

# DATABASE CONNECTORS (Updated)

# =========================================================



# 1. Get All Shops

def get_all_medical_shops(limit=20):

    return MEDICAL_SHOPS



# 2. Get Shop Details

def get_shop_details(shop_id):

    shop = next((s for s in MEDICAL_SHOPS if s['id'] == shop_id), None)

    return shop if shop else {"id": "unknown", "name": "Medical Shop", "area": "Chennai"}



# 3. Get Shop Medicines (இதை முழுசா மாத்துங்க)

def get_shop_medicines(shop_id, limit=20):

    # Drugs Store DB-ஐ தொடாமல், Shop Stock-ஐ மட்டும் ரிட்டர்ன் செய்யும்

    # கண்டிப்பா Data வரணும்னா இதை அப்படியே போடுங்க:

    return SHOP_SPECIFIC_STOCK

LANG = {

    'en': {

        'home': 'Home', 'about': 'About', 'services': 'Services', 'login': 'Login', 'logout': 'Logout',

        'user': 'User', 'language': 'Language', 'tamil': 'Tamil', 'english': 'English',

        'welcome_title': 'Welcome to GenMedX',

        'welcome_desc': 'An Online Clinic & Medical app for Tamil Nadu.<br>Manage medicines, clinics, appointments & lab services in one place.',

        'about_title': 'About GenMedX',

        'see_services_button': 'See Services', 'proceed_to_login_button': 'Proceed to Login',

        'login_title': 'Login to GenMedX', 'email_placeholder': 'Email ID', 'password_placeholder': 'Password',

        'invalid_login': 'Invalid email or password.', 'signup_button_text': 'Sign Up (New User)',

        'services_title': 'GenMedX Services', 'drugs_store_title': 'DRUGS STORE',

        'drugs_store_button': 'Explore Drug Store',

        'drugs_store_page_title': 'Drug Store',

        'search_placeholder': 'Search for medicines...',

        'upload_prescription': 'Upload Prescription',

        'allopathy': 'ALLOPATHY', 'ayurvedic': 'AYURVEDIC', 'homeopathy': 'HOMEOPATHY',

        'medical_devices': 'MEDICAL DEVICES', 'vitamins_supplements': 'Vitamins & Supplements',

        'back_to_drug_store': 'Back to Drug Store',

        'ayurvedic_products_title': 'Ayurvedic Products',

        'allopathy_products_title': 'Allopathic Medicines',

        'click_for_details': 'Click for Full Details',

        'back_to_services': 'Back to Services',

        

        # --- NEW ABOUT CONTENT (ENGLISH) ---

        'about_p1': 'GenMedX is a healthcare technology platform designed to make medical services more accessible.',

        'about_p2': 'We offer a partnership subscription model for local pharmacies.',

        'about_p3': 'Beyond pharmacy support, GenMedX provides doctor counselling services.',

        'about_p4': 'To enhance personalized healthcare, we have recently expanded our services.',

        'about_p5': 'At GenMedX, we believe healthcare should be more than just treatment.',

        'about_p6': 'GenMedX is not just an app; it is a step towards building a healthier community.',

        

        'doctor_consult_title': 'Doctor Consult', 'doctor_consult_desc_1': 'General Physician', 'doctor_consult_desc_2': 'Specialist', 'doctor_consult_desc_3': 'Video Consult', 'doctor_consult_button': 'Consult Doctor',

        'nurse_interventions': 'Nurse Services', 'geriatric_care': 'Geriatric Care', 'consult_nurse': 'Consult Nurse',

        'lab_interventions': 'Lab Services', 'lab_details': 'Lab Details',

        'pharmacist_interventions': 'Pharmacist Services', 'consult_pharmacy': 'Consult Pharmacy',

        'drugs_store_desc_1': 'Allopathy & Herbal', 'drugs_store_desc_2': 'Vitamins', 'drugs_store_desc_3': 'Medical Devices',

        'signup_title': 'Sign Up', 'all_fields_required': 'All fields required', 'enter_valid_email': 'Invalid Email', 'passwords_no_match': 'Passwords do not match', 'password_reqs': 'Weak Password', 'email_registered': 'Email already exists', 'confirm_password_placeholder': 'Confirm Password', 'already_registered': 'Login here',

        'page_not_found': 'Page Not Found', 'not_found_message': 'Path not found', 'go_home': 'Go Home',

        'nurse_services_title': 'Nurse Services', 'choose_service': 'Choose Service', 'call_nurse_home_visit': 'Home Visit', 'vitals_checkup': 'Vitals Checkup', 'post_hospitalization': 'Post Hospitalization', 'video_call': 'Video Call',

        'doctor_consult_page_title': 'Doctor Consultation', 'doctor_consult_page_content': 'Book your appointment',

        'nurse_video_consult_title': 'Nurse Video Call', 'video_placeholder': 'Video Interface',

        'service_detail_placeholder': 'Service details coming soon.',

        # Organ System Services

        'organ_system_title': 'Organ System Services',

        'organ_system_desc_1': 'Diabetic & BP Care',

        'organ_system_desc_2': 'Geriatric Support',

        'organ_system_desc_3': 'Report Analysis',

        'consult_organ_system': 'Consult Service',

        'organ_system_page_title': 'Services Organ System for Concern Department',

        'click_to_view_details': 'Click to view details',

        'back_to_organ_menu': 'Back to Menu',

        

        # 👇👇👇 இவைதான் உங்களுக்கு மிஸ் ஆகியிருக்கும்! 👇👇👇

        'seven_services': '7 Services',

        'ninety_days': 'For 90 days courses',

        'price_tag_old': 'Rs.11,000',

        'price_tag_new': 'Rs.8,000',

        # 👆👆👆



        'ai_chat_title': 'AI Health Assistant',

        'ai_chat_desc': 'Ask questions about health & medicines instantly.',

        'chat_now': 'Chat Now',



    },

    'ta': {

        'home': 'முகப்பு', 'about': 'பற்றி', 'services': 'சேவைகள்', 'login': 'உள்நுழை', 'logout': 'வெளியேறு',

        'user': 'பயனர்', 'language': 'மொழி', 'tamil': 'தமிழ்', 'english': 'English',

        'welcome_title': 'ஜென்மெட்எக்ஸ்-க்கு வரவேற்கிறோம்',

        'welcome_desc': 'தமிழ்நாட்டிற்கான ஒரு ஆன்லைன் மருத்துவமனை மற்றும் மருத்துவ செயலி.',

        'about_title': 'ஜென்மெட்எக்ஸ் பற்றி',

        'see_services_button': 'சேவைகளைப் பார்க்கவும்', 'proceed_to_login_button': 'உள்நுழையவும்',

        'login_title': 'ஜென்மெட்எக்ஸ்-ல் உள்நுழையவும்', 'email_placeholder': 'மின்னஞ்சல்', 'password_placeholder': 'கடவுச்சொல்',

        'invalid_login': 'தவறான மின்னஞ்சல்.', 'signup_button_text': 'பதிவு செய்யவும்',

        'services_title': 'ஜென்மெட்எக்ஸ் சேவைகள்', 'drugs_store_title': 'மருந்தகம்',

        'drugs_store_button': 'மருந்தகத்தைப் பார்க்கவும்',

        'drugs_store_page_title': 'மருந்தகம்',

        'search_placeholder': 'மருந்துகளைத் தேடுங்கள்...',

        'upload_prescription': 'மருந்துச் சீட்டைப் பதிவேற்றவும்',

        'allopathy': 'அலோபதி', 'ayurvedic': 'ஆயுர்வேதம்', 'homeopathy': 'ஹோமியோபதி',

        'medical_devices': 'மருத்துவ கருவிகள்', 'vitamins_supplements': 'வைட்டமின்கள்',

        'back_to_drug_store': 'மருந்தகத்திற்குத் திரும்பு',

        'ayurvedic_products_title': 'ஆயுர்வேத தயாரிப்புகள்',

        'allopathy_products_title': 'அலோபதி மருந்துகள்',

        'click_for_details': 'விவரங்களுக்கு கிளிக் செய்யவும்',

        'back_to_services': 'சேவைகளுக்குத் திரும்பு',

        

        'about_p1': 'ஜென்மெட்எக்ஸ் (GenMedX) என்பது மருத்துவ சேவைகளை அனைவருக்கும் எளிதாகவும், மலிவாகவும் கிடைக்கச் செய்யும் தளம்.',

        'about_p2': 'உள்ளூர் மருந்தகங்களுக்கான கூட்டாளர் சந்தா மாதிரியை நாங்கள் வழங்குகிறோம்.',

        'about_p3': 'மருந்தக சேவைகளைத் தாண்டி, பாதுகாப்பான ஆன்லைன் ஆலோசனைகளையும் வழங்குகிறது.',

        'about_p4': 'தனிப்பயனாக்கப்பட்ட சுகாதார சேவையை மேம்படுத்த, செவிலியர்கள் மற்றும் லேப் டெக்னீஷியன்களை இணைத்துள்ளோம்.',

        'about_p5': 'GenMedX-ல், சுகாதாரம் என்பது வெறும் சிகிச்சை மட்டுமல்ல.',

        'about_p6': 'GenMedX என்பது ஒரு செயலி மட்டுமல்ல; இது ஆரோக்கியமான சமூகத்தை உருவாக்குவதற்கான ஒரு படி.',



        'doctor_consult_title': 'மருத்துவர் ஆலோசனை', 'doctor_consult_desc_1': 'பொது மருத்துவர்', 'doctor_consult_desc_2': 'சிறப்பு மருத்துவர்', 'doctor_consult_desc_3': 'காணொளி ஆலோசனை', 'doctor_consult_button': 'மருத்துவரை அணுகவும்',

        'nurse_interventions': 'செவிலியர் சேவைகள்', 'geriatric_care': 'முதியோர் பராமரிப்பு', 'consult_nurse': 'செவிலியரிடம் ஆலோசனை',

        'lab_interventions': 'ஆய்வக சேவைகள்', 'lab_details': 'விவரங்கள்',

        'pharmacist_interventions': 'மருந்தாளர் சேவைகள்', 'consult_pharmacy': 'ஆலோசனை',

        'drugs_store_desc_1': 'அலோபதி & மூலிகை', 'drugs_store_desc_2': 'வைட்டமின்கள்', 'drugs_store_desc_3': 'கருவிகள்',

        'signup_title': 'பதிவு', 'all_fields_required': 'எல்லாம் தேவை', 'enter_valid_email': 'தவறான மின்னஞ்சல்', 'passwords_no_match': 'கடவுச்சொல் பொருந்தவில்லை', 'password_reqs': 'வலுவற்ற கடவுச்சொல்', 'email_registered': 'மின்னஞ்சல் உள்ளது', 'confirm_password_placeholder': 'உறுதிப்படுத்தவும்', 'already_registered': 'உள்நுழையவும்',

        'page_not_found': 'பக்கம் இல்லை', 'not_found_message': 'பாதை', 'go_home': 'முகப்பு',

        'nurse_services_title': 'செவிலியர் சேவைகள்', 'choose_service': 'தேர்ந்தெடு', 'call_nurse_home_visit': 'வீட்டு வருகை', 'vitals_checkup': 'உயிர் குறிகள்', 'post_hospitalization': 'பிந்தைய கவனிப்பு', 'video_call': 'காணொளி அழைப்பு',

        'doctor_consult_page_title': 'மருத்துவர் ஆலோசனை', 'doctor_consult_page_content': 'பதிவு செய்யவும்',

        'nurse_video_consult_title': 'செவிலியர் காணொளி', 'video_placeholder': 'இடைமுகம்',

        'service_detail_placeholder': 'விவரங்கள் விரைவில் வரும்.',

        # Organ System Services

        'organ_system_title': 'உறுப்பு மண்டல சேவைகள்',

        'organ_system_desc_1': 'நீரிழிவு & BP',

        'organ_system_desc_2': 'முதியோர் உதவி',

        'organ_system_desc_3': 'அறிக்கை ஆய்வு',

        'consult_organ_system': 'ஆலோசிக்கவும்',

        'organ_system_page_title': 'துறை சார்ந்த உறுப்பு மண்டல சேவைகள்',

        'click_to_view_details': 'விவரங்களைப் பார்க்க கிளிக் செய்யவும்',

        'back_to_organ_menu': 'மீண்டும் மெனுவிற்கு',

        

        # 👇👇👇 இவைதான் உங்களுக்கு மிஸ் ஆகியிருக்கும்! 👇👇👇

        'seven_services': '7 சேவைகள்',

        'ninety_days': '90 நாட்கள் படிப்புகளுக்கு',

        'price_tag_old': 'ரூ.11,000',

        'price_tag_new': 'ரூ.8,000',

        # 👆👆👆



        'ai_chat_title': 'AI மருத்துவ உதவியாளர்',

        'ai_chat_desc': 'உடல்நலம் மற்றும் மருந்துகள் பற்றிய கேள்விகளைக் கேளுங்கள்.',

        'chat_now': 'பேசவும்',



    }

}



AYURVEDIC_PRODUCTS_DATA = [

    {'key': 'moringa', 'url': "https://i.supaimg.com/84d9a0d0-0ed6-4b99-ae50-9c9998e0b28c.png", 'name': {'en': 'MORINGA', 'ta': 'முருங்கை'}},

    {'key': 'cumin', 'url': "https://i.supaimg.com/edb6de08-21c7-4638-b3f7-c26f02824981.png", 'name': {'en': 'CUMIN SEEDS', 'ta': 'சீரக விதை'}},

    {'key': 'fenugreek', 'url': "https://i.supaimg.com/20a68dcc-c2c1-451a-a7db-db9c97d81b18.png", 'name': {'en': 'FENUGREEK', 'ta': 'வெந்தயக் கீரை'}},

    {'key': 'mint', 'url': "https://i.supaimg.com/c16d157b-e411-47ef-90bb-c4107368e39f.png", 'name': {'en': 'MINT', 'ta': 'புதினா'}},

    {'key': 'keezhanelli', 'url': "https://i.supaimg.com/ff674f94-eb9e-4ea4-890b-b8d4a2b1a978.png", 'name': {'en': 'KEEZHANELLI', 'ta': 'கீழானெல்லி'}},

    {'key': 'neem', 'url': "https://i.supaimg.com/5e2d7f44-bbc1-46fc-a690-711389957cfd.png", 'name': {'en': 'NEEM', 'ta': 'வேப்பிலை'}},

    {'key': 'wonder-berry', 'url': "https://i.supaimg.com/295ee4c1-5abf-4c57-b2a9-af92fbfe66c6.png", 'name': {'en': 'WONDER BERRY', 'ta': 'மணத்தக்காளி'}},

    {'key': 'hibiscus', 'url': "https://i.supaimg.com/5837befa-f2da-4a0b-b2a9-477f6c84fe2d.png", 'name': {'en': 'HIBISCUS', 'ta': 'செம்பருத்தி'}},

    {'key': 'asafoetida', 'url': "https://i.supaimg.com/87ea4fae-c5bc-4d91-a23d-5c394d87491e.png", 'name': {'en': 'ASAFOETIDA', 'ta': 'பெருங்காயம்'}},

    {'key': 'turmeric', 'url': "https://i.supaimg.com/23d8a81f-e9df-4cd6-8c0f-4bb8c749ba8d.png", 'name': {'en': 'TURMERIC', 'ta': 'மஞ்சள்'}},

    {'key': 'ginger', 'url': "https://i.supaimg.com/a3a181af-bc92-4a83-b067-a5095fa88f81.png", 'name': {'en': 'GINGER', 'ta': 'இஞ்சி'}},

    {'key': 'cloves', 'url': "https://i.supaimg.com/54a90eff-a3fd-4699-9ce6-65c190af538d.png", 'name': {'en': 'CLOVES', 'ta': 'கிராம்பு'}},

    {'key': 'rose-petals', 'url': "https://i.supaimg.com/6abfd758-7caa-4734-bb3f-10532e1244b2.png", 'name': {'en': 'ROSE PETALS', 'ta': 'ரோஜா'}},

    {'key': 'aloevera', 'url': "https://i.supaimg.com/b35ad9de-eb69-49d3-95ed-a83f55395336.png", 'name': {'en': 'ALOEVERA', 'ta': 'கற்றாழை'}},

    {'key': 'cinnamon', 'url': "https://i.supaimg.com/a824d55e-961b-494e-ab4d-25bc06fd3952.png", 'name': {'en': 'CINNAMON', 'ta': 'இலவங்கப்பட்டை'}},

    {'key': 'shangupuspham', 'url': "https://i.supaimg.com/91d47146-0edc-4845-b3d6-7653e9b4e5c5.png", 'name': {'en': 'SHANGUPUSPHAM', 'ta': 'சங்கு புஷ்பம்'}},

    {'key': 'thulasi', 'url': "https://i.supaimg.com/e065794f-a3af-4b2b-a340-4f30cc9cc72c.png", 'name': {'en': 'THULASI', 'ta': 'துளசி'}},

    {'key': 'indigo-leaf', 'url': "https://i.supaimg.com/7ffd69c7-2a43-49a4-bf92-c348a6350a2a.png", 'name': {'en': 'INDIGO LEAF', 'ta': 'அவுரி இலை'}},

    {'key': 'bhringraj', 'url': "https://i.supaimg.com/3f35982a-f25b-405b-84ac-f2a82c944525.png", 'name': {'en': 'BHRINGRAJ', 'ta': 'கரிசலாங்கண்ணி'}},

    {'key': 'black-sesame-seeds', 'url': "https://i.supaimg.com/8c30eef1-4772-4f4f-b742-4567c3d23539.png", 'name': {'en': 'BLACK SESAME SEEDS', 'ta': 'கருப்பு எள்'}},

    {'key': 'haritaki', 'url': "https://i.supaimg.com/aaa4c518-9727-4436-8a03-6d84e49549f8.png", 'name': {'en': 'HARITAKI', 'ta': 'கடுக்காய்'}},

    {'key': 'coconut', 'url': "https://i.supaimg.com/f369be06-f265-4816-bd51-cf75e6bf63df.png", 'name': {'en': 'COCONUT', 'ta': 'தேங்காய்'}},

    {'key': 'garlic', 'url': "https://i.supaimg.com/18b8db3e-ab79-4e5d-b03e-8f40483789d6.png", 'name': {'en': 'GARLIC', 'ta': 'பூண்டு'}},

    {'key': 'jojoba', 'url': "https://i.supaimg.com/18229b86-190d-4847-a9b7-9281682a04d4.png", 'name': {'en': 'JOJOBA', 'ta': 'ஜோஜோபா'}},

    {'key': 'jatamansi', 'url': "https://i.supaimg.com/562bab6c-f0e8-425b-a0c6-4cf199431e77.png", 'name': {'en': 'JATAMANSI', 'ta': 'ஜடாமஞ்சி'}},

    {'key': 'curry-leaves', 'url': "https://i.supaimg.com/ab0bb3a5-5793-4dc9-9f1a-85f754fc1fa8.png", 'name': {'en': 'CURRY LEAVES', 'ta': 'கருவேப்பிலை'}},

    {'key': 'reetha', 'url': "https://i.supaimg.com/75e36086-0b30-4ec7-a1cb-c137c4d12fcb.png", 'name': {'en': 'REETHA', 'ta': 'பண்ணங்கொட்டை'}},

    {'key': 'eucalyptus', 'url': "https://i.supaimg.com/f255cf4b-ffd2-4248-9f4c-6ed8e21484bd.png", 'name': {'en': 'EUCALYPTUS', 'ta': 'தய்ழயிலை'}},

    {'key': 'elaichi', 'url': "https://i.supaimg.com/6dcb1f1f-06b4-489d-8118-6455965c1d0e.png", 'name': {'en': 'ELAICHI', 'ta': 'ஏலக்காய்'}},

    {'key': 'green-tea', 'url': "https://i.supaimg.com/1adc2be2-43c8-4c46-8b88-c976fddfdba4.png", 'name': {'en': 'GREEN TEA', 'ta': 'கிரீன் டீ'}}

]



# =========================================================

# DATABASE SETUP (Global)

# =========================================================

DB_FILE = "users.json"



# 1. டேட்டாவை லோட் செய்யும் ஃபங்ஷன்

def load_users():

    if not os.path.exists(DB_FILE):

        # முதல் முறை ரன் ஆகும்போது Default Admin-ஐ உருவாக்குவோம்

        default_data = {

            "admin@genmedx.com": {"password": "Admin@123", "role": "Admin", "name": "Super Admin"}

        }

        with open(DB_FILE, 'w') as f: json.dump(default_data, f)

        return default_data

    try:

        with open(DB_FILE, 'r') as f: return json.load(f)

    except:

        return {}



# 2. டேட்டாவை சேவ் செய்யும் ஃபங்ஷன்

def save_users(users_data):

    with open(DB_FILE, 'w') as f:

        json.dump(users_data, f, indent=4)



# =========================================================

# GLOBAL VARIABLES (முக்கியமான பகுதி)

# =========================================================



# 👇👇👇 இந்த வரிகள் எல்லாம் "ஓரத்தில்" (No Space at start) இருக்கணும் 👇👇👇



USERS = load_users()     # யூசர்கள் லோட் ஆகிடும்

SESSIONS = {}            # இதுதான் உங்களுக்கு எரர் அடிச்சது. இப்போ சரியாகிடும்.

USER_ACTIVITIES = []     # ஆக்டிவிட்டி ஸ்டோர்



# --- ADMIN CONFIGURATION ---

ADMIN_EMAIL = "admin@genmedx.com"



def extract_text_from_stream(filename, file_data):

    ext = filename.lower().split('.')[-1]

    text = ""

    print(f"DEBUG: Processing {filename} ({len(file_data)} bytes)")



    try:

        # 1. Handle Images (JPG, PNG, etc.)

        if ext in ['jpg', 'jpeg', 'png', 'bmp']:

            try:

                image_stream = io.BytesIO(file_data)

                image = Image.open(image_stream)

                # Tesseract ஐ பயன்படுத்தி டெக்ஸ்டை எடுக்கிறோம்

                text = pytesseract.image_to_string(image)

            except Exception as e:

                print(f"Image Error: {e}")



        # 2. Handle PDF

        elif ext == 'pdf':

            try:

                pdf_file = io.BytesIO(file_data)

                reader = pypdf.PdfReader(pdf_file)

                for page in reader.pages:

                    t = page.extract_text()

                    if t: text += t + "\n"

            except Exception as e:

                print(f"PDF Error: {e}")



        # 3. Handle Word (DOCX)

        elif ext in ['docx', 'doc']:

            try:

                doc_file = io.BytesIO(file_data)

                doc = docx.Document(doc_file)

                for para in doc.paragraphs:

                    text += para.text + "\n"

            except Exception as e:

                print(f"Word Error: {e}")



    except Exception as e:

        print(f"General Extract Error: {e}")

        

    return text.lower() 



def get_cookie(environ, name):

    cookies = environ.get('HTTP_COOKIE', '')

    for c in cookies.split(';'):

        if '=' in c:

            k, v = c.strip().split('=', 1)

            if k == name: return v

    return None



def make_set_cookie_header(name, value, days=30):

    expires = (datetime.utcnow() + timedelta(days=days)).strftime("%a, %d %b %Y %H:%M:%S GMT")

    return f"{name}={value}; Path=/; Expires={expires}; HttpOnly"



def serve_static_file(environ, start_response, file_path):

    try:

        clean_path = file_path.lstrip('/').replace('static/', '', 1)

        static_dir = os.path.join(os.getcwd(), 'static')

        full_path = os.path.join(static_dir, clean_path)

        if os.path.exists(full_path) and os.path.isfile(full_path):

            with open(full_path, 'rb') as f: file_data = f.read()

            content_type = 'image/jpeg' if clean_path.lower().endswith(('.jpg', '.jpeg')) else 'image/png'

            start_response('200 OK', [('Content-type', content_type)])

            return [file_data]

        else:

            start_response('404 Not Found', [('Content-type', 'text/plain; charset=utf-8')])

            return [b'File not found']

    except Exception as e:

        error_msg = f"<h1>Error Found!</h1><p><b>Error Details:</b> {str(e)}</p>"

        start_response('200 OK', [('Content-type', 'text/html')])

        return [error_msg.encode('utf-8')]



def serve_upload_file(environ, start_response, file_path):

    try:

        # /uploads/filename.jpg -> filename.jpg ஆக மாற்றுகிறோம்

        clean_path = file_path.replace('/uploads/', '', 1)

        upload_dir = os.path.join(os.getcwd(), 'uploads')

        

        # Reports folder குள்ள இருந்தால்

        if 'reports/' in file_path:

             clean_path = file_path.replace('/uploads/reports/', '', 1)

             upload_dir = os.path.join(upload_dir, 'reports')



        full_path = os.path.join(upload_dir, clean_path)

        

        if os.path.exists(full_path) and os.path.isfile(full_path):

            # File Extension பார்க்கிறோம்

            ext = clean_path.split('.')[-1].lower()

            content_type = 'text/plain'

            if ext in ['jpg', 'jpeg']: content_type = 'image/jpeg'

            elif ext == 'png': content_type = 'image/png'

            elif ext == 'pdf': content_type = 'application/pdf'

            

            with open(full_path, 'rb') as f: file_data = f.read()

            start_response('200 OK', [('Content-type', content_type)])

            return [file_data]

        else:

            start_response('404 Not Found', [('Content-type', 'text/plain')])

            return [b'File not found']

    except Exception as e:

        start_response('500 Error', [('Content-type', 'text/plain')])

        return [str(e).encode()]



def nav_bar(user, lang):

    link_style = "color:#2c3e50; text-decoration:none; font-weight:bold;"

    

    # அட்மின் லிங்க் லாஜிக்

    admin_link = ""

    if user == "admin@genmedx.com": # உங்கள் அட்மின் ஈமெயில்

        admin_link = f"<span style='margin: 0 10px;'>|</span> <a href='/admin' style='color:#d35400; font-weight:bold;'>🛡️ Admin</a>"



    # User இருந்தால் Logout காட்டும், இல்லையென்றால் Login காட்டும்

    if user:

        user_badge = f"<span style='font-weight:bold; color:#007bff;'>👤 {user}</span> | <a href='/logout' style='color:red; text-decoration:none; font-weight:bold;'>Logout 🚪</a>"

    else:

        user_badge = f"<a href='/login' style='{link_style}'>Login 🔐</a>"



    nav_html = f"""

        <a href='/home' style='{link_style}'>{LANG[lang]['home']}</a>

        <span style="margin: 0 10px;">|</span>

        <a href='/about' style='{link_style}'>{LANG[lang]['about']}</a>

        <span style="margin: 0 10px;">|</span>

        <a href='/services' style='{link_style}'>{LANG[lang]['services']}</a>

        {admin_link}

    """

    

    return f'''

    <div class="navbar" style="background:#fff; border-bottom:1px solid #ddd; padding:15px; font-size:16px; display:flex; justify-content:space-between; align-items:center; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">

        <div>{nav_html}</div>

        <div>{user_badge}</div>

    </div>

    '''



def pw_eye_head_html():

    eye_visible_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.816 1.097-2.276 2.24-3.638 2.895C9.879 11.832 8.12 12.5 6 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 1 1.172 8z"/><path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/></svg>'''

    eye_hidden_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7.028 7.028 0 0 0-2.79.588l.77.771A5.94 5.94 0 0 1 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.134 13.134 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755-.165.165-.337.328-.517.486l.708.709z"/><path d="M11.297 9.176a3.5 3.5 0 0 0-4.474-4.474l.823.823a2.5 2.5 0 0 1 2.829 2.829l.822.822zm-2.943 1.288.822.822.084.083a3.5 3.5 0 0 1-4.474-4.474l.083.084.823.823a2.5 2.5 0 0 0 2.829 2.829z"/><path d="M3.35 5.47c-.18.16-.353.322-.518.487A13.134 13.134 0 0 0 1.172 8l.195.288c.335.48.83 1.12 1.465 1.755C4.121 11.332 5.881 12.5 8 12.5c.716 0 1.39-.133 2.02-.36l.77.772A7.029 7.029 0 0 1 8 13.5C3 13.5 0 8 0 8s.939-1.721 2.641-3.238l.708.709zm10.296 8.884-12-12 .708-.708 12 12-.708.708z"/></svg>'''

    return f'''<style>.pw-container{{position:relative;display:inline-block;width:230px;}}.pw-eye{{position:absolute;right:8px;top:50%;transform:translateY(-50%);background:transparent;border:none;cursor:pointer;outline:none;line-height:0;}}.pw-input{{width:100%;padding-right:35px;}}</style><script>const eye_visible=`{eye_visible_svg}`;const eye_hidden=`{eye_hidden_svg}`;function toggleEye(id,eye_button){{var pwd=document.getElementById(id);if(pwd.type==="password"){{pwd.type="text";eye_button.innerHTML=eye_visible;}}else{{pwd.type="password";eye_button.innerHTML=eye_hidden;}}}}</script>'''



def page_logo_only():

    logo_path = "/static/GenMedX.jpg"

    html = f"""<html><head><title>GenMedX</title><meta http-equiv='refresh' content='3;url=/home'><style>body, html {{margin:0;padding:0;height:100%;font-family:Arial,sans-serif;background-color:#FFFFFF;}}.logo-container {{display:flex;justify-content:center;align-items:center;height:100vh;background-color:#FFFFFF;}}.logo-image {{max-width:650px;width:90vw;height:auto;border-radius:15px;animation:fadeIn 2s ease-in-out;}}@keyframes fadeIn {{from{{opacity:0;transform:scale(0.9);}} to{{opacity:1;transform:scale(1);}}}}</style></head><body><div class='logo-container'><img src='{logo_path}' alt='GenMedX Logo' class='logo-image'/></div></body></html>"""

    return html.encode('utf-8')



def page_professional_dashboard(user, lang, role):

    # 1. Tasks Filtering Logic

    my_tasks = []

    if 'USER_ACTIVITIES' in globals():

        for act in reversed(USER_ACTIVITIES):

            category = act.get('category', '')

            detail = act.get('detail', '')

            

            # Role Based Filtering

            if role == 'Doctor' and ('Booking' in category or 'VideoCall' in category): my_tasks.append(act)

            elif role == 'Nurse' and ('NurseRequest' in category or 'Booking' in category): my_tasks.append(act)

            elif role == 'Pharmacist' and 'PharmacyOrder' in category: my_tasks.append(act)

            elif role == 'LabTech' and ('Upload' in category or 'Lab' in detail): my_tasks.append(act)

            elif role == 'Counsellor' and ('Counselling' in detail or 'Booking' in category): my_tasks.append(act)



    # 2. HTML Table Logic

    rows_html = ""

    if not my_tasks:

        rows_html = "<tr><td colspan='3' style='text-align:center; padding:20px;'>No pending tasks.</td></tr>"

    else:

        for task in my_tasks:

            # File Link Logic

            display_detail = task['detail']

            if "Uploaded" in display_detail:

                 parts = display_detail.split(':')

                 if len(parts) > 1:

                     fname = parts[1].strip().split(' ')[0]

                     link = f"/uploads/reports/{fname}" if "(Organ System)" in display_detail else f"/uploads/{fname}"

                     display_detail = f"{display_detail} <a href='{link}' target='_blank'>[View File]</a>"

            

            rows_html += f"<tr><td>{task['time']}</td><td><span class='badge'>{task['category']}</span></td><td>{display_detail}</td></tr>"



    css = """

    <style>

        .dash-container { max-width: 1000px; margin: 30px auto; padding: 20px; }

        .welcome-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 30px; }

        .task-table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0 5px 15px rgba(0,0,0,0.1); border-radius: 10px; overflow: hidden; margin-bottom: 30px; }

        th, td { padding: 15px; text-align: left; border-bottom: 1px solid #eee; }

        th { background: #f8f9fa; color: #333; }

        .badge { background: #007bff; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px; }

        .pw-box { background: #fff3e0; border: 1px solid #ffcc80; padding: 20px; border-radius: 10px; margin-top: 20px; display:flex; align-items:center; justify-content:space-between; }

        .pw-btn { background: #ff9800; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight:bold; }

    </style>

    """



    content = f"""

    {css}

    <div class="dash-container">

        <div class="welcome-card">

            <h1>👨‍⚕️ {role} Dashboard</h1>

            <p>Welcome, <b>{USERS[user].get('name', user)}</b></p>

        </div>



        <h3>📅 Your Tasks</h3>

        <table class="task-table">

            <thead><tr><th>Time</th><th>Type</th><th>Details</th></tr></thead>

            <tbody>{rows_html}</tbody>

        </table>

        

        <div class="pw-box">

            <div>

                <h3 style="margin:0; color:#e65100;">🔐 Privacy & Security</h3>

                <p style="margin:5px 0 0 0; color:#555;">Change your default password here.</p>

            </div>

            <form action="/change-password" method="POST" style="display:flex; gap:10px;">

                <input type="password" name="new_password" placeholder="New Password" required style="padding:10px; border:1px solid #ccc; border-radius:5px;">

                <button type="submit" class="pw-btn">Update Password</button>

            </form>

        </div>



        <div style="margin-top: 30px; text-align: center;">

            <a href="/logout"><button style="padding: 10px 20px; background: #dc3545; color: white; border: none; border-radius: 5px; cursor: pointer;">Logout</button></a>

        </div>

    </div>

    """

    return f"<!DOCTYPE html><html><head><title>{role} Panel</title></head><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



# =========================================================

# NEW ADMIN PAGES (Manage Staff & Patients)

# =========================================================



def page_admin_staff(user, lang):

    # அட்மின் செக்கிங்

    if user not in USERS or USERS[user].get('role') != 'Admin':

        return page_notfound("Access Denied", user, lang)



    # Staff List Logic

    staff_rows = ""

    for email, data in USERS.items():

        role = data.get('role', 'Patient')

        if role != 'Admin' and role != 'Patient': 

            staff_rows += f"""

            <tr>

                <td>{data.get('name', email)}</td>

                <td>{email}</td>

                <td><b>{role}</b></td>

                <td>

                    <form action='/admin/delete-user' method='POST' onsubmit="return confirm('Remove {data.get('name')}?');">

                        <input type='hidden' name='email' value='{email}'>

                        <button style='background:#ff4444; color:white; border:none; padding:5px 10px; border-radius:5px; cursor:pointer;'>🗑️ Remove</button>

                    </form>

                </td>

            </tr>"""

    if not staff_rows: staff_rows = "<tr><td colspan='4' style='text-align:center;'>No Staff Found.</td></tr>"



    css = """<style>.admin-box { max-width: 1000px; margin: 30px auto; padding: 20px; font-family: sans-serif; } table { width: 100%; border-collapse: collapse; margin-top: 20px; } th, td { padding: 12px; border-bottom: 1px solid #ddd; text-align: left; } th { background: #f4f4f4; } .form-box { background: #e3f2fd; padding: 20px; border-radius: 10px; margin-bottom: 30px; } input, select, button { padding: 10px; margin: 5px; border-radius: 5px; border: 1px solid #ddd; } .back-btn { background: #555; color: white; text-decoration: none; padding: 10px 20px; border-radius: 5px; display: inline-block; margin-bottom: 20px; }</style>"""



    content = f"""

    {css}

    <div class="admin-box">

        <a href="/admin" class="back-btn">&larr; Back to Dashboard</a>

        <div class="form-box">

            <h2>➕ Add New Staff Member</h2>

            <form method="POST" action="/admin/create-user">

                <input type="text" name="name" placeholder="Name" required style="width:150px;">

                <input type="email" name="email" placeholder="Email" required style="width:200px;">

                <input type="text" name="password" value="Staff@123" required style="width:100px;">

                <select name="role">

                    <option value="Doctor">Doctor</option>

                    <option value="Nurse">Nurse</option>

                    <option value="Pharmacist">Pharmacist</option>

                    <option value="LabTech">Lab Tech</option>

                    <option value="Counsellor">Counsellor</option>

                </select>

                <button type="submit" style="background:#28a745; color:white; cursor:pointer;">Create</button>

            </form>

        </div>

        <h2>👨‍⚕️ Current Staff List</h2>

        <table><thead><tr><th>Name</th><th>Email</th><th>Role</th><th>Action</th></tr></thead><tbody>{staff_rows}</tbody></table>

    </div>

    """

    return f"<!DOCTYPE html><html><head><title>Manage Staff</title></head><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



def page_admin_patients(user, lang):

    # அட்மின் செக்கிங்

    if user not in USERS or USERS[user].get('role') != 'Admin':

        return page_notfound("Access Denied", user, lang)



    pat_rows = ""

    for email, data in USERS.items():

        if data.get('role') == 'Patient': 

            pat_rows += f"""

            <tr>

                <td>{data.get('name', email)}</td>

                <td>{email}</td>

                <td>

                    <form action='/admin/delete-user' method='POST' onsubmit="return confirm('Remove User {data.get('name')}?');">

                        <input type='hidden' name='email' value='{email}'>

                        <button style='background:#ff4444; color:white; border:none; padding:5px 10px; border-radius:5px; cursor:pointer;'>🗑️ Remove</button>

                    </form>

                </td>

            </tr>"""

    if not pat_rows: pat_rows = "<tr><td colspan='3' style='text-align:center;'>No Patients Found.</td></tr>"



    css = """<style>.admin-box { max-width: 900px; margin: 30px auto; padding: 20px; font-family: sans-serif; } table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0 5px 15px rgba(0,0,0,0.1); } th, td { padding: 15px; border-bottom: 1px solid #eee; text-align: left; } th { background: #007bff; color: white; } .back-btn { background: #555; color: white; text-decoration: none; padding: 10px 20px; border-radius: 5px; display: inline-block; margin-bottom: 20px; }</style>"""



    content = f"""

    {css}

    <div class="admin-box">

        <a href="/admin" class="back-btn">&larr; Back to Dashboard</a>

        <h1>👥 Registered Patients (Users)</h1>

        <table><thead><tr><th>Name</th><th>Email</th><th>Action</th></tr></thead><tbody>{pat_rows}</tbody></table>

    </div>

    """

    return f"<!DOCTYPE html><html><head><title>Manage Patients</title></head><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



def page_admin_dashboard(user, lang):

    print("DEBUG: New Admin Dashboard Loaded! ✅") # இது கண்டிப்பா வரணும்



    if user not in USERS or USERS[user].get('role') != 'Admin':

        return page_notfound("Access Denied", user, lang)



    rows_html = ""

    if 'USER_ACTIVITIES' in globals():

        for act in reversed(USER_ACTIVITIES[-10:]): 

            rows_html += f"<tr><td>{act['time']}</td><td>{act['email']}</td><td><span class='badge'>{act['category']}</span></td><td>{act['detail']}</td></tr>"



    css = """

    <style>

        .admin-container { max-width: 1000px; margin: 40px auto; padding: 20px; font-family: 'Segoe UI', sans-serif; text-align: center; }

        .grid-menu { display: flex; justify-content: center; gap: 30px; margin-bottom: 50px; flex-wrap: wrap; }

        .menu-card { 

            background: white; width: 250px; padding: 30px; border-radius: 15px; 

            box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-decoration: none; color: #333; transition: 0.3s; border: 1px solid #eee;

        }

        .menu-card:hover { transform: translateY(-10px); box-shadow: 0 15px 35px rgba(0,0,0,0.15); border-color: #007bff; }

        .icon { font-size: 3rem; margin-bottom: 15px; display: block; }

        .menu-title { font-size: 1.5rem; font-weight: bold; color: #2c3e50; }

        .act-box { text-align: left; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); }

        table { width: 100%; border-collapse: collapse; }

        th, td { padding: 12px; border-bottom: 1px solid #eee; }

        .badge { background: #6c757d; color: white; padding: 3px 8px; border-radius: 10px; font-size: 0.8rem; }

    </style>

    """



    content = f"""

    {css}

    <div class="admin-container">

        <h1 style="color:#2c3e50; margin-bottom: 10px;">🛡️ Super Admin Control Panel</h1>

        <div class="grid-menu">

            <a href="/admin/staff" class="menu-card" style="border-bottom: 5px solid #28a745;">

                <span class="icon">👨‍⚕️</span>

                <div class="menu-title">Manage Staff</div>

                <p>Doctors, Nurses, Pharmacists</p>

            </a>

            <a href="/admin/patients" class="menu-card" style="border-bottom: 5px solid #007bff;">

                <span class="icon">👥</span>

                <div class="menu-title">Manage Users</div>

                <p>View & Remove Patients</p>

            </a>

        </div>

        <div class="act-box">

            <h3 style="margin-top:0;">📊 Recent System Activities</h3>

            <table><thead><tr><th>Time</th><th>User</th><th>Type</th><th>Details</th></tr></thead><tbody>{rows_html}</tbody></table>

        </div>

        <br><a href="/logout"><button style="background:#dc3545; color:white; padding:10px 25px; border:none; border-radius:5px; cursor:pointer;">Logout</button></a>

    </div>

    """

    return f"<!DOCTYPE html><html><head><title>Admin Dashboard</title></head><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



def page_home(user, lang):

    # --- Language Specific Content ---

    if lang == 'ta':

        hero_title = "ஜென்மெட்எக்ஸ் (GenMedX)"

        hero_subtitle = "நவீன மருத்துவ வசதிகள் இப்போது உங்கள் விரல் நுனியில்.<br>மருந்துகள், மருத்துவர் ஆலோசனை மற்றும் பல சேவைகள்."

        btn_services = "எங்கள் சேவைகள்"

        btn_login = "உள்நுழையவும்"

        btn_about = "எங்களைப் பற்றி"

        why_title = "ஏன் ஜென்மெட்எக்ஸ்?"

        features = [

            {"icon": "💊", "title": "ஆன்லைன் மருந்தகம்", "desc": "வீட்டிலிருந்தே மருந்துகளை ஆர்டர் செய்யுங்கள். 10% தள்ளுபடி உண்டு."},

            {"icon": "👨‍⚕️", "title": "மருத்துவர் ஆலோசனை", "desc": "சிறந்த மருத்துவர்களிடம் வீடியோ கால் மூலம் ஆலோசனை பெறுங்கள்."},

            {"icon": "🚑", "title": "அவசர உதவி", "desc": "செவிலியர் மற்றும் அவசரகால உதவிகள் உங்கள் இருப்பிடத்திற்கே வரும்."},

            {"icon": "🤖", "title": "AI மருத்துவர்", "desc": "உங்கள் சந்தேகங்களுக்கு 24/7 AI உதவியாளர் பதில் அளிப்பார்."}

        ]

        footer_text = "© 2026 GenMedX. தமிழ்நாடு - அனைத்து உரிமைகளும் பாதுகாக்கப்பட்டவை."

    else:

        hero_title = "Welcome to GenMedX"

        hero_subtitle = "Advanced Healthcare at your fingertips.<br>Pharmacy, Consultation, and Diagnostics in one app."

        btn_services = "Explore Services"

        btn_login = "Login / Sign Up"

        btn_about = "About Us"

        why_title = "Why Choose GenMedX?"

        features = [

            {"icon": "💊", "title": "Online Pharmacy", "desc": "Order medicines from home with flat 10% discount."},

            {"icon": "👨‍⚕️", "title": "Expert Doctors", "desc": "Connect with top specialists via video consultation."},

            {"icon": "🚑", "title": "Emergency Care", "desc": "Nurse visits and emergency support at your doorstep."},

            {"icon": "🤖", "title": "AI Assistant", "desc": "Get instant health answers 24/7 from our AI bot."}

        ]

        footer_text = "© 2026 GenMedX. Tamil Nadu - All Rights Reserved."



    # --- Generate Feature Cards HTML ---

    cards_html = ""

    for f in features:

        cards_html += f"""

        <div class="feature-card">

            <div class="f-icon">{f['icon']}</div>

            <h3>{f['title']}</h3>

            <p>{f['desc']}</p>

        </div>

        """



    # --- Decide Button based on User Status ---

    if user:

        action_btn = f'<a href="/services" class="hero-btn primary-btn">{btn_services} &rarr;</a>'

    else:

        action_btn = f'<a href="/login" class="hero-btn primary-btn">{btn_login}</a>'



    # --- CSS Styles ---

    css = """

    <style>

        /* General Reset */

        body { margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; background-color: #f8f9fa; }

        

        /* Hero Section (Grand Look) */

        .hero-section {

            background: linear-gradient(135deg, #0061ff 0%, #60efff 100%);

            color: white;

            padding: 80px 20px 100px;

            text-align: center;

            border-bottom-left-radius: 50% 20px;

            border-bottom-right-radius: 50% 20px;

            position: relative;

            box-shadow: 0 10px 30px rgba(0,97,255,0.2);

            margin-bottom: 40px; /* Space between hero and content */

        }

        

        .hero-title { font-size: 3.5rem; margin-bottom: 10px; font-weight: 800; text-shadow: 0 2px 10px rgba(0,0,0,0.1); }

        .hero-subtitle { font-size: 1.3rem; margin-bottom: 40px; line-height: 1.6; opacity: 0.95; }

        

        /* Buttons */

        .btn-container { display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; }

        .hero-btn {

            padding: 15px 35px; border-radius: 30px; text-decoration: none; font-weight: bold; font-size: 1.1rem; transition: transform 0.3s, box-shadow 0.3s;

        }

        .primary-btn { background-color: #ffffff; color: #0061ff; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }

        .secondary-btn { background-color: rgba(255,255,255,0.2); color: white; border: 2px solid rgba(255,255,255,0.5); }

        

        .hero-btn:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,0.3); }

        .primary-btn:hover { background-color: #f0f8ff; }

        .secondary-btn:hover { background-color: rgba(255,255,255,0.4); }



        /* Features Section */

        /* I removed the negative margin so boxes sit below the title */

        .features-container {

            max-width: 1100px; 

            margin: 0 auto 40px; /* Changed: 0 margin top */

            padding: 0 20px;

            display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 30px;

        }

        

        .feature-card {

            background: white; padding: 30px; border-radius: 20px;

            text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.08);

            transition: transform 0.3s;

            border: 1px solid #eee; /* Added light border for clarity */

        }

        .feature-card:hover { transform: translateY(-10px); border-color: #0061ff; }

        .f-icon { font-size: 4rem; margin-bottom: 15px; }

        .feature-card h3 { color: #333; margin-bottom: 10px; }

        .feature-card p { color: #666; line-height: 1.5; }



        /* Language Toggle (Floating) */

        .lang-float {

            position: absolute; top: 20px; right: 20px;

            background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px;

        }

        .lang-float a { color: white; text-decoration: none; font-weight: bold; margin: 0 5px; font-size: 0.9rem; }

        .lang-float span { color: rgba(255,255,255,0.6); }



        /* Footer */

        .footer { text-align: center; padding: 30px; color: #888; font-size: 0.9rem; margin-top: 50px; border-top: 1px solid #eee; }

        

        @media (max-width: 600px) {

            .hero-title { font-size: 2.5rem; }

            .features-container { margin-top: 20px; }

        }

    </style>

    """



    content = f"""

    {css}

    

    <div class="hero-section">

        <div class="lang-float">

            <a href="/set-language?lang=en&ref=/home">English</a> <span>|</span> <a href="/set-language?lang=ta&ref=/home">தமிழ்</a>

        </div>

        

        <h1 class="hero-title">{hero_title}</h1>

        <p class="hero-subtitle">{hero_subtitle}</p>

        

        <div class="btn-container">

            {action_btn}

            <a href="/about" class="hero-btn secondary-btn">{btn_about}</a>

        </div>

    </div>



    <div style="text-align: center; margin-bottom: 30px;">

        <h2 style="color: #2c3e50; font-size: 2rem;">{why_title}</h2>

    </div>

    

    <div class="features-container">

        {cards_html}

    </div>



    <div class="footer">

        {footer_text}

    </div>

    """

    

    html = f"<!DOCTYPE html><html><head><title>{hero_title}</title></head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



def page_about(user, lang):

    # --- Content Based on Language ---

    if lang == 'ta':

        header_title = "எங்களைப் பற்றி"

        header_sub = "சுகாதார சேவையில் ஒரு புதிய புரட்சி."

        

        mission_title = "எங்கள் நோக்கம் (Mission)"

        mission_desc = "அனைவருக்கும் தரமான மருத்துவ சேவையை எளிதாகவும், மலிவாகவும் கொண்டு சேர்ப்பதே எங்கள் குறிக்கோள்."

        

        vision_title = "எங்கள் பார்வை (Vision)"

        vision_desc = "தொழில்நுட்பத்தின் மூலம் நோயாளிகள், மருத்துவர்கள் மற்றும் மருந்தகங்களை ஒரே தளத்தில் இணைத்தல்."

        

        story_title = "எங்கள் கதை"

        story_p1 = "ஜென்மெட்எக்ஸ் (GenMedX) என்பது சாதாரண மக்களுக்கான மருத்துவ செயலி. இது வெறுமனே மருந்துகளை ஆர்டர் செய்யும் தளம் மட்டுமல்ல."

        story_p2 = "நாங்கள் உள்ளூர் மருந்தகங்கள் மற்றும் மருத்துவர்களை ஆதரிக்கிறோம். எங்கள் தளத்தின் மூலம் நீங்கள் வீட்டிலிருந்தே மருத்துவ ஆலோசனைகளையும், மருந்துகளையும் பெற முடியும்."

        

        stats = [

            {"num": "10k+", "label": "பயனர்கள்"},

            {"num": "500+", "label": "மருத்துவர்கள்"},

            {"num": "24/7", "label": "ஆதரவு"}

        ]

        

        btn_contact = "தொடர்புக்கு"

    else:

        header_title = "About GenMedX"

        header_sub = "Revolutionizing Healthcare Access for Everyone."

        

        mission_title = "Our Mission"

        mission_desc = "To make quality healthcare accessible, affordable, and convenient for every individual using technology."

        

        vision_title = "Our Vision"

        vision_desc = "Creating a seamless ecosystem that connects patients, doctors, and local pharmacies efficiently."

        

        story_title = "Who We Are"

        story_p1 = "GenMedX is not just an app; it is a movement to bridge the gap in local healthcare. We empower local pharmacies and provide patients with digital tools."

        story_p2 = "From ordering medicines to booking lab tests and doctor consultations, we bring the hospital experience to your home."

        

        stats = [

            {"num": "10k+", "label": "Happy Users"},

            {"num": "500+", "label": "Doctors"},

            {"num": "24/7", "label": "Support"}

        ]

        

        btn_contact = "Contact Us"



    # --- CSS Styles ---

    css = """

    <style>

        body { font-family: 'Segoe UI', sans-serif; background: #f9f9f9; margin: 0; padding: 0; }

        

        /* Header Section */

        .about-header {

            background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%);

            color: white;

            padding: 80px 20px;

            text-align: center;

            border-bottom-left-radius: 50% 20px;

            border-bottom-right-radius: 50% 20px;

            box-shadow: 0 10px 20px rgba(0,0,0,0.1);

        }

        .about-header h1 { margin: 0; font-size: 3rem; font-weight: 800; }

        .about-header p { font-size: 1.2rem; margin-top: 10px; opacity: 0.9; }



        /* Container */

        .about-container { max-width: 1000px; margin: 0 auto; padding: 40px 20px; }



        /* Mission & Vision Cards */

        .mv-grid {

            display: flex; gap: 30px; flex-wrap: wrap; margin-top: -60px; justify-content: center;

        }

        .mv-card {

            background: white; padding: 30px; border-radius: 15px;

            flex: 1; min-width: 300px;

            box-shadow: 0 10px 30px rgba(0,0,0,0.1);

            text-align: center;

            transition: transform 0.3s;

        }

        .mv-card:hover { transform: translateY(-10px); }

        .mv-icon { font-size: 3rem; margin-bottom: 15px; display: block; }

        .mv-title { color: #2c3e50; font-size: 1.5rem; margin-bottom: 15px; font-weight: bold; }

        .mv-desc { color: #666; line-height: 1.6; }



        /* Story Section */

        .story-section { margin-top: 60px; display: flex; gap: 40px; align-items: center; flex-wrap: wrap; }

        .story-text { flex: 2; min-width: 300px; }

        .story-text h2 { color: #007bff; font-size: 2rem; margin-bottom: 20px; }

        .story-text p { color: #555; line-height: 1.8; font-size: 1.1rem; margin-bottom: 15px; text-align: justify; }

        

        .story-img { 

            flex: 1; min-width: 250px; height: 300px; 

            background: linear-gradient(45deg, #eee, #ddd); 

            border-radius: 20px; display: flex; align-items: center; justify-content: center; font-size: 5rem; color: #aaa;

            box-shadow: 0 5px 15px rgba(0,0,0,0.1);

        }



        /* Stats Section */

        .stats-row {

            display: flex; justify-content: space-around; margin-top: 60px;

            background: white; padding: 40px; border-radius: 20px;

            box-shadow: 0 5px 20px rgba(0,0,0,0.05); flex-wrap: wrap; gap: 20px;

        }

        .stat-item { text-align: center; }

        .stat-num { font-size: 2.5rem; font-weight: bold; color: #007bff; display: block; }

        .stat-label { color: #777; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px; }



        /* CTA */

        .about-cta { text-align: center; margin-top: 60px; }

        .cta-btn {

            background-color: #2c3e50; color: white; padding: 15px 40px; border-radius: 30px;

            text-decoration: none; font-size: 1.2rem; transition: background 0.3s;

        }

        .cta-btn:hover { background-color: #1a252f; }

    </style>

    """



    # Generate Stats HTML

    stats_html = ""

    for s in stats:

        stats_html += f"""

        <div class="stat-item">

            <span class="stat-num">{s['num']}</span>

            <span class="stat-label">{s['label']}</span>

        </div>

        """



    content = f"""

    {css}

    <div class="about-header">

        <h1>{header_title}</h1>

        <p>{header_sub}</p>

    </div>



    <div class="about-container">

        <div class="mv-grid">

            <div class="mv-card">

                <span class="mv-icon">🎯</span>

                <div class="mv-title">{mission_title}</div>

                <div class="mv-desc">{mission_desc}</div>

            </div>

            <div class="mv-card">

                <span class="mv-icon">👁️</span>

                <div class="mv-title">{vision_title}</div>

                <div class="mv-desc">{vision_desc}</div>

            </div>

        </div>



        <div class="story-section">

            <div class="story-img">🏥</div>

            <div class="story-text">

                <h2>{story_title}</h2>

                <p>{story_p1}</p>

                <p>{story_p2}</p>

            </div>

        </div>



        <div class="stats-row">

            {stats_html}

        </div>



        <div class="about-cta">

            <a href="mailto:support@genmedx.com" class="cta-btn">{btn_contact}</a>

        </div>

    </div>

    """

    

    html = f"<!DOCTYPE html><html><head><title>{header_title}</title></head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



def page_login(environ, start_response, user, lang):

    msg = ""

    if environ["REQUEST_METHOD"] == "POST":

        length = int(environ.get("CONTENT_LENGTH", 0))

        body = environ['wsgi.input'].read(length)

        data = parse_qs(body.decode('utf-8'))

        email = data.get("email", [""])[0].strip()

        password = data.get("password", [""])[0]

        

        # --- LOGIN LOGIC (UPDATED) ---

        # பழைய USERS[email] == password முறையை மாற்றவும்

        if email in USERS and USERS[email]['password'] == password:

            session_id = uuid.uuid4().hex

            SESSIONS[session_id] = email

            

            # ரோல் (Role) கண்டுபிடி

            user_role = USERS[email].get('role', 'Patient') 

            

            # Redirect Logic

            if user_role == 'Admin':

                redirect_url = "/admin"

            elif user_role in ['Doctor', 'Nurse', 'Pharmacist', 'LabTech', 'Counsellor']:

                # இவர்களுக்கு Professional Dashboard

                redirect_url = f"/professional-dashboard?role={user_role}"

            else:

                # சாதாரண Users (Patients)

                redirect_url = "/services"



            headers = [("Location", redirect_url), ("Set-Cookie", make_set_cookie_header("session_id", session_id))]

            start_response("302 Found", headers)

            return [b'']



    # --- MODERN STYLES ---

    css = """

    <style>

        body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; }

        .auth-container {

            display: flex; justify-content: center; align-items: center;

            min-height: 80vh;

            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

            padding: 20px;

        }

        .auth-card {

            background: rgba(255, 255, 255, 0.95);

            padding: 40px; border-radius: 20px;

            box-shadow: 0 10px 25px rgba(0,0,0,0.2);

            width: 100%; max-width: 400px;

            text-align: center;

            animation: fadeIn 0.8s ease-in-out;

        }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }

        

        h2 { color: #333; margin-bottom: 20px; font-weight: 700; }

        .input-group { margin-bottom: 20px; text-align: left; }

        .input-group label { display: block; margin-bottom: 8px; color: #555; font-size: 14px; font-weight: 600; }

        

        input[type="email"], input[type="password"] {

            width: 100%; padding: 12px 15px;

            border: 2px solid #e1e1e1; border-radius: 10px;

            font-size: 16px; transition: 0.3s;

            box-sizing: border-box; /* Fix padding issue */

        }

        input:focus { border-color: #764ba2; outline: none; box-shadow: 0 0 8px rgba(118, 75, 162, 0.2); }

        

        .login-btn {

            width: 100%; padding: 14px;

            background: linear-gradient(to right, #667eea, #764ba2);

            color: white; border: none; border-radius: 10px;

            font-size: 18px; font-weight: bold; cursor: pointer;

            transition: transform 0.2s;

        }

        .login-btn:hover { transform: scale(1.02); opacity: 0.9; }

        

        .switch-link { margin-top: 20px; font-size: 14px; color: #666; }

        .switch-link a { color: #764ba2; text-decoration: none; font-weight: bold; }

        .switch-link a:hover { text-decoration: underline; }

        

        .error-msg { background: #ffebee; color: #c62828; padding: 10px; border-radius: 8px; margin-bottom: 15px; font-size: 14px; }

        

        /* Eye Icon Fix */

        .pw-container { position: relative; width: 100%; }

        .pw-eye { position: absolute; right: 15px; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; color: #666; }

    </style>

    """



    eye_hidden_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7.028 7.028 0 0 0-2.79.588l.77.771A5.94 5.94 0 0 1 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.134 13.134 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755-.165.165-.337.328-.517.486l.708.709z"/><path d="M11.297 9.176a3.5 3.5 0 0 0-4.474-4.474l.823.823a2.5 2.5 0 0 1 2.829 2.829l.822.822zm-2.943 1.288.822.822.084.083a3.5 3.5 0 0 1-4.474-4.474l.083.084.823.823a2.5 2.5 0 0 0 2.829 2.829z"/><path d="M3.35 5.47c-.18.16-.353.322-.518.487A13.134 13.134 0 0 0 1.172 8l.195.288c.335.48.83 1.12 1.465 1.755C4.121 11.332 5.881 12.5 8 12.5c.716 0 1.39-.133 2.02-.36l.77.772A7.029 7.029 0 0 1 8 13.5C3 13.5 0 8 0 8s.939-1.721 2.641-3.238l.708.709zm10.296 8.884-12-12 .708-.708 12 12-.708.708z"/></svg>'''



    content = f'''

    {css}

    <div class="auth-container">

        <div class="auth-card">

            <div style="font-size: 40px; margin-bottom: 10px;">🔐</div>

            <h2>{LANG[lang]['login_title']}</h2>

            {msg}

            <form method='POST'>

                <div class="input-group">

                    <label>{LANG[lang]['email_placeholder']}</label>

                    <input type='email' name='email' placeholder="example@mail.com" required>

                </div>

                

                <div class="input-group">

                    <label>{LANG[lang]['password_placeholder']}</label>

                    <div class="pw-container">

                        <input type="password" id="login_pw" name="password" placeholder="••••••••" required>

                        <button type="button" class="pw-eye" onclick="toggleEye('login_pw', this)">{eye_hidden_svg}</button>

                    </div>

                </div>



                <button type='submit' class="login-btn">{LANG[lang]['login']}</button>

            </form>



            <div class="switch-link">

                New to GenMedX? <a href='/signup'>{LANG[lang]['signup_button_text']}</a>

            </div>

        </div>

    </div>

    '''

    

    html = f"<!DOCTYPE html><html><head><title>{LANG[lang]['login_title']}</title>{pw_eye_head_html()}</head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



def page_signup(environ, start_response, user, lang):

    msg = ""

    if environ["REQUEST_METHOD"] == "POST":

        length = int(environ.get("CONTENT_LENGTH", 0))

        body = environ['wsgi.input'].read(length)

        data = parse_qs(body.decode('utf-8'))

        email = data.get("email", [""])[0].strip()

        password = data.get("password", [""])[0]

        confirm = data.get("confirm", [""])[0]

        

        if not all([email, password, confirm]): msg = f"<div class='error-msg'>{LANG[lang]['all_fields_required']}</div>"

        elif not re.match(r'^[^@]+@[^@]+\.[^@]+$', email): msg = f"<div class='error-msg'>{LANG[lang]['enter_valid_email']}</div>"

        elif password != confirm: msg = f"<div class='error-msg'>{LANG[lang]['passwords_no_match']}</div>"

        elif not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', password): msg = f"<div class='error-msg'>Password must contain A-Z, a-z, 0-9 & 8+ chars.</div>"

        elif email in USERS: msg = f"<div class='error-msg'>{LANG[lang]['email_registered']}</div>"

        else:

            # புதிய பயனர்களை "Patient" ஆக சேர்க்கிறோம்

            USERS[email] = {

                "password": password, 

                "role": "Patient", 

                "name": email.split('@')[0]

            }

            save_users(USERS) # JSON-ல் சேவ் பண்றோம் (முக்கியம்!)



            start_response("302 Found", [("Location", "/login")])

            return [b'']



    # --- MODERN STYLES (Reuse for consistency) ---

    css = """

    <style>

        body { font-family: 'Segoe UI', sans-serif; background: #f0f2f5; }

        .auth-container {

            display: flex; justify-content: center; align-items: center;

            min-height: 90vh;

            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); /* Different Gradient for Signup */

            padding: 20px;

        }

        .auth-card {

            background: rgba(255, 255, 255, 0.95);

            padding: 40px; border-radius: 20px;

            box-shadow: 0 10px 25px rgba(0,0,0,0.2);

            width: 100%; max-width: 420px;

            text-align: center;

            animation: slideUp 0.8s ease-in-out;

        }

        @keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

        

        h2 { color: #333; margin-bottom: 10px; font-weight: 700; }

        .input-group { margin-bottom: 15px; text-align: left; }

        .input-group label { display: block; margin-bottom: 5px; color: #555; font-size: 14px; font-weight: 600; }

        

        input {

            width: 100%; padding: 12px 15px;

            border: 2px solid #e1e1e1; border-radius: 10px;

            font-size: 16px; transition: 0.3s;

            box-sizing: border-box;

        }

        input:focus { border-color: #11998e; outline: none; box-shadow: 0 0 8px rgba(17, 153, 142, 0.2); }

        

        .signup-btn {

            width: 100%; padding: 14px;

            background: linear-gradient(to right, #11998e, #38ef7d);

            color: white; border: none; border-radius: 10px;

            font-size: 18px; font-weight: bold; cursor: pointer;

            transition: transform 0.2s; margin-top: 10px;

        }

        .signup-btn:hover { transform: scale(1.02); opacity: 0.9; }

        

        .switch-link { margin-top: 20px; font-size: 14px; color: #666; }

        .switch-link a { color: #11998e; text-decoration: none; font-weight: bold; }

        

        .error-msg { background: #ffebee; color: #c62828; padding: 10px; border-radius: 8px; margin-bottom: 15px; font-size: 13px; }

        

        .pw-container { position: relative; width: 100%; }

        .pw-eye { position: absolute; right: 15px; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; color: #666; }

    </style>

    """



    eye_hidden_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M13.359 11.238C15.06 9.72 16 8 16 8s-3-5.5-8-5.5a7.028 7.028 0 0 0-2.79.588l.77.771A5.94 5.94 0 0 1 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.134 13.134 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755-.165.165-.337.328-.517.486l.708.709z"/><path d="M11.297 9.176a3.5 3.5 0 0 0-4.474-4.474l.823.823a2.5 2.5 0 0 1 2.829 2.829l.822.822zm-2.943 1.288.822.822.084.083a3.5 3.5 0 0 1-4.474-4.474l.083.084.823.823a2.5 2.5 0 0 0 2.829 2.829z"/><path d="M3.35 5.47c-.18.16-.353.322-.518.487A13.134 13.134 0 0 0 1.172 8l.195.288c.335.48.83 1.12 1.465 1.755C4.121 11.332 5.881 12.5 8 12.5c.716 0 1.39-.133 2.02-.36l.77.772A7.029 7.029 0 0 1 8 13.5C3 13.5 0 8 0 8s.939-1.721 2.641-3.238l.708.709zm10.296 8.884-12-12 .708-.708 12 12-.708.708z"/></svg>'''



    content = f'''

    {css}

    <div class="auth-container">

        <div class="auth-card">

            <div style="font-size: 40px; margin-bottom: 5px;">📝</div>

            <h2>{LANG[lang]['signup_title']}</h2>

            <p style="color:#666; font-size:14px; margin-bottom:20px;">Create your GenMedX account</p>

            {msg}

            <form method='POST'>

                <div class="input-group">

                    <label>{LANG[lang]['email_placeholder']}</label>

                    <input type='email' name='email' placeholder="example@mail.com" required>

                </div>

                

                <div class="input-group">

                    <label>{LANG[lang]['password_placeholder']}</label>

                    <div class="pw-container">

                        <input type="password" id="signup_pw" name="password" placeholder="Min 8 chars, A-Z, 0-9" required>

                        <button type="button" class="pw-eye" onclick="toggleEye('signup_pw', this)">{eye_hidden_svg}</button>

                    </div>

                </div>



                <div class="input-group">

                    <label>{LANG[lang]['confirm_password_placeholder']}</label>

                    <div class="pw-container">

                        <input type="password" id="signup_conf" name="confirm" placeholder="Repeat password" required>

                        <button type="button" class="pw-eye" onclick="toggleEye('signup_conf', this)">{eye_hidden_svg}</button>

                    </div>

                </div>



                <button type='submit' class="signup-btn">{LANG[lang]['signup_button_text']}</button>

            </form>



            <div class="switch-link">

                Already have an account? <a href='/login'>{LANG[lang]['already_registered']}</a>

            </div>

        </div>

    </div>

    '''

    

    html = f"<!DOCTYPE html><html><head><title>{LANG[lang]['signup_title']}</title>{pw_eye_head_html()}</head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



def page_services(user, lang):

    if not user:

        return page_login(None, None, user, lang)



    # --- மொழி மாற்றங்கள் (Translations) ---

    t_title = "எங்கள் சேவைகள்" if lang == 'ta' else "Our Services"

    

    # 1. Top Box

    t_drugs = "ஆன்லைன் மருந்தகம்" if lang == 'ta' else "Online Drugs Store"

    t_drugs_desc = "எல்லாவிதமான மருந்துகளையும் இங்கே ஆர்டர் செய்யலாம் (10% தள்ளுபடி)." if lang == 'ta' else "Order all medicines here with discounts."



    # 2. Middle 5 Boxes

    t_pharma = "மருந்தாளர் ஆலோசனை" if lang == 'ta' else "Pharmacist Intervention"

    t_pharma_desc = "மருந்து சந்தேகங்கள்" if lang == 'ta' else "Drug queries"



    t_doc = "மருத்துவர்" if lang == 'ta' else "Doctor Consult"

    t_doc_desc = "சிகிச்சை பெற" if lang == 'ta' else "Get treated"

    

    t_nurse = "செவிலியர்" if lang == 'ta' else "Nurse Service"

    t_nurse_desc = "வீட்டுப் பராமரிப்பு" if lang == 'ta' else "Home care"

    

    t_lab = "லேப் டெஸ்ட்" if lang == 'ta' else "Lab Tests"

    t_lab_desc = "ரத்த பரிசோதனை" if lang == 'ta' else "Diagnostics"

    

    t_organ = "உறுப்புகள்" if lang == 'ta' else "Organ Systems"

    t_organ_desc = "உடல் அறிவு" if lang == 'ta' else "Body info"



    # 3. Bottom Box

    t_ai = "AI மருத்துவ உதவியாளர்" if lang == 'ta' else "AI Health Assistant"

    t_ai_desc = "உங்கள் சந்தேகங்களை AI-இடம் கேட்டுத் தெரிந்துகொள்ளுங்கள்." if lang == 'ta' else "Chat with AI for instant health answers."



    html = f"""

    <!DOCTYPE html>

    <html>

    <head>

        <title>{t_title}</title>

        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <style>

            body {{ font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; background: #f4f6f9; }}

            .header {{ background: #007bff; color: white; padding: 20px; text-align: center; }}

            .container {{ padding: 20px; max-width: 1100px; margin: auto; }}

            

            /* GRID LAYOUT */

            .service-grid {{ 

                display: grid; 

                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); 

                gap: 20px; 

            }}



            /* CARD STYLES */

            .card {{ 

                background: white; 

                padding: 20px; 

                border-radius: 12px; 

                text-align: center; 

                text-decoration: none; 

                color: #333; 

                box-shadow: 0 4px 6px rgba(0,0,0,0.05); 

                transition: 0.3s;

                display: flex;

                flex-direction: column;

                align-items: center;

                justify-content: center;

            }}

            .card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0,0,0,0.1); }}

            

            .card h3 {{ margin: 10px 0 5px; font-size: 1.1em; color: #007bff; }}

            .card p {{ font-size: 0.9em; color: #666; margin: 0; }}

            .icon {{ font-size: 40px; margin-bottom: 10px; }}



            /* --- BIG BOX STYLES (Full Width) --- */

            .big-box {{

                grid-column: 1 / -1; 

                display: flex;

                flex-direction: row; 

                align-items: center;

                justify-content: flex-start;

                text-align: left;

                padding: 30px;

            }}

            .big-box .icon {{ font-size: 60px; margin-right: 30px; margin-bottom: 0; }}

            .big-box h3 {{ font-size: 1.8em; margin: 0; color: white !important; }}

            .big-box p {{ font-size: 1.1em; color: #f1f1f1 !important; margin-top: 5px; }}



            .drugs-style {{ 

                background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 

                color: white !important;

            }}

            

            .ai-style {{ 

                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 

                color: white !important;

            }}



            @media (max-width: 600px) {{

                .big-box {{ flex-direction: column; text-align: center; }}

                .big-box .icon {{ margin-right: 0; margin-bottom: 15px; }}

            }}

        </style>

    </head>

    <body>

        {nav_bar(user, lang)}

        <div class="header">

            <h1>{t_title}</h1>

        </div>



        <div class="container">

            <div class="service-grid">

                

                <a href="/drugs-store" class="card big-box drugs-style">

                    <span class="icon">💊</span>

                    <div>

                        <h3>{t_drugs}</h3>

                        <p>{t_drugs_desc}</p>

                    </div>

                </a>



                <a href="/pharmacy-consult" class="card">

                    <span class="icon">🧑‍🔬</span>

                    <h3>{t_pharma}</h3>

                    <p>{t_pharma_desc}</p>

                </a>



                <a href="/doctor-consult" class="card">

                    <span class="icon">👨‍⚕️</span>

                    <h3>{t_doc}</h3>

                    <p>{t_doc_desc}</p>

                </a>



                <a href="/nurse-services" class="card">

                    <span class="icon">👩‍⚕️</span>

                    <h3>{t_nurse}</h3>

                    <p>{t_nurse_desc}</p>

                </a>



                <a href="/lab-details" class="card">

                    <span class="icon">🔬</span>

                    <h3>{t_lab}</h3>

                    <p>{t_lab_desc}</p>

                </a>



                <a href="/organ-system-service" class="card">

                    <span class="icon">🫀</span>

                    <h3>{t_organ}</h3>

                    <p>{t_organ_desc}</p>

                </a>



                <a href="/ai-chat" class="card big-box ai-style">

                    <span class="icon">🤖</span>

                    <div>

                        <h3>{t_ai}</h3>

                        <p>{t_ai_desc}</p>

                    </div>

                </a>



            </div>

        </div>

    </body>

    </html>

    """

    return html



def page_nurse_services(user, lang):

    services = [

        {"key": "home-visit", "title": LANG[lang]['call_nurse_home_visit'], "icon": "🏠", "desc": "Professional care at your home"},

        {"key": "vitals-checkup", "title": LANG[lang]['vitals_checkup'], "icon": "🩺", "desc": "BP, Sugar & Pulse monitoring"},

        {"key": "post-hospitalization", "title": LANG[lang]['post_hospitalization'], "icon": "🛏️", "desc": "Wound dressing & recovery care"},

        {"key": "video-call", "title": LANG[lang]['video_call'], "icon": "📹", "desc": "Instant nurse consultation"}

    ]



    css = """

    <style>

        .nurse-header { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 60px 20px; text-align: center; color: white; border-radius: 0 0 50px 0; }

        .ns-grid { display: flex; flex-wrap: wrap; justify-content: center; gap: 30px; margin: 40px auto; max-width: 1000px; padding: 20px; }

        .ns-card { background: white; width: 220px; padding: 30px; border-radius: 20px; text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.05); text-decoration: none; color: #333; transition: 0.3s; border-bottom: 5px solid transparent; }

        .ns-card:hover { transform: translateY(-10px); border-bottom-color: #f5576c; box-shadow: 0 15px 35px rgba(0,0,0,0.15); }

        .ns-icon { font-size: 3.5rem; margin-bottom: 20px; display: block; }

        .ns-card h3 { font-size: 1.1rem; margin-bottom: 10px; }

        .ns-card p { font-size: 0.9rem; color: #777; }

    </style>

    """

    

    cards_html = ""

    for s in services:

        link = "/nurse-video-call" if s['key'] == 'video-call' else f"/nurse-service/{s['key']}"

        cards_html += f"""

        <a href="{link}" class="ns-card">

            <span class="ns-icon">{s['icon']}</span>

            <h3>{s['title']}</h3>

            <p>{s['desc']}</p>

        </a>

        """



    content = f"""

    {css}

    <div class="nurse-header">

        <h1>{LANG[lang]['nurse_services_title']}</h1>

        <p>Caring Hands, Right at Your Doorstep</p>

    </div>

    

    <div class="ns-grid">

        {cards_html}

    </div>

    

    <div style="text-align:center; margin-bottom:30px;">

        <a href="/services"><button style="padding:10px 20px;">{LANG[lang]['back_to_services']}</button></a>

    </div>

    """

    html = f"<!DOCTYPE html><html><head><title>Nurse Services</title></head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



def page_nurse_service_detail(user, lang, service_name, description):

    css = """

    <style>

        .detail-container { max-width: 800px; margin: 40px auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }

        .detail-header { background: #2c3e50; color: white; padding: 40px; text-align: center; }

        .detail-body { padding: 40px; }

        .price-box { background: #f8f9fa; border-left: 5px solid #28a745; padding: 20px; margin: 20px 0; }

        .book-btn { width: 100%; padding: 15px; background: #28a745; color: white; border: none; font-size: 1.1rem; font-weight: bold; border-radius: 10px; cursor: pointer; }

        .book-btn:hover { background: #218838; }

    </style>

    """

    

    content = f"""

    {css}

    <div class="detail-container">

        <div class="detail-header">

            <h1>{service_name}</h1>

        </div>

        <div class="detail-body">

            <p style="font-size:1.2rem; color:#555;">{description}</p>

            

            <div class="price-box">

                <h3 style="margin:0 0 10px 0;">Service Details</h3>

                <ul style="margin:0; padding-left:20px; color:#666;">

                    <li>Expert Qualified Nurse</li>

                    <li>Safety Protocols Followed</li>

                    <li>Available 9 AM - 9 PM</li>

                </ul>

            </div>

            

            <button class="book-btn" onclick="alert('Your request has been noted. Our team will call you shortly.')">Request This Service</button>

        </div>

        <div style="text-align:center; padding-bottom:20px;">

             <a href="/nurse-services" style="color:#666;">Cancel</a>

        </div>

    </div>

    """

    html = f"<!DOCTYPE html><html><head><title>{service_name}</title></head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



def page_video_consult(user, lang, environ):

    from urllib.parse import parse_qs

    qs = parse_qs(environ.get('QUERY_STRING', ''))

    target = qs.get('target', ['Medical Shop'])[0]



    content = f"""

    <div style="max-width:900px; margin:20px auto; padding:20px; font-family:sans-serif; text-align:center;">

        <div style="background:#000; height:450px; border-radius:30px; display:flex; flex-direction:column; align-items:center; justify-content:center; color:white; box-shadow:0 20px 50px rgba(0,0,0,0.3);">

            <div style="font-size:5rem; margin-bottom:20px;">🏪</div>

            <h2>Calling {target}...</h2>

            <p>Pharmacist will connect shortly</p>

            <br><br>

            <a href="/pharmacy-consult"><button style="background:red; color:white; border:none; padding:15px 40px; border-radius:30px; cursor:pointer;">End Call</button></a>

        </div>

    </div>

    """

    return f"<!DOCTYPE html><html><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



def page_lab_details(user, lang):

    css = """<style> .lab-header { background: linear-gradient(to right, #43e97b 0%, #38f9d7 100%); padding: 60px; text-align: center; color: #2c3e50; border-radius: 0 0 30px 30px; } .lab-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; max-width: 1000px; margin: 40px auto; padding: 20px; } .test-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.05); border-left: 5px solid #43e97b; transition: 0.3s; } .test-card:hover { transform: scale(1.02); box-shadow: 0 15px 30px rgba(0,0,0,0.1); } .price { font-size: 1.5rem; font-weight: bold; color: #2c3e50; margin: 10px 0; } .book-test-btn { background: #2c3e50; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; width: 100%; margin-top: 10px; text-decoration:none; display:inline-block; text-align:center; } </style>"""

    

    tests = [

        {"name": "Complete Blood Count (CBC)", "price": "₹350", "desc": "Check infection, anemia & more"},

        {"name": "Thyroid Profile (T3, T4, TSH)", "price": "₹550", "desc": "Thyroid function test"},

        {"name": "Diabetes Screening (HbA1c)", "price": "₹450", "desc": "3 months average sugar level"},

        {"name": "Full Body Checkup", "price": "₹1200", "desc": "Liver, Kidney, Lipid & Blood"}

    ]

    

    html_cards = ""

    for t in tests:

        # CHANGED BUTTON LINK

        html_cards += f"""

        <div class="test-card">

            <h3>{t['name']}</h3>

            <p style="color:#666;">{t['desc']}</p>

            <div class="price">{t['price']}</div>

            <a href="/api/log-action?cat=Booking&item=Lab+Test:+{t['name']}" class="book-test-btn">Book Now</a>

        </div>

        """



    content = f"""{css} <div class="lab-header"> <h1>🔬 Diagnostic Lab Services</h1> <p>Accurate Reports | Home Sample Collection</p> </div> <div class="lab-grid"> {html_cards} </div> <div style="text-align:center; margin-bottom:40px;"> <a href="/services"><button style="padding:10px 20px;">{LANG[lang]['back_to_services']}</button></a> </div>"""

    html = f"<!DOCTYPE html><html><head><title>Lab Tests</title></head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



def page_doctor_consult(user, lang):

    # Doctors Data (Tags சேர்த்திருக்கேன் தேடுவதற்காக)

    doctors = [

        {"id": "d1", "name": "Dr. Sarah", "spec": "Cardiologist", "exp": "10 Yrs", "img": "https://placehold.co/100?text=S", "tags": "heart cardio chest pain"},

        {"id": "d2", "name": "Dr. Rajesh", "spec": "General Physician", "exp": "8 Yrs", "img": "https://placehold.co/100?text=R", "tags": "fever cold flu general"},

        {"id": "d3", "name": "Dr. Anitha", "spec": "Dermatologist", "exp": "12 Yrs", "img": "https://placehold.co/100?text=A", "tags": "skin hair face acne"},

        {"id": "d4", "name": "Dr. John", "spec": "Pediatrician", "exp": "5 Yrs", "img": "https://placehold.co/100?text=J", "tags": "child baby kids"},

    ]

    

    doc_html = ""

    datalist_opts = ""

    

    # Datalist Options உருவாக்குதல் (Name & Spec)

    for d in doctors:

        datalist_opts += f'<option value="{d["name"]}">'

        datalist_opts += f'<option value="{d["spec"]}">'



    # Doctor Cards Generation

    for d in doctors:

        doc_html += f"""

        <div class="doc-card" data-search="{d['name']} {d['spec']} {d['tags']}">

            <img src="{d['img']}" class="doc-img">

            <h3>{d['name']}</h3>

            <p style="color:#007bff; font-weight:bold;">{d['spec']}</p>

            <p style="color:#666; font-size:0.9rem;">{d['exp']} Experience</p>

            <a href="/doctor-profile?id={d['id']}"><button class="doc-btn">View Profile</button></a>

        </div>

        """



    script = """

    <script>

        function filterDocs() {

            let input = document.getElementById('docSearch').value.toLowerCase();

            let cards = document.getElementsByClassName('doc-card');

            

            for (let i = 0; i < cards.length; i++) {

                // data-search attribute-ல் இருக்கும் வார்த்தைகளை வைத்து தேடுகிறது

                let searchData = cards[i].getAttribute('data-search').toLowerCase();

                

                if (searchData.includes(input)) {

                    cards[i].style.display = "block";

                } else {

                    cards[i].style.display = "none";

                }

            }

        }

    </script>

    """



    css = """<style>

        .doc-header { background:linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%); padding:60px; color:white; text-align:center; border-radius:0 0 30px 30px; }

        .search-area { max-width:600px; margin:-25px auto 30px; padding:0 20px; position:relative; }

        .search-inp { width:100%; padding:15px 25px; border-radius:50px; border:none; box-shadow:0 10px 20px rgba(0,0,0,0.15); outline:none; font-size:16px; }

        .doc-grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:25px; max-width:1000px; margin:0 auto; padding:20px; }

        .doc-card { background:white; padding:25px; border-radius:15px; text-align:center; box-shadow:0 5px 15px rgba(0,0,0,0.05); transition:0.3s; border:1px solid #f0f0f0; }

        .doc-card:hover { transform:translateY(-5px); box-shadow:0 15px 30px rgba(0,0,0,0.1); border-color:#a18cd1; }

        .doc-img { width:90px; height:90px; border-radius:50%; object-fit:cover; margin-bottom:15px; border:3px solid #f8f9fa; }

        .doc-btn { background:#a18cd1; color:white; border:none; padding:10px 25px; border-radius:25px; cursor:pointer; margin-top:15px; font-weight:bold; transition:0.3s; }

        .doc-btn:hover { background:#8e7cc3; }

    </style>"""



    content = f"""

    {css}

    <div class="doc-header">

        <h1>Find Best Doctors</h1>

        <p>Book appointments with top specialists</p>

    </div>

    

    <div class="search-area">

        <input type="text" id="docSearch" list="suggestions" class="search-inp" placeholder="Type doctor name or speciality..." onkeyup="filterDocs()">

        

        <datalist id="suggestions">

            {datalist_opts}

        </datalist>

    </div>

    

    <div class="doc-grid">

        {doc_html}

    </div>

    

    {script}

    <div style="text-align:center; margin:30px;"><a href="/services" style="color:#555;">Back to Services</a></div>

    """

    return f"<!DOCTYPE html><html><head><title>Doctors</title></head><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



def page_doctor_profile(user, lang, doc_id):

    # Demo logic to get doctor name

    doc_name = "Dr. Expert" # In real app, fetch from DB using doc_id

    

    content = f"""

    <div style="max-width:600px; margin:40px auto; padding:20px; font-family:sans-serif;">

        <div style="text-align:center;">

            <img src="https://placehold.co/150?text=Doc" style="border-radius:50%; border:5px solid #f0f0f0;">

            <h1 style="color:#2c3e50;">{doc_name}</h1>

            <p style="color:#666;">MBBS, MD - Senior Specialist</p>

        </div>

        

        <div style="margin-top:40px; display:flex; flex-direction:column; gap:20px;">

            <a href="/doctor-chat?id={doc_id}" style="text-decoration:none;">

                <div style="background:white; border:1px solid #ddd; padding:25px; border-radius:15px; display:flex; align-items:center; gap:20px; box-shadow:0 5px 15px rgba(0,0,0,0.05); transition:0.3s;">

                    <span style="font-size:2rem;">💬</span>

                    <div>

                        <h3 style="margin:0; color:#007bff;">Chat with Doctor</h3>

                        <p style="margin:5px 0 0 0; color:#666; font-size:0.9rem;">Send reports, get prescription (PDF/JPG)</p>

                    </div>

                </div>

            </a>



            <a href="/doctor-video-call?target={doc_name}" style="text-decoration:none;">

                <div style="background:white; border:1px solid #ddd; padding:25px; border-radius:15px; display:flex; align-items:center; gap:20px; box-shadow:0 5px 15px rgba(0,0,0,0.05); transition:0.3s;">

                    <span style="font-size:2rem;">📹</span>

                    <div>

                        <h3 style="margin:0; color:#e91e63;">Video Consultation</h3>

                        <p style="margin:5px 0 0 0; color:#666; font-size:0.9rem;">Face-to-face consultation</p>

                    </div>

                </div>

            </a>

        </div>

        

        <div style="text-align:center; margin-top:30px;">

            <a href="/doctor-consult" style="color:#666;">Back to Doctors</a>

        </div>

    </div>

    """

    return f"<!DOCTYPE html><html><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



def page_doctor_chat(user, lang, doc_id):

    content = f"""

    <div style="max-width:800px; margin:20px auto; font-family:sans-serif; height:80vh; display:flex; flex-direction:column; border:1px solid #ddd; border-radius:15px; overflow:hidden;">

        <div style="background:#007bff; color:white; padding:15px; display:flex; justify-content:space-between; align-items:center;">

            <b>Chatting with Doctor</b>

            <a href="/doctor-profile?id={doc_id}" style="color:white; text-decoration:none;">Close ✖</a>

        </div>

        

        <div id="chatArea" style="flex:1; background:#f5f5f5; padding:20px; overflow-y:auto;">

            <div style="background:white; padding:10px 15px; border-radius:10px; display:inline-block; max-width:70%;">

                Hello! How can I help you today? You can share your reports here.

            </div>

        </div>

        

        <div style="background:white; padding:10px; border-top:1px solid #ddd; display:flex; gap:10px; align-items:center;">

            <button onclick="document.getElementById('fileIn').click()" style="background:#eee; border:none; padding:10px; border-radius:50%; cursor:pointer;">📎</button>

            <input type="file" id="fileIn" hidden onchange="alert('File sent to Doctor!')">

            <input type="text" placeholder="Type a message..." style="flex:1; padding:10px; border:1px solid #ddd; border-radius:20px; outline:none;">

            <button style="background:#007bff; color:white; border:none; padding:10px 20px; border-radius:20px; cursor:pointer;">Send</button>

        </div>

    </div>

    """

    return f"<!DOCTYPE html><html><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



def page_doctor_video_call(user, lang, doc_name):

    # டாக்டர் பெயர் URL-ல் இருந்து வரும்

    content = f"""

    <div style="max-width:900px; margin:20px auto; padding:20px; font-family:sans-serif; text-align:center;">

        <div style="background:#2c3e50; height:500px; border-radius:30px; display:flex; flex-direction:column; align-items:center; justify-content:center; color:white; box-shadow:0 20px 50px rgba(0,0,0,0.3);">

            <div style="font-size:5rem; margin-bottom:20px; border:3px solid white; border-radius:50%; padding:10px;">👨‍⚕️</div>

            <h2>Connecting to {doc_name}...</h2>

            <p>Secure Medical Line | Encrypted</p>

            <div style="margin-top:20px;">

                <span style="display:inline-block; width:10px; height:10px; background:white; border-radius:50%; animation:blink 1s infinite;"></span>

                <span style="display:inline-block; width:10px; height:10px; background:white; border-radius:50%; animation:blink 1s infinite 0.2s;"></span>

                <span style="display:inline-block; width:10px; height:10px; background:white; border-radius:50%; animation:blink 1s infinite 0.4s;"></span>

            </div>

            <style>@keyframes blink {{ 0% {{ opacity: 0.2; }} 50% {{ opacity: 1; }} 100% {{ opacity: 0.2; }} }}</style>

            <br><br>

            <a href="/doctor-profile?id=d1"><button style="background:#e74c3c; color:white; border:none; padding:15px 40px; border-radius:30px; cursor:pointer; font-weight:bold; font-size:1.1rem;">End Consultation</button></a>

        </div>

    </div>

    """

    return f"<!DOCTYPE html><html><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



def page_drugs_store(user, lang, params=None):

    # --- Search Logic ---

    search_list = []

    for key, val in HERBAL_DB.items(): search_list.append({"id": key, "name": val['title'], "type": "Ayurvedic"})

    for key, val in ALLOPATHY_DB.items(): search_list.append({"id": key, "name": val['title'], "type": "Allopathy"})

    json_data = json.dumps(search_list)



    status_msg = ""

    if params and 'upload' in params:

        if params['upload'][0] == 'success': status_msg = "<div class='alert success'>✅ Prescription Uploaded Successfully!</div>"

        elif params['upload'][0] == 'failed': status_msg = "<div class='alert error'>❌ Upload Failed. Try again.</div>"



    css = """

    <style>

        .store-header { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 60px 20px; text-align: center; color: white; border-radius: 0 0 30px 30px; }

        .store-header h2 { font-size: 2.5rem; margin: 0; }

        .store-header p { font-size: 1.1rem; opacity: 0.9; }

        

        .search-wrapper { max-width: 600px; margin: -30px auto 30px; position: relative; z-index: 10; padding: 0 20px; }

        .search-input { width: 100%; padding: 18px 25px; border-radius: 50px; border: none; font-size: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.15); outline: none; }

        .search-results { position: absolute; top: 60px; left: 20px; right: 20px; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); overflow: hidden; display: none; }

        .search-item { padding: 15px; border-bottom: 1px solid #eee; cursor: pointer; display: flex; justify-content: space-between; }

        .search-item:hover { background: #f9f9f9; }



        /* CATEGORY ROWS */

        .cat-row { display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; margin-bottom: 20px; padding: 0 20px; }

        

        .cat-card { 

            background: white; border-radius: 20px; padding: 20px; width: 220px; 

            text-align: center; text-decoration: none; color: #333; 

            box-shadow: 0 5px 15px rgba(0,0,0,0.05); transition: transform 0.3s; 

            border: 1px solid #f0f0f0; 

        }

        .cat-card:hover { transform: translateY(-10px); box-shadow: 0 15px 30px rgba(0,0,0,0.1); border-color: #38ef7d; }

        .cat-img { height: 120px; width: 100%; object-fit: contain; margin-bottom: 15px; }

        

        .alert { padding: 15px; border-radius: 10px; text-align: center; margin: 20px auto; max-width: 500px; font-weight: bold; }

        .success { background: #d4edda; color: #155724; }

        .error { background: #f8d7da; color: #721c24; }

        

        .upload-section { background: #fff; padding: 30px; border-radius: 20px; max-width: 600px; margin: 40px auto; text-align: center; box-shadow: 0 5px 20px rgba(0,0,0,0.05); }

        .upload-btn { background: #333; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }

    </style>

    <script>

        const medicines = """ + json_data + """;

        function filterMedicines() {

            const input = document.getElementById("searchInput").value.toLowerCase();

            const resultsDiv = document.getElementById("resultsBox");

            resultsDiv.innerHTML = "";

            if (!input) { resultsDiv.style.display = "none"; return; }

            const filtered = medicines.filter(item => item.name.toLowerCase().includes(input));

            if (filtered.length > 0) {

                resultsDiv.style.display = "block";

                filtered.forEach(item => {

                    const div = document.createElement("div");

                    div.className = "search-item";

                    div.innerHTML = `<span>${item.name}</span> <small style='color:#888'>${item.type}</small>`;

                    div.onclick = function() { window.location.href = "/product-detail?id=" + item.id; };

                    resultsDiv.appendChild(div);

                });

            } else { resultsDiv.style.display = "none"; }

        }

    </script>

    """



    content = f"""

    {css}

    <div class="store-header">

        <h2>{LANG[lang]['drugs_store_page_title']}</h2>

        <p>Quality Medicines at Best Prices | Flat 10% Off</p>

    </div>



    <div class="search-wrapper">

        <input type="search" id="searchInput" class="search-input" placeholder="{LANG[lang]['search_placeholder']}" onkeyup="filterMedicines()" autocomplete="off">

        <div id="resultsBox" class="search-results"></div>

    </div>



    {status_msg}  <div class="upload-section">

        <h3>📝 Upload Prescription</h3>

        <p style="color:#666; font-size:0.9rem;">Upload your doctor's prescription and we will find the medicines for you.</p>

        

        <form method="post" action="/upload-prescription" enctype="multipart/form-data">

            

            <input type="hidden" name="source" value="drugs_store">

            

            <input type="file" name="prescription" style="margin: 15px 0;">

            <br>

            <button type="submit" class="upload-btn">Analyze & Order</button>

        </form>

    </div>



    <h3 style="text-align:center; color:#444; margin-top:40px; margin-bottom:20px;">Choose Category</h3>

    

    <div class="cat-row">

        <a href="/drugs-store/allopathy" class="cat-card">

            <img src="/static/allopathy.jpg" class="cat-img" onerror="this.src='https://placehold.co/150?text=Allopathy'">

            <h3>{LANG[lang]['allopathy']}</h3>

        </a>

        <a href="/drugs-store/ayurvedic" class="cat-card">

            <img src="/static/ayurvedic.jpg" class="cat-img" onerror="this.src='https://placehold.co/150?text=Ayurvedic'">

            <h3>{LANG[lang]['ayurvedic']}</h3>

        </a>

        <a href="/drugs-store/homeopathy" class="cat-card">

            <img src="/static/homeopathy.jpg" class="cat-img" onerror="this.src='https://placehold.co/150?text=Homeopathy'">

            <h3>{LANG[lang]['homeopathy']}</h3>

        </a>

    </div>



    <div class="cat-row">

        <a href="/drugs-store/medical-devices" class="cat-card">

            <img src="/static/medical_devices.jpg" class="cat-img" onerror="this.src='https://placehold.co/150?text=Devices'">

            <h3>{LANG[lang]['medical_devices']}</h3>

        </a>



        <a href="/drugs-store/vitamins" class="cat-card">

            <img src="/static/vitamins.jpg" class="cat-img" onerror="this.src='https://placehold.co/150?text=Vitamins'">

            <h3>{LANG[lang]['vitamins_supplements']}</h3>

        </a>

    </div>

    

    <div style="text-align:center; margin: 40px;">

        <a href="/services" style="color:#666; text-decoration:none;">&larr; {LANG[lang]['back_to_services']}</a>

    </div>

    """

    html = f"<!DOCTYPE html><html><head><title>Drug Store</title></head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



def page_ayurvedic_products(user, lang):

    styles = '''<style>.product-grid-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 25px; padding: 20px; } .product-item { flex: 1 1 calc(33.333% - 25px); max-width: calc(33.333% - 25px); min-width: 200px; display: flex; flex-direction: column; align-items: center; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.1); border-radius: 10px; padding: 15px; background-color: #ffffff; transition: transform 0.2s; } .product-item:hover { transform: translateY(-5px); } .image-wrapper { width: 100%; height: 200px; display: flex; justify-content: center; align-items: center; overflow: hidden; border-radius: 8px; margin-bottom: 15px; background-color: #f8f8f8; } .product-image { max-width: 100%; max-height: 100%; width: auto; height: auto; object-fit: contain; display: block; } .name-button { background-color: #2c3e50; color: white; border: none; border-radius: 5px; padding: 10px 18px; font-size: 15px; font-weight: bold; text-align: center; width: 100%; cursor: pointer; text-decoration: none; display: block; } .name-button:hover { background-color: #34495e; }</style>'''

    product_html_list = []

    for product in AYURVEDIC_PRODUCTS_DATA:

        product_name = product['name'].get(lang, product['name']['en'])

        link = f"/product-detail?id={product['key']}"

        product_html_list.append(f'''<div class="product-item"><div class="image-wrapper"><img src="{product['url']}" alt="{product_name}" class="product-image"></div><a href="{link}" class="name-button">{product_name}</a></div>''')

    content = f'''<div class="card" style="text-align:center;"><h2>{LANG[lang]['ayurvedic_products_title']}</h2><p style="color:#666;">{LANG[lang]['click_for_details']}</p><div class="product-grid-container">{''.join(product_html_list)}</div><a href="/drugs-store"><button style="margin-top:30px; margin-bottom: 20px;">{LANG[lang]['back_to_drug_store']}</button></a></div>'''

    html = f"<!DOCTYPE html><html><head><title>{LANG[lang]['ayurvedic_products_title']}</title>{styles}</head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



def page_allopathic_products(user, lang):

    # --- பழைய டிசைனுக்கான CSS ---

    styles = '''

    <style>

        .product-grid-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 25px; padding: 20px; } 

        .product-item { 

            flex: 1 1 calc(33.333% - 25px); max-width: calc(33.333% - 25px); min-width: 200px; 

            display: flex; flex-direction: column; align-items: center; text-align: center; 

            box-shadow: 0 2px 6px rgba(0,0,0,0.1); border-radius: 10px; padding: 15px; 

            background-color: #ffffff; transition: transform 0.2s; 

        } 

        .product-item:hover { transform: translateY(-5px); } 

        .image-wrapper { 

            width: 100%; height: 200px; display: flex; justify-content: center; align-items: center; 

            overflow: hidden; border-radius: 8px; margin-bottom: 15px; background-color: #ffffff; 

        } 

        .product-image { max-width: 100%; max-height: 100%; object-fit: contain; } 

        .name-button { 

            background-color: #00796b; color: white; border: none; border-radius: 5px; 

            padding: 10px 18px; font-size: 15px; font-weight: bold; text-align: center; 

            width: 100%; cursor: pointer; text-decoration: none; display: block; 

        } 

        .name-button:hover { background-color: #004d40; }

    </style>

    '''

    

    product_html_list = []

    # டேட்டாபேஸ்ல இருந்து எடுக்குறோம்

    for key, data in ALLOPATHY_DB.items():

        link = f"/product-detail?id={key}"

        img_src = data.get('image', '')

        

        # படம் இருக்கான்னு செக் பண்றோம்

        image_html = f'<img src="{img_src}" alt="{data["title"]}" class="product-image">' if img_src else '<span style="font-size:50px;">💊</span>'

        

        # பழைய கார்டு டிசைன்

        product_html_list.append(f'''

        <div class="product-item">

            <div class="image-wrapper">{image_html}</div>

            <a href="{link}" class="name-button">{data['title']}</a>

        </div>''')



    content = f'''

    <div class="card" style="text-align:center;">

        <h2>{LANG[lang]['allopathy_products_title']}</h2>

        <p style="color:#666;">{LANG[lang]['click_for_details']}</p>

        <div class="product-grid-container">{''.join(product_html_list)}</div>

        <a href="/drugs-store">

            <button style="margin-top:30px; margin-bottom: 20px;">{LANG[lang]['back_to_drug_store']}</button>

        </a>

    </div>

    '''

    

    html = f"<!DOCTYPE html><html><head><title>{LANG[lang]['allopathy_products_title']}</title>{styles}</head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



def page_acetaminophen_detail(user, lang):

    # --- 1. Brand Data (From your PDF & Screenshot) ---

    acetaminophen_brands = [

        {"brand": "Dolo 650", "mfr": "Micro Labs Ltd", "img": "/static/dolo650.jpg"},

        {"brand": "Calpol", "mfr": "GSK Pharmaceuticals", "img": "/static/calpol.jpg"},

        {"brand": "Crocin", "mfr": "GSK Consumer Healthcare", "img": "/static/crocin.jpg"},

        {"brand": "Pacimol", "mfr": "Ipca Laboratories", "img": "/static/pacimol.jpg"},

        {"brand": "Paracip", "mfr": "Cipla Ltd", "img": "/static/paracip.jpg"},

        {"brand": "Sumo L", "mfr": "Alkem Laboratories", "img": "/static/sumol.jpg"},

        {"brand": "Febrex", "mfr": "Indoco Remedies", "img": "/static/febrex.jpg"}

    ]



    # --- 2. Generate Brand Table Rows ---

    brand_rows_html = ""

    for item in acetaminophen_brands:

        brand_rows_html += f"""

        <tr>

            <td style="padding: 12px; border-bottom: 1px solid #eee; font-weight: bold; color: #2c3e50;">{item['brand']}</td>

            <td style="padding: 12px; border-bottom: 1px solid #eee; color: #555;">{item['mfr']}</td>

            <td style="padding: 12px; border-bottom: 1px solid #eee; text-align: center;">

                <img src="{item['img']}" onclick="openModal(this.src)" class="zoom-img" alt="{item['brand']}" onerror="this.onerror=null;this.src='https://placehold.co/50x50?text=No+Image';">

            </td>

        </tr>

        """



    # --- 3. Structure Images ---

    img_2d = "/static/aceta.png"

    img_3d = "/static/minophen.png"



    # --- 4. CSS & JS for Modal & Layout ---

    styles_script = """

    <style>

        .zoom-img { height: 50px; width: auto; border-radius: 5px; border: 1px solid #ddd; padding: 2px; cursor: pointer; transition: 0.3s; }

        .zoom-img:hover { transform: scale(1.1); border-color: #007bff; }

        

        .topic-box { margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 10px; border-left: 5px solid #007bff; }

        .topic-title { color: #2c3e50; font-size: 1.4rem; font-weight: bold; margin-bottom: 15px; border-bottom: 1px solid #ddd; padding-bottom: 10px; }

        .sub-topic { margin-top: 20px; font-weight: bold; color: #495057; font-size: 1.1rem; }

        .content-text { color: #555; line-height: 1.6; margin-bottom: 10px; }

        

        /* Image Placeholder Style */

        .img-placeholder {

            width: 100%; max-width: 300px; height: 150px; 

            background: #e9ecef; border: 2px dashed #adb5bd; border-radius: 10px;

            display: flex; align-items: center; justify-content: center;

            color: #6c757d; font-size: 0.9rem; margin: 10px 0; cursor: pointer;

        }

        .img-placeholder img { max-width: 100%; max-height: 100%; border-radius: 10px; }



        /* Modal Styles */

        .modal { display: none; position: fixed; z-index: 1000; padding-top: 50px; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.9); }

        .modal-content { margin: auto; display: block; width: 80%; max-width: 700px; animation: zoom 0.6s; }

        @keyframes zoom { from {transform:scale(0)} to {transform:scale(1)} }

        .close { position: absolute; top: 15px; right: 35px; color: #f1f1f1; font-size: 40px; font-weight: bold; transition: 0.3s; cursor: pointer; }

        

        /* Summary Table */

        .summary-table { width: 100%; border-collapse: collapse; margin-top: 15px; }

        .summary-table th, .summary-table td { border: 1px solid #ddd; padding: 10px; text-align: left; }

        .summary-table th { background-color: #007bff; color: white; }

    </style>



    <script>

        function openModal(src) {

            document.getElementById("myModal").style.display = "block";

            document.getElementById("img01").src = src;

        }

        function closeModal() { document.getElementById("myModal").style.display = "none"; }

        window.onclick = function(event) { if (event.target == document.getElementById("myModal")) closeModal(); }

    </script>

    """



    # --- updated content for page_acetaminophen_detail ---

    content = f"""

    {styles_script}

    <div style="max-width: 900px; margin: 40px auto; padding: 40px; background: white; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); font-family: 'Segoe UI', sans-serif;">

        

        <h1 style="color: #2c3e50; text-align: center; border-bottom: 3px solid #007bff; padding-bottom: 10px;">ACETAMINOPHEN (Paracetamol)</h1>

        

        <h3 style="color: #2c3e50; margin-top: 30px;">Popular Brand Names</h3>

        <div style="overflow-x: auto;">

            <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">

                <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">

                    <th style="padding: 12px;">Brand Name</th>

                    <th style="padding: 12px;">Manufacturer</th>

                    <th style="padding: 12px; text-align: center;">Image</th>

                </tr>

                {brand_rows_html}

            </table>

        </div>



        <div class="topic-box">

            <div class="topic-title">1. Chemical Structure & IUPAC Name</div>

            <p class="content-text">The chemical structure consists of an amide group attached to a benzene ring (aromatic ring) with a hydroxyl group at the para-position.</p>

            <ul>

                <li><b>IUPAC Name:</b> <i>N</i>-(4-hydroxyphenyl)acetamide</li>

                <li><b>Formula:</b> C<sub>8</sub>H<sub>9</sub>NO<sub>2</sub></li>

                <li><b>Weight:</b> 151.16 g/mol</li>

            </ul>

            

            <div style="display:flex; gap:20px; flex-wrap:wrap;">

                <div style="flex:1;">

                    <div class="sub-topic">2D Structure</div>

                    <div class="img-placeholder" onclick="openModal('{img_2d}')">

                        <img src="{img_2d}" onerror="this.style.display='none'; this.parentNode.innerHTML='Add 2D Image Here'">

                    </div>

                </div>

                <div style="flex:1;">

                    <div class="sub-topic">3D Structure</div>

                    <div class="img-placeholder" onclick="openModal('{img_3d}')">

                        <img src="{img_3d}" onerror="this.style.display='none'; this.parentNode.innerHTML='Add 3D Image Here'">

                    </div>

                </div>

            </div>

        </div>

        

        <div class="topic-box" style="border-left-color: #28a745;">

            <div class="topic-title">💊 2. Therapeutic Uses</div>

            <p class="content-text">

                Acetaminophen is primarily used for its <b>analgesic</b> (pain-relieving) and 

                <b>antipyretic</b> (fever-reducing) properties. Unlike NSAIDs (like Ibuprofen), 

                it has negligible anti-inflammatory effects.

            </p>

            <ul style="color: #555; line-height: 1.8; list-style-type: none; padding-left: 0;">

                <li style="margin-bottom: 10px;">🤕 <b>Pain Management:</b> Relieves mild to moderate pain such as headaches, migraines, toothaches, muscle aches, and menstrual cramps.</li>

                <li style="margin-bottom: 10px;">🌡️ <b>Fever Reduction:</b> Effective in treating pyrexia (fever) associated with the common cold or flu.</li>

                <li style="margin-bottom: 10px;">🏥 <b>Post-Surgical Pain:</b> Often used as a baseline analgesic after minor surgeries.</li>

                <li style="margin-bottom: 10px;">🦴 <b>Osteoarthritis:</b> Used as a first-line treatment for pain where inflammation is not the primary concern.</li>

            </ul>

        </div>



        <div id="myModal" class="modal">

            <span class="close" onclick="closeModal()">&times;</span>

            <img class="modal-content" id="img01">

        </div>



        <div class="topic-box" style="border-left-color: #dc3545;">

            <div class="topic-title">⚠️ 3. Adverse Drug Reactions (ADR)</div>

            <p class="content-text">

                While safe at therapeutic doses, it has specific risks:

            </p>

            <ul style="color: #555; line-height: 1.8; list-style-type: none; padding-left: 0;">

                <li style="margin-bottom: 10px;">🧪 <b>Hepatotoxicity (Liver Damage):</b> This is the most serious ADR, usually occurring with an overdose. It is caused by the accumulation of the toxic metabolite <b>NAPQI</b> (<i>N</i>-acetyl-<i>p</i>-benzoquinone imine).</li>

                <li style="margin-bottom: 10px;">🩺 <b>Dermatological Reactions:</b> Rare but serious skin reactions like Stevens-Johnson Syndrome (SJS) or Toxic Epidermal Necrolysis (TEN).</li>

                <li style="margin-bottom: 10px;">🤢 <b>Gastrointestinal:</b> Nausea and vomiting (less common compared to NSAIDs).</li>

                <li style="margin-bottom: 10px;">🩸 <b>Hematological:</b> Very rarely, it can cause thrombocytopenia (low platelet count) or leucopenia.</li>

            </ul>

        </div>



        <div class="topic-box" style="border-left-color: #ffc107;">

            <div class="topic-title">🤝 4. Drug-Drug Interactions</div>

            <p class="content-text">

                Taking Acetaminophen with other substances can change how it works or increase risks:

            </p>

            <ul style="color: #555; line-height: 1.8; list-style-type: none; padding-left: 0;">

                <li style="margin-bottom: 10px;">🍺 <b>Alcohol:</b> Increases the risk of hepatotoxicity because chronic alcohol consumption induces the CYP2E1 enzyme, leading to higher production of the toxic metabolite NAPQI.</li>

                <li style="margin-bottom: 10px;">💊 <b>Warfarin:</b> Chronic high doses of acetaminophen can enhance the anticoagulant effect of Warfarin, increasing the risk of bleeding.</li>

                <li style="margin-bottom: 10px;">🧪 <b>Isoniazid & Rifampin:</b> These anti-TB drugs induce liver enzymes, increasing the risk of liver injury when taken with acetaminophen.</li>

                <li style="margin-bottom: 10px;">📉 <b>Cholestyramine:</b> Reduces the absorption of acetaminophen if taken together.</li>

                <li style="margin-bottom: 10px;">🚀 <b>Metoclopramide/Domperidone:</b> These drugs increase the rate of gastric emptying, which can speed up the absorption of acetaminophen.</li>

            </ul>

        </div>



        <div class="topic-box" style="border-left-color: #17a2b8;">

            <div class="topic-title">🍎 5. Food-Drug Interaction</div>

            <p class="content-text">

                Certain foods and dietary habits can affect how your body absorbs or processes Acetaminophen:

            </p>

            

            <div class="sub-topic">🥯 1. High-Carbohydrate Meals</div>

            <p class="content-text">Eating a meal very high in carbohydrates (especially those rich in pectin or fiber) can <b>delay the absorption</b> of Acetaminophen.</p>

            <ul style="color: #555; line-height: 1.6;">

                <li><b>Mechanism:</b> Carbohydrates can bind to the drug or physically slow down its movement from the stomach to the small intestine.</li>

                <li><b>Result:</b> A delayed onset of pain relief.</li>

            </ul>



            <div class="sub-topic">🍷 2. Chronic Alcohol Consumption</div>

            <p class="content-text">This is the most clinically significant "dietary" interaction.</p>

            <ul style="color: #555; line-height: 1.6;">

                <li><b>The Science:</b> Chronic alcohol use induces the <b>CYP2E1</b> enzyme.</li>

                <li><b>The Danger:</b> This causes the body to produce more <b>NAPQI</b> (toxic metabolite), leading to severe <b>hepatotoxicity</b> (liver cell death).</li>

            </ul>



            <div class="sub-topic">☕ 3. Caffeine</div>

            <p class="content-text">Caffeine is actually a "helpful" interaction and is often formulated together with the drug.</p>

            <ul style="color: #555; line-height: 1.6;">

                <li><b>Effect:</b> Caffeine can <b>increase the rate of absorption</b> and enhance the analgesic (pain-killing) effect.</li>

            </ul>



            <div class="sub-topic">🥦 4. Cruciferous Vegetables</div>

            <p class="content-text">Vegetables like broccoli, brussels sprouts, and cabbage can induce certain liver enzymes (like CYP1A2).</p>

            <ul style="color: #555; line-height: 1.6;">

                <li><b>Effect:</b> A diet very heavy in these vegetables might slightly <b>increase the metabolism</b> of the drug, potentially reducing its duration of action.</li>

            </ul>

        </div>



        <div class="topic-box" style="border-left-color: #6c757d; background-color: #fcfcfc;">

            <div class="topic-title">📊 Summary Table for Study</div>

            <p class="content-text">Quick reference guide for Acetaminophen interactions:</p>

            

            <div style="overflow-x: auto;">

                <table class="summary-table" style="width: 100%; border-collapse: collapse; margin-top: 15px;">

                    <thead>

                        <tr style="background-color: #6c757d; color: white;">

                            <th style="padding: 12px; border: 1px solid #ddd;">🍎 Food/Substance</th>

                            <th style="padding: 12px; border: 1px solid #ddd;">🔄 Effect on Drug</th>

                            <th style="padding: 12px; border: 1px solid #ddd;">🩺 Clinical Result</th>

                        </tr>

                    </thead>

                    <tbody>

                        <tr>

                            <td style="padding: 10px; border: 1px solid #ddd;">🥯 <b>High Fiber/Carbs</b></td>

                            <td style="padding: 10px; border: 1px solid #ddd;">Slows gastric emptying</td>

                            <td style="padding: 10px; border: 1px solid #ddd;">🐢 Slower pain relief</td>

                        </tr>

                        <tr style="background-color: #fff5f5;">

                            <td style="padding: 10px; border: 1px solid #ddd;">🍺 <b>Alcohol (Chronic)</b></td>

                            <td style="padding: 10px; border: 1px solid #ddd;">Induces CYP2E1 enzyme</td>

                            <td style="padding: 10px; border: 1px solid #ddd;">🚨 <b>High Risk of Liver Damage</b></td>

                        </tr>

                        <tr>

                            <td style="padding: 10px; border: 1px solid #ddd;">☕ <b>Caffeine</b></td>

                            <td style="padding: 10px; border: 1px solid #ddd;">Increases absorption rate</td>

                            <td style="padding: 10px; border: 1px solid #ddd;">⚡ Faster, stronger pain relief</td>

                        </tr>

                        <tr style="background-color: #f0fdf4;">

                            <td style="padding: 10px; border: 1px solid #ddd;">🥣 <b>Empty Stomach</b></td>

                            <td style="padding: 10px; border: 1px solid #ddd;">Faster gastric emptying</td>

                            <td style="padding: 10px; border: 1px solid #ddd;">⏩ Quickest onset of action</td>

                        </tr>

                    </tbody>

                </table>

            </div>

        </div>



        <br><br>

        <div style="text-align: center; padding-bottom: 20px;">

            <a href="/drugs-store/allopathy" style="text-decoration: none;">

                <button style="background: #6c757d; color: white; border: none; padding: 12px 30px; border-radius: 8px; cursor: pointer; font-weight: bold;">

                    &larr; Back to Allopathy

                </button>

            </a>

        </div>



    </div>

    """



    return f"<!DOCTYPE html><html><head><title>Acetaminophen Details</title></head><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



def page_ibuprofen_detail(user, lang):

    content = f"""

    <style>

        .med-container {{ max-width: 850px; margin: 30px auto; padding: 40px; background: #fff; font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #000; }}

        .med-title {{ font-size: 2rem; font-weight: bold; margin-bottom: 25px; text-transform: uppercase; border-bottom: 3px solid #007bff; padding-bottom: 10px; text-align: center; color: #2c3e50; }}

        .info-label {{ font-weight: bold; margin-top: 22px; display: block; font-size: 1.1rem; color: #2c3e50; }}

        .info-text {{ margin-bottom: 15px; display: block; color: #333; }}

        .structure-box {{ text-align: center; margin: 40px 0; padding: 20px; background: #fdfdfd; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}

        .structure-img {{ max-width: 100%; height: auto; border-radius: 5px; }}

        

        .usage-list {{ margin-top: 10px; padding-left: 0; list-style-type: none; }}

        .usage-item {{ margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #eee; }}

        .usage-title {{ font-weight: bold; display: block; color: #2c3e50; }}

        

        .section-divider {{ border-top: 2px solid #eee; margin-top: 40px; padding-top: 25px; }}

        .section-header {{ font-size: 1.4rem; font-weight: bold; color: #2c3e50; margin-bottom: 15px; text-transform: uppercase; display: flex; align-items: center; }}

        

        /* Box Styles */

        .warning-box {{ background-color: #fff5f5; border-left: 5px solid #e53e3e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(229, 62, 62, 0.1); }}

        .warning-title {{ color: #c53030; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .interaction-box {{ background-color: #fffaf0; border-left: 5px solid #ed8936; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(237, 137, 54, 0.1); }}

        .interaction-title {{ color: #dd6b20; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .food-box {{ background-color: #f0fdf4; border-left: 5px solid #22c55e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(34, 197, 94, 0.1); }}

        .food-title {{ color: #15803d; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .dosing-box {{ background-color: #f0f9ff; border-left: 5px solid #0ea5e9; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(14, 165, 233, 0.1); }}

        .dosing-title {{ color: #0369a1; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .im-box {{ background-color: #f5f3ff; border-left: 5px solid #7c3aed; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(124, 58, 237, 0.1); }}

        .im-title {{ color: #5b21b6; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}



        .summary-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background-color: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}

        .summary-table th, .summary-table td {{ border: 1px solid #eee; padding: 15px; text-align: left; font-size: 0.95rem; }}

        .summary-table th {{ background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%); color: white; text-transform: uppercase; letter-spacing: 1px; }}

        .summary-table tr:nth-child(even) {{ background-color: #fcfcfc; }}

        .param-name {{ font-weight: bold; color: #2c3e50; width: 35%; background-color: #f8f9fa; }}

    </style>



    <div class="med-container">

        <div class="med-title">IBUPROFEN</div>



        <div class="section-header">🧪 Chemical Specifications</div>

        <span class="info-label">IUPAC Name:</span>

        <span class="info-text">2-(4-Isobutylphenyl)propanoic acid</span>

        

        <span class="info-label">Molecular Formula:</span>

        <span class="info-text">C<sub>13</sub>H<sub>18</sub>O<sub>2</sub></span>



        <span class="info-label">Structure:</span>

        <span class="info-text">A propionic acid group attached to a phenyl ring, with an isobutyl group (2-methylpropyl) at the 4-position.</span>



        <span class="info-label">Alternative Names:</span>

        <span class="info-text">-2-(p-isobutylphenyl)propionic acid, 4-isobutyl-&alpha;-methylphenylacetic acid.</span>



        <span class="info-label">Molecular Weight:</span>

        <span class="info-text">206.29g/mol</span>



        <div class="structure-box">

                        <img src="/static/ib_structure.jpg" class="structure-img" alt="Ibuprofen Structure Diagram" onerror="this.src='https://placehold.co/500x300?text=Ibuprofen+Structure+Diagram'">

            <p style="margin-top:10px; color: #666;"><b>Ibuprofen</b></p>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff;">💊 Therapeutic Uses</div>

            <p>Ibuprofen is widely used for both acute and chronic conditions across different age groups:</p>

            <div class="usage-list">

                <div class="usage-item"><span class="usage-title">Pain Relief:</span>Effective for mild to moderate pain, including headaches, migraines, dental pain, muscle aches, and backaches.</div>

                <div class="usage-item"><span class="usage-title">Fever Reduction:</span>Used as an antipyretic to reduce high body temperatures in adults and children (typically older than 6 months).</div>

                <div class="usage-item"><span class="usage-title">Inflammatory Conditions:</span>Prescribed for long-term management of rheumatoid arthritis, osteoarthritis, and ankylosing spondylitis.</div>

                <div class="usage-item"><span class="usage-title">Menstrual Cramps:</span>Specifically indicated for relieving symptoms of primary dysmenorrhea.</div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #6f42c1;">⚠️ Adverse Drug Reaction</div>

            <p><b>Common Adverse Reactions:</b></p>

            <p>Most patients experience only mild symptoms, primarily affecting the digestive and nervous systems:</p>

            <div class="usage-list">

                <div class="usage-item"><span class="usage-title">Gastrointestinal (GI):</span>Indigestion, heartburn, nausea, stomach pain, gas, bloating, diarrhea, or constipation.</div>

                <div class="usage-item"><span class="usage-title">Central Nervous System:</span>Dizziness, headache, nervousness, and drowsiness.</div>

                <div class="usage-item"><span class="usage-title">Other:</span>Tinnitus (ringing in the ears), mild skin rashes, and fluid retention (edema).</div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #e53e3e;">🚨 Serious and Potentially Fatal Reactions</div>

            <div class="warning-box">

                <span class="warning-title">Black Box Warnings</span>

                <p>The FDA and other health agencies have issued Black Box Warnings for several severe risks associated with ibuprofen.</p>

            </div>

            <div class="usage-list">

                <div class="usage-item"><span class="usage-title">Cardiovascular:</span>Increased risk of fatal heart attack or stroke, which can occur even in the first few weeks of use.</div>

                <div class="usage-item"><span class="usage-title">Severe Gastrointestinal:</span>Serious bleeding, ulceration, and perforation of the stomach or intestines, which may occur without warning.</div>

                <div class="usage-item"><span class="usage-title">Renal (Kidney):</span>Acute kidney injury (AKI), interstitial nephritis, and renal failure, especially in those with pre-existing kidney disease or dehydration.</div>

                <div class="usage-item"><span class="usage-title">Anaphylaxis:</span>Severe allergic reactions involving swelling of the face/throat, difficulty breathing, and shock.</div>

                <div class="usage-item"><span class="usage-title">Severe Skin Reactions:</span>Rare but dangerous conditions like Stevens-Johnson syndrome (SJS) or toxic epidermal necrolysis (TEN) characterized by blistering and peeling skin.</div>

                <div class="usage-item"><span class="usage-title">Pregnancy Risks:</span>Use after 20 weeks of pregnancy can cause low amniotic fluid and harm the unborn baby's kidneys or heart.</div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ed8936;">🤝 Drug-Drug Interaction</div>

            <div class="interaction-box">

                <span class="interaction-title">High-Risk Interactions (Increased Bleeding)</span>

                <p>Combining ibuprofen with medications that also affect blood clotting significantly elevates the risk of gastrointestinal (GI) bleeding or bruising.</p>

            </div>

            <div class="usage-list">

                <div class="usage-item"><span><b>Anticoagulants:</b> Medications like warfarin (Coumadin), apixaban (Eliquis), and rivaroxaban (Xarelto).</span></div>

                <div class="usage-item"><span><b>Antiplatelets:</b> Low-dose aspirin or clopidogrel (Plavix).</span></div>

                <div class="usage-item"><span><b>Antidepressants (SSRIs/SNRIs):</b> Drugs like fluoxetine (Prozac), sertraline (Zoloft), and duloxetine (Cymbalta) can increase GI bleeding risk by up to 10–15 times when combined with ibuprofen.</span></div>

                <div class="usage-item"><span><b>Corticosteroids:</b> Taking oral steroids like prednisone with ibuprofen increases the risk of stomach ulcers and bleeding.</span></div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #22c55e;">🍎 Food-Drug Interaction</div>

            <div class="food-box">

                <span class="food-title">Taking with Food/Milk</span>

                <p>Taking ibuprofen with a meal or a glass of milk is widely recommended by the Mayo Clinic to reduce stomach irritation and upset.</p>

            </div>

            <div class="usage-list">

                <div class="usage-item">

                    <span class="usage-title">Absorption Speed:</span>

                    <span>Food can slow down how fast your body absorbs the medicine. For rapid relief (e.g., for a sudden headache), taking it on an empty stomach may be more effective. Research indicates that food can reduce the maximum concentration (Cmax) by 30%–50% and delay the time it takes to work by 30–60 minutes.</span>

                </div>

                <div class="usage-item">

                    <span class="usage-title">Total Dosage:</span>

                    <span>Interestingly, food does not change the total amount of drug absorbed by your body, just the speed at which it gets there.</span>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header">📊 Summary Table for Study</div>

            <p style="font-weight: bold; margin-bottom: 10px; color: #666;">Pharmacological Profile</p>

            <table class="summary-table">

                <thead>

                    <tr><th>Parameter</th><th>Description</th></tr>

                </thead>

                <tbody>

                    <tr><td class="param-name">Drug Class</td><td>Non-Steroidal Anti-Inflammatory Drug (NSAID); Propionic acid derivative.</td></tr>

                    <tr><td class="param-name">Mechanism</td><td>Non-selective inhibition of COX-1 and COX-2 enzymes, blocking the conversion of arachidonic acid to prostaglandins.</td></tr>

                    <tr><td class="param-name">Primary Actions</td><td>Analgesic (pain), Antipyretic (fever), Anti-inflammatory.</td></tr>

                    <tr><td class="param-name">Metabolism</td><td>Primarily hepatic via CYP2C9 and CYP2C8 enzymes.</td></tr>

                    <tr><td class="param-name">Excretion</td><td>>90% renal (urine) as inactive metabolites; ~1% unchanged.</td></tr>

                </tbody>

            </table>

        </div>



        <div class="section-divider">

            <div class="section-header">🏢 Common Brand Name (India)</div>

            <table class="summary-table">

                <thead>

                    <tr><th>Name Type</th><th>Common Names in India</th></tr>

                </thead>

                <tbody>

                    <tr><td class="param-name">Generic Name</td><td>Ibuprofen</td></tr>

                    <tr><td class="param-name">Pure Ibuprofen Brands</td><td>Brufen, Ibugesic, Ibuvon, Novigan</td></tr>

                    <tr><td class="param-name">Combination Brands (with Paracetamol)</td><td>Combiflam, Flexon, Ibugesic Plus, Ibuflamar-P</td></tr>

                </tbody>

            </table>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #0ea5e9;">💉 IV Infusion Dosing</div>

            <div class="dosing-box">

                <span class="dosing-title">General Considerations for IV Ibuprofen</span>

                <div class="usage-list">

                    <div class="usage-item"><span class="usage-title">Maximum Daily Dose:</span>There is a maximum daily amount that should not be exceeded.</div>

                    <div class="usage-item"><span class="usage-title">Administration Time:</span>The medication is typically administered over a specific period of time via infusion.</div>

                    <div class="usage-item"><span class="usage-title">Dilution:</span>The medication often requires dilution before administration. Compatible fluids are commonly used for this process.</div>

                    <div class="usage-item"><span class="usage-title">Hydration:</span>Maintaining adequate hydration is important before receiving IV ibuprofen.</div>

                    <div class="usage-item"><span class="usage-title">Contraindications:</span>IV ibuprofen is not suitable for everyone and has specific contraindications, such as in certain surgical settings or for individuals with particular allergies.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #0ea5e9;">👄 Oral Dosing</div>

            <div class="dosing-box">

                <span class="dosing-title">Pediatric Use</span>

                <p>For children, ibuprofen dosing is typically determined by weight and age. Doses can be administered at regular intervals, but it is important not to exceed the maximum recommended number of doses within a 24-hour period.</p>

                

                <span class="dosing-title">Adult & Adolescent Use</span>

                <p>For individuals aged 12 years and older, over-the-counter ibuprofen is commonly used. Tablets, capsules, and syrup formulations are available. It is important to adhere to the maximum daily dose for over-the-counter use unless otherwise directed by a healthcare professional. Prescription-strength ibuprofen may have higher maximum daily allowances but require strict medical supervision.</p>

                

                <span class="dosing-title">Important Safety Information</span>

                <div class="usage-list">

                    <div class="usage-item"><span class="usage-title">Concentration Awareness:</span>Be aware that the concentration of ibuprofen can differ significantly between infant drops and children's suspension. Using the correct measuring tool for the specific product is essential to ensure accurate dosing.</div>

                    <div class="usage-item"><span class="usage-title">Measuring Accuracy:</span>Always use the oral syringe or dosing cup provided with the medication to ensure accurate measurement. Avoid using household spoons, as they are not designed for precise medicinal dosing.</div>

                    <div class="usage-item"><span class="usage-title">Administration Guidelines:</span>Taking ibuprofen with food or milk may help to minimize the risk of stomach upset.</div>

                    <div class="usage-item"><span class="usage-title">Age Considerations:</span>Ibuprofen should not be given to infants under a certain age without consulting a healthcare professional.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #7c3aed;">💪 Intramuscular Dosing</div>

            <div class="im-box">

                <p>If a patient cannot take ibuprofen orally, the intravenous (IV) route is used in hospital settings.</p>

                <span class="im-title">Important considerations for intravenous administration of ibuprofen include:</span>

                <div class="usage-list">

                    <div class="usage-item"><span>Injectable ibuprofen must be diluted in a suitable solution before administration.</span></div>

                    <div class="usage-item"><span>The infusion is typically administered over a specific duration, which may vary depending on the patient's age and condition.</span></div>

                </div>

            </div>

        </div>



        <center style="margin-top: 50px; margin-bottom: 30px;">

            <a href="/drugs-store/allopathy" style="text-decoration: none;">

                <button style="padding: 15px 40px; cursor: pointer; background: linear-gradient(135deg, #2c3e50 0%, #000 100%); color: #fff; border: none; border-radius: 30px; font-weight: bold; font-size: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">Back to Products</button>

            </a>

        </center>

    </div>

    """

    # இந்த வரியில curly braces-ஐ கவனிங்க bro

    html = f"<!DOCTYPE html><html><head><title>Ibuprofen - Professional Profile</title></head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



def page_aspirin_detail(user, lang):

    content = f"""

    <style>

        .med-container {{ max-width: 850px; margin: 30px auto; padding: 40px; background: #fff; font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #000; }}

        .med-title {{ font-size: 2rem; font-weight: bold; margin-bottom: 25px; text-transform: uppercase; border-bottom: 3px solid #e53e3e; padding-bottom: 10px; text-align: center; color: #2c3e50; }}

        .info-label {{ font-weight: bold; margin-top: 22px; display: block; font-size: 1.1rem; color: #2c3e50; }}

        .info-text {{ margin-bottom: 15px; display: block; color: #333; }}

        .structure-box {{ text-align: center; margin: 40px 0; padding: 20px; background: #fdfdfd; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}

        .structure-img {{ max-width: 100%; height: auto; border-radius: 5px; }}

        

        .usage-list {{ margin-top: 10px; padding-left: 0; list-style-type: none; }}

        .usage-item {{ margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #eee; }}

        .usage-title {{ font-weight: bold; display: block; color: #2c3e50; }}

        

        .section-divider {{ border-top: 2px solid #eee; margin-top: 40px; padding-top: 25px; }}

        .section-header {{ font-size: 1.4rem; font-weight: bold; color: #2c3e50; margin-bottom: 15px; text-transform: uppercase; display: flex; align-items: center; }}

        

        /* Box Styles */

        .warning-box {{ background-color: #fff5f5; border-left: 5px solid #e53e3e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(229, 62, 62, 0.1); }}

        .warning-title {{ color: #c53030; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .interaction-box {{ background-color: #fffaf0; border-left: 5px solid #ed8936; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(237, 137, 54, 0.1); }}

        .interaction-title {{ color: #dd6b20; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .food-box {{ background-color: #f0fdf4; border-left: 5px solid #22c55e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(34, 197, 94, 0.1); }}

        .food-title {{ color: #15803d; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .study-box {{ background-color: #f8f9fa; border-left: 5px solid #6c757d; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(108, 117, 125, 0.1); }}

        .study-title {{ color: #495057; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .im-box {{ background-color: #f5f3ff; border-left: 5px solid #7c3aed; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(124, 58, 237, 0.1); }}



        .summary-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background-color: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}

        .summary-table th, .summary-table td {{ border: 1px solid #eee; padding: 15px; text-align: left; font-size: 0.95rem; }}

        .summary-table th {{ background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%); color: white; text-transform: uppercase; letter-spacing: 1px; }}

        .summary-table tr:nth-child(even) {{ background-color: #fcfcfc; }}

        .param-name {{ font-weight: bold; color: #2c3e50; width: 35%; background-color: #f8f9fa; }}

    </style>



    <div class="med-container">

        <div class="med-title">ASPIRIN</div>



        <div class="section-header">🧪 Chemical Structure and IUPAC Name</div>

        <span class="info-label">Parent Structure:</span>

        <span class="info-text">Benzoic acid (Benzene ring + Carboxyl group).</span>

        

        <span class="info-label">Substitution:</span>

        <span class="info-text">An acetoxy group is attached at the C-2 position.</span>



        <span class="info-label">Molecular Weight:</span>

        <span class="info-text">Approximately 180.16 g/mol.</span>



        <span class="info-label">Synthesis:</span>

        <span class="info-text">Produced by reacting salicylic acid with acetic anhydride.</span>



        <div class="structure-box">

            <img src="/static/aspirin_structure.png" class="structure-img" alt="Aspirin Structure Diagram" onerror="this.src='https://placehold.co/400x300?text=Aspirin+Structure+C9H8O4'">

            <p style="margin-top:10px; color: #666; font-size: 1.2rem;"><b>C<sub>9</sub>H<sub>8</sub>O<sub>4</sub></b></p>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff;">💊 Therapeutic Uses</div>

            <div class="usage-list">

                <div class="usage-item">

                    <span class="usage-title">Pain & Inflammation:</span>

                    <span>Relieves mild to moderate pain (headaches, toothaches, menstrual cramps) and reduces inflammation in conditions like rheumatoid arthritis.</span>

                </div>

                <div class="usage-item">

                    <span class="usage-title">Cardiovascular Health (Low-Dose):</span>

                    <ul>

                        <li><b>Prevention:</b> Daily low-dose (75-100 mg) is used to prevent heart attacks and strokes in high-risk individuals (e.g., hypertension, high cholesterol, diabetes).</li>

                        <li><b>Acute Treatment:</b> Administered immediately during a heart attack or stroke to prevent further clot formation.</li>

                        <li><b>Post-Procedure:</b> Used after cardiovascular procedures like stents (angioplasty) or bypass surgery.</li>

                    </ul>

                </div>

                <div class="usage-item">

                    <span class="usage-title">Fever Reduction:</span>

                    <span>Acts as an antipyretic, lowering high body temperatures.</span>

                </div>

                <div class="usage-item">

                    <span class="usage-title">Other Potential Benefits:</span>

                    <span>Emerging research suggests it may reduce the risk of certain cancers, such as stomach, intestinal, or breast cancer.</span>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #6f42c1;">⚠️ Adverse Drug Reaction (ADR)</div>

            <p><b>Common Adverse Reactions:</b></p>

            <div class="usage-list">

                <div class="usage-item"><span class="usage-title">Gastrointestinal (GI) Distress:</span>Indigestion, heartburn, nausea, and stomach pain are the most frequent complaints. Taking aspirin with food can often help reduce these symptoms.</div>

                <div class="usage-item"><span class="usage-title">Increased Bleeding:</span>Aspirin reduces the blood's ability to clot, leading to easier bruising, frequent nosebleeds, and longer bleeding times for minor cuts.</div>

                <div class="usage-item"><span class="usage-title">Tinnitus:</span>High doses can cause a persistent ringing or buzzing in the ears, which may indicate salicylate toxicity.</div>

            </div>

            

            <div class="warning-box">

                <span class="warning-title">Serious & Life-Threatening Risks</span>

                <div class="usage-list" style="margin-top: 10px;">

                    <div class="usage-item"><span class="usage-title">Gastrointestinal Ulcers & Hemorrhage:</span>Aspirin can cause erosions and ulcers in the stomach and intestines, potentially leading to severe internal bleeding. Warning signs include black, tarry stools or vomiting blood that looks like coffee grounds.</div>

                    <div class="usage-item"><span class="usage-title">Reye's Syndrome:</span>A rare but potentially fatal condition causing brain and liver swelling in children and teenagers, typically following a viral infection (like the flu or chickenpox).</div>

                    <div class="usage-item"><span class="usage-title">Aspirin-Exacerbated Respiratory Disease (AERD):</span>In people with asthma and nasal polyps, aspirin can trigger severe asthma attacks, wheezing, and sinus inflammation.</div>

                    <div class="usage-item"><span class="usage-title">Hemorrhagic Stroke:</span>While aspirin helps prevent clot-related strokes, it slightly increases the risk of bleeding into the brain.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ed8936;">🤝 Drug-Drug Interaction</div>

            <table class="summary-table">

                <thead>

                    <tr><th>Drug Class</th><th>Interaction Effect</th></tr>

                </thead>

                <tbody>

                    <tr><td class="param-name">Anticoagulants</td><td>Massive increase in major bleeding risk.</td></tr>

                    <tr><td class="param-name">Ibuprofen</td><td>Blocks aspirin's heart-protective benefits.</td></tr>

                    <tr><td class="param-name">SSRIs</td><td>Increases risk of stomach and internal bleeding.</td></tr>

                    <tr><td class="param-name">Methotrexate</td><td>Risk of severe, toxic buildup in the body.</td></tr>

                    <tr><td class="param-name">ACE Inhibitors</td><td>Aspirin may make these less effective for BP.</td></tr>

                </tbody>

            </table>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #22c55e;">🍎 Food-Drug Interaction</div>

            <div class="usage-list">

                <div class="usage-item">

                    <span class="usage-title">Alcohol:</span>

                    <span>Consuming alcohol—especially three or more drinks daily—while taking aspirin significantly irritates the stomach lining and increases the risk of gastrointestinal (GI) bleeding. In some cases, this can lead to life-threatening internal bleeding.</span>

                </div>

                <div class="usage-item">

                    <span class="usage-title">Anticoagulant Herbs ("The G's"):</span>

                    <span>Many common herbs possess natural blood-thinning properties. Combining these with aspirin can lead to excessive bleeding or bruising:</span>

                    <ul style="margin-top: 5px;">

                        <li><b>Garlic & Ginger:</b> Can increase antiplatelet activity, making it harder for the blood to clot.</li>

                        <li><b>Ginkgo Biloba & Ginseng:</b> Often reported to increase bleeding risk when taken with aspirin.</li>

                    </ul>

                </div>

                <div class="usage-item">

                    <span class="usage-title">Other Supplements:</span>

                    <span>High-dose Vitamin E, Omega-3 fatty acids (Fish Oil), and Turmeric may also amplify aspirin's thinning effect, heightening the risk of hemorrhage.</span>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header">📊 Summary Table for Study</div>

            

            <div class="study-box">

                <span class="study-title">The Early Gold Standard</span>

                <p><b>ISIS-2 (1988)</b></p>

                <ul>

                    <li><b>Target:</b> Patients actively having a heart attack.</li>

                    <li><b>Result:</b> Aspirin reduced 5-week vascular mortality by 23%.</li>

                    <li><b>Impact:</b> Cemented aspirin as an immediate, emergency treatment for acute MI.</li>

                </ul>

            </div>



            <div class="study-box">

                <span class="study-title">Primary Prevention in Healthy Adults</span>

                <ul>

                    <li><b>Physicians' Health Study (1989):</b> Found a 44% reduction in first heart attacks in men, though it didn't change overall death rates.</li>

                    <li><b>Women's Health Study (2005):</b> Showed aspirin was better at preventing strokes than heart attacks in women.</li>

                    <li><b>Impact:</b> Led to decades of "an aspirin a day" advice for the general public.</li>

                </ul>

            </div>



            <div class="study-box">

                <span class="study-title">The Modern Pivot: 2018 "Big Three" Trials</span>

                <p>Recent large-scale studies fundamentally changed how doctors prescribe aspirin for people without known heart disease:</p>

                <ul>

                    <li><b>ARRIVE:</b> Proved that in patients with moderate risk factors (like high BP), aspirin did not significantly reduce heart events compared to a placebo.</li>

                    <li><b>ASPREE:</b> Specifically looked at healthy adults over 70. It found no heart benefit but a significantly higher risk of major bleeding and even slightly higher mortality.</li>

                    <li><b>ASCEND:</b> Looked at adults with diabetes. While it reduced heart events by 12%, it increased major bleeding by 29%, making the "risk vs. benefit" a virtual tie.</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header">🏢 Common Brand Name (India)</div>

            <p style="font-weight: bold; margin-bottom: 10px; color: #666;">Most Popular Brands</p>

            <table class="summary-table">

                <tbody>

                    <tr>

                        <td class="param-name">Ecosprin (USV Private Limited)</td>

                        <td>The most widely prescribed brand for heart protection. It is typically available in low doses like 75 mg and 150 mg for preventing heart attacks and strokes.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Disprin (Reckitt Benckiser)</td>

                        <td>A very common household name, usually sold as a 325 mg soluble tablet. It is primarily used for quick relief from headaches, pain, and fever.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Loprin (Torrent Pharmaceuticals)</td>

                        <td>Another major brand used for cardiovascular health, often found in 75 mg and 150 mg strengths.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Delisprin (Aristo Pharmaceuticals)</td>

                        <td>Frequently prescribed for antiplatelet therapy to prevent blood clots in high-risk patients.</td>

                    </tr>

                </tbody>

            </table>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #0ea5e9;">💊 Oral Dosing</div>

            <div class="study-box" style="border-left-color: #0ea5e9; background-color: #f0f9ff;">

                <span class="study-title" style="color: #0369a1;">1. Oral Tablet Dosing</span>

                <p>Aspirin tablets are available in different concentrations for various purposes, often categorized into lower doses for cardiovascular protection and higher doses for pain or fever management.</p>

                <div class="usage-list">

                    <div class="usage-item">

                        <span class="usage-title">Low-Dose (Antiplatelet):</span>

                        <span><b>Usage:</b> Often prescribed for long-term use under medical supervision to help reduce the risk of heart attacks and strokes.</span><br>

                        <span><b>Examples (India):</b> Ecosprin 75, Loprin 75, and Delisprin.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">High-Dose (Pain/Fever Relief):</span>

                        <span><b>Usage:</b> Used for short-term relief of pain and fever.</span><br>

                        <span><b>Examples (India):</b> Disprin 325 mg (often soluble) and Ecosprin 325.</span>

                    </div>

                </div>



                <span class="study-title" style="color: #0369a1; margin-top: 20px;">2. Oral Liquids (Syrups and Drops)</span>

                <p>Aspirin liquids are generally not recommended or commonly available for children and teenagers due to the risk of Reye's syndrome, a rare but serious condition that can affect the brain and liver.</p>

                <div class="usage-list">

                    <div class="usage-item"><b>Alternatives:</b> For children’s pain or fever, healthcare professionals often recommend alternatives like Paracetamol (e.g., Crocin) or Ibuprofen (e.g., Ibugesic).</div>

                    <div class="usage-item"><b>Soluble Tablets:</b> Some aspirin, such as Disprin or Alka-Seltzer, come in effervescent form designed to be dissolved in water.</div>

                </div>



                <span class="study-title" style="color: #0369a1; margin-top: 20px;">3. Considerations by Condition</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Heart Protection:</b> Often involves a consistent, low-dose daily regimen, typically under the guidance of a physician.</div>

                    <div class="usage-item"><b>Mild Pain/Fever:</b> Involves the use of standard tablets, with the dose and frequency determined by the intensity of symptoms and professional advice.</div>

                    <div class="usage-item"><b>Acute Heart Attack:</b> In emergency situations, a specific, higher dose of chewable aspirin is sometimes advised, according to medical guidance.</div>

                    <div class="usage-item"><b>Children (<16 years):</b> Generally avoided, as noted above, due to the risk of Reye's Syndrome.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #7c3aed;">💉 IV Infusion Dosing</div>

            <div class="im-box">

                <span class="study-title" style="color: #5b21b6;">Adult IV Dosing Guidelines</span>

                <p>Intravenous (IV) aspirin, commonly formulated as Lysine Acetylsalicylate, is used in specialized clinical settings where rapid platelet inhibition is required. For acute conditions such as myocardial infarction (MI) or acute ischemic stroke, dosing is determined by a healthcare professional, often based on specific clinical protocols.</p>

                

                <span class="study-title" style="color: #5b21b6; margin-top: 15px;">Administration Method:</span>

                <div class="usage-list">

                    <div class="usage-item"><b>IV Injection:</b> Can be given as a slow injection.</div>

                    <div class="usage-item"><b>IV Infusion:</b> The medication is reconstituted and diluted in fluids such as 0.9% Sodium Chloride or 5% Glucose.</div>

                    <div class="usage-item"><b>Speed of Action:</b> IV administration achieves total platelet inhibition rapidly.</div>

                </div>



                <span class="study-title" style="color: #5b21b6; margin-top: 20px;">Pediatric IV Dosing (e.g., Kawasaki Disease):</span>

                <p>In specialized pediatric settings, IV aspirin may be used for specific conditions. Dosage is strictly determined and administered by a qualified healthcare provider.</p>

                

                <span class="study-title" style="color: #5b21b6; margin-top: 20px;">Clinical Indications for IV Route:</span>

                <p>IV aspirin is typically reserved for scenarios where oral administration is impossible or rapid action is necessary:</p>

                <div class="usage-list">

                    <div class="usage-item"><b>Rapid Platelet Blockade:</b> Required for procedures like carotid stenting.</div>

                    <div class="usage-item"><b>Inability to Swallow:</b> Used in patients with acute stroke or MI who cannot take oral medication and lack nasogastric access.</div>

                    <div class="usage-item"><b>Acute Migraine:</b> Used in tertiary referral settings for severe, refractory headaches.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #e67e22;">💪 Intramuscular Dosing</div>

            <div class="interaction-box" style="border-left-color: #e67e22;">

                <p>Aspirin is not administered via intramuscular (IM) injection. There are no commercially available IM formulations of aspirin (acetylsalicylic acid) for human use.</p>

                <span class="study-title" style="color: #c05621; margin-top: 15px;">Why IM Injection is Avoided:</span>

                <div class="usage-list">

                    <div class="usage-item"><span class="usage-title">Tissue Irritation:</span>Aspirin is highly acidic. Injecting it directly into muscle tissue would cause severe local irritation, pain, and potential tissue necrosis (cell death).</div>

                    <div class="usage-item"><span class="usage-title">Absorption Issues:</span>Aspirin is a pro-drug that needs to be converted into its active form (salicylate). The muscle does not provide the optimal environment for this conversion or consistent absorption.</div>

                    <div class="usage-item"><span class="usage-title">Bleeding Risk:</span>Because aspirin is an antiplatelet (blood thinner), an IM injection carries a high risk of causing a hematoma (a large, painful bruise or collection of blood) within the muscle.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #10b981;">👴 Geriatric Dose Adjustment</div>

            <div class="study-box" style="border-left-color: #10b981;">

                <span class="study-title" style="color: #047857;">1. Primary Prevention (No History of Heart Disease)</span>

                <p>For adults 60–65+ who have never had a heart attack or stroke, the current medical consensus has shifted away from routine aspirin use.</p>

                <div class="usage-list">

                    <div class="usage-item"><b>Ages 60–69:</b> The USPSTF recommends against starting a daily aspirin unless there is a very high cardiovascular risk and low bleeding risk.</div>

                    <div class="usage-item"><b>Ages 70+:</b> Major medical societies (AHA/ACC) strongly recommend against routine low-dose aspirin for primary prevention, as the risk of serious hemorrhage is nearly doubled in this age group.</div>

                    <div class="usage-item"><b>Anemia Risk:</b> Recent studies found that even low-dose aspirin (100 mg) increases the risk of anemia by 20% in seniors due to slow, occult GI blood loss.</div>

                </div>



                <span class="study-title" style="color: #047857; margin-top: 20px;">2. Secondary Prevention (History of Heart Disease)</span>

                <p>If you have already been diagnosed with a heart condition (e.g., prior MI, stroke, or stent), the benefits of aspirin usually far outweigh the bleeding risks, regardless of age.</p>

                <div class="usage-list">

                    <div class="usage-item"><b>Standard Dose:</b> 75 mg to 100 mg daily (81 mg is the standard in the US).</div>

                    <div class="usage-item"><b>Dose Adjustment:</b> Clinical trials like ADAPTABLE confirmed that for secondary prevention, a dose of 81 mg is as effective as 325 mg but carries a lower risk of bleeding.</div>

                    <div class="usage-item"><b>Stomach Protection:</b> For patients over 75, many doctors now co-prescribe a Proton Pump Inhibitor (PPI) like Omeprazole to reduce the 70–90% risk of upper GI bleeding.</div>

                </div>



                <table class="summary-table" style="margin-top: 20px;">

                    <thead>

                        <tr style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">

                            <th>Age Group</th>

                            <th>Primary Prevention (Healthy)</th>

                            <th>Secondary Prevention (Heart History)</th>

                        </tr>

                    </thead>

                    <tbody>

                        <tr>

                            <td><b>60–69</b></td>

                            <td>Generally not recommended.</td>

                            <td>Strongly recommended (75–100 mg).</td>

                        </tr>

                        <tr>

                            <td><b>70–75</b></td>

                            <td>Routine use not recommended.</td>

                            <td>Strongly recommended (75–100 mg).</td>

                        </tr>

                        <tr>

                            <td><b>75+</b></td>

                            <td>Avoid; bleeding risk is too high.</td>

                            <td>Use with PPI for stomach protection.</td>

                        </tr>

                    </tbody>

                </table>

            </div>

        </div>



        <center style="margin-top: 50px; margin-bottom: 30px;">

            <a href="/drugs-store/allopathy" style="text-decoration: none;">

                <button style="padding: 15px 40px; cursor: pointer; background: linear-gradient(135deg, #2c3e50 0%, #000 100%); color: #fff; border: none; border-radius: 30px; font-weight: bold; font-size: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">Back to Products</button>

            </a>

        </center>

    </div>

    """

    html = f"<!DOCTYPE html><html><head><title>Aspirin - Professional Profile</title></head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



def page_diclofenac_detail(user, lang):

    content = f"""

    <style>

        .med-container {{ max-width: 850px; margin: 30px auto; padding: 40px; background: #fff; font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #000; }}

        .med-title {{ font-size: 2rem; font-weight: bold; margin-bottom: 25px; text-transform: uppercase; border-bottom: 3px solid #ff9800; padding-bottom: 10px; text-align: center; color: #2c3e50; }}

        .info-label {{ font-weight: bold; margin-top: 22px; display: block; font-size: 1.1rem; color: #2c3e50; }}

        .info-text {{ margin-bottom: 15px; display: block; color: #333; }}

        .structure-box {{ text-align: center; margin: 40px 0; padding: 20px; background: #fdfdfd; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}

        .structure-img {{ max-width: 100%; height: auto; border-radius: 5px; }}

        

        .usage-list {{ margin-top: 10px; padding-left: 0; list-style-type: none; }}

        .usage-item {{ margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #eee; }}

        .usage-title {{ font-weight: bold; display: block; color: #2c3e50; }}

        

        .section-divider {{ border-top: 2px solid #eee; margin-top: 40px; padding-top: 25px; }}

        .section-header {{ font-size: 1.4rem; font-weight: bold; color: #2c3e50; margin-bottom: 15px; text-transform: uppercase; display: flex; align-items: center; }}

        

        /* Box Styles */

        .warning-box {{ background-color: #fff5f5; border-left: 5px solid #e53e3e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(229, 62, 62, 0.1); }}

        .warning-title {{ color: #c53030; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .interaction-box {{ background-color: #fffaf0; border-left: 5px solid #ed8936; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(237, 137, 54, 0.1); }}

        .interaction-title {{ color: #dd6b20; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .food-box {{ background-color: #f0fdf4; border-left: 5px solid #22c55e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(34, 197, 94, 0.1); }}

        .food-title {{ color: #15803d; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .study-box {{ background-color: #f8f9fa; border-left: 5px solid #6c757d; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(108, 117, 125, 0.1); }}

        .study-title {{ color: #495057; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .im-box {{ background-color: #f5f3ff; border-left: 5px solid #7c3aed; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(124, 58, 237, 0.1); }}



        .summary-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background-color: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}

        .summary-table th, .summary-table td {{ border: 1px solid #eee; padding: 15px; text-align: left; font-size: 0.95rem; }}

        .summary-table th {{ background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%); color: white; text-transform: uppercase; letter-spacing: 1px; }}

        .summary-table tr:nth-child(even) {{ background-color: #fcfcfc; }}

        .param-name {{ font-weight: bold; color: #2c3e50; width: 35%; background-color: #f8f9fa; }}

    </style>



    <div class="med-container">

        <div class="med-title">DICLOFENAC</div>



        <div class="section-header">🧪 Chemical Structure and IUPAC Name</div>

        <span class="info-label">IUPAC Name:</span>

        <span class="info-text">2-[2-(2,6-dichloroanilino)phenyl]acetic acid.</span>

        

        <span class="info-label">Alternative IUPAC Name:</span>

        <span class="info-text">2-((2,6-dichlorophenyl)amino) benzeneacetic acid.</span>



        <span class="info-label">Molecular Formula:</span>

        <span class="info-text">C<sub>14</sub>H<sub>11</sub>Cl<sub>2</sub>NO<sub>2</sub></span>



        <span class="info-label">Molecular Weight:</span>

        <span class="info-text">296.15 g/mol.</span>

        

        <span class="info-label">CAS Registry Number:</span>

        <span class="info-text">15307-86-5.</span>



        <div class="structure-box">

            <img src="/static/diclofenac_structure.png" class="structure-img" alt="Diclofenac Structure Diagram" onerror="this.src='https://placehold.co/400x300?text=Diclofenac+Structure'">

            <p style="margin-top:10px; color: #666; font-size: 1.2rem;"><b>diclofenac</b></p>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff;">💊 Therapeutic Uses</div>

            <div class="usage-list">

                <div class="usage-item">

                    <span class="usage-title">Arthritis Management:</span>

                    <span>It is widely prescribed to relieve pain, swelling, and joint stiffness caused by osteoarthritis, rheumatoid arthritis, and ankylosing spondylitis.</span>

                </div>

                <div class="usage-item">

                    <span class="usage-title">Acute Pain Relief:</span>

                    <span>Effective for moderate to severe pain from migraines, dental surgery, and post-operative recovery.</span>

                </div>

                <div class="usage-item">

                    <span class="usage-title">Musculoskeletal Disorders:</span>

                    <span>Used to treat strains, sprains, back pain, and inflammatory conditions like bursitis and tendinitis.</span>

                </div>

                <div class="usage-item">

                    <span class="usage-title">Menstrual Pain:</span>

                    <span>Alleviates cramps and discomfort associated with primary dysmenorrhea.</span>

                </div>

                <div class="usage-item">

                    <span class="usage-title">Ophthalmic Uses:</span>

                    <span>Eye drop formulations treat post-operative inflammation after cataract surgery and manage pain from corneal abrasions.</span>

                </div>

                <div class="usage-item">

                    <span class="usage-title">Dermatological Conditions:</span>

                    <span>A 3% topical gel is specifically indicated for actinic keratosis, a scaly skin condition caused by sun damage.</span>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #6f42c1;">⚠️ Adverse Drug Reaction (ADR)</div>

            <p><b>Common Adverse Reactions (affect 1% to 10% of patients):</b></p>

            <div class="usage-list">

                <div class="usage-item"><span class="usage-title">Gastrointestinal:</span>Nausea, vomiting, diarrhea, constipation, gas (flatulence), and abdominal pain or cramps.</div>

                <div class="usage-item"><span class="usage-title">Central Nervous System:</span>Headaches and dizziness are frequently reported.</div>

                <div class="usage-item"><span class="usage-title">Dermatological:</span>Mild skin rash, itching (pruritus), and increased sweating.</div>

                <div class="usage-item"><span class="usage-title">Other:</span>Tinnitus (ringing in the ears) and fluid retention leading to edema.</div>

            </div>

            

            <div class="warning-box">

                <span class="warning-title">Serious & Life-Threatening Reactions (FDA Boxed Warnings)</span>

                <div class="usage-list" style="margin-top: 10px;">

                    <div class="usage-item"><span class="usage-title">Cardiovascular Events:</span>Increased risk of serious thrombotic events, including heart attack and stroke, which can be fatal. This risk may increase with higher doses or long-term use.</div>

                    <div class="usage-item"><span class="usage-title">Gastrointestinal Complications:</span>Serious risk of bleeding, ulceration, and perforation of the stomach or intestines. These can occur at any time without warning.</div>

                    <div class="usage-item"><span class="usage-title">Hepatotoxicity:</span>While rare, diclofenac can cause clinically apparent liver injury, including liver failure or hepatitis. Elevations in liver enzymes occur in up to 15% of chronic users.</div>

                    <div class="usage-item"><span class="usage-title">Renal Damage:</span>Long-term use can lead to acute kidney injury, renal papillary necrosis, or hyperkalemia, particularly in elderly patients or those with existing kidney issues.</div>

                    <div class="usage-item"><span class="usage-title">Severe Skin Reactions:</span>Potential for fatal conditions like Stevens-Johnson Syndrome (SJS) and Toxic Epidermal Necrolysis (TEN).</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ed8936;">🤝 Drug-Drug Interaction</div>

            <div class="interaction-box">

                <div class="usage-list">

                    <div class="usage-item">

                        <span class="usage-title">Anticoagulants & Antiplatelets:</span>

                        <span>Drugs like warfarin (Coumadin), rivaroxaban (Xarelto), apixaban (Eliquis), and clopidogrel (Plavix) have a synergistic effect with diclofenac, dramatically increasing the risk of life-threatening gastrointestinal bleeding.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Methotrexate:</span>

                        <span>Diclofenac reduces the renal clearance of methotrexate, which can lead to toxic accumulation and potentially fatal outcomes.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Lithium:</span>

                        <span>It can increase lithium levels in the blood to toxic ranges by reducing renal excretion.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Cyclosporine & Tacrolimus:</span>

                        <span>These immunosuppressants, when taken with diclofenac, carry a severely elevated risk of nephrotoxicity (kidney damage).</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">The "Triple Whammy":</span>

                        <span>Taking diclofenac simultaneously with ACE inhibitors/ARBs (e.g., lisinopril, losartan) and diuretics (e.g., furosemide) creates an extremely high risk for acute kidney injury.</span>

                    </div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #22c55e;">🍎 Food-Drug Interaction</div>

            <div class="food-box">

                <div class="usage-list">

                    <div class="usage-item">

                        <span class="usage-title">Delayed Onset:</span>

                        <span>Taking diclofenac with a meal can delay the onset of absorption by 1 to 4.5 hours. For enteric-coated tablets, this delay can sometimes extend up to 12 hours.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Reduced Peak Levels:</span>

                        <span>Food can reduce peak plasma levels (Cmax) by approximately 20% to 50%. This is why doctors may recommend taking it on an empty stomach when rapid relief is needed (e.g., for migraines or acute injury).</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Consistency of Effect:</span>

                        <span>For chronic conditions like arthritis, the total exposure (AUC) remains similar whether taken with or without food, so long-term efficacy is generally unaffected.</span>

                    </div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header">📊 Summary Table for Study</div>

            <table class="summary-table">

                <tbody>

                    <tr>

                        <td class="param-name">Comparative Efficacy (Oral)</td>

                        <td>A large-scale network meta-analysis of over 146,000 patients found that diclofenac 150 mg/day was more effective for pain relief than celecoxib 200 mg, naproxen 1,000 mg, and ibuprofen 2,400 mg.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Topical vs. Oral</td>

                        <td>Studies indicate that topical diclofenac (1.5% solution or 1% gel) provides pain relief equivalent to oral doses for knee osteoarthritis but reduces GI adverse events by nearly 70% (approximately 6.5% vs. 23.8% for oral).</td>

                    </tr>

                    <tr>

                        <td class="param-name">Stiffness and Function</td>

                        <td>In elderly patients with knee osteoarthritis, diclofenac significantly improved WOMAC scores for stiffness and physical function, showing higher efficacy in these specific metrics than acetaminophen and several other NSAIDs.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Acute Pain (Dental)</td>

                        <td>Diclofenac potassium has been shown to be superior to naproxen sodium and etodolac in reducing post-operative swelling following third molar extraction, while providing similar levels of pain control.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Short-Term Relief</td>

                        <td>Diclofenac patches deliver the most pronounced short-term relief within the first 1-2 weeks of treatment compared to gels or solutions, which tend to show more sustained long-term efficacy (8-12 weeks).</td>

                    </tr>

                </tbody>

            </table>

        </div>



        <div class="section-divider">

            <div class="section-header">🏢 Common Brand Name (India)</div>

            <div class="study-box">

                <ul style="line-height: 1.8; color: #555;">

                    <li><b>Voveran (Novartis/Abbott/Dr. Reddy's):</b> One of the most widely recognized and prescribed brands in India. Available as Voveran-D (Dispersible tablets), Voveran SR (Sustained-release tablets), Voveran Emulgel (Topical gel), and Voveran AQ (Aqueous injection).</li>

                    <li><b>Reactin (Cipla):</b> A popular choice for rapid action, often containing diclofenac potassium. Available as Reactin-100 SR and standard tablets.</li>

                    <li><b>Dicloran (Torrent Pharmaceuticals/Lekar Pharma):</b> A long-standing brand trusted for both oral and injectable forms.</li>

                    <li><b>Oxalgin (Zydus Cadila):</b> Widely used in clinical practice for managing musculoskeletal pain.</li>

                    <li><b>Diclomol (Win-Medicare):</b> Extremely common combination of diclofenac + paracetamol, often used for dental pain and minor injuries.</li>

                    <li><b>Relaxyl (Franco-Indian Pharmaceuticals):</b> Frequently used for its injectable and topical forms in hospital settings.</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #0ea5e9;">💉 IV Infusion Dosing</div>

            <div class="study-box" style="border-left-color: #0ea5e9; background-color: #f0f9ff;">

                <span class="study-title" style="color: #0369a1;">1. Traditional IV Infusion (e.g., Voltarol/Voveran)</span>

                <p>Traditional ampoules are not designed for direct injection and must be diluted and buffered to prevent venous irritation and thrombosis.</p>

                <div class="usage-list">

                    <div class="usage-item"><b>Administration:</b> Generally administered via slow infusion.</div>

                    <div class="usage-item"><b>Preparation:</b> Requires dilution in 0.9% Sodium Chloride or 5% Glucose. <b>CRITICAL:</b> The solution must be buffered with sodium bicarbonate immediately before adding the diclofenac.</div>

                    <div class="usage-item"><b>Administration Rate:</b> Infusion is typically given slowly to minimize risks.</div>

                    <div class="usage-item"><b>Maximum Amount:</b> Strict maximum daily limits apply to reduce adverse effects.</div>

                </div>



                <span class="study-title" style="color: #0369a1; margin-top: 20px;">2. IV Bolus Injection (e.g., Dyloject)</span>

                <p>Newer formulations use hydroxypropyl-β-cyclodextrin (HPβCD) to improve solubility, allowing for rapid administration without dilution.</p>

                <div class="usage-list">

                    <div class="usage-item"><b>Administration:</b> Designed for direct IV bolus injection.</div>

                    <div class="usage-item"><b>Administration Rate:</b> Injected over a specific, short period.</div>

                    <div class="usage-item"><b>Frequency/Maximum:</b> Administered at intervals as directed. Total daily administration is limited to avoid toxicity.</div>

                </div>



                <span class="study-title" style="color: #0369a1; margin-top: 20px;">3. Post-Operative Usage</span>

                <p>For the management of pain after surgery, a specific protocol is often followed:</p>

                <div class="usage-list">

                    <div class="usage-item"><b>Initiation:</b> A loading dose may be administered via infusion shortly after surgery.</div>

                    <div class="usage-item"><b>Maintenance:</b> This may be followed by a controlled infusion, ensuring total daily limits are not exceeded.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff;">💊 Oral Dosing</div>

            <div class="study-box" style="border-left-color: #007bff;">

                <span class="study-title">General Considerations for Oral Diclofenac</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Conditions Treated:</b> Oral formulations are used for managing symptoms associated with conditions such as osteoarthritis, rheumatoid arthritis, ankylosing spondylitis, and acute pain or primary dysmenorrhea.</div>

                    <div class="usage-item"><b>Formulations:</b> Diclofenac potassium is often used for rapid onset, while diclofenac sodium is common in delayed-release or extended-release formulations.</div>

                    <div class="usage-item"><b>Administration:</b> To reduce stomach irritation, delayed-release tablets are often taken with or after food. Immediate-release formulations or oral solutions may be taken on an empty stomach for faster absorption.</div>

                    <div class="usage-item"><b>Usage Guidelines:</b> Tablets and capsules should typically be swallowed whole and not crushed, split, or chewed.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #e67e22;">💪 Intramuscular Dosing</div>

            <div class="interaction-box" style="border-left-color: #e67e22;">

                <div class="usage-list">

                    <div class="usage-item"><span class="usage-title">Administration Method:</span>The medication is generally given as a deep intramuscular injection, typically into the upper outer quadrant of the buttock.</div>

                    <div class="usage-item"><span class="usage-title">Severe Cases:</span>For severe pain management, such as renal colic, healthcare providers may determine if a second injection is appropriate, typically allowing a significant interval between doses.</div>

                    <div class="usage-item"><span class="usage-title">Duration:</span>Treatment is typically intended for short-term use, generally limited to a few days. If further pain relief is required, practitioners often transition patients to oral or rectal forms.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #10b981;">👴 Geriatric Dose Adjustment</div>

            <div class="study-box" style="border-left-color: #10b981;">

                <span class="study-title" style="color: #047857;">Critical Risks for 65+ Population</span>

                <p>Geriatric patients are at an increased risk for serious NSAID-associated events:</p>

                <div class="usage-list">

                    <div class="usage-item"><b>Gastrointestinal (GI):</b> Higher risk of fatal GI bleeding, ulcers, and stomach perforation, even without warning symptoms.</div>

                    <div class="usage-item"><b>Cardiovascular:</b> Increased likelihood of heart attack, stroke, and new or worsening heart failure.</div>

                    <div class="usage-item"><b>Renal (Kidney):</b> Heightened risk of acute kidney injury, particularly in those also taking diuretics or ACE inhibitors.</div>

                </div>



                <span class="study-title" style="color: #047857; margin-top: 20px;">Monitoring and Precautions</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Comorbidities:</b> Diclofenac is listed on the Beers Criteria (a list of medications that may be inappropriate for older adults) and should be avoided or used with extreme caution in seniors with existing heart, stomach, or kidney issues.</div>

                    <div class="usage-item"><b>Routine Lab Tests:</b> If used long-term, healthcare providers should periodically monitor renal function, hepatic enzymes, and blood pressure.</div>

                    <div class="usage-item"><b>Gastroprotection:</b> Doctors may consider co-prescribing a proton pump inhibitor (PPI) to reduce the risk of stomach ulcers.</div>

                </div>

            </div>

        </div>



        <center style="margin-top: 50px; margin-bottom: 30px;">

            <a href="/drugs-store/allopathy" style="text-decoration: none;">

                <button style="padding: 15px 40px; cursor: pointer; background: linear-gradient(135deg, #2c3e50 0%, #000 100%); color: #fff; border: none; border-radius: 30px; font-weight: bold; font-size: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">Back to Products</button>

            </a>

        </center>

    </div>

    """

    html = f"<!DOCTYPE html><html><head><title>Diclofenac - Professional Profile</title></head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



def page_amoxicillin_detail(user, lang):

    content = f"""

    <style>

        .med-container {{ max-width: 850px; margin: 30px auto; padding: 40px; background: #fff; font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #000; }}

        .med-title {{ font-size: 2rem; font-weight: bold; margin-bottom: 25px; text-transform: uppercase; border-bottom: 3px solid #20c997; padding-bottom: 10px; text-align: center; color: #2c3e50; }}

        .info-label {{ font-weight: bold; margin-top: 22px; display: block; font-size: 1.1rem; color: #2c3e50; }}

        .info-text {{ margin-bottom: 15px; display: block; color: #333; }}

        .structure-box {{ text-align: center; margin: 40px 0; padding: 20px; background: #fdfdfd; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}

        .structure-img {{ max-width: 100%; height: auto; border-radius: 5px; }}

        

        .usage-list {{ margin-top: 10px; padding-left: 0; list-style-type: none; }}

        .usage-item {{ margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #eee; }}

        .usage-title {{ font-weight: bold; display: block; color: #2c3e50; }}

        

        .section-divider {{ border-top: 2px solid #eee; margin-top: 40px; padding-top: 25px; }}

        .section-header {{ font-size: 1.4rem; font-weight: bold; color: #2c3e50; margin-bottom: 15px; text-transform: uppercase; display: flex; align-items: center; }}

        

        /* Box Styles */

        .warning-box {{ background-color: #fff5f5; border-left: 5px solid #e53e3e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(229, 62, 62, 0.1); }}

        .warning-title {{ color: #c53030; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .interaction-box {{ background-color: #fffaf0; border-left: 5px solid #ed8936; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(237, 137, 54, 0.1); }}

        .interaction-title {{ color: #dd6b20; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .food-box {{ background-color: #f0fdf4; border-left: 5px solid #22c55e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(34, 197, 94, 0.1); }}

        .food-title {{ color: #15803d; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .study-box {{ background-color: #f8f9fa; border-left: 5px solid #6c757d; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(108, 117, 125, 0.1); }}

        .study-title {{ color: #495057; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .im-box {{ background-color: #f5f3ff; border-left: 5px solid #7c3aed; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(124, 58, 237, 0.1); }}



        .summary-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background-color: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}

        .summary-table th, .summary-table td {{ border: 1px solid #eee; padding: 15px; text-align: left; font-size: 0.95rem; }}

        .summary-table th {{ background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%); color: white; text-transform: uppercase; letter-spacing: 1px; }}

        .summary-table tr:nth-child(even) {{ background-color: #fcfcfc; }}

        .param-name {{ font-weight: bold; color: #2c3e50; width: 35%; background-color: #f8f9fa; }}

    </style>



    <div class="med-container">

        <div class="med-title">AMOXICILLIN</div>



        <div class="section-header">🧪 Chemical Structure and Properties</div>

        

        <table class="summary-table">

            <thead>

                <tr>

                    <th>Property</th>

                    <th>Value (Anhydrous)</th>

                    <th>Value (Trihydrate)</th>

                </tr>

            </thead>

            <tbody>

                <tr>

                    <td class="param-name">Molecular Weight</td>

                    <td>365.41 g/mol</td>

                    <td>419.45 g/mol</td>

                </tr>

                <tr>

                    <td class="param-name">Melting Point</td>

                    <td>194 °C</td>

                    <td>—</td>

                </tr>

                <tr>

                    <td class="param-name">Appearance</td>

                    <td>White to off-white crystalline powder</td>

                    <td>White, practically odorless powder</td>

                </tr>

                <tr>

                    <td class="param-name">Solubility</td>

                    <td>Soluble in water, methanol, and ethanol</td>

                    <td>Slightly soluble in water and methanol</td>

                </tr>

                <tr>

                    <td class="param-name">pKa</td>

                    <td>2.4 (acidic), 9.6 (basic)</td>

                    <td>2.6 (acidic)</td>

                </tr>

            </tbody>

        </table>



        <div class="structure-box">

            <img src="/static/amoxicillin_structure.png" class="structure-img" alt="Amoxicillin Structure" onerror="this.src='https://placehold.co/400x300?text=Amoxicillin+Structure'">

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff;">💊 Therapeutic Uses</div>

            <div class="usage-list">

                <div class="usage-item">

                    <span class="usage-title">Ear, Nose, and Throat (ENT) Infections:</span>

                    <span>Effectively treats tonsillitis, pharyngitis, and acute otitis media (middle ear infections), particularly in children.</span>

                </div>

                <div class="usage-item">

                    <span class="usage-title">Respiratory Tract Infections:</span>

                    <span>Used for community-acquired pneumonia, bronchitis, and acute bacterial sinusitis.</span>

                </div>

                <div class="usage-item">

                    <span class="usage-title">Genitourinary Tract Infections:</span>

                    <span>Prescribed for urinary tract infections (UTIs) caused by organisms like E. coli or P. mirabilis.</span>

                </div>

                <div class="usage-item">

                    <span class="usage-title">Skin and Soft Tissue Infections:</span>

                    <span>Treats conditions such as cellulitis and impetigo.</span>

                </div>

                <div class="usage-item">

                    <span class="usage-title">Helicobacter pylori Eradication:</span>

                    <span>Administered as part of a triple therapy (with clarithromycin and a proton pump inhibitor) to reduce the risk of duodenal ulcer recurrence.</span>

                </div>

                <div class="usage-item">

                    <span class="usage-title">Acute Uncomplicated Gonorrhea:</span>

                    <span>Indicated for anogenital and urethral infections.</span>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #6f42c1;">⚠️ Adverse Drug Reaction (ADR)</div>

            <div class="usage-list">

                <div class="usage-item"><span class="usage-title">Gastrointestinal:</span>Nausea, vomiting, and diarrhea are the most frequently reported side effects. Stomach pain or discomfort may also occur.</div>

                <div class="usage-item"><span class="usage-title">Dermatological:</span>A mild skin rash is common, especially in children (5–10%).</div>

                <div class="usage-item"><span class="usage-title">Neurological:</span>Headaches are frequently noted.</div>

                <div class="usage-item"><span class="usage-title">Infections:</span>Disruption of normal flora can lead to vaginal yeast infections (candidiasis) or oral thrush.</div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ed8936;">🤝 Drug-Drug Interaction</div>

            <div class="interaction-box">

                <div class="usage-list">

                    <div class="usage-item">

                        <span class="usage-title">Methotrexate:</span>

                        <span>Amoxicillin can reduce the renal clearance of methotrexate, leading to increased blood levels and potential toxicity. Symptoms of toxicity include nausea, vomiting, mouth ulcers, and low blood cell counts.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Warfarin (and other Anticoagulants):</span>

                        <span>Taking amoxicillin while on warfarin or other blood thinners can increase the risk of bleeding. This is largely due to the antibiotic's effect on gut bacteria that produce Vitamin K, which is essential for blood clotting.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Probenecid:</span>

                        <span>This medication (often used for gout) reduces the renal tubular secretion of amoxicillin, which increases amoxicillin blood levels. While this can sometimes be used therapeutically to maintain higher antibiotic levels, it also increases the risk of side effects.</span>

                    </div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #22c55e;">🍎 Food-Drug Interaction</div>

            <div class="food-box">

                <div class="usage-list">

                    <div class="usage-item">

                        <span class="usage-title">Stomach Upset Management:</span>

                        <span>Although it can be taken on an empty stomach, taking amoxicillin with a meal or snack is highly recommended to reduce common gastrointestinal side effects like nausea or abdominal pain.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Dairy Compatibility:</span>

                        <span>You can safely consume milk, yogurt, and cheese with amoxicillin. Unlike tetracyclines, calcium does not interfere with its effectiveness.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Liquid Forms for Children:</span>

                        <span>If using the oral suspension, it can be mixed with formula, milk, or fruit juice to improve taste, provided the entire mixture is consumed immediately.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Alcohol:</span>

                        <span>While there is no direct chemical interaction that makes amoxicillin dangerous with alcohol, avoiding or limiting alcohol is advised as it can weaken the immune system and worsen nausea or dehydration.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Guar Gum:</span>

                        <span>High amounts of guar gum (a fiber found in some processed foods and supplements) may reduce the absorption of amoxicillin. It is best to space them two hours apart.</span>

                    </div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header">📊 Summary Table for Study</div>

            <div class="study-box">

                <div class="usage-list">

                    <div class="usage-item"><b>Stability:</b> Amoxicillin is acid-stable, allowing for effective oral administration despite gastric acid.</div>

                    <div class="usage-item"><b>Resistance:</b> Susceptible to Beta-lactamase enzymes; often combined with clavulanic acid to broaden its spectrum.</div>

                    <div class="usage-item"><b>Special Populations:</b> Dosage adjustment is required for patients with severe renal impairment.</div>

                    <div class="usage-item"><b>Laboratory Interference:</b> Can cause false-positive urine glucose results when using certain copper reduction tests.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header">🏢 Common Brand Name (India)</div>

            <div class="study-box">

                <ul style="line-height: 1.8; color: #555;">

                    <li><b>Mox (Sun Pharmaceutical Industries Ltd.):</b> One of the oldest and most recognized brands in the country.</li>

                    <li><b>Novamox (Cipla Ltd.):</b> Widely prescribed for ENT and respiratory infections.</li>

                    <li><b>Almox (Alkem Laboratories Ltd.):</b> Known for being a cost-effective standalone option.</li>

                    <li><b>Cipmox (Cipla Ltd.):</b> Often used for pediatric patients in syrup form.</li>

                    <li><b>Wymox (Abbott Healthcare):</b> Frequently used for typhoid and dental infections.</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #0ea5e9;">💉 IV Infusion Dosing</div>

            <div class="study-box" style="border-left-color: #0ea5e9; background-color: #f0f9ff;">

                <div class="usage-list">

                    <div class="usage-item"><b>Administration Methods:</b> The medication can be given as a slow injection or an intermittent infusion, depending on the dose and clinical setting.</div>

                    <div class="usage-item"><b>Preparation:</b> Reconstitution is typically done using 0.9% Sodium Chloride or Water for Injections.</div>

                    <div class="usage-item"><b>Stability:</b> Amoxicillin is known to be less stable in glucose-containing fluids, necessitating rapid administration if glucose solutions are used.</div>

                    <div class="usage-item"><b>Monitoring:</b> The frequency of dosing and total daily amount is adjusted by healthcare professionals based on the severity of the infection and the patient's renal function.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff;">💊 Oral Dosing</div>

            <div class="study-box" style="border-left-color: #007bff;">

                <div class="usage-list">

                    <div class="usage-item"><b>Adult Dosage (Age 18+ or weight ≥ 40 kg):</b> Dosage for adults generally depends on the severity of the infection and the specific condition being treated, with frequencies typically ranging from every 8 to 12 hours.</div>

                    <div class="usage-item"><b>Pediatric Dosage (Weight < 40 kg):</b> Children's doses are typically determined by weight (mg/kg/day) and are calculated by a pediatrician or healthcare provider.</div>

                    <div class="usage-item"><b>Administration:</b> Amoxicillin can generally be taken with or without food, though taking it with food may reduce potential stomach upset.</div>

                    <div class="usage-item"><b>Duration:</b> It is essential to complete the full course of treatment as prescribed, even if symptoms improve, to ensure the infection is fully treated and to prevent antibiotic resistance.</div>

                    <div class="usage-item"><b>Special Considerations:</b> Dosage adjustments may be necessary for individuals with renal impairment.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #e67e22;">💪 Intramuscular Dosing Overview</div>

            <table class="summary-table">

                <thead>

                    <tr style="background: linear-gradient(135deg, #e67e22 0%, #d35400 100%);">

                        <th>Feature</th>

                        <th>Oral</th>

                        <th>Intramuscular (IM)</th>

                        <th>Intravenous (IV)</th>

                    </tr>

                </thead>

                <tbody>

                    <tr>

                        <td class="param-name">Bioavailability</td>

                        <td>~70–90%</td>

                        <td>100%</td>

                        <td>100%</td>

                    </tr>

                    <tr>

                        <td class="param-name">Peak Concentration</td>

                        <td>1–2 hours</td>

                        <td>~30 minutes</td>

                        <td>Immediate.</td>

                    </tr>

                </tbody>

            </table>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #10b981;">👴 Geriatric Dose Adjustment</div>

            <div class="study-box" style="border-left-color: #10b981;">

                <span class="study-title" style="color: #047857;">Geriatric Dosing Considerations:</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Renal Function Assessment:</b> Amoxicillin clearance is primarily renal. Because kidney function often declines with age, clinicians base dosage adjustments on the patient's estimated glomerular filtration rate (eGFR) or creatinine clearance, rather than age alone.</div>

                    <div class="usage-item"><b>Dosage Adjustment:</b> For patients with significant renal impairment, lower doses or extended dosing intervals are typically required to prevent accumulation.</div>

                    <div class="usage-item"><b>Monitoring:</b> Older adults may be more sensitive to side effects like diarrhea, and monitoring is recommended for potential drug-drug interactions, particularly with medications like warfarin or methotrexate.</div>

                </div>



                <span class="study-title" style="color: #047857; margin-top: 20px;">General Renal Considerations (Age 65+):</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Normal/Mildly Reduced Function:</b> Often requires no adjustment from standard adult dosing.</div>

                    <div class="usage-item"><b>Moderate to Severe Impairment:</b> Requires careful adjustment based on the specific GFR/CrCl, as outlined in clinical guidelines.</div>

                    <div class="usage-item"><b>Hemodialysis:</b> Requires specific, adjusted dosing, often including supplemental doses.</div>

                </div>

            </div>

        </div>



        <center style="margin-top: 50px; margin-bottom: 30px;">

            <a href="/drugs-store/allopathy" style="text-decoration: none;">

                <button style="padding: 15px 40px; cursor: pointer; background: linear-gradient(135deg, #2c3e50 0%, #000 100%); color: #fff; border: none; border-radius: 30px; font-weight: bold; font-size: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">Back to Products</button>

            </a>

        </center>

    </div>

    """

    html = f"<!DOCTYPE html><html><head><title>Amoxicillin - Professional Profile</title></head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



def page_morphine_detail(user, lang):

    content = f"""

    <style>

        .med-container {{ max-width: 850px; margin: 30px auto; padding: 40px; background: #fff; font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #000; }}

        .med-title {{ font-size: 2rem; font-weight: bold; margin-bottom: 25px; text-transform: uppercase; border-bottom: 3px solid #6a1b9a; padding-bottom: 10px; text-align: center; color: #2c3e50; }}

        .info-label {{ font-weight: bold; margin-top: 22px; display: block; font-size: 1.1rem; color: #2c3e50; }}

        .info-text {{ margin-bottom: 15px; display: block; color: #333; }}

        .structure-box {{ text-align: center; margin: 40px 0; padding: 20px; background: #fdfdfd; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}

        .structure-img {{ max-width: 100%; height: auto; border-radius: 5px; }}

        

        .usage-list {{ margin-top: 10px; padding-left: 0; list-style-type: none; }}

        .usage-item {{ margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #eee; }}

        .usage-title {{ font-weight: bold; display: block; color: #2c3e50; }}

        

        .section-divider {{ border-top: 2px solid #eee; margin-top: 40px; padding-top: 25px; }}

        .section-header {{ font-size: 1.4rem; font-weight: bold; color: #2c3e50; margin-bottom: 15px; text-transform: uppercase; display: flex; align-items: center; }}

        

        /* Box Styles */

        .warning-box {{ background-color: #fff5f5; border-left: 5px solid #e53e3e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(229, 62, 62, 0.1); }}

        .warning-title {{ color: #c53030; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .interaction-box {{ background-color: #fffaf0; border-left: 5px solid #ed8936; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(237, 137, 54, 0.1); }}

        .food-box {{ background-color: #f0fdf4; border-left: 5px solid #22c55e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(34, 197, 94, 0.1); }}

        .study-box {{ background-color: #f8f9fa; border-left: 5px solid #6c757d; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(108, 117, 125, 0.1); }}

        .study-title {{ color: #495057; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .im-box {{ background-color: #f5f3ff; border-left: 5px solid #6a1b9a; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(106, 27, 154, 0.1); }}



        .summary-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background-color: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}

        .summary-table th, .summary-table td {{ border: 1px solid #eee; padding: 15px; text-align: left; font-size: 0.95rem; }}

        .summary-table th {{ background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%); color: white; text-transform: uppercase; letter-spacing: 1px; }}

        .summary-table tr:nth-child(even) {{ background-color: #fcfcfc; }}

        .param-name {{ font-weight: bold; color: #2c3e50; width: 35%; background-color: #f8f9fa; }}

    </style>



    <div class="med-container">

        <div class="med-title">MORPHINE</div>



        <div class="section-header">🧪 Chemical Structure and IUPAC</div>

        

        <span class="info-label">Molecular Formula:</span>

        <span class="info-text">C<sub>17</sub>H<sub>19</sub>NO<sub>3</sub></span>



        <span class="info-label">Molar Mass:</span>

        <span class="info-text">285.34 g/mol</span>



        <span class="info-label">Structural Characteristics:</span>

        <div class="usage-list">

            <div class="usage-item"><b>Pentacyclic Ring System:</b> Contains five fused rings: a phenolic ring (A), a cyclohexane ring (B), a cyclohexene ring (C), a piperidine ring (D), and a tetrahydrofuran ring (E).</div>

            <div class="usage-item"><b>Functional Groups:</b> Features two hydroxyl (-OH) groups (one phenolic at C-3 and one alcoholic at C-6), an ether bridge (epoxide) between C-4 and C-5, and a tertiary amine with an N-methyl group.</div>

            <div class="usage-item"><b>Stereochemistry:</b> Naturally occurring morphine is the levorotatory isomer, specifically the (5R, 6S, 9R, 13S, 14R) configuration.</div>

        </div>



        <div class="structure-box">

            <img src="/static/morphine_structure.png" class="structure-img" alt="Morphine Structure" onerror="this.src='https://placehold.co/400x300?text=Morphine+Structure'">

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff;">💊 Therapeutic Uses</div>

            <div class="usage-list">

                <div class="usage-item"><b>Analgesia:</b> Effectively manages severe acute and chronic pain. Widely used for pain associated with cancer, post-surgical recovery, and severe traumatic injuries.</div>

                <div class="usage-item"><b>Anxiolysis:</b> Reduces anxiety and creates a sense of relaxation.</div>

                <div class="usage-item"><b>Euphoria:</b> Produces feelings of contentment, often contributing to pain relief.</div>

                <div class="usage-item"><b>Sedation:</b> Induces drowsiness.</div>

                <div class="usage-item"><b>Cough Suppression:</b> Used in some instances for severe coughing.</div>

            </div>

            

            <div class="study-box" style="border-left-color: #007bff;">

                <span class="study-title">Important Clinical Considerations:</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Administration:</b> Available via injection, oral solution, and tablets.</div>

                    <div class="usage-item"><b>Mechanism:</b> Acts as a full agonist at the μ-opioid receptor, with no ceiling effect for pain relief.</div>

                    <div class="usage-item"><b>Risks:</b> High potential for physical dependence and addiction, although this is manageable with proper, short-term usage.</div>

                    <div class="usage-item"><b>Side Effects:</b> Common side effects include constipation, nausea, vomiting, dizziness, and mental confusion.</div>

                    <div class="usage-item"><b>Overdose:</b> Significant respiratory depression can occur, which is the primary danger in overdose situations.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #6f42c1;">⚠️ Adverse Drug Reactions (ADR)</div>

            <div class="usage-list">

                <div class="usage-item"><span class="usage-title">Gastrointestinal:</span>Constipation is the most common, often persistent, side effect (requires management with laxatives). Nausea and vomiting are also very common, particularly when initiating therapy.</div>

                <div class="usage-item"><span class="usage-title">Central Nervous System:</span>Drowsiness, dizziness, lightheadedness, and sedation.</div>

                <div class="usage-item"><span class="usage-title">Skin/Cardiovascular:</span>Sweating (diaphoresis) and itchy skin (pruritus).</div>

                <div class="usage-item"><span class="usage-title">Genitourinary:</span>Urinary retention.</div>

            </div>

            

            <div class="warning-box">

                <span class="warning-title">Serious or Life-Threatening Reactions</span>

                <div class="usage-list" style="margin-top: 10px;">

                    <div class="usage-item"><b>Respiratory Depression:</b> The most severe risk, characterized by slow, shallow, or irregular breathing.</div>

                    <div class="usage-item"><b>Severe Hypotension/Bradycardia:</b> Low blood pressure and slow heart rate.</div>

                    <div class="usage-item"><b>Allergic Reactions:</b> Anaphylaxis, rash, hives, and swelling of the face or throat.</div>

                    <div class="usage-item"><b>Opioid-Induced Hyperalgesia (OIH):</b> A paradoxical increase in pain sensitivity.</div>

                    <div class="usage-item"><b>Serotonin Syndrome:</b> Agitation, fever, shivering, tremor, and diarrhea (especially if taken with other serotonergic medications).</div>

                    <div class="usage-item"><b>Neurological:</b> Confusion, hallucinations, and seizures.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ed8936;">🤝 Drug-Drug Interactions</div>

            <div class="interaction-box">

                <div class="usage-list">

                    <div class="usage-item"><b>Alcohol & CNS Depressants:</b> Combining morphine with alcohol, benzodiazepines (e.g., alprazolam, diazepam), sedatives, or tranquilizers increases the risk of dangerous respiratory depression and, in extreme cases, fatal overdose.</div>

                    <div class="usage-item"><b>MAOIs:</b> Medications such as phenelzine, linezolid, and rasagiline should be avoided within 14 days of starting morphine due to the risk of severe adverse reactions, including serotonin syndrome.</div>

                    <div class="usage-item"><b>Other Opioids & Cough Medicines:</b> Combining morphine with other opioid analgesics or narcotic cough suppressants increases the risk of excessive sedation and breathing problems.</div>

                    <div class="usage-item"><b>Muscle Relaxants & Antihistamines:</b> Drugs like cyclobenzaprine or sedating antihistamines (e.g., diphenhydramine) increase the sedative effects.</div>

                    <div class="usage-item"><b>Antidepressants & Psychiatric Meds:</b> Certain antidepressants (amitriptyline, sertraline, fluoxetine) and anti-nausea drugs (ondansetron) can interact with morphine.</div>

                    <div class="usage-item"><b>Parkinson's & Bladder Medications:</b> Medications with anticholinergic properties combined with morphine increase the risk of severe constipation and urinary retention.</div>

                    <div class="usage-item"><b>Buprenorphine:</b> Using it with morphine may reduce the analgesic effect and trigger withdrawal symptoms.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #22c55e;">🍎 Food-Drug Interactions</div>

            <div class="food-box">

                <div class="usage-list">

                    <div class="usage-item"><b>Alcohol:</b> Avoid completely. Alcohol intensifies morphine's side effects, including extreme dizziness, drowsiness, breathing problems, and in severe cases, coma or death.</div>

                    <div class="usage-item"><b>High-Fat Meals:</b> While most formulations can be taken with or without food, some high-fat meals might affect the release rate of specific extended-release capsules.</div>

                    <div class="usage-item"><b>Constipation Management:</b> Morphine commonly causes constipation, so increasing fluid intake and dietary fiber is recommended.</div>

                </div>

                <span class="usage-title" style="margin-top: 15px; color: #15803d;">Important Tips:</span>

                <ul style="margin-top: 5px; color: #555;">

                    <li>Take with or without food.</li>

                    <li>If taking liquid morphine, check for sugar or alcohol content, especially if you have diabetes or alcohol dependence.</li>

                    <li>Always inform your healthcare provider about all prescriptions, OTC, and herbal supplements.</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header">📊 Summary Table for Study</div>

            <table class="summary-table">

                <tbody>

                    <tr><td class="param-name">Drug Class</td><td>Opioid analgesic (pure μ-agonist)</td></tr>

                    <tr><td class="param-name">Primary Indications</td><td>Severe acute and chronic pain, cancer pain, myocardial infarction, labour pain, acute pulmonary edema.</td></tr>

                    <tr><td class="param-name">Mechanism of Action</td><td>Activates μ-opioid receptors in the central nervous system (brain and spinal cord), reducing pain perception.</td></tr>

                    <tr><td class="param-name">Administration Routes</td><td>Oral (immediate and extended-release), intravenous (IV), intramuscular (IM), subcutaneous, epidural, intrathecal.</td></tr>

                    <tr><td class="param-name">Dosage Forms</td><td>Tablets (15mg, 30mg), Extended-Release (10mg-200mg), Injection (0.5mg/mL - 50mg/mL), Oral solution.</td></tr>

                    <tr><td class="param-name">Pharmacokinetics</td><td><b>Half-life:</b> 2-3 hours. <b>Duration:</b> 3-7 hours.<br><b>Metabolism:</b> ~90% by liver.<br><b>Excretion:</b> 70-80% in urine within 48 hours.</td></tr>

                    <tr><td class="param-name">Common Side Effects</td><td>Constipation, nausea, vomiting, dizziness, headache, somnolence, sweating, pruritus.</td></tr>

                    <tr><td class="param-name">Serious Risks</td><td>Respiratory depression, physical dependence, tolerance, addiction, hypotension.</td></tr>

                    <tr><td class="param-name">Contraindications</td><td>Acute/severe asthma, gastrointestinal obstruction, known hypersensitivity.</td></tr>

                    <tr><td class="param-name" style="color: #e53e3e;">Antidote</td><td><b style="color: #e53e3e;">Naloxone</b></td></tr>

                </tbody>

            </table>

        </div>



        <div class="section-divider">

            <div class="section-header">🏢 Common Brand Names (India)</div>

            <div class="study-box">

                <ul style="line-height: 1.8; color: #555;">

                    <li><b>Morcontin:</b> Available in different strengths, often used for sustained-release.</li>

                    <li><b>Duramor:</b> Commonly available for pain management.</li>

                    <li><b>Morphitroy:</b> Tablet form often used in pain management.</li>

                    <li><b>Vermor:</b> Available in multiple variants.</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #0ea5e9;">💉 IV Infusion Dosing</div>

            <div class="study-box" style="border-left-color: #0ea5e9; background-color: #f0f9ff;">

                <div class="usage-list">

                    <div class="usage-item"><b>Individualized Dosage:</b> Dosing must be titrated based on pain severity, response, and potential for adverse events.</div>

                    <div class="usage-item"><b>Administration:</b> When administered as an intermittent bolus, the injection should be given slowly to minimize side effects.</div>

                    <div class="usage-item"><b>Monitoring:</b> Close monitoring of respiratory rate, blood pressure, and sedation levels is required during treatment.</div>

                    <div class="usage-item"><b>Renal/Hepatic Impairment:</b> Adjustments to dosage, often involving reduction, are necessary for patients with renal or hepatic impairment.</div>

                    <div class="usage-item"><b>Conversion:</b> When converting between intravenous and oral administration, adjustments are necessary due to differences in bioavailability.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #6a1b9a;">💊 Oral & IM Dosing Warnings</div>

            <div class="im-box">

                <div class="usage-list">

                    <div class="usage-item"><b>Oral Dosing:</b> Providing general information on the oral dosing of morphine is not possible as it is a controlled substance that should only be taken under the guidance of a medical professional.</div>

                    <div class="usage-item"><b>Intramuscular (IM) Dosing:</b> Information regarding the IM dosing of morphine is strictly for administration by qualified healthcare professionals.</div>

                </div>

                <p style="color: #4a148c; font-weight: bold; margin-top: 15px;">⚠️ Critical Safety Note:</p>

                <p>Morphine is a controlled substance with significant risks. Its administration requires careful consideration of individual patient factors, medical history, and pain severity. It is crucial that any administration of morphine be performed under the direct supervision of a healthcare professional who can accurately assess the patient's needs and monitor for potential side effects or adverse reactions. Attempting to administer morphine without proper medical training and oversight can be extremely dangerous and lead to serious health complications or overdose.</p>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #10b981;">👴 Geriatric Dose Adjustment (Age 65+)</div>

            <div class="study-box" style="border-left-color: #10b981;">

                <p>The standard medical approach for geriatric patients often involves a <b>"start low and go slow"</b> method.</p>

                

                <span class="study-title" style="color: #047857;">Administration Principles:</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Initial Dose Adjustment:</b> For opioid-naive elderly patients, the initial starting dose is typically reduced compared to standard adult doses.</div>

                    <div class="usage-item"><b>Oral:</b> Clinical guidelines often suggest using lower initial doses of immediate-release oral morphine, sometimes starting with a smaller dose and extending the time between doses.</div>

                    <div class="usage-item"><b>Intravenous Titration:</b> In acute settings, clinicians may use smaller boluses and longer intervals to safely manage pain and monitor side effects.</div>

                    <div class="usage-item"><b>Monitoring:</b> Adjustments should be made slowly based on clinical response and frequent monitoring for sedation and respiratory rate.</div>

                </div>



                <span class="study-title" style="color: #047857; margin-top: 20px;">Factors Affecting Dosage:</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Renal Impairment:</b> Reduced excretion of active metabolites (M3G, M6G) can lead to potential toxicity, necessitating lower doses.</div>

                    <div class="usage-item"><b>Hepatic Impairment:</b> Decreased metabolism can increase bioavailability and prolong the drug's half-life.</div>

                    <div class="usage-item"><b>Frailty/Debilitation:</b> Enhanced sensitivity to CNS depressants and higher risk of falls or delirium necessitates using the lowest effective dose.</div>

                </div>

                

                <span class="study-title" style="color: #047857; margin-top: 20px;">Risks and Precautions in Elderly:</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Respiratory Depression:</b> The most serious risk, often occurring after large initial doses or rapid titration.</div>

                    <div class="usage-item"><b>Cognitive Effects:</b> Increased risk of delirium, confusion, and memory loss.</div>

                    <div class="usage-item"><b>Physical Hazards:</b> Higher incidence of falls, fractures, and severe constipation.</div>

                    <div class="usage-item"><b>Polypharmacy:</b> Older adults frequently take other medications (like benzodiazepines) which can cause dangerous interactions.</div>

                </div>

            </div>

        </div>



        <center style="margin-top: 50px; margin-bottom: 30px;">

            <a href="/drugs-store/allopathy" style="text-decoration: none;">

                <button style="padding: 15px 40px; cursor: pointer; background: linear-gradient(135deg, #2c3e50 0%, #000 100%); color: #fff; border: none; border-radius: 30px; font-weight: bold; font-size: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">Back to Products</button>

            </a>

        </center>

    </div>

    """

    html = f"<!DOCTYPE html><html><head><title>Morphine - Professional Profile</title></head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



def page_azithromycin_detail(user, lang):

    content = f"""

    <style>

        .med-container {{ max-width: 850px; margin: 30px auto; padding: 40px; background: #fff; font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #000; }}

        .med-title {{ font-size: 2rem; font-weight: bold; margin-bottom: 25px; text-transform: uppercase; border-bottom: 3px solid #00bcd4; padding-bottom: 10px; text-align: center; color: #2c3e50; }}

        .info-label {{ font-weight: bold; margin-top: 22px; display: block; font-size: 1.1rem; color: #2c3e50; }}

        .info-text {{ margin-bottom: 15px; display: block; color: #333; }}

        .structure-box {{ text-align: center; margin: 40px 0; padding: 20px; background: #fdfdfd; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}

        .structure-img {{ max-width: 100%; height: auto; border-radius: 5px; }}

        

        .usage-list {{ margin-top: 10px; padding-left: 0; list-style-type: none; }}

        .usage-item {{ margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #eee; }}

        .usage-title {{ font-weight: bold; display: block; color: #2c3e50; }}

        

        .section-divider {{ border-top: 2px solid #eee; margin-top: 40px; padding-top: 25px; }}

        .section-header {{ font-size: 1.4rem; font-weight: bold; color: #2c3e50; margin-bottom: 15px; text-transform: uppercase; display: flex; align-items: center; }}

        

        /* Box Styles */

        .warning-box {{ background-color: #fff5f5; border-left: 5px solid #e53e3e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(229, 62, 62, 0.1); }}

        .warning-title {{ color: #c53030; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .interaction-box {{ background-color: #fffaf0; border-left: 5px solid #ed8936; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(237, 137, 54, 0.1); }}

        .food-box {{ background-color: #f0fdf4; border-left: 5px solid #22c55e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(34, 197, 94, 0.1); }}

        .study-box {{ background-color: #f8f9fa; border-left: 5px solid #6c757d; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(108, 117, 125, 0.1); }}

        .im-box {{ background-color: #fff3e0; border-left: 5px solid #ff9800; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(255, 152, 0, 0.1); }}



        .summary-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background-color: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}

        .summary-table th, .summary-table td {{ border: 1px solid #eee; padding: 15px; text-align: left; font-size: 0.95rem; }}

        .summary-table th {{ background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%); color: white; text-transform: uppercase; letter-spacing: 1px; }}

        .summary-table tr:nth-child(even) {{ background-color: #fcfcfc; }}

        .param-name {{ font-weight: bold; color: #2c3e50; width: 35%; background-color: #f8f9fa; }}

    </style>



    <div class="med-container">

        <div class="med-title">AZITHROMYCIN</div>



        <div class="section-header">🧪 Chemical Structure and IUPAC Name</div>

        

        <table class="summary-table">

            <thead>

                <tr>

                    <th>Property</th>

                    <th>Value (Anhydrous)</th>

                    <th>Value (Trihydrate)</th>

                </tr>

            </thead>

            <tbody>

                <tr>

                    <td class="param-name">Molecular Weight</td>

                    <td>365.41 g/mol</td>

                    <td>419.45 g/mol</td>

                </tr>

                <tr>

                    <td class="param-name">Melting Point</td>

                    <td>194 °C</td>

                    <td>—</td>

                </tr>

                <tr>

                    <td class="param-name">Appearance</td>

                    <td>White to off-white crystalline powder</td>

                    <td>White, practically odorless powder</td>

                </tr>

                <tr>

                    <td class="param-name">Solubility</td>

                    <td>Soluble in water, methanol, and ethanol</td>

                    <td>Slightly soluble in water and methanol</td>

                </tr>

                <tr>

                    <td class="param-name">pKa</td>

                    <td>2.4 (acidic), 9.6 (basic)</td>

                    <td>2.6 (acidic)</td>

                </tr>

            </tbody>

        </table>



        <div class="structure-box">

            <img src="/static/azithromycin_structure.png" class="structure-img" alt="Azithromycin Structure" onerror="this.src='https://placehold.co/400x300?text=Azithromycin+Structure'">

            <p style="margin-top:10px; color: #666; font-size: 1.2rem;"><b>Azithromycin</b></p>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff;">💊 Therapeutic Uses</div>

            

            <div class="study-box" style="border-left-color: #007bff;">

                <span class="usage-title" style="color: #0056b3; font-size: 1.1rem;">Respiratory Tract Infections:</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Community-Acquired Pneumonia:</b> Caused by S. pneumoniae, H. influenzae, and atypical bacteria like Mycoplasma pneumoniae.</div>

                    <div class="usage-item"><b>Acute Bacterial Exacerbations of COPD:</b> Chronic bronchitis or lung disease flare-ups.</div>

                    <div class="usage-item"><b>Sinus & Throat Infections:</b> Including acute bacterial sinusitis, pharyngitis, and tonsillitis (often as a second-line treatment for those allergic to penicillin).</div>

                </div>



                <span class="usage-title" style="color: #0056b3; font-size: 1.1rem; margin-top: 15px;">Sexually Transmitted Infections (STIs):</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Urethritis and Cervicitis:</b> Typically caused by Chlamydia trachomatis or Neisseria gonorrhoeae.</div>

                    <div class="usage-item"><b>Genital Ulcer Disease (Chancroid):</b> Caused by Haemophilus ducreyi in men.</div>

                </div>



                <span class="usage-title" style="color: #0056b3; font-size: 1.1rem; margin-top: 15px;">Other Infections:</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Skin and Soft Tissue:</b> Uncomplicated infections like folliculitis or cellulitis caused by Staphylococcus aureus or Streptococcus pyogenes.</div>

                    <div class="usage-item"><b>Pediatric Otitis Media:</b> Middle ear infections in children older than 6 months.</div>

                    <div class="usage-item"><b>MAC Prophylaxis:</b> Prevention and treatment of disseminated Mycobacterium avium complex (MAC) in patients with advanced HIV/AIDS.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #6f42c1;">⚠️ Adverse Drug Reaction (ADR)</div>

            <p><b>Common Adverse Reactions:</b> Most side effects are mild-to-moderate and resolve after completing the course.</p>

            <div class="usage-list">

                <div class="usage-item"><span class="usage-title">Gastrointestinal (Most Common):</span>Diarrhea (5-14%), nausea (3-18%), abdominal pain (3-7%), and vomiting (2-7%).</div>

                <div class="usage-item"><span class="usage-title">Central Nervous System:</span>Headache, dizziness, and fatigue.</div>

                <div class="usage-item"><span class="usage-title">Sensory Changes:</span>Altered sense of taste or smell.</div>

            </div>

            

            <div class="warning-box">

                <span class="warning-title">Serious and Rare Reactions (Require immediate medical attention)</span>

                <div class="usage-list" style="margin-top: 10px;">

                    <div class="usage-item"><b>Cardiovascular Risks:</b> Azithromycin can cause QT prolongation, potentially leading to fatal arrhythmias like torsades de pointes. This risk is highest in elderly patients and those with pre-existing heart conditions or low potassium/magnesium levels.</div>

                    <div class="usage-item"><b>Hepatotoxicity (Liver Injury):</b> Symptoms include jaundice (yellowing of skin/eyes), dark urine, and severe abdominal pain. Injury typically appears 1-3 weeks after starting the drug and can range from mild enzyme elevations to acute liver failure.</div>

                    <div class="usage-item"><b>Severe Skin Reactions:</b> Rare but dangerous conditions like Stevens-Johnson Syndrome (SJS), Toxic Epidermal Necrolysis (TEN), and DRESS syndrome (Drug Reaction with Eosinophilia and Systemic Symptoms).</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ed8936;">🤝 Drug-Drug Interactions</div>

            <div class="interaction-box">

                <div class="usage-list">

                    <div class="usage-item">

                        <span class="usage-title">QT-Prolonging Drugs:</span>

                        <span>Combining azithromycin with other medications that affect heart rhythm can lead to life-threatening arrhythmias (Torsades de Pointes). Includes Anti-arrhythmics (Amiodarone, sotalol, quinidine, dofetilide), Antipsychotics/Antidepressants (Pimozide - contraindicated, citalopram, haloperidol), and Other Antibiotics (Fluoroquinolones like moxifloxacin, ciprofloxacin).</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Blood Thinners (Warfarin):</span>

                        <span>Azithromycin can potentiate the effects of oral anticoagulants like Warfarin (Jantoven), significantly increasing the risk of bleeding. Frequent monitoring of prothrombin time (INR) is recommended.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Colchicine:</span>

                        <span>Used for gout, this combination can increase Colchicine levels to toxic amounts, potentially causing multi-organ damage.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Digoxin:</span>

                        <span>Azithromycin may increase Digoxin levels, possibly by altering intestinal flora. Monitoring for digoxin toxicity (nausea, vomiting, arrhythmias) is advised.</span>

                    </div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #22c55e;">🍎 Food-Drug Interactions</div>

            <div class="food-box">

                <div class="usage-list">

                    <div class="usage-item"><b>Dairy (Milk, Yogurt, Cheese):</b> Unlike many other antibiotics, azithromycin does not have a major interaction with calcium. You can usually consume dairy normally, although some sources suggest separating intake by 2 hours if eating yogurt for probiotic benefits.</div>

                    <div class="usage-item"><b>Grapefruit & Grapefruit Juice:</b> While reports are uncommon, some experts advise avoiding grapefruit as it can interfere with how your body processes certain medications.</div>

                    <div class="usage-item"><b>Alcohol:</b> Alcohol does not directly stop azithromycin from working, but it can worsen common side effects like dizziness, nausea, and upset stomach. It is generally safer to limit alcohol until you finish your course.</div>

                    <div class="usage-item"><b>Spicy or Rich Foods:</b> If you experience stomach pain or diarrhea, stick to bland, simple meals until your symptoms improve.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header">📊 Summary Table for Study</div>

            <table class="summary-table">

                <thead>

                    <tr>

                        <th>Formulation</th>

                        <th>Interaction with Food</th>

                        <th>Recommended Timing</th>

                    </tr>

                </thead>

                <tbody>

                    <tr>

                        <td class="param-name">Tablets</td>

                        <td>Minor: Food may slightly increase peak levels but does not affect overall absorption.</td>

                        <td>Take with or without food; take with food if it upsets your stomach.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Oral Suspension (Liquid)</td>

                        <td>Food does not decrease overall absorption.</td>

                        <td>Can be taken with or without food.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Capsules</td>

                        <td>Significant: Food can reduce absorption by up to 50%.</td>

                        <td>Must be taken on an empty stomach (1 hour before or 2 hours after meals).</td>

                    </tr>

                    <tr>

                        <td class="param-name">Antacids (Al/Mg)</td>

                        <td>Absorption Blocked: Reduces effectiveness if taken together.</td>

                        <td>Separate by at least 2 hours before or after.</td>

                    </tr>

                </tbody>

            </table>

        </div>



        <div class="section-divider">

            <div class="section-header">🏢 Common Brand Names (India)</div>

            <div class="study-box">

                <ul style="line-height: 1.8; color: #555;">

                    <li><b>Azithral (Alembic Pharmaceuticals Ltd):</b> One of the oldest and most popular brands, available in tablets, capsules, and syrups.</li>

                    <li><b>Azee (Cipla Ltd):</b> Known for its affordability and wide distribution.</li>

                    <li><b>Aziwok (Dr. Reddy's Laboratories Ltd):</b> Extensively used for respiratory and skin infections.</li>

                    <li><b>Zady (Mankind Pharma Ltd):</b> A popular budget-friendly choice from a leading Indian manufacturer.</li>

                    <li><b>Azibact (Ipca Laboratories Ltd):</b> Highly recommended for skin and ear infections.</li>

                    <li><b>Azax (Sun Pharmaceutical Industries Ltd):</b> Produced by India's top pharma company, widely prescribed for throat and chest infections.</li>

                    <li><b>Azilide (Micro Labs Ltd):</b> Frequently used for infections of the respiratory tract.</li>

                    <li><b>Azivent (Aristo Pharmaceuticals Pvt Ltd):</b> Often used for typhoid fever and certain STIs.</li>

                    <li><b>Azicip (Cipla Ltd):</b> Another major brand from Cipla, known for high quality and reliability.</li>

                    <li><b>Azikem (Alkem Laboratories Ltd):</b> A cost-effective generic brand commonly used in hospital settings.</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #0ea5e9;">💉 IV Infusion Dosing</div>

            <div class="study-box" style="border-left-color: #0ea5e9; background-color: #f0f9ff;">

                <span class="study-title" style="color: #0369a1;">1. Standard Adult Dosing:</span>

                <p>For many infections, IV azithromycin is used initially, followed by oral therapy to complete the course.</p>

                <div class="usage-list">

                    <div class="usage-item"><b>Community-Acquired Pneumonia (CAP):</b> Typically administered once daily for a period followed by oral therapy.</div>

                    <div class="usage-item"><b>Pelvic Inflammatory Disease (PID):</b> Usually administered daily for 1 to 2 days, followed by oral therapy.</div>

                    <div class="usage-item"><b>Severe Sepsis:</b> Dosage is determined by the healthcare provider based on the clinical response.</div>

                </div>



                <span class="study-title" style="color: #0369a1; margin-top: 20px;">2. Reconstitution & Dilution:</span>

                <p>Azithromycin requires specific preparation steps.</p>

                <div class="usage-list">

                    <div class="usage-item"><b>Step 1: Reconstitution:</b> The 500 mg vial is reconstituted with Sterile Water for Injection, which creates a specific concentration.</div>

                    <div class="usage-item"><b>Step 2: Dilution:</b> The reconstituted solution must be transferred into a compatible diluent (e.g., Normal Saline, 5% Dextrose, or Lactated Ringer's) to reach the appropriate concentration for infusion.</div>

                </div>



                <span class="study-title" style="color: #0369a1; margin-top: 20px;">3. Infusion Rate & Concentration:</span>

                <p>The infusion rate is adjusted based on the final concentration of the mixture to minimize the risk of local site reactions.</p>

                <div class="usage-list">

                    <div class="usage-item"><b>1 mg/mL Concentration:</b> Administered over a longer duration.</div>

                    <div class="usage-item"><b>2 mg/mL Concentration:</b> Administered over a shorter duration.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff;">💊 Oral Dosing</div>

            <div class="study-box" style="border-left-color: #007bff;">

                <div class="usage-list">

                    <div class="usage-item"><b>Adults:</b> Regimens for infections like pneumonia, bronchitis, or skin infections often involve an initial dose followed by a lower daily dose for several days. Infections like chlamydia may require a single, higher dose.</div>

                    <div class="usage-item"><b>Children:</b> Pediatric dosing is specifically calculated based on the child's weight (mg/kg) and the type of infection.</div>

                    <div class="usage-item"><b>Formulation Matters:</b> Azithromycin tablets can be taken with or without food. However, capsules should be taken on an empty stomach (1 hour before or 2 hours after a meal) for proper absorption.</div>

                    <div class="usage-item"><b>Avoid Antacids:</b> Do not take antacids containing aluminum or magnesium at the same time; separate them from the medication dose.</div>

                    <div class="usage-item"><b>Finish the Course:</b> It is essential to complete the full prescribed course to ensure the infection is treated and to prevent antibiotic resistance.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ff9800;">💪 Intramuscular (IM) Dosing</div>

            <div class="im-box">

                <div class="usage-list">

                    <div class="usage-item"><b>Avoid IM Injection:</b> Standard injectable azithromycin is designed exclusively for intravenous (IV) infusion only.</div>

                    <div class="usage-item"><b>Injection Site Reactions:</b> Azithromycin is known to cause significant local tissue irritation. Clinical studies have shown that even when diluted and given as an IV infusion, it can cause pain and inflammation at the site. Administering it directly into a muscle (IM) would likely cause severe pain and local tissue damage.</div>

                    <div class="usage-item"><b>No IV Bolus:</b> It should also never be given as a rapid "bolus" injection into a vein. It must be diluted and infused over at least 60 minutes.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #10b981;">👴 Geriatric Dose Adjustment</div>

            <div class="study-box" style="border-left-color: #10b981;">

                <div class="usage-list">

                    <div class="usage-item">

                        <span class="usage-title" style="color: #047857;">QT-Prolonging Drugs:</span>

                        <span>Combining azithromycin with other medications that affect heart rhythm can lead to life-threatening arrhythmias (Torsades de Pointes). Includes Anti-arrhythmics (Amiodarone, sotalol, quinidine, dofetilide), Antipsychotics/Antidepressants (Pimozide - contraindicated, citalopram, haloperidol), and Other Antibiotics (Fluoroquinolones like moxifloxacin, ciprofloxacin).</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title" style="color: #047857;">Blood Thinners (Warfarin):</span>

                        <span>Azithromycin can potentiate the effects of oral anticoagulants like Warfarin (Jantoven), significantly increasing the risk of bleeding. Frequent monitoring of prothrombin time (INR) is recommended.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title" style="color: #047857;">Colchicine:</span>

                        <span>Used for gout, this combination can increase Colchicine levels to toxic amounts, potentially causing multi-organ damage.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title" style="color: #047857;">Digoxin:</span>

                        <span>Azithromycin may increase Digoxin levels, possibly by altering intestinal flora. Monitoring for digoxin toxicity (nausea, vomiting, arrhythmias) is advised.</span>

                    </div>

                </div>

            </div>

        </div>



        <center style="margin-top: 50px; margin-bottom: 30px;">

            <a href="/drugs-store/allopathy" style="text-decoration: none;">

                <button style="padding: 15px 40px; cursor: pointer; background: linear-gradient(135deg, #2c3e50 0%, #000 100%); color: #fff; border: none; border-radius: 30px; font-weight: bold; font-size: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">Back to Products</button>

            </a>

        </center>

    </div>

    """

    html = f"<!DOCTYPE html><html><head><title>Azithromycin - Professional Profile</title></head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



def page_ciprofloxacin_detail(user, lang):

    content = f"""

    <style>

        .med-container {{ max-width: 850px; margin: 30px auto; padding: 40px; background: #fff; font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #000; }}

        .med-title {{ font-size: 2rem; font-weight: bold; margin-bottom: 25px; text-transform: uppercase; border-bottom: 3px solid #ff5722; padding-bottom: 10px; text-align: center; color: #2c3e50; }}

        .info-label {{ font-weight: bold; margin-top: 22px; display: block; font-size: 1.1rem; color: #2c3e50; }}

        .info-text {{ margin-bottom: 15px; display: block; color: #333; }}

        .structure-box {{ text-align: center; margin: 40px 0; padding: 20px; background: #fdfdfd; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}

        .structure-img {{ max-width: 100%; height: auto; border-radius: 5px; }}

        

        .usage-list {{ margin-top: 10px; padding-left: 0; list-style-type: none; }}

        .usage-item {{ margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #eee; }}

        .usage-title {{ font-weight: bold; display: block; color: #2c3e50; }}

        

        .section-divider {{ border-top: 2px solid #eee; margin-top: 40px; padding-top: 25px; }}

        .section-header {{ font-size: 1.4rem; font-weight: bold; color: #2c3e50; margin-bottom: 15px; text-transform: uppercase; display: flex; align-items: center; }}

        

        /* Box Styles */

        .warning-box {{ background-color: #fff5f5; border-left: 5px solid #e53e3e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(229, 62, 62, 0.1); }}

        .warning-title {{ color: #c53030; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .interaction-box {{ background-color: #fffaf0; border-left: 5px solid #ed8936; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(237, 137, 54, 0.1); }}

        .food-box {{ background-color: #f0fdf4; border-left: 5px solid #22c55e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(34, 197, 94, 0.1); }}

        .study-box {{ background-color: #f8f9fa; border-left: 5px solid #6c757d; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(108, 117, 125, 0.1); }}

        .im-box {{ background-color: #fff3e0; border-left: 5px solid #ff9800; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(255, 152, 0, 0.1); }}



        .summary-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background-color: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}

        .summary-table th, .summary-table td {{ border: 1px solid #eee; padding: 15px; text-align: left; font-size: 0.95rem; }}

        .summary-table th {{ background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%); color: white; text-transform: uppercase; letter-spacing: 1px; }}

        .summary-table tr:nth-child(even) {{ background-color: #fcfcfc; }}

        .param-name {{ font-weight: bold; color: #2c3e50; width: 35%; background-color: #f8f9fa; }}

    </style>



    <div class="med-container">

        <div class="med-title">CIPROFLOXACIN</div>



        <div class="section-header">🧪 Chemical Structure and IUPAC Name</div>

        

        <span class="info-label">IUPAC Name:</span>

        <span class="info-text">1-cyclopropyl-6-fluoro-4-oxo-7-(piperazin-1-yl)-1,4-dihydroquinoline-3-carboxylic acid.</span>



        <table class="summary-table">

            <thead>

                <tr>

                    <th>Property</th>

                    <th>Value</th>

                </tr>

            </thead>

            <tbody>

                <tr>

                    <td class="param-name">Physical Form</td>

                    <td>Faint to light yellow crystalline powder.</td>

                </tr>

                <tr>

                    <td class="param-name">Melting Point</td>

                    <td>255-257 °C (decomposes).</td>

                </tr>

                <tr>

                    <td class="param-name">Solubility</td>

                    <td>Practically insoluble in water and ethanol; soluble in dilute (0.1N) hydrochloric acid.</td>

                </tr>

                <tr>

                    <td class="param-name">pKa</td>

                    <td>6.09 (carboxylic acid) and 8.74 (piperazinyl nitrogen).</td>

                </tr>

            </tbody>

        </table>



        <div class="structure-box">

            <img src="/static/ciprofloxacin_structure.png" class="structure-img" alt="Ciprofloxacin Structure" onerror="this.src='https://placehold.co/400x300?text=Ciprofloxacin+Structure'">

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff;">💊 Therapeutic Uses</div>

            <div class="study-box" style="border-left-color: #007bff;">

                <div class="usage-list">

                    <div class="usage-item"><b>Urinary Tract Infections (UTIs):</b> Includes both uncomplicated and complicated UTIs, as well as kidney infections (pyelonephritis).</div>

                    <div class="usage-item"><b>Respiratory Tract Infections:</b> Used for pneumonia and acute exacerbations of chronic bronchitis.</div>

                    <div class="usage-item"><b>Gastrointestinal Infections:</b> Effective against infectious diarrhea (caused by E. coli, Campylobacter, or Shigella) and Typhoid Fever.</div>

                    <div class="usage-item"><b>Bone and Joint Infections:</b> Treatment of osteomyelitis and other infections caused by susceptible organisms.</div>

                    <div class="usage-item"><b>Skin and Skin Structure Infections:</b> Treats infections caused by various bacteria, including Pseudomonas aeruginosa and Staphylococcus aureus.</div>

                    <div class="usage-item"><b>Prostatitis:</b> Specifically for chronic bacterial prostatitis.</div>

                    <div class="usage-item"><b>Sexually Transmitted Infections (STIs):</b> Used for uncomplicated cervical and urethral gonorrhea (though resistance has made this less common) and chancroid.</div>

                    <div class="usage-item"><b>Bioterrorism Agents:</b> Approved for both adults and children for Inhalational Anthrax (post-exposure) and Plague.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #6f42c1;">⚠️ Adverse Drug Reaction (ADR)</div>

            <div class="warning-box">

                <span class="warning-title">Severe & Black Box Warnings</span>

                <div class="usage-list" style="margin-top: 10px;">

                    <div class="usage-item"><b>Tendinitis and Tendon Rupture:</b> Most commonly affecting the Achilles tendon, but can occur in the shoulder, hand, or thumb. This can happen within hours of the first dose or months after stopping treatment.</div>

                    <div class="usage-item"><b>Peripheral Neuropathy:</b> Nerve damage that may lead to permanent pain, burning, tingling, or numbness in the arms or legs.</div>

                    <div class="usage-item"><b>Central Nervous System (CNS) Effects:</b> Includes seizures, tremors, and serious mental health issues such as psychosis, hallucinations, anxiety, depression, and suicidal thoughts.</div>

                    <div class="usage-item"><b>Exacerbation of Myasthenia Gravis:</b> Can significantly worsen muscle weakness and breathing problems in patients with this condition, potentially leading to death.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ed8936;">🤝 Drug-Drug Interactions</div>

            <div class="interaction-box">

                <div class="usage-list">

                    <div class="usage-item"><b>Antacids & Minerals:</b> Avoid taking ciprofloxacin at the same time as antacids or supplements containing magnesium, aluminum, calcium, iron, or zinc.</div>

                    <div class="usage-item"><b>Dairy Products:</b> Calcium in milk, yogurt, and cheese can block absorption. While it is okay to have these as part of a larger meal, they should not be consumed alone with the medication.</div>

                    <div class="usage-item"><b>Sucralfate (Carafate):</b> This ulcer medication significantly reduces ciprofloxacin levels and should be strictly separated.</div>

                    <div class="usage-item"><b>Timing Rule:</b> Generally, take ciprofloxacin 2 hours before or 6 hours after these products.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #22c55e;">🍎 Food-Drug Interactions</div>

            <div class="food-box">

                <div class="usage-list">

                    <div class="usage-item">

                        <span class="usage-title">Dairy Products & Calcium-Fortified Foods:</span>

                        <span>Calcium binds to ciprofloxacin in the digestive tract, forming a "complex" that the body cannot absorb. This can reduce the drug's concentration by 30-50% or more.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Caffeine (Coffee, Tea, Energy Drinks, Chocolate):</span>

                        <span>Ciprofloxacin blocks the liver enzyme (CYP1A2) that breaks down caffeine. This causes caffeine to stay in your system longer than usual.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Fortified Juices & Enteral Nutrition:</span>

                        <span>While plain orange juice is generally okay, calcium-fortified versions interfere with absorption just like milk. For those on enteral nutrition (like Ensure), the feeding should be held for 1 hour before and 2 hours after the dose, as the high mineral content in these formulas can reduce ciprofloxacin levels by up to 67%.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Alcohol:</span>

                        <span>There is no known direct chemical interaction between alcohol and ciprofloxacin. However, alcohol can worsen side effects like dizziness and stomach upset, and it may slow your recovery from the infection.</span>

                    </div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header">📊 Summary Table for Study</div>

            <table class="summary-table">

                <thead>

                    <tr>

                        <th>Category</th>

                        <th>Key Details</th>

                    </tr>

                </thead>

                <tbody>

                    <tr>

                        <td class="param-name">Primary Uses</td>

                        <td>Complicated UTIs, Prostatitis, Anthrax, Infectious Diarrhea, Osteomyelitis.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Black Box Warnings</td>

                        <td>Tendon Rupture, Peripheral Neuropathy, CNS effects, Myasthenia Gravis.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Major Interaction</td>

                        <td>Tizanidine (absolute contraindication), Theophylline, Warfarin.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Chelation</td>

                        <td>Calcium, Iron, and Magnesium stop absorption (The "2 hours before/6 hours after" rule).</td>

                    </tr>

                    <tr>

                        <td class="param-name">Cautions</td>

                        <td>QT Prolongation, Photosensitivity, Aortic Aneurysm risk.</td>

                    </tr>

                </tbody>

            </table>

        </div>



        <div class="section-divider">

            <div class="section-header">🏢 Common Brand Names (India)</div>

            <div class="study-box">

                <ul style="line-height: 1.8; color: #555;">

                    <li><b>Ciplox</b> (manufactured by Cipla Ltd.)</li>

                    <li><b>Cifran</b> (manufactured by Sun Pharmaceutical Industries Ltd.)</li>

                    <li><b>Ciprobid</b> (manufactured by Zydus Cadila)</li>

                    <li><b>Alcoflox</b> (manufactured by Alkem Laboratories)</li>

                    <li><b>Ciprozol</b> (manufactured by Mankind Pharma)</li>

                    <li><b>Floxip</b> (manufactured by Abbott India)</li>

                    <li><b>Ciprolup</b> (manufactured by Lupin Ltd.)</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #0ea5e9;">💉 IV Infusion Dosing</div>

            <div class="study-box" style="border-left-color: #0ea5e9; background-color: #f0f9ff;">

                <span class="study-title" style="color: #0369a1;">Standard Adult IV Administration:</span>

                <div class="usage-list">

                    <div class="usage-item">In adults, Ciprofloxacin IV is generally administered in doses adjusted according to the site and severity of the infection, typically at intervals of 8 to 12 hours.</div>

                    <div class="usage-item"><b>Common Applications:</b> It is often used for complicated urinary tract infections, lower respiratory tract infections, skin infections, bone and joint infections, chronic prostatitis, and inhalational anthrax.</div>

                    <div class="usage-item"><b>Typical Usage:</b> Dosages for adults frequently involve a specific amount, which may be adjusted based on the specific infection.</div>

                </div>



                <span class="study-title" style="color: #0369a1; margin-top: 20px;">Pediatric IV Administration (Ages 1-17):</span>

                <div class="usage-list">

                    <div class="usage-item">Pediatric dosing is based on weight and is generally restricted to specific, documented infections, such as complicated UTIs or inhalation anthrax.</div>

                    <div class="usage-item"><b>Administration:</b> It is administered at specific intervals, such as every 8 or 12 hours.</div>

                    <div class="usage-item"><b>Dosage considerations:</b> Pediatric dosages are often calculated based on weight, with maximum amounts per dose.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff;">💊 Oral Dosing</div>

            <div class="study-box" style="border-left-color: #007bff;">

                <span class="study-title">Important Considerations</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Drug/Food Interactions:</b> Avoid taking ciprofloxacin with dairy products (like milk or yogurt) or calcium-fortified foods alone, as they may decrease absorption. It should be taken 2 hours before or 6 hours after mineral supplements, antacids, or iron preparations.</div>

                    <div class="usage-item"><b>Suspension:</b> Shake the liquid suspension well before each use and avoid using it for feeding tubes.</div>

                    <div class="usage-item"><b>Side Effects:</b> Potential side effects include nausea, diarrhea, and risks of tendonitis or tendon rupture.</div>

                    <div class="usage-item"><b>Renal Impairment:</b> Patients with kidney issues may require adjusted dosing regimens.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ff9800;">💪 Intramuscular Dosing</div>

            <div class="im-box">

                <div class="usage-list">

                    <div class="usage-item"><b>Irritation and Tissue Damage:</b> Ciprofloxacin solutions are highly acidic (pH 3.3 to 4.6), which can cause significant pain, inflammation, and potential tissue necrosis if injected into muscle.</div>

                    <div class="usage-item"><b>Approved Routes:</b> For systemic treatment, it is strictly limited to oral (tablets/suspension) and intravenous (IV) infusion.</div>

                    <div class="usage-item"><b>Pharmacokinetics:</b> IV administration is designed as a slow infusion (over 60 minutes) to minimize venous irritation and ensure controlled absorption, which cannot be achieved via IM injection.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #10b981;">👴 Geriatric Dose Adjustment</div>

            <div class="study-box" style="border-left-color: #10b981;">

                <span class="study-title" style="color: #047857;">Dosage Adjustments Based on Renal Function:</span>

                <p>For patients with a known or estimated creatinine clearance (CrCI), the following guidelines apply:</p>

                

                <table class="summary-table">

                    <thead>

                        <tr style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">

                            <th>Creatinine Clearance (CrCI)</th>

                            <th>Dosage Consideration</th>

                        </tr>

                    </thead>

                    <tbody>

                        <tr>

                            <td><b>>50 mL/min</b></td>

                            <td>Generally no adjustment required; standard adult dosing may be utilized.</td>

                        </tr>

                        <tr>

                            <td><b>30-50 mL/min</b></td>

                            <td>Dosage may require reduction and monitoring based on clinical assessment.</td>

                        </tr>

                        <tr>

                            <td><b>5-29 mL/min</b></td>

                            <td>Dose adjustment is recommended to prevent accumulation, often with extended intervals.</td>

                        </tr>

                        <tr>

                            <td><b>Hemodialysis / Peritoneal Dialysis</b></td>

                            <td>Dose adjustments are required, typically administered after dialysis.</td>

                        </tr>

                    </tbody>

                </table>

            </div>

        </div>



        <center style="margin-top: 50px; margin-bottom: 30px;">

            <a href="/drugs-store/allopathy" style="text-decoration: none;">

                <button style="padding: 15px 40px; cursor: pointer; background: linear-gradient(135deg, #2c3e50 0%, #000 100%); color: #fff; border: none; border-radius: 30px; font-weight: bold; font-size: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">Back to Products</button>

            </a>

        </center>

    </div>

    """

    html = f"<!DOCTYPE html><html><head><title>Ciprofloxacin - Professional Profile</title></head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



def page_doxycycline_detail(user, lang):

    content = f"""

    <style>

        .med-container {{ max-width: 850px; margin: 30px auto; padding: 40px; background: #fff; font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #000; }}

        .med-title {{ font-size: 2rem; font-weight: bold; margin-bottom: 25px; text-transform: uppercase; border-bottom: 3px solid #009688; padding-bottom: 10px; text-align: center; color: #2c3e50; }}

        .info-label {{ font-weight: bold; margin-top: 22px; display: block; font-size: 1.1rem; color: #2c3e50; }}

        .info-text {{ margin-bottom: 15px; display: block; color: #333; }}

        .structure-box {{ text-align: center; margin: 40px 0; padding: 20px; background: #fdfdfd; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}

        .structure-img {{ max-width: 100%; height: auto; border-radius: 5px; }}

        

        .usage-list {{ margin-top: 10px; padding-left: 0; list-style-type: none; }}

        .usage-item {{ margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #eee; }}

        .usage-title {{ font-weight: bold; display: block; color: #2c3e50; }}

        

        .section-divider {{ border-top: 2px solid #eee; margin-top: 40px; padding-top: 25px; }}

        .section-header {{ font-size: 1.4rem; font-weight: bold; color: #2c3e50; margin-bottom: 15px; text-transform: uppercase; display: flex; align-items: center; }}

        

        /* Box Styles */

        .warning-box {{ background-color: #fff5f5; border-left: 5px solid #e53e3e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(229, 62, 62, 0.1); }}

        .warning-title {{ color: #c53030; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .interaction-box {{ background-color: #fffaf0; border-left: 5px solid #ed8936; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(237, 137, 54, 0.1); }}

        .food-box {{ background-color: #f0fdf4; border-left: 5px solid #22c55e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(34, 197, 94, 0.1); }}

        .study-box {{ background-color: #f8f9fa; border-left: 5px solid #6c757d; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(108, 117, 125, 0.1); }}

        .im-box {{ background-color: #fff3e0; border-left: 5px solid #ff9800; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(255, 152, 0, 0.1); }}



        .summary-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background-color: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}

        .summary-table th, .summary-table td {{ border: 1px solid #eee; padding: 15px; text-align: left; font-size: 0.95rem; }}

        .summary-table th {{ background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%); color: white; text-transform: uppercase; letter-spacing: 1px; }}

        .summary-table tr:nth-child(even) {{ background-color: #fcfcfc; }}

        .param-name {{ font-weight: bold; color: #2c3e50; width: 35%; background-color: #f8f9fa; }}

    </style>



    <div class="med-container">

        <div class="med-title">DOXYCYCLINE</div>



        <div class="section-header">🧪 Chemical Structure and IUPAC Name</div>

        

        <span class="info-label">IUPAC Name:</span>

        <span class="info-text">(4S, 4aR, 5S, 5aR, 6R, 12aS)-4-(dimethylamino)-3,5,10,12,12a-pentahydroxy-6-methyl-1,11-dioxo-1,4,4,5,5a,6,11,12a-octahydrotetracene-2-carboxamide.</span>



        <table class="summary-table">

            <thead>

                <tr>

                    <th>Property</th>

                    <th>Value</th>

                </tr>

            </thead>

            <tbody>

                <tr>

                    <td class="param-name">Structure</td>

                    <td>A tetracycline derivative with a distinct, highly lipid-soluble four-ring structure.</td>

                </tr>

                <tr>

                    <td class="param-name">Molar Mass</td>

                    <td>444.4 g/mol (anhydrous).</td>

                </tr>

                <tr>

                    <td class="param-name">Stability</td>

                    <td>Noted for its high serum stability.</td>

                </tr>

                <tr>

                    <td class="param-name">Common Forms</td>

                    <td>Highly water-soluble hyclate salt and the less soluble monohydrate.</td>

                </tr>

            </tbody>

        </table>



        <div class="structure-box">

            <img src="/static/doxycycline_structure.png" class="structure-img" alt="Doxycycline Structure" onerror="this.src='https://placehold.co/400x300?text=Doxycycline+Structure'">

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff;">💊 Therapeutic Uses</div>

            <div class="study-box" style="border-left-color: #007bff;">

                <div class="usage-list">

                    <div class="usage-item"><b>Skin Conditions:</b> Widely used for moderate-to-severe acne vulgaris and rosacea.</div>

                    <div class="usage-item"><b>Respiratory Infections:</b> Effective against pneumonia, bronchitis, and sinusitis caused by susceptible organisms like Mycoplasma pneumoniae.</div>

                    <div class="usage-item"><b>Sexually Transmitted Infections (STIs):</b> Used to treat chlamydia, syphilis (in penicillin-allergic patients), and non-gonococcal urethritis.</div>

                    <div class="usage-item"><b>Tick-borne & Rickettsial Illnesses:</b> First-line treatment for Lyme disease, Rocky Mountain spotted fever, and typhus.</div>

                    <div class="usage-item"><b>Malaria:</b> Prescribed for both the prevention (prophylaxis) of malaria in travelers and as part of a combination therapy to treat active cases.</div>

                    <div class="usage-item"><b>Biological Threat Agents:</b> FDA-approved for the treatment and post-exposure prevention of anthrax, plague, and tularemia.</div>

                    <div class="usage-item"><b>Other Infections:</b> Includes treatment for cholera, brucellosis (with other drugs), and periodontitis (gum disease).</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #6f42c1;">⚠️ Adverse Drug Reaction (ADR)</div>

            <div class="study-box" style="border-left-color: #6f42c1; background-color: #f3e5f5;">

                <span class="usage-title" style="color: #4a148c;">Common Side Effects</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Gastrointestinal Distress:</b> Nausea, vomiting, and diarrhea are the most frequently reported side effects.</div>

                    <div class="usage-item"><b>Photosensitivity:</b> Significant increase in sensitivity to UV light, which can lead to severe sunburn-like reactions, rashes, or blisters even with brief exposure.</div>

                    <div class="usage-item"><b>Esophageal Irritation:</b> Can cause esophagitis or ulcers if the pill lodges in the throat. This is typically avoided by taking the dose with plenty of water and remaining upright for 30 minutes.</div>

                    <div class="usage-item"><b>Secondary Infections:</b> Overgrowth of non-susceptible organisms can lead to vaginal yeast infections (candidiasis) or oral thrush.</div>

                </div>

            </div>

            

            <div class="warning-box">

                <span class="warning-title">Severe & Rare Warnings</span>

                <div class="usage-list" style="margin-top: 10px;">

                    <div class="usage-item"><b>Intracranial Hypertension (IH):</b> Increased pressure around the brain, presenting as severe headaches, blurred vision, or permanent vision loss. Risk is higher in overweight women of childbearing age.</div>

                    <div class="usage-item"><b>Severe Skin Reactions:</b> Rare but life-threatening conditions such as Stevens-Johnson Syndrome (SJS) or Toxic Epidermal Necrolysis (TEN).</div>

                    <div class="usage-item"><b>C. difficile-Associated Diarrhea:</b> A severe form of antibiotic-associated diarrhea that can occur up to two months after stopping treatment.</div>

                    <div class="usage-item"><b>Hepatotoxicity:</b> Rare cases of liver damage, especially with high doses or long-term use.</div>

                    <div class="usage-item"><b>Blood Disorders:</b> Potential for hemolytic anemia, thrombocytopenia (low platelets), or neutropenia (low white blood cells).</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ed8936;">🤝 Drug-Drug Interactions</div>

            <div class="interaction-box">

                <div class="usage-list">

                    <div class="usage-item"><b>Antacids & Indigestion Meds:</b> Products containing aluminum, calcium, or magnesium (e.g., Tums, Mylanta, Gaviscon) should be separated by at least 2-3 hours.</div>

                    <div class="usage-item"><b>Minerals & Supplements:</b> Iron, zinc, and magnesium supplements significantly block absorption. It is recommended to take doxycycline 2 hours before or 3 hours after these products.</div>

                    <div class="usage-item"><b>Retinoids (Acne Meds):</b> Combining doxycycline with oral retinoids like isotretinoin (Accutane) or acitretin significantly increases the risk of intracranial hypertension (pseudotumor cerebri), a serious condition involving increased pressure around the brain.</div>

                    <div class="usage-item"><b>Blood Thinners (Warfarin):</b> Doxycycline can enhance the effect of warfarin, increasing the risk of serious bleeding. Patients typically require more frequent INR monitoring and potential dose adjustments.</div>

                    <div class="usage-item"><b>Seizure Medications:</b> Drugs such as phenytoin, carbamazepine, and phenobarbital can cause the body to process doxycycline faster, potentially leading to an undertreated infection.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #22c55e;">🍎 Food-Drug Interactions</div>

            <div class="food-box">

                <div class="usage-list">

                    <div class="usage-item">

                        <span class="usage-title">Dairy Products & Calcium-Rich Foods:</span>

                        <span>The calcium in dairy binds to doxycycline in the gut, forming an insoluble complex (a process called chelation) that the body cannot absorb. Avoid milk, cheese, yogurt, and ice cream within 2 hours before or after your dose. Calcium in milk, cheese, and yogurt can reduce bioavailability by approximately 30%.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Fortified Foods:</span>

                        <span>Be cautious with calcium-fortified orange juice or plant milks (almond, soy) as they can have the same effect.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Alcohol Consumption:</span>

                        <span>Regular, heavy alcohol consumption can speed up the metabolism of doxycycline, causing it to leave your system too quickly and potentially failing to treat the infection. It is generally recommended to avoid alcohol during treatment to minimize side effects like dizziness and to support your immune system.</span>

                    </div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header">📊 Summary Table for Study</div>

            <table class="summary-table">

                <thead>

                    <tr>

                        <th>Category</th>

                        <th>Clinical Efficacy & Profile</th>

                    </tr>

                </thead>

                <tbody>

                    <tr>

                        <td class="param-name">General Safety</td>

                        <td>Doxycycline is generally well-tolerated. A meta-analysis of 67 studies found that while mild adverse events (gastrointestinal and dermatological) are reported in up to 50% of patients, severe reactions are rare (0%-14%).</td>

                    </tr>

                    <tr>

                        <td class="param-name">STI Prevention (Doxy-PEP)</td>

                        <td>Landmark trials (e.g., DoxyPEP study) have shown that a single 200mg dose taken within 72 hours of unprotected sex reduces the risk of syphilis and chlamydia by 80-90% and gonorrhea by ~50% in high-risk populations.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Dermatology</td>

                        <td>It is considered the first-line systemic antibiotic for moderate-to-severe acne vulgaris due to its dual antimicrobial and anti-inflammatory properties.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Malaria Prophylaxis</td>

                        <td>Studies have demonstrated protection rates exceeding 93% in travelers to chloroquine-resistant areas when taken daily.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Lyme Disease</td>

                        <td>It is as effective as other first-line agents (like amoxicillin) for treating early Lyme disease, with the added benefit of covering common co-infections like Ehrlichia.</td>

                    </tr>

                </tbody>

            </table>

        </div>



        <div class="section-divider">

            <div class="section-header">🏢 Common Brand Names (India)</div>

            <div class="study-box">

                <ul style="line-height: 1.8; color: #555;">

                    <li><b>Doxy-1 / Doxy-1 L-DR:</b> One of the most widely recognized brands in India, manufactured by USV Private Limited.</li>

                    <li><b>Doxt-SL:</b> A popular combination of doxycycline and Lactic Acid Bacillus from Ranbaxy (Sun Pharma).</li>

                    <li><b>Lenteclin:</b> Produced by Aristo Pharmaceuticals.</li>

                    <li><b>Minicycline:</b> A common brand from Shreya Life Sciences.</li>

                    <li><b>Microdox:</b> Often used for skin conditions and acne, from Micro Labs.</li>

                    <li><b>Doxicip:</b> A reliable generic version from Cipla.</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #0ea5e9;">💉 IV Infusion Dosing</div>

            <div class="study-box" style="border-left-color: #0ea5e9; background-color: #f0f9ff;">

                <span class="study-title" style="color: #0369a1;">Standard IV Administration:</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Approved Route:</b> For patients who cannot take the medication orally, the only approved parenteral route for humans is intravenous (IV) infusion.</div>

                    <div class="usage-item"><b>Adults:</b> The initial dose is followed by daily maintenance doses, with amounts determined by a healthcare provider based on the severity of the infection.</div>

                    <div class="usage-item"><b>Pediatrics (>8 years):</b> Dosage is often calculated based on weight, with children above a certain weight threshold typically receiving adult dosages, while those below require lower amounts as determined by a pediatrician.</div>

                    <div class="usage-item"><b>Severe Infections:</b> For severe cases, providers may adjust the administration frequency, such as splitting the total daily amount into two doses.</div>

                    <div class="usage-item"><b>Administration Risks:</b> It must be highly diluted and infused slowly, typically over a period of 1 to 4 hours. Rapid IV injection is dangerous and can lead to sudden collapse, vertigo, or facial flushing.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff;">💊 Oral Dosing</div>

            <div class="study-box" style="border-left-color: #007bff;">

                <span class="study-title">Important Considerations</span>

                <div class="usage-list">

                    <div class="usage-item"><b>General Use:</b> It is generally taken to manage various bacterial infections, inflammatory conditions, and for certain prophylaxis scenarios.</div>

                    <div class="usage-item"><b>Dosage Variations:</b> Oral doxycycline dosage depends heavily on the condition being treated and the specific salt formulation used.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ff9800;">💪 Intramuscular Dosing</div>

            <div class="im-box">

                <div class="usage-list">

                    <div class="usage-item"><b>Strict Contraindication:</b> Doxycycline is not administered by intramuscular (IM) injection.</div>

                    <div class="usage-item"><b>Guidelines:</b> Official prescribing information and clinical guidelines explicitly state that intravenous (IV) solutions of doxycycline should not be injected intramuscularly or subcutaneously.</div>

                    <div class="usage-item"><b>Tissue Damage:</b> Such an administration can cause severe local tissue irritation and damage.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #10b981;">👴 Geriatric Dose Adjustment</div>

            <div class="study-box" style="border-left-color: #10b981;">

                <span class="study-title" style="color: #047857;">Dosage Considerations (Age 65+):</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Routine Adjustment:</b> For patients aged 65 and older, no routine dose adjustment is typically required for doxycycline.</div>

                    <div class="usage-item"><b>Safety Profile:</b> Unlike many other antibiotics, doxycycline is notably safe for the elderly due to its unique excretion profile.</div>

                </div>

            </div>

        </div>



        <center style="margin-top: 50px; margin-bottom: 30px;">

            <a href="/drugs-store/allopathy" style="text-decoration: none;">

                <button style="padding: 15px 40px; cursor: pointer; background: linear-gradient(135deg, #2c3e50 0%, #000 100%); color: #fff; border: none; border-radius: 30px; font-weight: bold; font-size: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">Back to Products</button>

            </a>

        </center>

    </div>

    """

    return f"<!DOCTYPE html><html><head><title>Doxycycline - Professional Profile</title></head><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



def page_metronidazole_detail(user, lang):

    content = f"""

    <style>

        .med-container {{ max-width: 850px; margin: 30px auto; padding: 40px; background: #fff; font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #000; }}

        .med-title {{ font-size: 2rem; font-weight: bold; margin-bottom: 25px; text-transform: uppercase; border-bottom: 3px solid #009688; padding-bottom: 10px; text-align: center; color: #2c3e50; }}

        .info-label {{ font-weight: bold; margin-top: 22px; display: block; font-size: 1.1rem; color: #2c3e50; }}

        .info-text {{ margin-bottom: 15px; display: block; color: #333; }}

        .structure-box {{ text-align: center; margin: 40px 0; padding: 20px; background: #fdfdfd; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}

        .structure-img {{ max-width: 100%; height: auto; border-radius: 5px; }}

        

        .usage-list {{ margin-top: 10px; padding-left: 0; list-style-type: none; }}

        .usage-item {{ margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #eee; }}

        .usage-title {{ font-weight: bold; display: block; color: #2c3e50; }}

        

        .section-divider {{ border-top: 2px solid #eee; margin-top: 40px; padding-top: 25px; }}

        .section-header {{ font-size: 1.4rem; font-weight: bold; color: #2c3e50; margin-bottom: 15px; text-transform: uppercase; display: flex; align-items: center; }}

        

        /* Box Styles */

        .warning-box {{ background-color: #fff5f5; border-left: 5px solid #e53e3e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(229, 62, 62, 0.1); }}

        .warning-title {{ color: #c53030; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .interaction-box {{ background-color: #fffaf0; border-left: 5px solid #ed8936; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(237, 137, 54, 0.1); }}

        .food-box {{ background-color: #f0fdf4; border-left: 5px solid #22c55e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(34, 197, 94, 0.1); }}

        .study-box {{ background-color: #f8f9fa; border-left: 5px solid #6c757d; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(108, 117, 125, 0.1); }}

        .im-box {{ background-color: #fff3e0; border-left: 5px solid #ff9800; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(255, 152, 0, 0.1); }}



        .summary-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background-color: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}

        .summary-table th, .summary-table td {{ border: 1px solid #eee; padding: 15px; text-align: left; font-size: 0.95rem; }}

        .summary-table th {{ background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%); color: white; text-transform: uppercase; letter-spacing: 1px; }}

        .summary-table tr:nth-child(even) {{ background-color: #fcfcfc; }}

        .param-name {{ font-weight: bold; color: #2c3e50; width: 35%; background-color: #f8f9fa; }}

    </style>



    <div class="med-container">

        <div class="med-title">METRONIDAZOLE</div>



        <div class="section-header">🧪 Chemical Structure and IUPAC Name</div>

        

        <span class="info-label">IUPAC Name:</span>

        <span class="info-text">2-(2-methyl-5-nitro-1H-imidazol-1-yl)ethanol</span>



        <table class="summary-table">

            <thead>

                <tr>

                    <th>Property</th>

                    <th>Value</th>

                </tr>

            </thead>

            <tbody>

                <tr>

                    <td class="param-name">Molecular Weight</td>

                    <td>171.15 g/mol.</td>

                </tr>

                <tr>

                    <td class="param-name">Core Ring</td>

                    <td>It features a five-membered imidazole ring (a heterocyclic ring containing two nitrogen atoms).</td>

                </tr>

                <tr>

                    <td class="param-name">Nitro Group (5-position)</td>

                    <td>Essential for its antimicrobial activity, as it is reduced within anaerobic cells to create toxic free radicals.</td>

                </tr>

                <tr>

                    <td class="param-name">Other Groups</td>

                    <td>Methyl Group attached at the 2-position. Ethanol Side Chain attached to the nitrogen at the 1-position.</td>

                </tr>

            </tbody>

        </table>



        <div class="structure-box">

            <img src="/static/metronidazole_structure.png" class="structure-img" alt="Metronidazole Structure" onerror="this.src='https://placehold.co/400x300?text=Metronidazole+Structure'">

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff;">💊 Therapeutic Uses</div>

            <div class="study-box" style="border-left-color: #007bff;">

                <div class="usage-list">

                    <div class="usage-item"><b>Bacterial Vaginosis (BV):</b> A common use for treating vaginal overgrowth of harmful bacteria.</div>

                    <div class="usage-item"><b>Intra-abdominal Infections:</b> Often used in combination with other antibiotics to treat peritonitis or intra-abdominal abscesses.</div>

                    <div class="usage-item"><b>Gastrointestinal Infections:</b> Previously a mainstay for Clostridioides difficile (C. diff) infection, though now primarily reserved for non-severe initial cases.</div>

                    <div class="usage-item"><b>Pelvic Inflammatory Disease (PID):</b> Frequently added to multi-drug regimens to provide coverage against anaerobic organisms.</div>

                    <div class="usage-item"><b>Dental Infections:</b> Used for acute orofacial infections, dental abscesses, and severe gum diseases like periodontitis.</div>

                    <div class="usage-item"><b>Surgical Prophylaxis:</b> Administered preoperatively (especially for colorectal or gynecological surgeries) to prevent postoperative anaerobic infections.</div>

                    <div class="usage-item"><b>Helicobacter pylori Eradication:</b> Part of a multi-drug "triple" or "quadruple" therapy to treat stomach ulcers.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #6f42c1;">⚠️ Adverse Drug Reaction (ADR)</div>

            <div class="study-box" style="border-left-color: #6f42c1; background-color: #f3e5f5;">

                <span class="usage-title" style="color: #4a148c;">Common Side Effects</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Gastrointestinal:</b> Nausea (up to 12%), vomiting, diarrhea (up to 4%), and abdominal cramping. Taking the drug with food can often mitigate stomach upset.</div>

                    <div class="usage-item"><b>Dysgeusia:</b> A sharp, unpleasant metallic taste in the mouth is reported by approximately 9% of patients.</div>

                    <div class="usage-item"><b>Neurological:</b> Headaches are the most common side effect, affecting up to 18% of users. Dizziness and drowsiness are also frequent.</div>

                </div>

            </div>

            

            <div class="warning-box">

                <span class="warning-title">Severe & Rare Warnings</span>

                <div class="usage-list" style="margin-top: 10px;">

                    <div class="usage-item"><b>Hepatotoxicity:</b> Severe, potentially fatal liver injury has been reported, especially in patients with Cockayne syndrome.</div>

                    <div class="usage-item"><b>Severe Skin Reactions:</b> Rare instances of Stevens-Johnson Syndrome (SJS) or Toxic Epidermal Necrolysis (TEN) marked by blistering or peeling skin.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ed8936;">🤝 Drug-Drug Interactions</div>

            <div class="interaction-box">

                <div class="usage-list">

                    <div class="usage-item"><b>Alcohol (Disulfiram-like Reaction):</b> Metronidazole inhibits aldehyde dehydrogenase, the enzyme that breaks down alcohol. This causes toxic acetaldehyde to build up in the blood.</div>

                    <div class="usage-item"><b>Warfarin (Blood Thinner):</b> Metronidazole inhibits the metabolism of the more active S-warfarin, increasing bleeding risks.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #22c55e;">🍎 Food-Drug Interactions</div>

            <div class="food-box">

                <div class="usage-list">

                    <div class="usage-item">

                        <span class="usage-title">The Alcohol Rule (Non-Negotiable):</span>

                        <span>You must strictly avoid alcohol and products containing propylene glycol during treatment and for at least 3 days (72 hours) after your last dose.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Immediate-Release (Standard Tablets/Capsules):</span>

                        <span>Can be taken with or without food. If the medication causes an upset stomach, taking it with a meal or snack (like crackers or toast) may help reduce gastrointestinal side effects.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Extended-Release (ER) Tablets:</span>

                        <span>These must be taken on an empty stomach, either 1 hour before or 2 hours after a meal. Do not crush or chew ER tablets, as this can affect how the drug is absorbed.</span>

                    </div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header">📊 Summary Table for Study</div>

            <table class="summary-table">

                <thead>

                    <tr>

                        <th>Category</th>

                        <th>Clinical Efficacy & Profile</th>

                    </tr>

                </thead>

                <tbody>

                    <tr>

                        <td class="param-name">Standard Dosing</td>

                        <td>Typical adult dosing for anaerobic infections is 500 mg every 6 to 8 hours, with a maximum daily limit of 4 grams.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Bacterial Vaginosis (BV)</td>

                        <td>Clinical trials show that single-dose vaginal gel (1.3%) is as effective as multi-day oral regimens but with significantly fewer gastrointestinal side effects.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Pediatrics</td>

                        <td>Recent studies supported a labeling update for infants under 4 months; dosing is weight-based (e.g. 15 mg/kg loading dose) followed by maintenance every 6-12 hours depending on age.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Absorption</td>

                        <td>Food may slightly delay reaching peak blood levels but does not reduce the total amount of drug absorbed.</td>

                    </tr>

                </tbody>

            </table>

        </div>



        <div class="section-divider">

            <div class="section-header">🏢 Common Brand Names (India)</div>

            <div class="study-box">

                <ul style="line-height: 1.8; color: #555;">

                    <li><b>Metrogyl:</b> Manufactured by J.B. Chemicals & Pharmaceuticals, this is perhaps the most ubiquitous brand in the country. Available as tablets, ER, Suspension, and IV.</li>

                    <li><b>Flagyl:</b> Manufactured by Sanofi (and marketed by Abbott in some regions), this is the global innovator brand and remains a staple in Indian healthcare.</li>

                    <li><b>Aristogyl:</b> Produced by Aristo Pharmaceuticals, it is a very common and cost-effective alternative frequently found in pharmacies.</li>

                    <li><b>Metron:</b> A popular brand from Cipla, often used for gastrointestinal and dental infections.</li>

                    <li><b>Aldezol:</b> A well-known brand from Albert David Ltd.</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #0ea5e9;">💉 IV Infusion Dosing</div>

            <div class="study-box" style="border-left-color: #0ea5e9; background-color: #f0f9ff;">

                <span class="study-title" style="color: #0369a1;">Standard Adult Dosing:</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Loading & Maintenance:</b> An initial loading dose is typically administered, followed by a maintenance dose infused over an hour, scheduled often every 6 hours depending on clinical judgment.</div>

                    <div class="usage-item"><b>Maximum Dose:</b> Total daily administration is monitored to avoid exceeding recommended 24-hour limits.</div>

                    <div class="usage-item"><b>Surgical Prophylaxis:</b> An initial infusion is typically completed before the first incision. Additional doses are administered postoperatively (generally limited to the day of surgery).</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff;">💊 Oral Dosing</div>

            <div class="study-box" style="border-left-color: #007bff;">

                <span class="study-title">Important Considerations</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Administration with Food:</b> Standard immediate-release tablets and capsules can be taken with food to help reduce potential stomach upset.</div>

                    <div class="usage-item"><b>Extended-Release Formulation:</b> Extended-release (ER) tablets are designed to be taken on an empty stomach, typically one hour before or two hours after a meal. ER tablets should be swallowed whole and not broken, crushed, or chewed.</div>

                    <div class="usage-item"><b>Treatment Completion:</b> It is important to complete the entire course of medication as prescribed, even if symptoms improve, to ensure the infection is fully treated and to prevent recurrence.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ff9800;">💪 Intramuscular Dosing</div>

            <div class="im-box">

                <div class="usage-list">

                    <div class="usage-item"><b>Strict Contraindication:</b> Metronidazole is not administered via intramuscular (IM) injection.</div>

                    <div class="usage-item"><b>Formulation Constraints:</b> The standard parenteral formulation of metronidazole is a large-volume, ready-to-use intravenous infusion (typically 500 mg in 100 mL of solution). This volume is far too large for a single intramuscular injection (usually limited to 1-5 mL).</div>

                    <div class="usage-item"><b>Tissue Irritation:</b> Highly concentrated or large-volume injections into muscle tissue can cause significant pain, tissue damage, or abscess formation.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #10b981;">👴 Geriatric Dose Adjustment</div>

            <div class="study-box" style="border-left-color: #10b981;">

                <span class="study-title" style="color: #047857;">Dosage Considerations (Age 65+):</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Routine Adjustment:</b> For patients aged 65 and older, metronidazole typically does not require an automatic dose reduction based on age alone, but cautious dosing and close monitoring are recommended.</div>

                    <div class="usage-item"><b>Liver Function:</b> The liver is the primary organ that metabolizes metronidazole. Older adults are more likely to have decreased hepatic function. In cases of severe hepatic impairment (Child-Pugh C), clinicians may consider lower doses.</div>

                    <div class="usage-item"><b>Active Metabolites:</b> Studies show that in patients over 70, the concentration of the drug's active metabolite can be higher than in younger adults, even with normal kidney and liver tests.</div>

                    <div class="usage-item"><b>Kidney Function:</b> While metronidazole itself is not heavily cleared by the kidneys, its metabolites are. In severe renal impairment, these metabolites can accumulate.</div>

                </div>

            </div>

        </div>



        <center style="margin-top: 50px; margin-bottom: 30px;">

            <a href="/drugs-store/allopathy" style="text-decoration: none;">

                <button style="padding: 15px 40px; cursor: pointer; background: linear-gradient(135deg, #2c3e50 0%, #000 100%); color: #fff; border: none; border-radius: 30px; font-weight: bold; font-size: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">Back to Products</button>

            </a>

        </center>

    </div>

    """

    return f"<!DOCTYPE html><html><head><title>Metronidazole - Professional Profile</title></head><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



def page_fluconazole_detail(user, lang):

    content = f"""

    <style>

        .med-container {{ max-width: 850px; margin: 30px auto; padding: 40px; background: #fff; font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #000; }}

        .med-title {{ font-size: 2rem; font-weight: bold; margin-bottom: 25px; text-transform: uppercase; border-bottom: 3px solid #1e88e5; padding-bottom: 10px; text-align: center; color: #2c3e50; }}

        .info-label {{ font-weight: bold; margin-top: 22px; display: block; font-size: 1.1rem; color: #2c3e50; }}

        .info-text {{ margin-bottom: 15px; display: block; color: #333; }}

        .structure-box {{ text-align: center; margin: 40px 0; padding: 20px; background: #fdfdfd; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}

        .structure-img {{ max-width: 100%; height: auto; border-radius: 5px; }}

        

        .usage-list {{ margin-top: 10px; padding-left: 0; list-style-type: none; }}

        .usage-item {{ margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #eee; }}

        .usage-title {{ font-weight: bold; display: block; color: #2c3e50; }}

        

        .section-divider {{ border-top: 2px solid #eee; margin-top: 40px; padding-top: 25px; }}

        .section-header {{ font-size: 1.4rem; font-weight: bold; color: #2c3e50; margin-bottom: 15px; text-transform: uppercase; display: flex; align-items: center; }}

        

        /* Box Styles */

        .warning-box {{ background-color: #fff5f5; border-left: 5px solid #e53e3e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(229, 62, 62, 0.1); }}

        .warning-title {{ color: #c53030; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .interaction-box {{ background-color: #fffaf0; border-left: 5px solid #ed8936; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(237, 137, 54, 0.1); }}

        .food-box {{ background-color: #f0fdf4; border-left: 5px solid #22c55e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(34, 197, 94, 0.1); }}

        .study-box {{ background-color: #f8f9fa; border-left: 5px solid #6c757d; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(108, 117, 125, 0.1); }}

        .im-box {{ background-color: #fff3e0; border-left: 5px solid #ff9800; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(255, 152, 0, 0.1); }}



        .summary-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background-color: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}

        .summary-table th, .summary-table td {{ border: 1px solid #eee; padding: 15px; text-align: left; font-size: 0.95rem; }}

        .summary-table th {{ background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%); color: white; text-transform: uppercase; letter-spacing: 1px; }}

        .summary-table tr:nth-child(even) {{ background-color: #fcfcfc; }}

        .param-name {{ font-weight: bold; color: #2c3e50; width: 35%; background-color: #f8f9fa; }}

    </style>



    <div class="med-container">

        <div class="med-title">FLUCONAZOLE</div>



        <div class="section-header">🧪 Chemical Structure and IUPAC Name</div>

        

        <span class="info-label">Molecular Formula:</span>

        <span class="info-text">C13H12F2N6O</span>



        <table class="summary-table">

            <thead>

                <tr>

                    <th>Component</th>

                    <th>Detail</th>

                </tr>

            </thead>

            <tbody>

                <tr>

                    <td class="param-name">Basic Backbone</td>

                    <td>Contains a central propan-2-ol chain.</td>

                </tr>

                <tr>

                    <td class="param-name">Triazole Groups</td>

                    <td>Features two 1H-1,2,4-triazol-1-ylmethyl elements.</td>

                </tr>

                <tr>

                    <td class="param-name">Phenyl Group</td>

                    <td>A 2,4-difluorophenyl group is linked at the second carbon position.</td>

                </tr>

            </tbody>

        </table>



        <div class="structure-box">

            <img src="/static/fluconazole_structure.png" class="structure-img" alt="Fluconazole Structure" onerror="this.src='https://placehold.co/400x300?text=Fluconazole+Structure'">

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff;">💊 Therapeutic Uses</div>

            <div class="study-box" style="border-left-color: #007bff;">

                <div class="usage-list">

                    <div class="usage-item"><b>Candidiasis (Yeast Infections):</b> Used for Vaginal Thrush (usually a single 150mg oral tablet), Mucosal infections (oral or esophageal thrush), and Systemic/Invasive issues like candidemia (bloodstream) and lung pneumonia. Also effective for Candida-related UTIs and peritonitis.</div>

                    <div class="usage-item"><b>Cryptococcal Meningitis:</b> Serves as both primary therapy and long-term maintenance to stop relapse, especially in HIV/AIDS patients.</div>

                    <div class="usage-item"><b>Dermatophytosis (Skin Fungi):</b> Treats Tinea corporis (ringworm), Tinea cruris (jock itch), Tinea pedis (athlete's foot), and Onychomycosis (fungal nail issues).</div>

                    <div class="usage-item"><b>Deep Endemic Mycoses:</b> Utilized for Valley fever (coccidioidomycosis), histoplasmosis, and blastomycosis.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #6f42c1;">⚠️ Adverse Drug Reaction (ADR)</div>

            <div class="study-box" style="border-left-color: #6f42c1; background-color: #f3e5f5;">

                <span class="usage-title" style="color: #4a148c;">Common Side Effects</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Gastrointestinal:</b> Nausea (up to 7%), abdominal discomfort (6%), diarrhea (3%), and vomiting (2%).</div>

                    <div class="usage-item"><b>Nervous System:</b> Headaches are highly common (up to 13%). Dizziness and altered taste sensation can also happen.</div>

                    <div class="usage-item"><b>Dermatologic:</b> Mild rashes on the skin.</div>

                </div>

            </div>

            

            <div class="warning-box">

                <span class="warning-title">Severe & Rare Warnings</span>

                <div class="usage-list" style="margin-top: 10px;">

                    <div class="usage-item"><b>Heart Rhythm Issues:</b> Risk of QT interval prolongation, leading to a dangerous condition called torsades de pointes.</div>

                    <div class="usage-item"><b>Severe Skin Reactions:</b> Life-threatening conditions like Stevens-Johnson Syndrome (SJS) and Toxic Epidermal Necrolysis (TEN), causing blistering and peeling.</div>

                    <div class="usage-item"><b>Adrenal Insufficiency:</b> Might lower cortisol production, causing severe weakness, weight loss, and lack of appetite.</div>

                    <div class="usage-item"><b>Allergic Reactions:</b> Anaphylactic shock including difficulty breathing and swelling of the throat/lips/face.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ed8936;">🤝 Drug-Drug Interactions</div>

            <div class="interaction-box">

                <p style="font-weight:bold; color:#c53030;">Strictly Contraindicated (Do NOT Mix):</p>

                <p>Using this medicine with the following drugs triggers severe, life-threatening heart rhythm abnormalities (QT prolongation):</p>

                <div class="usage-list">

                    <div class="usage-item"><b>Antibiotics:</b> Erythromycin and Clarithromycin.</div>

                    <div class="usage-item"><b>Antipsychotics:</b> Pimozide, Quetiapine, and Haloperidol.</div>

                    <div class="usage-item"><b>Heart Rhythm Drugs:</b> Amiodarone, Quinidine, and Disopyramide.</div>

                    <div class="usage-item"><b>GI Stimulants:</b> Cisapride.</div>

                    <div class="usage-item"><b>Antihistamines:</b> Astemizole and Terfenadine (if dose is 400mg or more).</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #22c55e;">🍎 Food-Drug Interactions</div>

            <div class="food-box">

                <div class="usage-list">

                    <div class="usage-item">

                        <span class="usage-title">General Absorption:</span>

                        <span>Unlike many antifungals, food does not change how this drug is absorbed. It can be taken safely with or without meals. Dairy products and grapefruit juice also do not block its absorption.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Caffeine Intake:</span>

                        <span>This medication slows the breakdown of caffeine in the body by nearly 25%. This can increase jitteriness, heart racing, and sleep issues.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Alcohol Consumption:</span>

                        <span>There is no immediate "disulfiram-like" illness (vomiting) when mixed. However, since both alcohol and this drug strain the liver, combining them increases liver toxicity and worsens dizziness.</span>

                    </div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header">📊 Summary Table for Study</div>

            <table class="summary-table">

                <thead>

                    <tr>

                        <th>Metric</th>

                        <th>Clinical Finding</th>

                    </tr>

                </thead>

                <tbody>

                    <tr>

                        <td class="param-name">Bioavailability</td>

                        <td>Excellent (greater than 90%); IV and oral dosages are fully interchangeable.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Side Effect Rate</td>

                        <td>Overall low (around 6 to 16%). Headache (13%) and stomach upset are top complaints.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Serious Risks</td>

                        <td>Extremely rare occurrences of liver toxicity (less than 1%) and QT prolongation.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Resistance Profile</td>

                        <td>Resistance is emerging in C. glabrata and C. krusei. Long-term use can create resistance in C. albicans.</td>

                    </tr>

                </tbody>

            </table>

        </div>



        <div class="section-divider">

            <div class="section-header">🏢 Common Brand Names (India)</div>

            <div class="study-box">

                <ul style="line-height: 1.8; color: #555;">

                    <li><b>Forcan:</b> Made by Cipla Ltd, one of the most trusted and prescribed options.</li>

                    <li><b>Zocon:</b> Made by FDC Ltd, a very common household name for treating standard fungal issues.</li>

                    <li><b>Fusys:</b> Made by Zydus Healthcare Limited, known for fast action against yeast overgrowth.</li>

                    <li><b>Syscan:</b> Made by Torrent Pharmaceuticals Ltd, recognized for broad clinical reliability.</li>

                    <li><b>Onecan:</b> Made by Wallace Pharmaceuticals, heavily used by dermatologists for nail and skin fungi.</li>

                    <li><b>AF:</b> Produced by Systopic Laboratories (often seen in 150mg and 400mg variants).</li>

                    <li><b>Fluka & Flutas:</b> Made by Cipla and Intas respectively, used for high-dose treatments.</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #0ea5e9;">💉 IV Infusion Dosing</div>

            <div class="study-box" style="border-left-color: #0ea5e9; background-color: #f0f9ff;">

                <span class="study-title" style="color: #0369a1;">Adult Protocols:</span>

                <div class="usage-list">

                    <div class="usage-item"><b>General Strategy:</b> Treatment usually begins with a high loading dose to reach optimal blood concentration quickly, followed by physician-determined daily maintenance amounts.</div>

                    <div class="usage-item"><b>Invasive vs Mucosal:</b> Invasive candidiasis needs high daily amounts, whereas esophageal or oral thrush needs lower daily amounts.</div>

                    <div class="usage-item"><b>Meningitis & UTI:</b> Moderate to high doses for Cryptococcal issues; variable dosing for urinary tract infections based on severity.</div>

                </div>



                <span class="study-title" style="color: #0369a1; margin-top: 20px;">Pediatric Protocols (4 Weeks to 11 Years):</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Dosing Metric:</b> Strictly weight-based and personalized by a pediatrician.</div>

                    <div class="usage-item"><b>Mucosal & Invasive:</b> Mucosal issues start with a loading dose then daily upkeep. Invasive and meningitis cases are strictly calculated per kg of body weight daily.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff;">💊 Oral Dosing</div>

            <div class="study-box" style="border-left-color: #007bff;">

                <div class="usage-list">

                    <div class="usage-item"><b>Vaginal Thrush:</b> Standard protocol is a single dose. Recurrent cases might require weekly doses over a longer period.</div>

                    <div class="usage-item"><b>Oral/Esophageal Thrush:</b> Daily pill consumption for several weeks is standard.</div>

                    <div class="usage-item"><b>Systemic Fungi:</b> Issues like Cryptococcal Meningitis need daily oral intake for weeks.</div>

                    <div class="usage-item"><b>Skin & Nails:</b> Ringworm, athlete's foot, and nail fungi are commonly treated with a once-a-week pill for several weeks or even months.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ff9800;">💪 Intramuscular Dosing</div>

            <div class="im-box">

                <div class="usage-list">

                    <div class="usage-item"><b>Strict Contraindication:</b> There is absolutely zero intramuscular (IM) dosing for this drug.</div>

                    <div class="usage-item"><b>Available Formulations:</b> It is manufactured exclusively for oral ingestion (tablets/liquids) or direct intravenous (IV) infusion due to specific clinical constraints.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #10b981;">👴 Geriatric Dose Adjustment</div>

            <div class="study-box" style="border-left-color: #10b981;">

                <span class="study-title" style="color: #047857;">Dosage Considerations (Age 65+):</span>

                <div class="usage-list">

                    <div class="usage-item"><b>Renal Dependency:</b> For elderly patients, dose modifications are based completely on kidney function rather than numerical age. The drug exits the body mostly unchanged via the kidneys.</div>

                    <div class="usage-item"><b>Risk of Toxicity:</b> Any age-related drop in kidney performance can cause the drug to build up dangerously in the system.</div>

                    <div class="usage-item"><b>Clearance Calculation:</b> Doctors must calculate Creatinine Clearance (CrCl) to adjust the dose. Simple serum creatinine tests are not enough as they underestimate kidney decline in older adults. If renal function is normal, standard doses apply.</div>

                </div>

            </div>

        </div>



        <center style="margin-top: 50px; margin-bottom: 30px;">

            <a href="/drugs-store/allopathy" style="text-decoration: none;">

                <button style="padding: 15px 40px; cursor: pointer; background: linear-gradient(135deg, #2c3e50 0%, #000 100%); color: #fff; border: none; border-radius: 30px; font-weight: bold; font-size: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">Back to Products</button>

            </a>

        </center>

    </div>

    """

    return f"<!DOCTYPE html><html><head><title>Fluconazole - Professional Profile</title></head><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



def page_lisinopril_detail(user, lang):

    content = f"""

    <style>

        .med-container {{ max-width: 850px; margin: 30px auto; padding: 40px; background: #fff; font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #000; }}

        .med-title {{ font-size: 2rem; font-weight: bold; margin-bottom: 25px; text-transform: uppercase; border-bottom: 3px solid #009688; padding-bottom: 10px; text-align: center; color: #2c3e50; }}

        .info-label {{ font-weight: bold; margin-top: 22px; display: block; font-size: 1.1rem; color: #2c3e50; }}

        .info-text {{ margin-bottom: 15px; display: block; color: #333; }}

        .structure-box {{ text-align: center; margin: 40px 0; padding: 20px; background: #fdfdfd; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}

        .structure-img {{ max-width: 100%; height: auto; border-radius: 5px; }}

        

        .usage-list {{ margin-top: 10px; padding-left: 0; list-style-type: none; }}

        .usage-item {{ margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #eee; }}

        .usage-title {{ font-weight: bold; display: block; color: #2c3e50; }}

        

        .section-divider {{ border-top: 2px solid #eee; margin-top: 40px; padding-top: 25px; }}

        .section-header {{ font-size: 1.4rem; font-weight: bold; color: #2c3e50; margin-bottom: 15px; text-transform: uppercase; display: flex; align-items: center; }}

        

        /* Box Styles */

        .warning-box {{ background-color: #fff5f5; border-left: 5px solid #e53e3e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(229, 62, 62, 0.1); }}

        .warning-title {{ color: #c53030; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; display: block; }}

        .interaction-box {{ background-color: #fffaf0; border-left: 5px solid #ed8936; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(237, 137, 54, 0.1); }}

        .food-box {{ background-color: #f0fdf4; border-left: 5px solid #22c55e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(34, 197, 94, 0.1); }}

        .study-box {{ background-color: #f8f9fa; border-left: 5px solid #6c757d; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(108, 117, 125, 0.1); }}

        .im-box {{ background-color: #fff3e0; border-left: 5px solid #ff9800; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(255, 152, 0, 0.1); }}



        .summary-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background-color: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}

        .summary-table th, .summary-table td {{ border: 1px solid #eee; padding: 15px; text-align: left; font-size: 0.95rem; }}

        .summary-table th {{ background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%); color: white; text-transform: uppercase; letter-spacing: 1px; }}

        .summary-table tr:nth-child(even) {{ background-color: #fcfcfc; }}

        .param-name {{ font-weight: bold; color: #2c3e50; width: 35%; background-color: #f8f9fa; }}

    </style>



    <div class="med-container">

        <div class="med-title">LISINOPRIL</div>



        <div class="section-header">🧪 Chemical Structure and IUPAC Name</div>

        

        <span class="info-label">IUPAC Name:</span>

        <span class="info-text">(2S)-1-[(2S)-6-amino-2-{{[(1S)-1-carboxy-3-phenylpropyl] amino}}hexanoyl] pyrrolidine-2-carboxylic acid</span>



        <table class="summary-table">

            <thead>

                <tr>

                    <th>Chemical Structure and Formula</th>

                    <th>Details</th>

                </tr>

            </thead>

            <tbody>

                <tr>

                    <td class="param-name">Chemical State</td>

                    <td>Lisinopril is most commonly used in its dihydrate form, which is its most stable crystalline state.</td>

                </tr>

                <tr>

                    <td class="param-name">Empirical Formula (Anhydrous)</td>

                    <td>C21H31N305</td>

                </tr>

                <tr>

                    <td class="param-name">Empirical Formula (Dihydrate)</td>

                    <td>C21H31N3O5.2H2O</td>

                </tr>

                <tr>

                    <td class="param-name">Molecular Weight</td>

                    <td>405.5 g/mol (Anhydrous) or 441.52 g/mol (Dihydrate)</td>

                </tr>

            </tbody>

        </table>



        <div class="structure-box">

            <img src="/static/lisinopril_structure.png" class="structure-img" alt="Lisinopril Structure" onerror="this.src='https://placehold.co/400x300?text=Lisinopril+Structure'">

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff;">💊 Therapeutic Uses</div>

            <div class="study-box" style="border-left-color: #007bff;">

                <div class="usage-list">

                    <div class="usage-item"><b>Hypertension (High Blood Pressure):</b> It is used alone or in combination with other medications (like diuretics) to lower blood pressure in adults and children aged 6 years and older.</div>

                    <div class="usage-item"><b>Heart Failure:</b> It serves as an adjunctive therapy (usually alongside diuretics and digitalis) to manage symptoms and improve survival in patients with congestive heart failure.</div>

                    <div class="usage-item"><b>Acute Myocardial Infarction (Heart Attack):</b> Administered within 24 hours of a heart attack, it helps improve survival rates and prevents further heart muscle damage.</div>

                    <div class="usage-item"><b>Diabetic Nephropathy:</b> It is widely used to slow the progression of kidney disease in patients with Type 2 diabetes and high blood pressure.</div>

                    <div class="usage-item"><b>Proteinuria:</b> It helps reduce protein in the urine, particularly in patients with IgA nephropathy.</div>

                    <div class="usage-item"><b>Diabetic Retinopathy:</b> Some research suggests it may help slow the progression of eye disease in diabetic patients.</div>

                    <div class="usage-item"><b>Migraine Prevention:</b> While not a first-line treatment, it is sometimes prescribed off-label to reduce the frequency of migraine attacks.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #6f42c1;">⚠️ Adverse Drug Reaction (ADR)</div>

            <div class="study-box" style="border-left-color: #6f42c1; background-color: #f3e5f5;">

                <div class="usage-list">

                    <div class="usage-item"><b>Dry Cough:</b> A persistent, non-productive tickle in the throat is one of the most well-known ACE inhibitor side effects. It may take up to a month to resolve after stopping the drug.</div>

                    <div class="usage-item"><b>Dizziness and Lightheadedness:</b> Often caused by a sudden drop in blood pressure (orthostatic hypotension), especially when standing up.</div>

                    <div class="usage-item"><b>Headache:</b> Reported as one of the most frequent side effects in clinical trials.</div>

                    <div class="usage-item"><b>Fatigue:</b> Feeling unusually tired or weak.</div>

                    <div class="usage-item"><b>Digestive Issues:</b> Including nausea, diarrhea, or an upset stomach.</div>

                </div>

            </div>

            

            <div class="warning-box">

                <span class="warning-title">Severe & Rare Warnings</span>

                <div class="usage-list" style="margin-top: 10px;">

                    <div class="usage-item"><b>Angioedema:</b> This rare but critical reaction involves rapid swelling of the face, lips, tongue, or throat, which can block the airway. It can occur after the first dose or even years into treatment.</div>

                    <div class="usage-item"><b>Hyperkalemia (High Potassium):</b> Lisinopril can cause dangerously high potassium levels, which may lead to fatal heart arrhythmias. Symptoms include muscle weakness or irregular heartbeat.</div>

                    <div class="usage-item"><b>Kidney Dysfunction:</b> In some patients, especially those with pre-existing kidney issues or heart failure, lisinopril can cause acute renal failure.</div>

                    <div class="usage-item"><b>Liver Toxicity:</b> Rarely, it can cause a syndrome starting with jaundice (yellowing of eyes/skin) that can progress to liver failure.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ed8936;">🤝 Drug-Drug Interactions</div>

            <div class="interaction-box">

                <div class="usage-list">

                    <div class="usage-item"><b>The "Triple Whammy" (Major Risk):</b> The most dangerous combination is the simultaneous use of three drug classes: ACE Inhibitors (like Lisinopril), Diuretics (e.g., Furosemide, Hydrochlorothiazide), and NSAIDs (e.g., Ibuprofen, Naproxen, Celecoxib).</div>

                    <div class="usage-item"><b>Potassium-Sparing Diuretics:</b> Avoid Spironolactone, amiloride, and triamterene.</div>

                    <div class="usage-item"><b>Potassium Supplements:</b> OTC or prescription potassium chloride.</div>

                    <div class="usage-item"><b>Salt Substitutes:</b> Many "low-sodium" salts use potassium chloride instead of sodium chloride.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #22c55e;">🍎 Food-Drug Interactions</div>

            <div class="food-box">

                <div class="usage-list">

                    <div class="usage-item">

                        <span class="usage-title">Potassium-Rich Foods:</span>

                        <span>The most critical interaction involves potassium. Lisinopril causes your kidneys to retain potassium, and adding high-potassium foods can lead to hyperkalemia (dangerously high blood potassium). Foods to Limit: Bananas, oranges, potatoes, tomatoes, avocados, spinach, and dried fruits like raisins or prunes.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Salt Substitutes:</span>

                        <span>Most "low-sodium" salt substitutes (e.g., No Salt, Morton Salt Substitute) use potassium chloride and should be avoided unless specifically approved by your doctor.</span>

                    </div>

                    <div class="usage-item">

                        <span class="usage-title">Alcohol Interactions:</span>

                        <span>Combining alcohol with lisinopril is generally discouraged for two main reasons: Excessive Hypotension. Alcohol can enhance the blood pressure-lowering effect of lisinopril, leading to extreme dizziness, lightheadedness, and fainting, especially when standing up.</span>

                    </div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header">📊 Summary Table for Study</div>

            <table class="summary-table">

                <thead>

                    <tr>

                        <th>Category</th>

                        <th>Research-Backed Therapeutic Evidence</th>

                    </tr>

                </thead>

                <tbody>

                    <tr>

                        <td class="param-name">Cardioprotection</td>

                        <td>Studies like GISSI-3 confirm that early intervention after a heart attack reduces the risk of "cardiac rupture" and "pump failure".</td>

                    </tr>

                    <tr>

                        <td class="param-name">Renoprotection</td>

                        <td>Extensive evidence shows lisinopril is highly effective for proteinuric kidney disease, offering superior outcomes in diabetic nephropathy compared to other standard treatments.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Dose Optimization</td>

                        <td>The ATLAS trial established that for heart failure, titrating to the highest tolerable dose provides significantly greater protection against hospitalisation than maintaining low doses.</td>

                    </tr>

                    <tr>

                        <td class="param-name">Safety Profile</td>

                        <td>Across large-scale trials, lisinopril showed a consistent safety profile. While it increases the risk of hypotension (low blood pressure) and renal dysfunction during the acute phase of treatment, these events are typically manageable without stopping the drug.</td>

                    </tr>

                </tbody>

            </table>

        </div>



        <div class="section-divider">

            <div class="section-header">🏢 Common Brand Names (India)</div>

            <div class="study-box">

                <ul style="line-height: 1.8; color: #555;">

                    <li><b>Listril:</b> Manufactured by Torrent Pharmaceuticals Ltd., this is one of the most widely prescribed brands.</li>

                    <li><b>Lipril:</b> Produced by Lupin Ltd.</li>

                    <li><b>Lisoril:</b> Manufactured by Ipca Laboratories Ltd.</li>

                    <li><b>Hipril:</b> Produced by Micro Labs Ltd.</li>

                    <li><b>Cipril:</b> Manufactured by Cipla Ltd.</li>

                    <li><b>Zestril:</b> Originally a global brand by AstraZeneca, it is also available in India through various suppliers.</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #0ea5e9;">💉 IV Infusion Dosing</div>

            <div class="study-box" style="border-left-color: #0ea5e9; background-color: #f0f9ff;">

                <div class="usage-list">

                    <div class="usage-item">Lisinopril is not typically administered as an IV infusion in standard clinical practice. It is primarily available as an oral tablet or oral solution.</div>

                    <div class="usage-item">If an intravenous ACE inhibitor is required (for example, in a hypertensive emergency or for patients unable to take oral medications), Enalaprilat (the active metabolite of enalapril) is the only drug in this class commonly available in an IV formulation.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff;">💊 Oral Dosing</div>

            <div class="study-box" style="border-left-color: #007bff;">

                <div class="usage-list">

                    <div class="usage-item">Lisinopril is an ACE inhibitor, often administered as a single daily oral dose, with or without food.</div>

                    <div class="usage-item">The appropriate dosage is determined by a healthcare provider based on the condition being treated, such as hypertension, heart failure, or post-myocardial infarction, as well as the patient's renal function.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ff9800;">💪 Intramuscular Dosing</div>

            <div class="im-box">

                <div class="usage-list">

                    <div class="usage-item">Lisinopril is not administered intramuscularly (IM). It is exclusively available as an oral medication, typically in the form of tablets or an oral solution.</div>

                    <div class="usage-item"><b>Why IM Dosing Does Not Exist....</b> Formulation Availability: There is no commercially manufactured intramuscular injection for lisinopril. Pharmacokinetic Profile: Lisinopril is designed for slow and steady absorption through the gastrointestinal tract, reaching peak serum concentrations in about 6 to 8 hours. Class Alternatives: If an injectable ACE inhibitor is clinically necessary (such as in a hypertensive emergency or for a patient who cannot swallow), physicians use Enalaprilat, which is the only drug in this class available for intravenous (IV) use. There is no standard IM alternative in the ACE inhibitor class.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #10b981;">👴 Geriatric Dose Adjustment</div>

            <div class="study-box" style="border-left-color: #10b981;">

                <span class="study-title" style="color: #047857;">Dosing Adjustment:</span>

                <div class="usage-list">

                    <div class="usage-item">For most geriatric patients, clinicians follow a "start low and go slow" approach with lisinopril to prevent a sudden drop in blood pressure.</div>

                    <div class="usage-item"><b>Hypertension (Normal Kidney Function):</b> Therapy is typically initiated at a lower, initial oral dose.</div>

                    <div class="usage-item"><b>Hypertension (Patients on Diuretics):</b> The starting dose is usually reduced to prevent excessive hypotension.</div>

                    <div class="usage-item"><b>Heart Failure:</b> Initial dosing often begins with a lower dose to monitor for tolerance.</div>

                    <div class="usage-item"><b>Acute Heart Attack (MI):</b> Dosing is initiated carefully within 24 hours of symptoms, with dosage adjustments made based on response.</div>

                </div>

            </div>

        </div>



        <center style="margin-top: 50px; margin-bottom: 30px;">

            <a href="/drugs-store/allopathy" style="text-decoration: none;">

                <button style="padding: 15px 40px; cursor: pointer; background: linear-gradient(135deg, #2c3e50 0%, #000 100%); color: #fff; border: none; border-radius: 30px; font-weight: bold; font-size: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">Back to Products</button>

            </a>

        </center>

    </div>

    """

    return f"<!DOCTYPE html><html><head><title>Lisinopril - Professional Profile</title></head><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



def page_amlodipine_detail(user, lang):

    content = f"""

    <style>

        .med-container {{ max-width: 850px; margin: 30px auto; padding: 40px; background: #fff; font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #000; }}

        .med-title {{ font-size: 2.2rem; font-weight: bold; margin-bottom: 25px; text-transform: uppercase; border-bottom: 4px solid #3f51b5; padding-bottom: 10px; text-align: center; color: #2c3e50; }}

        .section-header {{ font-size: 1.4rem; font-weight: bold; color: #2c3e50; margin-top: 35px; margin-bottom: 15px; text-transform: uppercase; border-left: 5px solid #3f51b5; padding-left: 15px; background: #e8eaf6; padding: 8px 15px; }}

        .info-label {{ font-weight: bold; color: #283593; }}

        .structure-box {{ text-align: center; margin: 30px 0; padding: 20px; background: #fdfdfd; border: 1px solid #eee; border-radius: 15px; }}

        .warning-box {{ background-color: #fff5f5; border-left: 5px solid #e53e3e; padding: 20px; margin-top: 15px; border-radius: 8px; color: #c53030; }}

        .interaction-box {{ background-color: #fffaf0; border-left: 5px solid #ed8936; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(237, 137, 54, 0.1); }}

        .food-box {{ background-color: #f0fdf4; border-left: 5px solid #22c55e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(34, 197, 94, 0.1); }}

        .study-box {{ background-color: #f8f9fa; border-left: 5px solid #6c757d; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(108, 117, 125, 0.1); }}

        .im-box {{ background-color: #fff3e0; border-left: 5px solid #ff9800; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(255, 152, 0, 0.1); }}

        .summary-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background-color: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}

        .summary-table th, .summary-table td {{ border: 1px solid #eee; padding: 12px; text-align: left; }}

        .summary-table th {{ background: #2c3e50; color: white; }}

        .usage-list {{ margin-top: 10px; padding-left: 0; list-style-type: none; }}

        .usage-item {{ margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #eee; }}

        ul li {{ margin-bottom: 10px; }}

    </style>



    <div class="med-container">

        <div class="med-title">AMLODIPINE</div>



        <div class="section-header">🧪 Chemical Structure and IUPAC Name</div>

        

        <p><span class="info-label">The systematic name for Amlodipine is:</span><br> 3-ethyl 5-methyl 2-[(2-aminoethoxy)methyl]-4-(2-chlorophenyl)-6-methyl-1,4-dihydropyridine-3,5-dicarboxylate</p>



        <table class="summary-table">

            <thead>

                <tr>

                    <th>Chemical Structure & Formula</th>

                    <th>Value</th>

                </tr>

            </thead>

            <tbody>

                <tr>

                    <td class="param-name" style="font-weight: bold; background-color: #f8f9fa;">Molecular Formula</td>

                    <td>C20H25ClN2O5</td>

                </tr>

                <tr>

                    <td class="param-name" style="font-weight: bold; background-color: #f8f9fa;">Molecular Weight</td>

                    <td>Approximately 408.8 g/mol</td>

                </tr>

            </tbody>

        </table>



        <div class="structure-box">

            <img src="/static/amlodipine_structure.png" style="max-width:100%; height:auto;" alt="Amlodipine Chemical Structure" onerror="this.src='https://placehold.co/400x300?text=Amlodipine+Structure'">

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff; border-left-color: #007bff; background: #e3f2fd;">💊 Therapeutic Uses</div>

            <div class="study-box" style="border-left-color: #007bff;">

                <ul>

                    <li><b>Hypertension (High Blood Pressure):</b> It is a common first-line treatment used alone or in combination with other medications to lower blood pressure, which reduces the risk of fatal and non-fatal cardiovascular events, particularly strokes and heart attacks.</li>

                    <li><b>Chronic Stable Angina:</b> Used for the symptomatic treatment of chest pain that typically occurs during physical exertion or stress.</li>

                    <li><b>Vasospastic Angina (Prinzmetal's or Variant Angina):</b> Indicated for confirmed or suspected contraction of the coronary arteries that happens at rest.</li>

                    <li><b>Coronary Artery Disease (CAD):</b> In patients with angiographically documented CAD (without heart failure or low ejection fraction), it is used to reduce the risk of hospitalisation for angina and coronary revascularisation procedures.</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #6f42c1; border-left-color: #6f42c1; background: #f3e5f5;">⚠️ Adverse Drug Reaction (ADR)</div>

            <div class="study-box" style="border-left-color: #6f42c1; background-color: #f3e5f5;">

                <p><b>Incidence of Common Adverse Reactions to Amlodipine (%):</b></p>

                <div style="text-align: center; margin: 15px 0;">

                    <img src="/static/amlodipine_adr_chart.png" alt="Amlodipine ADR Chart" style="max-width: 100%; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">

                </div>

                ```

                <ul>

                    <li><b>Peripheral Edema:</b> Swelling of the ankles or feet is the most common ADR, affecting roughly 9.4% of patients. It is dose-dependent and more prevalent in women.</li>

                    <li><b>Headache:</b> Reported by about 8.0% of users, often occurring at the start of treatment and subsiding over time.</li>

                    <li><b>Fatigue & Somnolence:</b> Patients may experience tiredness (4.50%) or unusual sleepiness (1.40%).</li>

                    <li><b>Dizziness:</b> Reported by 3.80% of users.</li>

                    <li><b>Gastrointestinal Issues:</b> Includes nausea (3.40%) and abdominal pain (1.60%).</li>

                    <li><b>Flushing:</b> A sensation of warmth or redness in the face and neck, seen in about 2.6% of women and less frequently in men.</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ed8936; border-left-color: #ed8936; background: #fff3e0;">🤝 Drug-Drug Interactions</div>

            <div class="interaction-box">

                <p style="font-weight:bold; color:#c53030; font-size: 1.1rem;">1. Cholesterol Medications (Statins)</p>

                <p>Amlodipine can significantly increase the levels of certain statins in your blood, raising the risk of muscle damage (myopathy) or a life-threatening condition called rhabdomyolysis.</p>

                <ul>

                    <li><b>Simvastatin (Zocor):</b> Dose should generally not exceed 20 mg daily when taken with amlodipine.</li>

                    <li><b>Lovastatin (Altoprev):</b> Similar dose limits (20 mg) are often recommended.</li>

                    <li><b>Atorvastatin (Lipitor):</b> While less severe, amlodipine can still increase atorvastatin levels by about 18%, requiring close monitoring for muscle pain.</li>

                </ul>

                

                <p style="font-weight:bold; color:#c53030; margin-top:15px; font-size: 1.1rem;">2. Immunosuppressants (Transplant Meds)</p>

                <p>Amlodipine can increase the concentration of these drugs, which have a "narrow therapeutic index," meaning even a small increase can be toxic.</p>

                <ul>

                    <li>Tacrolimus (Prograf)</li>

                    <li>Cyclosporine (Neoral, Gengraf)</li>

                    <li>Sirolimus (Rapamune)</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #22c55e; border-left-color: #22c55e; background: #e8f5e9;">🍎 Food-Drug Interactions</div>

            <div class="food-box">

                <p style="font-weight:bold; color:#15803d; font-size: 1.1rem;">1. Grapefruit and Grapefruit Juice</p>

                <p>Unlike other drugs in its class, amlodipine's interaction with grapefruit is often considered mild to moderate, though it is still widely recommended to be avoided.</p>

                <ul>

                    <li><b>The Effect:</b> Grapefruit contains compounds that inhibit the CYP3A4 enzyme in your gut, which is responsible for breaking down amlodipine. Consuming it can lead to higher levels of the drug in your bloodstream.</li>

                    <li><b>The Risk:</b> An increase in amlodipine concentration can worsen side effects like headaches, flushing, or dizziness.</li>

                </ul>

                

                <p style="font-weight:bold; color:#15803d; margin-top: 15px; font-size: 1.1rem;">2. Alcohol</p>

                <p>There is no direct chemical interaction, but alcohol can have additive effects with amlodipine.</p>

                <ul>

                    <li><b>Low Blood Pressure:</b> Both amlodipine and alcohol lower blood pressure. Taking them together can cause it to drop too low, leading to fainting, lightheadedness, or extreme drowsiness.</li>

                    <li><b>Initial Phases:</b> These effects are most common when you first start the medication or if your dose is increased.</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header">📊 Summary Table for Study</div>

            <p><b>Key Takeaways for Study:</b></p>

            <table class="summary-table">

                <thead><tr><th>Category</th><th>Details</th></tr></thead>

                <tbody>

                    <tr><td style="font-weight: bold; background-color: #f8f9fa;">Mechanism</td><td>It is a third-generation dihydropyridine that inhibits calcium influx into vascular smooth muscle, causing direct vasodilation.</td></tr>

                    <tr><td style="font-weight: bold; background-color: #f8f9fa;">Pharmacokinetics</td><td>It has a exceptionally long half-life (30-50 hours), meaning it stays effective for over 24 hours even if a dose is occasionally missed.</td></tr>

                    <tr><td style="font-weight: bold; background-color: #f8f9fa;">Metabolism</td><td>Primarily metabolised in the liver by CYP3A4; dose adjustments are often needed for patients with hepatic impairment but not for those with renal failure.</td></tr>

                    <tr><td style="font-weight: bold; background-color: #f8f9fa;">Clinical Strength</td><td>Particularly strong in preventing stroke and managing stable angina, but generally not used as a primary treatment for symptomatic heart failure (though it is safe to use in such patients for other reasons).</td></tr>

                </tbody>

            </table>

        </div>



        <div class="section-divider">

            <div class="section-header">🏢 Common Brand Names (India)</div>

            <div class="study-box">

                <ul>

                    <li><b>Amlopres:</b> Manufactured by Cipla Ltd.</li>

                    <li><b>Amlokind:</b> Manufactured by Mankind Pharma Ltd.</li>

                    <li><b>AMlong:</b> Manufactured by Micro Labs Ltd.</li>

                    <li><b>Amlovas:</b> Manufactured by Macleods Pharmaceuticals Pvt Ltd.</li>

                    <li><b>Amlodac:</b> Manufactured by Zydus Cadila.</li>

                    <li><b>Amtas:</b> Manufactured by Intas Pharmaceuticals Ltd.</li>

                    <li><b>Amlogard:</b> Manufactured by Mylan Pharmaceuticals (now Viatris).</li>

                    <li><b>Amlopin:</b> Manufactured by USV Private Limited.</li>

                    <li><b>Amlosafe:</b> Manufactured by Aristo Pharmaceuticals Pvt Ltd.</li>

                    <li><b>Amodep:</b> Manufactured by FDC Ltd.</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #0ea5e9; border-left-color: #0ea5e9; background: #f0f9ff;">💉 IV Infusion Dosing</div>

            <div class="study-box" style="border-left-color: #0ea5e9;">

                <p>Amlodipine is not available or FDA-approved for intravenous (IV) infusion. It is strictly an oral medication, available only as tablets, oral solutions, or suspensions.</p>

                <p style="font-weight: bold; margin-top: 15px;">Why Amlodipine is Not Used for IV Infusion......</p>

                <ul>

                    <li><b>Pharmacokinetics:</b> Amlodipine has a very slow onset of action (taking 6-12 hours to reach peak levels) and a long half-life (30-50 hours). These characteristics make it unsuitable for acute situations like hypertensive emergencies, where rapid control and the ability to quickly "turn off" the drug's effect are required.</li>

                    <li><b>Safety:</b> Because its effects last for several days, an IV overdose or an adverse reaction would be extremely difficult to manage in an emergency setting.</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff; border-left-color: #007bff; background: #e3f2fd;">💊 Oral Dosing</div>

            <div class="study-box" style="border-left-color: #007bff;">

                <p>Amlodipine is an oral medication typically taken once daily, with or without food. Because of its long half-life, the medication maintains its effects for over 24 hours.</p>

                <ul>

                    <li><b>Adult Administration - Hypertension (High Blood Pressure):</b> The medication is initiated at a lower dosage and may be titrated upwards by a healthcare provider if necessary.</li>

                    <li><b>Adult Administration - Angina & Coronary Artery Disease:</b> Dosage is determined by a physician based on the necessary level of symptom control.</li>

                    <li><b>Pediatric Administration (Ages 6-17):</b> Amlodipine is approved for treating high blood pressure in children and adolescents, with dosages determined by a pediatrician.</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ff9800; border-left-color: #ff9800; background: #fff3e0;">💪 Intramuscular Dosing</div>

            <div class="im-box">

                <p><b>INTRAMUSCULAR DOSING ADJUSTMENT:</b></p>

                <p>Amlodipine is never administered via intramuscular (IM) injection.</p>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #10b981; border-left-color: #10b981; background: #e8f5e9;">👴 Geriatric Dose Adjustment</div>

            <div class="study-box" style="border-left-color: #10b981;">

                <p style="font-weight: bold;">Oral Dosing for Seniors (65+)</p>

                <ul>

                    <li><b>Initial Dose:</b> The recommended starting dose is typically 2.5 mg once daily.</li>

                    <li><b>Rationale:</b> Elderly patients may have decreased clearance of the drug, leading to higher plasma concentrations and an increased risk of side effects like dizziness, fainting, or swelling.</li>

                    <li><b>Titration:</b> Most clinicians will "start low and go slow," monitoring blood pressure for 7-14 days before considering a dose increase to 5 mg.</li>

                </ul>

                <p style="font-weight: bold; margin-top: 15px;">Other Geriatric Considerations:</p>

                <ul>

                    <li><b>Initial Dose for Hypertension:</b> A lower starting dose is frequently considered for elderly patients.</li>

                    <li><b>Initial Dose for Angina:</b> For chronic stable or vasospastic angina, a lower initial dose is sometimes suggested, with potential for titration to achieve the desired effect.</li>

                    <li><b>Maximum Dose:</b> The maximum recommended dose is generally consistent, regardless of age.</li>

                </ul>

            </div>

        </div>



        <center style="margin-top: 50px; margin-bottom: 30px;">

            <a href="/drugs-store/allopathy" style="text-decoration: none;">

                <button style="padding: 15px 40px; cursor: pointer; background: linear-gradient(135deg, #2c3e50 0%, #000 100%); color: #fff; border: none; border-radius: 30px; font-weight: bold; font-size: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">Back to Products</button>

            </a>

        </center>

    </div>

    """

    return f"<!DOCTYPE html><html><head><title>Amlodipine - Professional Profile</title></head><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



def page_metoprolol_detail(user, lang):

    content = f"""

    <style>

        .med-container {{ max-width: 850px; margin: 30px auto; padding: 40px; background: #fff; font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #000; }}

        .med-title {{ font-size: 2.2rem; font-weight: bold; margin-bottom: 25px; text-transform: uppercase; border-bottom: 4px solid #f44336; padding-bottom: 10px; text-align: center; color: #2c3e50; }}

        .section-header {{ font-size: 1.4rem; font-weight: bold; color: #2c3e50; margin-top: 35px; margin-bottom: 15px; text-transform: uppercase; border-left: 5px solid #f44336; padding-left: 15px; background: #ffebee; padding: 8px 15px; }}

        .info-label {{ font-weight: bold; color: #d32f2f; }}

        .structure-box {{ text-align: center; margin: 30px 0; padding: 20px; background: #fdfdfd; border: 1px solid #eee; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}

        .structure-img {{ max-width: 100%; height: auto; border-radius: 5px; }}

        .warning-box {{ background-color: #fff5f5; border-left: 5px solid #e53e3e; padding: 20px; margin-top: 15px; border-radius: 8px; color: #c53030; }}

        .interaction-box {{ background-color: #fffaf0; border-left: 5px solid #ed8936; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(237, 137, 54, 0.1); }}

        .food-box {{ background-color: #f0fdf4; border-left: 5px solid #22c55e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(34, 197, 94, 0.1); }}

        .study-box {{ background-color: #f8f9fa; border-left: 5px solid #6c757d; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(108, 117, 125, 0.1); }}

        .im-box {{ background-color: #fff3e0; border-left: 5px solid #ff9800; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(255, 152, 0, 0.1); }}

        .summary-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background-color: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}

        .summary-table th, .summary-table td {{ border: 1px solid #eee; padding: 12px; text-align: left; }}

        .summary-table th {{ background: #2c3e50; color: white; }}

        .usage-list {{ margin-top: 10px; padding-left: 0; list-style-type: none; }}

        .usage-item {{ margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #eee; }}

        ul li {{ margin-bottom: 10px; }}

    </style>



    <div class="med-container">

        <div class="med-title">METOPROLOL</div>



        <div class="section-header">🧪 1. Chemical Structure and IUPAC Name</div>

        

        <p><span class="info-label">The IUPAC name for metoprolol is:</span><br> 1-[4-(2-methoxyethyl)phenoxy]-3-(propan-2-ylamino)propan-2-ol (or similarly, (RS)-1-[4-(2-methoxyethyl)phenoxy]-3-[(propan-2-yl)amino] propan-2-ol to denote its racemic form).</p>



        <table class="summary-table">

            <thead>

                <tr>

                    <th>Chemical Structure Information</th>

                    <th>Details</th>

                </tr>

            </thead>

            <tbody>

                <tr>

                    <td class="param-name" style="font-weight: bold; background-color: #f8f9fa;">Classification</td>

                    <td>Metoprolol is a selective beta-receptor blocker.</td>

                </tr>

                <tr>

                    <td class="param-name" style="font-weight: bold; background-color: #f8f9fa;">Molecular Weight</td>

                    <td>Approximately 267.36 g/mol.</td>

                </tr>

                <tr>

                    <td class="param-name" style="font-weight: bold; background-color: #f8f9fa;">Structural Characteristics</td>

                    <td>Structurally, it is a propanolamine derivative where the propan-2-ol backbone is substituted by a 4-(2-methoxyethyl)phenoxy group at the first position and an isopropylamino (propan-2-ylamino) group at the third position.</td>

                </tr>

            </tbody>

        </table>



        <div class="structure-box">

            <img src="/static/metoprolol_structure.png" style="max-width:100%; height:auto;" alt="Metoprolol Chemical Structure" onerror="this.src='https://placehold.co/400x300?text=Metoprolol+Structure'">

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff; border-left-color: #007bff; background: #e3f2fd;">💊 2. Therapeutic Uses</div>

            <div class="study-box" style="border-left-color: #007bff;">

                <p>Metoprolol is primarily used for cardiovascular conditions:</p>

                <ul>

                    <li><b>Hypertension:</b> To lower high blood pressure.</li>

                    <li><b>Angina Pectoris:</b> For long-term treatment of chest pain.</li>

                    <li><b>Heart Failure:</b> Stable, symptomatic (usually using the Succinate form).</li>

                    <li><b>Myocardial Infarction:</b> Early intervention and late maintenance to reduce mortality.</li>

                    <li><b>Arrhythmias:</b> Specifically supraventricular tachycardia (SVT) and atrial fibrillation.</li>

                    <li><b>Migraine Prophylaxis:</b> To reduce the frequency of migraine attacks.</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #6f42c1; border-left-color: #6f42c1; background: #f3e5f5;">⚠️ 3. Adverse Drug Reaction (ADR)</div>

            <div class="study-box" style="border-left-color: #6f42c1; background-color: #f3e5f5;">

                <p><b>Common side effects include:</b></p>

                <ul>

                    <li><b>Cardiovascular:</b> Bradycardia (slow heart rate), hypotension, cold extremities.</li>

                    <li><b>CNS:</b> Fatigue, dizziness, depression, nightmares, and insomnia.</li>

                    <li><b>Respiratory:</b> Shortness of breath or bronchospasm (use with caution in asthma).</li>

                    <li><b>GI:</b> Nausea, diarrhea, or constipation.</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ed8936; border-left-color: #ed8936; background: #fff3e0;">🤝 4. Drug-Drug Interactions</div>

            <div class="interaction-box">

                <div class="usage-list">

                    <div class="usage-item"><b>Catecholamine-depleters (e.g., Reserpine):</b> Can cause additive bradycardia or hypotension.</div>

                    <div class="usage-item"><b>CYP2D6 Inhibitors (e.g., Fluoxetine, Paroxetine):</b> Increase metoprolol blood levels significantly.</div>

                    <div class="usage-item"><b>Calcium Channel Blockers (e.g., Verapamil, Diltiazem):</b> Can lead to severe bradycardia or heart block.</div>

                    <div class="usage-item"><b>Digoxin:</b> Increases risk of slow heart rate (bradycardia).</div>

                    <div class="usage-item"><b>Clonidine:</b> Risk of rebound hypertension if discontinued abruptly while on beta-blockers.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #22c55e; border-left-color: #22c55e; background: #e8f5e9;">🍎 5. Food-Drug Interactions</div>

            <div class="food-box">

                <div class="usage-list">

                    <div class="usage-item"><b>Bioavailability:</b> Food significantly increases the absorption and bioavailability of metoprolol.</div>

                    <div class="usage-item"><b>Recommendation:</b> It is recommended to take the medication with or immediately after a meal to maintain consistent blood levels.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header">📊 6. Summary Table for Study</div>

            <table class="summary-table">

                <thead>

                    <tr>

                        <th>Feature</th>

                        <th>Metoprolol Tartrate</th>

                        <th>Metoprolol Succinate</th>

                    </tr>

                </thead>

                <tbody>

                    <tr>

                        <td style="font-weight: bold; background-color: #f8f9fa;">Release Type</td>

                        <td>Immediate-release (IR)</td>

                        <td>Extended-release (ER/XL)</td>

                    </tr>

                    <tr>

                        <td style="font-weight: bold; background-color: #f8f9fa;">Dosing Frequency</td>

                        <td>2-3 times daily</td>

                        <td>Once daily</td>

                    </tr>

                    <tr>

                        <td style="font-weight: bold; background-color: #f8f9fa;">Primary Use</td>

                        <td>Acute MI, Hypertension</td>

                        <td>Heart Failure, Chronic Hypertension</td>

                    </tr>

                    <tr>

                        <td style="font-weight: bold; background-color: #f8f9fa;">Metabolism</td>

                        <td>Hepatic (CYP2D6)</td>

                        <td>Hepatic (CYP2D6)</td>

                    </tr>

                </tbody>

            </table>

        </div>



        <div class="section-divider">

            <div class="section-header">🏢 7. Common Brand Names (India)</div>

            <div class="study-box">

                <ul>

                    <li>Metolar (Cipla)</li>

                    <li>Met-XL (Ajanta Pharma)</li>

                    <li>Starpress (Lupin)</li>

                    <li>Revelol (Ipca)</li>

                    <li>Seloken (AstraZeneca)</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #0ea5e9; border-left-color: #0ea5e9; background: #f0f9ff;">💉 8. IV Infusion Dosing</div>

            <div class="study-box" style="border-left-color: #0ea5e9;">

                <div class="usage-list">

                    <div class="usage-item"><b>Indication:</b> Acute Myocardial Infarction or Arrhythmias.</div>

                    <div class="usage-item"><b>Standard Dose:</b> 5 mg given as a slow IV bolus (1-2 mg/min).</div>

                    <div class="usage-item"><b>Repeat:</b> Can be repeated every 2-5 minutes up to a total of 15 mg.</div>

                    <div class="usage-item"><b>Transition:</b> Oral therapy typically starts 15 minutes after the last IV dose.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff; border-left-color: #007bff; background: #e3f2fd;">💊 9. Oral Dosing (Syrup/Drops/Tablets)</div>

            <div class="study-box" style="border-left-color: #007bff;">

                <div class="usage-list">

                    <div class="usage-item"><b>Tablets:</b> Available in 12.5 mg, 25 mg, 50 mg, and 100 mg strengths.</div>

                    <div class="usage-item"><b>Oral Solution:</b> 100 mg daily in divided doses (e.g., Lopressor solution).</div>

                    <div class="usage-item"><b>Suspension:</b> Often compounded for pediatrics (e.g., 10 mg/mL).</div>

                    <div class="usage-item"><b>Sprinkle Capsules:</b> Kapspargo Sprinkle can be opened and sprinkled on soft food (like applesauce) for patients with swallowing difficulties.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ff9800; border-left-color: #ff9800; background: #fff3e0;">💪 10. Intramuscular (IM) Dosing</div>

            <div class="im-box">

                <p><b>Note:</b> Metoprolol is not standardly administered via IM injection. The absorption is unpredictable and it can cause local tissue irritation. Standard parenteral use is strictly Intravenous (IV) or Oral.</p>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #10b981; border-left-color: #10b981; background: #e8f5e9;">👴 11. Geriatric Dose Adjustment (Age 65+)</div>

            <div class="study-box" style="border-left-color: #10b981;">

                <div class="usage-list">

                    <div class="usage-item"><b>Sensitivity:</b> Elderly patients are more sensitive to beta-blockade and have a higher risk of hepatic/renal impairment.</div>

                    <div class="usage-item"><b>Guidelines:</b> Always start at the low end of the dosing range (e.g., 12.5 mg or 25 mg).</div>

                    <div class="usage-item"><b>Exposure:</b> Studies suggest that for the same dose, elderly women may have higher drug exposure than elderly men, so extra caution is needed during titration.</div>

                </div>

            </div>

        </div>



        <center style="margin-top: 50px; margin-bottom: 30px;">

            <a href="/drugs-store/allopathy" style="text-decoration: none;">

                <button style="padding: 15px 40px; background: #f44336; color: white; border: none; border-radius: 25px; cursor: pointer; font-weight: bold; font-size: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">Back to Allopathy List</button>

            </a>

        </center>

    </div>

    """

    return f"<!DOCTYPE html><html><head><title>Metoprolol - Professional Profile</title></head><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



def page_atorvastatin_detail(user, lang):

    content = f"""

    <style>

        .med-container {{ max-width: 850px; margin: 30px auto; padding: 40px; background: #fff; font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #000; }}

        .med-title {{ font-size: 2.2rem; font-weight: bold; margin-bottom: 25px; text-transform: uppercase; border-bottom: 4px solid #4caf50; padding-bottom: 10px; text-align: center; color: #2c3e50; }}

        .section-header {{ font-size: 1.4rem; font-weight: bold; color: #2c3e50; margin-top: 35px; margin-bottom: 15px; text-transform: uppercase; border-left: 5px solid #4caf50; padding-left: 15px; background: #e8f5e9; padding: 8px 15px; }}

        .info-label {{ font-weight: bold; color: #388e3c; }}

        .structure-box {{ text-align: center; margin: 30px 0; padding: 20px; background: #fdfdfd; border: 1px solid #eee; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}

        .structure-img {{ max-width: 100%; height: auto; border-radius: 5px; }}

        .warning-box {{ background-color: #fff5f5; border-left: 5px solid #e53e3e; padding: 20px; margin-top: 15px; border-radius: 8px; color: #c53030; }}

        .interaction-box {{ background-color: #fffaf0; border-left: 5px solid #ed8936; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(237, 137, 54, 0.1); }}

        .food-box {{ background-color: #f0fdf4; border-left: 5px solid #22c55e; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(34, 197, 94, 0.1); }}

        .study-box {{ background-color: #f8f9fa; border-left: 5px solid #6c757d; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(108, 117, 125, 0.1); }}

        .im-box {{ background-color: #fff3e0; border-left: 5px solid #ff9800; padding: 20px; margin-top: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(255, 152, 0, 0.1); }}

        .summary-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background-color: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}

        .summary-table th, .summary-table td {{ border: 1px solid #eee; padding: 12px; text-align: left; }}

        .summary-table th {{ background: #2c3e50; color: white; }}

        .usage-list {{ margin-top: 10px; padding-left: 0; list-style-type: none; }}

        .usage-item {{ margin-bottom: 15px; padding-left: 10px; border-left: 3px solid #eee; }}

        ul li {{ margin-bottom: 10px; }}

    </style>



    <div class="med-container">

        <div class="med-title">ASTROVASTATIN (Atorvastatin)</div>



        <div class="section-header">🧪 1) Chemical Structure & IUPAC Name</div>

        

        <table class="summary-table">

            <thead>

                <tr>

                    <th>Chemical Structure Information</th>

                    <th>Details</th>

                </tr>

            </thead>

            <tbody>

                <tr>

                    <td class="param-name" style="font-weight: bold; background-color: #f8f9fa;">Molecular Formula</td>

                    <td>C33H35FN2O5</td>

                </tr>

                <tr>

                    <td class="param-name" style="font-weight: bold; background-color: #f8f9fa;">Chemical Class</td>

                    <td>It is a synthetic lipid-lowering agent and a selective, competitive inhibitor of HMG-CoA reductase.</td>

                </tr>

            </tbody>

        </table>



        <div class="structure-box">

            <img src="/static/atorvastatin_structure.png" style="max-width:100%; height:auto;" alt="Atorvastatin Chemical Structure" onerror="this.src='https://placehold.co/400x300?text=Atorvastatin+Structure'">

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #007bff; border-left-color: #007bff; background: #e3f2fd;">💊 2) Therapeutic Uses</div>

            <div class="study-box" style="border-left-color: #007bff;">

                <div class="usage-list">

                    <div class="usage-item"><b>Hyperlipidemia:</b> To lower "bad" cholesterol (LDL) and triglycerides and raise "good" cholesterol (HDL).</div>

                    <div class="usage-item"><b>Cardiovascular Prevention:</b> Reducing the risk of heart attack, stroke, and angina in patients with or at high risk for heart disease.</div>

                    <div class="usage-item"><b>Pediatric Use:</b> Treatment of heterozygous familial hypercholesterolemia in children (10-17 years).</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #6f42c1; border-left-color: #6f42c1; background: #f3e5f5;">⚠️ 3) Adverse Drug Reactions (ADR)</div>

            <div class="study-box" style="border-left-color: #6f42c1; background-color: #f3e5f5;">

                <div class="usage-list">

                    <div class="usage-item"><b>Common:</b> Myalgia (muscle pain), diarrhea, joint pain (arthralgia), and insomnia.</div>

                    <div class="usage-item"><b>Serious:</b> Rhabdomyolysis (severe muscle breakdown), liver enzyme elevation (Hepatotoxicity), and increased blood sugar levels.</div>

                    <div class="usage-item"><b>Others:</b> Nasopharyngitis, headache, and allergic reactions (rash, pruritus).</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ed8936; border-left-color: #ed8936; background: #fff3e0;">🤝 4) Drug-Drug Interactions</div>

            <div class="interaction-box">

                <div class="usage-list">

                    <div class="usage-item"><b>CYP3A4 Inhibitors:</b> Drugs like clarithromycin, itraconazole, and certain HIV/HCV protease inhibitors can significantly increase atorvastatin levels, raising the risk of muscle injury.</div>

                    <div class="usage-item"><b>Digoxin:</b> May increase plasma digoxin concentrations.</div>

                    <div class="usage-item"><b>Oral Contraceptives:</b> May increase levels of norethindrone and ethinyl estradiol.</div>

                    <div class="usage-item"><b>Other Statins:</b> Combining with other statins is generally avoided to prevent toxicity.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #22c55e; border-left-color: #22c55e; background: #e8f5e9;">🍎 5) Food-Drug Interactions</div>

            <div class="food-box">

                <div class="usage-list">

                    <div class="usage-item"><b>Grapefruit Juice:</b> Contains compounds that inhibit the enzyme (CYP3A4) responsible for breaking down the drug. Consuming large amounts (>1.2L/day) can lead to toxic levels of atorvastatin.</div>

                    <div class="usage-item"><b>Alcohol:</b> Excessive use can increase the risk of liver damage.</div>

                    <div class="usage-item"><b>High-Fat Meals:</b> While it can be taken with or without food, a high-fat diet should be avoided as part of the overall therapy for high cholesterol.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header">📊 6) Summary table for study</div>

            <table class="summary-table">

                <thead>

                    <tr>

                        <th>Parameter</th>

                        <th>Details</th>

                    </tr>

                </thead>

                <tbody>

                    <tr>

                        <td style="font-weight: bold; background-color: #f8f9fa;">Drug Class</td>

                        <td>HMG-CoA Reductase Inhibitor (Statin)</td>

                    </tr>

                    <tr>

                        <td style="font-weight: bold; background-color: #f8f9fa;">Mechanism</td>

                        <td>Inhibits cholesterol synthesis in the liver</td>

                    </tr>

                    <tr>

                        <td style="font-weight: bold; background-color: #f8f9fa;">Half-Life</td>

                        <td>~14 hours (active metabolites 20-30 hours)</td>

                    </tr>

                    <tr>

                        <td style="font-weight: bold; background-color: #f8f9fa;">Metabolism</td>

                        <td>Hepatic (primarily via CYP3A4)</td>

                    </tr>

                    <tr>

                        <td style="font-weight: bold; background-color: #f8f9fa;">Excretion</td>

                        <td>Primarily in bile; <2% in urine</td>

                    </tr>

                </tbody>

            </table>

        </div>



        <div class="section-divider">

            <div class="section-header">🏢 7) Common Brand Names in India</div>

            <div class="study-box">

                <ul>

                    <li>Storvas (Sun Pharma)</li>

                    <li>Lipvas (Cipla)</li>

                    <li>Tonact (Lupin)</li>

                    <li>Atorva (Zydus Cadila)</li>

                    <li>Avas (Micro Labs)</li>

                    <li>Stator (Abbott)</li>

                    <li>Lipicure (Intas)</li>

                </ul>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #0ea5e9; border-left-color: #0ea5e9; background: #f0f9ff;">💉 8) IV INFUSION DOSING</div>

            <div class="study-box" style="border-left-color: #0ea5e9;">

                <div class="usage-list">

                    <div class="usage-item">There is no standard IV infusion dosing for Atorvastatin (commonly misspelled as "astrovastatin") because it is not currently manufactured or approved for intravenous use in humans.</div>

                    <div class="usage-item">Atorvastatin (brand name: Lipitor) is strictly an oral medication. It is available as film-coated tablets or an oral suspension.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #ff9800; border-left-color: #ff9800; background: #fff3e0;">💪 9) INTRAMUSCULAR DOSING</div>

            <div class="im-box">

                <div class="usage-list">

                    <div class="usage-item">There is no intramuscular (IM) dosing for Atorvastatin (often spelled "astrovastatin").</div>

                    <div class="usage-item">Atorvastatin (Lipitor) is strictly an oral medication and is not manufactured or approved as an injection for humans.</div>

                </div>

                <p><b>There are several medical and practical reasons why this route is not used:</b></p>

                <p style="font-weight: bold; color: #ff9800;">Why It Is Not Given Intramuscularly</p>

                <div class="usage-list">

                    <div class="usage-item"><b>Formulation:</b> Current commercial versions of Atorvastatin are only produced as film-coated tablets or oral suspensions. There is no stable, injectable liquid version available for clinical use.</div>

                    <div class="usage-item"><b>Muscle Safety:</b> One of the most significant side effects of statins is myopathy (muscle damage). Intramuscular injections naturally cause localized muscle trauma and can raise Creatine Kinase (CK) levels. Administering a statin via IM would make it impossible for doctors to distinguish between normal injection site soreness and a dangerous drug reaction.</div>

                    <div class="usage-item"><b>Liver Efficiency:</b> Atorvastatin works primarily in the liver. The oral route allows the drug to be absorbed by the gut and sent directly to the liver (first-pass metabolism), where it is most effective at inhibiting cholesterol production.</div>

                </div>

            </div>

        </div>



        <div class="section-divider">

            <div class="section-header" style="color: #10b981; border-left-color: #10b981; background: #e8f5e9;">👴 10) Geriatric dose adjustment</div>

            <div class="study-box" style="border-left-color: #10b981;">

                <p style="font-weight: bold;">1. General Dosing Approach (65+ Years)</p>

                <p>While the standard adult dose range is 10 mg to 80 mg once daily, the approach for older adults depends on their specific health profile:</p>

                <div class="usage-list">

                    <div class="usage-item"><b>Starting Dose:</b> Physicians often start geriatric patients at a lower dose (10 mg or 20 mg) to assess tolerability before increasing.</div>

                    <div class="usage-item"><b>Titration:</b> Adjustments are typically made every 2 to 4 weeks based on lipid (cholesterol) goals and how well the patient handles the drug.</div>

                    <div class="usage-item"><b>Maximum Dose:</b> While 80 mg is the maximum, it is used with extra caution in the elderly due to the increased risk of muscle-related side effects.</div>

                </div>

                

                <p style="font-weight: bold; margin-top: 15px;">2. Dosing Considerations by Age Sub-Groups</p>

                <table class="summary-table">

                    <thead>

                        <tr>

                            <th>Age Group</th>

                            <th>Focus</th>

                            <th>Considerations</th>

                        </tr>

                    </thead>

                    <tbody>

                        <tr>

                            <td style="font-weight: bold; background-color: #f8f9fa;">65 to 75 Years</td>

                            <td>High to Moderate Intensity</td>

                            <td>Dosage is typically determined by assessing cardiovascular risk factors and the presence of established heart disease.</td>

                        </tr>

                        <tr>

                            <td style="font-weight: bold; background-color: #f8f9fa;">Over 75 Years</td>

                            <td>Moderate Intensity</td>

                            <td>A more cautious approach is often preferred for primary prevention to balance therapeutic benefits with potential risks.</td>

                        </tr>

                    </tbody>

                </table>

            </div>

        </div>



        <center style="margin-top: 50px; margin-bottom: 30px;">

            <a href="/drugs-store/allopathy" style="text-decoration: none;">

                <button style="padding: 15px 40px; background: #4caf50; color: white; border: none; border-radius: 25px; cursor: pointer; font-weight: bold; font-size: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">Back to Allopathy List</button>

            </a>

        </center>

    </div>

    """

    return f"<!DOCTYPE html><html><head><title>Atorvastatin - Professional Profile</title></head><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



def page_product_detail(user, lang, product_id):

    # 1. Acetaminophen

    if product_id == 'acetaminophen':

        return page_acetaminophen_detail(user, lang)



    # 2. Ibuprofen Check

    if product_id == 'ibuprofen':

        return page_ibuprofen_detail(user, lang)

        

    # 3. Aspirin Check

    if product_id == 'aspirin':

        return page_aspirin_detail(user, lang)



    # 4. Diclofenac Check

    if product_id == 'diclofenac':

        return page_diclofenac_detail(user, lang)

        

    # 5. Amoxicillin Check

    if product_id == 'amoxicillin':

        return page_amoxicillin_detail(user, lang)

    

    # 6. Morphine (NEWLY ADDED)

    if product_id == 'morphine':

        return page_morphine_detail(user, lang)

    

    # 7. Azithromycin (NEWLY ADDED)

    if product_id == 'azithromycin':

        return page_azithromycin_detail(user, lang)

    

    # 8. Ciprofloxacin (NEWLY ADDED)

    if product_id == 'ciprofloxacin':

        return page_ciprofloxacin_detail(user, lang)

    

    # New Doxycycline Check

    if product_id == 'doxycycline':

        return page_doxycycline_detail(user, lang)

    

    if product_id == 'metronidazole':

        return page_metronidazole_detail(user, lang)

    

    if product_id == 'fluconazole':

        return page_fluconazole_detail(user, lang)

    

    if product_id == 'lisinopril':

        return page_lisinopril_detail(user, lang)

    

    if product_id == 'amlodipine':

        return page_amlodipine_detail(user, lang)

    

    if product_id == 'metoprolol':

        return page_metoprolol_detail(user, lang)

    

    if product_id == 'atorvastatin':

        return page_atorvastatin_detail(user, lang)



    # 6. Standard Template for other items

    product_text = HERBAL_DB.get(product_id) or ALLOPATHY_DB.get(product_id)

    if not product_text:

        return page_notfound(f"Product ID: {product_id}", user, lang)



    name = product_text.get('title', 'Unknown Medicine')

    description = product_text.get('desc', 'Description coming soon...')

    usage = product_text.get('usage', 'Usage details coming soon...')

    references = product_text.get('ref', [])

    image_url = product_text.get('image', 'https://placehold.co/150?text=Medicine')



    ref_html = "".join([f"<li style='margin-bottom:8px;'>📚 {r}</li>" for r in references]) if references else ""

    

    content = f"""

    <div style="max-width: 800px; margin: 40px auto; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; font-family: sans-serif;">

        <h1 style="text-transform: uppercase;">{name}</h1>

        <img src="{image_url}" style="max-width: 300px; border-radius: 10px; margin: 20px 0;">

        <div style="text-align: left; padding: 20px;">

            <h3>Description</h3><p>{description}</p>

            <h3>Usage</h3><p>{usage}</p>

            {f"<h3>References</h3><ul>{ref_html}</ul>" if ref_html else ""}

        </div>

        <a href="/drugs-store/allopathy"><button style="padding: 10px 25px;">Back</button></a>

    </div>

    """

    html = f"<!DOCTYPE html><html><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



# -----------------------------------------------------------

# இதுக்கு மேலே பேஸ்ட் பண்ணுங்க

# -----------------------------------------------------------

def page_notfound(path, user, lang):

    content = f"""<div class='card'><h2>404 - {LANG[lang]['page_not_found']}</h2><p>{LANG[lang]['not_found_message']} <b>{path}</b> does not exist.</p><a href='/'><button>{LANG[lang]['go_home']}</button></a></div>"""

    html = f"<!DOCTYPE html><html><head><title>404</title></head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



def page_notfound(path, user, lang):

    content = f"""<div class='card'><h2>404 - {LANG[lang]['page_not_found']}</h2><p>{LANG[lang]['not_found_message']} <b>{path}</b> does not exist.</p><a href='/'><button>{LANG[lang]['go_home']}</button></a></div>"""

    html = f"<!DOCTYPE html><html><head><title>404</title></head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



def page_logout(environ, start_response):

    cookie_session = get_cookie(environ, "session_id")

    if cookie_session in SESSIONS: del SESSIONS[cookie_session]

    headers = [("Location", "/login"), ("Set-Cookie", make_set_cookie_header("session_id", "", days=-1))]

    start_response("302 Found", headers); return [b'']



def page_ai_chat(user, lang):

    styles = """

    <style>

        .chat-container { max-width: 800px; margin: 20px auto; background: #fff; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); overflow: hidden; display: flex; flex-direction: column; height: 80vh; }

        .chat-header { background: #2c3e50; color: white; padding: 15px; text-align: center; font-weight: bold; font-size: 1.2rem; }

        .chat-box { flex: 1; padding: 20px; overflow-y: auto; background: #f4f7f6; display: flex; flex-direction: column; gap: 15px; }

        .message { max-width: 75%; padding: 10px 15px; border-radius: 15px; line-height: 1.5; position: relative; word-wrap: break-word; }

        .user-msg { align-self: flex-end; background: #007bff; color: white; border-bottom-right-radius: 2px; }

        .ai-msg { align-self: flex-start; background: #e9ecef; color: #333; border-bottom-left-radius: 2px; }

        .input-area { padding: 15px; background: #fff; border-top: 1px solid #ddd; display: flex; gap: 10px; }

        .chat-input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 25px; outline: none; }

        .send-btn { background: #2c3e50; color: white; border: none; padding: 10px 20px; border-radius: 25px; cursor: pointer; font-weight: bold; }

        .send-btn:hover { background: #34495e; }

        .loading { font-size: 12px; color: #666; text-align: center; display: none; }

    </style>

    <script>

        async function sendMessage() {

            const inputField = document.getElementById("userCheck");

            const chatBox = document.getElementById("chatBox");

            const loading = document.getElementById("loading");

            const message = inputField.value.trim();



            if (!message) return;



            // 1. Add User Message

            chatBox.innerHTML += `<div class="message user-msg">${message}</div>`;

            inputField.value = "";

            chatBox.scrollTop = chatBox.scrollHeight;

            loading.style.display = "block";



            // 2. Call Backend API

            try {

                const response = await fetch("/api/chat", {

                    method: "POST",

                    headers: { "Content-Type": "application/json" },

                    body: JSON.stringify({ message: message })

                });

                const data = await response.json();

                

                // 3. Add AI Response

                // Simple formatting: Replace newlines with <br> and bolding ** with <b>

                let formattedReply = data.reply.replace(/\\n/g, "<br>").replace(/\\*\\*(.*?)\\*\\*/g, "<b>$1</b>");

                

                chatBox.innerHTML += `<div class="message ai-msg">${formattedReply}</div>`;

            } catch (error) {

                chatBox.innerHTML += `<div class="message ai-msg" style="color:red;">Error connecting to AI.</div>`;

            }

            

            loading.style.display = "none";

            chatBox.scrollTop = chatBox.scrollHeight;

        }



        function handleEnter(e) {

            if (e.key === "Enter") sendMessage();

        }

    </script>

    """

    

    content = f"""

    <div class="chat-container">

        <div class="chat-header">🤖 GenMedX AI Assistant</div>

        <div id="chatBox" class="chat-box">

            <div class="message ai-msg">Hello! I am your AI Medical Assistant. How can I help you today? <br><small>(Note: I provide information, not medical diagnosis.)</small></div>

        </div>

        <div id="loading" class="loading">Thinking...</div>

        <div class="input-area">

            <input type="text" id="userCheck" class="chat-input" placeholder="Ask about medicines, symptoms..." onkeypress="handleEnter(event)">

            <button class="send-btn" onclick="sendMessage()">Send</button>

        </div>

    </div>

    <div style="text-align:center; margin-bottom:20px;">

        <a href="/services"><button style="padding:10px 20px; cursor:pointer;">Back to Services</button></a>

    </div>

    """

    

    html = f"<!DOCTYPE html><html><head><title>AI Chat</title>{styles}</head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



def page_pharmacy_consult(user, lang):

    # JavaScript க்கான டேட்டா (Shops + Medicines)

    combined_data = []

    for s in MEDICAL_SHOPS:

        combined_data.append({"type": "shop", "name": s['name'], "id": s['id']})

    for m in SHOP_SPECIFIC_STOCK:

        combined_data.append({"type": "med", "name": m['name'], "id": m['name']}) # Use name as ID for meds

    

    json_data = json.dumps(combined_data)

    

    title = "Pharmacist Intervention"

    ph = "Search for Medical Shop or Medicine..."



    css = """

    <style>

        .ph-header { background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); padding: 50px 20px; text-align: center; color: white; border-radius: 0 0 30px 30px; }

        .ph-container { max-width: 900px; margin: 0 auto; padding: 20px; }

        .search-box { width: 100%; padding: 18px; border-radius: 50px; border: 1px solid #ddd; font-size: 1.1rem; outline: none; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }

        .s-results { background:white; border:1px solid #eee; display:none; margin-top:5px; border-radius:10px; overflow:hidden; }

        .s-item { padding:12px; border-bottom:1px solid #f0f0f0; cursor:pointer; display:flex; justify-content:space-between; }

        .s-item:hover { background:#f9f9f9; }

        .tag { font-size:0.8rem; padding:2px 6px; border-radius:4px; color:white; }

        .tag-shop { background:#28a745; } .tag-med { background:#ff9800; }

        .big-upload { background: #f0f8ff; border: 2px dashed #007bff; border-radius: 20px; padding: 40px; text-align: center; margin: 30px 0; }

        .shop-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }

        .shop-card { background: white; border: 1px solid #eee; border-radius: 15px; padding: 15px; display: flex; align-items: center; gap: 15px; box-shadow: 0 3px 6px rgba(0,0,0,0.05); text-decoration: none; color: #333; transition: 0.3s; }

        .shop-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); border-color: #007bff; }

    </style>

    <script>

        const allData = """ + json_data + """;

        function mainSearch() {

            const input = document.getElementById("mainSearch").value.toLowerCase();

            const resDiv = document.getElementById("mainRes");

            resDiv.innerHTML = "";

            if (!input) { resDiv.style.display = "none"; return; }

            

            const filtered = allData.filter(i => i.name.toLowerCase().includes(input));

            

            if (filtered.length > 0) {

                resDiv.style.display = "block";

                filtered.forEach(i => {

                    const d = document.createElement("div"); d.className = "s-item";

                    let tag = i.type === 'shop' ? '<span class="tag tag-shop">SHOP</span>' : '<span class="tag tag-med">MEDICINE</span>';

                    d.innerHTML = `<span>${i.name}</span> ${tag}`;

                    d.onclick = function() {

                        if(i.type === 'shop') window.location.href = "/shop-detail?id=" + i.id;

                        else window.location.href = "/global-search?q=" + i.name;

                    };

                    resDiv.appendChild(d);

                });

            } else { resDiv.style.display = "none"; }

        }

        function handleEnter(e) {

            if(e.key === 'Enter') {

                let val = document.getElementById("mainSearch").value;

                // Default to global search logic if enter pressed

                window.location.href = "/global-search?q=" + val;

            }

        }

    </script>

    """

    

    # Shops HTML

    shops_html = "".join([f'<a href="/shop-detail?id={s["id"]}" class="shop-card"><img src="{s["img"]}" style="width:60px;height:60px;border-radius:50%;"><div><h3>{s["name"]}</h3><p style="margin:0;color:#666;">{s["area"]}</p></div></a>' for s in MEDICAL_SHOPS])



    content = f"""

    {css}

    <div class="ph-header"><h1>{title}</h1><p>Find Medicines & Shops</p></div>

    <div class="ph-container">

        

        <input type="text" id="mainSearch" class="search-box" placeholder="{ph}" onkeyup="mainSearch()" onkeypress="handleEnter(event)">

        <div id="mainRes" class="s-results"></div>



        <div class="big-upload">

            <h2 style="color:#007bff; margin-top:0;">📤 Upload Prescription</h2>

            <p>We will tell you which shops have your medicines.</p>

            <form method="post" action="/upload-prescription" enctype="multipart/form-data">

                <input type="file" name="prescription" required>

                <input type="hidden" name="source" value="pharmacy_main">

                <br><br>

                <button type="submit" style="padding:12px 25px; background:#007bff; color:white; border:none; border-radius:50px; cursor:pointer; font-weight:bold;">Analyze & Find Shops</button>

            </form>

        </div>



        <h3>🏥 Partner Medical Shops</h3>

        <div class="shop-list">{shops_html}</div>

        <div style="text-align:center; margin-top:30px;"><a href="/services" style="color:#666;">Back to Services</a></div>

    </div>

    """

    return f"<!DOCTYPE html><html><head><title>{title}</title></head><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')

# --- 1. HOMEOPATHY PAGE ---

def page_homeopathy_products(user, lang):

    products = [

        {"name": "Arnica Montana", "desc": "For muscle pain & bruises", "img": "https://placehold.co/200?text=Arnica"},

        {"name": "Nux Vomica", "desc": "For digestive issues", "img": "https://placehold.co/200?text=Nux+Vomica"},

        {"name": "Oscillococcinum", "desc": "Flu relief", "img": "https://placehold.co/200?text=Oscillo"},

        {"name": "Rhus Tox", "desc": "Joint pain relief", "img": "https://placehold.co/200?text=Rhus+Tox"},

        {"name": "Belladonna", "desc": "For fever & inflammation", "img": "https://placehold.co/200?text=Belladonna"},

        {"name": "Arsenicum Album", "desc": "Food poisoning relief", "img": "https://placehold.co/200?text=Arsenicum"}

    ]

    

    cards_html = ""

    for p in products:

        # CHANGED BUTTON LINK

        cards_html += f"""

        <div class="product-item">

            <div class="image-wrapper"><img src="{p['img']}" class="product-image"></div>

            <h3>{p['name']}</h3>

            <p style="font-size:0.9rem; color:#666;">{p['desc']}</p>

            <a href="/api/log-action?cat=Order&item={p['name']}" class="name-button">Add to Cart</a>

        </div>"""



    css = """<style>.product-grid-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 25px; padding: 20px; } .product-item { background: white; width: 220px; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); transition: 0.3s; } .product-item:hover { transform: translateY(-5px); } .image-wrapper { height: 150px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; } .product-image { max-height: 100%; max-width: 100%; } .name-button { background: #6f42c1; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; width: 100%; margin-top: 10px; text-decoration:none; display:inline-block; }</style>"""



    content = f"""{css}<div class="card" style="text-align:center;"><h2 style="color:#6f42c1;">Homeopathy Medicines</h2><p>Natural & Safe Remedies</p><div class="product-grid-container">{cards_html}</div><a href="/drugs-store"><button style="margin-top:20px;">Back to Store</button></a></div>"""

    html = f"<!DOCTYPE html><html><head><title>Homeopathy</title></head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



def page_medical_devices(user, lang):

    devices = [

        {"name": "Digital Thermometer", "desc": "Accurate fever check", "img": "https://placehold.co/200?text=Thermometer"},

        {"name": "Pulse Oximeter", "desc": "Check oxygen levels", "img": "https://placehold.co/200?text=Oximeter"},

        {"name": "BP Monitor (Digital)", "desc": "Automatic BP Check", "img": "https://placehold.co/200?text=BP+Monitor"},

        {"name": "Glucometer Kit", "desc": "Blood sugar test", "img": "https://placehold.co/200?text=Glucometer"},

        {"name": "Nebulizer", "desc": "For respiratory relief", "img": "https://placehold.co/200?text=Nebulizer"}

    ]

    

    cards_html = ""

    for d in devices:

        # இங்கேதான் Admin Logic பட்டன் இருக்கு

        cards_html += f"""

        <div class="product-item">

            <div class="image-wrapper"><img src="{d['img']}" class="product-image"></div>

            <h3>{d['name']}</h3>

            <p style="font-size:0.9rem; color:#666;">{d['desc']}</p>

            <a href="/api/log-action?cat=Order&item={d['name']}" class="name-button" style="display:inline-block; margin-top:10px; text-decoration:none; background:#e67e22; color:white; padding:8px 15px; border-radius:5px;">Buy Now</a>

        </div>"""



    css = """<style>.product-grid-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 25px; padding: 20px; } .product-item { background: white; width: 220px; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); transition: 0.3s; } .product-item:hover { transform: translateY(-5px); } .image-wrapper { height: 150px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; } .product-image { max-height: 100%; max-width: 100%; }</style>"""



    content = f"""{css}<div class="card" style="text-align:center;"><h2 style="color:#e67e22;">Medical Devices</h2><p>Essential Healthcare Gadgets</p><div class="product-grid-container">{cards_html}</div><a href="/drugs-store"><button style="margin-top:20px;">Back to Store</button></a></div>"""

    html = f"<!DOCTYPE html><html><head><title>Medical Devices</title></head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



# --- 3. VITAMINS PAGE ---

def page_vitamins(user, lang):

    vitamins = [

        {"name": "Vitamin C (500mg)", "desc": "Immunity Booster", "img": "https://placehold.co/200?text=Vit+C"},

        {"name": "Multivitamin Tablets", "desc": "Daily supplement", "img": "https://placehold.co/200?text=Multivit"},

        {"name": "Vitamin D3", "desc": "For bone health", "img": "https://placehold.co/200?text=Vit+D3"},

        {"name": "Fish Oil (Omega-3)", "desc": "Heart health", "img": "https://placehold.co/200?text=Fish+Oil"},

        {"name": "Calcium + Magnesium", "desc": "Strong bones", "img": "https://placehold.co/200?text=Calcium"}

    ]

    

    cards_html = ""

    for v in vitamins:

        # CHANGED BUTTON LINK

        cards_html += f"""

        <div class="product-item">

            <div class="image-wrapper"><img src="{v['img']}" class="product-image"></div>

            <h3>{v['name']}</h3>

            <p style="font-size:0.9rem; color:#666;">{v['desc']}</p>

            <a href="/api/log-action?cat=Order&item={v['name']}" class="name-button">Add to Cart</a>

        </div>"""



    css = """<style>.product-grid-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 25px; padding: 20px; } .product-item { background: white; width: 220px; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); transition: 0.3s; } .product-item:hover { transform: translateY(-5px); } .image-wrapper { height: 150px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; } .product-image { max-height: 100%; max-width: 100%; } .name-button { background: #e91e63; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; width: 100%; margin-top: 10px; text-decoration:none; display:inline-block; }</style>"""



    content = f"""{css}<div class="card" style="text-align:center;"><h2 style="color:#e91e63;">Vitamins & Supplements</h2><p>Boost your health daily</p><div class="product-grid-container">{cards_html}</div><a href="/drugs-store"><button style="margin-top:20px;">Back to Store</button></a></div>"""

    html = f"<!DOCTYPE html><html><head><title>Vitamins</title></head><body>{nav_bar(user, lang)}{content}</body></html>"

    return html.encode('utf-8')



# =========================================================

# 1. ORGAN SYSTEM DATABASE (இது இருந்தால் தான் வேலை செய்யும்)

# =========================================================

ORGAN_SYSTEM_DB = {

    'diabetic': {

        'en': {

            'title': 'Diabetic Counselling',

            'desc': 'Diet charts, sugar monitoring & insulin training.',

            'content': 'Diabetes management requires a holistic approach. We provide:\n1. Customized Diet Plans.\n2. Exercise Routines.\n3. Glucose Monitoring.'

        },

        'ta': {

            'title': 'நீரிழிவு ஆலோசனை',

            'desc': 'உணவு அட்டவணை மற்றும் இன்சுலின் பயிற்சி.',

            'content': 'நீரிழிவு மேலாண்மைக்கான முழுமையான அணுகுமுறை:\n1. உணவுத் திட்டங்கள்.\n2. உடற்பயிற்சி.\n3. சர்க்கரை அளவு கண்காணிப்பு.'

        }

    },

    'geriatric': {

        'en': {

            'title': 'Geriatric Counselling',

            'desc': 'Elderly care, mobility support & memory exercises.',

            'content': 'We ensure quality of life for the elderly via:\n1. Fall prevention strategies.\n2. Dementia support.\n3. Medication management.'

        },

        'ta': {

            'title': 'முதியோர் ஆலோசனை',

            'desc': 'முதியோர் பராமரிப்பு மற்றும் நினைவாற்றல் பயிற்சிகள்.',

            'content': 'முதியோர்களுக்கான சேவைகள்:\n1. வீழ்ச்சி தடுப்பு.\n2. நினைவாற்றல் பயிற்சி.\n3. மருந்து நிர்வாகம்.'

        }

    },

    'lab_reports': {

        'en': {

            'title': 'Lab Reports & Radiology',

            'desc': 'Interpretation of Blood tests, X-Rays, MRI & CT.',

            'content': 'Upload your reports for expert analysis. We explain MRI, CT, and Blood work results clearly.'

        },

        'ta': {

            'title': 'ஆய்வக அறிக்கைகள்',

            'desc': 'ரத்த பரிசோதனை, X-Ray, MRI விளக்கங்கள்.',

            'content': 'உங்கள் மருத்துவ அறிக்கைகளை பதிவேற்றுங்கள். நாங்கள் தெளிவான விளக்கத்தை அளிக்கிறோம்.'

        }

    },

    'only_counselling': {

        'en': {

            'title': 'General Counselling',

            'desc': 'Mental health, stress relief & lifestyle advice.',

            'content': 'A safe space for:\n1. Stress management.\n2. Work-life balance.\n3. Sleep hygiene.'

        },

        'ta': {

            'title': 'பொது ஆலோசனை',

            'desc': 'மனநலம் மற்றும் வாழ்க்கை முறை ஆலோசனை.',

            'content': 'மன அழுத்தம் மற்றும் தூக்கமின்மைக்கான தீர்வுகள்.'

        }

    },

    'bp_counselling': {

        'en': {

            'title': 'BP (Hypertension) Care',

            'desc': 'DASH diet & heart health monitoring.',

            'content': 'Control High BP with:\n1. Low sodium diet.\n2. Weight management.\n3. Regular monitoring.'

        },

        'ta': {

            'title': 'இரத்த அழுத்த (BP) பராமரிப்பு',

            'desc': 'உணவு முறை மற்றும் இதய ஆரோக்கியம்.',

            'content': 'BP கட்டுப்படுத்த:\n1. குறைந்த உப்பு உணவு.\n2. உடல் எடை குறைப்பு.\n3. தொடர் பரிசோதனை.'

        }

    }

}



def page_organ_system_detail(user, lang, topic_id, params=None):

    # 1. Topic செக்கிங்

    if topic_id not in ORGAN_SYSTEM_DB:

        return page_notfound("Topic ID", user, lang)

    

    # 2. டேட்டா எடுத்தல்

    data = ORGAN_SYSTEM_DB[topic_id][lang]

    title = data['title']

    main_content = data['content'].replace('\n', '<br>')

    

    # 3. Status Message Logic

    status_msg = ""

    if params and 'status' in params:

        if params['status'][0] == 'success':

            status_msg = "<div style='background:#d4edda; color:#155724; padding:15px; border-radius:5px; margin-bottom:20px; border:1px solid #c3e6cb;'>✅ Report Uploaded Successfully! Admin will review it shortly.</div>"

        elif params['status'][0] == 'failed':

            status_msg = "<div style='background:#f8d7da; color:#721c24; padding:15px; border-radius:5px; margin-bottom:20px; border:1px solid #f5c6cb;'>❌ Upload Failed. Please try again.</div>"



    # --- STYLE (டிசைன்) ---

    styles = """

    <style>

        .fade-in { animation: fadeIn 0.8s ease-in; }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

        

        .content-box {

            background: #ffffff;

            border: 1px solid #e0e0e0; border-radius: 20px;

            padding: 35px; text-align: left; line-height: 1.9;

            font-size: 1.15rem; color: #555; margin: 30px 0;

            box-shadow: 0 10px 30px rgba(0,0,0,0.05); position: relative; overflow: hidden;

        }

        .content-box::before {

            content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 5px;

            background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);

        }



        /* Upload Box */

        .upload-box {

            background: #f8f9fa; border: 2px dashed #007bff; border-radius: 15px;

            padding: 30px; text-align: center; margin-bottom: 30px;

        }



        /* BADGES (இதுதான் உங்களுக்கு வராம இருக்கு) */

        .ellipse-top {

            background: linear-gradient(135deg, #f1c40f 0%, #f39c12 100%);

            color: #fff; border-radius: 50px; padding: 12px 35px;

            display: inline-block; font-weight: bold; font-size: 1.1rem;

            box-shadow: 0 4px 15px rgba(243, 156, 18, 0.4);

            text-transform: uppercase; border: 2px solid #fff;

        }

        .bottom-row {

            display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 30px; margin-top: 10px;

        }

        .diamond-badge {

            position: relative; padding: 15px 30px; border-radius: 50px;

            color: white; font-weight: bold; font-size: 1.1rem;

            display: flex; align-items: center; justify-content: center;

            box-shadow: 0 10px 20px rgba(0,0,0,0.2); border: 3px solid white;

            min-width: 200px;

        }

        .badge-time { background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%); }

        .badge-price { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); flex-direction: column; line-height: 1.2; }

    </style>

    """



    # --- HTML CONTENT ---

    

    if topic_id == 'lab_reports':

        # 3rd Box (Lab Reports) - Price Tag வராது

        specific_content = f'''

        <div class="card fade-in" style="max-width: 900px; margin: 0 auto; text-align: center;">

            <h1 style="color: #2c3e50; font-size: 2rem; margin-bottom: 25px;">{title}</h1>

            {status_msg}



            <form method="POST" action="/upload-organ-report" enctype="multipart/form-data">

                <div class="upload-box">

                    <h3 style="color: #007bff; margin-top:0;">Upload Reports / Images</h3>

                    <p>Upload your Lab Reports, X-Rays, MRI, or CT Scan images here.</p>

                    <input type="file" name="report_file" required style="margin: 10px 0;">

                    <br>

                    <button type="submit" style="background:#007bff; color:white; padding:10px 20px; border:none; border-radius:5px; cursor:pointer; margin-top:10px;">Upload & Submit</button>

                </div>

            </form>



            <div class="content-box">{main_content}</div>



            <br>

            <a href="/organ-system-service"><button style="background-color: #555; padding: 12px 25px;">{LANG[lang]['back_to_organ_menu']}</button></a>

        </div>

        '''

    else:

        # மற்ற 4 Boxes - Price Tag & Badges வரும்

        specific_content = f'''

        <div class="card fade-in" style="max-width: 900px; margin: 0 auto; text-align: center;">

            <h1 style="color: #2c3e50; font-size: 2rem; margin-bottom: 25px; text-transform: uppercase;">{title}</h1>

            

            <div style="margin-bottom: 20px;">

                <div class="ellipse-top">{LANG[lang]['seven_services']}</div>

            </div>



            <div class="content-box">

                {main_content}

            </div>



            <div class="bottom-row">

                <div class="diamond-badge badge-time">

                    <span>🕒 {LANG[lang]['ninety_days']}</span>

                </div>

                <div class="diamond-badge badge-price">

                    <span style="font-size: 0.9rem; text-decoration: line-through; opacity: 0.8;">{LANG[lang]['price_tag_old']}</span>

                    <span style="font-size: 1.4rem; font-weight: 800;">{LANG[lang]['price_tag_new']} 💥</span>

                </div>

            </div>

            

            <br>

            <a href="/api/log-action?cat=Booking&item={title}" style="text-decoration:none;">

                <button style="background-color: #007bff; color: white; padding: 15px 30px; border-radius: 30px; font-weight:bold; cursor:pointer;">

                   Start Program Now

                </button>

            </a>



            <br><br>

            <a href="/organ-system-service"><button style="background-color: #555; padding: 12px 25px;">{LANG[lang]['back_to_organ_menu']}</button></a>

        </div>

        '''



    html = f"<!DOCTYPE html><html><head><title>{title}</title>{styles}</head><body>{nav_bar(user, lang)}{specific_content}</body></html>"

    return html.encode('utf-8')



def page_organ_system_menu(user, lang):

    styles = """

    <style>

        .topic-grid { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; padding: 20px; }

        .topic-box {

            flex: 1 1 300px; max-width: 350px;

            background: white; border: 1px solid #ddd;

            border-radius: 15px; padding: 25px;

            text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);

            transition: transform 0.2s; cursor: pointer;

            text-decoration: none; color: #333;

        }

        .topic-box:hover { transform: translateY(-5px); border-color: #9c27b0; }

        .topic-title { font-size: 1.3rem; font-weight: bold; color: #4a148c; margin-bottom: 10px; }

        .topic-desc { font-size: 0.95rem; color: #666; }

    </style>

    """

    boxes_html = ""

    for key, data in ORGAN_SYSTEM_DB.items():

        title = data[lang]['title']

        desc = data[lang]['desc']

        link = f"/organ-system-detail?id={key}"

        boxes_html += f"""

        <a href="{link}" class="topic-box">

            <div class="topic-title">{title}</div>

            <div class="topic-desc">{desc}</div>

            <br><span style="color: #9c27b0; font-weight: bold;">Click to View &rarr;</span>

        </a>

        """



    content = f'''

    <div class="card" style="max-width: 1000px; margin: 0 auto; text-align: center;">

        <h2 style="color: #2c3e50;">Organ System Services</h2>

        <div class="topic-grid">{boxes_html}</div>

        <div style="margin-top: 30px;"><a href="/services"><button>Back to Services</button></a></div>

    </div>

    '''

    return f"<!DOCTYPE html><html><head><title>Organ Services</title>{styles}</head><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



def page_shop_detail(user, lang, shop_id, filter_meds=None):

    shop = next((s for s in MEDICAL_SHOPS if s['id'] == shop_id), None)

    shop_name = shop['name'] if shop else "Medical Shop"

    medicines = SHOP_SPECIFIC_STOCK

    json_data = json.dumps(medicines) 



    meds_html = ""

    # மருந்துகளை லிஸ்ட் செய்யும் லூப்

    for m in medicines:

        meds_html += f"""

        <div style="display:flex; justify-content:space-between; padding:15px; border-bottom:1px solid #eee;">

            <div><strong>{m['name']}</strong><br><small>₹{m['price']}</small></div>

            <a href="/api/log-action?cat=Order&item={m['name']} at {shop_name}" style="background:#28a745; color:white; padding:5px 15px; text-decoration:none; border-radius:20px; font-size:0.8rem;">Add</a>

        </div>"""



    content = f"""

    <div style="max-width:800px; margin:0 auto; padding:20px; font-family:sans-serif;">

        <div style="background:#28a745; color:white; padding:30px; text-align:center; border-radius:15px;">

            <h1>🏥 {shop_name}</h1>

        </div>



        <div style="position:relative; margin:20px 0;">

            <input type="text" id="shopSearch" onkeyup="searchMeds()" onkeypress="checkEnter(event)" 

                   style="width:100%; padding:15px 25px; border-radius:35px; border:2px solid #28a745; outline:none; font-size:16px;" 

                   placeholder="Search medicine & press Enter...">

            <div id="searchRes" style="position:absolute; top:60px; left:0; right:0; background:white; border:1px solid #ddd; border-radius:15px; z-index:100; display:none; box-shadow:0 10px 25px rgba(0,0,0,0.1); overflow:hidden;"></div>

        </div>



        <div style="background:#f9fff9; border:2px dashed #28a745; padding:25px; text-align:center; border-radius:20px; margin-bottom:25px;">

            <h3>📤 Upload Prescription</h3>

            <form method="post" action="/upload-prescription" enctype="multipart/form-data">

                <input type="file" name="prescription" required>

                

                <input type="hidden" name="shop_id" value="{shop_id}">

                <input type="hidden" name="source" value="shop_page"> 

                

                <br><br>

                <button type="submit" style="background:#28a745; color:white; border:none; padding:12px 30px; border-radius:10px; cursor:pointer; font-weight:bold;">Check Stock Status</button>

            </form>

        </div>



        <a href="/video-consult?target={shop_name}" style="text-decoration:none;">

            <button style="width:100%; padding:18px; background:linear-gradient(135deg, #e91e63 0%, #c2185b 100%); color:white; border:none; border-radius:15px; font-size:1.1rem; font-weight:bold; cursor:pointer;">📹 Video Call {shop_name}</button>

        </a>



        <div style="background:white; border:1px solid #eee; border-radius:20px; padding:25px; margin-top:25px;">

            <h3>Available Medicines</h3>

            {meds_html}

        </div>

        <center><br><a href="/pharmacy-consult" style="color:#666;">&larr; Back to Shops</a></center>

    </div>



    <script>

        const shopStock = {json_data};

        function searchMeds() {{

            const input = document.getElementById('shopSearch').value.toLowerCase();

            const resDiv = document.getElementById('searchRes');

            resDiv.innerHTML = "";

            if (!input) {{ resDiv.style.display = "none"; return; }}

            const filtered = shopStock.filter(i => i.name.toLowerCase().includes(input));

            if (filtered.length > 0) {{

                resDiv.style.display = "block";

                filtered.forEach(i => {{

                    const d = document.createElement("div");

                    d.style = "padding:12px; border-bottom:1px solid #eee; cursor:pointer;";

                    d.innerHTML = `💊 ${{i.name}} <span style="float:right; color:#28a745;">₹${{i.price}}</span>`;

                    d.onclick = () => {{ window.location.href = "/shop-search-result?shop_id={shop_id}&q=" + i.name; }};

                    resDiv.appendChild(d);

                }});

            }} else {{ resDiv.style.display = "none"; }}

        }}

        function checkEnter(e) {{

            if (e.key === 'Enter') {{

                const val = document.getElementById('shopSearch').value;

                if(val) window.location.href = "/shop-search-result?shop_id={shop_id}&q=" + val;

            }}

        }}

    </script>

    """

    return f"<!DOCTYPE html><html><head><title>{shop_name}</title></head><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')

# --- 2. GLOBAL SEARCH RESULT (Where is the medicine?) ---





def page_global_search_result(user, lang, query):

    # எந்தெந்த கடையில் இந்த மருந்து இருக்குனு தேடுவோம்

    available_shops = []

    

    # Simple logic: Check against SHOP_SPECIFIC_STOCK (Demo Data)

    # ரியல் டைம்ல ஒவ்வொரு கடைக்கும் தனி DB இருக்கும்.

    is_available = any(m['name'].lower() == query.lower() for m in SHOP_SPECIFIC_STOCK)

    

    if is_available:

        # சும்மா டெமோக்காக: அந்த மருந்து லிஸ்ட்ல இருந்தா, எல்லா கடையையும் காட்டுவோம்

        available_shops = MEDICAL_SHOPS

    

    shops_html = ""

    if available_shops:

        for s in available_shops:

            shops_html += f"""

            <div style="border:1px solid #eee; background:white; padding:15px; border-radius:10px; display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">

                <div style="text-align:left;">

                    <b style="font-size:1.1rem;">{s["name"]}</b><br>

                    <small style="color:#666;">📍 {s["area"]}</small><br>

                    <span style="color:green; font-size:0.8rem;">✅ Stock Available</span>

                </div>

                <a href="/shop-search-result?shop_id={s['id']}&q={query}">

                    <button style="background:#007bff; color:white; border:none; padding:8px 15px; border-radius:5px; cursor:pointer;">View Price & Order</button>

                </a>

            </div>"""

    else:

        shops_html = "<p>Sorry, this medicine is not available in any partner shops.</p>"



    content = f"""

    <div style="max-width:800px; margin:40px auto; padding:20px; text-align:center; font-family:sans-serif;">

        <h1 style="color:#007bff;">🔍 Search Results: "{query}"</h1>

        <p>This medicine is available in the following shops:</p>

        <div style="margin-top:30px;">

            {shops_html}

        </div>

        <br>

        <a href="/pharmacy-consult" style="color:#666;">&larr; Back to Search</a>

    </div>

    """

    return f"<!DOCTYPE html><html><head><title>Search Results</title></head><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



def page_prescription_results(user, lang, found_ids, source="main_page", shop_id=None):

    found_list = found_ids.split(',') if found_ids else []

    result_html = ""

    back_link = "/services"



    # ====================================================

    # CASE 1: DRUGS STORE UPLOAD (Search Internal DBs only)

    # ====================================================

    if source == "drugs_store":

        result_html += "<h2>💊 Online Store Search Results</h2>"

        found_any = False

        

        # உங்ககிட்ட ஏற்கனவே இருக்கிற எல்லா DB-யையும் இங்க லிஸ்ட் பண்றேன்

        # குறிப்பு: இதுல இல்லாத DB பெயர் இருந்தா அதை நீக்கிடுங்க

        full_inventory = {}

        if 'ALLOPATHY_DB' in globals(): full_inventory.update(ALLOPATHY_DB)

        if 'HERBAL_DB' in globals(): full_inventory.update(HERBAL_DB)

        if 'HOMEOPATHY_DB' in globals(): full_inventory.update(HOMEOPATHY_DB)

        if 'DEVICES_DB' in globals(): full_inventory.update(DEVICES_DB)

        if 'VITAMINS_DB' in globals(): full_inventory.update(VITAMINS_DB)

        

        # ஒருவேளை மேலே சொன்ன DB பெயர்கள் உங்க கோட்ல வேற மாதிரி இருந்தா, அதை இங்க மாத்திக்கோங்க.

        

        for m_name in found_list:

            m_name_clean = m_name.strip().lower()

            match_key = None

            match_item = None

            

            # Inventory-ல் தேடுதல்

            for key, val in full_inventory.items():

                # Title அல்லது Key-ல் தேடுறோம்

                title = val.get('title', val.get('name', ''))

                if m_name_clean in title.lower() or m_name_clean in key.lower():

                    match_key = key

                    match_item = val

                    break

            

            if match_item:

                found_any = True

                title = match_item.get('title', match_item.get('name', 'Unknown'))

                price = match_item.get('price', 'Check Price')

                # டைப் (Type) இல்லனா General-னு வைச்சுக்கலாம்

                category = match_item.get('type', 'General') 

                

                result_html += f"""

                <div style="background:white; border-left:5px solid #28a745; padding:15px; margin-bottom:15px; border-radius:5px; box-shadow:0 2px 5px rgba(0,0,0,0.1); display:flex; justify-content:space-between; align-items:center;">

                    <div>

                        <b style="font-size:1.1rem; color:#2c3e50;">{title}</b><br>

                        <span style="background:#e8f5e9; color:#2e7d32; padding:2px 8px; border-radius:10px; font-size:0.8rem;">{category}</span>

                        <span style="margin-left:10px; color:#555;">Price info inside</span>

                    </div>

                    <a href="/product-detail?id={match_key}" style="background:#28a745; color:white; padding:10px 20px; text-decoration:none; border-radius:50px; font-weight:bold;">View Details</a>

                </div>"""

            else:

                result_html += f"""

                <div style="background:#fff5f5; border:1px solid #fc8181; padding:15px; border-radius:5px; margin-bottom:10px; color:#c53030;">

                    <b>❌ {m_name}</b> - Not available in Online Store.

                </div>"""

        

        if not found_any:

            result_html += "<p style='text-align:center;'>No matching products found in our online inventory.</p>"

        

        back_link = "/drugs-store"



    # ====================================================

    # CASE 2: PHARMACIST UPLOAD (Search Medical Shops)

    # ====================================================

    elif source == "pharmacy_main":

        result_html += "<h2>🏥 Stock Availability in Partner Shops</h2>"

        result_html += "<p>We found your medicines in these partner shops:</p>"

        

        # Logic: SHOP_SPECIFIC_STOCK லிஸ்ட்ல மருந்து இருக்கான்னு பார்க்கிறோம்

        medicines_found = []

        for m_name in found_list:

            m_clean = m_name.strip().lower()

            stock_item = next((i for i in SHOP_SPECIFIC_STOCK if i['name'].lower() in m_clean), None)

            if stock_item:

                medicines_found.append(stock_item)

        

        if medicines_found:

            # மருந்து இருக்குன்னா, எல்லா மெடிக்கல் ஷாப்பையும் காட்டுவோம் (Demo Logic)

            for shop in MEDICAL_SHOPS:

                meds_text = ", ".join([f"{m['name']} (₹{m['price']})" for m in medicines_found])

                

                result_html += f"""

                <div style="background:white; border:1px solid #ddd; padding:20px; margin-bottom:15px; border-radius:10px; box-shadow:0 3px 6px rgba(0,0,0,0.05);">

                    <div style="display:flex; justify-content:space-between; align-items:start;">

                        <div>

                            <h3 style="margin:0; color:#007bff;">{shop['name']}</h3>

                            <p style="margin:5px 0; color:#666;">📍 {shop['area']}</p>

                            <div style="margin-top:10px; padding:10px; background:#f0f8ff; border-radius:5px; font-size:0.9rem;">

                                <b>Available:</b> {meds_text}

                            </div>

                        </div>

                        <a href="/shop-detail?id={shop['id']}">

                            <button style="background:#007bff; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer;">Visit Shop</button>

                        </a>

                    </div>

                </div>"""

        else:

             result_html += "<div style='text-align:center; padding:30px; background:white;'><h3>❌ Out of Stock</h3><p>Sorry, none of our partner shops have these medicines currently.</p></div>"



        back_link = "/pharmacy-consult"



    # ====================================================

    # CASE 3: INSIDE A SPECIFIC SHOP

    # ====================================================

    elif source == "shop_page" and shop_id:

        shop = next((s for s in MEDICAL_SHOPS if s['id'] == shop_id), None)

        sname = shop['name'] if shop else "Shop"

        result_html += f"<h2>Stock Status at {sname}</h2>"

        for m_name in found_list:

            m_name = m_name.strip()

            item = next((i for i in SHOP_SPECIFIC_STOCK if i['name'].lower() in m_name.lower()), None)

            if item:

                result_html += f"""<div style="background:#d4edda; padding:15px; border-radius:10px; margin-bottom:10px; border:1px solid #c3e6cb;">✅ <b>{item['name']}</b> is Available - ₹{item['price']}<br><a href="/api/log-action?cat=Order&item={item['name']}" style="color:green; font-weight:bold; float:right;">Order Now</a><br style="clear:both;"></div>"""

            else:

                result_html += f"""<div style="background:#f8d7da; padding:15px; border-radius:10px; margin-bottom:10px; border:1px solid #f5c6cb;">❌ <b>{m_name}</b> - Out of Stock Here</div>"""

        back_link = f"/shop-detail?id={shop_id}"



    content = f"""<div style="max-width:700px; margin:40px auto; padding:20px; font-family:sans-serif;">{result_html}<br><br><center><a href="{back_link}"><button style="padding:10px 25px; cursor:pointer; background:#555; color:white; border:none; border-radius:20px;">&larr; Back</button></a></center></div>"""

    return f"<!DOCTYPE html><html><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



def page_shop_search_result(user, lang, shop_id, query):

    # 1. எந்தக் கடை என்று கண்டுபிடிக்கிறோம்

    shop = next((s for s in MEDICAL_SHOPS if s['id'] == shop_id), None)

    shop_name = shop['name'] if shop else "Medical Shop"



    # 2. அந்த மருந்து நம்மகிட்ட இருக்கிற லிஸ்ட் (SHOP_SPECIFIC_STOCK)-ல இருக்கான்னு பார்க்கிறோம்

    # (பெரிய எழுத்து/சின்ன எழுத்து பிரச்சனை வராம இருக்க lower() பயன்படுத்துறோம்)

    item = next((m for m in SHOP_SPECIFIC_STOCK if m['name'].lower() == query.lower().strip()), None)



    status_html = ""



    if item:

        # --- மருந்து இருந்தால் (Green Logic) ---

        status_html = f"""

        <div style="background:#d4edda; border:1px solid #c3e6cb; padding:30px; border-radius:15px; text-align:center; color:#155724; box-shadow:0 4px 6px rgba(0,0,0,0.05);">

            <div style="font-size:3rem;">✅</div>

            <h2 style="margin:10px 0;">In Stock!</h2>

            <p style="font-size:1.2rem;"><b>{item['name']}</b> is available at {shop_name}.</p>

            <h3 style="color:#28a745;">Price: ₹{item['price']}</h3>

            <br>

            <a href="/api/log-action?cat=Order&item={item['name']} at {shop_name}">

                <button style="background:#28a745; color:white; padding:12px 30px; border:none; border-radius:25px; font-size:1rem; cursor:pointer; font-weight:bold;">Order Now</button>

            </a>

        </div>

        """

    else:

        # --- மருந்து இல்லை என்றால் (Red Logic) ---

        status_html = f"""

        <div style="background:#f8d7da; border:1px solid #f5c6cb; padding:30px; border-radius:15px; text-align:center; color:#721c24; box-shadow:0 4px 6px rgba(0,0,0,0.05);">

            <div style="font-size:3rem;">❌</div>

            <h2 style="margin:10px 0;">Stock Over</h2>

            <p style="font-size:1.1rem;">Sorry, <b>{query}</b> is currently not available at {shop_name}.</p>

            <p style="font-size:0.9rem; color:#666;">Try checking other partner shops.</p>

        </div>

        """



    content = f"""

    <div style="max-width:600px; margin:40px auto; padding:20px; font-family:sans-serif;">

        {status_html}

        <br><br>

        <center>

            <a href="/shop-detail?id={shop_id}" style="text-decoration:none;">

                <button style="padding:10px 25px; background:#555; color:white; border:none; border-radius:30px; cursor:pointer; font-weight:bold;">&larr; Back to {shop_name}</button>

            </a>

        </center>

    </div>

    """

    return f"<!DOCTYPE html><html><head><title>Search Result - {shop_name}</title></head><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



def page_nurse_video_call(user, lang):

    content = f"""

    <div style="max-width:900px; margin:20px auto; padding:20px; font-family:sans-serif; text-align:center;">

        <div style="background:#000; height:500px; border-radius:30px; display:flex; flex-direction:column; align-items:center; justify-content:center; color:white; box-shadow:0 20px 50px rgba(0,0,0,0.3);">

            <div style="font-size:5rem; margin-bottom:20px;">👩‍⚕️</div>

            <h2>Connecting to Next Available Nurse...</h2>

            <p>Please wait, you are in queue.</p>

            <div style="margin-top:20px;">

                <img src="https://i.gifer.com/ZZ5H.gif" width="50">

            </div>

            <br><br>

            <a href="/nurse-services"><button style="background:red; color:white; border:none; padding:15px 40px; border-radius:30px; cursor:pointer; font-weight:bold;">End Call</button></a>

        </div>

    </div>

    """

    return f"<!DOCTYPE html><html><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



# --- 1. PAGE: HOMEOPATHY PRODUCTS ---

def page_homeopathy_products(user, lang):

    cards_html = ""

    # DB-ல் இருந்து டேட்டாவை எடுக்கிறோம்

    for key, val in HOMEOPATHY_DB.items():

        link = f"/product-detail?id={key}"

        cards_html += f"""

        <div class="product-item">

            <div class="image-wrapper"><img src="{val['image']}" class="product-image"></div>

            <h3>{val['title']}</h3>

            <p style="font-size:0.9rem; color:#666;">{val['desc']}</p>

            <a href="{link}" class="name-button">View Details</a>

        </div>"""



    styles = '''<style>.product-grid-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 25px; padding: 20px; } .product-item { background: white; width: 220px; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); transition: 0.3s; } .product-item:hover { transform: translateY(-5px); } .image-wrapper { height: 150px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; } .product-image { max-height: 100%; max-width: 100%; } .name-button { background: #6f42c1; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; width: 100%; margin-top: 10px; text-decoration:none; display:inline-block; }</style>'''

    

    content = f'''{styles}<div class="card" style="text-align:center;"><h2 style="color:#6f42c1;">Homeopathy Medicines</h2><p>Natural & Safe Remedies</p><div class="product-grid-container">{cards_html}</div><a href="/drugs-store"><button style="margin-top:20px;">Back to Store</button></a></div>'''

    return f"<!DOCTYPE html><html><head><title>Homeopathy</title></head><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')





# --- 2. PAGE: MEDICAL DEVICES ---

def page_medical_devices(user, lang):

    cards_html = ""

    for key, val in DEVICES_DB.items():

        link = f"/product-detail?id={key}"

        cards_html += f"""

        <div class="product-item">

            <div class="image-wrapper"><img src="{val['image']}" class="product-image"></div>

            <h3>{val['title']}</h3>

            <p style="font-size:0.9rem; color:#666;">{val['desc']}</p>

            <a href="{link}" class="name-button" style="background:#e67e22;">View Details</a>

        </div>"""



    styles = '''<style>.product-grid-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 25px; padding: 20px; } .product-item { background: white; width: 220px; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); transition: 0.3s; } .product-item:hover { transform: translateY(-5px); } .image-wrapper { height: 150px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; } .product-image { max-height: 100%; max-width: 100%; } .name-button { color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; width: 100%; margin-top: 10px; text-decoration:none; display:inline-block; }</style>'''



    content = f'''{styles}<div class="card" style="text-align:center;"><h2 style="color:#e67e22;">Medical Devices</h2><p>Essential Healthcare Gadgets</p><div class="product-grid-container">{cards_html}</div><a href="/drugs-store"><button style="margin-top:20px;">Back to Store</button></a></div>'''

    return f"<!DOCTYPE html><html><head><title>Medical Devices</title></head><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')





# --- 3. PAGE: VITAMINS ---

def page_vitamins(user, lang):

    cards_html = ""

    for key, val in VITAMINS_DB.items():

        link = f"/product-detail?id={key}"

        cards_html += f"""

        <div class="product-item">

            <div class="image-wrapper"><img src="{val['image']}" class="product-image"></div>

            <h3>{val['title']}</h3>

            <p style="font-size:0.9rem; color:#666;">{val['desc']}</p>

            <a href="{link}" class="name-button" style="background:#e91e63;">View Details</a>

        </div>"""



    styles = '''<style>.product-grid-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 25px; padding: 20px; } .product-item { background: white; width: 220px; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); transition: 0.3s; } .product-item:hover { transform: translateY(-5px); } .image-wrapper { height: 150px; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; } .product-image { max-height: 100%; max-width: 100%; } .name-button { color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; width: 100%; margin-top: 10px; text-decoration:none; display:inline-block; }</style>'''



    content = f'''{styles}<div class="card" style="text-align:center;"><h2 style="color:#e91e63;">Vitamins & Supplements</h2><p>Boost your health daily</p><div class="product-grid-container">{cards_html}</div><a href="/drugs-store"><button style="margin-top:20px;">Back to Store</button></a></div>'''

    return f"<!DOCTYPE html><html><head><title>Vitamins</title></head><body>{nav_bar(user, lang)}{content}</body></html>".encode('utf-8')



# =======================================================================

# MAIN APP ENTRY POINT (100% Complete Version)

# =======================================================================

def app(environ, start_response):

    status = '200 OK'

    lang_cookie = get_cookie(environ, 'lang')

    lang = lang_cookie if lang_cookie in LANG else 'en'

    

    path = environ.get("PATH_INFO", "/")

    cookie_session = get_cookie(environ, "session_id")

    user = SESSIONS.get(cookie_session) if cookie_session else None



    # --- 1. LANGUAGE SETTING ---

    if path == '/set-language':

        params = parse_qs(environ.get('QUERY_STRING', ''))

        new_lang = params.get('lang', ['en'])[0]

        ref = params.get('ref', [environ.get('HTTP_REFERER', '/home')])[0]

        headers = [('Location', ref), ('Set-Cookie', make_set_cookie_header('lang', new_lang))]

        start_response('302 Found', headers)

        return [b'']

        

    # --- 2. STATIC & UPLOADS ---

    if path.startswith('/static/'): return serve_static_file(environ, start_response, path)

    if path.startswith('/uploads/'): return serve_upload_file(environ, start_response, path)

    

    # --- 3. AUTH ROUTES (UPDATED) ---

    if path == '/logout': return page_logout(environ, start_response)



    if path == '/admin':

        if not user: 

            start_response("302 Found", [("Location", "/login")])

            return [b'']

        response = page_admin_dashboard(user, lang)

        start_response('200 OK', [("Content-type", "text/html; charset=utf-8")])

        return [response]



    elif path == '/admin/staff':

        response = page_admin_staff(user, lang)

        start_response('200 OK', [("Content-type", "text/html; charset=utf-8")])

        return [response]



    elif path == '/admin/patients':

        response = page_admin_patients(user, lang)

        start_response('200 OK', [("Content-type", "text/html; charset=utf-8")])

        return [response]



    elif path == '/admin/create-user' and environ['REQUEST_METHOD'] == 'POST':

        try:

            length = int(environ.get("CONTENT_LENGTH", 0))

            body = environ['wsgi.input'].read(length)

            data = parse_qs(body.decode('utf-8'))

            name = data.get('name', [''])[0]

            email = data.get('email', [''])[0]

            role = data.get('role', ['Doctor'])[0]

            pwd = data.get('password', ['123'])[0]

            if email:

                USERS[email] = {"password": pwd, "role": role, "name": name}

                save_users(USERS)

        except: pass

        start_response("302 Found", [("Location", "/admin/staff")])

        return [b'']



    elif path == '/admin/delete-user' and environ['REQUEST_METHOD'] == 'POST':

        try:

            length = int(environ.get("CONTENT_LENGTH", 0))

            body = environ['wsgi.input'].read(length)

            data = parse_qs(body.decode('utf-8'))

            email = data.get('email', [''])[0]

            if email in USERS:

                del USERS[email]

                save_users(USERS)

        except: pass

        ref = environ.get('HTTP_REFERER', '/admin')

        start_response("302 Found", [("Location", ref)])

        return [b'']



    # --- 4. PAGE ROUTING ---

    if path == "/": response = page_logo_only()

    elif path == "/home": response = page_home(user, lang)

    elif path == "/about": response = page_about(user, lang)

    elif path == "/login":

        response = page_login(environ, start_response, user, lang)

        if isinstance(response, list): return response

    elif path == "/signup":

        response = page_signup(environ, start_response, user, lang)

        if isinstance(response, list): return response



    elif path == "/services":

        if not user:

            start_response("302 Found", [("Location", "/login")])

            return [b'']

        if user == "admin@genmedx.com":

            start_response("302 Found", [("Location", "/admin")])

            return [b'']

        elif user in ["doctor@genmedx.com", "nurse@genmedx.com"]:

            response = page_professional_dashboard(user, lang, "Doctor")

            start_response('200 OK', [("Content-type", "text/html; charset=utf-8")])

            return [response]

        response = page_services(user, lang)



    # --- MEDICAL SHOP ROUTES ---

    elif path == '/drugs-store':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        params = parse_qs(environ.get('QUERY_STRING', ''))

        response = page_drugs_store(user, lang, params)



    elif path == '/shop-detail':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        params = parse_qs(environ.get('QUERY_STRING', ''))

        shop_id = params.get('id', [''])[0]

        filter_meds = params.get('filter_meds', [None])[0]

        response = page_shop_detail(user, lang, shop_id, filter_meds)



    elif path == '/shop-search-result':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        params = parse_qs(environ.get('QUERY_STRING', ''))

        shop_id = params.get('shop_id', [''])[0]

        q = params.get('q', [''])[0]

        response = page_shop_search_result(user, lang, shop_id, q)



    # --- CONSULTATION SERVICES ---

    elif path == '/pharmacy-consult':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        response = page_pharmacy_consult(user, lang)



    elif path == '/video-consult':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        response = page_video_consult(user, lang, environ)



    elif path == '/prescription-results':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        params = parse_qs(environ.get('QUERY_STRING', ''))

        found_ids = params.get('ids', [''])[0]

        source = params.get('source', ['main_page'])[0]

        shop_id = params.get('shop_id', [None])[0]

        response = page_prescription_results(user, lang, found_ids, source, shop_id)



    # --- PRODUCT & ORGAN ROUTES ---

    elif path == '/drugs-store/ayurvedic':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        response = page_ayurvedic_products(user, lang)

    elif path == '/drugs-store/allopathy':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        response = page_allopathic_products(user, lang)

    elif path == '/drugs-store/homeopathy':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        response = page_homeopathy_products(user, lang)

    elif path == '/drugs-store/medical-devices':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        response = page_medical_devices(user, lang)

    elif path == '/drugs-store/vitamins':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        response = page_vitamins(user, lang)

    elif path == '/product-detail':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        params = parse_qs(environ.get('QUERY_STRING', ''))

        response = page_product_detail(user, lang, params.get('id', [''])[0])



    elif path == '/organ-system-service':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        response = page_organ_system_menu(user, lang)



    elif path == '/organ-system-detail':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        params = parse_qs(environ.get('QUERY_STRING', ''))

        response = page_organ_system_detail(user, lang, params.get('id', [''])[0], params)



    elif path == '/doctor-consult':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        response = page_doctor_consult(user, lang)

    elif path == '/nurse-services':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        response = page_nurse_services(user, lang)

    elif path == '/lab-details':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        response = page_lab_details(user, lang)

    elif path == '/ai-chat':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        response = page_ai_chat(user, lang)



    # --- 🔵 UPLOAD: ORGAN REPORT (இதுதான் மிஸ் ஆகியிருந்தது!) ---

    elif path == '/upload-organ-report' and environ.get('REQUEST_METHOD') == 'POST':

        try:

            from email.parser import BytesParser

            from email import policy

            content_length = int(environ.get('CONTENT_LENGTH', 0))

            body = environ['wsgi.input'].read(content_length)

            msg = BytesParser(policy=policy.default).parsebytes(b'Content-Type: ' + environ.get('CONTENT_TYPE', '').encode() + b'\r\n\r\n' + body)

            file_saved = False

            for part in msg.iter_parts():

                filename = part.get_filename()

                if filename:

                    if not os.path.exists('uploads/reports'): os.makedirs('uploads/reports')

                    filepath = os.path.join('uploads', 'reports', filename)

                    with open(filepath, 'wb') as f: f.write(part.get_payload(decode=True))

                    USER_ACTIVITIES.append({"email": user, "category": "Upload", "detail": f"Uploaded (Organ System): {filename}", "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

                    file_saved = True

                    break

            status_q = 'success' if file_saved else 'failed'

            start_response('302 Found', [('Location', f'/organ-system-detail?id=lab_reports&status={status_q}')])

            return [b'']

        except:

            start_response('302 Found', [('Location', '/organ-system-detail?id=lab_reports&status=failed')])

            return [b'']



    # --- 🔵 UPLOAD: PRESCRIPTION (Final Fixed Version) ---

    elif path == '/upload-prescription' and environ.get('REQUEST_METHOD') == 'POST':

        try:

            # 1. Read Request Body

            content_length = int(environ.get('CONTENT_LENGTH', 0))

            body = environ['wsgi.input'].read(content_length)

            

            # 2. Prepare Headers for Parsing

            content_type = environ.get('CONTENT_TYPE', '')

            headers_items = f"Content-Type: {content_type}\nContent-Length: {content_length}\n\n".encode()

            

            # 3. Parse Multipart Data

            msg = message_from_bytes(headers_items + body, policy=HTTP)



            shop_id = ""

            source = "main_page"

            filename = ""

            file_data = None

            

            # 4. Extract Fields

            if msg.is_multipart():

                for part in msg.iter_parts():

                    disposition = part.get("Content-Disposition", "")

                    if 'name="shop_id"' in disposition:

                        shop_id = part.get_payload(decode=True).decode('utf-8').strip()

                    elif 'name="source"' in disposition:

                        source = part.get_payload(decode=True).decode('utf-8').strip()

                    elif 'name="prescription"' in disposition and part.get_filename():

                        filename = part.get_filename()

                        file_data = part.get_payload(decode=True)

            

            # 5. Check if File Exists

            if not file_data: 

                print("DEBUG: No file data found")

                start_response('302 Found', [('Location', '/services')])

                return [b'']

            

            # 6. Extract Text (OCR)

            extracted_text = extract_text_from_stream(filename, file_data)

            print(f"DEBUG: Source={source}, Extracted Text Length={len(extracted_text)}")

            

            found_medicines = []

            

            # 7. LOGIC: Decide Search Database based on Source

            if source == "drugs_store":

                # --- CASE A: Drugs Store Upload -> Search Online Inventory ---

                online_inventory = {}

                if 'ALLOPATHY_DB' in globals(): online_inventory.update(ALLOPATHY_DB)

                if 'HERBAL_DB' in globals(): online_inventory.update(HERBAL_DB)

                if 'HOMEOPATHY_DB' in globals(): online_inventory.update(HOMEOPATHY_DB)

                if 'DEVICES_DB' in globals(): online_inventory.update(DEVICES_DB)

                if 'VITAMINS_DB' in globals(): online_inventory.update(VITAMINS_DB)

                

                for key, val in online_inventory.items():

                    title = val.get('title', val.get('name', '')).lower()

                    # Check Name OR Key

                    if title in extracted_text.lower() or key in extracted_text.lower():

                        found_medicines.append(title)



            else:

                # --- CASE B: Pharmacist/Main Upload -> Search Shop Stock ---

                # (இங்கே SHOP_SPECIFIC_STOCK-ல் இருக்கும் பெயர்களை தேடுகிறோம்)

                if 'SHOP_SPECIFIC_STOCK' in globals():

                    for item in SHOP_SPECIFIC_STOCK:

                        if item['name'].lower() in extracted_text.lower():

                            found_medicines.append(item['name'])



            # 8. If nothing found, add dummy fallback (To avoid empty page)

            if not found_medicines: 

                # டெஸ்டிங்கிற்காக Dolo-வை சேர்க்கிறோம், 

                # ரியல் டைம்ல இதை எடுத்துவிட்டு "Not Found" காட்டலாம்.

                found_medicines = ["Dolo 650"] 



            # 9. Redirect to Results

            found_str = ",".join(found_medicines)

            # URL Encoding to be safe

            from urllib.parse import quote

            safe_ids = quote(found_str)

            

            redirect_url = f"/prescription-results?ids={safe_ids}&source={source}&shop_id={shop_id}"

            

            print(f"DEBUG: Redirecting to {redirect_url}")

            start_response('302 Found', [('Location', redirect_url)])

            return [b'']



        except Exception as e:

            # Error வந்தால் Blank Page வராமல் இருக்க, இதை பிரிண்ட் செய்து Home-க்கு அனுப்பும்

            print(f"CRITICAL ERROR in Upload: {str(e)}")

            start_response('302 Found', [('Location', '/services')])

            return [b'']

        

    elif path == '/global-search':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        params = parse_qs(environ.get('QUERY_STRING', ''))

        q = params.get('q', [''])[0]

        response = page_global_search_result(user, lang, q)



    elif path == '/nurse-video-call':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        response = page_nurse_video_call(user, lang)



    elif path == '/doctor-video-call':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        params = parse_qs(environ.get('QUERY_STRING', ''))

        doc_name = params.get('target', ['Doctor'])[0]

        response = page_doctor_video_call(user, lang, doc_name)



    elif path == '/api/log-action':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        params = parse_qs(environ.get('QUERY_STRING', ''))

        item = params.get('item', ['Unknown'])[0]

        USER_ACTIVITIES.append({"email": user, "category": "Order", "detail": item, "time": datetime.now().strftime("%H:%M:%S")})

        html = "<html><head><meta http-equiv='refresh' content='2;url=/services'></head><body style='text-align:center;padding:50px;'><h1>✅ Order Placed!</h1><p>Redirecting...</p></body></html>"

        start_response('200 OK', [("Content-type", "text/html; charset=utf-8")])

        return [html.encode('utf-8')]

    

    elif path == '/doctor-profile':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        params = parse_qs(environ.get('QUERY_STRING', ''))

        doc_id = params.get('id', [''])[0]

        response = page_doctor_profile(user, lang, doc_id)



    elif path == '/doctor-chat':

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        params = parse_qs(environ.get('QUERY_STRING', ''))

        doc_id = params.get('id', [''])[0]

        response = page_doctor_chat(user, lang, doc_id)

    

    elif path == '/api/chat':

        # Check input, generate AI response

        try:

            length = int(environ.get('CONTENT_LENGTH', 0))

            body = environ['wsgi.input'].read(length).decode('utf-8')

            user_msg = body

            if body.startswith('{'): 

                try: user_msg = json.loads(body).get('message', '') 

                except: pass

            reply = get_ai_response(user_msg) if user_msg else "Hi there!"

            resp = json.dumps({"reply": reply}).encode('utf-8')

            start_response('200 OK', [('Content-Type', 'application/json')])

            return [resp]

        except:

            return [b'{"reply": "Error"}']

        

    # Nurse service detail route

    elif path.startswith('/nurse-service/'):

        if not user: start_response("302 Found", [("Location", "/login")]); return [b'']

        # URL-ல் இருந்து சர்வீஸ் பெயரை பிரித்தெடுத்தல்

        service_key = path.split('/')[-1]

        

        # Dictionary-ல் இருந்து விபரங்களை எடுத்தல்

        # (NURSE_SERVICE_DETAILS ஏற்கனவே உங்க கோட்ல மேல இருக்கு)

        details = NURSE_SERVICE_DETAILS.get(lang, NURSE_SERVICE_DETAILS['en']).get(service_key, {})

        title = details.get('title', 'Service')

        desc = details.get('description', 'Details coming soon...')

        

        response = page_nurse_service_detail(user, lang, title, desc)



    # --- 404 NOT FOUND ---

    else:

        response = page_notfound(path, user, lang)

        start_response('404 Not Found', [("Content-type", "text/html; charset=utf-8")])

        return [response]



    start_response(status, [("Content-type", "text/html; charset=utf-8")])

    if isinstance(response, str): response = response.encode('utf-8')

    return [response]



if __name__ == "__main__":

    HOST, PORT = "", 8080

    if not os.path.exists('uploads'):

        os.makedirs('uploads')

    print(f"Starting GenMedX server on http://127.0.0.1:{PORT}")

    try:

        with make_server(HOST, PORT, app) as httpd:

            httpd.serve_forever()

    except KeyboardInterrupt:

        print("\nStopping Server...")



