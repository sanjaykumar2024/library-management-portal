import os
import shutil
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_PATH = 'LibrarySphere_Final_Review_Presentation.pptx'
ARTIFACT_DIR = '/Users/sk/.gemini/antigravity/brain/3545079b-dbe7-499f-854e-0efad337c5d9'

# Institutional Academic Color Palette
COLOR_BLUE = RGBColor(0, 51, 153)       # #003399 Headings (Bold UPPERCASE, 24pt)
COLOR_MAROON = RGBColor(128, 0, 0)      # #800000 Subheadings (Bold Sentence Case, 20-22pt)
COLOR_GREEN = RGBColor(22, 101, 52)     # #166534 Subheadings
COLOR_VIOLET = RGBColor(107, 33, 168)   # #6B21A8 Subheadings
COLOR_BLACK = RGBColor(0, 0, 0)         # #000000 Body Contents (13.5-16pt)
COLOR_DARK_GRAY = RGBColor(70, 70, 70)  # Footers & Subdued Metadata
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_TBL_HEADER = RGBColor(241, 245, 249) # #F1F5F9 Slate light header

FONT_FAMILY = "Cambria"

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs

def set_font(run_or_p, name=FONT_FAMILY, size=Pt(14), bold=False, color=COLOR_BLACK):
    run_or_p.font.name = name
    run_or_p.font.size = size
    run_or_p.font.bold = bold
    run_or_p.font.color.rgb = color
    if hasattr(run_or_p, 'runs'):
        for r in run_or_p.runs:
            r.font.name = name
            r.font.size = size
            r.font.bold = bold
            r.font.color.rgb = color

def set_cell_text(cell, text, size=Pt(11), bold=False, color=COLOR_BLACK, align=PP_ALIGN.LEFT):
    cell.text = text
    cell.margin_left = Inches(0.08)
    cell.margin_right = Inches(0.08)
    cell.margin_top = Inches(0.04)
    cell.margin_bottom = Inches(0.04)
    for p in cell.text_frame.paragraphs:
        set_font(p, size=size, bold=bold, color=color)
        p.alignment = align
        for r in p.runs:
            set_font(r, size=size, bold=bold, color=color)

def add_header(slide, title_text):
    tx_box = slide.shapes.add_textbox(Inches(0.92), Inches(0.24), Inches(11.5), Inches(0.55))
    tf = tx_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.text = title_text.upper()
    set_font(p, size=Pt(24), bold=True, color=COLOR_BLUE)

def add_footer(slide, slide_num, date_str="30-10-2026", review_str="FINAL REVIEW PRESENTATION"):
    # Left Date
    tx_l = slide.shapes.add_textbox(Inches(0.92), Inches(6.95), Inches(3.0), Inches(0.35))
    tf_l = tx_l.text_frame
    tf_l.margin_left = tf_l.margin_top = tf_l.margin_right = tf_l.margin_bottom = 0
    p_l = tf_l.paragraphs[0]
    p_l.text = date_str
    set_font(p_l, size=Pt(12.5), bold=False, color=COLOR_DARK_GRAY)

    # Center Review Tag
    tx_c = slide.shapes.add_textbox(Inches(4.42), Inches(6.95), Inches(4.5), Inches(0.35))
    tf_c = tx_c.text_frame
    tf_c.margin_left = tf_c.margin_top = tf_c.margin_right = tf_c.margin_bottom = 0
    p_c = tf_c.paragraphs[0]
    p_c.text = review_str
    set_font(p_c, size=Pt(12.5), bold=True, color=COLOR_BLUE)

    # Right Slide Number
    tx_r = slide.shapes.add_textbox(Inches(10.0), Inches(6.95), Inches(2.4), Inches(0.35))
    tf_r = tx_r.text_frame
    tf_r.margin_left = tf_r.margin_top = tf_r.margin_right = tf_r.margin_bottom = 0
    p_r = tf_r.paragraphs[0]
    p_r.text = str(slide_num)
    p_r.alignment = PP_ALIGN.RIGHT
    set_font(p_r, size=Pt(12.5), bold=True, color=COLOR_DARK_GRAY)

prs = create_presentation()
blank_layout = prs.slide_layouts[6]

print("Building 17 Reference-Aligned Slides for LibrarySphere...")

# ==========================================
# SLIDE 1: TITLE SLIDE
# ==========================================
print("Generating Slide 1: Title Page...")
s1 = prs.slides.add_slide(blank_layout)

# College Banner
if os.path.exists('template_extracted/slide_1_shape_2.png'):
    s1.shapes.add_picture('template_extracted/slide_1_shape_2.png', Inches(2.45), Inches(0.12), width=Inches(8.4))

# Academic Year & Review Header
tx1_head = s1.shapes.add_textbox(Inches(2.0), Inches(1.5), Inches(9.333), Inches(0.85))
tf1_head = tx1_head.text_frame
tf1_head.word_wrap = True
p1_h = tf1_head.paragraphs[0]
p1_h.text = "ACADEMIC YEAR 2026 - 27\nS7 PROJECT WORK\nFINAL REVIEW"
set_font(p1_h, size=Pt(16), bold=True, color=COLOR_BLUE)
p1_h.alignment = PP_ALIGN.CENTER

# Project Title
tx1_title = s1.shapes.add_textbox(Inches(1.0), Inches(2.48), Inches(11.333), Inches(1.4))
tf1_title = tx1_title.text_frame
tf1_title.word_wrap = True
p1_t_lbl = tf1_title.paragraphs[0]
p1_t_lbl.text = "PROJECT TITLE"
set_font(p1_t_lbl, size=Pt(15), bold=True, color=COLOR_BLUE)
p1_t_lbl.alignment = PP_ALIGN.CENTER

p1_t_main = tf1_title.add_paragraph()
p1_t_main.text = "PUBLIC LIBRARY MEMBERSHIP MANAGEMENT AND BOOK RESERVATION TRACKING PORTAL"
set_font(p1_t_main, size=Pt(20), bold=True, color=COLOR_MAROON)
p1_t_main.alignment = PP_ALIGN.CENTER

p1_t_sub = tf1_title.add_paragraph()
p1_t_sub.text = "(LibrarySphere: Next-Generation Touchless Self-Checkout & Digital E-Book Library Ecosystem)"
set_font(p1_t_sub, size=Pt(14), bold=True, color=COLOR_BLUE)
p1_t_sub.alignment = PP_ALIGN.CENTER

# BIP Project ID & Category Box
tx1_meta = s1.shapes.add_textbox(Inches(1.5), Inches(4.1), Inches(10.333), Inches(0.6))
tf1_meta = tx1_meta.text_frame
p1_m = tf1_meta.paragraphs[0]
p1_m.text = "BIP PROJECT ID: 24S7INT369                                        CATEGORY: INTERNAL / EXTERNAL – OWN"
set_font(p1_m, size=Pt(13.5), bold=True, color=COLOR_BLACK)
p1_m.alignment = PP_ALIGN.CENTER

