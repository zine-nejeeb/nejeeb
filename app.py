import streamlit as st
import pandas as pd
import random
import google.generativeai as genai

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="منصة نجيب للرياضيات", page_icon="📐", layout="wide")

# --- 2. إعداد الذكاء الاصطناعي (Gemini) ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.warning("⚠️ لم يتم تفعيل ذكاء Gemini بعد. تأكد من إعداد Secrets.")

def get_ai_hint(question, user_answer, correct_answer):
    prompt = f"أنت معلم رياضيات جزائري خبير. الطالب أخطأ في إجابة سؤال '{question}' حيث اختار '{user_answer}' بينما الصحيح هو '{correct_answer}'. أعطه تلميحاً مشجعاً وذكياً بالعامية الجزائرية المهذبة أو العربية الفصحى ليجد الحل بنفسه دون إعطائه الإجابة مباشرة."
    try:
        return model.generate_content(prompt).text
    except:
        return "فكر مجدداً يا بطل، راجع قواعد الدرس وستصل للحل! ✨"

# --- 3. وظائف البيانات ---
def load_data(file_name):
    try:
        return pd.read_csv(file_name).to_dict('records')
    except:
        return []

# --- 4. منطق توليد السؤال المفلتر ---
def generate_question(selected_subject):
    templates = load_data("templates.csv")
    resources = load_data("resources.csv")
    
    if not templates or not resources:
        return None
    
    # تصفية القوالب حسب الدرس المختار
    filtered_tpls = [t for t in templates if t['Subject'] == selected_subject]
    if not filtered_tpls: return None
    
    tpl = random.choice(filtered_tpls)
    matches = [r for r in resources if str(r['Template_ID']) == str(tpl['ID'])]
    
    if matches:
        res = random.choice(matches)
        # دمج البيانات في القالب
        q_text = tpl['Temp_Text']
        q_text = q_text.replace("{N1}", str(res.get('N1',''))).replace("{N2}", str(res.get('N2','')))
        q_text = q_text.replace("{Expression}", str(res.get('Expression',''))).replace("{H}", str(res.get('H',''))).replace("{A}", str(res.get('A','')))
        
        options = [str(res['Correct_Answer']), str(res['Wrong1']), str(res['Wrong2']), str(res['Wrong3'])]
        random.shuffle(options)
        return {"text": q_text, "correct": str(res['Correct_Answer']), "options": options}
    return None

# --- 5. الواجهة الرسومية ---
st.title("🚀 منصة نجيب: تحدي الرياضيات (4 متوسط)")

# القائمة الجانبية
templates_all = load_data("templates.csv")
if templates_all:
    subjects = sorted(list(set([t['Subject'] for t in templates_all])))
    selected_subject = st.sidebar.selectbox("📖 اختر الدرس:", subjects)
    st.sidebar.divider()
    st.sidebar.info("هذا التطبيق يساعدك على التحضير لشهادة التعليم المتوسط BEM باستخدام الذكاء الاصطناعي.")

if st.button("🎲 ابدأ تحدي جديد"):
    result = generate_question(selected_subject)
    if result:
        st.session_state['current_q'] = result
        st.session_state['feedback'] = None
        st.session_state['hint'] = None

# عرض السؤال
if 'current_q' in st.session_state:
    q = st.session_state['current_q']
    st.subheader(q['text'])
    
    # عرض الخيارات كأزرار أعمدة
    cols = st.columns(2)
    for i, opt in enumerate(q['options']):
        with cols[i % 2]:
            if st.button(opt, key=f"btn_{opt}", use_container_width=True):
                if opt == q['correct']:
                    st.session_state['feedback'] = "✅ أحسنت! إجابة صحيحة عبقرية."
                    st.session_state['hint'] = None
                    st.balloons()
                else:
                    st.session_state['feedback'] = "❌ إجابة خاطئة، حاول مجدداً!"
                    with st.spinner("🤖 المعلم الذكي يكتب لك تلميحاً..."):
                        st.session_state['hint'] = get_ai_hint(q['text'], opt, q['correct'])

    # عرض التغذية الراجعة
    if st.session_state.get('feedback'):
        if "✅" in st.session_state['feedback']: st.success(st.session_state['feedback'])
        else: st.error(st.session_state['feedback'])
    
    if st.session_state.get('hint'):
        st.info(f"💡 **تلميح المعلم:** {st.session_state['hint']}")
