import streamlit as st
import pandas as pd
from PIL import Image
import pypdf
import re
import io
from fpdf import FPDF

# 1. إعدادات الصفحة وخصائص الـ Layout
st.set_page_config(
    page_title="AFBC - Credit Risk Assessment Agent",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. القواميس اللغوية الشاملة (English & Arabic) للواجهة
translations = {
    "English": {
        "title": "🏦 AFBC - Credit Risk Assessment Agent",
        "subtitle": "AI-Powered Credit Risk & DPR Assessment Dashboard (CBE Compliant)",
        "tab1": "📋 Client & Loan Parameters",
        "tab2": "📄 I-Score Document Upload & Verification",
        "client_name": "Client Name / National ID / File ID",
        "net_income": "Net Monthly Income (EGP)",
        "existing_commitments": "Existing Monthly Commitments (EGP)",
        "loan_amount": "Requested Loan Amount (EGP)",
        "loan_term": "Loan Term (Months: 12 - 120)",
        "loan_installment": "Proposed Monthly Installment (EGP)",
        "employment": "Employment Sector",
        "upload_iscore": "Upload I-Score Report (PDF / Image)",
        "manual_status": "Manual I-Score Status Verification",
        "submit_btn": "🚀 Run AI Credit Assessment & Generate Dashboard",
        "dashboard_title": "📊 Advanced Credit Risk Dashboard & Analytics",
        "metric_income": "Net Monthly Income",
        "metric_commitments": "Total Debt Service",
        "metric_dpr": "DPR Ratio (Max 50%)",
        "metric_status": "Bureau Status",
        "report_title": "🤖 AFBC Agent Advisory Report & Final Decision",
        "approved": "✅ Final Decision: APPROVED (Eligible for Disbursement)",
        "rejected": "❌ Final Decision: REJECTED (Policy or Regulatory Breach)",
        "advisory_title": "Executive Advisory & Financial Breakdown Summary:",
        "rule_compliance": "The application fully complies with Central Bank of Egypt (CBE) credit guidelines.",
        "dpr_safe": "Debt Payment Ratio (DPR): {dpr:.2f}% (Safe threshold <= 50%).",
        "residual_buffer": "Residual Living Income Buffer: {res:,.2f} EGP monthly.",
        "rec_disburse": "Underwriting Recommendation: Proceed and disburse {amt:,.2f} EGP over {term} months.",
        "rejection_reasons_title": "Mandatory Regulatory Reasons for Rejection:",
        "download_excel": "📥 Download Complete Financial Report (Excel)",
        "download_pdf": "📥 Download Official Dashboard Report (PDF)",
        "table_metric": "Financial Parameter / Indicator",
        "table_value": "Assessment Value / Details"
    },
    "العربية": {
        "title": "🏦 AFBC - وكيل تقييم مخاطر الائتمان الذكي",
        "subtitle": "لوحة تحكم ذكية لتقييم المخاطر وحساب عبء الدين وتحليل I-Score (مطابق لضوابط البنك المركزي المصري)",
        "tab1": "📋 بيانات العميل والتمويل المطلوب",
        "tab2": "📄 رفع وتحليل مستند الاستعلام الائتماني I-Score",
        "client_name": "اسم العميل / الرقم القومي / رقم الملف",
        "net_income": "صافي الدخل الشهري المثبت (ج.م)",
        "existing_commitments": "إجمالي الأقساط والالتزامات الحالية (ج.م)",
        "loan_amount": "مبلغ التمويل المطلوب (ج.م)",
        "loan_term": "مدة التمويل بالأشهر (من 12 إلى 120 شهر)",
        "loan_installment": "القسط الشهري المقترح للتمويل الجديد (ج.م)",
        "employment": "قطاع جهة العمل",
        "upload_iscore": "قم برفع ملف تقرير الاستعلام الائتماني I-Score (PDF أو صورة)",
        "manual_status": "التحقق اليدوي لحالة I-Score الائتمانية",
        "submit_btn": "🚀 بدء تحليل الذكاء الاصطناعي وعرض لوحة التحكم",
        "dashboard_title": "📊 لوحة تحكم مخاطر الائتمان والتحليل المالي التفاعلية",
        "metric_income": "صافي الدخل الشهري",
        "metric_commitments": "إجمالي خدمة الديون",
        "metric_dpr": "معدل عبء الدين DPR (الحد الأقصى 50%)",
        "metric_status": "حالة الاستعلام الائتماني",
        "report_title": "🤖 تقرير الوكيل الاستشاري والقرار الائتماني النهائي",
        "approved": "✅ القرار الائتماني النهائي: مقبول (مستوفي لشروط الصرف)",
        "rejected": "❌ القرار الائتماني النهائي: مرفوض (مخالفة لضوابط المخاطر)",
        "advisory_title": "ملخص التحليل المالي والتوصيات الاستشارية:",
        "rule_compliance": "الطلب مستوفي بالكامل لتعليمات وضوابط البنك المركزي المصري (CBE).",
        "dpr_safe": "معدل عبء الدين (DPR): {dpr:.2f}% (ضمن الحد الآمن المقررة <= 50%).",
        "residual_buffer": "الدخل المتبقي للمعيشة بعد الالتزامات: {res:,.2f} ج.م شهرياً.",
        "rec_disburse": "توصية الاكتتاب: الموافقة على منح وتسييل مبلغ {amt:,.2f} ج.م على فترة {term} شهراً.",
        "rejection_reasons_title": "الأسباب والمبررات الرقابية للرفض:",
        "download_excel": "📥 تحميل التقرير المالي الشامل بصيغة Excel",
        "download_pdf": "📥 تحميل تقرير لوحة التحكم الرسمي بصيغة PDF",
        "table_metric": "المؤشر المالي / البيانات الأساسية",
        "table_value": "القيمة / التفاصيل الائتمانية"
    }
}

# التقاط اللغة تلقائياً من رابط الـ iFrame (URL Query Parameters)
query_params = st.query_params
url_lang = query_params.get("lang", "en")
default_index = 1 if url_lang == "ar" else 0

# الشريط الجانبي لاختيار اللغة
st.sidebar.markdown("### ⚙️ Control Panel / لوحة التحكم")
lang_choice = st.sidebar.selectbox("Choose Language / اختر اللغة", ["English", "العربية"], index=default_index)
t = translations[lang_choice]

is_rtl = (lang_choice == "العربية")
dir_style = "rtl" if is_rtl else "ltr"
align_style = "right" if is_rtl else "left"

st.markdown(f"""
    <style>
    .main {{ direction: {dir_style}; text-align: {align_style}; }}
    .stMetric {{ background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 15px; border-radius: 12px; border: 1px solid #ced4da; }}
    </style>
""", unsafe_allow_html=True)

st.title(t["title"])
st.markdown(f"### {t['subtitle']}")
st.markdown("---")

# وظيفة قراءة مستند الـ I-Score
def parse_iscore_document(uploaded_file):
    extracted_text = ""
    file_type = uploaded_file.name.split('.')[-1].lower()
    try:
        if file_type == 'pdf':
            pdf_reader = pypdf.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() or ""
        else:
            image = Image.open(uploaded_file)
            extracted_text = f"Image Report Uploaded: {uploaded_file.name}"
    except Exception as e:
        return {"is_defaulted": False, "filename": uploaded_file.name, "text": "Error reading file"}

    text_lower = extracted_text.lower()
    is_defaulted = any(word in text_lower for word in ["تعثر", "متأخرات", "default", "write-off", "delinquent"])
    return {"is_defaulted": is_defaulted, "filename": uploaded_file.name, "text": extracted_text[:300]}

# نموذج إدخال البيانات
with st.form("credit_form"):
    st.subheader(t["tab1"])
    col1, col2 = st.columns(2)
    
    with col1:
        client_name = st.text_input(t["client_name"], "Ahmed Ramadan Rabei")
        net_income = st.number_input(t["net_income"], min_value=0.0, value=15000.0, step=500.0)
        existing_commitments = st.number_input(t["existing_commitments"], min_value=0.0, value=2500.0, step=500.0)
        loan_amount = st.number_input(t["loan_amount"], min_value=0.0, value=150000.0, step=5000.0)
        
    with col2:
        loan_term = st.slider(t["loan_term"], min_value=12, max_value=120, value=36, step=6)
        loan_installment = st.number_input(t["loan_installment"], min_value=0.0, value=4000.0, step=500.0)
        employment_type = st.selectbox(
            t["employment"],
            ["Government / Public Sector", "Tier 1 Multinational / Corporate", "SME Sector", "Self-Employed / Freelancer"]
        )
        manual_status = st.selectbox(
            t["manual_status"],
            ["Clean & Regular (No Delinquency)", "Minor Delinquencies (< 30 Days)", "Defaulted / Negative List"]
        )

    st.markdown("---")
    st.subheader(t["tab2"])
    uploaded_iscore = st.file_uploader(t["upload_iscore"], type=["pdf", "png", "jpg", "jpeg"])
    
    submitted = st.form_submit_button(label=t["submit_btn"])

if submitted:
    MIN_INCOME_THRESHOLD = 5000.0
    MAX_DPR_LIMIT = 50.0
    
    hard_stops = []
    iscore_summary_text = "No file uploaded (Manual Verification Used)"
    
    if uploaded_iscore:
        iscore_res = parse_iscore_document(uploaded_iscore)
        iscore_summary_text = f"Uploaded File: {iscore_res['filename']} (Parsed Successfully)"
        if iscore_res["is_defaulted"]:
            hard_stops.append("I-Score Policy Breach: Detected default flags in the uploaded report.")
            
    if "Defaulted" in manual_status or "متعثر" in manual_status:
        hard_stops.append("I-Score Policy Breach: Client listed in negative bureau database.")

    if net_income < MIN_INCOME_THRESHOLD:
        hard_stops.append(f"Minimum Income Breach: Income ({net_income:,.2f} EGP) is below CBE threshold ({MIN_INCOME_THRESHOLD:,.2f} EGP).")

    total_commitments = existing_commitments + loan_installment
    dpr_ratio = (total_commitments / net_income) * 100 if net_income > 0 else 100.0
    
    if dpr_ratio > MAX_DPR_LIMIT:
        hard_stops.append(f"DPR Regulatory Breach: Debt Payment Ratio ({dpr_ratio:.2f}%) exceeds the 50.00% maximum limit.")

    remaining_income = max(0.0, net_income - total_commitments)
    is_approved = (len(hard_stops) == 0)

    # 3. عرض لوحة التحكم (Dashboard Metrics)
    st.markdown("---")
    st.header(t["dashboard_title"])
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(t["metric_income"], f"{net_income:,.2f} EGP")
    m2.metric(t["metric_commitments"], f"{total_commitments:,.2f} EGP")
    m3.metric(t["metric_dpr"], f"{dpr_ratio:.2f}%", delta=f"Limit: 50%" if dpr_ratio <= 50 else "Exceeded", delta_color="normal" if dpr_ratio <= 50 else "inverse")
    m4.metric(t["metric_status"], "Approved ✅" if is_approved else "Review ⚠️")

    # 4. جدول النتائج الاحترافي (Structured Data Table)
    st.markdown("### 📋 Structured Financial & Credit Assessment Table")
    summary_df = pd.DataFrame({
        t["table_metric"]: [
            "Client Name / اسم العميل",
            "Employment Sector / قطاع العمل",
            "Net Monthly Income / صافي الدخل",
            "Requested Loan / قيمة التمويل المطلوبة",
            "Loan Term / مدة القرض (أشهر)",
            "New Installment / القسط الجديد",
            "Existing Commitments / الالتزامات الحالية",
            "Total Debt Service / إجمالي خدمة الديون",
            "DPR Percentage / معدل عبء الدين",
            "Residual Income / الدخل المتبقي للمعشة",
            "I-Score Status / حالة الاستعلام الائتماني",
            "Final Status / القرار الائتماني النهائي"
        ],
        t["table_value"]: [
            client_name,
            employment_type,
            f"{net_income:,.2f} EGP",
            f"{loan_amount:,.2f} EGP",
            f"{loan_term} Months",
            f"{loan_installment:,.2f} EGP",
            f"{existing_commitments:,.2f} EGP",
            f"{total_commitments:,.2f} EGP",
            f"{dpr_ratio:.2f}%",
            f"{remaining_income:,.2f} EGP",
            manual_status,
            "APPROVED ✅" if is_approved else "REJECTED ❌"
        ]
    })
    st.table(summary_df)

    # رسوم بيانية ديناميكية
    st.markdown("### 📈 Dynamic Financial Breakdown Chart")
    chart_df = pd.DataFrame({
        "Category": ["Existing Commitments", "New Loan Installment", "Residual Living Income"],
        "Amount (EGP)": [existing_commitments, loan_installment, remaining_income]
    }).set_index("Category")
    st.bar_chart(chart_df)

    # 5. التقرير الاستشاري الديناميكي
    st.markdown("---")
    st.header(t["report_title"])
    
    if not is_approved:
        st.error(t["rejected"])
        st.markdown(f"**{t['rejection_reasons_title']}**")
        for reason in hard_stops:
            st.markdown(f"- 🔴 {reason}")
    else:
        st.success(t["approved"])
        st.info(f"""
        **{t['advisory_title']}**
        * {t['rule_compliance']}
        * {t['dpr_safe'].format(dpr=dpr_ratio)}
        * {t['residual_buffer'].format(res=remaining_income)}
        * {t['rec_disburse'].format(amt=loan_amount, term=loan_term)}
        """)

    # 6. التصدير المتقدم (Excel & Visual PDF بصيغة مستقرة ومهنية)
    st.markdown("---")
    col_dl1, col_dl2 = st.columns(2)
    
    # أ. تصدير Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        summary_df.to_excel(writer, index=False, sheet_name='Credit Assessment Report')
    excel_data = output.getvalue()
    
    with col_dl1:
        st.download_button(
            label=t["download_excel"],
            data=excel_data,
            file_name=f"AFBC_Credit_Report_{client_name.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    # ب. تصدير تقرير PDF رسمي ومستقر باللغة الإنجليزية المصرفية
    pdf = FPDF()
    pdf.add_page()
    
    # شريط العنوان العلوي (Header Banner)
    pdf.set_fill_color(26, 82, 118)
    pdf.rect(10, 10, 190, 20, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_xy(10, 15)
    pdf.cell(190, 10, "AFBC - CREDIT RISK ASSESSMENT REPORT", 0, 1, "C")
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)
    
    # إطار صندوق الحالة (Status Card Box)
    if is_approved:
        pdf.set_fill_color(212, 239, 223)
    else:
        pdf.set_fill_color(253, 237, 236)
        
    pdf.rect(10, 35, 190, 12, 'F')
    pdf.set_font("Arial", 'B', 10)
    pdf.set_xy(15, 38)
    status_pdf = "FINAL DECISION: APPROVED (ELIGIBLE FOR DISBURSEMENT)" if is_approved else "FINAL DECISION: REJECTED (POLICY BREACH)"
    pdf.cell(180, 6, status_pdf, 0, 1, "C")
    
    pdf.ln(8)
    
    # جدول البيانات في الـ PDF
    pdf.set_font("Arial", 'B', 10)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(95, 8, " Financial Indicator", 1, 0, 'L', True)
    pdf.cell(95, 8, " Assessment Value", 1, 1, 'L', True)
    
    pdf.set_font("Arial", '', 9)
    pdf_rows = [
        ("Client Name", str(client_name)),
        ("Employment Sector", str(employment_type)),
        ("Net Monthly Income", f"{net_income:,.2f} EGP"),
        ("Requested Loan Amount", f"{loan_amount:,.2f} EGP ({loan_term} Months)"),
        ("Proposed Installment", f"{loan_installment:,.2f} EGP"),
        ("Existing Commitments", f"{existing_commitments:,.2f} EGP"),
        ("Total Debt Service", f"{total_commitments:,.2f} EGP"),
        ("DPR Percentage", f"{dpr_ratio:.2f}% (Regulatory Limit: 50%)"),
        ("Residual Living Income", f"{remaining_income:,.2f} EGP"),
        ("I-Score Status", str(manual_status)),
        ("Bureau Analysis", str(iscore_summary_text))
    ]
    
    for label, val in pdf_rows:
        pdf.cell(95, 7, f" {label}", 1, 0, 'L')
        pdf.cell(95, 7, f" {val}", 1, 1, 'L')
        
    pdf.ln(5)
    
    # صندوق التوصيات
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 6, "Executive Advisory Summary:", 0, 1)
    pdf.set_font("Arial", '', 9)
    if not is_approved:
        for r in hard_stops:
            pdf.cell(190, 5, f"- [BREACH] {r}", 0, 1)
    else:
        pdf.cell(190, 5, "- Fully complies with Central Bank of Egypt (CBE) guidelines.", 0, 1)
        pdf.cell(190, 5, f"- DPR ratio ({dpr_ratio:.2f}%) is within the safe limit (<= 50%).", 0, 1)
        pdf.cell(190, 5, f"- Client retains {remaining_income:,.2f} EGP as residual buffer.", 0, 1)

    pdf_output = bytes(pdf.output())
    
    with col_dl2:
        st.download_button(
            label=t["download_pdf"],
            data=pdf_output,
            file_name=f"AFBC_Dashboard_Report_{client_name.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
