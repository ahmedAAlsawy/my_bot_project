import google.generativeai as genai

# مفتاحك الحالي
GEMINI_KEY = 'AIzaSyAxs4q6ZxVWwZcD9WBkkZBYHlbRHaJdi7k'

# تجربة موديل gemini-pro (لأنه الأكثر توافقاً مع المفاتيح القديمة)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

print("⏳ جاري محاولة الاتصال بـ Gemini...")

try:
    response = model.generate_content("أهلاً، هل أنت مستعد للعمل كمصحح لغوي؟")
    print("\n✅ نجح الاتصال! رد الذكاء الاصطناعي:")
    print("-" * 30)
    print(response.text)
    print("-" * 30)
except Exception as e:
    print("\n❌ فشل الاتصال. نوع الخطأ:")
    print(str(e))
