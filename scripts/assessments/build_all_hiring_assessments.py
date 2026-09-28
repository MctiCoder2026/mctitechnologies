from assessments.models import (
    Assessment,
    AssessmentQuestion,
    AssessmentOption,
)

# Python Trainer already has its own verified 25-question bank.
# This master builder handles the remaining hiring assessments.
QUESTION_BANKS = {}

def q(category, question, correct, wrong1, wrong2, wrong3):
    """Compact question definition. Correct answer is always option 1."""
    return (
        category,
        question,
        [correct, wrong1, wrong2, wrong3],
        0,
    )




QUESTION_BANKS.update({

"hiring-data-analytics-trainer": [
q("Data Fundamentals","What is the main purpose of data analysis?","To extract useful insights from data","To increase file size","To replace all databases","To design logos"),
q("Data Fundamentals","Which measure represents the middle value in ordered data?","Median","Mean","Range","Variance"),
q("Data Fundamentals","Which data type represents categories such as department names?","Categorical data","Continuous data","Binary code only","Timestamp only"),
q("Data Fundamentals","What does a NULL value commonly represent in a dataset?","Missing or unknown data","Always zero","Duplicate data","A formula"),
q("Data Fundamentals","Which chart is commonly suitable for comparing values across categories?","Bar chart","Scatter plot only","Source-code window","Text editor"),

q("Excel SQL BI","Which Excel function calculates an arithmetic average?","AVERAGE","COUNTIF","CONCAT","LEFT"),
q("Excel SQL BI","What is a PivotTable mainly used for?","Summarizing and analyzing data","Writing Python classes","Creating operating systems","Encrypting files"),
q("Excel SQL BI","Which SQL clause filters rows based on a condition?","WHERE","ORDER","CREATE","JOINED"),
q("Excel SQL BI","Which SQL operation combines related rows from multiple tables?","JOIN","PRINT","FORMAT","COMMITMENT"),
q("Excel SQL BI","What is a dashboard intended to provide?","A visual summary of important metrics","A replacement for raw data collection","Only decorative graphics","A programming compiler"),

q("Practical & Debugging","A numeric column contains text values by mistake. What should an analyst do first?","Inspect and clean the data before analysis","Ignore the values","Delete the entire database","Change every value to zero"),
q("Practical & Debugging","A report total suddenly doubles after a table join. What should be checked first?","Whether the join created duplicate matches","Monitor brightness","Excel font size","Internet browser history"),
q("Practical & Debugging","Which practice helps make an analysis reproducible?","Document data sources and transformation steps","Manually change results each time","Hide formulas","Delete source files"),
q("Practical & Debugging","Before removing duplicate records, what should be verified?","Which fields define a true duplicate","The chart colour","The file icon","The computer wallpaper"),
q("Practical & Debugging","A dashboard KPI disagrees with the source report. What is the best first action?","Trace the calculation and filters back to source data","Publish it anyway","Guess the correct number","Delete the KPI"),

q("Training Ability","A beginner is confused about mean and median. What is the best teaching approach?","Use a small real-life dataset and calculate both","Give definitions only","Skip the topic","Ask them to memorize formulas"),
q("Training Ability","How should a trainer introduce PivotTables to beginners?","Demonstrate a simple summary task using sample data","Start with complex macros","Avoid hands-on practice","Teach only keyboard shortcuts"),
q("Training Ability","A student creates a wrong chart. What should the trainer ask first?","What question the chart is supposed to answer","Why the student used a computer","To copy another chart","To remove all labels"),
q("Training Ability","What best demonstrates that a student understands SQL GROUP BY?","The student can solve a small aggregation task independently","The student says yes","The student copies a query","The student remembers the spelling"),
q("Training Ability","Students have different Excel skill levels. What is an effective approach?","Use guided exercises with extension tasks for faster learners","Teach only advanced students","Remove practical exercises","Give completed files only"),

q("Industry Understanding","Why is data validation important before business reporting?","Poor-quality input can produce misleading conclusions","It changes monitor resolution","It automatically increases sales","It removes the need for analysis"),
q("Industry Understanding","What is a KPI?","A measurable indicator used to track performance","A programming language","A database password","An image format"),
q("Industry Understanding","Why should sensitive business data have controlled access?","To protect confidentiality and reduce unauthorized exposure","To make reports slower","To increase duplicate records","To remove backups"),
q("Industry Understanding","What should an analyst do when evidence does not support a requested conclusion?","Report the findings accurately and explain the limitation","Alter the data to match the request","Hide conflicting records","Invent additional observations"),
q("Industry Understanding","Before deploying a new management dashboard, what should be done?","Validate calculations and test filters against trusted data","Delete previous reports immediately","Publish without checking","Use random sample values"),
],

"hiring-full-stack-development-trainer": [
q("Web Fundamentals","What is HTML primarily used for?","Structuring web content","Managing database backups","Compiling Java","Configuring routers"),
q("Web Fundamentals","What is CSS primarily responsible for?","Presentation and layout of web pages","Database transactions","Server passwords","Python package installation"),
q("Web Fundamentals","Which language commonly adds interactive behavior in a browser?","JavaScript","SQL","CSS only","Markdown"),
q("Web Fundamentals","What does responsive web design aim to achieve?","Usable layouts across different screen sizes","Only desktop support","Faster CPU speed","Automatic database normalization"),
q("Web Fundamentals","Which HTTP method is commonly used to retrieve a resource?","GET","DROP","COMPILE","PUSHFILE"),

q("Full Stack Concepts","What is an API commonly used for?","Communication between software components","Changing monitor brightness","Creating folders only","Replacing all databases"),
q("Full Stack Concepts","What is the purpose of a database primary key?","Uniquely identify a record","Style an HTML element","Start a web server","Encrypt CSS"),
q("Full Stack Concepts","Why is Git used in software development?","Version control and collaboration","Graphic design","Database indexing only","Operating system installation"),
q("Full Stack Concepts","What is server-side validation used for?","Checking submitted data before trusted processing","Changing CSS colours","Increasing screen size","Creating browser bookmarks"),
q("Full Stack Concepts","What is authentication intended to establish?","Who a user is","Which CSS framework is installed","The monitor model","The file extension"),

q("Practical & Debugging","A page works on desktop but overflows on mobile. What should be checked first?","Responsive CSS and viewport behavior","Database password","Git username only","Server timezone"),
q("Practical & Debugging","A form submits but the database is not updated. What is a useful first debugging step?","Inspect request handling, validation and server logs","Rewrite the entire application","Change the logo","Delete the repository"),
q("Practical & Debugging","A JavaScript function is not running. What should be inspected first?","Browser console errors and event binding","Printer settings","Database table colour","Monitor cable"),
q("Practical & Debugging","Before changing production code, what is good practice?","Test the change in a safe environment and keep version history","Edit production blindly","Delete the previous version","Disable backups"),
q("Practical & Debugging","A login-protected page is accessible without login. What type of issue should be checked?","Authorization/access-control logic","Font family","Image dimensions","CSS spacing"),

q("Training Ability","How should HTML forms be introduced to beginners?","Build a small form and explain each field through practice","Start with deployment architecture only","Ask students to memorize tags without use","Skip validation"),
q("Training Ability","A student copied React code but cannot explain state. What should the trainer do?","Use a small interactive example and ask the student to predict changes","Move to the next framework","Give more code to copy","Mark the topic complete"),
q("Training Ability","What is a useful way to teach Git commits?","Have students make small changes and inspect their commit history","Only dictate commands","Avoid repositories","Use screenshots instead of practice"),
q("Training Ability","A student receives a 404 error. What should a trainer encourage?","Trace the requested URL and routing configuration","Reinstall the operating system immediately","Ignore the error","Change random CSS"),
q("Training Ability","How can a trainer verify full-stack understanding?","Give a small feature requiring UI, server logic and data storage","Ask only theoretical definitions","Check typing speed","Ask whether they understood"),

q("Industry Understanding","Why should passwords not be stored as plain text?","A secure password-hashing approach reduces exposure if data is compromised","Plain text improves security","Browsers require plain text","CSS cannot read hashes"),
q("Industry Understanding","What is deployment?","Making an application available in its target environment","Creating only HTML headings","Deleting source code","Renaming variables"),
q("Industry Understanding","Why are environment variables commonly used for secrets/configuration?","They help separate sensitive or environment-specific settings from source code","They replace testing","They automatically fix bugs","They are CSS variables"),
q("Industry Understanding","What is the purpose of code review?","Identify issues and improve code quality before changes are accepted","Increase file size","Remove version history","Avoid collaboration"),
q("Industry Understanding","Before releasing a new feature, what should be verified?","Required functionality and important existing flows still work","Only the homepage colour","Only developer login","Nothing if code compiles"),
],

"hiring-cyber-security-trainer": [
q("Security Fundamentals","What is the principle of least privilege?","Give users only the access needed for their tasks","Give every user administrator access","Share one password with everyone","Disable access controls"),
q("Security Fundamentals","What does MFA add to authentication?","An additional verification factor","A larger monitor","A second username only","Automatic administrator rights"),
q("Security Fundamentals","What is phishing?","A deceptive attempt to obtain sensitive information","A database backup method","A network cable standard","A software update"),
q("Security Fundamentals","What is the main purpose of a firewall?","Control network traffic according to security rules","Create spreadsheets","Design websites","Compress images"),
q("Security Fundamentals","Why are software security updates important?","They can fix known vulnerabilities","They remove all passwords","They eliminate the need for backups","They guarantee no future attacks"),

q("Networking & Defense","What does HTTPS primarily add to HTTP communication?","Encrypted transport using TLS","Unlimited bandwidth","A database engine","A programming language"),
q("Networking & Defense","What is network segmentation used for?","Limit and control communication between network areas","Increase monitor resolution","Replace authentication","Remove IP addresses"),
q("Networking & Defense","What is a VPN commonly used for?","Creating an encrypted connection across an untrusted network","Deleting malware automatically","Replacing every firewall","Increasing disk capacity"),
q("Networking & Defense","What is the purpose of logging security events?","Support monitoring, investigation and accountability","Hide system activity","Replace access control","Increase CPU clock speed"),
q("Networking & Defense","Which practice is safest for administrator accounts?","Use separate privileged accounts with strong controls","Share one admin account","Use default passwords","Disable audit logs"),

q("Practical & Troubleshooting","A user reports a suspicious login notification. What should be done first?","Verify the event and secure the account using approved procedures","Ignore it","Publish the password","Delete all company data"),
q("Practical & Troubleshooting","A computer may be infected with malware. What is an appropriate initial response?","Isolate it as appropriate and follow the incident-response process","Connect it to more systems","Disable all logs","Send the suspected file to everyone"),
q("Practical & Troubleshooting","Repeated failed logins appear in logs. What should a defender do?","Investigate the source and apply appropriate account/network protections","Delete the logs","Share credentials","Turn off authentication"),
q("Practical & Troubleshooting","Before performing a security test on a system, what is essential?","Explicit authorization and defined scope","Only technical skill","A public IP address","Anonymous access"),
q("Practical & Troubleshooting","A security configuration change is proposed for production. What is good practice?","Assess, test, document and use approved change procedures","Apply random settings","Disable backups first","Hide the change from administrators"),

q("Training Ability","How should password security be taught to beginners?","Use practical examples of strong unique passwords and MFA","Teach password sharing","Use only technical jargon","Skip demonstrations"),
q("Training Ability","A student asks to attack an external website for practice. What should a trainer do?","Explain legal/ethical boundaries and use authorized labs","Provide an unauthorized target","Encourage testing any public site","Ignore permission requirements"),
q("Training Ability","What environment is appropriate for teaching security testing?","An isolated or explicitly authorized lab","An unrelated company's live network","Any public Wi-Fi device","A stranger's account"),
q("Training Ability","How can a trainer check understanding of phishing awareness?","Use a safe scenario and ask students to identify warning signs","Ask only if they understood","Collect their passwords","Send real malicious attachments"),
q("Training Ability","A beginner confuses authentication with authorization. What is a useful explanation?","Authentication verifies identity; authorization determines permitted actions","They are always identical","Authorization creates passwords","Authentication controls CSS"),

q("Professional & Ethical Practice","What should an ethical security professional do after discovering a vulnerability during authorized work?","Follow the agreed reporting and disclosure process","Exploit it beyond scope","Publish sensitive details immediately","Hide it permanently"),
q("Professional & Ethical Practice","Why is scope important in a penetration test?","It defines what systems and actions are authorized","It increases internet speed","It replaces documentation","It makes passwords unnecessary"),
q("Professional & Ethical Practice","Why should security evidence and logs be handled carefully?","To preserve integrity, confidentiality and usefulness for investigation","To make files larger","To avoid all documentation","To allow unrestricted sharing"),
q("Professional & Ethical Practice","What is defense in depth?","Using multiple complementary security controls","Relying on one password","Removing monitoring","Giving all users the same permissions"),
q("Professional & Ethical Practice","What should be emphasized when teaching ethical hacking?","Authorization, defensive learning, responsible conduct and legal boundaries","Unauthorized access as practice","Credential sharing","Avoiding documentation"),
],

})


