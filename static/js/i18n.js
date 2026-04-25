/**
 * FractureAI — Multi-Language Support (i18n)
 * =============================================
 * Supports English (en) and Hindi (hi).
 * Translates UI elements marked with data-i18n attributes.
 */

// ═══ Translation Dictionaries ═══

const translations = {
    en: {
        // Navigation
        home: "Home",
        scan: "Scan X-Ray",
        dashboard: "Dashboard",
        login: "Log In",
        logout: "Logout",

        // Hero
        ai_active: "AI SYSTEM ACTIVE",
        hero_subtitle: "Advanced AI-Powered Bone Fracture Detection System",
        hero_desc: "Upload your X-ray for instant AI diagnosis with heatmap visualization, severity prediction, and personalized recovery plans.",
        start_scan: "Start AI Scan",
        view_dashboard: "View Dashboard",
        get_started: "Get Started Free",
        accuracy: "Accuracy",
        scan_time: "Scan Time",
        availability: "Available",
        compliant: "Compliant",

        // Features
        features_title: "Powered by Next-Gen AI",
        features_desc: "Our deep learning CNN analyzes X-ray images with precision, providing instant and reliable fracture detection.",
        f1_title: "AI Fracture Detection",
        f1_desc: "CNN-powered analysis detects bone fractures from X-ray images with high accuracy and confidence scoring.",
        f2_title: "Heatmap Visualization",
        f2_desc: "Grad-CAM heatmaps highlight exact fracture regions, making AI decisions transparent and explainable.",
        f3_title: "Severity Prediction",
        f3_desc: "Classifies fractures as Low, Medium, or High severity with detailed fracture type identification.",
        f4_title: "Live Camera Scanning",
        f4_desc: "Point your camera at an X-ray film for real-time AI analysis without uploading files.",
        f5_title: "Voice Commands",
        f5_desc: "Navigate hands-free with speech recognition. Say 'scan' or 'dashboard' to control the app.",
        f6_title: "Smart PDF Reports",
        f6_desc: "Auto-generated medical reports with diagnosis, heatmaps, recovery plans, and doctor recommendations.",
        f7_title: "Recovery Suggestions",
        f7_desc: "Personalized recovery plans including diet, exercises, and timelines based on your specific fracture.",
        f8_title: "Patient Dashboard",
        f8_desc: "Complete history of all scans with analytics, trends, and visual statistics.",
        f9_title: "Multi-Language",
        f9_desc: "Full English and Hindi support. Switch languages instantly with a single click.",

        // How it works
        how_title: "How It Works",
        how_desc: "Three simple steps to AI-powered diagnosis",
        step1_title: "Upload X-Ray",
        step1_desc: "Drag & drop or select your X-ray image. Supports PNG, JPG, and JPEG formats.",
        step2_title: "AI Analysis",
        step2_desc: "Our CNN model analyzes the image, generates a heatmap, and classifies severity in seconds.",
        step3_title: "Get Results",
        step3_desc: "View detailed results with heatmap, download PDF report, and get recovery suggestions.",

        // CTA
        cta_title: "Ready to Scan?",
        cta_desc: "Start analyzing X-rays with AI in seconds. No credit card required.",

        // Auth
        login_title: "Welcome Back",
        login_subtitle: "Sign in to your FractureAI account",
        signup_title: "Create Account",
        signup_subtitle: "Join FractureAI for free AI diagnostics",
        username: "Username",
        password: "Password",
        email: "Email",
        full_name: "Full Name",
        confirm_password: "Confirm Password",
        login_btn: "Sign In",
        create_account: "Create Account",
        no_account: "Don't have an account?",
        signup_link: "Sign up",
        has_account: "Already have an account?",
        login_link: "Sign in",
        or: "or",

        // Scan page
        scan_title: "X-Ray Analysis",
        scan_subtitle: "Upload an X-ray image or use your camera for instant AI fracture detection",
        upload_title: "Upload X-Ray Image",
        camera_title: "Live Camera Scanner",
        drag_drop: "Drag & Drop your X-ray here",
        or_click: "or click to browse files",
        body_part: "Body Part",
        analyze_btn: "Analyze with AI",
        analyzing: "Analyzing X-ray with AI...",
        start_camera: "Start Camera",
        capture_analyze: "Capture & Analyze",
        camera_off: "Camera is off",
        camera_result: "Camera Analysis Result",

        // Results
        result_title: "Analysis Results",
        confidence: "Confidence",
        severity: "Severity Level",
        fracture_type: "Fracture Type",
        original_xray: "Original X-Ray",
        ai_heatmap: "AI Heatmap (Grad-CAM)",
        heatmap_desc: "Red/Yellow regions indicate areas the AI identified as potential fracture zones.",
        recovery_title: "AI Recovery Suggestions",
        doctor_title: "Recommended Specialists",
        download_pdf: "Download PDF Report",
        email_report: "Email Report",
        new_scan: "New Scan",
        to_dashboard: "Dashboard",
        result_disclaimer: "AI-generated results are for informational purposes only. Always consult a qualified healthcare professional for medical diagnosis and treatment.",

        // Dashboard
        dashboard_title: "Patient Dashboard",
        dashboard_subtitle: "Your complete scan history and analytics",
        total_scans: "Total Scans",
        fractures_found: "Fractures Found",
        normal_scans: "Normal Scans",
        avg_confidence: "Avg. Confidence",
        scan_history: "Scan History",
        date: "Date",
        result: "Result",
        actions: "Actions",
        no_scans: "No scans yet",
        no_scans_desc: "Upload your first X-ray to get started with AI diagnosis.",
        first_scan: "Start First Scan",

        // Voice
        listening: "Listening...",
        say_command: "Say a command...",

        // Footer
        disclaimer: "AI-powered diagnostic tool. Not a substitute for professional medical advice.",
    },

    hi: {
        // Navigation
        home: "होम",
        scan: "एक्स-रे स्कैन",
        dashboard: "डैशबोर्ड",
        login: "लॉग इन",
        logout: "लॉग आउट",

        // Hero
        ai_active: "AI सिस्टम सक्रिय",
        hero_subtitle: "उन्नत AI-संचालित हड्डी फ्रैक्चर पहचान प्रणाली",
        hero_desc: "तत्काल AI निदान, हीटमैप विज़ुअलाइज़ेशन, गंभीरता भविष्यवाणी और व्यक्तिगत रिकवरी योजनाओं के लिए अपना एक्स-रे अपलोड करें।",
        start_scan: "AI स्कैन शुरू करें",
        view_dashboard: "डैशबोर्ड देखें",
        get_started: "मुफ्त में शुरू करें",
        accuracy: "सटीकता",
        scan_time: "स्कैन समय",
        availability: "उपलब्ध",
        compliant: "अनुपालन",

        // Features
        features_title: "अगली पीढ़ी की AI तकनीक",
        features_desc: "हमारा डीप लर्निंग CNN एक्स-रे छवियों का सटीकता से विश्लेषण करता है।",
        f1_title: "AI फ्रैक्चर पहचान",
        f1_desc: "CNN-संचालित विश्लेषण उच्च सटीकता के साथ एक्स-रे से हड्डी के फ्रैक्चर का पता लगाता है।",
        f2_title: "हीटमैप विज़ुअलाइज़ेशन",
        f2_desc: "Grad-CAM हीटमैप सटीक फ्रैक्चर क्षेत्रों को हाइलाइट करता है।",
        f3_title: "गंभीरता भविष्यवाणी",
        f3_desc: "फ्रैक्चर को निम्न, मध्यम या उच्च गंभीरता में वर्गीकृत करता है।",
        f4_title: "लाइव कैमरा स्कैनिंग",
        f4_desc: "रीयल-टाइम AI विश्लेषण के लिए अपने कैमरे को एक्स-रे फिल्म पर इंगित करें।",
        f5_title: "वॉइस कमांड",
        f5_desc: "स्पीच रिकग्निशन से हैंड्स-फ्री नेविगेट करें।",
        f6_title: "स्मार्ट PDF रिपोर्ट",
        f6_desc: "निदान, हीटमैप, रिकवरी योजनाओं के साथ स्वचालित मेडिकल रिपोर्ट।",
        f7_title: "रिकवरी सुझाव",
        f7_desc: "आहार, व्यायाम और समयरेखा सहित व्यक्तिगत रिकवरी योजनाएं।",
        f8_title: "रोगी डैशबोर्ड",
        f8_desc: "विश्लेषण और रुझानों के साथ सभी स्कैन का पूरा इतिहास।",
        f9_title: "बहु-भाषा",
        f9_desc: "पूर्ण अंग्रेजी और हिंदी समर्थन। एक क्लिक में भाषा बदलें।",

        // How it works
        how_title: "यह कैसे काम करता है",
        how_desc: "AI-संचालित निदान के लिए तीन सरल चरण",
        step1_title: "एक्स-रे अपलोड करें",
        step1_desc: "अपनी एक्स-रे छवि को ड्रैग और ड्रॉप करें। PNG, JPG प्रारूप समर्थित हैं।",
        step2_title: "AI विश्लेषण",
        step2_desc: "हमारा CNN मॉडल सेकंडों में हीटमैप बनाता और गंभीरता वर्गीकृत करता है।",
        step3_title: "परिणाम प्राप्त करें",
        step3_desc: "हीटमैप, PDF रिपोर्ट और रिकवरी सुझावों के साथ विस्तृत परिणाम देखें।",

        // CTA
        cta_title: "स्कैन के लिए तैयार?",
        cta_desc: "सेकंडों में AI से एक्स-रे विश्लेषण शुरू करें।",

        // Auth
        login_title: "वापसी पर स्वागत",
        login_subtitle: "अपने FractureAI खाते में साइन इन करें",
        signup_title: "खाता बनाएं",
        signup_subtitle: "मुफ्त AI निदान के लिए FractureAI से जुड़ें",
        username: "उपयोगकर्ता नाम",
        password: "पासवर्ड",
        email: "ईमेल",
        full_name: "पूरा नाम",
        confirm_password: "पासवर्ड की पुष्टि",
        login_btn: "साइन इन",
        create_account: "खाता बनाएं",
        no_account: "खाता नहीं है?",
        signup_link: "साइन अप करें",
        has_account: "पहले से खाता है?",
        login_link: "साइन इन करें",
        or: "या",

        // Scan page
        scan_title: "एक्स-रे विश्लेषण",
        scan_subtitle: "तत्काल AI फ्रैक्चर पहचान के लिए एक्स-रे अपलोड करें या कैमरा उपयोग करें",
        upload_title: "एक्स-रे छवि अपलोड करें",
        camera_title: "लाइव कैमरा स्कैनर",
        drag_drop: "अपना एक्स-रे यहां ड्रैग और ड्रॉप करें",
        or_click: "या फाइल ब्राउज़ करने के लिए क्लिक करें",
        body_part: "शरीर का अंग",
        analyze_btn: "AI से विश्लेषण करें",
        analyzing: "AI से एक्स-रे का विश्लेषण हो रहा है...",
        start_camera: "कैमरा शुरू करें",
        capture_analyze: "कैप्चर और विश्लेषण",
        camera_off: "कैमरा बंद है",
        camera_result: "कैमरा विश्लेषण परिणाम",

        // Results
        result_title: "विश्लेषण परिणाम",
        confidence: "विश्वास",
        severity: "गंभीरता स्तर",
        fracture_type: "फ्रैक्चर प्रकार",
        original_xray: "मूल एक्स-रे",
        ai_heatmap: "AI हीटमैप (Grad-CAM)",
        heatmap_desc: "लाल/पीले क्षेत्र AI द्वारा पहचाने गए संभावित फ्रैक्चर ज़ोन को दर्शाते हैं।",
        recovery_title: "AI रिकवरी सुझाव",
        doctor_title: "अनुशंसित विशेषज्ञ",
        download_pdf: "PDF रिपोर्ट डाउनलोड करें",
        email_report: "रिपोर्ट ईमेल करें",
        new_scan: "नया स्कैन",
        to_dashboard: "डैशबोर्ड",
        result_disclaimer: "AI-जनित परिणाम केवल सूचनात्मक उद्देश्यों के लिए हैं। कृपया चिकित्सा निदान के लिए योग्य चिकित्सक से परामर्श करें।",

        // Dashboard
        dashboard_title: "रोगी डैशबोर्ड",
        dashboard_subtitle: "आपका पूरा स्कैन इतिहास और विश्लेषण",
        total_scans: "कुल स्कैन",
        fractures_found: "फ्रैक्चर पाए गए",
        normal_scans: "सामान्य स्कैन",
        avg_confidence: "औसत विश्वास",
        scan_history: "स्कैन इतिहास",
        date: "तारीख",
        result: "परिणाम",
        actions: "कार्य",
        no_scans: "अभी तक कोई स्कैन नहीं",
        no_scans_desc: "AI निदान शुरू करने के लिए अपना पहला एक्स-रे अपलोड करें।",
        first_scan: "पहला स्कैन शुरू करें",

        // Voice
        listening: "सुन रहा है...",
        say_command: "एक कमांड बोलें...",

        // Footer
        disclaimer: "AI-संचालित डायग्नोस्टिक टूल। पेशेवर चिकित्सा सलाह का विकल्प नहीं।",
    },
};


// ═══ Language State ═══
let currentLanguage = localStorage.getItem('fractureai-lang') || 'en';

/**
 * Toggle between English and Hindi.
 */
function toggleLanguage() {
    currentLanguage = currentLanguage === 'en' ? 'hi' : 'en';
    localStorage.setItem('fractureai-lang', currentLanguage);
    applyTranslations();

    // Visual feedback
    const btn = document.getElementById('lang-toggle');
    if (btn) {
        btn.title = currentLanguage === 'en' ? 'Switch to Hindi' : 'अंग्रेजी में बदलें';
    }
}

/**
 * Apply translations to all elements with data-i18n attributes.
 */
function applyTranslations() {
    const dict = translations[currentLanguage] || translations.en;

    document.querySelectorAll('[data-i18n]').forEach((el) => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) {
            el.textContent = dict[key];
        }
    });
}

// Apply translations on page load
document.addEventListener('DOMContentLoaded', () => {
    if (currentLanguage !== 'en') {
        applyTranslations();
    }
});
