def q(question, correct, wrong1, wrong2, wrong3):
    return (question, [correct, wrong1, wrong2, wrong3], 0)


AUTO_BANKS_BATCH3 = {

"hiring-hardware-networking-trainer": {
"practical": [
q("A desktop powers on but shows no display. What should be checked first?","Power, display connections, monitor input and basic hardware indicators systematically","Reinstall every application","Format the disk immediately","Change the wallpaper"),
q("A computer repeatedly overheats and shuts down. What should be investigated?","Cooling, airflow, fans, dust and thermal conditions","Keyboard language","Desktop icons","Printer queue"),
q("A PC cannot access the network while nearby systems can. What is a useful first check?","Its physical connection and IP configuration","Monitor resolution","CPU cabinet colour","Document formatting"),
q("A user can reach devices by IP address but not by hostname. What should be investigated?","DNS or name-resolution configuration","RAM colour","Printer toner","Keyboard layout"),
q("A newly installed RAM module causes boot problems. What should be checked?","Compatibility, seating and diagnostic results","Browser bookmarks","IP address only","Desktop background"),
q("A network printer is unreachable from multiple PCs. What should be checked?","Printer connectivity, network configuration and reachability","Excel formulas","CPU temperature of every PC","Website CSS"),
q("A workstation receives a 169.254.x.x address instead of the expected network address. What should be investigated?","DHCP availability and network connectivity","Screen brightness","Audio settings","Browser cache only"),
q("Two devices have accidentally been configured with the same IP address. What problem can result?","An IP address conflict causing unreliable connectivity","Automatic bandwidth increase","More storage space","Improved DNS"),
q("Before replacing a suspected failed hardware component, what is good practice?","Diagnose systematically and confirm the likely cause","Replace every component","Format all drives","Disable backups"),
q("What best demonstrates practical hardware and networking ability?","Diagnosing a realistic fault systematically and explaining the resolution","Memorizing component names only","Knowing cable colours only","Reinstalling Windows for every problem"),
],
"communication": [
q("How should computer hardware be introduced to beginners?","Use real components and explain their purpose with practical demonstrations","Give model numbers only","Avoid opening a computer","Teach definitions without examples"),
q("A student confuses RAM with storage. What should the trainer do?","Use a simple comparison and demonstrate their different roles","Say they are identical","Skip the topic","Ask them to memorize abbreviations"),
q("How should IP addressing be taught effectively?","Combine a simple network diagram with configuration and connectivity practice","Teach numbers only","Avoid practical configuration","Start only with advanced routing"),
q("A student cannot diagnose a network problem. What should the trainer encourage?","Use a structured troubleshooting sequence from basic connectivity upward","Change random settings","Format the PC","Guess the cause"),
q("During a hardware practical, a student is handling components unsafely. What should the trainer do?","Stop the unsafe action and demonstrate proper handling procedures","Ignore it","Encourage faster handling","Remove all safety guidance"),
q("How can a trainer verify networking understanding?","Give a small network problem and ask the student to diagnose and explain it","Ask only if they understood","Check typing speed","Check attendance"),
q("A student asks why a ping fails. What is the best teaching approach?","Walk through possible layers and test relevant causes systematically","Give one fixed answer for every failure","Reinstall the OS immediately","Ignore the question"),
q("Students have different hardware experience levels. What should the trainer do?","Use core practical tasks with additional challenges and targeted support","Teach only experienced students","Avoid practical work","Give everyone the answers"),
q("A trainer encounters an unfamiliar hardware fault. What should they do?","Diagnose carefully, consult reliable technical information and avoid pretending certainty","Invent a cause","Replace random parts","Tell students hardware faults cannot be investigated"),
q("What should a hardware trainer emphasize alongside technical skill?","Safety, systematic troubleshooting, documentation and responsible equipment handling","Speed alone","Guesswork","Changing settings without records"),
],
},

"hiring-aws-cloud-networking-trainer": {
"practical": [
q("An EC2 instance is running but cannot be reached over the expected port. What should be checked?","Security rules, network path, instance configuration and service availability","Dashboard colour","S3 bucket name only","Keyboard settings"),
q("A private server needs outbound internet access without accepting unsolicited inbound internet connections. What AWS networking component is commonly considered?","A NAT gateway or appropriate NAT design","An internet-facing database password","A public S3 object","A larger instance name"),
q("Two VPC subnets need different routing behavior. What should be configured appropriately?","Route tables associated with the relevant subnets","IAM usernames only","CloudWatch dashboard colours","EC2 tags only"),
q("A website must remain available if one application instance fails. What architecture principle should be applied?","Redundancy across appropriate resources with health-aware traffic distribution","Use one server only","Disable monitoring","Store all backups on the same instance"),
q("An AWS resource should be accessible only by users who need it. What principle should guide permissions?","Least privilege","Give AdministratorAccess to everyone","Share the root account","Disable authentication"),
q("Application performance suddenly degrades. What is a useful first cloud troubleshooting step?","Review relevant metrics, logs, recent changes and resource health","Resize randomly without evidence","Delete monitoring data","Change the AWS console language"),
q("A production database requires protection against accidental data loss. What should be considered?","Appropriate backups, recovery strategy, access controls and tested restoration procedures","Only changing the database name","Removing snapshots","Sharing credentials"),
q("A cloud bill unexpectedly increases. What should be investigated?","Usage, resource changes, pricing dimensions and cost-monitoring data","Website font size","User profile photos","Local printer settings"),
q("A public cloud storage bucket contains confidential files. What should be done?","Correct access controls promptly and review exposure according to incident procedures","Leave it public","Post the link internally and externally","Disable logging"),
q("Before making a major AWS production change, what is good practice?","Assess impact, test appropriately, document the change and maintain rollback or recovery capability","Change production without review","Delete backups first","Disable monitoring"),
],
"communication": [
q("How should cloud computing be introduced to beginners?","Use a simple comparison between local infrastructure and on-demand cloud resources","Start with complex multi-region architecture","Teach service names only","Avoid examples"),
q("A student confuses a public subnet with a private subnet. What should the trainer do?","Use a network diagram and explain routing and exposure with a practical example","Say the names alone explain everything","Skip routing","Ask them to memorize definitions"),
q("How should IAM be taught effectively?","Use users, roles, permissions and least-privilege scenarios in a controlled environment","Give everyone administrator access","Share one account","Avoid permission exercises"),
q("A student deploys an instance but cannot connect to it. What should the trainer encourage?","Troubleshoot networking, access rules, credentials and service state systematically","Delete the account","Create random instances","Change unrelated settings"),
q("What is an effective way to teach AWS networking?","Build a small VPC scenario and trace traffic through subnets, routes and security controls","Teach service logos","Avoid diagrams","Use definitions only"),
q("How can a trainer verify cloud understanding?","Give an architecture requirement and ask the student to design and justify a solution","Ask only whether they understood","Check typing speed","Ask them to memorize AWS service names"),
q("A student asks which AWS service is always best. What should the trainer explain?","Service choice depends on requirements, constraints, security, reliability and cost","The newest service is always best","The most expensive service is always best","Choose randomly"),
q("During a cloud demo, deployment fails unexpectedly. What should the trainer do?","Troubleshoot transparently using logs and configuration while explaining the reasoning","Hide the error","End the class immediately","Blame the student"),
q("What should students learn about cloud cost alongside deployment?","Resources have cost implications and should be monitored and designed responsibly","Cloud resources are always free","Cost never affects architecture","Only finance teams need to know"),
q("What professional habit should an AWS trainer model?","Secure, documented and evidence-based configuration and troubleshooting","Using root credentials for daily work","Sharing secrets","Making undocumented production changes"),
],
},

"hiring-digital-marketing-ai-trainer": {
"practical": [
q("A paid campaign receives many clicks but very few enquiries. What should be investigated first?","Traffic relevance, campaign targeting, landing-page experience and conversion tracking","Logo colour only","Follower count only","Computer RAM"),
q("A website ranks for keywords that bring irrelevant visitors. What should be reviewed?","Search intent, keyword targeting and content relevance","Printer settings","Domain logo size","Email signature"),
q("An ad platform reports conversions but CRM shows far fewer genuine leads. What should be checked?","Conversion definitions, tracking implementation and lead-quality data","Increase reported conversions manually","Ignore CRM data","Change the campaign name"),
q("A landing page has strong traffic but poor form submissions. What is a sensible approach?","Review message relevance, user experience, trust, form friction and measurement","Add random animations","Remove analytics","Assume traffic is the only goal"),
q("A campaign's cost per lead rises sharply. What should the marketer investigate?","Recent changes in audience, competition, creative, bidding, landing page and tracking","Only office internet speed","Employee attendance","Website footer colour"),
q("AI-generated ad copy contains an unsupported claim. What should be done?","Correct or remove the claim and verify the final copy before publishing","Publish it because AI wrote it","Make the claim stronger","Remove all human review"),
q("Customer data is being considered for use in an AI marketing tool. What should be checked first?","Privacy, permission, sensitivity, security and organizational policy","Only prompt length","Only follower count","Nothing"),
q("A social campaign has high engagement but no business outcome. What should be reviewed?","Whether objectives, audience, call-to-action and measurement align with the intended outcome","Only number of emojis","Computer storage","Post colour"),
q("Two landing-page versions need to be compared fairly. What technique is appropriate?","A controlled A/B test with a defined metric","Change both versions continuously","Choose the prettier page","Ask one employee"),
q("Before reporting marketing ROI, what should be verified?","Reliable cost, attribution and outcome data with clearly defined calculations","Only impressions","Only likes","Only follower growth"),
],
"communication": [
q("How should SEO be introduced to beginners?","Connect user search intent, useful content and basic technical factors using practical examples","Promise guaranteed first ranking","Teach keyword stuffing","Avoid search examples"),
q("A student believes more social-media followers always means better marketing. What should the trainer explain?","Metrics should be connected to objectives, audience quality and meaningful outcomes","Followers are the only metric","Analytics is unnecessary","Every follower becomes a customer"),
q("How should paid advertising be taught effectively?","Use a controlled campaign example covering objective, audience, creative, budget and measurement","Teach only the boost button","Promise guaranteed returns","Ignore tracking"),
q("A student asks AI to create an entire campaign and wants to publish it unchanged. What should the trainer teach?","AI output requires human review, factual verification, brand judgment and performance testing","AI output should always be published directly","Human review reduces quality","Analytics is unnecessary with AI"),
q("How can a trainer verify digital-marketing understanding?","Give a business scenario and ask the student to design and justify a measurable campaign","Ask only definitions","Check typing speed","Ask how many apps they use"),
q("A student's campaign performs poorly. What should the trainer encourage?","Analyze evidence, form a hypothesis, test improvements and measure results","Change everything randomly","Hide the poor results","Blame the platform immediately"),
q("A student wants to guarantee a client a number-one Google ranking. What should the trainer explain?","Avoid unsupported guarantees and communicate realistic, evidence-based expectations","Guarantee it to close the sale","Create fake reports","Ignore search guidelines"),
q("What is an effective way to teach analytics?","Use real or realistic campaign data and ask students to interpret metrics in context","Teach metric names only","Avoid datasets","Focus only on colourful charts"),
q("A student asks which marketing channel is always best. What should the trainer explain?","Channel choice depends on audience, objective, offer, budget and evidence","One channel is always best","Always choose the most expensive platform","Choose based only on popularity"),
q("What professional behavior should a digital-marketing trainer model?","Accurate claims, ethical practices, measurement, experimentation and responsible AI use","Fake testimonials","Hidden conditions","Publishing unverified AI content"),
],
},

}