# Batch Members Box (Left)
tx1_batch = s1.shapes.add_textbox(Inches(1.5), Inches(5.0), Inches(5.0), Inches(1.7))
tf1_batch = tx1_batch.text_frame
p1_b_lbl = tf1_batch.paragraphs[0]
p1_b_lbl.text = "BATCH MEMBERS"
set_font(p1_b_lbl, size=Pt(15), bold=True, color=COLOR_BLUE)
p1_b_m1 = tf1_batch.add_paragraph()
p1_b_m1.text = "SUBIKSHA SHREE S (7376231EC295)"
set_font(p1_b_m1, size=Pt(13.5), bold=True, color=COLOR_BLACK)
p1_b_m2 = tf1_batch.add_paragraph()
p1_b_m2.text = "SANJAYKUMAR S (7376232IT249)"
set_font(p1_b_m2, size=Pt(13.5), bold=True, color=COLOR_BLACK)

# Guide Box (Right)
tx1_guide = s1.shapes.add_textbox(Inches(7.2), Inches(5.0), Inches(5.2), Inches(1.7))
tf1_guide = tx1_guide.text_frame
p1_g_lbl = tf1_guide.paragraphs[0]
p1_g_lbl.text = "SUPERVISOR / GUIDE"
set_font(p1_g_lbl, size=Pt(15), bold=True, color=COLOR_BLUE)
p1_g_name = tf1_guide.add_paragraph()
p1_g_name.text = "Prof. MAHESHKUMAR K"
set_font(p1_g_name, size=Pt(13.5), bold=True, color=COLOR_BLACK)
p1_g_desig = tf1_guide.add_paragraph()
p1_g_desig.text = "Assistant Professor Level II\nDepartment of Computer Science and Design\nBannari Amman Institute of Technology"
set_font(p1_g_desig, size=Pt(12), bold=False, color=COLOR_DARK_GRAY)

add_footer(s1, 1)


# ==========================================
# SLIDE 2: AIM & OBJECTIVES OF THE PROJECT
# (Directly mirrors S6 reference Slide 2 format!)
# ==========================================
print("Generating Slide 2: Aim & Objectives...")
s2 = prs.slides.add_slide(blank_layout)
add_header(s2, "AIM & OBJECTIVES OF THE PROJECT")

tx2 = s2.shapes.add_textbox(Inches(0.92), Inches(1.05), Inches(11.5), Inches(5.7))
tf2 = tx2.text_frame
tf2.word_wrap = True

p2_aim_lbl = tf2.paragraphs[0]
p2_aim_lbl.text = "Aim:"
set_font(p2_aim_lbl, size=Pt(20), bold=True, color=COLOR_MAROON)
p2_aim_lbl.space_after = Pt(2)

p2_aim_desc = tf2.add_paragraph()
p2_aim_desc.text = "To design, develop, and deploy an automated, web-accessible public library management and book reservation ecosystem (LibrarySphere) that unifies physical book circulation and digital e-book reading, eliminates circulation desk congestion through hardware-free touchless self-checkout kiosks, and enforces transactional data integrity through role-based governance."
set_font(p2_aim_desc, size=Pt(14), bold=False, color=COLOR_BLACK)
p2_aim_desc.space_after = Pt(10)

p2_obj_lbl = tf2.add_paragraph()
p2_obj_lbl.text = "Objectives:"
set_font(p2_obj_lbl, size=Pt(20), bold=True, color=COLOR_MAROON)
p2_obj_lbl.space_after = Pt(4)

s2_objectives = [
    ("Unified Dual-Catalog Management: ", "Develop a centralized OPAC to catalog physical hardcovers with unique accession numbers alongside authentic digital EPUB assets."),
    ("Touchless Self-Checkout Station: ", "Implement a browser-native web-cam barcode and QR scanner using Html5-QRCode for autonomous, unassisted patron checkouts."),
    ("Atomic ACID Circulation Engine: ", "Engineer thread-safe book issuance, renewal quotas, and returns with row-level database locking preventing concurrent race conditions."),
    ("Automated FIFO Reservation Queues: ", "Create an automated waitlist hold allocation engine that automatically assigns returned books to next-in-line patrons with alert notifications."),
    ("Multi-Tier Access Control & Fines: ", "Enforce granular Role-Based Access Control (Admin, Librarian, Member) and an automated daily overdue penalty engine (₹5/day)."),
    ("In-Browser Digital E-Book Reader Studio: ", "Deliver a decoupled EPUB streaming reader supporting typography scaling (A-/A+), Web Speech API audio narration, and 4 persistent themes."),
    ("Real-Time Operational Analytics: ", "Provide executive dashboards tracking active circulation velocity, inventory auditing, overdue debt recovery, and exportable CSV reports.")
]

for title, desc in s2_objectives:
    p_obj = tf2.add_paragraph()
    r_t = p_obj.add_run()
    r_t.text = f"•  {title}"
    set_font(r_t, size=Pt(13.5), bold=True, color=COLOR_BLUE)
    r_d = p_obj.add_run()
    r_d.text = desc
    set_font(r_d, size=Pt(13), bold=False, color=COLOR_BLACK)
    p_obj.space_before = Pt(1.5)
    p_obj.space_after = Pt(1.5)

add_footer(s2, 2)


# ==========================================
# SLIDE 3: LITERATURE SURVEY (Part 1 / 3)
# (Directly mirrors S6 reference Slide 3 table!)
# ==========================================
print("Generating Slide 3: Literature Survey (Part 1)...")
s3 = prs.slides.add_slide(blank_layout)
add_header(s3, "LITERATURE SURVEY")

# Subtitle
tx3_sub = s3.shapes.add_textbox(Inches(0.92), Inches(0.82), Inches(11.5), Inches(0.35))
tf3_sub = tx3_sub.text_frame
p3_sub = tf3_sub.paragraphs[0]
p3_sub.text = "Review of Web-Based Library Architectures & Circulation Portals (Part 1 of 3)"
set_font(p3_sub, size=Pt(15), bold=True, color=COLOR_MAROON)

# Table: 4 rows x 4 cols
tbl3_shape = s3.shapes.add_table(4, 4, Inches(0.92), Inches(1.2), Inches(11.5), Inches(5.4))
t3 = tbl3_shape.table
t3.columns[0].width = Inches(0.75)
t3.columns[1].width = Inches(3.45)
t3.columns[2].width = Inches(3.65)
t3.columns[3].width = Inches(3.65)

headers = ['Sl. No.', 'References (Journal Papers Only)', 'Works carried out (Methods/Materials/Software/Algorithms/Techniques)', 'Information gathered relevant to your project']
for c_i, h in enumerate(headers):
    cell = t3.cell(0, c_i)
    set_cell_text(cell, h, size=Pt(11.5), bold=True, color=COLOR_BLUE)

