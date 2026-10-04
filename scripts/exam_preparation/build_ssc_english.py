from assessments.models import Assessment, AssessmentQuestion, AssessmentOption

SLUG = "ssc-english-first-language-practice"

assessment, _ = Assessment.objects.update_or_create(
    slug=SLUG,
    defaults={
        "title": "SSC English First Language – Board Practice",
        "assessment_type": "exam_preparation",
        "description": (
            "SSC English First Language practice based on 2024, 2025 "
            "and 2026 Board activity sheets."
        ),
        "total_questions": 25,
        "passing_score": 0,
        "duration_minutes": 25,
        "is_active": True,
        "certificate_enabled": False,
        "lead_capture_enabled": False,
    },
)

SOURCES = {
    2024: ("SSC English First Language Board Paper", "2024 III 07 1100 / N 580"),
    2025: ("SSC English First Language Board Paper", "2025 III 01 1100 / N 815"),
    2026: ("SSC English First Language Board Paper", "2026 II 27 1100 / N 915"),
}

# question, options, correct index, category, year
# Adapted MCQ practice from the uploaded activity sheets.
QUESTIONS = [

# ======================== 2024 ========================

(
'Pick out the infinitive in: "Every child is free to grow."',
["to grow","is","free","child"],
0,"Language Study",2024
),
(
'Which punctuation is correct?',
["Dr. Kalam sat contemplating deeply.","Dr Kalam sat contemplating deeply","dr. kalam sat contemplating deeply","Dr Kalam, sat contemplating deeply."],
0,"Language Study",2024
),
(
'In "He gave the reward to none", which is the finite verb?',
["gave","to","reward","none"],
0,"Language Study",2024
),
(
'Which word is a homophone of "ware"?',
["wear","where","were","war"],
0,"Vocabulary",2024
),
(
'Which transformation correctly uses "as soon as" for: "No sooner is the bill passed than it will become an act"?',
["As soon as the bill is passed, it will become an act.","As soon the bill passed it becomes an act.","The bill as soon will become an act.","As soon as an act, the bill passes."],
0,"Language Study",2024
),
(
'Who started Apple with Steve Jobs according to the passage?',
["Steve Wozniak","Bill Gates","John Sculley","Edwin Land"],
0,"Textual Passage",2024
),
(
'At what age did Steve Jobs start Apple with Woz?',
["20","18","25","30"],
0,"Textual Passage",2024
),
(
'Which company is described as the world’s most successful animation studio in the passage?',
["Pixar","Next","Apple","Microsoft"],
0,"Textual Passage",2024
),
(
'Who became Steve Jobs’ wife according to the passage?',
["Laurene","Smita","Joan","Anita"],
0,"Textual Passage",2024
),
(
'What advice is given near the end of Steve Jobs’ passage?',
["Keep looking and do not settle.","Avoid creative work.","Success requires no failure.","Never start over."],
0,"Textual Passage",2024
),
(
'Pandit Ravi Shankar is identified in the passage as a ______ maestro.',
["sitar","tabla","flute","sarod"],
0,"Textual Passage",2024
),
(
'What was the name of Smita’s brother?',
["Anant","Anil","Woz","Robert"],
0,"Textual Passage",2024
),
(
'What instrument were Smita and Anant learning?',
["Sitar","Tabla","Violin","Piano"],
0,"Textual Passage",2024
),
(
'According to the passage, Anant was suffering from ______.',
["cancer","malaria","asthma","diabetes"],
0,"Textual Passage",2024
),
(
'Anant was especially good at which school sport?',
["Table-tennis","Cricket","Football","Chess"],
0,"Textual Passage",2024
),
(
'In "All the world’s a stage", which figure of speech is used?',
["Metaphor","Simile","Personification","Alliteration"],
0,"Poetry",2024
),
(
'In "All the World’s a Stage", how many ages of man are mentioned?',
["Seven","Five","Six","Eight"],
0,"Poetry",2024
),
(
'Which stage is described as "creeping like snail"?',
["Schoolboy","Soldier","Justice","Lover"],
0,"Poetry",2024
),
(
'Which stage is described as "full of strange oaths"?',
["Soldier","Infant","Justice","Schoolboy"],
0,"Poetry",2024
),
(
'Which stage is described as "sighing like furnace"?',
["Lover","Soldier","Justice","Infant"],
0,"Poetry",2024
),

# ======================== 2025 ========================

(
'Pick out the infinitive in: "He was asking to go for the concert."',
["to go","asking","was","concert"],
0,"Language Study",2025
),
(
'What type of sentence is: "Get out and wait in the yard."?',
["Imperative","Interrogative","Exclamatory","Assertive"],
0,"Language Study",2025
),
(
'Which is the correct alphabetical order?',
["indisputable, inequality, interactions, inventions","inequality, indisputable, inventions, interactions","interactions, inventions, inequality, indisputable","inventions, interactions, indisputable, inequality"],
0,"Language Study",2025
),
(
'Which is the correctly punctuated form?',
["Can you cook?","can you cook.","Can you cook.","can You cook?"],
0,"Language Study",2025
),
(
'Past Perfect Continuous form of "I am doing my bit" is:',
["I had been doing my bit.","I have done my bit.","I was doing my bit.","I had done my bit."],
0,"Language Study",2025
),
(
'Machu Picchu is located in ______.',
["Peru","Australia","Austria","The U.S."],
0,"Textual Passage",2025
),
(
'Sydney Opera House is located in ______.',
["Australia","Austria","Peru","The U.S."],
0,"Textual Passage",2025
),
(
'Yellowstone National Park is located in ______.',
["The U.S.","Peru","Australia","Austria"],
0,"Textual Passage",2025
),
(
'The Historic Centre of Vienna is located in ______.',
["Austria","Australia","Peru","The U.S."],
0,"Textual Passage",2025
),
(
'According to the passage, how many World Heritage Sites existed as of 2009?',
["890","689","176","148"],
0,"Textual Passage",2025
),
(
'According to the passage, which country had the highest number of World Heritage Sites?',
["Italy","India","Peru","Australia"],
0,"Textual Passage",2025
),
(
'Which is mentioned as a danger to World Heritage Sites?',
["Uncontrolled urbanization","Free education","Organic farming","Space exploration"],
0,"Textual Passage",2025
),
(
'Which word from the World Heritage activity is an adjective?',
["natural","allocate","protect","preserve"],
0,"Vocabulary",2025
),
(
'In the passage, a person who works for social change is called an ______.',
["activist","artist","scientist","merchant"],
0,"Vocabulary",2025
),
(
'Kailash Satyarthi says the empty chair is a reminder of ______.',
["children who are left behind","World Heritage Sites","his family","tourists"],
0,"Textual Passage",2025
),
(
'In "Night of the Scorpion", the narrator’s father is described as a ______.',
["sceptic and rationalist","poet and singer","doctor and scientist","farmer and merchant"],
0,"Poetry",2025
),
(
'For approximately how long did the mother suffer before the sting lost its effect?',
["Twenty hours","Two hours","Ten hours","Twenty minutes"],
0,"Poetry",2025
),
(
'At the end of "Night of the Scorpion", whom does the mother thank?',
["God","The neighbours","The doctor","The poet"],
0,"Poetry",2025
),
(
'Who wrote "Where the Mind is Without Fear"?',
["Rabindranath Tagore","William Shakespeare","Nissim Ezekiel","Berton Braley"],
0,"Poetry",2025
),
(
'In the Rangoli passage, what was traditionally used to make Rangoli?',
["Rice flour","Cement","Plastic powder","Metal dust"],
0,"Non-textual Passage",2025
),

# ======================== 2026 ========================

(
'Pick out the infinitive in: "Every child is free to grow."',
["to grow","free","is","child"],
0,"Language Study",2026
),
(
'Which meaningful word can be formed from "abogll"?',
["global","goball","ballog","logbal"],
0,"Language Study",2026
),
(
'What type of sentence is: "How frightened their eyes look!"?',
["Exclamatory","Interrogative","Imperative","Assertive"],
0,"Language Study",2026
),
(
'Future Perfect form of "I shall be telling you three stories" is:',
["I shall have told you three stories.","I shall tell you three stories.","I told you three stories.","I have been telling you three stories."],
0,"Language Study",2026
),
(
'Passive voice of "Anil was watching a wrestling match" is:',
["A wrestling match was being watched by Anil.","A wrestling match is watched by Anil.","Anil had watched a wrestling match.","A wrestling match has been watched by Anil."],
0,"Language Study",2026
),
(
'Joan is described in the passage as approximately how old?',
["17 to 18 years","10 to 12 years","25 to 30 years","40 years"],
0,"Textual Passage",2026
),
(
'What did Joan ask Robert to give her?',
["A horse, armour and some soldiers","A ship and sailors","Books and money","Food and shelter"],
0,"Textual Passage",2026
),
(
'Whom did Joan want to be sent to?',
["The Dauphin","The King of England","The Pope","The Steward"],
0,"Textual Passage",2026
),
(
'In the Joan passage, "grimly" means ______.',
["seriously","happily","carelessly","quietly"],
0,"Vocabulary",2026
),
(
'In the Joan passage, "armour" means ______.',
["protective clothing of metal worn in battle","a musical instrument","a royal building","a farming tool"],
0,"Vocabulary",2026
),
(
'In the Joan passage, "blockhead" means ______.',
["stupid person","brave soldier","wise person","royal officer"],
0,"Vocabulary",2026
),
(
'In the Joan passage, "assuming" means ______.',
["taken for granted","being frightened","speaking softly","fighting bravely"],
0,"Vocabulary",2026
),
(
'In "The Luncheon" extract, what did the narrator order for himself?',
["Coffee","Ice cream","Peach","Asparagus"],
0,"Textual Passage",2026
),
(
'What fruit did the guest take while they were waiting for coffee?',
["Peach","Apple","Orange","Mango"],
0,"Textual Passage",2026
),
(
'The word "miserable" in the luncheon passage is closest in meaning to ______.',
["unhappy","delighted","wealthy","brave"],
0,"Vocabulary",2026
),
(
'In the poem "The Pulley", which quality was left at the bottom of God’s glass of blessings?',
["Rest","Strength","Beauty","Wisdom"],
0,"Poetry",2026
),
(
'Which of these blessings is explicitly mentioned in "The Pulley"?',
["Strength","Fame","Power","Youth"],
0,"Poetry",2026
),
(
'What is the rhyme scheme option given for "The Pulley" that matches the stanza pattern?',
["a b c b c","a a b b c","a b c c b","a b a b a"],
0,"Poetry",2026
),
(
'Who is the poet of "The Will to Win"?',
["Berton Braley","Rabindranath Tagore","William Shakespeare","Nissim Ezekiel"],
0,"Poetry",2026
),
(
'According to the 2026 non-textual passage, what are stated as the main causes affecting many species?',
["Air and water pollution","Only sound pollution","Only tourism","Only snowfall"],
0,"Non-textual Passage",2026
),
]

added = 0

for text, options, correct, category, year in QUESTIONS:
    source_name, source_reference = SOURCES[year]

    q, created = AssessmentQuestion.objects.get_or_create(
        assessment=assessment,
        question_text=text,
        board_year=year,
        defaults={
            "category": category,
            "order": assessment.questions.count() + 1,
            "marks": 1,
            "is_active": True,
            "question_origin": "board_based",
            "source_name": source_name,
            "source_reference": source_reference,
        },
    )

    if created:
        for i, option in enumerate(options):
            AssessmentOption.objects.create(
                question=q,
                option_text=option,
                is_correct=(i == correct),
                order=i + 1,
            )
        added += 1

print("=" * 72)
print("SSC ENGLISH FIRST LANGUAGE – BOARD PRACTICE BANK")
print("=" * 72)
print("Assessment:", assessment.id, assessment.slug)
print("New questions:", added)
print("Total active:", assessment.questions.filter(is_active=True).count())

for year in (2024, 2025, 2026):
    print(year, assessment.questions.filter(
        is_active=True,
        board_year=year
    ).count())

print("=" * 72)
