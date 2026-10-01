from assessments.models import Assessment, AssessmentQuestion, AssessmentOption

ASSESSMENT_ID = 32

QUESTIONS = {
1266: (
"तुमच्या बँकेतून बोलत असल्याचे सांगून कोणी संशयास्पद व्यवहार थांबवण्यासाठी तुमचा OTP मागितला, तर तुम्ही काय करावे?",
"कोई व्यक्ति बैंक से बोलने का दावा करके संदिग्ध लेन-देन रोकने के लिए आपका OTP मांगे, तो आपको क्या करना चाहिए?"
),
1267: (
"तुम्हाला QR कोड पाठवून पैसे प्राप्त करण्यासाठी तो स्कॅन करून UPI PIN टाकण्यास सांगितले जाते. सर्वात सुरक्षित कृती कोणती?",
"आपको QR कोड भेजकर पैसे प्राप्त करने के लिए उसे स्कैन करके UPI PIN डालने को कहा जाता है। सबसे सुरक्षित प्रतिक्रिया क्या है?"
),
1268: (
"तुमच्या बँकेचे KYC आज संपणार असल्याचा संदेश येतो आणि तातडीच्या पडताळणीसाठी लिंक दिली जाते. तुम्ही काय करावे?",
"आपको संदेश मिलता है कि आपके बैंक का KYC आज समाप्त हो जाएगा और तुरंत सत्यापन के लिए लिंक दिया गया है। आपको क्या करना चाहिए?"
),
1269: (
"कस्टमर सपोर्टमधून बोलत असल्याचे सांगणारी व्यक्ती तुम्हाला screen-sharing app install करण्यास सांगते. तुम्ही काय करावे?",
"कस्टमर सपोर्ट से बोलने का दावा करने वाला व्यक्ति आपको screen-sharing app install करने को कहता है। आपको क्या करना चाहिए?"
),
1270: (
"तुम्हाला मोठे बक्षीस मिळाल्याचे सांगणारी अनपेक्षित लिंक येते. सर्वात सुरक्षित कृती कोणती?",
"आपको अचानक एक लिंक मिलता है जिसमें कहा जाता है कि आपने बड़ा पुरस्कार जीता है। सबसे सुरक्षित कदम क्या है?"
),
1271: (
"अनोळखी कॉल करणाऱ्या व्यक्तीसोबत कोणती माहिती कधीही शेअर करू नये?",
"किसी अनजान कॉल करने वाले व्यक्ति के साथ कौन-सी जानकारी कभी साझा नहीं करनी चाहिए?"
),
1272: (
"पोलीस अधिकारी असल्याचे सांगणारी व्यक्ती तुम्ही 'digital arrest' मध्ये आहात असे सांगून त्वरित पैसे ट्रान्सफर करण्यास सांगते. तुम्ही काय करावे?",
"पुलिस अधिकारी होने का दावा करने वाला व्यक्ति कहता है कि आप 'digital arrest' में हैं और तुरंत पैसे ट्रांसफर करें। आपको क्या करना चाहिए?"
),
1273: (
"तुमच्याकडून चुकून संशयित फसवणूक करणाऱ्याला पैसे पाठवले गेले. सर्वप्रथम काय करावे?",
"आपने गलती से किसी संदिग्ध ठग को पैसे भेज दिए। सबसे पहले क्या करना चाहिए?"
),
1274: (
"Phishing म्हणजे काय?",
"Phishing क्या है?"
),
1275: (
"मजबूत password वापरण्याची चांगली पद्धत कोणती?",
"मजबूत password के लिए अच्छी आदत कौन-सी है?"
),
1276: (
"WhatsApp वरून बँकेकडून आल्याचे सांगणारी अनपेक्षित APK/app file मिळाल्यास काय करावे?",
"WhatsApp पर बैंक से आई बताई जाने वाली अनजान APK/app file मिले तो आपको क्या करना चाहिए?"
),
1277: (
"एखादी job offer interview होण्यापूर्वी registration fee मागत असेल, तर सर्वात सुरक्षित पद्धत कोणती?",
"यदि कोई job offer interview से पहले registration fee मांगता है, तो सबसे सुरक्षित तरीका क्या है?"
),
1278: (
"Social media वर कोणी तुमच्या मित्राचे रूप घेऊन तातडीने पैसे मागत असेल तर काय करावे?",
"Social media पर कोई आपके मित्र की नकल करके तुरंत पैसे मांगता है, तो आपको क्या करना चाहिए?"
),
1279: (
"Website वर login credentials टाकण्यापूर्वी काय तपासावे?",
"Website पर login credentials डालने से पहले आपको क्या जांचना चाहिए?"
),
1280: (
"कॉल करणाऱ्या व्यक्तीला तुमचे नाव आणि काही account details माहीत आहेत. त्यामुळे ती व्यक्ती खरी असल्याचे सिद्ध होते का?",
"कॉल करने वाले व्यक्ति को आपका नाम और कुछ account details पता हैं। क्या इससे साबित होता है कि वह व्यक्ति असली है?"
),
1281: (
"तुमच्या UPI app मध्ये संशयास्पद payment request दिसल्यास काय करावे?",
"आपके UPI app में संदिग्ध payment request दिखाई दे तो आपको क्या करना चाहिए?"
),
1282: (
"एखादी अनोळखी व्यक्ती कोणताही धोका नसताना हमखास खूप जास्त investment return देण्याचे आश्वासन देते. तुम्ही काय करावे?",
"कोई अनजान व्यक्ति बिना किसी जोखिम के बहुत अधिक guaranteed investment return का वादा करे, तो आपको क्या करना चाहिए?"
),
1283: (
"Two-factor authentication उपयोगी का आहे?",
"Two-factor authentication उपयोगी क्यों है?"
),
1284: (
"Banking apps असलेला तुमचा फोन हरवला तर तातडीने कोणती योग्य कृती करावी?",
"यदि banking apps वाला आपका फोन खो जाए, तो तुरंत कौन-सा उचित कदम उठाना चाहिए?"
),
1285: (
"SMS मधून आलेली लिंक तुमच्या बँकेच्या website सारखीच दिसते. तुम्ही काय करावे?",
"SMS से मिला लिंक आपके बैंक की website जैसा दिखाई देता है। आपको क्या करना चाहिए?"
),
1286: (
"Public किंवा shared computer वापरताना कोणती पद्धत सर्वात सुरक्षित आहे?",
"Public या shared computer का उपयोग करते समय कौन-सा व्यवहार सबसे सुरक्षित है?"
),
1287: (
"Cyber fraud झाल्यानंतर पुराव्यांबाबत काय करावे?",
"Cyber fraud होने के बाद सबूतों के साथ क्या करना चाहिए?"
),
1288: (
"भारतामध्ये आर्थिक cyber fraud नोंदवण्यासाठी National Cyber Crime Helpline नंबर कोणता आहे?",
"भारत में financial cyber fraud की रिपोर्ट करने के लिए National Cyber Crime Helpline नंबर क्या है?"
),
1289: (
"भारतामध्ये cybercrime ची online तक्रार कुठे करता येते?",
"भारत में cybercrime की online रिपोर्ट कहां की जा सकती है?"
),
1290: (
"अनेक cyber fraud प्रयत्नांपासून सर्वोत्तम संरक्षण देणारी विचारसरणी कोणती?",
"कई cyber fraud प्रयासों से सबसे अच्छी सुरक्षा देने वाली सोच कौन-सी है?"
),
}