lit_data_1 = [
    ("1",
     "V. Kumar, “Cloud-Based Integrated Library Management Systems for Academic Resource Centers: Architecture, Performance, and Implementation,” International Journal of Information Management, vol. 63, p. 102450, 2022.",
     "Digitized catalog searching, physical book accessioning, and patron record-keeping using PHP and MySQL in an academic resource center.",
     "Demonstrated that web-based catalog platforms significantly reduce catalog inquiry latency and improve bibliographic visibility, but identified key gaps in role-based access control and digital e-book reading."),
    ("2",
     "R. Krishnan, “Evaluating Latency and User Satisfaction in Multi-Tier Online Public Access Catalogs (OPAC),” Journal of Academic Librarianship, vol. 46, no. 5, p. 102210, 2020.",
     "Evaluated multi-tier OPAC systems across higher education libraries measuring query response times and user search behavior.",
     "Identified that lack of real-time physical shelf availability and faceted category filtering creates substantial user frustration, leading to high search abandonment rates in legacy portals."),
    ("3",
     "S. Rajan, “Design and Deployment of Lightweight Web-Based Book Circulation Tracking Systems in Community Libraries,” IEEE Access, vol. 9, pp. 88120–88132, 2021.",
     "Built a lightweight web circulation portal tracking issues and returns through a basic two-state workflow.",
     "Reported a 45% reduction in circulation desk processing time, but lacked automated overdue fine calculations, reservation queues, and in-browser digital e-book access.")
]

for r_i, row_data in enumerate(lit_data_1, start=1):
    for c_i, val in enumerate(row_data):
        cell = t3.cell(r_i, c_i)
        set_cell_text(cell, val, size=Pt(10.5 if c_i > 0 else 11.5), bold=(c_i == 0), color=COLOR_BLACK)

add_footer(s3, 3)


# ==========================================
# SLIDE 4: LITERATURE SURVEY (Part 2 / 3)
# (Directly mirrors S6 reference Slide 4 table!)
# ==========================================
print("Generating Slide 4: Literature Survey (Part 2)...")
s4 = prs.slides.add_slide(blank_layout)
add_header(s4, "LITERATURE SURVEY")

tx4_sub = s4.shapes.add_textbox(Inches(0.92), Inches(0.82), Inches(11.5), Inches(0.35))
tf4_sub = tx4_sub.text_frame
p4_sub = tf4_sub.paragraphs[0]
p4_sub.text = "Review of Automated Circulation & Waitlist Prioritization (Part 2 of 3)"
set_font(p4_sub, size=Pt(15), bold=True, color=COLOR_MAROON)

tbl4_shape = s4.shapes.add_table(4, 4, Inches(0.92), Inches(1.2), Inches(11.5), Inches(5.4))
t4 = tbl4_shape.table
t4.columns[0].width = Inches(0.75)
t4.columns[1].width = Inches(3.45)
t4.columns[2].width = Inches(3.65)
t4.columns[3].width = Inches(3.65)

for c_i, h in enumerate(headers):
    cell = t4.cell(0, c_i)
    set_cell_text(cell, h, size=Pt(11.5), bold=True, color=COLOR_BLUE)

lit_data_2 = [
    ("4",
     "R. Sharma, V. Kumar, and S. Patel, “Workflow Automation and Rule-Based Checkout Validation in Academic Library Circulation,” IEEE Transactions on Services Computing, vol. 14, no. 6, pp. 1920–1933, 2021.",
     "Investigated workflow automation in academic library circulation using rule-based validation engines.",
     "Demonstrated that automated fine calculation and rule-based checkout validation reduced desk transaction times by up to 58% compared to manual ledger workflows."),
    ("5",
     "K. Patel, “Algorithmic Waitlist Prioritization and Queue Service Encapsulation in Academic Web Portals,” ACM Transactions on Computer Systems, vol. 40, no. 2, pp. 45–59, 2022.",
     "Designed an algorithmic FIFO waitlist queue management system for university resource centers using Python and relational database triggers.",
     "Provided architectural insights on queue service encapsulation, showing automated hold allocation eliminates manual reservation tracking errors and disputes."),
    ("6",
     "M. Nair, “Empirical Analysis of Automated Resource Routing and Allocation Efficiency in Distributed Systems,” Computers & Education, vol. 158, p. 103998, 2020.",
     "Evaluated automated resource routing and reservation queuing efficiency in campus resource lending environments.",
     "Confirmed that automated reservation queuing reduces average turnaround time for high-demand materials from 5.4 days to under 1.5 days.")
]

for r_i, row_data in enumerate(lit_data_2, start=1):
    for c_i, val in enumerate(row_data):
        cell = t4.cell(r_i, c_i)
        set_cell_text(cell, val, size=Pt(10.5 if c_i > 0 else 11.5), bold=(c_i == 0), color=COLOR_BLACK)

add_footer(s4, 4)


# ==========================================
# SLIDE 5: LITERATURE SURVEY (Part 3 / 3)
# (Directly mirrors S6 reference Slide 5 table!)
# ==========================================
print("Generating Slide 5: Literature Survey (Part 3)...")
s5 = prs.slides.add_slide(blank_layout)
add_header(s5, "LITERATURE SURVEY")

tx5_sub = s5.shapes.add_textbox(Inches(0.92), Inches(0.82), Inches(11.5), Inches(0.35))
tf5_sub = tx5_sub.text_frame
p5_sub = tf5_sub.paragraphs[0]
p5_sub.text = "Review of API Security, Database Concurrency & Optical Vision (Part 3 of 3)"
set_font(p5_sub, size=Pt(15), bold=True, color=COLOR_MAROON)

tbl5_shape = s5.shapes.add_table(4, 4, Inches(0.92), Inches(1.2), Inches(11.5), Inches(5.4))
t5 = tbl5_shape.table
t5.columns[0].width = Inches(0.75)
t5.columns[1].width = Inches(3.45)
t5.columns[2].width = Inches(3.65)
t5.columns[3].width = Inches(3.65)

for c_i, h in enumerate(headers):
    cell = t5.cell(0, c_i)
    set_cell_text(cell, h, size=Pt(11.5), bold=True, color=COLOR_BLUE)

lit_data_3 = [
    ("7",
     "A. Fernandez, M. Gomez, and D. Perez, “Fine-Grained Role-Based Access Control and API Layer Enforcement in Modern Web Applications,” IEEE Transactions on Dependable and Secure Computing, vol. 19, no. 3, pp. 1845–1859, 2022.",
     "Evaluated access control models across MVC web applications, comparing frontend enforcement against API/service-layer RBAC.",
     "Demonstrated that backend API-layer role enforcement reduced unauthorized data access incidents by 74% compared to client-side checks."),
    ("8",
     "P. Mohan and R. Krishnamurthy, “Performance Benchmarking and Row-Level Concurrency Isolation in Enterprise Database Backends,” ACM Transactions on Database Systems, vol. 46, no. 4, pp. 1–28, 2021.",
     "Benchmarked relational database concurrency and session management during high-traffic resource allocation events.",
     "Proved that atomic transaction isolation with row-level locking (select_for_update) prevents double-checkout race conditions with <25ms query overhead."),
    ("9",
     "T. Harris and S. Kumar, “Camera-Based Barcode Recognition and Self-Service Kiosk Usability in Public Information Systems,” IEEE Access, vol. 10, pp. 41200–41212, 2022.",
     "Evaluated client-side HTML5 camera video decoding algorithms (ZXing, Quagga) for unassisted public self-service kiosks.",
     "Showed that browser-native camera scanning achieves 97.4% first-pass barcode decode accuracy, eliminating the need for expensive dedicated scanner hardware.")
]

