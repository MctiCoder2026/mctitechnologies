from assessments.models import Assessment, AssessmentQuestion, AssessmentOption

SLUG = "ai-ready-maharashtra-2026-marathi"

assessment, created = Assessment.objects.get_or_create(
    slug=SLUG,
    defaults={
        "title": "MCTI AI Ready Maharashtra – AI Awareness Quiz 2026 (Marathi)",
        "assessment_type": "awareness",
        "is_active": True,
    }
)

assessment.title = "MCTI AI Ready Maharashtra – AI Awareness Quiz 2026 (Marathi)"
assessment.assessment_type = "awareness"
assessment.is_active = True
assessment.save()

QUESTIONS = [
    (
        "कृत्रिम बुद्धिमत्ता (Artificial Intelligence / AI) म्हणजे काय?",
        ["मानवी बुद्धिमत्तेसारखी कामे करू शकणारे संगणकीय तंत्रज्ञान",
         "फक्त इंटरनेटचा वेग वाढवणारे तंत्रज्ञान",
         "फक्त संगणक दुरुस्त करण्याची पद्धत",
         "फक्त मोबाईल नेटवर्कची सेवा"],
        0, "AI Basics"
    ),
    (
        "खालीलपैकी AI चा सामान्य वापर कोणता आहे?",
        ["Voice Assistant", "साधा इलेक्ट्रिक स्विच", "पेन ड्राइव्ह", "USB केबल"],
        0, "AI Awareness"
    ),
    (
        "ChatGPT सारखे AI साधन मुख्यतः कशासाठी वापरले जाऊ शकते?",
        ["माहिती समजून घेणे, कल्पना तयार करणे आणि मजकूरावर मदत घेणे",
         "फक्त फोन चार्ज करणे",
         "फक्त इंटरनेट बंद करणे",
         "फक्त फाइल delete करणे"],
        0, "Generative AI"
    ),
    (
        "Generative AI म्हणजे काय?",
        ["नवीन मजकूर, चित्र किंवा इतर content तयार करू शकणारी AI",
         "फक्त calculator",
         "फक्त antivirus",
         "फक्त operating system"],
        0, "Generative AI"
    ),
    (
        "AI ला दिलेल्या सूचनेला सामान्यतः काय म्हणतात?",
        ["Prompt", "Folder", "Password", "Browser"],
        0, "Prompting"
    ),
    (
        "चांगला AI Prompt कसा असावा?",
        ["स्पष्ट आणि आवश्यक संदर्भासह",
         "नेहमी फक्त एक शब्दाचा",
         "पूर्णपणे अस्पष्ट",
         "फक्त मोठ्या अक्षरात"],
        0, "Prompting"
    ),
    (
        "विद्यार्थी AI चा योग्य वापर कसा करू शकतो?",
        ["विषय समजून घेण्यासाठी आणि सरावासाठी",
         "विचार न करता प्रत्येक उत्तर copy करण्यासाठी",
         "परीक्षेत गैरप्रकार करण्यासाठी",
         "फक्त social media साठी"],
        0, "Education"
    ),
    (
        "AI ने दिलेली माहिती वापरण्यापूर्वी काय करणे योग्य आहे?",
        ["महत्त्वाची माहिती विश्वासार्ह स्रोतांमधून तपासणे",
         "नेहमी 100% बरोबर मानणे",
         "कधीही वाचू नये",
         "ताबडतोब सर्वांना forward करणे"],
        0, "Responsible AI"
    ),
    (
        "AI कधी चुकीची किंवा बनावट माहिती देऊ शकते का?",
        ["होय", "नाही, कधीच नाही", "फक्त रविवारी", "फक्त मोबाईलवर"],
        0, "Responsible AI"
    ),
    (
        "AI वापरताना कोणती माहिती share करणे टाळावे?",
        ["Password आणि संवेदनशील वैयक्तिक माहिती",
         "सामान्य अभ्यासाचा प्रश्न",
         "सार्वजनिक विषयाचे नाव",
         "सामान्य कल्पना"],
        0, "AI Safety"
    ),
    (
        "Machine Learning म्हणजे काय?",
        ["डेटामधील patterns वापरून प्रणालीला शिकण्यास मदत करणारी AI पद्धत",
         "फक्त typing शिकण्याची पद्धत",
         "computer assembling",
         "printer repair"],
        0, "Machine Learning"
    ),
    (
        "AI प्रणालींसाठी Data का महत्त्वाचा असतो?",
        ["AI models patterns शिकण्यासाठी data वापरू शकतात",
         "Data मुळे monitor मोठा होतो",
         "Data फक्त keyboard साठी असतो",
         "AI ला data ची गरजच नसते"],
        0, "Data Literacy"
    ),
    (
        "खालीलपैकी Computer Vision चे उदाहरण कोणते?",
        ["चित्रातील वस्तू ओळखणे",
         "फोन चार्ज करणे",
         "keyboard साफ करणे",
         "speaker चा आवाज वाढवणे"],
        0, "Computer Vision"
    ),
    (
        "Speech Recognition म्हणजे काय?",
        ["बोललेले शब्द संगणकाद्वारे ओळखणे",
         "फोटो print करणे",
         "battery बदलणे",
         "Wi-Fi cable जोडणे"],
        0, "AI Applications"
    ),
    (
        "Recommendation system चे उदाहरण कोणते?",
        ["तुमच्या आवडीनुसार video किंवा product सुचवणे",
         "calculator मध्ये बेरीज करणे",
         "computer बंद करणे",
         "file rename करणे"],
        0, "AI Applications"
    ),
    (
        "AI मुळे भविष्यातील नोकऱ्यांमध्ये कोणते कौशल्य अधिक उपयुक्त ठरू शकते?",
        ["AI tools समजून त्यांचा जबाबदारीने वापर करण्याचे कौशल्य",
         "फक्त mouse click करणे",
         "फक्त file copy करणे",
         "technology पूर्णपणे टाळणे"],
        0, "Future Skills"
    ),
    (
        "AI चा वापर Resume तयार करण्यात होऊ शकतो का?",
        ["होय, draft आणि सुधारणा करण्यासाठी",
         "नाही, कोणत्याही परिस्थितीत नाही",
         "फक्त printer असल्यास",
         "फक्त gaming साठी"],
        0, "Career"
    ),
    (
        "AI चा वापर Coding शिकताना कसा होऊ शकतो?",
        ["Code समजावून घेणे आणि errors समजण्यास मदत घेणे",
         "फक्त computer बंद करणे",
         "फक्त wallpaper बदलणे",
         "फक्त password तयार करणे"],
        0, "Coding & AI"
    ),
    (
        "AI वापरताना Critical Thinking का आवश्यक आहे?",
        ["AI चे उत्तर योग्य, संबंधित आणि विश्वासार्ह आहे का हे तपासण्यासाठी",
         "AI पेक्षा वेगाने typing करण्यासाठी",
         "screen brightness वाढवण्यासाठी",
         "internet बंद करण्यासाठी"],
        0, "Critical Thinking"
    ),
    (
        "Deepfake म्हणजे काय?",
        ["AI वापरून तयार किंवा बदललेले वास्तवासारखे दिसणारे बनावट media",
         "नवीन hard disk",
         "computer game",
         "email folder"],
        0, "Digital Safety"
    ),
    (
        "AI तयार केलेला फोटो किंवा video पाहताना काय करणे योग्य आहे?",
        ["संशयास्पद content ची सत्यता तपासणे",
         "नेहमी खरे मानणे",
         "ताबडतोब forward करणे",
         "source कधीही पाहू नये"],
        0, "Digital Safety"
    ),
    (
        "AI Bias म्हणजे काय?",
        ["AI च्या output मध्ये काही गटांविषयी अन्यायकारक किंवा पक्षपाती pattern दिसणे",
         "computer चा आवाज",
         "internet speed",
         "keyboard setting"],
        0, "Responsible AI"
    ),
    (
        "AI मानवाची प्रत्येक गोष्टीत पूर्णपणे जागा घेईल असे निश्चितपणे म्हणता येते का?",
        ["नाही, AI अनेक कामांत सहाय्यक साधन म्हणून वापरले जाते आणि परिणाम क्षेत्रानुसार बदलतात",
         "होय, प्रत्येक नोकरी लगेच संपेल",
         "AI फक्त विद्यार्थ्यांची जागा घेते",
         "AI फक्त शिक्षकांची जागा घेते"],
        0, "Future of Work"
    ),
    (
        "AI Ready विद्यार्थी होण्यासाठी सर्वात योग्य दृष्टिकोन कोणता?",
        ["AI समजून घेणे, प्रत्यक्ष वापर करणे आणि जबाबदारीने पडताळणी करणे",
         "AI ची भीती बाळगून कधीही वापरू नये",
         "AI चे प्रत्येक उत्तर विचार न करता मान्य करणे",
         "फक्त AI बद्दल video पाहणे"],
        0, "AI Readiness"
    ),
    (
        "AI शिकण्याची सुरुवात करण्यासाठी विद्यार्थ्याने काय करावे?",
        ["मूलभूत संकल्पना समजून सुरक्षितपणे AI tools वर सराव करावा",
         "सर्वात आधी महाग computer घ्यावा",
         "Programming येईपर्यंत AI वापरू नये",
         "AI फक्त engineers साठी आहे असे मानावे"],
        0, "AI Readiness"
    ),
]