OPTIONS = {
5157:("OTP लगेच शेअर करा","OTP तुरंत साझा करें"),
5158:("OTP चा फक्त अर्धा भाग शेअर करा","OTP का केवल आधा हिस्सा साझा करें"),
5159:("OTP शेअर करू नका आणि अधिकृत माध्यमातून बँकेशी संपर्क साधा","OTP साझा न करें और बैंक के आधिकारिक माध्यम से संपर्क करें"),
5160:("OTP SMS ने पाठवा","OTP को SMS से भेजें"),

5161:("QR कोड नेहमी सुरक्षित असतात म्हणून स्कॅन करा","QR कोड हमेशा सुरक्षित होते हैं, इसलिए स्कैन करें"),
5162:("पैसे मिळवण्यासाठी UPI PIN आवश्यक आहे म्हणून तो टाका","पैसे प्राप्त करने के लिए UPI PIN जरूरी है, इसलिए उसे डालें"),
5163:("पुढे जाऊ नका; पैसे प्राप्त करण्यासाठी सामान्यतः UPI PIN टाकण्याची गरज नसते","आगे न बढ़ें; पैसे प्राप्त करने के लिए सामान्यतः UPI PIN डालने की जरूरत नहीं होती"),
5164:("QR कोड आधी मित्रांना फॉरवर्ड करा","QR कोड पहले दोस्तों को फॉरवर्ड करें"),

5165:("लिंक लगेच उघडा","लिंक तुरंत खोलें"),
5166:("त्या पेजवर banking password टाका","उस पेज पर banking password डालें"),
5167:("बँकेच्या अधिकृत app, website किंवा customer-care माध्यमातून विनंती पडताळा","बैंक के आधिकारिक app, website या customer-care माध्यम से अनुरोध की पुष्टि करें"),
5168:("संदेश कुटुंबाला फॉरवर्ड करा","संदेश परिवार को फॉरवर्ड करें"),

5169:("App install करून पूर्ण access द्या","App install करके पूरा access दें"),
5170:("फक्त पाच मिनिटांसाठी app install करा","App केवल पांच मिनट के लिए install करें"),
5171:("App install करू नका आणि कंपनीच्या अधिकृत support माध्यमातून संपर्क साधा","App install न करें और कंपनी के आधिकारिक support माध्यम से संपर्क करें"),
5172:("Gallery लपवून screen share करा","Gallery छिपाकर screen share करें"),

5173:("लगेच क्लिक करा","तुरंत क्लिक करें"),
5174:("बक्षीस मिळवण्यासाठी bank details टाका","पुरस्कार पाने के लिए bank details डालें"),
5175:("क्लिक करू नका; पाठवणारा आणि ऑफर स्वतंत्रपणे पडताळा","क्लिक न करें; भेजने वाले और ऑफर की स्वतंत्र रूप से पुष्टि करें"),
5176:("आधी group मध्ये शेअर करा","पहले group में साझा करें"),

5177:("तुमचा आवडता रंग","आपका पसंदीदा रंग"),
5178:("OTP, PIN, password किंवा CVV","OTP, PIN, password या CVV"),
5179:("तुमच्या शहराचे नाव","आपके शहर का नाम"),
5180:("तुमची पसंतीची भाषा","आपकी पसंदीदा भाषा"),

5181:("पैसे त्वरित ट्रान्सफर करा","पैसे तुरंत ट्रांसफर करें"),
5182:("ते परवानगी देईपर्यंत video call वर रहा","जब तक वे अनुमति न दें video call पर रहें"),
5183:("पैसे ट्रान्सफर करू नका; अधिकृत यंत्रणेशी स्वतंत्रपणे संपर्क करून संशयास्पद प्रकाराची तक्रार करा","पैसे ट्रांसफर न करें; वैध अधिकारियों से स्वतंत्र रूप से संपर्क करके संदिग्ध गतिविधि की रिपोर्ट करें"),
5184:("तुमचा banking password द्या","अपना banking password दें"),

5185:("उद्यापर्यंत थांबा","कल तक इंतजार करें"),
5186:("सर्व messages delete करा","सभी messages delete करें"),
5187:("तात्काळ bank/payment provider शी संपर्क करा आणि 1930 किंवा National Cyber Crime Reporting Portal वर आर्थिक cyber fraud नोंदवा","तुरंत bank/payment provider से संपर्क करें और 1930 या National Cyber Crime Reporting Portal पर financial cyber fraud की रिपोर्ट करें"),
5188:("फक्त social media वर post करा","केवल social media पर post करें"),

5189:("फोन charge करण्याची पद्धत","फोन charge करने की विधि"),
5190:("लोकांकडून माहिती मिळवण्यासाठी किंवा malicious links उघडायला लावण्यासाठी केलेला फसवा प्रयत्न","लोगों से जानकारी निकलवाने या malicious links खुलवाने का धोखाधड़ी वाला प्रयास"),
5191:("Computer monitor चा एक प्रकार","Computer monitor का एक प्रकार"),
5192:("Banking reward programme","Banking reward programme"),

5193:("सगळीकडे एकच password वापरा","हर जगह एक ही password इस्तेमाल करें"),
5194:("Mobile number ला password म्हणून वापरा","अपने mobile number को password बनाएं"),
5195:("महत्त्वाच्या accounts साठी मजबूत आणि वेगळा password वापरा","महत्वपूर्ण accounts के लिए मजबूत और अलग password इस्तेमाल करें"),
5196:("जवळच्या मित्रांसोबत passwords शेअर करा","करीबी दोस्तों के साथ passwords साझा करें"),

5197:("लगेच install करा","तुरंत install करें"),
5198:("मित्राला forward केल्यानंतर install करा","दोस्त को forward करने के बाद install करें"),
5199:("Install करू नका; बँकेचे अधिकृत app/source वापरा","Install न करें; बैंक का आधिकारिक app/source इस्तेमाल करें"),
5200:("Phone security बंद करून install करा","Phone security बंद करके install करें"),

5201:("Job reserve करण्यासाठी लगेच पैसे भरा","Job reserve करने के लिए तुरंत भुगतान करें"),
5202:("पैसे देण्यापूर्वी किंवा संवेदनशील माहिती शेअर करण्यापूर्वी employer ची स्वतंत्रपणे पडताळणी करा","भुगतान करने या संवेदनशील जानकारी साझा करने से पहले employer की स्वतंत्र रूप से पुष्टि करें"),
5203:("तुमचा banking PIN पाठवा","अपना banking PIN भेजें"),
5204:("पैसे उधार घेऊन त्वरित भरा","पैसे उधार लेकर तुरंत भुगतान करें"),

5205:("पैसे त्वरित पाठवा","पैसे तुरंत भेजें"),
5206:("दुसऱ्या विश्वासार्ह संपर्क पद्धतीने मित्राशी पडताळणी करा","किसी दूसरे भरोसेमंद संपर्क माध्यम से अपने मित्र से पुष्टि करें"),
5207:("त्याऐवजी OTP पाठवा","इसके बजाय OTP भेजें"),
5208:("मित्राचे पुढील सर्व messages दुर्लक्षित करा","मित्र के भविष्य के सभी messages नजरअंदाज करें"),

5209:("फक्त website चा रंग","केवल website का रंग"),
5210:("Address/domain आणि तुम्ही खऱ्या अधिकृत service वर आहात का ते तपासा","Address/domain और यह जांचें कि आप वास्तविक आधिकारिक service पर पहुंचे हैं"),
5211:("त्यावर किती advertisements आहेत","उस पर कितने advertisements हैं"),
5212:("त्यावर मोठा logo आहे का","क्या उस पर बड़ा logo है"),

5213:("हो, नेहमी","हां, हमेशा"),
5214:("हो, जर ते professional वाटत असतील","हां, यदि वे professional लगें"),
5215:("नाही; वैयक्तिक माहिती data leaks किंवा इतर स्रोतांमधून मिळू शकते","नहीं; व्यक्तिगत जानकारी data leaks या अन्य स्रोतों से मिल सकती है"),
5216:("हो, जर त्यांनी दोनदा call केला","हां, यदि उन्होंने दो बार call किया"),

5217:("काय होते ते पाहण्यासाठी approve करा","क्या होता है देखने के लिए approve करें"),
5218:("तुमचा PIN टाका","अपना PIN डालें"),
5219:("Request decline करा आणि गरज असल्यास स्वतंत्रपणे पडताळणी करा","Request decline करें और जरूरत हो तो स्वतंत्र रूप से पुष्टि करें"),
5220:("Approve करा आणि नंतर refund मागा","Approve करें और बाद में refund मांगें"),

5221:("लगेच invest करा","तुरंत invest करें"),
5222:("Offer सर्वांना शेअर करा","Offer सभी के साथ साझा करें"),
5223:("सावध रहा आणि कोणतीही कृती करण्यापूर्वी entity व दाव्यांची पडताळणी करा","सावधानी बरतें और कोई कदम उठाने से पहले entity और दावों की पुष्टि करें"),
5224:("Banking app चा remote access द्या","Banking app का remote access दें"),

5225:("Screen अधिक bright होते","Screen अधिक bright होती है"),
5226:("Account protection चा अतिरिक्त स्तर मिळतो","Account protection की एक अतिरिक्त परत मिलती है"),
5227:("Passwords आपोआप share होतात","Passwords अपने आप share होते हैं"),
5228:("Security ची गरज संपते","Security की जरूरत समाप्त हो जाती है"),

5229:("काही दिवस काहीही करू नका","कई दिनों तक कुछ न करें"),
5230:("संबंधित accounts/SIM सुरक्षित करण्यासाठी त्वरित कृती करा आणि योग्य service providers शी संपर्क साधा","संबंधित accounts/SIM को सुरक्षित करने के लिए तुरंत कार्रवाई करें और उचित service providers से संपर्क करें"),
5231:("Banking password online post करा","Banking password online post करें"),
5232:("Phone ची battery संपेपर्यंत थांबा","Phone की battery खत्म होने तक इंतजार करें"),

5233:("Logo बरोबर आहे म्हणून विश्वास ठेवा","Logo सही है इसलिए भरोसा करें"),
5234:("SMS ने आली म्हणून लिंक वापरा","SMS से आया है इसलिए लिंक इस्तेमाल करें"),
5235:("त्याऐवजी बँकेचे अधिकृत app उघडा किंवा अधिकृत website address स्वतः टाका","इसके बजाय बैंक का आधिकारिक app खोलें या आधिकारिक website address स्वयं डालें"),
5236:("फक्त PIN टाका","केवल PIN डालें"),

5237:("Browser मध्ये banking passwords save करा","Browser में banking passwords save करें"),
5238:("Account logged in ठेवून द्या","Account logged in छोड़ दें"),
5239:("शक्य असल्यास संवेदनशील transactions टाळा आणि नेहमी sign out करा","जहां संभव हो संवेदनशील transactions से बचें और हमेशा sign out करें"),
5240:("Computer owner सोबत password शेअर करा","Computer owner के साथ password साझा करें"),

5241:("सर्व messages लगेच delete करा","सभी messages तुरंत delete करें"),
5242:("Reporting साठी transaction details, messages, screenshots आणि इतर संबंधित पुरावे जतन करा","Reporting के लिए transaction details, messages, screenshots और अन्य संबंधित सबूत सुरक्षित रखें"),
5243:("Report करण्यापूर्वी प्रत्येक device factory-reset करा","Report करने से पहले हर device factory-reset करें"),
5244:("फक्त मित्रांना सांगा","केवल दोस्तों को बताएं"),

5245:("100","100"),
5246:("108","108"),
5247:("1930","1930"),
5248:("101","101"),

5249:("फक्त social media वर","केवल social media पर"),
5250:("National Cyber Crime Reporting Portal","National Cyber Crime Reporting Portal"),
5251:("कोणत्याही random forum वर","किसी random forum पर"),
5252:("फक्त मित्रांना email करून","केवल दोस्तों को email करके"),

5253:("Message मध्ये urgency दिसली की लगेच कृती करा","Message में urgency दिखे तो तुरंत कार्रवाई करें"),
5254:("तुमचे नाव माहीत असलेल्या प्रत्येकावर विश्वास ठेवा","हर उस व्यक्ति पर भरोसा करें जिसे आपका नाम पता है"),
5255:("थांबा, स्वतंत्रपणे पडताळणी करा आणि संवेदनशील credentials कधीही उघड करू नका","रुकें, स्वतंत्र रूप से पुष्टि करें और संवेदनशील credentials कभी साझा न करें"),
5256:("Call करणाऱ्यांनी सुचवलेले प्रत्येक app install करा","Call करने वालों द्वारा सुझाया गया हर app install करें"),
}

