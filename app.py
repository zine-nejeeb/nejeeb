import streamlit as st
import pandas as pd
import random
import google.generativeai as genai

# 1. إعدادات الواجهة
st.set_page_config(page_title="تحدي الرياضيات الذكي", page_icon="📐")

# 2. إعداد الذكاء الاصطناعي (Gemini)
# سيقرأ المفتاح من Secrets التي وضعناها في Streamlit Cloud
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("⚠️ خطأ في إعداد مفتاح الذكاء الاصطناعي. تأكد من ضبط Secrets.")

# --- 🌟 الإضافة الإبداعية: دالة التلميح الذكي 🌟 ---
def get_ai_hint(question, user_answer, correct_answer):
    prompt = f"""
    أنت معلم رياضيات ذكي ومرح. الطالب أجاب بـ '{user_answer}' 
    على السؤال: '{question}'. والإجابة الصحيحة هي '{correct_answer}'.
    لا تعطِ الإجابة الصحيحة أبداً. أعطِ تلميحاً ذكياً ومختصراً جداً (باللغة العربية) 
    يساعد الطالب على اكتشاف خطأه بنفسه. استخدم رموزاً تعبيرية.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "فكر جيداً في القاعدة، أنت قادم على الحل! ✨"

# 3. دالة جلب البيانات من CSV
def load_data(file_name):
    try:
        return pd.read_csv(file_name).to_dict('records')
    except:
        return []

# 4. دالة توليد السؤال
def generate_question():
    templates = load_data("templates.csv")
    resources = load_data("resources.csv")
    
    if templates and resources:
        tpl = random.choice(templates)
        matches = [r for r in resources if r['Template_ID'] == tpl['ID']]
        if matches:
            res = random.choice(matches)
            txt = tpl['Temp_Text'].replace("{N1}", str(res.get('N1',''))).replace("{N2}", str(res.get('N2','')))
            txt = txt.replace("{Expression}", str(res.get('Expression',''))).replace("{H}", str(res.get('H',''))).replace("{A}", str(res.get('A','')))
            
            opts = [str(res['Correct_Answer']), str(res['Wrong1']), str(res['Wrong2']), str(res['Wrong3'])]
            random.shuffle(opts)
            return txt, str(res['Correct_Answer']), opts
    return None, None, None

# 5. واجهة المستخدم
st.title("📐 مسابقة الرياضيات - السنة 4 متوسط")

if st.button("🎲 سؤال جديد"):
    q_txt, correct, options = generate_question()
    st.session_state['q'] = q_txt
    st.session_state['correct'] = correct
    st.session_state['options'] = options
    st.session_state['feedback'] = None
    st.session_state['ai_hint'] = None

if 'q' in st.session_state:
    st.markdown(f"### {st.session_state['q']}")
    
    # عرض الأزرار كخيارات
    for opt in st.session_state['options']:
        if st.button(opt, key=opt):
            if opt == st.session_state['correct']:
                st.session_state['feedback'] = "✅ ممتاز! إجابة صحيحة"
                st.session_state['ai_hint'] = None
                st.balloons()
            else:
                st.session_state['feedback'] = "❌ إجابة غير دقيقة.."
                # استدعاء الذكاء الاصطناعي عند الخطأ
                with st.spinner("🤖 المعلم الذكي يحلل إجابتك..."):
                    hint = get_ai_hint(st.session_state['q'], opt, st.session_state['correct'])
                    st.session_state['ai_hint'] = hint

    # عرض النتائج والتلميحات
    if st.session_state['feedback']:
        if "✅" in st.session_state['feedback']:
            st.success(st.session_state['feedback'])
        else:
            st.error(st.session_state['feedback'])
            
    if st.session_state.get('ai_hint'):
        st.info(f"💡 **نصيحة المعلم:** {st.session_state['ai_hint']}")
