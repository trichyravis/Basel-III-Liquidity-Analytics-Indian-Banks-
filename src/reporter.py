
from fpdf import FPDF
import datetime

class RiskReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Basel III Liquidity Risk Report', 0, 1, 'C')
        self.ln(5)

def generate_pdf(bank, lcr, nsfr, scenario):
    pdf = RiskReport()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    pdf.cell(0, 10, f"Date: {datetime.date.today()}", ln=1)
    pdf.cell(0, 10, f"Entity: {bank}", ln=1)
    pdf.cell(0, 10, f"Stress Scenario: {scenario}", ln=1)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, "Regulatory Metrics Output:", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Liquidity Coverage Ratio (LCR): {lcr}%", ln=1)
    pdf.cell(0, 10, f"Net Stable Funding Ratio (NSFR): {nsfr}%", ln=1)
    
    # Return as binary string for Streamlit download
    return pdf.output(dest='S').encode('latin-1')
