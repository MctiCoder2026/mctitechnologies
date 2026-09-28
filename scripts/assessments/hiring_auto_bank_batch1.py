def q(question, correct, wrong1, wrong2, wrong3):
    return (question, [correct, wrong1, wrong2, wrong3], 0)


AUTO_BANKS_BATCH1 = {

"hiring-full-stack-development-trainer": {
"practical": [
q("A responsive page looks correct on desktop but breaks on mobile. What should you inspect first?","Viewport settings and responsive CSS rules","Database indexes","Git username","Server timezone"),
q("A form submits successfully but no record is saved. What should you inspect first?","Request handling, validation and database save logic","Logo dimensions","Browser bookmarks","Monitor resolution"),
q("A JavaScript click handler does not run. What is the best first check?","Browser console errors and event binding","Database password","CSS font family","Server disk name"),
q("An API returns HTTP 500. What should the developer inspect first?","Server logs and the failing request path","Homepage colours","Browser history","Image resolution"),
q("A protected dashboard opens without login. What should be checked?","Authentication and authorization logic","CSS margins","Database table colour","HTML heading size"),
q("A database query becomes slow as data grows. What is a useful investigation?","Query plan, filtering and appropriate indexes","Changing the website logo","Removing validation","Increasing font size"),
q("A new deployment breaks a previously working feature. What is the best response?","Investigate logs and changes, restore service safely, then fix and retest","Delete the repository","Ignore users","Change random production files"),
q("Frontend data is not appearing although the API works in direct testing. What should be inspected?","Network request, response handling and frontend state/rendering","Printer configuration","Database table names only","Keyboard settings"),
q("Two developers modify the same code and Git reports a conflict. What should they do?","Review both changes and resolve the conflict deliberately","Delete both branches","Overwrite everything without review","Stop using version control"),
q("Before releasing a full-stack feature, what is strongest practice?","Test UI, server logic, validation, permissions and important existing flows","Check only the homepage","Deploy without testing","Remove error handling"),
],
"communication": [
q("A beginner cannot understand client versus server. What is the best explanation?","Use a simple request-response example and demonstrate it","Start with distributed systems theory","Ask them to memorize definitions","Skip the topic"),
q("A student copies React code but cannot explain state. What should the trainer do?","Use a small example and ask the student to predict and modify state changes","Give more code to copy","Mark the topic complete","Avoid questions"),
q("A student's web project has many errors. What is the best trainer approach?","Help them isolate one problem at a time and explain the debugging process","Rewrite the whole project for them","Tell them to start another course","Ignore the errors"),
q("How should Git be taught effectively?","Use a small repository with real commits, branches and recovery examples","Teach commands only from slides","Avoid practical work","Give a completed repository"),
q("A student asks a question you cannot answer confidently. What should you do?","Say you will verify it and return with an accurate explanation","Invent an answer","Criticize the question","Change the topic permanently"),
q("How can a trainer check whether students understand APIs?","Give them a small API task and ask them to explain request and response behavior","Ask only if they understood","Check typing speed","Check attendance"),
q("Students have different coding speeds. What is an effective class strategy?","Use core guided tasks plus extension challenges and targeted support","Teach only fast students","Stop practical sessions","Give everyone final code"),
q("A student receives a 404 error. What should the trainer encourage first?","Trace the requested URL and routing configuration systematically","Reinstall the operating system","Change CSS","Ignore the error"),
q("What makes a live coding demonstration effective?","Explain reasoning, test assumptions and discuss errors as they occur","Paste final code silently","Hide all errors","Avoid student questions"),
q("A student is losing confidence in programming. What should the trainer do?","Break tasks into achievable steps and build confidence through guided practice","Tell them coding is not suitable for them","Give only advanced projects","Complete all work for them"),
],
},

"hiring-cyber-security-trainer": {
"practical": [
q("A workstation may be infected with malware. What is an appropriate initial action?","Isolate it as appropriate and follow the approved incident-response process","Connect it to more systems","Delete all logs","Share the suspicious file"),
q("Repeated failed administrator logins appear in logs. What should be done?","Investigate the source and apply appropriate account and network protections","Delete the logs","Disable authentication","Share the admin password"),
q("Before conducting a penetration test, what must be confirmed?","Explicit authorization and defined scope","Only internet speed","A public target","Anonymous access"),
q("A user reports entering credentials on a suspected phishing page. What should happen promptly?","Follow the approved account-security and incident-response procedure","Ignore it until next month","Publish the credentials","Delete unrelated systems"),
q("A firewall rule unexpectedly exposes an internal service. What should be done?","Assess and correct the rule through approved change and incident procedures","Leave it exposed","Disable all firewalls","Share the service publicly"),
q("A security alert indicates unusual outbound traffic. What is the best next step?","Investigate affected systems, logs and network activity using approved procedures","Delete all evidence","Ignore the alert","Restart random devices"),
q("A critical vulnerability is reported in software used by the organization. What should the team do?","Assess exposure and apply appropriate mitigation or patching through controlled procedures","Ignore all advisories","Publish internal credentials","Disable backups"),
q("An employee requests administrator access for convenience. What principle should guide the decision?","Least privilege based on legitimate job requirements","Everyone should be administrator","Passwords should be shared","Logging should be disabled"),
q("During an authorized security test you discover sensitive data outside the expected task. What should you do?","Stay within scope, protect the data and report appropriately","Copy it for personal use","Publish it","Continue exploring without authorization"),
q("After a security incident is contained, what is an important next activity?","Document findings, determine causes and improve controls where appropriate","Delete all records","Hide the incident","Remove monitoring"),
],
"communication": [
q("How should ethical hacking be introduced to beginners?","Start with authorization, scope, defensive purpose and safe labs","Start by attacking public systems","Ignore legal boundaries","Share real credentials"),
q("A student asks to test an unrelated company's website. What should the trainer say?","Use only systems explicitly authorized for training and testing","Any public website is acceptable","Permission is unnecessary for students","Use anonymous tools instead"),
q("A beginner confuses authentication and authorization. What is the best teaching approach?","Use a simple example showing identity verification versus permitted actions","Say they are identical","Skip the difference","Give definitions without examples"),
q("How should phishing awareness be taught safely?","Use controlled examples and teach students to recognize warning signs","Send real malicious attachments","Collect student passwords","Use live victims"),
q("A student makes an unsafe suggestion during a lab. What should the trainer do?","Correct it immediately and reinforce safe, authorized procedures","Encourage experimentation on public targets","Ignore it","Remove all safety rules"),
q("How can a trainer verify understanding of network security?","Give a safe scenario and ask the learner to select and justify defensive controls","Ask only yes or no","Check attendance","Ask them to memorize tool names"),
q("A student is overwhelmed by security terminology. What should the trainer do?","Introduce concepts progressively with simple examples and practical demonstrations","Add more jargon","Skip fundamentals","Give advanced exploit material immediately"),
q("What is an effective way to teach incident response?","Use a controlled scenario requiring detection, containment, evidence handling and reporting","Teach only definitions","Avoid scenarios","Remove documentation"),
q("A student asks a security question outside your expertise. What is the best response?","Acknowledge the limit, verify reliable information and follow up","Invent a technical answer","Dismiss the student","Change the subject"),
q("What should a cyber-security trainer consistently model?","Responsible, legal, evidence-based and security-conscious professional behavior","Unauthorized experimentation","Credential sharing","Disabling audit trails"),
],
},

"hiring-java-trainer": {
"practical": [
q("A Java application throws NullPointerException. What should be inspected first?","The stack trace and the reference that is null","Monitor brightness","CSS files","Printer settings"),
q("A loop never terminates. What should be checked?","The termination condition and updates to controlling variables","The package name colour","JDK logo","Screen resolution"),
q("A program fails to compile after a code change. What is the best first step?","Read the compiler error and inspect the referenced code","Delete the JDK","Rewrite the entire project","Ignore the compiler"),
q("A collection must prevent duplicate values. Which structure is commonly appropriate?","A Set implementation when its semantics fit the requirement","ArrayList only","StringBuilder","Scanner"),
q("You need fast lookup of values using unique keys. Which structure is commonly suitable?","A Map such as HashMap when ordering requirements permit","A plain String","Thread only","Exception"),
q("A database connection is opened repeatedly but not released. What problem may result?","Resource exhaustion or connection leaks","Improved performance automatically","CSS errors","Duplicate Java classes"),
q("A method contains the same logic copied in several places. What is a good improvement?","Refactor reusable behavior into an appropriate method or component","Copy it more times","Remove method names","Use only global state"),
q("A Java web API accepts invalid input and later fails. What should be improved?","Input validation and controlled error handling","Logo design","Browser bookmarks","Monitor size"),
q("Before updating a production Java application, what is good practice?","Test the change and important existing behavior with versioned deployment procedures","Edit production blindly","Delete source history","Disable backups"),
q("What best demonstrates practical Java development ability?","Building, debugging and explaining a small working application feature","Memorizing keywords only","Knowing the Java logo","Copying code without understanding"),
],
"communication": [
q("How should classes and objects be explained to beginners?","Use a simple blueprint-and-instance example followed by code","Start with advanced reflection","Give definitions only","Skip objects"),
q("A student understands syntax but struggles with OOP. What should the trainer do?","Use small real-world models and progressively build classes and relationships","Give more syntax to memorize","Skip OOP","Move directly to frameworks"),
q("A student's code throws an exception. What should the trainer encourage?","Read the stack trace and reason from the failure location","Delete the project","Ignore the exception","Copy another solution"),
q("How can a trainer verify understanding of inheritance?","Ask the student to design and explain a small parent-child class example","Ask only whether they understood","Check typing speed","Show the same slide"),
q("What is an effective way to teach collections?","Compare structures through practical data-handling problems","Teach method names only","Avoid coding","Use screenshots only"),
q("A student copies code from the internet that works but cannot explain it. What should the trainer do?","Ask them to explain, modify and test the code before accepting the solution","Mark it complete immediately","Encourage more copying","Ignore understanding"),
q("Students have mixed Java skill levels. What should the trainer do?","Use common core exercises with extension tasks and targeted support","Teach only experienced students","Remove practicals","Give all solutions first"),
q("A student asks why interfaces are useful. What is the best approach?","Demonstrate a small design where multiple implementations follow the same contract","Ask them to memorize the definition","Say they are always required","Skip the question"),
q("During live coding, the trainer makes an error. What is the best response?","Debug it transparently and demonstrate a systematic problem-solving process","Hide the error","End the class","Blame the software"),
q("A student is frustrated by repeated Java errors. What should the trainer do?","Break the problem into smaller steps and guide the student toward the solution","Tell them to quit Java","Complete every task for them","Ignore them"),
],
},

}