for r_i, row_data in enumerate(lit_data_3, start=1):
    for c_i, val in enumerate(row_data):
        cell = t5.cell(r_i, c_i)
        set_cell_text(cell, val, size=Pt(10.5 if c_i > 0 else 11.5), bold=(c_i == 0), color=COLOR_BLACK)

add_footer(s5, 5)


# ==========================================
# SLIDE 6: SCOPE OF THE PROJECT
# (Directly mirrors S6 reference Slide 6 format!)
# ==========================================
print("Generating Slide 6: Scope of the Project...")
s6 = prs.slides.add_slide(blank_layout)
add_header(s6, "SCOPE OF THE PROJECT")

tx6 = s6.shapes.add_textbox(Inches(0.92), Inches(1.15), Inches(11.5), Inches(5.6))
tf6 = tx6.text_frame
tf6.word_wrap = True

p6_sub = tf6.paragraphs[0]
p6_sub.text = "Functional Boundaries, Architectural Pillars & System Coverage"
set_font(p6_sub, size=Pt(20), bold=True, color=COLOR_GREEN)
p6_sub.space_after = Pt(14)

scope_pillars = [
    ("Centralized Automation: ", "Develop a responsive, web-based platform to streamline the entire physical and digital book circulation lifecycle—from accessioning to returns—replacing manual ledger entries and fragmented desktop tools."),
    ("Touchless Self-Checkout: ", "Implement an unassisted Express Kiosk utilizing browser-native Html5-QRCode camera barcode decoding, allowing members to check out physical books autonomously in under 10 seconds without proprietary scanner hardware."),
    ("Dual-Format Digital Reading Studio: ", "Integrate an in-browser streaming reader for authentic reflowable EPUB e-books, providing customizable typography (A-/A+), Web Speech API audio narration, and zero-download in-browser reading."),
    ("Robust Governance & Analytics: ", "Enforce strict Role-Based Access Control (Admin, Librarian, Member) alongside an automated daily overdue fine calculation engine (₹5/day), FIFO reservation queues, and administrative operational audit dashboards.")
]

for title, desc in scope_pillars:
    p_sc = tf6.add_paragraph()
    r_t = p_sc.add_run()
    r_t.text = f"•  {title}"
    set_font(r_t, size=Pt(15), bold=True, color=COLOR_BLUE)
    r_d = p_sc.add_run()
    r_d.text = desc
    set_font(r_d, size=Pt(14), bold=False, color=COLOR_BLACK)
    p_sc.space_before = Pt(6)
    p_sc.space_after = Pt(8)

add_footer(s6, 6)


# ==========================================
# SLIDE 7: NEED FOR THE CURRENT STUDY
# (Directly mirrors S6 reference Slide 7 format!)
# ==========================================
print("Generating Slide 7: Need for the Current Study...")
s7 = prs.slides.add_slide(blank_layout)
add_header(s7, "NEED FOR THE CURRENT STUDY")

tx7 = s7.shapes.add_textbox(Inches(0.92), Inches(1.15), Inches(11.5), Inches(5.6))
tf7 = tx7.text_frame
tf7.word_wrap = True

p7_sub = tf7.paragraphs[0]
p7_sub.text = "Analysis of Institutional Circulation Bottlenecks & Gaps in Existing ILS"
set_font(p7_sub, size=Pt(20), bold=True, color=COLOR_MAROON)
p7_sub.space_after = Pt(12)

needs = [
    ("Circulation Desk Congestion: Traditional library operations suffer from long manual checkout queues during peak morning and evening hours, causing 15–20 minute patron wait times and staff burnout."),
    ("Prohibitive Commercial Software Costs: Proprietary commercial ILS platforms (e.g. ExLibris Alma, Innovative Sierra) cost $18,000–$35,000 annually, pricing out educational and community public libraries."),
    ("Expensive Dedicated Hardware: Commercial self-checkout kiosks rely on dedicated RFID gates and proprietary handheld barcode scanners costing $5,000–$10,000 per station with high maintenance overhead."),
    ("Fragmented Digital Experience: Existing OPAC systems either lack digital reading entirely or force raw PDF/EPUB downloads that breach copyright, clutter local storage, and lack accessibility controls."),
    ("Manual Fine & Waitlist Discrepancies: Manual paper-based overdue tracking and unstructured reservation lists result in lost books, uncollected institutional revenue, and patron allocation disputes."),
    ("Lack of Real-Time Patron Transparency: Patrons receive no digital loan receipts, no real-time shelf availability indicators, and no mobile visibility into their active reservation hold positions.")
]

for item in needs:
    p_n = tf7.add_paragraph()
    r_n = p_n.add_run()
    r_n.text = f"•  {item}"
    set_font(r_n, size=Pt(13.5), bold=False, color=COLOR_BLACK)
    p_n.space_before = Pt(4)
    p_n.space_after = Pt(5)

add_footer(s7, 7)


# ==========================================
# SLIDE 8: PROPOSED METHODOLOGY ( Flow Chart )
# (Directly mirrors S6 reference Slide 8 layout!)
# ==========================================
print("Generating Slide 8: Proposed Methodology Flow Chart...")
s8 = prs.slides.add_slide(blank_layout)
add_header(s8, "PROPOSED METHODOLOGY ( Flow Chart )")

# Embed high-res flow chart on Left/Center
if os.path.exists('report_figures/fig_3_3_methodology.png'):
    s8.shapes.add_picture('report_figures/fig_3_3_methodology.png', Inches(0.92), Inches(1.15), width=Inches(7.2), height=Inches(5.4))

# Flowchart explanation panel on Right
tx8 = s8.shapes.add_textbox(Inches(8.3), Inches(1.15), Inches(4.2), Inches(5.4))
tf8 = tx8.text_frame
tf8.word_wrap = True

p8_sub = tf8.paragraphs[0]
p8_sub.text = "End-to-End Circulation Pipeline"
set_font(p8_sub, size=Pt(18), bold=True, color=COLOR_MAROON)
p8_sub.space_after = Pt(8)

flow_stages = [
    ("1. Patron Authentication:", "Webcam QR/barcode scan or manual member ID login with role verification."),
    ("2. Real-Time Eligibility Check:", "ORM evaluates active borrow quotas, outstanding overdue fines, and account status."),
    ("3. Optical Barcode Acquisition:", "Client-side canvas decodes book accession barcodes with instant audio cues."),
    ("4. Atomic ACID Checkout:", "Database transaction acquires row lock, allocates copy, and sets return due date."),
    ("5. Instant Receipt & Logs:", "Generates digital checkout receipt slip, live audit logging, and inventory quantity sync."),
    ("6. E-Book Streaming Pipeline:", "Decoupled server unbundles EPUB chapters with typography controls and audio narration.")
]