QUESTION_BANKS.update({

"hiring-java-trainer": [
q("Java Fundamentals","Which method is the standard entry point of a basic Java application?","public static void main(String[] args)","public void start()","static int run()","private main()"),
q("Java Fundamentals","Which keyword creates an object in Java?","new","create","object","make"),
q("Java Fundamentals","Which Java type stores whole numbers such as 10?","int","boolean","char[] only","void"),
q("Java Fundamentals","Which keyword is used to inherit from a class?","extends","inherits","implementsClass","parent"),
q("Java Fundamentals","What does JVM stand for?","Java Virtual Machine","Java Variable Manager","Joint Virtual Module","Java Visual Method"),

q("OOP & Collections","What is encapsulation?","Bundling data and behavior while controlling access","Running many loops","Creating only static methods","Deleting constructors"),
q("OOP & Collections","What does method overriding allow?","A subclass to provide its own implementation of an inherited method","Two variables to share a name in one scope","A class to avoid methods","A constructor to return a value"),
q("OOP & Collections","Which collection allows indexed access and duplicate elements?","ArrayList","HashSet","TreeSet only","Map key set only"),
q("OOP & Collections","What does a HashMap primarily store?","Key-value pairs","Only unique integers","Only sorted strings","HTML elements"),
q("OOP & Collections","What is an interface commonly used for?","Defining a contract that implementing classes follow","Storing database rows directly","Creating operating systems","Replacing every class"),

q("Practical & Debugging","What exception commonly occurs when calling a method on a null reference?","NullPointerException","IOException only","ArithmeticException always","ClassCastException always"),
q("Practical & Debugging","What is the purpose of try-catch?","Handle exceptions in a controlled way","Create inheritance","Declare packages","Compile CSS"),
q("Practical & Debugging","A loop never ends. What should be inspected first?","Its termination condition and variable updates","The monitor resolution","The class filename colour","The keyboard layout"),
q("Practical & Debugging","A Java file fails to compile. What is the best first step?","Read the compiler error and inspect the referenced line","Rewrite the entire project","Delete the JDK","Ignore the error"),
q("Practical & Debugging","Why should database resources be closed or managed properly?","To avoid resource leaks and reliability problems","To increase duplicate records","To disable transactions","To remove validation"),

q("Training Ability","How should OOP be introduced to a beginner?","Use a simple real-world object example and build a small class","Begin only with complex design patterns","Ask students to memorize definitions","Skip objects"),
q("Training Ability","A student confuses a class with an object. What should a trainer do?","Demonstrate a class as a blueprint and create multiple instances","Give more definitions only","Skip the question","Ask the student to copy code"),
q("Training Ability","What best checks understanding of inheritance?","Ask the student to design a small parent-child class example","Ask only whether they understood","Show a slide again","Check typing speed"),
q("Training Ability","A student's code throws an exception. What should the trainer encourage?","Read the stack trace and identify where the failure begins","Delete all code","Copy another solution","Ignore stack traces"),
q("Training Ability","How should collections be taught effectively?","Compare structures using small practical data-handling tasks","Teach method names without examples","Avoid coding exercises","Use only theory notes"),

q("Development Understanding","Why are packages used in Java projects?","To organize related classes and manage namespaces","To replace databases","To create passwords","To style web pages"),
q("Development Understanding","What is Maven or Gradle commonly used for?","Build and dependency management","Image editing","Network cabling","Spreadsheet formatting"),
q("Development Understanding","Why are automated tests useful?","They help verify behavior and detect regressions","They eliminate all bugs permanently","They replace requirements","They make source control unnecessary"),
q("Development Understanding","What is REST commonly associated with?","Designing web APIs around resources and HTTP operations","Desktop wallpaper settings","Java bytecode only","Database passwords"),
q("Development Understanding","Before deploying a Java application change, what should be done?","Test the change and important existing functionality","Deploy directly without testing","Delete version history","Modify production data randomly"),
],

"hiring-mia-accounts-trainer": [
q("Accounting Fundamentals","What is the basic accounting equation?","Assets = Liabilities + Capital","Sales = Assets + Password","Cash = Profit + Stock only","Expenses = Assets + Sales"),
q("Accounting Fundamentals","Which document is commonly issued to record a sale to a customer?","Sales invoice","Password report","Attendance sheet","Network log"),
q("Accounting Fundamentals","What is a ledger used for?","Classifying and summarizing transactions by account","Creating presentations","Managing network IPs","Writing source code"),
q("Accounting Fundamentals","What is a trial balance primarily used to check?","Whether debit and credit balances arithmetically agree","Employee attendance","Internet speed","Document formatting"),
q("Accounting Fundamentals","Which statement reports income and expenses for a period?","Profit and Loss Statement","Network Statement","Attendance Register","CSS Report"),

q("Tally & GST","What is a voucher in Tally primarily used for?","Recording a business transaction","Designing a logo","Creating a website","Installing Windows"),
q("Tally & GST","Which voucher is commonly used for money received?","Receipt voucher","Payment voucher","Contra only","Stock journal only"),
q("Tally & GST","Which voucher is commonly used for money paid?","Payment voucher","Receipt voucher","Sales order only","Memorandum only"),
q("Tally & GST","What is GST generally applied to?","Taxable supplies of goods and services according to applicable rules","Employee passwords","Computer memory","Website domains"),
q("Tally & GST","Why should GST details in an invoice be checked carefully?","Incorrect tax details can affect accounting and compliance","They only change invoice colour","They control internet speed","They replace customer details"),

q("Excel Practical","Which Excel function is commonly used to total a range?","SUM","LEFT","UPPER","LEN only"),
q("Excel Practical","What is an absolute cell reference such as $A$1 useful for?","Keeping a reference fixed when a formula is copied","Deleting a worksheet","Creating a password","Changing file type"),
q("Excel Practical","What is VLOOKUP/XLOOKUP commonly used for?","Finding related values from a table or range","Creating operating systems","Compressing files","Drawing charts only"),
q("Excel Practical","Why are PivotTables useful in accounting work?","They quickly summarize transaction data","They replace source transactions","They create GST registrations","They install Tally"),
q("Excel Practical","A total in an Excel report looks wrong. What should be checked first?","Formula references, filters and source values","Screen brightness","Printer colour","File icon"),

q("Training Ability","How should debit and credit be introduced to beginners?","Use simple business transactions and show their effect on accounts","Ask students to memorize rules without entries","Start only with final accounts","Skip journal entries"),
q("Training Ability","A student can enter vouchers but cannot explain them. What should a trainer do?","Ask the student to identify the business transaction and accounting effect","Give more vouchers to copy","Mark the module complete","Avoid questions"),
q("Training Ability","What is an effective way to teach Tally?","Combine concept explanation with hands-on company and voucher practice","Use screenshots only","Avoid practical entries","Teach shortcuts only"),
q("Training Ability","How can a trainer check Advanced Excel understanding?","Give a small business dataset and ask for a useful report","Ask only formula names","Check typing speed","Ask whether the student attended"),
q("Training Ability","A learner makes repeated accounting-entry mistakes. What is the best response?","Trace the transaction logic with the learner and provide guided practice","Give the correct file without explanation","Skip accounting concepts","Remove all exercises"),

q("Business Practice","Why should financial records have supporting documents?","They provide evidence and help verification","They increase monitor speed","They replace accounting entries","They remove the need for controls"),
q("Business Practice","Why is regular reconciliation important?","It helps identify differences between records and external statements","It changes GST rates","It replaces invoices","It increases file size"),
q("Business Practice","How should confidential financial information be handled?","Only through authorized access and appropriate controls","Shared publicly","Sent to anyone who asks","Stored without access restrictions"),
q("Business Practice","Before finalizing a client accounting report, what should be done?","Review entries, balances and relevant reconciliations","Assume all entries are correct","Delete supporting records","Change figures to expected values"),
q("Business Practice","What is a trainer's responsibility when accounting rules or tax provisions change?","Use current reliable guidance and update teaching material","Continue teaching outdated rules knowingly","Guess the new rule","Avoid explaining the change"),
],

"hiring-tele-sales": [
q("Communication","What is the best opening for a professional sales call?","Introduce yourself, the organization and reason for calling clearly","Immediately demand payment","Speak without confirming the person","Start with unrelated questions"),
q("Communication","Why is active listening important in telesales?","It helps understand the prospect's actual needs","It makes calls longer only","It avoids recording enquiries","It replaces product knowledge"),
q("Communication","What should a salesperson do if a prospect is speaking?","Listen without unnecessary interruption","Talk over the prospect","End the call immediately","Mute permanently"),
q("Communication","Which communication style is generally most effective?","Clear, respectful and need-focused","Aggressive and rushed","Unclear and technical","Argumentative"),
q("Communication","If a prospect does not understand a course feature, what should the salesperson do?","Explain it simply with a relevant benefit or example","Repeat the same sentence louder","Ignore the question","Promise an unrelated feature"),

q("Lead Qualification","Why should a salesperson ask about the learner's goal?","To recommend relevant options and understand intent","To avoid updating CRM","To increase call duration","To collect unrelated information"),
q("Lead Qualification","Which information is useful when qualifying a training enquiry?","Career goal, current background, course interest and timeline","Favourite movie only","Phone wallpaper","Computer brand only"),
q("Lead Qualification","A prospect wants Data Analytics but has unclear goals. What is the best next step?","Ask focused questions about background and career objective","Immediately force admission","Reject the enquiry","Quote a random course"),
q("Lead Qualification","What is a hot lead generally characterized by?","Clear interest and meaningful near-term intent","No interest and wrong contact","A disconnected number only","No requirement at all"),
q("Lead Qualification","Why should enquiry details be recorded accurately?","So follow-up and counselling use reliable information","To make CRM slower","To avoid future contact","To increase duplicate leads"),

q("Follow-up & CRM","What is the purpose of a scheduled follow-up?","Continue the sales conversation at an agreed or useful time","Call continuously without context","Delete the lead","Avoid recording activity"),
q("Follow-up & CRM","A prospect asks to call tomorrow at 5 PM. What should be done?","Record the follow-up accurately and contact around the agreed time","Call repeatedly today","Close the lead immediately","Ignore the request"),
q("Follow-up & CRM","Why should call notes be added to CRM?","To preserve context for future follow-up and team visibility","To replace the customer's phone number","To hide previous conversations","To create duplicate enquiries"),
q("Follow-up & CRM","A lead does not answer one call. What is the best response?","Record the attempt and follow the approved follow-up process","Mark them permanently uninterested immediately","Call every minute","Delete the enquiry"),
q("Follow-up & CRM","What should happen when an enquiry converts to admission?","Update the CRM status accurately according to process","Keep it marked new forever","Delete the history","Create many duplicate leads"),

q("Objection Handling","A prospect says the fee is high. What should the salesperson do first?","Understand the concern and explain relevant value/options accurately","Argue with the prospect","Invent a discount","End the call"),
q("Objection Handling","A prospect says they need time to decide. What is appropriate?","Clarify any unanswered concern and agree on a reasonable follow-up","Pressure them continuously","Mark selected automatically","Promise guaranteed employment"),
q("Objection Handling","What should a salesperson do when they do not know an answer?","Say they will verify the correct information and follow up","Invent an answer","Blame the prospect","Change the subject permanently"),
q("Objection Handling","Why should false guarantees be avoided?","They damage trust and can mislead customers","They always improve long-term retention","They remove the need for counselling","They are required in sales"),
q("Objection Handling","A learner is comparing two courses. What is the best approach?","Compare them based on the learner's goals, prerequisites and outcomes","Always push the more expensive one","Criticize every competitor","Choose randomly"),

q("Conversion & Professionalism","What is a good call-to-action after a productive counselling call?","Agree on a clear next step such as visit, demo or follow-up","Leave the conversation without a next step","Demand immediate admission in every case","Delete the enquiry"),
q("Conversion & Professionalism","Why is timely follow-up important?","Interest and context can reduce over time","It guarantees every sale","It eliminates the need for counselling","It makes CRM unnecessary"),
q("Conversion & Professionalism","How should customer personal data be handled?","According to authorized business processes and privacy expectations","Shared with unrelated people","Posted publicly","Used for unrelated purposes without permission"),
q("Conversion & Professionalism","Which is a better sales measure than call count alone?","Meaningful outcomes such as qualified follow-ups and conversions","Maximum call duration only","Number of missed calls","Number of duplicate entries"),
q("Conversion & Professionalism","What is the goal of ethical telesales?","Help suitable prospects make informed decisions while achieving legitimate sales goals","Pressure every person into buying","Hide important conditions","Promise outcomes the organization cannot guarantee"),
],

"hiring-receptionist": [
q("Front Desk Communication","What should a receptionist do when a visitor enters the office?","Greet them professionally and identify how to assist","Ignore them until they ask repeatedly","Ask them to leave immediately","Continue a personal call"),
q("Front Desk Communication","How should an incoming business call normally be answered?","With a clear professional greeting and organization identification","With silence","Using only a personal nickname","By immediately placing every caller on hold"),
q("Front Desk Communication","If a visitor asks a question you cannot answer, what should you do?","Connect them to the appropriate person or verify the information","Invent an answer","Ignore the visitor","Give confidential information"),
q("Front Desk Communication","What is active listening at the front desk?","Paying attention, clarifying when needed and responding appropriately","Interrupting quickly","Avoiding eye contact and context","Speaking continuously"),
q("Front Desk Communication","How should an upset visitor be handled?","Remain calm, listen and follow the appropriate escalation process","Argue loudly","Ignore the concern","Promise anything requested"),

q("Office Coordination","Why should appointments be recorded accurately?","To avoid scheduling confusion and support coordination","To increase paperwork only","To remove visitor details","To avoid informing staff"),
q("Office Coordination","Two visitors arrive for different staff members at the same time. What should you do?","Acknowledge both and coordinate with the relevant staff professionally","Ignore one visitor","Send both away","Choose based on appearance"),
q("Office Coordination","A staff member is unavailable for a scheduled visitor. What is appropriate?","Inform the visitor politely and coordinate an alternative or next step","Pretend the staff member is present","Give the visitor staff passwords","Ignore the appointment"),
q("Office Coordination","Why is a visitor register useful?","It supports reception records, coordination and applicable security processes","It replaces all employee records","It is only decoration","It controls internet speed"),
q("Office Coordination","An important message arrives for a staff member. What should the receptionist do?","Record the essential details and pass it through the approved channel","Rely only on memory","Post it publicly","Delete it"),

q("Computer & Office Skills","Which application is commonly suitable for preparing a formal letter?","Microsoft Word or equivalent word processor","Calculator only","BIOS setup","Router console"),
q("Computer & Office Skills","Which spreadsheet feature is useful for organizing a visitor or enquiry list?","Rows, columns, sorting and filtering","Slide transitions","Video effects","Source-code compiler"),
q("Computer & Office Skills","What should be checked before sending a professional email?","Recipient, subject, content and attachments","Only font colour","Only internet speed","Nothing"),
q("Computer & Office Skills","Why are clear filenames useful?","They make documents easier to identify and manage","They increase RAM","They replace backups","They change file contents automatically"),
q("Computer & Office Skills","A printer does not print a document. What is a sensible first check?","Printer status, selected printer and print queue","Delete all office files","Change every password","Reinstall the operating system immediately"),

q("Enquiry Handling","A student asks about a course. What should reception do first?","Capture the basic requirement accurately and guide them to the appropriate counsellor/process","Quote random information","Promise admission benefits not approved","Ignore the enquiry"),
q("Enquiry Handling","Why should mobile numbers be entered carefully?","Incorrect numbers can break follow-up communication","They affect screen brightness","They replace names","They are never used"),
q("Enquiry Handling","An existing student asks about fees but you are not authorized to access billing. What should you do?","Direct the student to the authorized person/process","Open restricted records anyway","Guess the balance","Share another student's information"),
q("Enquiry Handling","A caller asks for confidential information about another student. What should you do?","Follow privacy rules and do not disclose unauthorized information","Provide all available details","Send database screenshots","Share passwords"),
q("Enquiry Handling","What makes an enquiry record useful?","Accurate contact details, requirement and relevant notes","Only the person's first name","Random comments","Duplicate entries"),

q("Professionalism & Scenarios","What is appropriate front-desk appearance and behavior?","Neat, professional and aligned with workplace standards","Careless and dismissive","Constant personal phone use","Ignoring visitors"),
q("Professionalism & Scenarios","How should confidential documents at reception be handled?","Keep them protected and accessible only to authorized people","Leave them visible to all visitors","Photograph and share them","Discard them anywhere"),
q("Professionalism & Scenarios","A visitor arrives while you are handling a phone call. What is appropriate?","Acknowledge the visitor briefly and complete/route the call efficiently","Ignore the visitor completely","End every call abruptly","Ask the visitor to answer the phone"),
q("Professionalism & Scenarios","Why is punctuality important for reception work?","The front desk is a time-sensitive contact point for visitors and calls","It only affects computer speed","It is unrelated to service","It removes the need for coordination"),
q("Professionalism & Scenarios","If you make an entry mistake in an office system, what should you do?","Correct it through the proper process and inform the relevant person if necessary","Hide the mistake","Create more entries to cover it","Delete unrelated records"),
],

})


