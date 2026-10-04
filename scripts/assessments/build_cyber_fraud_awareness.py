from assessments.models import Assessment, AssessmentQuestion, AssessmentOption

TITLE = "MCTI Cyber Fraud Awareness Test 2026"
SLUG = "mcti-cyber-fraud-awareness-2026"

assessment, created = Assessment.objects.get_or_create(
    slug=SLUG,
    defaults={
        "title": TITLE,
        "assessment_type": "awareness",
        "description": (
            "Free cyber fraud awareness test by MCTI. "
            "Learn to identify common digital scams and safer online practices."
        ),
        "is_active": True,
    }
)

changed = False

if assessment.title != TITLE:
    assessment.title = TITLE
    changed = True

if not assessment.is_active:
    assessment.is_active = True
    changed = True

if changed:
    assessment.save()

QUESTIONS = [
(
"Someone calls claiming to be from your bank and asks for your OTP to stop a suspicious transaction. What should you do?",
[
"Share the OTP quickly",
"Share only half of the OTP",
"Do not share the OTP and contact the bank through an official channel",
"Send the OTP by SMS instead"
],
2,
"Never share OTP, PIN, password or other confidential banking credentials with callers."
),
(
"You receive a QR code and are told to scan it and enter your UPI PIN to receive money. What is the safest response?",
[
"Scan it because QR codes are always safe",
"Enter the UPI PIN because it is needed to receive money",
"Do not proceed; receiving money normally does not require entering your UPI PIN",
"Forward the QR code to friends first"
],
2,
"Be cautious with unknown QR codes. A UPI PIN is used to authorize transactions, not simply to receive money."
),
(
"A message says your bank KYC will expire today and gives a link for urgent verification. What should you do?",
[
"Open the link immediately",
"Enter your banking password on the page",
"Verify the request using the bank's official app, website or customer-care channel",
"Forward the message to family"
],
2,
"Urgency and fake KYC links are common phishing techniques. Verify independently using official channels."
),
(
"A caller claiming to be customer support asks you to install a screen-sharing app. What should you do?",
[
"Install it and give full access",
"Install it only for five minutes",
"Avoid installing it and contact the company through its official support channel",
"Share your screen but hide your gallery"
],
2,
"Remote-access and screen-sharing tools can expose sensitive information or allow control of your device."
),
(
"You receive an unexpected link saying you have won a large prize. What is the safest action?",
[
"Click immediately",
"Enter your bank details to claim it",
"Do not click; independently verify the sender and offer",
"Share it in a group first"
],
2,
"Unexpected prize messages commonly use phishing links or requests for personal information."
),
(
"Which information should never be shared with an unknown caller?",
[
"Your favourite colour",
"OTP, PIN, password or CVV",
"Your city name",
"Your preferred language"
],
1,
"Banking credentials such as OTP, PIN, password and CVV must be protected."
),
(
"A person claiming to be a police officer says you are under 'digital arrest' and must transfer money immediately. What should you do?",
[
"Transfer money immediately",
"Stay on the video call until they allow you to leave",
"Do not transfer money; independently contact legitimate authorities and report suspicious activity",
"Give them your banking password"
],
2,
"Threats, urgency and demands for money should be independently verified through legitimate official channels."
),
(
"You accidentally sent money to a suspected fraudster. What should you do first?",
[
"Wait until tomorrow",
"Delete all messages",
"Immediately contact your bank/payment provider and report the financial cyber fraud through 1930 or the National Cyber Crime Reporting Portal",
"Post only on social media"
],
2,
"Rapid reporting can help authorities and financial institutions respond to financial cyber fraud."
),
(
"What is phishing?",
[
"A method of charging a phone",
"A fraudulent attempt to trick people into revealing information or visiting malicious links",
"A type of computer monitor",
"A banking reward programme"
],
1,
"Phishing attempts often impersonate trusted organisations to steal information or trigger unsafe actions."
),
(
"What is a strong password practice?",
[
"Use the same password everywhere",
"Use your mobile number as your password",
"Use a strong unique password for important accounts",
"Share passwords with close friends"
],
2,
"Unique passwords reduce the impact if one account or service is compromised."
),
(
"You receive an unexpected APK/app file through WhatsApp claiming to be from a bank. What should you do?",
[
"Install it immediately",
"Install it after forwarding it to a friend",
"Do not install it; use the bank's official app/source",
"Disable phone security and install it"
],
2,
"Unexpected app files can be malicious. Use trusted official sources."
),
(
"A job offer asks you to pay a registration fee before any interview. What is the safest approach?",
[
"Pay immediately to reserve the job",
"Verify the employer independently before paying or sharing sensitive information",
"Send your banking PIN",
"Borrow money and pay quickly"
],
1,
"Unexpected job offers requesting money or sensitive information should be independently verified."
),
(
"Someone on social media impersonates your friend and urgently asks for money. What should you do?",
[
"Send money immediately",
"Verify with your friend through another trusted contact method",
"Send your OTP instead",
"Ignore all future messages from your friend"
],
1,
"Account impersonation can be used for fraud. Verify unusual requests independently."
),
(
"What should you check before entering credentials on a website?",
[
"Only the website colour",
"The address/domain and whether you reached the genuine official service",
"How many advertisements it has",
"Whether it has a large logo"
],
1,
"Fake websites may imitate trusted brands. Check that you are using the genuine service."
),
(
"A caller knows your name and some account details. Does that prove the caller is genuine?",
[
"Yes, always",
"Yes, if they sound professional",
"No; personal information can be obtained from leaks or other sources",
"Yes, if they call twice"
],
2,
"Knowing some personal details does not prove that a caller represents a legitimate organisation."
),
(
"What should you do if a suspicious payment request appears in your UPI app?",
[
"Approve it to see what happens",
"Enter your PIN",
"Decline it and verify independently if necessary",
"Approve and request a refund later"
],
2,
"Do not authorize unexpected payment or collect requests."
),
(
"A stranger promises guaranteed very high investment returns with no risk. What should you do?",
[
"Invest immediately",
"Share the offer with everyone",
"Treat it cautiously and verify the entity and claims before taking any action",
"Give them remote access to your banking app"
],
2,
"Unrealistic or guaranteed-return claims can be a warning sign of fraud."
),
(
"Why is two-factor authentication useful?",
[
"It makes the screen brighter",
"It adds an additional layer of account protection",
"It automatically shares passwords",
"It removes the need for security"
],
1,
"Additional authentication can make account takeover harder even if a password is compromised."
),
(
"If your phone with banking apps is lost, what is a sensible immediate action?",
[
"Do nothing for several days",
"Act quickly to secure relevant accounts/SIM and contact appropriate service providers",
"Post your banking password online",
"Wait for the phone battery to finish"
],
1,
"Promptly securing accounts and communication access can reduce risk after device loss."
),
(
"A link received by SMS looks almost identical to your bank's website. What should you do?",
[
"Trust it because the logo is correct",
"Use the link because it arrived by SMS",
"Open the bank through its official app or independently entered official website instead",
"Enter only your PIN"
],
2,
"Branding can be copied. Avoid relying on unsolicited links for sensitive banking activity."
),
(
"Which behaviour is safest on public or shared computers?",
[
"Save banking passwords in the browser",
"Leave your account logged in",
"Avoid sensitive transactions where possible and always sign out",
"Share your password with the computer owner"
],
2,
"Shared devices can expose sessions or credentials."
),
(
"What should you do with evidence after a cyber fraud?",
[
"Delete all messages immediately",
"Keep relevant transaction details, messages, screenshots and other evidence for reporting",
"Factory-reset every device before reporting",
"Only tell friends"
],
1,
"Relevant records can help when reporting a cyber incident or financial fraud."
),
(
"What is the National Cyber Crime Helpline number for reporting financial cyber fraud in India?",
[
"100",
"108",
"1930",
"101"
],
2,
"1930 is the National Cyber Crime Helpline for immediate reporting of financial cyber fraud."
),
(
"Where can cybercrime be reported online in India?",
[
"Only on social media",
"National Cyber Crime Reporting Portal",
"Any random forum",
"Only by email to friends"
],
1,
"The Government of India's National Cyber Crime Reporting Portal provides online cybercrime reporting facilities."
),
(
"Which mindset provides the best protection against many cyber fraud attempts?",
[
"Act immediately whenever a message creates urgency",
"Trust anyone who knows your name",
"Pause, verify independently, and never disclose sensitive credentials",
"Install every app recommended by callers"
],
2,
"Pausing and independently verifying unexpected requests helps resist urgency, impersonation and social-engineering tactics."
),
]