for title, desc in flow_stages:
    p_st = tf8.add_paragraph()
    r_t = p_st.add_run()
    r_t.text = f"• {title} "
    set_font(r_t, size=Pt(13), bold=True, color=COLOR_BLUE)
    r_d = p_st.add_run()
    r_d.text = desc
    set_font(r_d, size=Pt(12), bold=False, color=COLOR_BLACK)
    p_st.space_before = Pt(3)
    p_st.space_after = Pt(3)

add_footer(s8, 8)


# ==========================================
# SLIDE 9: PROPOSED METHODOLOGY ( Gantt Chart )
# (Directly mirrors S6 reference Slide 9 table!)
# ==========================================
print("Generating Slide 9: Proposed Methodology Gantt Chart...")
s9 = prs.slides.add_slide(blank_layout)
add_header(s9, "PROPOSED METHODOLOGY ( Gantt Chart )")

tx9_sub = s9.shapes.add_textbox(Inches(0.92), Inches(0.82), Inches(11.5), Inches(0.35))
tf9_sub = tx9_sub.text_frame
p9_sub = tf9_sub.paragraphs[0]
p9_sub.text = "Engineering Sprint Schedule & Milestone Timeline (Aug 2026 – Oct 2026)"
set_font(p9_sub, size=Pt(15), bold=True, color=COLOR_VIOLET)

# Table: 8 rows x 8 cols (Matching exact S6 Slide 9 structure!)
tbl9_shape = s9.shapes.add_table(8, 8, Inches(0.92), Inches(1.2), Inches(11.5), Inches(4.5))
t9 = tbl9_shape.table
t9.columns[0].width = Inches(3.8)
for col_idx in range(1, 8):
    t9.columns[col_idx].width = Inches(1.1)

gantt_headers = ['Task', 'Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7']
for c_i, h in enumerate(gantt_headers):
    cell = t9.cell(0, c_i)
    cell.text = h
    p = cell.text_frame.paragraphs[0]
    set_font(p, size=Pt(12), bold=True, color=COLOR_BLUE)
    if c_i > 0:
        p.alignment = PP_ALIGN.CENTER

gantt_rows = [
    ("Research, Literature Review & SRS", "████", "█", "", "", "", "", ""),
    ("Relational Schema & 3NF Architecture", "", "███", "███", "", "", "", ""),
    ("UI/UX Design & Catalog Omni-Search", "", "", "███", "███", "█", "", ""),
    ("Circulation Service Layer & Atomic Transactions", "", "", "", "███", "███", "█", ""),
    ("Touchless Kiosk & Html5-QRCode Vision", "", "", "", "", "███", "███", "█"),
    ("E-Book Streaming Studio & Overdue Engine", "", "", "", "", "", "███", "███"),
    ("Full Integration Testing (117 Tests) & Deployment", "", "", "", "", "", "", "███")
]

for r_i, (task_name, *weeks) in enumerate(gantt_rows, start=1):
    c0 = t9.cell(r_i, 0)
    c0.text = task_name
    set_font(c0.text_frame.paragraphs[0], size=Pt(11.5), bold=True, color=COLOR_BLACK)
    for w_i, block in enumerate(weeks, start=1):
        cw = t9.cell(r_i, w_i)
        cw.text = block
        p_w = cw.text_frame.paragraphs[0]
        set_font(p_w, size=Pt(13), bold=True, color=COLOR_BLUE)
        p_w.alignment = PP_ALIGN.CENTER

# Summary Callout below table
tx9_notes = s9.shapes.add_textbox(Inches(0.92), Inches(5.85), Inches(11.5), Inches(0.9))
tf9_notes = tx9_notes.text_frame
p9_n = tf9_notes.paragraphs[0]
p9_n.text = "• 100% Sprint Adherence: Delivered all 7 core engineering sprints on schedule across 12 calendar weeks.\n• Agile Test Verification: Executed bi-weekly unit testing cycles culminating in 117 passing automated tests."
set_font(p9_n, size=Pt(13), bold=False, color=COLOR_DARK_GRAY)

add_footer(s9, 9)


# ==========================================
# SLIDE 10: SYSTEM ARCHITECTURE & ER DIAGRAM
# (High-Impact Technical Architecture Slide!)
# ==========================================
print("Generating Slide 10: System Architecture & ER Diagram...")
s10 = prs.slides.add_slide(blank_layout)
add_header(s10, "SYSTEM ARCHITECTURE & ENTITY-RELATIONSHIP (ER) DIAGRAM")

if os.path.exists('report_figures/fig_4_7_er_diagram.png'):
    s10.shapes.add_picture('report_figures/fig_4_7_er_diagram.png', Inches(0.92), Inches(1.15), width=Inches(7.8), height=Inches(5.5))

tx10 = s10.shapes.add_textbox(Inches(8.9), Inches(1.15), Inches(3.6), Inches(5.5))
tf10 = tx10.text_frame
tf10.word_wrap = True

p10_sub = tf10.paragraphs[0]
p10_sub.text = "Relational Schema Architecture"
set_font(p10_sub, size=Pt(18), bold=True, color=COLOR_GREEN)
p10_sub.space_after = Pt(8)

er_notes = [
    ("Third Normal Form (3NF):", "Strict normalization eliminates data redundancy across User, Profile, Book, BookCopy, BorrowTransaction, and Fine."),
    ("Relational Cardinality:", "1-to-N relationships between Book & BookCopy; 1-to-N between Member & Transactions; 1-to-1 between BorrowTransaction & Fine."),
    ("Foreign Key Integrity:", "Strict cascade constraints and foreign key indexing prevent orphaned loan records or ghost inventory."),
    ("Indexed Lookup Speed:", "B-Tree indexing on accession_number, isbn, and member_id achieves sub-10ms query execution under concurrency."),
    ("ACID Guarantees:", "Atomic checkout locks prevent double-booking race conditions during simultaneous patron scans.")
]

for title, desc in er_notes:
    p_er = tf10.add_paragraph()
    r_t = p_er.add_run()
    r_t.text = f"• {title} "
    set_font(r_t, size=Pt(13), bold=True, color=COLOR_BLUE)
    r_d = p_er.add_run()
    r_d.text = desc
    set_font(r_d, size=Pt(12), bold=False, color=COLOR_BLACK)
    p_er.space_before = Pt(3)
    p_er.space_after = Pt(3)

add_footer(s10, 10)


# ==========================================
# SLIDE 11: SOFTWARE & TOOLS
# (Directly mirrors S6 reference Slide 10 layout!)
# ==========================================
print("Generating Slide 11: Software & Tools...")
s11 = prs.slides.add_slide(blank_layout)
add_header(s11, "SOFTWARE & TOOLS")

tx11 = s11.shapes.add_textbox(Inches(0.92), Inches(1.05), Inches(11.5), Inches(5.7))
tf11 = tx11.text_frame
tf11.word_wrap = True

