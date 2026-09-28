def q(question, correct, wrong1, wrong2, wrong3):
    return (question, [correct, wrong1, wrong2, wrong3], 0)


AUTO_BANKS_BATCH2 = {

# ============================================================
# MIA / ACCOUNTS TRAINER
# ============================================================
"hiring-mia-accounts-trainer": {
"practical": [
q("A trial balance does not agree. What should be checked first?","Ledger postings, balances and debit-credit entries systematically","Change the final total manually","Delete all vouchers","Ignore the difference"),
q("A customer payment is received against an outstanding invoice. What should be recorded correctly?","The receipt and its allocation against the appropriate customer outstanding","A purchase voucher","A stock journal only","An employee attendance entry"),
q("A GST invoice contains an incorrect tax rate. What should be done?","Verify the applicable transaction details and correct the invoice according to proper accounting and tax procedure","Change the customer name only","Ignore the tax difference","Delete all company data"),
q("An Excel accounting report total is incorrect. What should be checked first?","Source values, formulas, references and filters","Screen brightness","Worksheet colour","Printer settings"),
q("A business wants monthly expense totals by category from transaction data. What is a suitable approach?","Classify transactions correctly and summarize them using an appropriate Excel report or PivotTable","Select random expenses","Use only the first transaction","Delete category information"),
q("A Tally ledger has been created under the wrong group. What should be done?","Review the accounting nature and correct the ledger grouping appropriately","Create duplicate ledgers","Ignore the grouping","Delete unrelated vouchers"),
q("A bank balance in books differs from the bank statement. What process helps investigate the difference?","Bank reconciliation","Stock valuation only","Payroll processing","Logo verification"),
q("Before finalizing a Profit and Loss report, what should be verified?","Relevant ledger balances, period, classifications and adjustments","Only report colour","Only company logo","Only page size"),
q("A student enters a purchase as a sales transaction in Tally. What should the trainer first ask them to identify?","The underlying business transaction and which accounts are affected","The keyboard shortcut used","The voucher colour","The computer name"),
q("What best demonstrates practical accounting software ability?","Accurately recording transactions and explaining their accounting effect and resulting reports","Memorizing menu names only","Typing vouchers quickly without understanding","Knowing only shortcut keys"),
],
"communication": [
q("How should debit and credit be introduced to a beginner?","Use simple business transactions and demonstrate their effect on accounts","Give rules only for memorization","Start with complex final accounts","Skip journal entries"),
q("A student can enter Tally vouchers but cannot explain them. What should the trainer do?","Ask the student to identify the transaction, accounts involved and accounting effect","Give more vouchers to copy","Mark the topic complete","Ignore conceptual understanding"),
q("What is an effective way to teach GST entries?","Explain the transaction first, then demonstrate the correct entry and verify its report impact","Teach shortcut keys only","Avoid invoices","Ask students to memorize tax screens"),
q("A beginner is confused by ledger groups. What should the trainer do?","Use familiar business accounts and classify them step by step","Give a long list to memorize","Skip grouping","Create every ledger under one group"),
q("How should Advanced Excel be taught to accounting students?","Use realistic business datasets and reporting tasks","Teach formulas without data","Avoid practical exercises","Use only presentation slides"),
q("A student's balance sheet is incorrect. What should the trainer encourage?","Trace the entries and classifications systematically rather than guessing","Change figures until totals match","Copy another student's report","Ignore the difference"),
q("How can a trainer verify accounting understanding?","Give a new business transaction and ask the learner to record and explain it","Ask only whether they understood","Check typing speed","Check attendance only"),
q("Students have different accounting backgrounds. What is an effective approach?","Establish core concepts and provide guided practice with additional challenges where needed","Teach only experienced students","Skip fundamentals for everyone","Give completed company data"),
q("A student asks a question about a tax rule the trainer is not certain about. What should the trainer do?","Verify the current authoritative information before giving a definitive answer","Invent a rule","Guess from memory","Tell the student tax rules never change"),
q("What is most important when training students for accounting jobs?","Accuracy, conceptual understanding, practical software use and professional responsibility","Speed alone","Memorizing menus","Avoiding reconciliation"),
],
},

# ============================================================
# TELE SALES EXECUTIVE
# ============================================================
"hiring-tele-sales": {
"practical": [
q("A new enquiry asks only 'fees?'. What is the best first response?","Acknowledge the enquiry and understand the student's course need before giving relevant guidance","Send only the highest fee","Ignore the enquiry","Immediately mark the lead closed"),
q("A prospect says the course fee is too high. What should the executive do?","Understand the concern, explain relevant value and available legitimate options without making false promises","Argue with the prospect","Immediately offer any unauthorized discount","End the call"),
q("A lead asks for a callback tomorrow at 4 PM. What should happen?","Record the follow-up accurately in CRM and contact them at the agreed time","Rely on memory","Call repeatedly today","Close the enquiry"),
q("A prospect is interested but wants to discuss with parents. What is an appropriate action?","Agree on a reasonable follow-up and provide clear information they can discuss","Pressure them to pay immediately","Mark them rejected","Call every few minutes"),
q("A lead has already spoken with another MCTI counsellor. What should you do?","Check CRM history and coordinate to avoid conflicting or duplicate communication","Pretend no previous conversation happened","Create many duplicate enquiries","Criticize the other counsellor"),
q("A student wants Data Analytics but their actual goal and background are unclear. What should the executive do?","Ask relevant qualification, career-goal and skill questions before recommending the next step","Promise a job immediately","Select the most expensive course automatically","Avoid asking questions"),
q("A prospect says another institute offers a lower price. What is the best approach?","Understand what they are comparing and explain MCTI's relevant offering factually","Make false claims about the competitor","Insult the competitor","Promise anything to close the sale"),
q("A lead does not answer the first call. What should the executive do?","Follow the approved follow-up process and record each meaningful attempt","Call continuously without limit","Delete the lead","Mark it converted"),
q("A student is ready to visit the branch. What information should be confirmed?","Branch, suitable visit time, course interest and any useful visit instructions","Only the student's first name","Nothing","Their social-media password"),
q("What is the strongest sign of a well-managed sales enquiry?","Accurate CRM history, clear next action and communication aligned with the student's need","Many undocumented calls","Immediate discounting","A long WhatsApp message regardless of need"),
],
"communication": [
q("What should happen at the beginning of a sales call?","Introduce yourself clearly, confirm the prospect and establish the purpose politely","Immediately demand payment","Speak continuously without listening","Ask unrelated personal questions"),
q("A prospect is speaking about their career concern. What should the executive do?","Listen actively and ask relevant follow-up questions","Interrupt with the fee repeatedly","Ignore their concern","Read a fixed script regardless of their answer"),
q("A prospect becomes irritated during a call. What is the best response?","Stay calm, listen, respond respectfully and avoid escalating the conversation","Argue until they agree","Raise your voice","Mock the prospect"),
q("What makes a course recommendation credible?","Connecting the recommendation to the prospect's stated goals, background and needs","Always recommending the highest-priced course","Guaranteeing a job","Using pressure"),
q("A prospect asks something you do not know. What should you do?","Say you will verify the information and follow up accurately","Invent an answer","Avoid the prospect forever","Give a random estimate as fact"),
q("What is an effective way to handle an objection?","Understand the real concern before responding with relevant information","Interrupt immediately","Repeat the same sentence","Ignore the objection"),
q("A prospect says 'I will think about it.' What is a useful response?","Understand what information or concern remains and agree on an appropriate next step","Say goodbye and delete the lead","Call every ten minutes","Pressure them for card details"),
q("How should WhatsApp follow-up messages be written?","Clear, relevant, professional and connected to the previous conversation","As long as possible","In all capital letters","With unrelated offers"),
q("What is more important than speaking continuously in counselling sales?","Listening and understanding the prospect's actual requirement","Using difficult English","Speaking faster than the prospect","Reading every course name"),
q("What communication behavior supports long-term trust?","Accurate information, respectful follow-up and avoiding unsupported promises","Guaranteed placement claims regardless of facts","Hidden conditions","Pressure and repeated spam"),
],
},

# ============================================================
# RECEPTIONIST
# ============================================================
"hiring-receptionist": {
"practical": [
q("A visitor arrives while the phone is ringing. What is the best approach?","Acknowledge the visitor promptly while handling the call professionally and prioritizing both appropriately","Ignore the visitor completely","Disconnect every call","Leave the reception desk"),
q("A student asks to meet a staff member who is currently unavailable. What should the receptionist do?","Explain availability politely and coordinate an appropriate next step","Say the staff member does not want to meet them","Send the visitor into any room","Ignore the request"),
q("A new walk-in enquiry arrives. What information should be captured accurately?","Relevant contact and course-enquiry details according to the institute process","Only the visitor's first name","No information","Their personal passwords"),
q("Two visitors claim they have appointments at the same time. What should the receptionist do?","Verify the appointments and coordinate calmly with the relevant staff","Ask them to argue with each other","Send both away","Choose one randomly"),
q("A parent is upset about waiting time. What is the best response?","Listen respectfully, check the situation and provide an accurate update or escalation","Argue about how busy the office is","Ignore them","Give a false waiting time"),
q("A caller asks for confidential student information. What should the receptionist do?","Follow privacy and authorization procedures before disclosing any information","Share everything immediately","Post the information publicly","Guess whether the caller is genuine"),
q("A courier arrives for a staff member. What should happen?","Follow the office receiving and notification procedure accurately","Leave the package outside unattended","Open it without reason","Discard it"),
q("A visitor asks for directions to a classroom. What is the best response?","Give clear directions or appropriately guide them","Point randomly","Say you do not know without checking","Send them outside"),
q("A scheduled meeting changes location. What should the receptionist do?","Update relevant information and communicate the change to affected people promptly","Keep the old information","Tell only one random visitor","Delete the schedule"),
q("What is essential when maintaining a front-desk enquiry record?","Accurate details, timely updates and clear follow-up ownership","Decorative formatting only","Remembering everything without records","Creating duplicate records for every call"),
],
"communication": [
q("How should a receptionist greet a visitor?","Politely, professionally and with attention to how they can be assisted","Without looking up","By immediately asking for money","By continuing a personal call"),
q("A caller is speaking very quickly and details are unclear. What should you do?","Politely ask for clarification and confirm important information","Pretend you understood","End the call","Write random details"),
q("A visitor asks a question you cannot answer. What is the best response?","Check with the appropriate person or source and provide accurate guidance","Invent an answer","Ignore them","Send them to an unrelated department"),
q("A parent is angry. What communication style is appropriate?","Calm, respectful listening with factual assistance or proper escalation","Matching their anger","Sarcasm","Interrupting continuously"),
q("What is important when transferring a phone call?","Confirm the purpose and transfer to the appropriate person when possible","Transfer randomly","Disconnect without explanation","Share unrelated internal information"),
q("How should confidential information be discussed at reception?","Only with authorized people and with appropriate discretion","Loudly in front of visitors","On public social media","With anyone who asks"),
q("A visitor has difficulty understanding English. What is a good approach?","Communicate patiently using a language or simple explanation available and appropriate","Make fun of them","Speak faster","Refuse assistance"),
q("What creates a professional first impression?","Courteous communication, attentiveness, accurate information and organized handling","Expensive decoration alone","Speaking loudly","Ignoring waiting visitors"),
q("A staff member gives unclear instructions about a visitor. What should the receptionist do?","Clarify the instruction before acting when necessary","Guess and act randomly","Tell the visitor confidential details","Ignore all instructions"),
q("What should a receptionist do when several people need assistance?","Acknowledge them, prioritize appropriately and communicate expected next steps","Serve only familiar people","Ignore the queue","Leave the desk"),
],
},

# ============================================================
# AI & MACHINE LEARNING TRAINER
# ============================================================
"hiring-ai-ml-trainer": {
"practical": [
q("A classification model performs well on training data but poorly on unseen data. What should be investigated?","Overfitting and the model's generalization to validation or test data","Monitor brightness","Dataset filename","Python logo"),
q("A dataset contains many missing values. What should happen before blindly training a model?","Understand the missingness and choose an appropriate handling strategy","Replace every missing value with the same random number","Delete the target column automatically","Ignore all missing values"),
q("A model has 95% accuracy on a highly imbalanced dataset. What should you do?","Examine class distribution and appropriate metrics such as precision, recall or F1","Assume the model is excellent from accuracy alone","Delete the minority class","Increase the displayed accuracy"),
q("Training and test data accidentally contain overlapping records. What risk does this create?","Data leakage and misleading evaluation","Better security","Automatic fairness","Reduced storage only"),
q("A business asks why a model made an important prediction. What should the ML practitioner consider?","Appropriate interpretability, evidence and limitations for the use case","Invent a reason","Hide all model information","Claim AI can never be questioned"),
q("A feature contains information that would only be known after the predicted event. What is the concern?","Target or future-information leakage","CSS formatting","Network routing","Image compression"),
q("A model's performance drops after deployment because real-world data has changed. What should be investigated?","Data or concept drift and the need for monitoring or retraining","Keyboard layout","File extension","Website colour"),
q("Before using personal data to train an AI model, what should be considered?","Privacy, authorization, purpose, security and applicable policy or requirements","Only model speed","Only dataset size","Nothing if AI is involved"),
q("Two models have similar performance but one is much simpler. What should influence the choice?","Requirements such as interpretability, reliability, cost and maintainability in addition to performance","Always choose the largest model","Choose randomly","Select by model name"),
q("What best demonstrates practical ML ability?","Preparing data, building and evaluating a model, explaining choices and recognizing limitations","Memorizing algorithm names only","Running copied code without understanding","Knowing AI terminology only"),
],
"communication": [
q("How should machine learning be introduced to beginners?","Use a simple prediction example connecting data, patterns, training and evaluation","Start with advanced mathematical proofs only","Give buzzwords only","Skip examples"),
q("A student believes AI always gives correct answers. What should the trainer explain?","AI systems can make errors and outputs require appropriate evaluation and verification","AI is always correct","Only humans make errors","Verification is unnecessary"),
q("How should overfitting be taught effectively?","Compare training and unseen-data performance using a simple example","Give the definition only","Avoid evaluation examples","Say more training accuracy is always better"),
q("A student copies an ML notebook but cannot explain the pipeline. What should the trainer do?","Ask them to explain and modify each stage from data preparation through evaluation","Mark it complete","Give another notebook to copy","Ignore understanding"),
q("What is a responsible way to teach generative AI?","Include verification, privacy, bias, limitations and appropriate human judgment","Teach students to trust every output","Encourage uploading confidential data","Avoid discussing limitations"),
q("A student asks which ML algorithm is always best. What should the trainer explain?","Model choice depends on the problem, data, constraints and evaluation","One algorithm is always best","Always use the newest model","Choose based on popularity only"),
q("How can a trainer verify understanding of classification metrics?","Give a scenario and ask the student to interpret relevant metrics and trade-offs","Ask them to memorize metric names","Check typing speed","Ask only if they understood"),
q("Students are intimidated by ML mathematics. What is a useful teaching approach?","Build intuition with examples, then progressively connect concepts to the required mathematics","Remove all explanation","Start with the hardest derivation","Tell them mathematics is unnecessary in every case"),
q("During an AI demonstration the model gives a wrong answer. What should the trainer do?","Use it to demonstrate verification, limitations and systematic evaluation","Hide the result","Claim the answer is actually correct","End the demonstration"),
q("What should an AI trainer encourage when students use AI coding tools?","Understand, test and verify generated code rather than accepting it blindly","Submit generated code without reading it","Disable all testing","Assume generated code is secure"),
],
},

}