existing = {
    q.order: q
    for q in assessment.questions.all()
}

for order, (text, options, correct, explanation) in enumerate(QUESTIONS, start=1):

    q = existing.get(order)

    defaults = {
        "question_text": text,
        "is_active": True,
        "marks": 1,
        "order": order,
        "question_origin": "mcti_practice",
        "source_name": "MCTI Cyber Fraud Awareness - based on public cyber-safety guidance",
        "source_reference": "RBI / CERT-In / National Cyber Crime Reporting Portal",
    }

    if q is None:
        q = AssessmentQuestion.objects.create(
            assessment=assessment,
            **defaults
        )
    else:
        for field, value in defaults.items():
            setattr(q, field, value)
        q.save()

    option_objects = list(
        AssessmentOption.objects
        .filter(question=q)
        .order_by("id")
    )

    for idx, option_text in enumerate(options):

        is_correct = idx == correct

        if idx < len(option_objects):
            opt = option_objects[idx]
            opt.option_text = option_text
            opt.is_correct = is_correct
            opt.save(
                update_fields=["option_text", "is_correct"]
            )
        else:
            AssessmentOption.objects.create(
                question=q,
                option_text=option_text,
                is_correct=is_correct
            )

    # Remove only surplus options for THIS newly managed question.
    option_objects = list(
        AssessmentOption.objects
        .filter(question=q)
        .order_by("id")
    )

    if len(option_objects) > 4:
        for extra in option_objects[4:]:
            extra.delete()

# Do not delete historical questions/attempts.
assessment.questions.filter(
    order__gt=len(QUESTIONS)
).update(is_active=False)

print("=" * 55)
print("MCTI CYBER FRAUD AWARENESS TEST READY")
print("=" * 55)
print("Assessment ID:", assessment.id)
print("Slug:", assessment.slug)
print(
    "Active Questions:",
    assessment.questions.filter(is_active=True).count()
)
print(
    "Options:",
    AssessmentOption.objects.filter(
        question__assessment=assessment,
        question__is_active=True
    ).count()
)
print("=" * 55)