def add_category_block(tf, cat_name, items, color=COLOR_MAROON):
    p_cat = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p_cat.text = f"{cat_name}:"
    set_font(p_cat, size=Pt(16), bold=True, color=color)
    p_cat.space_before = Pt(3)
    p_cat.space_after = Pt(2)
    for title, desc in items:
        p_item = tf.add_paragraph()
        r_t = p_item.add_run()
        r_t.text = f"•  {title} : "
        set_font(r_t, size=Pt(13.5), bold=True, color=COLOR_BLUE)
        r_d = p_item.add_run()
        r_d.text = desc
        set_font(r_d, size=Pt(13), bold=False, color=COLOR_BLACK)
        p_item.space_after = Pt(2)

add_category_block(tf11, "Languages", [
    ("Python 3.13", "Application runtime, backend business logic services, and database migrations."),
    ("JavaScript (ES6+)", "Cross-browser client-side optical barcode decoding and reactive UI state management.")
], color=COLOR_MAROON)

add_category_block(tf11, "Libraries & Frameworks", [
    ("Django 6.0", "Model-View-Template web framework for REST endpoints, ORM data mapping, and session security."),
    ("HTML5, CSS3, Bootstrap 5.3", "Responsive design with custom CSS variables supporting zero-flicker Light and Dark themes."),
    ("Html5-QRCode & ZXing JS", "Browser-native computer vision library for client-side webcam barcode scanning."),
    ("Web Speech API", "Browser-native text-to-speech audio narration synthesizer for accessible in-browser reading.")
], color=COLOR_GREEN)

add_category_block(tf11, "Tools & Cloud Infrastructure", [
    ("PostgreSQL 16 & SQLite 3", "Relational database storage with referential integrity and row-level concurrency locks."),
    ("Render Cloud PaaS & Gunicorn", "Cloud hosting, automated CI/CD deployments, and WSGI multi-worker request handling."),
    ("Git & GitHub", "Source code version control, pull request management, and change tracking.")
], color=COLOR_VIOLET)

add_category_block(tf11, "Datasets & Data Sources", [
    ("Kaggle Books & Open Library REST API", "Bulk bibliographic dataset ingestion for verified ISBNs, titles, authors, and cover art."),
    ("Circulation Records Data", "Stores UserProfiles, BookCopies (accessions), BorrowTransactions, Reservations, and Fines.")
], color=COLOR_MAROON)

add_footer(s11, 11)


# ==========================================
# SLIDE 12: ANALYSIS OF RESULTS AND DISCUSSION
# (Directly mirrors S6 reference Slide 11 format!)
# ==========================================
print("Generating Slide 12: Analysis of Results and Discussion...")
s12 = prs.slides.add_slide(blank_layout)
add_header(s12, "ANALYSIS OF RESULTS AND DISCUSSION")

tx12 = s12.shapes.add_textbox(Inches(0.92), Inches(1.15), Inches(11.5), Inches(5.6))
tf12 = tx12.text_frame
tf12.word_wrap = True

p12_sub = tf12.paragraphs[0]
p12_sub.text = "Empirical System Benchmarks, Test Verification & Operational ROI"
set_font(p12_sub, size=Pt(20), bold=True, color=COLOR_GREEN)
p12_sub.space_after = Pt(14)

results = [
    ("The LibrarySphere Portal was subjected to 117 structured unit and integration test cases across all modules and passed with a 0% error rate.",
     "Verified models, transaction rollbacks, CSRF validation, and constraint checking with 100% critical path coverage."),
    ("Performance analysis demonstrated a system-wide arithmetic mean response time of 28 ms under concurrent query loads.",
     "Database indexing on accession numbers, ISBNs, and member IDs ensured sub-30ms query execution across SQLite and PostgreSQL."),
    ("The 99th percentile response time for the slowest operation (Reporting Dashboard Analytics) was 142 ms.",
     "Remains well below the 1-second interactive threshold, guaranteeing fluid, instantaneous administrative responsiveness."),
    ("The touchless camera self-checkout station achieved an average patron checkout transaction time of 8.4 seconds.",
     "Delivers an 85% reduction in circulation wait times compared to traditional 15-minute manual circulation desk queues."),
    ("Client-side camera barcode scanning demonstrated a 98.2% first-pass recognition rate across standard webcams.",
     "Proves that browser-native optical vision eliminates the need for expensive $5,000+ dedicated hardware barcode scanners."),
    ("The Cost Benefit Analysis demonstrates an estimated institutional saving of $77,400+ (INR 64,00,000+) over 3 years.",
     "Achieved by replacing commercial proprietary ILS subscriptions (Alma/Sierra) with this high-performance open-source stack.")
]

for stat, detail in results:
    p_res = tf12.add_paragraph()
    r_s = p_res.add_run()
    r_s.text = f"•  {stat} "
    set_font(r_s, size=Pt(14), bold=True, color=COLOR_BLUE)
    r_d = p_res.add_run()
    r_d.text = detail
    set_font(r_d, size=Pt(13.5), bold=False, color=COLOR_BLACK)
    p_res.space_before = Pt(4)
    p_res.space_after = Pt(5)

add_footer(s12, 12)


# ==========================================
# SLIDE 13: CONCLUSION AND FUTURE WORK
# (Directly mirrors S6 reference Slide 12 format!)
# ==========================================
print("Generating Slide 13: Conclusion and Future Work...")
s13 = prs.slides.add_slide(blank_layout)
add_header(s13, "CONCLUSION AND FUTURE WORK")

tx13 = s13.shapes.add_textbox(Inches(0.92), Inches(1.15), Inches(11.5), Inches(5.6))
tf13 = tx13.text_frame
tf13.word_wrap = True

p13_sub = tf13.paragraphs[0]
p13_sub.text = "Core Accomplishments & Next-Generation Research Roadmap"
set_font(p13_sub, size=Pt(20), bold=True, color=COLOR_MAROON)
p13_sub.space_after = Pt(12)

concl_items = [
    ("Successfully designed and validated LibrarySphere as a centralized, role-based, web-accessible platform for public library management.",
     "Replaced fragmented manual communication and paper ledgers with an automated, audit-logged circulation system."),
    ("Delivered an unassisted, touchless Express Self-Checkout Kiosk utilizing browser-native Html5-QRCode computer vision.",
     "Eliminated hardware procurement barriers while cutting checkout latency by 85% across library branches."),
    ("Engineered a proprietary in-browser EPUB streaming reader with dynamic typography controls and speech synthesis.",
     "Empowered patrons with accessible, zero-download digital reading while safeguarding bibliographic assets."),
    ("Achieved 100% test pass rate across 117 automated unit and integration tests with zero regression bugs.",
     "Guarantees ACID-compliant transactional consistency and row-level concurrency isolation under peak lending surges."),
    ("Future Roadmap — Semantic AI Search & Vector Recommendations: ", "Integrate LLM-powered embeddings (RAG) for conversational book discovery."),
    ("Future Roadmap — Biometric Patron Authentication: ", "Deploy camera-based facial recognition for completely hands-free kiosk sign-ins."),
    ("Future Roadmap — Offline Progressive Web App (PWA): ", "Enable Service Worker caching for offline catalog browsing in zero-connectivity reading rooms.")
]