# Repeat-safe: this dedicated assessment is controlled by this script.
# Existing English assessment is never touched.
existing = {q.order: q for q in assessment.questions.all()}

for order, (text, options, correct, category) in enumerate(QUESTIONS, start=1):
    q = existing.get(order)

    if q is None:
        q = AssessmentQuestion.objects.create(
            assessment=assessment,
            question_text=text,
            category=category,
            order=order,
            marks=1,
            is_active=True,
            question_origin="mcti_practice",
            source_name="MCTI Technologies",
            source_reference="AI Ready Maharashtra 2026 – Marathi Awareness Practice",
        )
    else:
        q.question_text = text
        q.category = category
        q.marks = 1
        q.is_active = True
        q.question_origin = "mcti_practice"
        q.source_name = "MCTI Technologies"
        q.source_reference = "AI Ready Maharashtra 2026 – Marathi Awareness Practice"
        q.save()

    q.options.all().delete()

    for option_order, option_text in enumerate(options, start=1):
        AssessmentOption.objects.create(
            question=q,
            option_text=option_text,
            is_correct=(option_order - 1 == correct),
            order=option_order,
        )

# Deactivate accidental extra questions only inside Marathi assessment.
assessment.questions.filter(order__gt=25).update(is_active=False)

print("ASSESSMENT:", assessment.id, assessment.slug)
print("ACTIVE QUESTIONS:", assessment.questions.filter(is_active=True).count())
print("OPTIONS:", AssessmentOption.objects.filter(
    question__assessment=assessment,
    question__is_active=True
).count())
