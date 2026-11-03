/* MCTI Enquiry WhatsApp Languages V1 */
(function () {
"use strict";

const translations = {
  mr: {
    welcome: ({name, institute, course, courseDetailsUrl, location, signoff}) =>
`नमस्कार *${name}* 👋

*${institute}* शी संपर्क साधल्याबद्दल धन्यवाद.

🎓 *तुमचे करिअर, आमची बांधिलकी.*

⭐ नवी मुंबईतील आमच्या केंद्रांना 2,250+ Google Reviews मिळाले आहेत.

आम्ही तुम्हाला खालील बाबींमध्ये मार्गदर्शन करू:
✅ करिअरसाठी उपयुक्त संगणक अभ्यासक्रम
✅ कोर्स फी आणि बॅचच्या वेळा
✅ करिअर समुपदेशन आणि कौशल्य विकास

📚 *तुम्ही चौकशी केलेला कोर्स: ${course}*

अभ्यासक्रम आणि करिअरच्या संधी पाहा:
🔗 ${courseDetailsUrl}

🧠 *मोफत करिअर ॲप्टिट्यूड टेस्ट*
https://mctitechnologies.com/career/aptitude/start/

📍 *आमच्या केंद्राला भेट द्या*
${location}

📅 भेटीसाठी सोयीचा दिवस आणि वेळ कळवा.

${signoff}`,

    appointment: ({name, course, date, time, location, signoff}) =>
`नमस्कार ${name},

*${course}* साठी तुमची समुपदेशन भेट निश्चित झाली आहे.

📅 ${date}
⏰ ${time}

${location}

कृपया 5–10 मिनिटे आधी या आणि भेटीची पुष्टी करा.

${signoff}`,

    afterVisit: ({name, institute, branch, course, signoff}) =>
`नमस्कार ${name},

*${course}* संदर्भात *${institute} – ${branch}* येथे भेट दिल्याबद्दल धन्यवाद.

अभ्यासक्रम, फी किंवा बॅचबद्दल आणखी काही माहिती हवी आहे का?

${signoff}`,

    courseFeeDetails: ({name, course, courseDetailsUrl, amount, signoff}) =>
`नमस्कार ${name},

*${course}* ची माहिती खाली दिली आहे.

*अभ्यासक्रम आणि अभ्यासक्रमाची रूपरेषा:*
${courseDetailsUrl}

*अंदाजे कोर्स फी:* ₹${amount}

*सूचना:* ही फी केवळ अंदाजे आहे, अंतिम कोटेशन नाही. प्रवेशापूर्वी केंद्र अंतिम फी, समाविष्ट सुविधा आणि पेमेंट अटी निश्चित करेल.

बॅचच्या वेळांबाबत मदत हवी असल्यास कळवा.

${signoff}`,

    approxFee: ({name, course, amount, signoff}) =>
`नमस्कार ${name},

*${course}* ची अंदाजे फी *₹${amount}* आहे.

निवडलेल्या प्रशिक्षण योजनेनुसार आणि लागू ऑफरनुसार अंतिम फी केंद्र निश्चित करेल.

🎓 पात्रता आणि सध्याच्या अटींनुसार *50% पर्यंत शिष्यवृत्तीचा लाभ* मिळू शकतो.

शिष्यवृत्ती चाचणी:
https://mctitechnologies.com/assessment/scholarship/

चाचणीनंतर *DONE* असा रिप्लाय द्या. आमचे समुपदेशक लागू लाभाची माहिती देतील.

${signoff}`,

    followup1: ({name, course, signoff}) =>
`नमस्कार ${name},

*${course}* संदर्भातील तुमच्या चौकशीसाठी संपर्क करत आहोत.

अभ्यासक्रम, फी किंवा बॅचच्या वेळांबद्दल काही मदत हवी आहे का?

${signoff}`,

    followup2: ({name, course, signoff}) =>
`नमस्कार ${name},

नवीन कौशल्य शिकण्याची सुरुवात नियमित सरावाने होते. *${course}* तुमच्या उद्दिष्टासाठी योग्य असल्यास आम्ही सुरुवात करण्यास मदत करू.

तुम्ही या महिन्यात प्रवेश घेण्याचा विचार करत आहात की नंतर?

${signoff}`,

    offer: ({name, course, offer, validity, signoff}) =>
`नमस्कार ${name},

*${course}* साठी सध्याची ऑफर:

${offer}

वैधता: ${validity}

ऑफरची माहिती समजावून सांगू का?

${signoff}`,

    decision: ({name, course, signoff}) =>
`नमस्कार ${name},

*${course}* साठी तुमचा निर्णय कळवा:

1. प्रवेश घेण्यासाठी तयार आहे
2. नंतर संपर्क करा — तारीख कळवतो/कळवते
3. माझी चौकशी बंद करा

पुढील संदेश नको असल्यास कृपया कळवा. आम्ही तुमच्या निर्णयाचा आदर करू.

${signoff}`
  },

  hi: {
    welcome: ({name, institute, course, courseDetailsUrl, location, signoff}) =>
`नमस्ते *${name}* 👋

*${institute}* से संपर्क करने के लिए धन्यवाद।

🎓 *आपका करियर, हमारी प्रतिबद्धता।*

⭐ नवी मुंबई के हमारे केंद्रों को 2,250+ Google Reviews मिले हैं।

हम आपकी सहायता करेंगे:
✅ करियर से जुड़े कंप्यूटर कोर्स
✅ कोर्स फीस और बैच टाइमिंग
✅ करियर काउंसलिंग और स्किल डेवलपमेंट

📚 *आपका पूछताछ किया गया कोर्स: ${course}*

कोर्स की जानकारी और करियर के अवसर:
🔗 ${courseDetailsUrl}

🧠 *फ्री करियर एप्टीट्यूड टेस्ट*
https://mctitechnologies.com/career/aptitude/start/

📍 *हमारे सेंटर पर आएं*
${location}

📅 कृपया आने का सुविधाजनक दिन और समय बताएं।

${signoff}`,

    appointment: ({name, course, date, time, location, signoff}) =>
`नमस्ते ${name},

*${course}* के लिए आपकी काउंसलिंग अपॉइंटमेंट निश्चित हो गई है।

📅 ${date}
⏰ ${time}

${location}

कृपया 5–10 मिनट पहले आएं और अपनी विजिट कन्फर्म करें।

${signoff}`,

    afterVisit: ({name, institute, branch, course, signoff}) =>
`नमस्ते ${name},

*${course}* के बारे में जानकारी लेने के लिए *${institute} – ${branch}* आने पर धन्यवाद।

क्या कोर्स, फीस या बैच के बारे में आपको और जानकारी चाहिए?

${signoff}`,

    courseFeeDetails: ({name, course, courseDetailsUrl, amount, signoff}) =>
`नमस्ते ${name},

*${course}* की जानकारी नीचे दी गई है।

*कोर्स विवरण और सिलेबस:*
${courseDetailsUrl}

*अनुमानित कोर्स फीस:* ₹${amount}

*सूचना:* यह केवल अनुमानित फीस है, अंतिम कोटेशन नहीं। एडमिशन से पहले सेंटर अंतिम फीस, कोर्स में शामिल सुविधाएं और भुगतान की शर्तें बताएगा।

बैच टाइमिंग में सहायता चाहिए तो बताएं।

${signoff}`,

    approxFee: ({name, course, amount, signoff}) =>
`नमस्ते ${name},

*${course}* की अनुमानित फीस *₹${amount}* है।

चुने गए ट्रेनिंग प्लान और लागू ऑफर के अनुसार अंतिम फीस सेंटर तय करेगा।

🎓 पात्रता और वर्तमान नियमों के अनुसार *50% तक स्कॉलरशिप का लाभ* मिल सकता है।

स्कॉलरशिप टेस्ट:
https://mctitechnologies.com/assessment/scholarship/

टेस्ट के बाद *DONE* लिखकर भेजें। हमारे काउंसलर लागू लाभ की जानकारी देंगे।

${signoff}`,

    followup1: ({name, course, signoff}) =>
`नमस्ते ${name},

*${course}* के बारे में आपकी पूछताछ के संबंध में संपर्क कर रहे हैं।

क्या आपको सिलेबस, फीस या बैच टाइमिंग के बारे में मदद चाहिए?

${signoff}`,

    followup2: ({name, course, signoff}) =>
`नमस्ते ${name},

नई स्किल सीखने की शुरुआत नियमित अभ्यास से होती है। यदि *${course}* आपके लक्ष्य के लिए सही है, तो हम शुरुआत करने में सहायता करेंगे।

आप इस महीने एडमिशन लेना चाहते हैं या बाद में?

${signoff}`,

    offer: ({name, course, offer, validity, signoff}) =>
`नमस्ते ${name},

*${course}* के लिए वर्तमान ऑफर:

${offer}

ऑफर की अंतिम तारीख: ${validity}

क्या आप ऑफर की पूरी जानकारी लेना चाहेंगे?

${signoff}`,

    decision: ({name, course, signoff}) =>
`नमस्ते ${name},

*${course}* के लिए अपना निर्णय बताएं:

1. एडमिशन लेने के लिए तैयार हूं
2. बाद में संपर्क करें — तारीख बताऊंगा/बताऊंगी
3. मेरी पूछताछ बंद करें

यदि आप आगे संदेश नहीं चाहते हैं, तो बताएं। हम आपके निर्णय का सम्मान करेंगे।

${signoff}`
  }
};

window.MCTIEnquiryLanguages = Object.freeze({
    build: function(language, template, data) {
        const fn = translations[language] && translations[language][template];
        return fn ? fn(data) : null;
    }
});
})();