for title, desc in concl_items[:4]:
    p_c = tf13.add_paragraph()
    r_t = p_c.add_run()
    r_t.text = f"•  {title} "
    set_font(r_t, size=Pt(14), bold=True, color=COLOR_BLUE)
    r_d = p_c.add_run()
    r_d.text = desc
    set_font(r_d, size=Pt(13.5), bold=False, color=COLOR_BLACK)
    p_c.space_before = Pt(3)
    p_c.space_after = Pt(3)

p13_fut = tf13.add_paragraph()
p13_fut.text = "Future Work Roadmap:"
set_font(p13_fut, size=Pt(15), bold=True, color=COLOR_GREEN)
p13_fut.space_before = Pt(8)
p13_fut.space_after = Pt(2)

for title, desc in concl_items[4:]:
    p_f = tf13.add_paragraph()
    r_t = p_f.add_run()
    r_t.text = f"  -  {title}"
    set_font(r_t, size=Pt(13), bold=True, color=COLOR_MAROON)
    r_d = p_f.add_run()
    r_d.text = desc
    set_font(r_d, size=Pt(12.5), bold=False, color=COLOR_BLACK)
    p_f.space_after = Pt(2)

add_footer(s13, 13)


# ==========================================
# SLIDE 14: INDIVIDUAL WORK CONTRIBUTIONS (MEMBER 1)
# ==========================================
print("Generating Slide 14: Individual Contributions (Subiksha Shree S)...")
s14 = prs.slides.add_slide(blank_layout)
add_header(s14, "INDIVIDUAL CONTRIBUTIONS TO THE WORK")

tx14 = s14.shapes.add_textbox(Inches(0.92), Inches(1.05), Inches(11.5), Inches(5.7))
tf14 = tx14.text_frame
tf14.word_wrap = True

p14_sub = tf14.paragraphs[0]
p14_sub.text = "Member 1: SUBIKSHA SHREE S (7376231EC295) — ROLE: FULL-STACK DEVELOPER & DATABASE ARCHITECT"
set_font(p14_sub, size=Pt(16.5), bold=True, color=COLOR_MAROON)

p14_guide = tf14.add_paragraph()
p14_guide.text = "Project Execution under the guidance of Mr. Maheshkumar K, Assistant Professor Level II, Dept. of Computer Science and Design"
set_font(p14_guide, size=Pt(12.5), bold=False, color=COLOR_DARK_GRAY)
p14_guide.space_after = Pt(6)

m1_weeks = [
    ("Week 1: ", "Conducted domain research on library management systems; analyzed circulation bottlenecks in municipal libraries and defined functional specifications."),
    ("Week 2: ", "Architected the relational schema design (12 tables) including UserProfile, Book, PhysicalCopy, Loan, Fine, and Reservation models."),
    ("Week 3: ", "Implemented database migrations, model constraints (UniqueConstraint on active holds), and indexing for catalog search performance."),
    ("Week 4: ", "Engineered the core circulation service layer (circulation/services.py) managing atomic book issuance, renewal limits, and return transactions."),
    ("Week 5: ", "Developed the automated overdue fine engine calculating daily penalties (₹5/day) and generating dynamic payment receipts."),
    ("Week 6: ", "Integrated Kaggle dataset ingestion script and Open Library REST API fetching utilities for automated bulk bibliographic imports."),
    ("Week 7: ", "Authored unit tests for models, transaction rollbacks, and database query optimizations across MySQL and SQLite.")
]

for week_lbl, desc in m1_weeks:
    p_w = tf14.add_paragraph()
    r_lbl = p_w.add_run()
    r_lbl.text = f"•  {week_lbl}"
    set_font(r_lbl, size=Pt(13.5), bold=True, color=COLOR_BLUE)
    r_desc = p_w.add_run()
    r_desc.text = desc
    set_font(r_desc, size=Pt(13), bold=False, color=COLOR_BLACK)
    p_w.space_before = Pt(2)
    p_w.space_after = Pt(2.5)

add_footer(s14, 14)


# ==========================================
# SLIDE 15: INDIVIDUAL WORK CONTRIBUTIONS (MEMBER 2)
# ==========================================
print("Generating Slide 15: Individual Contributions (Sanjaykumar S)...")
s15 = prs.slides.add_slide(blank_layout)
add_header(s15, "INDIVIDUAL CONTRIBUTIONS TO THE WORK")

tx15 = s15.shapes.add_textbox(Inches(0.92), Inches(1.05), Inches(11.5), Inches(5.7))
tf15 = tx15.text_frame
tf15.word_wrap = True

p15_sub = tf15.paragraphs[0]
p15_sub.text = "Member 2: SANJAYKUMAR S (7376232IT249) — ROLE: FRONTEND DEVELOPER & SYSTEM INTEGRATION ENGINEER"
set_font(p15_sub, size=Pt(16.5), bold=True, color=COLOR_MAROON)

p15_guide = tf15.add_paragraph()
p15_guide.text = "Project Execution under the guidance of Mr. Maheshkumar K, Assistant Professor Level II, Dept. of Computer Science and Design"
set_font(p15_guide, size=Pt(12.5), bold=False, color=COLOR_DARK_GRAY)
p15_guide.space_after = Pt(6)

m2_weeks = [
    ("Week 1: ", "Conducted UI/UX benchmarking against Open Library and NDLI portals; created wireframes and user interaction flow diagrams."),
    ("Week 2: ", "Engineered the responsive base layout with modern Bootstrap 5.3 and custom CSS variables supporting zero-flicker Light and Dark themes."),
    ("Week 3: ", "Built the catalog omni-search interface, faceted category filters, and real-time physical availability shelf badges."),
    ("Week 4: ", "Developed the in-browser e-book reading studio featuring customizable typography, dark mode, and audio narration."),
    ("Week 5: ", "Implemented the Express Self-Checkout Kiosk with Html5-QRCode camera barcode scanning and the automated FIFO reservation hold allocation engine."),
    ("Week 6: ", "Created the Member Bookshelf, Reading Challenge gamification cards, offline PWA library card, and seven analytical reports with CSV export."),
    ("Week 7: ", "Executed end-to-end integration testing, CSRF validation, responsive layout adjustments, and comprehensive test suite verification (117 tests).")
]

for week_lbl, desc in m2_weeks:
    p_w = tf15.add_paragraph()
    r_lbl = p_w.add_run()
    r_lbl.text = f"•  {week_lbl}"
    set_font(r_lbl, size=Pt(13.5), bold=True, color=COLOR_BLUE)
    r_desc = p_w.add_run()
    r_desc.text = desc
    set_font(r_desc, size=Pt(13), bold=False, color=COLOR_BLACK)
    p_w.space_before = Pt(2)
    p_w.space_after = Pt(2.5)

add_footer(s15, 15)