QUESTION_BANKS.update({

"hiring-ai-ml-trainer": [
q("AI & ML Fundamentals","What is machine learning?","A method where systems learn patterns from data","A type of computer monitor","A network cable","A spreadsheet format"),
q("AI & ML Fundamentals","Which learning type uses labeled training examples?","Supervised learning","Unsupervised learning only","Random learning","Manual formatting"),
q("AI & ML Fundamentals","What is a feature in a machine-learning dataset?","An input variable used by a model","A password","A file extension","A database backup"),
q("AI & ML Fundamentals","What is a target variable in supervised learning?","The value the model is intended to predict","The computer hostname","A chart colour","The training file name"),
q("AI & ML Fundamentals","What is generative AI designed to do?","Generate new content based on learned patterns","Only store files","Only sort spreadsheets","Configure routers"),

q("Models & Evaluation","Why is data commonly divided into training and test sets?","To evaluate performance on data not used for training","To duplicate every record","To remove all features","To avoid evaluation"),
q("Models & Evaluation","What is overfitting?","A model learns training data too specifically and generalizes poorly","A model has no input","A computer has too much RAM","A dataset has a filename"),
q("Models & Evaluation","Which metric is commonly used for classification performance?","Accuracy","File size","Screen resolution","Disk speed"),
q("Models & Evaluation","What does a confusion matrix summarize?","Classification predictions compared with actual classes","Network routes","Excel formulas","File permissions"),
q("Models & Evaluation","Why should model evaluation use appropriate metrics?","Different problems and error costs require different measures","One metric is perfect for every problem","Metrics replace data","Evaluation is unnecessary"),

q("Practical & Responsible AI","What should be checked before training a model on collected data?","Data quality, relevance and appropriate use","Only filename length","Monitor size","Keyboard layout"),
q("Practical & Responsible AI","A model performs well in training but poorly on new data. What is a likely concern?","Overfitting","File compression","Screen scaling","Database indexing"),
q("Practical & Responsible AI","Why should sensitive personal data be handled carefully in AI projects?","Privacy, security and appropriate-use obligations apply","AI removes privacy concerns","Sensitive data should always be public","It improves model accuracy automatically"),
q("Practical & Responsible AI","What is a useful first step when model predictions appear biased?","Inspect data, evaluation results and relevant groups for systematic problems","Hide the results","Increase random predictions","Remove all testing"),
q("Practical & Responsible AI","What should happen before relying on AI output for an important decision?","Validate the output and use appropriate human oversight","Assume every output is correct","Remove review processes","Ignore source data"),

q("Training Ability","How should machine learning be introduced to beginners?","Use a simple prediction example linking data, features and target","Begin only with advanced mathematics","Ask students to memorize algorithms","Skip datasets"),
q("Training Ability","A student thinks AI always gives correct answers. What should a trainer explain?","AI outputs can be incorrect and should be critically evaluated","AI is always authoritative","AI never depends on data","Verification is unnecessary"),
q("Training Ability","How can a trainer teach classification effectively?","Use a small labeled dataset and demonstrate prediction and evaluation","Use definitions only","Avoid examples","Teach only software installation"),
q("Training Ability","What best checks whether students understand overfitting?","Ask them to compare training and validation/test behavior in an example","Ask only if they understood","Check typing speed","Give them the definition to copy"),
q("Training Ability","How should prompt engineering be taught?","Through clear goals, context, constraints, iteration and output verification","As a collection of magic phrases","Without checking results","By hiding task context"),

q("Industry Understanding","Why is versioning useful in ML projects?","It helps track code, data/model changes and experiments","It removes the need for testing","It guarantees accuracy","It replaces documentation"),
q("Industry Understanding","What is model deployment?","Making a trained model available for use in a target system","Deleting training data automatically","Creating slides","Installing a printer"),
q("Industry Understanding","Why should deployed models be monitored?","Real-world data and performance can change over time","Models never change in usefulness","Monitoring reduces accuracy","Deployment guarantees permanent performance"),
q("Industry Understanding","What is responsible AI concerned with?","Safe, fair, transparent and accountable use of AI","Only faster processors","Only larger datasets","Removing human responsibility"),
q("Industry Understanding","Before using a third-party AI tool with company data, what should be considered?","Data sensitivity, permissions, tool terms and organizational policy","Only the tool logo","Only browser colour","Nothing because AI tools are always private"),
],

"hiring-hardware-networking-trainer": [
q("Hardware Fundamentals","Which component performs most general-purpose processing in a computer?","CPU","Keyboard","Monitor","Speaker"),
q("Hardware Fundamentals","What is RAM primarily used for?","Temporary working memory for active programs","Permanent archival storage only","Network routing","Printing"),
q("Hardware Fundamentals","Which device is commonly used for long-term computer storage?","SSD or hard drive","RAM module only","CPU fan","Mouse"),
q("Hardware Fundamentals","What is the purpose of a power supply unit?","Convert and supply electrical power required by computer components","Store user passwords","Route internet traffic","Display graphics"),
q("Hardware Fundamentals","What does BIOS/UEFI help do during startup?","Initialize hardware and begin the boot process","Create Excel formulas","Send emails","Configure website CSS"),

q("Networking Fundamentals","What is an IP address used for?","Identifying and addressing devices on an IP network","Naming Excel worksheets","Storing passwords","Formatting disks"),
q("Networking Fundamentals","What is the primary role of a network switch?","Connect devices within a network and forward frames appropriately","Convert Word files to PDF","Cool the CPU","Create user accounts"),
q("Networking Fundamentals","What is a router primarily used for?","Forward traffic between different networks","Increase RAM","Store keyboard input","Display webpages"),
q("Networking Fundamentals","What does DHCP commonly provide automatically?","IP configuration to network clients","CPU clock speed","User passwords","Printer ink"),
q("Networking Fundamentals","What does DNS commonly translate?","Domain names to IP addresses","RAM to storage","Passwords to usernames","Images to videos"),

q("Practical & Troubleshooting","A desktop has no power. What should be checked first?","Power source, cable, switch and basic PSU connections","Reinstall every application","Change the IP address","Format the disk"),
q("Practical & Troubleshooting","A PC powers on but shows no display. What is a sensible first approach?","Check display connections and basic hardware indicators systematically","Immediately replace every component","Delete the operating system","Change the router password"),
q("Practical & Troubleshooting","One computer cannot access the network while others can. What should be checked first?","Its local connection and IP configuration","Replace the office router immediately","Delete all network accounts","Change every device IP"),
q("Practical & Troubleshooting","What does ping commonly help test?","Basic IP reachability","Disk formatting","RAM capacity","Printer toner"),
q("Practical & Troubleshooting","Why should hardware troubleshooting be systematic?","It helps isolate the cause without unnecessary changes","Random replacement is always faster","Documentation is unnecessary","Every fault has the same cause"),

q("Training Ability","How should computer components be introduced to beginners?","Show real components and explain each function with hands-on identification","Use names only","Avoid opening training systems","Start with advanced server clusters"),
q("Training Ability","A student confuses a switch and router. What should a trainer do?","Use a simple network diagram and practical example of each role","Ask them to memorize definitions only","Skip networking","Tell them both are identical"),
q("Training Ability","What is an effective way to teach IP configuration?","Configure a safe lab network and verify connectivity","Use theory only","Change production networks without permission","Avoid troubleshooting"),
q("Training Ability","How should troubleshooting be taught?","Use symptoms, hypotheses, checks and verification in a repeatable process","Encourage random changes","Always replace hardware first","Ignore documentation"),
q("Training Ability","How can a trainer verify hardware skills?","Give a controlled practical task requiring identification or diagnosis","Ask only theoretical questions","Check handwriting","Ask whether the student understood"),

q("Professional Practice","Why should a computer be powered down appropriately before internal hardware work?","To reduce electrical and component risks","To increase internet speed","To update DNS","To improve spreadsheet formulas"),
q("Professional Practice","Why is documentation useful in network support?","It records configurations, changes and troubleshooting context","It replaces security controls","It makes IP addresses unnecessary","It prevents every failure"),
q("Professional Practice","Why should default device passwords be changed?","Default credentials can create security risk","They improve cooling","They reduce RAM usage","They are required for printing"),
q("Professional Practice","Before changing a production network configuration, what is good practice?","Understand impact, document, back up relevant configuration and use approved change procedures","Make random changes","Disable all logs","Remove existing documentation"),
q("Professional Practice","What should a technician do after fixing a fault?","Verify normal operation and document the resolution when appropriate","Leave without testing","Create another fault","Delete all logs"),
],

"hiring-aws-cloud-networking-trainer": [
q("Cloud Fundamentals","What is cloud computing?","On-demand access to computing resources delivered through networked services","A local keyboard feature","A spreadsheet formula","A monitor setting"),
q("Cloud Fundamentals","What is an AWS Region?","A geographic area containing AWS infrastructure locations","A single user account","A programming language","A local folder"),
q("Cloud Fundamentals","What is an Availability Zone?","An isolated infrastructure location within an AWS Region","A billing password","A DNS record only","A laptop partition"),
q("Cloud Fundamentals","Which AWS service provides resizable virtual compute instances?","Amazon EC2","Amazon S3","Amazon Route 53 only","Amazon SNS only"),
q("Cloud Fundamentals","Which AWS service is commonly used for object storage?","Amazon S3","Amazon EC2","Amazon VPC","Amazon IAM"),

q("AWS Networking","What is an Amazon VPC?","A logically isolated virtual network in AWS","A physical keyboard","An object-storage bucket","A programming framework"),
q("AWS Networking","What is a subnet?","A range of IP addresses within a VPC","An IAM password","An S3 object","A billing report"),
q("AWS Networking","What does a route table control?","Where network traffic from a subnet or gateway is directed","EC2 CPU speed","S3 file names","IAM usernames"),
q("AWS Networking","What is a security group used for?","Controlling allowed inbound and outbound traffic for associated resources","Creating S3 folders","Managing invoices","Compiling applications"),
q("AWS Networking","What is an Internet Gateway used for in a VPC?","Enable appropriate communication between VPC resources and the internet","Store objects","Create IAM users","Resize EBS volumes"),

q("Security & Reliability","What is AWS IAM primarily used for?","Managing identities and permissions","Designing webpages","Storing public videos only","Creating network cables"),
q("Security & Reliability","What does least privilege mean in AWS permissions?","Grant only permissions required for the task","Give AdministratorAccess to everyone","Share root credentials","Disable authentication"),
q("Security & Reliability","Why should the AWS root user be strongly protected?","It has highly privileged account-level capabilities","It cannot change anything","It is only for S3 uploads","It is a guest account"),
q("Security & Reliability","Why are multiple Availability Zones commonly used in resilient architectures?","To reduce dependence on a single infrastructure location","To remove all networking","To eliminate backups","To avoid permissions"),
q("Security & Reliability","What is a key cloud security principle?","Understand the shared responsibility model and secure what the customer controls","Assume the provider secures every customer configuration automatically","Make all resources public","Share credentials between users"),

q("Practical & Training","An EC2 instance should accept web traffic but not unrestricted administrative access. What should be configured carefully?","Security-group rules based on required ports and trusted sources","S3 object names","Billing currency","Instance tag colour"),
q("Practical & Training","A private subnet needs outbound internet access without accepting unsolicited inbound internet connections. What AWS component is commonly used?","NAT Gateway with appropriate routing","Public S3 bucket","IAM group","CloudWatch alarm only"),
q("Practical & Training","How should VPC concepts be taught to beginners?","Use a simple diagram showing VPC, subnets, routes and gateways, then build a lab","Start with a large production architecture","Teach service names only","Avoid practical configuration"),
q("Practical & Training","A student cannot connect to an EC2 service. What should they be encouraged to inspect?","Instance state, addressing, routes, security controls and service status systematically","Delete the account","Create random permissions","Disable all security"),
q("Practical & Training","What best verifies AWS networking understanding?","A controlled lab requiring students to build and explain a working network path","Memorizing service logos","Reading slides only","Checking typing speed"),

q("Operations & Industry","What is Amazon CloudWatch commonly used for?","Monitoring metrics, logs and alarms","Writing Java source code","Replacing IAM","Creating physical switches"),
q("Operations & Industry","Why are infrastructure changes ideally documented or managed as code?","They become more repeatable, reviewable and auditable","They eliminate every outage","They remove security requirements","They make backups unnecessary"),
q("Operations & Industry","Why should cloud costs be monitored?","Usage-based resources can create unexpected spending if unmanaged","AWS resources are always free","Billing never changes","Cost has no operational impact"),
q("Operations & Industry","Before deleting or replacing a production cloud resource, what should be checked?","Dependencies, data, backups, impact and approved change plan","Only its display name","Nothing if deletion is available","Whether the console is in dark mode"),
q("Operations & Industry","What is a sound approach to cloud architecture?","Balance security, reliability, performance, operations and cost for requirements","Always choose the largest resource","Make every service public","Ignore failure scenarios"),
],

"hiring-digital-marketing-ai-trainer": [
q("Marketing Fundamentals","What is a target audience?","The group of people a marketing effort is intended to reach","Every internet user automatically","Only existing employees","A website server"),
q("Marketing Fundamentals","What is a conversion in digital marketing?","A desired user action such as a lead, signup or purchase","Any page colour change","A computer restart","A domain renewal"),
q("Marketing Fundamentals","What is a call-to-action intended to do?","Encourage the audience toward a clear next step","Hide the offer","Increase file size","Replace analytics"),
q("Marketing Fundamentals","Why is a value proposition important?","It communicates why an offering is relevant or useful to the customer","It replaces product quality","It is only a logo","It guarantees sales"),
q("Marketing Fundamentals","What is a marketing funnel used to represent?","Stages people may move through from awareness toward conversion","A network topology","An accounting ledger","A programming loop"),

q("SEO Ads & Analytics","What does SEO aim to improve?","Relevant visibility in organic search results","Computer RAM","Email storage only","Printer quality"),
q("SEO Ads & Analytics","Why is search intent important in keyword research?","It helps align content with what users are trying to accomplish","It changes the domain extension","It guarantees first ranking","It removes competition"),
q("SEO Ads & Analytics","What is CTR commonly calculated as?","Clicks divided by impressions","Sales divided by staff","Cost divided by page count","Followers divided by passwords"),
q("SEO Ads & Analytics","What is a landing page commonly designed for?","A focused campaign objective or conversion action","Operating-system installation","Network routing","Database backup only"),
q("SEO Ads & Analytics","Why should campaign tracking be configured?","To measure performance and support better decisions","To make ads colourful","To eliminate marketing costs","To guarantee conversions"),

q("Social & Content","What makes content useful to an audience?","It addresses relevant needs, questions or interests","It uses the most hashtags possible","It is always long","It avoids a clear purpose"),
q("Social & Content","Why should content format vary by platform and audience?","User behavior and platform conventions differ","All platforms are identical","Formatting never matters","Only follower count matters"),
q("Social & Content","What is engagement rate intended to help measure?","Audience interaction relative to an appropriate exposure or audience measure","CPU performance","GST liability","Network latency"),
q("Social & Content","What is A/B testing used for?","Comparing variations to learn which performs better for a defined metric","Publishing random content","Avoiding analytics","Creating duplicate CRM leads"),
q("Social & Content","Why is a content calendar useful?","It supports planned, consistent and coordinated publishing","It guarantees viral posts","It replaces strategy","It removes the need for review"),

q("AI in Marketing","What is a good use of generative AI in marketing?","Assisting ideation and drafts that are reviewed and adapted by humans","Publishing every output without checking","Creating false customer claims","Uploading confidential data without consideration"),
q("AI in Marketing","Why should AI-generated marketing copy be reviewed?","It may contain errors, unsupported claims or unsuitable tone","AI output is legally guaranteed","Review always reduces quality","AI never makes factual mistakes"),
q("AI in Marketing","What improves an AI prompt for a marketing task?","Clear objective, audience, context, constraints and desired output","Only writing 'make it good'","Removing all context","Using unrelated keywords"),
q("AI in Marketing","What should be considered before giving customer data to an AI tool?","Privacy, permission, sensitivity and organizational policy","Only prompt length","Only font style","Nothing"),
q("AI in Marketing","How should AI support a marketer?","As a tool for productivity and analysis with human judgment and verification","As an unquestioned decision-maker","As a replacement for all measurement","As a source of guaranteed facts"),

q("Training & Professional Practice","How should SEO be introduced to beginners?","Connect search intent, useful content and basic technical factors using examples","Promise guaranteed number-one rankings","Teach keyword stuffing","Avoid search examples"),
q("Training & Professional Practice","What is an effective way to teach paid ads?","Use campaign objectives, audience, creative, budget and measurement in a controlled example","Focus only on the boost button","Ignore conversion tracking","Promise fixed returns"),
q("Training & Professional Practice","A student reports high clicks but few leads. What should a trainer encourage them to inspect?","Traffic relevance, landing-page experience and conversion tracking","Only logo size","Only follower count","Computer storage"),
q("Training & Professional Practice","What best checks digital-marketing understanding?","Give a business scenario and ask the learner to design and justify a measurable campaign","Ask only definitions","Check typing speed","Ask whether they use social media"),
q("Training & Professional Practice","What should ethical marketing avoid?","Misleading claims, fabricated evidence and deceptive practices","Clear disclosures","Accurate measurement","Customer-focused communication"),
],

})

