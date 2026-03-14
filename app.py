import streamlit as st
import pandas as pd
import random
import google.generativeai as genai

# إعدادات الواجهة
st.set_page_config(page_title="تحدي الرياضيات الذكي", page_icon="📐")

# دالة جلب البيانات من CSV
def load_data(file_name):
    try:
        return pd.read_csv(file_name).to_dict('records')
    except:
        return []

# دالة توليد السؤال
def generate_question():
    templates = load_data("templates.csv")
    resources = load_data("resources.csv")
    
    if templates and resources:
        tpl = random.choice(templates)
        # جلب المعطيات المناسبة للقالب
        matches = [r for r in resources if r['Template_ID'] == tpl['ID']]
        if matches:
            res = random.choice(matches)
            # دمج المعطيات في النص
            txt = tpl['Temp_Text'].replace("{N1}", str(res.get('N1',''))).replace("{N2}", str(res.get('N2','')))
            txt = txt.replace("{Expression}", str(res.get('Expression',''))).replace("{H}", str(res.get('H',''))).replace("{A}", str(res.get('A','')))
            
            # تجهيز الخيارات
            opts = [str(res['Correct_Answer']), str(res['Wrong1']), str(res['Wrong2']), str(res['Wrong3'])]
            random.shuffle(opts)
            return txt, str(res['Correct_Answer']), opts
    return None, None, None

# واجهة المستخدم
st.title("📐 مسابقة الرياضيات - السنة 4 متوسط")

if st.button("🎲 سؤال جديد"):
    q_txt, correct, options = generate_question()
    st.session_state['q'] = q_txt
    st.session_state['correct'] = correct
    st.session_state['options'] = options
    st.session_state['feedback'] = None

if 'q' in st.session_state:
    st.markdown(f"### {st.session_state['q']}")
    
    # عرض الأزرار
    for opt in st.session_state['options']:
        if st.button(opt, key=opt):
            if opt == st.session_state['correct']:
                st.session_state['feedback'] = "✅ ممتاز! إجابة صحيحة"
                st.balloons()
            else:
                st.session_state['feedback'] = "❌ حاول مرة أخرى، ركز في القاعدة!"

    if st.session_state['feedback']:
        st.write(st.session_state['feedback'])