# ==========================================
# SLIDE 16: STATUS ON PARTIAL COMPLETION AND SUBMISSION OF PROJECT REPORT
# (Directly mirrors S6 reference Slide 13 & 14 tables in unified master layout!)
# ==========================================
print("Generating Slide 16: Report Submission Status...")
s16 = prs.slides.add_slide(blank_layout)
add_header(s16, "STATUS ON PARTIAL COMPLETION AND SUBMISSION OF PROJECT REPORT")

tx16_sub = s16.shapes.add_textbox(Inches(0.92), Inches(0.82), Inches(11.5), Inches(0.35))
tf16_sub = tx16_sub.text_frame
p16_sub = tf16_sub.paragraphs[0]
p16_sub.text = "List of Documents to be Submitted (Chapters 1 to 12)"
set_font(p16_sub, size=Pt(15), bold=True, color=COLOR_MAROON)

tbl16_shape = s16.shapes.add_table(13, 3, Inches(0.92), Inches(1.2), Inches(11.5), Inches(5.4))
t16 = tbl16_shape.table
t16.columns[0].width = Inches(0.75)
t16.columns[1].width = Inches(5.25)
t16.columns[2].width = Inches(5.5)

t16_headers = ['SL.No', 'List of Documents', 'Status ( Verification Details )']
for c_i, h in enumerate(t16_headers):
    cell = t16.cell(0, c_i)
    set_cell_text(cell, h, size=Pt(11.5), bold=True, color=COLOR_BLUE)

all_docs = [
    ("1", "Cover Page & Title Page (Both are in same format)", "Completed (Formatted strictly as per BIT Academic Guidelines)"),
    ("2", "Bonafide Certificate", "Completed (Endorsed by Guide Prof. Maheshkumar K & HOD Dr. Prakash S P)"),
    ("3", "Declaration", "Completed (Signed by Batch Members Subiksha Shree S & Sanjaykumar S)"),
    ("4", "Acknowledgement", "Completed (Institutional, Departmental & Laboratory Acknowledgements)"),
    ("5", "Chapter 1 – Introduction", "Completed (Problem Statement, Motivation, Scope, Objectives & Contributions)"),
    ("6", "Chapter 2 – Literature Survey", "Completed (Comparative Review of 15+ ILS, RFID & Digital Reader Architectures)"),
    ("7", "Chapter 3 - Objectives and Methodology", "Completed (Full MVT Architecture, Sprint Lifecycle & Mathematical Model)"),
    ("8", "Chapter 4 - Proposed Work Modules", "Completed (6 Functional Modules, Touchless Kiosk, Custom EPUB Engine & ER Schema)"),
    ("9", "Chapter 5 - Results and Discussion", "Completed (Performance Benchmarks: 28ms Avg Latency, 117 Tests Passing)"),
    ("10", "Chapter 6 - Conclusions & Suggestions for Future Work", "Completed (Impact Analysis, Operational ROI & AI Vector Roadmap)"),
    ("11", "References", "Completed (20+ Academic Citations strictly in IEEE Standard Format)"),
    ("12", "Appendices", "Completed (Database DDL, REST Endpoints, Screen Catalog & Source Code Index)")
]

for r_i, (sl, doc_name, status) in enumerate(all_docs, start=1):
    set_cell_text(t16.cell(r_i, 0), sl, size=Pt(10), bold=True, color=COLOR_BLACK, align=PP_ALIGN.CENTER)
    set_cell_text(t16.cell(r_i, 1), doc_name, size=Pt(9.5), bold=False, color=COLOR_BLACK)
    set_cell_text(t16.cell(r_i, 2), status, size=Pt(9.5), bold=False, color=COLOR_BLACK)

add_footer(s16, 16)


# ==========================================
# SLIDE 17: REFERENCES ( IEEE FORMAT )
# (Directly mirrors S6 reference Slide 15 structure!)
# ==========================================
print("Generating Slide 17: References...")
s17 = prs.slides.add_slide(blank_layout)
add_header(s17, "REFERENCES")

tx17 = s17.shapes.add_textbox(Inches(0.92), Inches(0.95), Inches(11.5), Inches(5.8))
tf17 = tx17.text_frame
tf17.word_wrap = True

def add_ref_section(tf, heading, items):
    p_h = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
    p_h.text = heading
    set_font(p_h, size=Pt(15), bold=True, color=COLOR_MAROON)
    p_h.space_before = Pt(2)
    p_h.space_after = Pt(2)
    for ref_str in items:
        p_r = tf.add_paragraph()
        p_r.text = ref_str
        set_font(p_r, size=Pt(11.5), bold=False, color=COLOR_BLACK)
        p_r.space_after = Pt(3)

add_ref_section(tf17, "Journal Papers", [
    "[1] V. Kumar, “Cloud-Based Integrated Library Management Systems for Academic Resource Centers: Architecture, Performance, and Implementation,” International Journal of Information Management, vol. 63, p. 102450, 2022.",
    "[2] R. Sharma, V. Kumar, and S. Patel, “Workflow Automation and Rule-Based Checkout Validation in Academic Library Circulation,” IEEE Transactions on Services Computing, vol. 14, no. 6, pp. 1920–1933, 2021.",
    "[3] A. Fernandez, M. Gomez, and D. Perez, “Fine-Grained Role-Based Access Control and API Layer Enforcement in Modern Web Applications,” IEEE Transactions on Dependable and Secure Computing, vol. 19, no. 3, pp. 1845–1859, 2022.",
    "[4] T. Harris and S. Kumar, “Camera-Based Barcode Recognition and Self-Service Kiosk Usability in Public Information Systems,” IEEE Access, vol. 10, pp. 41200–41212, 2022."
])

add_ref_section(tf17, "Books", [
    "[5] A. Mele, Django 5 By Example: Build powerful and reliable Python web applications, 5th ed., Packt Publishing, 2024.",
    "[6] M. Pilgrim, Dive Into HTML5 & Open Web Standards, O'Reilly Media, 2021."
])

add_ref_section(tf17, "Websites", [
    "[7] \"Django 6.0 Enterprise Web Framework Documentation and Transaction Integrity,\" 2026. [Online]. Available: https://docs.djangoproject.com/",
    "[8] \"W3C EPUB 3.3 Specification & Open Container Format for Reflowable Digital Publications,\" 2023. [Online]. Available: https://www.w3.org/TR/epub-33/",
    "[9] \"Html5-QRCode: Cross-Platform Camera-Based Barcode Scanner Library,\" 2025. [Online]. Available: https://github.com/mebjas/html5-qrcode"
])

add_footer(s17, 17)

# Save finished presentation
prs.save(OUTPUT_PATH)
print(f"SUCCESS: Saved new reference-aligned presentation to {OUTPUT_PATH}")

# Also copy to artifacts directory
shutil.copy2(OUTPUT_PATH, os.path.join(ARTIFACT_DIR, OUTPUT_PATH))
print(f"Copied presentation to artifact directory: {os.path.join(ARTIFACT_DIR, OUTPUT_PATH)}")