assessment = Assessment.objects.get(id=ASSESSMENT_ID)

questions = {
    q.id: q
    for q in assessment.questions.filter(
        id__in=QUESTIONS.keys()
    )
}

if len(questions) != 25:
    raise RuntimeError(
        f"Expected 25 Cyber questions, found {len(questions)}"
    )

valid_option_ids = set(
    AssessmentOption.objects.filter(
        question__assessment=assessment,
        id__in=OPTIONS.keys()
    ).values_list("id", flat=True)
)

if len(valid_option_ids) != 100:
    raise RuntimeError(
        f"Expected 100 Cyber options, found {len(valid_option_ids)}"
    )

for qid, (mr, hi) in QUESTIONS.items():
    AssessmentQuestion.objects.filter(
        id=qid,
        assessment=assessment
    ).update(
        question_text_mr=mr,
        question_text_hi=hi
    )

for oid, (mr, hi) in OPTIONS.items():
    AssessmentOption.objects.filter(
        id=oid,
        question__assessment=assessment
    ).update(
        option_text_mr=mr,
        option_text_hi=hi
    )

qs = list(
    assessment.questions.filter(is_active=True)
    .prefetch_related("options")
    .order_by("order", "id")
)
opts = [o for q in qs for o in q.options.all()]

mq = sum(bool((q.question_text_mr or "").strip()) for q in qs)
hq = sum(bool((q.question_text_hi or "").strip()) for q in qs)
mo = sum(bool((o.option_text_mr or "").strip()) for o in opts)
ho = sum(bool((o.option_text_hi or "").strip()) for o in opts)

print("========================================")
print("CYBER MULTILINGUAL SEED COMPLETE")
print("========================================")
print("Assessment:", assessment.title)
print("Questions:", len(qs))
print("Marathi questions:", f"{mq}/{len(qs)}")
print("Hindi questions:", f"{hq}/{len(qs)}")
print("Options:", len(opts))
print("Marathi options:", f"{mo}/{len(opts)}")
print("Hindi options:", f"{ho}/{len(opts)}")

if not (
    len(qs) == 25 and
    mq == 25 and hq == 25 and
    len(opts) == 100 and
    mo == 100 and ho == 100
):
    raise RuntimeError("CYBER TRANSLATION AUDIT FAILED")

print("AUDIT: PASS")
