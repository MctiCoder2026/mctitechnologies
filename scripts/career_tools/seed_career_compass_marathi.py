from career_tools.models import CareerCompassQuestion

MR = {
1: (
    "शळनतर मकळ वळ मळल तर तमहल कय करयल जसत आवडल?",
    "कमपयटर, मबईल कव नवन ततरजञन वपरन पहण",
    "पस कमवणयचय कव वयवसयचय कलपन वचरत घण",
    "चतरकल, डझइन, वहडओ कव करएटवह कम करण",
    "मतरश बलण, तयन मदत करण कव मरगदरशन करण",
),
2: (
    "भवषयतल कमबददल वचर करतन तमहल कय अधक आकरषत करत?",
    "ततरजञनसबत कम करण आण नवन डजटल गषट शकण",
    "सवतच वयवसय कव वयवसथपन करण",
    "लकश सवद सधण आण टमसबत कम करण",
    "हतन कव उपकरणसबत परतयकष कम करण",
),
3: (
    "नवन गषट शकतन तमहल कणत पदधत जसत आवडत?",
    "कमपयटरवर करन पहण",
    "तयमगच करण आण वजञन समजन घण",
    "चतर, डझइन कव वहडओचय मधयमतन शकण",
    "परतयकष करन आण सरवतन शकण",
),
4: (
    "खललपक कणत परजकट तमह आनदन करल?",
    "एक सध वबसइट कव डजटल परजकट तयर करण",
    "लहन वयवसयसठ यजन तयर करण",
    "पसटर, लग कव वहडओ तयर करण",
    "एखद करयकरम आयजत करन लकश समनवय सधण",
),
5: (
    "कणतय परकरचय गषटबददल तमहल सरवधक कतहल वटत?",
    "नवन अपस, AI आण डजटल ततरजञन",
    "वजञन, परयग आण गषट कश कम करतत",
    "वयवसय, मरकटग आण पस कस वढतत",
    "मशन, सधन आण वसत परतयकष कश चलतत",
),
6: (
    "तमचय आवडच एक कलब नवडयच झल तर तमह कणत नवडल?",
    "Coding / Technology Club",
    "Business / Entrepreneurship Club",
    "Art / Media / Design Club",
    "Communication / Social Activity Club",
),

7: (
    "शळतल कणतय परकरच वषय तमहल तलनन सप कव रचकर वटतत?",
    "गणत, लजक कव कमपयटर",
    "वजञन आण परयग",
    "भष, सवद आण सदरकरण",
    "कल, डझइन कव करएटवह वषय",
),
8: (
    "आकड आण गणन असलल कम मळल तर तमहल कय वटत?",
    "लजक वपरन सडवयल आवडल",
    "हशब आण आरथक उपयग समजन घययल आवडल",
    "डटमधल करण कव पटरन शधयल आवडल",
    "परतयकष उदहरणतन समजन घययल आवडल",
),
9: (
    "वजञनतल एखद सकलपन शकतन तमहल कय आवडत?",
    "तच ततरजञनत उपयग कस हत ह पहण",
    "परयग करन करण समजन घण",
    "चतर कव वहजयअलचय मधयमतन समजन घण",
    "मडल कव उपकरण वपरन परतयकष पहण",
),
10: (
    "भष कव सवदचय वषयत तमहल कणत कम आवडल?",
    "महत डजटल सवरपत मडण",
    "एखद कलपन लकन पटवन सगण",
    "कथ, कटट कव करएटवह लखन करण",
    "लकश बलण कव सदरकरण करण",
),
11: (
    "परजकटसठ वषय नवडयच झल तर तमह कय नवडल?",
    "Technology कव Computer",
    "Business कव Market",
    "Science कव Research",
    "Design कव Media",
),
12: (
    "शकतन तमहल कणत गषट सरवधक मदत करत?",
    "Step-by-step logical instructions",
    "Concept आण करण समजण",
    "Visual examples आण creativity",
    "Hands-on practice आण demonstration",
),

13: (
    "एखद समसय आल तर तमह सरवपरथम कय करत?",
    "त छट टपप करन logical solution शधत/शधत",
    "करण शधन महतच वशलषण करत/करत",
    "वगवगळय नवन कलपन सचवत/सचवत",
    "परतयकष करन कणत उपय चलत त पहत/पहत",
),
14: (
    "गरप परजकटमधय अडचण आल तर तमच नसरगक भमक कणत असत?",
    "Technical problem सडवण",
    "Planning आण resources manage करण",
    "नवन creative idea दण",
    "सगळयश बलन team coordinate करण",
),
15: (
    "अपरचत परशन मळलयस तमह कय करण पसत करल?",
    "Logic आण pattern वपरण",
    "Facts तपसन करण शधण",
    "नवन approach तयर करण",
    "उदहरण कव practical trial करन पहण",
),
16: (
    "एखद कम अपकषपरमण झल नह तर?",
    "System कव process मधय error शधन",
    "Result च analysis करन करण शधन",
    "वगळ creative पदधत वपरन",
    "परतयकष बदल करन पनह परयतन करन",
),
17: (
    "तमचयकड मरयदत पस आण वळ असल तर परजकट कस परण करल?",
    "यगय digital tools वपरन",
    "Budget आण priorities ठरवन",
    "कम resources मधय creative solution शधन",
    "उपलबध वसतन practical solution बनवन",
),
18: (
    "दन परययपक नरणय घययच असल तर तमह कशवर भर दत?",
    "Logic आण efficiency",
    "Facts आण evidence",
    "लकवर हणर परणम",
    "Practical usefulness",
),

19: (
    "तमहल कणतय परकर कम करयल जसत आवडत?",
    "कमपयटर आण digital tools सबत",
    "Planning, targets आण business tasks सबत",
    "Creative freedom असललय कमत",
    "लक आण team सबत",
),
20: (
    "तमहल task दल तर कणत परसथत जसत आवडल?",
    "सपषट problem आण logical solution",
    "Research करन उततर शधण",
    "सवतच कलपन वपरणयच सवततरय",
    "परतयकष वसत कव equipment सबत कम",
),
21: (
    "गरपमधय तमह सहस कणत भमक घत?",
    "Technical कम सभळण",
    "Planning कव leadership घण",
    "Presentation कव creative भग करण",
    "लकन जडन communication करण",
),
22: (
    "कम करतन तमहल कय जसत motivate करत?",
    "नवन technology शकण",
    "Result, growth आण earning potential",
    "नवन कहतर तयर करण",
    "लकन मदत करण आण appreciation मळण",
),
23: (
    "तमहल कणत कमच वतवरण जसत आवडल?",
    "Digital आण technology-focused",
    "Business आण performance-focused",
    "Research आण knowledge-focused",
    "Workshop, field कव practical environment",
),
24: (
    "एखद कम परण कलयवर तमहल सरवधक समधन कशतन मळत?",
    "System कव technology वयवसथत चललयवर",
    "Target कव business result मळलयवर",
    "सदर कव creative output तयर झलयवर",
    "एखदय वयकतल मदत झलयवर",
),

25: (
    "भवषयत कणतय परकरचय ठकण कम करणयच कलपन तमहल आवडत?",
    "IT company कव technology environment",
    "Company, office कव सवतच business",
    "Laboratory, research कव analytical environment",
    "Studio, media कव creative environment",
),
26: (
    "कमसठ कणत वतवरण तमहल जसत यगय वटत?",
    "Computer-based आण digital",
    "Targets, customers आण management",
    "Study, analysis आण research",
    "Hands-on technical कव field work",
),
27: (
    "तमहल कणतय परकरचय लकसबत कम करयल आवडल?",
    "Developers कव technology professionals",
    "Business owners, managers कव customers",
    "Scientists, analysts कव researchers",
    "Students, teams कव public-facing people",
),
28: (
    "तमचय भवषयतल कमत कय असव अस तमहल वटत?",
    "Technology आण continuous learning",
    "Growth, leadership आण business opportunities",
    "Creativity आण नवन ideas",
    "Practical skills आण visible output",
),
29: (
    "तमचयसठ ideal career मधय कय महततवच आह?",
    "Digital skills वपरणयच सध",
    "Income growth आण business responsibility",
    "Knowledge, investigation आण analysis",
    "People interaction आण positive impact",
),
30: (
    "10व नतर पढल दश explore करतन तमहल कणत परयय सरवत जवळच वटत?",
    "Computer, IT आण Digital Technology",
    "Commerce, Business आण Management",
    "Science आण Analytical Studies",
    "Skill-based, Technical कव Practical Education",
),
}

updated = 0

for order, values in MR.items():
    q = CareerCompassQuestion.objects.filter(order=order).first()

    if not q:
        print(f"Missing question order {order}")
        continue

    (
        q.question_mr,
        q.option_a_mr,
        q.option_b_mr,
        q.option_c_mr,
        q.option_d_mr,
    ) = values

    q.save(update_fields=[
        "question_mr",
        "option_a_mr",
        "option_b_mr",
        "option_c_mr",
        "option_d_mr",
    ])

    updated += 1

print("Marathi questions updated:", updated)
print(
    "Complete Marathi questions:",
    CareerCompassQuestion.objects.filter(
        is_active=True
    ).exclude(question_mr="").count()
)