def seed_assessment(slug, questions):
    assessment = Assessment.objects.get(
        slug=slug,
        assessment_type="hiring",
    )

    if len(questions) != 25:
        raise ValueError(
            f"{slug}: expected 25 questions, got {len(questions)}"
        )

    for order, item in enumerate(questions, start=1):
        category, text, options, correct_index = item

        if len(options) != 4:
            raise ValueError(
                f"{slug} Q{order}: expected 4 options"
            )

        if correct_index not in (0, 1, 2, 3):
            raise ValueError(
                f"{slug} Q{order}: invalid correct_index"
            )

        question, _ = AssessmentQuestion.objects.update_or_create(
            assessment=assessment,
            order=order,
            defaults={
                "question_text": text,
                "category": category,
                "marks": 1,
                "is_active": True,
            },
        )

        for option_order, option_text in enumerate(options, start=1):
            AssessmentOption.objects.update_or_create(
                question=question,
                order=option_order,
                defaults={
                    "option_text": option_text,
                    "is_correct": (
                        option_order - 1 == correct_index
                    ),
                },
            )

    return assessment


def audit(assessment):
    questions = assessment.questions.filter(is_active=True)

    invalid = []

    for question in questions:
        options = question.options.all()

        if (
            options.count() != 4
            or options.filter(is_correct=True).count() != 1
        ):
            invalid.append(question.order)

    return {
        "questions": questions.count(),
        "options": AssessmentOption.objects.filter(
            question__assessment=assessment,
            question__is_active=True,
        ).count(),
        "correct": AssessmentOption.objects.filter(
            question__assessment=assessment,
            question__is_active=True,
            is_correct=True,
        ).count(),
        "invalid": invalid,
    }


if not QUESTION_BANKS:
    print("MASTER HIRING BUILDER READY")
    print("Question banks not loaded yet.")
else:
    total_questions = 0

    for slug, questions in QUESTION_BANKS.items():
        assessment = seed_assessment(slug, questions)
        result = audit(assessment)

        if (
            result["questions"] != 25
            or result["options"] != 100
            or result["correct"] != 25
            or result["invalid"]
        ):
            raise RuntimeError(
                f"{slug} FAILED AUDIT: {result}"
            )

        total_questions += result["questions"]

        print(
            f"OK | {slug} | "
            f"Q={result['questions']} | "
            f"Options={result['options']} | "
            f"Correct={result['correct']}"
        )

    print("=" * 60)
    print("ASSESSMENTS BUILT:", len(QUESTION_BANKS))
    print("QUESTIONS BUILT:", total_questions)
    print("ALL QUESTION BANKS PASSED AUDIT")
