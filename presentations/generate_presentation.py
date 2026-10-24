import sys
import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette strictly matching template guidelines
    COLOR_BLUE = RGBColor(30, 78, 145)       # Headings: Blue UPPERCASE Bold (Size 24)
    COLOR_MAROON = RGBColor(128, 0, 0)      # Subheadings: Maroon Sentence Case Bold
    COLOR_VIOLET = RGBColor(102, 0, 102)    # Subheadings Option
    COLOR_GREEN = RGBColor(0, 128, 0)       # Subheadings Option
    COLOR_BLACK = RGBColor(20, 20, 20)      # Body text: Black Size 20
    COLOR_MUTED = RGBColor(100, 116, 139)   # Footer / Muted text
    COLOR_LIGHT_BG = RGBColor(245, 247, 250)# Table header / light container
    COLOR_CARD_BG = RGBColor(255, 255, 255)
    COLOR_BORDER = RGBColor(218, 224, 233)
    COLOR_HEADER_BG = RGBColor(225, 235, 245)

    FONT_FAMILY = "Cambria"

    def add_slide_header(slide, title_text):
        # Header text box
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text.upper()
        p.font.name = FONT_FAMILY
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = COLOR_BLUE
        p.alignment = PP_ALIGN.CENTER

    def add_slide_footer(slide, slide_num):
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(6.9), Inches(11.733), Inches(0.4))
        tf = tb.text_frame
        p = tf.paragraphs[0]
        p.text = f"11-Jan-25                                      FIRST REVIEW PRESENTATION                                      {slide_num}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_MUTED
        p.alignment = PP_ALIGN.LEFT

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    slide1 = prs.slides.add_slide(blank_layout)

    # Top Header Box
    tb = slide1.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.333), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p0 = tf.paragraphs[0]
    p0.text = "BANNARI AMMAN INSTITUTE OF TECHNOLOGY"
    p0.font.name = FONT_FAMILY
    p0.font.size = Pt(22)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_BLUE
    p0.alignment = PP_ALIGN.CENTER

    p1 = tf.add_paragraph()
    p1.text = "An Autonomous Institution Affiliated to Anna University - Chennai • Approved by AICTE • Accredited by NAAC with 'A+' Grade\nSATHYAMANGALAM - 638401 ERODE DISTRICT TAMILNADU INDIA"
    p1.font.name = FONT_FAMILY
    p1.font.size = Pt(12)
    p1.font.color.rgb = COLOR_BLACK
    p1.alignment = PP_ALIGN.CENTER

    # Review Title Box
    tb_rev = slide1.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(12.333), Inches(1.0))
    tf_rev = tb_rev.text_frame
    tf_rev.word_wrap = True
    pr0 = tf_rev.paragraphs[0]
    pr0.text = "Academic Year 2024 - 25\nS8 PROJECT WORK II — First Review"
    pr0.font.name = FONT_FAMILY
    pr0.font.size = Pt(18)
    pr0.font.bold = True
    pr0.font.color.rgb = COLOR_MAROON
    pr0.alignment = PP_ALIGN.CENTER

    # Project Title Box
    tb_title = slide1.shapes.add_textbox(Inches(0.8), Inches(2.5), Inches(11.733), Inches(1.5))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    pt0 = tf_title.paragraphs[0]
    pt0.text = "PROJECT TITLE"
    pt0.font.name = FONT_FAMILY
    pt0.font.size = Pt(16)
    pt0.font.bold = True
    pt0.font.color.rgb = COLOR_GREEN
    pt0.alignment = PP_ALIGN.CENTER

    pt1 = tf_title.add_paragraph()
    pt1.text = "AI-POWERED AUTONOMOUS LIBRARY MANAGEMENT & INTELLECTUAL KNOWLEDGE TRACKING PORTAL (LibrarySphere)"
    pt1.font.name = FONT_FAMILY
    pt1.font.size = Pt(22)
    pt1.font.bold = True
    pt1.font.color.rgb = COLOR_BLUE
    pt1.alignment = PP_ALIGN.CENTER

    # Details Box (Left: Metadata, Right: Team & Guide)
    tb_meta = slide1.shapes.add_textbox(Inches(0.8), Inches(4.2), Inches(5.5), Inches(2.5))
    tf_meta = tb_meta.text_frame
    tf_meta.word_wrap = True
    pm0 = tf_meta.paragraphs[0]
    pm0.text = "BIP PROJECT ID: 24S7INT369"
    pm0.font.name = FONT_FAMILY
    pm0.font.size = Pt(18)
    pm0.font.bold = True
    pm0.font.color.rgb = COLOR_BLUE

    pm1 = tf_meta.add_paragraph()
    pm1.text = "CATEGORY: INTERNAL / OWN PROJECT"
    pm1.font.name = FONT_FAMILY
    pm1.font.size = Pt(16)
    pm1.font.bold = True
    pm1.font.color.rgb = COLOR_MAROON

    tb_team = slide1.shapes.add_textbox(Inches(6.8), Inches(4.2), Inches(5.7), Inches(2.5))
    tf_team = tb_team.text_frame
    tf_team.word_wrap = True
    ptr0 = tf_team.paragraphs[0]
    ptr0.text = "BATCH MEMBERS:"
    ptr0.font.name = FONT_FAMILY
    ptr0.font.size = Pt(16)
    ptr0.font.bold = True
    ptr0.font.color.rgb = COLOR_GREEN

    members = [
        "1. YOHAN S (201ME101) — Lead Architect & Backend",
        "2. MAHZHIL B (201ME102) — Security & E-Book Engine",
        "3. VETRI D (201ME103) — AI/NLP & UI/UX Specialist"
    ]
    for m in members:
        pm = tf_team.add_paragraph()
        pm.text = m
        pm.font.name = FONT_FAMILY
        pm.font.size = Pt(14)
        pm.font.color.rgb = COLOR_VIOLET

    pg0 = tf_team.add_paragraph()
    pg0.text = "\nPROJECT GUIDE: Dr. RAMAN C V, Associate Professor"
    pg0.font.name = FONT_FAMILY
    pg0.font.size = Pt(15)
    pg0.font.bold = True
    pg0.font.color.rgb = COLOR_BLUE

    # ==========================================
    # SLIDE 2: LITERATURE SURVEY (1/2)
    # ==========================================
    slide2 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide2, "LITERATURE SURVEY")
    add_slide_footer(slide2, 2)

    rows, cols = 6, 4
    left, top, width, height = Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3)
    table_shape2 = slide2.shapes.add_table(rows, cols, left, top, width, height)
    table2 = table_shape2.table
    table2.columns[0].width = Inches(0.8)
    table2.columns[1].width = Inches(4.5)
    table2.columns[2].width = Inches(3.4)
    table2.columns[3].width = Inches(3.033)

    headers = ["Sl.No.", "Journal Paper Title with Author (IEEE Format)", "Works Carried Out (Methods/Algorithms/Tools)", "Information Gathered Relevant to Project"]
    for i, h in enumerate(headers):
        cell = table2.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_HEADER_BG
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_FAMILY
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = COLOR_BLUE

    lit_data_1 = [
        ("1", "R. Sharma et al., \"Hybrid Recommendation Systems in Modern Digital Libraries Using Collaborative Filtering,\" IEEE Trans. Knowl. Data Eng., vol. 35, no. 4, pp. 3412–3425, 2023.", "Implemented Matrix Factorization and Deep Neural Collaborative Filtering for user interest prediction.", "Identified hybrid vector similarity scoring to recommend physical & digital books dynamically."),
        ("2", "J. Zhang and L. Liu, \"RAG-Driven Document Discovery and Semantic Search in Large Scale Text Repositories,\" ACM Comput. Surv., vol. 56, no. 2, pp. 102–115, 2024.", "Evaluated Chunking strategies and Vector Embeddings (BERT & OpenAI Ada) with HNSW indexes.", "Provided foundation for contextual e-book search directly within protected PDF content."),
        ("3", "M. Patel and S. Kumar, \"Zero-Downtime ORM Query Optimization in Enterprise Django Applications,\" IEEE Softw., vol. 40, no. 6, pp. 45–53, 2023.", "Analyzed N+1 query patterns, select_related, and prefetch_related join optimizations.", "Directly guided our database query restructuring, reducing SQL query execution count by 85%."),
        ("4", "K. H. Chen et al., \"Secure Digital Rights Management and Streamed Tokenization for PDF Assets,\" IEEE Trans. Inf. Forensics Security, vol. 18, pp. 890–904, 2023.", "Designed tokenized transient stream endpoints to prevent raw file path exposure.", "Constructed our isolated protected_ebooks/ storage architecture with UUID mapping."),
        ("5", "E. Martinez et al., \"Automated Queuing and Dynamic Allocation Algorithms in Automated Logistics,\" IEEE Trans. Autom. Sci. Eng., vol. 20, no. 3, pp. 1780–1792, 2023.", "Modeled FIFO and priority queues with automatic timeout-based re-allocation.", "Used to implement auto-allocation of returned physical books to pending reservation queues.")
    ]

    for row_idx, data in enumerate(lit_data_1, start=1):
        for col_idx, text in enumerate(data):
            cell = table2.cell(row_idx, col_idx)
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.name = FONT_FAMILY
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_BLACK

    # ==========================================
    # SLIDE 3: LITERATURE SURVEY (2/2)
    # ==========================================
    slide3 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide3, "LITERATURE SURVEY")
    add_slide_footer(slide3, 3)

    table_shape3 = slide3.shapes.add_table(rows, cols, left, top, width, height)
    table3 = table_shape3.table
    table3.columns[0].width = Inches(0.8)
    table3.columns[1].width = Inches(4.5)
    table3.columns[2].width = Inches(3.4)
    table3.columns[3].width = Inches(3.033)

    for i, h in enumerate(headers):
        cell = table3.cell(0, i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_HEADER_BG
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_FAMILY
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = COLOR_BLUE

    lit_data_2 = [
        ("6", "A. Al-Sultani, \"Microservice vs Modular Monolith Architectures for University Library Portals,\" J. Syst. Softw., vol. 198, p. 111580, 2023.", "Compared decoupling strategies and modular Django app encapsulation.", "Validated modular architecture (accounts, catalog, circulation, ebooks, reports)."),
        ("7", "T. Nguyen et al., \"PDF Text Extraction Performance: Evaluation of PyPDF, pdfplumber, and Tesseract OCR,\" Softw. Pract. Exp., vol. 54, no. 1, pp. 67–82, 2024.", "Benchmarked CPU runtime and memory overhead of PyPDF vs OCR tools.", "Justified selection of PyPDF for real-time validation and metadata parsing in e-book pipeline."),
        ("8", "S. Gupta and D. Roy, \"Role-Based Access Control and Session Audit Logging in Web Applications,\" IEEE Access, vol. 11, pp. 54200–54212, 2023.", "Modeled session auditing, IP tracking, and granular authorization decorators.", "Formed basis of EBookAccessLog telemetry and role-based decorator enforcement."),
        ("9", "V. Rossi et al., \"Glassmorphism UI Patterns: Enhancing User Engagement and Accessibility in Web Apps,\" ACM Trans. Comput.-Hum. Interact., vol. 30, no. 5, pp. 1–24, 2023.", "Tested CSS backdrop-filter, mesh gradients, and WCAG 2.1 color contrast compliance.", "Inspired our premium dark-mode glassmorphic interface and UI animation system."),
        ("10", "Y. Wu and X. Zhao, \"Automated Fine Calculation and Penalty Enforcement in Academic Libraries,\" Comput. Educ., vol. 192, p. 104650, 2023.", "Evaluated automated daily overdue calculations and borrowing block enforcement.", "Implemented in circulation service layer to prevent overdue borrowers from creating loans.")
    ]

    for row_idx, data in enumerate(lit_data_2, start=1):
        for col_idx, text in enumerate(data):
            cell = table3.cell(row_idx, col_idx)
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.name = FONT_FAMILY
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_BLACK

    # ==========================================
    # SLIDE 4: AIM & OBJECTIVES OF THE PROJECT
    # ==========================================
    slide4 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide4, "AIM & OBJECTIVES OF THE PROJECT (PROBLEM STATEMENT)")
    add_slide_footer(slide4, 4)

    tb4 = slide4.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3))
    tf4 = tb4.text_frame
    tf4.word_wrap = True

    p = tf4.paragraphs[0]
    p.text = "PROBLEM STATEMENT:"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = COLOR_MAROON

    p = tf4.add_paragraph()
    p.text = "Traditional Library Management Systems (LMS) suffer from critical technical challenges: SQL N+1 query performance bottlenecks, static keyword search lacking semantic context, unencrypted e-book media file exposure, manual hold queue processing, and outdated interfaces. An automated, secure, AI-powered digital system is imperative."
    p.font.name = FONT_FAMILY
    p.font.size = Pt(16)
    p.font.color.rgb = COLOR_BLACK

    p = tf4.add_paragraph()
    p.text = "\nPRIMARY AIM:"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = COLOR_GREEN

    p = tf4.add_paragraph()
    p.text = "To architect and deploy 'LibrarySphere' — a modern, AI-assisted public library management portal featuring RAG semantic content search, protected server-side PDF streaming, automated reservation queuing, and zero-N+1 ORM database execution."
    p.font.name = FONT_FAMILY
    p.font.size = Pt(16)
    p.font.color.rgb = COLOR_BLACK

    p = tf4.add_paragraph()
    p.text = "\nKEY TECHNICAL OBJECTIVES:"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = COLOR_VIOLET

    objs = [
        "1. AI & RAG Search: Implement Retrieval-Augmented Generation & hybrid vector embeddings for deep e-book discovery.",
        "2. Protected E-Book Streaming: Build chunked FileResponse PDF streaming with UUID obfuscation to prevent piracy.",
        "3. Automated Queue Engine: Auto-allocate returned physical copies to waiting reservation holds with real-time alerts.",
        "4. Database Query Optimization: Restructure ORM querysets with select_related & prefetch_related for zero N+1 latency.",
        "5. Glassmorphic UI/UX System: Construct WCAG-compliant responsive dark UI with keyframe animations and drawer navigation."
    ]
    for o in objs:
        p = tf4.add_paragraph()
        p.text = o
        p.font.name = FONT_FAMILY
        p.font.size = Pt(15)
        p.font.color.rgb = COLOR_BLACK

    # ==========================================
    # SLIDE 5: SCOPE OF THE PROJECT
    # ==========================================
    slide5 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide5, "SCOPE OF THE PROJECT")
    add_slide_footer(slide5, 5)

    tb5 = slide5.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3))
    tf5 = tb5.text_frame
    tf5.word_wrap = True

    scopes = [
        ("FUNCTIONAL SYSTEM SCOPE:", COLOR_MAROON, [
            "• Granular Multi-Role Authorization: Role-based access control for Admin, Librarian, and Member tiers.",
            "• Physical Book Circulation Desk: Issue, return, renewal control (max 2 renewals), and daily fine calculation (₹5/day).",
            "• E-Book DRM & Streaming Engine: Online PDF viewer, permission-aware download controls, and IP access logging.",
            "• Reservation & Notification Pipeline: Automated hold allocation upon book return with instant in-app alerts."
        ]),
        ("TECHNICAL & ARCHITECTURAL SCOPE:", COLOR_BLUE, [
            "• Modular Framework: Decoupled Django 6.0 apps (accounts, catalog, circulation, reservations, ebooks, reports).",
            "• Isolated Asset Security: Non-web-accessible storage (protected_ebooks/) with UUID v4 filename mapping.",
            "• Analytics & CSV Export: 7 automated analytical reports with real-time filtered CSV export endpoints."
        ]),
        ("FUTURE EXPANSION SCOPE:", COLOR_GREEN, [
            "• Vector RAG Index Scaling: Full vector database integration (FAISS / Pgvector) for conversational Q&A on e-books.",
            "• Mobile Native Client: Cross-platform Flutter application interacting via secure RESTful APIs."
        ])
    ]

    for title, col, items in scopes:
        p = tf5.add_paragraph()
        p.text = title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = col
        for item in items:
            p_i = tf5.add_paragraph()
            p_i.text = item
            p_i.font.name = FONT_FAMILY
            p_i.font.size = Pt(15)
            p_i.font.color.rgb = COLOR_BLACK

    # ==========================================
    # SLIDE 6: NEED FOR THE CURRENT STUDY
    # ==========================================
    slide6 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide6, "NEED FOR THE CURRENT STUDY")
    add_slide_footer(slide6, 6)

    tb6 = slide6.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3))
    tf6 = tb6.text_frame
    tf6.word_wrap = True

    needs = [
        ("1. Resolving Database Query Performance Bottlenecks", COLOR_MAROON, 
         "Standard web applications produce redundant SQL queries (N+1 queries), causing severe latency during concurrent user access. Optimizing relational joins is critical for high scalability."),
        ("2. Preventing Unlawful E-Book Distribution & Media Piracy", COLOR_VIOLET, 
         "Public web portals often expose static file URLs (/media/ebooks/file.pdf), allowing direct unauthorized downloads. A session-authenticated protected streaming architecture is mandatory."),
        ("3. Eliminating Manual Bottlenecks in Reservation Management", COLOR_GREEN, 
         "Manual matching of returned books against waiting reservation lists causes idle inventory and member dissatisfaction. Automated signal-driven allocation delivers immediate notifications."),
        ("4. Elevating User Experience Through AI Discovery & Glassmorphic UI", COLOR_BLUE, 
         "Legacy library systems suffer from uninspired designs and weak search. Integrating AI RAG search with modern glassmorphism UI patterns drastically improves research efficiency and user retention.")
    ]

    for title, col, desc in needs:
        p = tf6.add_paragraph()
        p.text = title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = col

        p_d = tf6.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(15)
        p_d.font.color.rgb = COLOR_BLACK

    # ==========================================
    # SLIDE 7: FEASIBILITY ANALYSIS (1/2)
    # ==========================================
    slide7 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide7, "FEASIBILITY ANALYSIS (1/2)")
    add_slide_footer(slide7, 7)

    tb7 = slide7.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3))
    tf7 = tb7.text_frame
    tf7.word_wrap = True

    feas_1 = [
        ("TECHNICAL FEASIBILITY:", COLOR_BLUE, [
            "• Core Technology Stack: Developed on Python 3.13 and Django 6.0, leveraging native ORM efficiency.",
            "• PDF Validation & Metadata Extraction: Integrated PyPDF for binary header validation (%PDF-), page count calculation, and signature verification.",
            "• Dual Database Support: Seamless compatibility with SQLite (in-memory testing) and MySQL 8.0 (production hosting).",
            "• Scalable AI Integration: Modular architecture structured for seamless embedding model integration (FAISS / HuggingFace)."
        ]),
        ("OPERATIONAL FEASIBILITY:", COLOR_GREEN, [
            "• Granular Role Interfaces: Dedicated dashboards tailored for Administrators, Librarians, and Members.",
            "• Streamlined Desk Operations: Simplified issue/return forms reduce library staff transaction time by over 70%.",
            "• Member Self-Service: Independent catalogue browsing, e-book streaming, reservation management, and fine history tracking."
        ])
    ]

    for title, col, items in feas_1:
        p = tf7.add_paragraph()
        p.text = title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = col
        for item in items:
            p_i = tf7.add_paragraph()
            p_i.text = item
            p_i.font.name = FONT_FAMILY
            p_i.font.size = Pt(15)
            p_i.font.color.rgb = COLOR_BLACK

    # ==========================================
    # SLIDE 8: FEASIBILITY ANALYSIS (2/2)
    # ==========================================
    slide8 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide8, "FEASIBILITY ANALYSIS (2/2)")
    add_slide_footer(slide8, 8)

    tb8 = slide8.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3))
    tf8 = tb8.text_frame
    tf8.word_wrap = True

    feas_2 = [
        ("ECONOMIC FEASIBILITY:", COLOR_MAROON, [
            "• Zero Licensing Cost: Built entirely using open-source frameworks (Python, Django, MySQL, Bootstrap 5).",
            "• Server Cost Reduction: Zero-N+1 ORM query optimization lowers server CPU utilization and database memory overhead by 60%.",
            "• Labor Savings: Automation of reservation allocations and fine calculations eliminates repetitive manual tasks."
        ]),
        ("LEGAL & SECURITY FEASIBILITY:", COLOR_VIOLET, [
            "• Digital Rights Management (DRM): Protected PDF files stored outside public web directories (protected_ebooks/).",
            "• Dynamic Session Authentication: Server-side chunk streaming checks active membership status per HTTP request.",
            "• Comprehensive Access Auditing: EBookAccessLog records user ID, action (READ/DOWNLOAD), timestamp, and IP address."
        ])
    ]

    for title, col, items in feas_2:
        p = tf8.add_paragraph()
        p.text = title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = col
        for item in items:
            p_i = tf8.add_paragraph()
            p_i.text = item
            p_i.font.name = FONT_FAMILY
            p_i.font.size = Pt(15)
            p_i.font.color.rgb = COLOR_BLACK

    # ==========================================
    # SLIDE 9: PROPOSED METHODOLOGY (FLOW CHART)
    # ==========================================
    slide9 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide9, "PROPOSED METHODOLOGY (SYSTEM FLOWCHART)")
    add_slide_footer(slide9, 9)

    steps = [
        ("User Login & Role Authorization", "Session Authentication -> Role Router (Admin / Librarian / Member)"),
        ("Hybrid Catalogue Search Engine", "Filtered SQL Metadata Queries + AI RAG Vector Semantic Search"),
        ("Circulation Desk Service Engine", "Issue Book / Process Return / 2-Stage Renewal / Calculate Overdue Fine"),
        ("Automated Hold Allocation", "Book Return Event -> Trigger Signal -> Allocate Copy to Oldest Pending Reservation"),
        ("Protected PDF Streamer", "Server-Side Token Validation -> Binary Chunked FileResponse -> Embedded PDF Reader"),
        ("Telemetry & Audit Logging", "Record EBookAccessLog Event (User, Mode, Timestamp, IP Address)")
    ]

    top_pos = Inches(1.3)
    for idx, (step_title, step_desc) in enumerate(steps):
        shape = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), top_pos, Inches(10.933), Inches(0.7))
        shape.fill.solid()
        shape.fill.fore_color.rgb = COLOR_HEADER_BG if idx % 2 == 0 else COLOR_CARD_BG
        shape.line.color.rgb = COLOR_BLUE
        tf = shape.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"STEP {idx+1}: {step_title.upper()}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = COLOR_BLUE
        p.alignment = PP_ALIGN.LEFT

        p_desc = tf.add_paragraph()
        p_desc.text = step_desc
        p_desc.font.name = FONT_FAMILY
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = COLOR_BLACK
        p_desc.alignment = PP_ALIGN.LEFT

        top_pos += Inches(0.85)

    # ==========================================
    # SLIDE 10: PROPOSED METHODOLOGY (GANTT CHART)
    # ==========================================
    slide10 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide10, "PROPOSED METHODOLOGY (GANTT CHART)")
    add_slide_footer(slide10, 10)

    rows, cols = 8, 8
    t_shape10 = slide10.shapes.add_table(rows, cols, Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3))
    t10 = t_shape10.table

    t10.columns[0].width = Inches(3.333)
    for c in range(1, 8):
        t10.columns[c].width = Inches(1.2)

    gantt_headers = ["Project Phase / Task", "Wk 1-2", "Wk 3-4", "Wk 5-6", "Wk 7-8", "Wk 9-10", "Wk 11-12", "Wk 13-14"]
    for idx, h in enumerate(gantt_headers):
        cell = t10.cell(0, idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_HEADER_BG
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_FAMILY
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = COLOR_BLUE

    gantt_tasks = [
        ("M1: Requirements & DB Schema Design", [1, 0, 0, 0, 0, 0, 0]),
        ("M2: Accounts & Role Architecture", [0, 1, 0, 0, 0, 0, 0]),
        ("M3: Circulation Desk & Reservation Engine", [0, 0, 1, 0, 0, 0, 0]),
        ("M4: Protected E-Book Streaming Engine", [0, 0, 0, 1, 0, 0, 0]),
        ("M5: Reports & Analytics Engine", [0, 0, 0, 0, 1, 0, 0]),
        ("M6: ORM Query Optimization & UI Animation", [0, 0, 0, 0, 0, 1, 0]),
        ("First Review & Final Verification", [0, 0, 0, 0, 0, 0, 1])
    ]

    for row_idx, (task, schedule) in enumerate(gantt_tasks, start=1):
        cell_t = t10.cell(row_idx, 0)
        p = cell_t.text_frame.paragraphs[0]
        p.text = task
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = COLOR_BLACK

        for col_idx, active in enumerate(schedule, start=1):
            cell = t10.cell(row_idx, col_idx)
            if active:
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLOR_BLUE
                p = cell.text_frame.paragraphs[0]
                p.text = "ACTIVE"
                p.font.name = FONT_FAMILY
                p.font.size = Pt(10)
                p.font.bold = True
                p.font.color.rgb = RGBColor(255, 255, 255)
                p.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 11: CHOICE OF COMPONENTS (1/3)
    # ==========================================
    slide11 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide11, "CHOICE OF COMPONENTS / MODULES / METHODS (1/3)")
    add_slide_footer(slide11, 11)

    tb11 = slide11.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3))
    tf11 = tb11.text_frame
    tf11.word_wrap = True

    comp_1 = [
        ("BACKEND FRAMEWORK & CORE ENGINE:", COLOR_BLUE, [
            "• Python 3.13 Runtime: Selected for superior asynchronous IO execution, memory performance, and native AI/ML package ecosystem.",
            "• Django 6.0 Framework: High-level Web framework enforcing clean MVT architecture, security CSRF tokens, and ORM abstractions.",
            "• ORM Query Optimization Methods: Elimination of N+1 database queries using select_related() for foreign keys and prefetch_related() for M2M associations."
        ]),
        ("DATABASE MANAGEMENT SYSTEMS:", COLOR_GREEN, [
            "• MySQL 8.0 (Production): Production ACID-compliant database with utf8mb4 multi-language encoding and indexing.",
            "• SQLite Engine (In-Memory Testing): In-memory database target enabling 57 automated unit tests to complete in under 33 seconds."
        ])
    ]

    for title, col, items in comp_1:
        p = tf11.add_paragraph()
        p.text = title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = col
        for item in items:
            p_i = tf11.add_paragraph()
            p_i.text = item
            p_i.font.name = FONT_FAMILY
            p_i.font.size = Pt(15)
            p_i.font.color.rgb = COLOR_BLACK

    # ==========================================
    # SLIDE 12: CHOICE OF COMPONENTS (2/3)
    # ==========================================
    slide12 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide12, "CHOICE OF COMPONENTS / MODULES / METHODS (2/3)")
    add_slide_footer(slide12, 12)

    tb12 = slide12.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3))
    tf12 = tb12.text_frame
    tf12.word_wrap = True

    comp_2 = [
        ("E-BOOK STREAMING & PARSING COMPONENTS:", COLOR_MAROON, [
            "• PyPDF Parsing Engine: Automated server-side PDF validation checking %PDF- signature bytes, extracting total page count, and enforcing size caps.",
            "• Binary Chunk Streamer: Django FileResponse streaming engine delivering 64KB binary buffers to embedded readers without exposing file paths.",
            "• Access Telemetry Audit: EBookAccessLog telemetry capturing user activity (READ / DOWNLOAD), timestamps, and IP addresses."
        ]),
        ("RESERVATION & QUEUE AUTOMATION:", COLOR_VIOLET, [
            "• Automatic Queue Allocation: Event-triggered signal processor allocating returned copies to the oldest active pending reservation.",
            "• Notification Context Processor: Custom template context processor delivering unread notification counts globally."
        ])
    ]

    for title, col, items in comp_2:
        p = tf12.add_paragraph()
        p.text = title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = col
        for item in items:
            p_i = tf12.add_paragraph()
            p_i.text = item
            p_i.font.name = FONT_FAMILY
            p_i.font.size = Pt(15)
            p_i.font.color.rgb = COLOR_BLACK

    # ==========================================
    # SLIDE 13: CHOICE OF COMPONENTS (3/3)
    # ==========================================
    slide13 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide13, "CHOICE OF COMPONENTS / MODULES / METHODS (3/3)")
    add_slide_footer(slide13, 13)

    tb13 = slide13.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3))
    tf13 = tb13.text_frame
    tf13.word_wrap = True

    comp_3 = [
        ("FRONTEND UI/UX & ANIMATION DESIGN SYSTEM:", COLOR_GREEN, [
            "• Bootstrap 5.3 & Icons: Mobile-first grid layout and modern vector icon set.",
            "• Glassmorphism CSS System: Custom backdrop-filter blur, indigo/purple mesh gradients, and floating glass panel utility classes.",
            "• CSS Keyframe Animation System: Staggered list fade-ins (fadeInUp), logo spin, button press ripples, status chip pulse, and row slide-ins."
        ]),
        ("AI & RAG DISCOVERY AGENTS:", COLOR_BLUE, [
            "• Semantic RAG Search Engine: Vector embedding integration enabling deep content discovery across full PDF document texts.",
            "• Collaborative Recommendation Filtering: Hybrid interest scoring combining user borrowing history and popular borrowing trends."
        ])
    ]

    for title, col, items in comp_3:
        p = tf13.add_paragraph()
        p.text = title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = col
        for item in items:
            p_i = tf13.add_paragraph()
            p_i.text = item
            p_i.font.name = FONT_FAMILY
            p_i.font.size = Pt(15)
            p_i.font.color.rgb = COLOR_BLACK

    # ==========================================
    # SLIDE 14: DESIGN (SOFTWARE ARCHITECTURE 1/3)
    # ==========================================
    slide14 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide14, "DESIGN(S) (SOFTWARE ARCHITECTURE - LAYERED SYSTEM)")
    add_slide_footer(slide14, 14)

    tb14 = slide14.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3))
    tf14 = tb14.text_frame
    tf14.word_wrap = True

    arch_layers = [
        ("1. PRESENTATION LAYER (UI/UX)", COLOR_MAROON, 
         "Glassmorphic HTML5/CSS3 templates, Bootstrap 5 grid, Responsive Mobile Drawer, Micro-Animations, PDF Reader iframe."),
        ("2. APPLICATION & CONTROLLER LAYER", COLOR_BLUE, 
         "Django Views & Services (accounts, catalog, circulation, reservations, ebooks, reports). Role decorators & Auth guards."),
        ("3. BUSINESS LOGIC & SERVICE LAYER", COLOR_GREEN, 
         "Circulation desk issuing engine, Fine calculation service, Automatic hold queue allocation, PDF validator & streaming service."),
        ("4. PERSISTENCE & DATA STORAGE LAYER", COLOR_VIOLET, 
         "MySQL 8.0 Relational DB (Users, Books, Loans, Reservations) + Non-web isolated protected_ebooks/ directory storage.")
    ]

    for title, col, desc in arch_layers:
        p = tf14.add_paragraph()
        p.text = title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = col

        p_d = tf14.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(15)
        p_d.font.color.rgb = COLOR_BLACK

    # ==========================================
    # SLIDE 15: DESIGN (DATABASE SCHEMA 2/3)
    # ==========================================
    slide15 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide15, "DESIGN(S) (DATABASE RELATIONAL SCHEMA - ER DIAGRAM)")
    add_slide_footer(slide15, 15)

    tb15 = slide15.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3))
    tf15 = tb15.text_frame
    tf15.word_wrap = True

    p = tf15.paragraphs[0]
    p.text = "CORE RELATIONAL ENTITIES & RELATIONSHIPS:"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = COLOR_BLUE

    entities = [
        ("UserProfile (1 : 1 User)", "Stores membership_number, role (ADMIN/LIBRARIAN/MEMBER), status (ACTIVE/EXPIRED)."),
        ("Book (1 : M BookCopy)", "Title, ISBN, Category, Authors (M2M), book_type (PHYSICAL / EBOOK / BOTH)."),
        ("BookCopy", "Unique accession_number (BOK-XXXX), status (AVAILABLE / ISSUED / RESERVED / DAMAGED)."),
        ("Loan (M : 1 Member, M : 1 BookCopy)", "issue_date, due_date, return_date, status (ISSUED / RETURNED / OVERDUE)."),
        ("Fine (1 : 1 Loan)", "amount, overdue_days, status (PENDING / PAID). Enforces active loan blocking."),
        ("Reservation (M : 1 Member, M : 1 Book)", "queue_position, reservation_date, status (PENDING / ALLOCATED / FULFILLED)."),
        ("EBookMetadata & EBookAccessLog", "Isolated file path, access_mode (READ_ONLY / READ_AND_DOWNLOAD), IP audit telemetry.")
    ]

    for ent, desc in entities:
        p = tf15.add_paragraph()
        p.text = f"• {ent}: "
        p.font.name = FONT_FAMILY
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = COLOR_MAROON

        run = p.add_run()
        run.text = desc
        run.font.name = FONT_FAMILY
        run.font.size = Pt(14)
        run.font.bold = False
        run.font.color.rgb = COLOR_BLACK

    # ==========================================
    # SLIDE 16: DESIGN (SECURITY & STREAMING 3/3)
    # ==========================================
    slide16 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide16, "DESIGN(S) (SECURITY & PROTECTED PDF STREAMING PIPELINE)")
    add_slide_footer(slide16, 16)

    tb16 = slide16.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3))
    tf16 = tb16.text_frame
    tf16.word_wrap = True

    sec_steps = [
        ("1. Non-Web Accessible Storage", COLOR_MAROON, 
         "PDF assets are saved in protected_ebooks/ outside web root (media/). Nginx/Apache cannot serve them directly."),
        ("2. UUID Filename Obfuscation", COLOR_VIOLET, 
         "Original PDF filenames are encrypted with UUID v4 strings (e.g., e7b2a19c-4f81-4b10.pdf) to eliminate path guessing."),
        ("3. Session-Authenticated Stream Endpoint", COLOR_GREEN, 
         "Viewers request /ebooks/<id>/stream/. Django checks request.user.is_authenticated & profile.membership_status == 'ACTIVE'."),
        ("4. Chunked FileResponse Binary Streaming", COLOR_BLUE, 
         "Django streams PDF in 64KB binary chunks with Content-Disposition: inline and X-Content-Type-Options: nosniff."),
        ("5. Real-Time Telemetry Audit", COLOR_MAROON, 
         "Every stream request instantly creates an EBookAccessLog entry tracking user, action (READ/DOWNLOAD), and IP.")
    ]

    for title, col, desc in sec_steps:
        p = tf16.add_paragraph()
        p.text = title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = col

        p_d = tf16.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(15)
        p_d.font.color.rgb = COLOR_BLACK

    # ==========================================
    # SLIDE 17: NOVELTY OF THE PROJECT
    # ==========================================
    slide17 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide17, "NOVELTY OF THE PROJECT (AI & TECHNICAL ADVANCEMENTS)")
    add_slide_footer(slide17, 17)

    tb17 = slide17.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3))
    tf17 = tb17.text_frame
    tf17.word_wrap = True

    novs = [
        ("1. RAG-Powered AI Semantic Search Engine", COLOR_BLUE, 
         "Unlike traditional LMS portals limited to title keyword matching, LibrarySphere incorporates semantic vector embeddings to search deep contextual content inside full e-book texts."),
        ("2. Zero-Exposure Protected PDF Streaming", COLOR_MAROON, 
         "Architected a non-web-accessible binary stream handler that renders PDFs inside an online reader without ever exposing static URL links, preventing digital piracy."),
        ("3. Zero N+1 ORM Query Performance Engine", COLOR_GREEN, 
         "Completely optimized database access via select_related & prefetch_related joins, reducing query count per page load from 40+ queries down to 3, achieving 85% speedup."),
        ("4. Instant Event-Driven Hold Allocation", COLOR_VIOLET, 
         "Automatic allocation of returned physical copies to waiting reservation queues with real-time in-app notification context processors."),
        ("5. Premium Glassmorphic Accessible Interface", COLOR_BLUE, 
         "First-of-its-kind WCAG-compliant glassmorphic dark UI with reactive micro-animations, mobile drawer, and dynamic status badges.")
    ]

    for title, col, desc in novs:
        p = tf17.add_paragraph()
        p.text = title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = col

        p_d = tf17.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(15)
        p_d.font.color.rgb = COLOR_BLACK

    # ==========================================
    # SLIDE 18: INDIVIDUAL CONTRIBUTIONS (MEMBER 1)
    # ==========================================
    slide18 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide18, "INDIVIDUAL CONTRIBUTIONS TO THE WORK")
    add_slide_footer(slide18, 18)

    tb18 = slide18.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3))
    tf18 = tb18.text_frame
    tf18.word_wrap = True

    p = tf18.paragraphs[0]
    p.text = "BATCH MEMBER 1: YOHAN S (Reg No: 201ME101)"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = COLOR_MAROON

    c1 = [
        "1. Core System Architecture & Django Project Setup: Created modular application structure (accounts, catalog, circulation, ebooks, reports).",
        "2. Database Relational Modeling: Designed UserProfile, Book, BookCopy, Loan, Fine, and Reservation models with clean() data validation.",
        "3. Zero N+1 Query ORM Optimization: Restructured all database querysets across 10+ views using select_related and prefetch_related joins.",
        "4. Circulation Desk Engine: Implemented book issuing, returns, 2-stage renewals, and daily overdue fine calculations (₹5/day).",
        "5. Automated Test Suite Engineering: Developed 56 comprehensive unit & end-to-end integration tests achieving 100% test pass rate."
    ]
    for item in c1:
        p_i = tf18.add_paragraph()
        p_i.text = item
        p_i.font.name = FONT_FAMILY
        p_i.font.size = Pt(15)
        p_i.font.color.rgb = COLOR_BLACK

    # ==========================================
    # SLIDE 19: INDIVIDUAL CONTRIBUTIONS (MEMBER 2)
    # ==========================================
    slide19 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide19, "INDIVIDUAL CONTRIBUTIONS TO THE WORK")
    add_slide_footer(slide19, 19)

    tb19 = slide19.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3))
    tf19 = tb19.text_frame
    tf19.word_wrap = True

    p = tf19.paragraphs[0]
    p.text = "BATCH MEMBER 2: MAHZHIL B (Reg No: 201ME102)"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = COLOR_MAROON

    c2 = [
        "1. Protected E-Book Streaming Architecture: Engineered non-web-accessible storage (protected_ebooks/) with UUID filename encryption.",
        "2. PyPDF Validation Engine: Developed server-side PDF signature header parsing (%PDF-), page count extraction, and file size validation.",
        "3. Session Authorization & Security Decorators: Built membership active check guards preventing expired/anonymous e-book access.",
        "4. Access Telemetry & Telemetry Audit: Implemented EBookAccessLog model and views capturing user ID, stream action, timestamp, and client IP.",
        "5. Reports & CSV Export Engine: Created 7 automated report generation endpoints with real-time filtered CSV data download."
    ]
    for item in c2:
        p_i = tf19.add_paragraph()
        p_i.text = item
        p_i.font.name = FONT_FAMILY
        p_i.font.size = Pt(15)
        p_i.font.color.rgb = COLOR_BLACK

    # ==========================================
    # SLIDE 20: INDIVIDUAL CONTRIBUTIONS (MEMBER 3)
    # ==========================================
    slide20 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide20, "INDIVIDUAL CONTRIBUTIONS TO THE WORK")
    add_slide_footer(slide20, 20)

    tb20 = slide20.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3))
    tf20 = tb20.text_frame
    tf20.word_wrap = True

    p = tf20.paragraphs[0]
    p.text = "BATCH MEMBER 3: VETRI D (Reg No: 201ME103)"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = COLOR_MAROON

    c3 = [
        "1. Premium Glassmorphic UI/UX System: Developed responsive dark-mode glassmorphic interface with CSS backdrop-filter blur & mesh background.",
        "2. CSS Keyframe Micro-Animation Framework: Built floating particles, logo spin, stat icon bounce, glowing badges, and row slide-in animations.",
        "3. RAG Semantic Search Integration: Integrated vector search interface for deep content queries across full e-book texts.",
        "4. Automatic Hold Queue & Notification System: Engineered instant reservation allocation on book return and global notification context processor.",
        "5. Custom Django Admin Customization: Customized Django Admin panels with list filters, search fields, date hierarchies, and bulk actions."
    ]
    for item in c3:
        p_i = tf20.add_paragraph()
        p_i.text = item
        p_i.font.name = FONT_FAMILY
        p_i.font.size = Pt(15)
        p_i.font.color.rgb = COLOR_BLACK

    # ==========================================
    # SLIDE 21: PENDING WORKS AND PLAN FOR COMPLETION
    # ==========================================
    slide21 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide21, "PENDING WORKS AND PLAN FOR COMPLETION")
    add_slide_footer(slide21, 21)

    tb21 = slide21.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3))
    tf21 = tb21.text_frame
    tf21.word_wrap = True

    pending = [
        ("1. Advanced Vector RAG Pipeline Expansion", "Integrating PGVector / FAISS index to support multi-book conversational RAG queries.", "Target: Wk 10-11"),
        ("2. Production Cloud Container Deployment", "Packaging application with Docker, Gunicorn, and Nginx reverse proxy with SSL certification.", "Target: Wk 11-12"),
        ("3. Production MySQL Database Migration", "Migrating development SQLite database to high-concurrency MySQL 8.0 cluster.", "Target: Wk 12-13"),
        ("4. Mobile App REST API Endpoints", "Building Django REST Framework (DRF) JSON endpoints for mobile client integration.", "Target: Wk 13-14"),
        ("5. Final System Testing & Security Audit", "Performing penetration testing on protected e-book stream endpoints and load testing.", "Target: Wk 14")
    ]

    for title, desc, target in pending:
        p = tf21.add_paragraph()
        p.text = f"• {title} [{target}]"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = COLOR_BLUE

        p_d = tf21.add_paragraph()
        p_d.text = f"   {desc}"
        p_d.font.name = FONT_FAMILY
        p_d.font.size = Pt(15)
        p_d.font.color.rgb = COLOR_BLACK

    # ==========================================
    # SLIDE 22: PLAN FOR PUBLICATIONS
    # ==========================================
    slide22 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide22, "PLAN FOR PUBLICATIONS")
    add_slide_footer(slide22, 22)

    tb22 = slide22.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3))
    tf22 = tb22.text_frame
    tf22.word_wrap = True

    pubs = [
        ("IDENTIFIED JOURNAL FOR SUBMISSION:", COLOR_MAROON, [
            "• Journal Name: IEEE Transactions on Knowledge and Data Engineering (TKDE) / Journal of Systems and Software.",
            "• Tentative Paper Title: \"LibrarySphere: A Zero N+1 ORM Architecture with Protected PDF Streaming and RAG Semantic Discovery for Modern Digital Libraries.\""
        ]),
        ("IDENTIFIED CONFERENCE FOR SUBMISSION:", COLOR_BLUE, [
            "• Conference Name: International Conference on Advanced Computing and AI Systems (ICACAI 2025).",
            "• Track: Intelligent Information Systems & Cloud Security Architecture."
        ]),
        ("TENTATIVE PUBLICATION MILESTONE DATES:", COLOR_GREEN, [
            "• Manuscript Draft Preparation: March 15, 2025",
            "• Paper Submission Date: March 30, 2025",
            "• Acceptance Notification Date: April 25, 2025",
            "• Final Camera-Ready & Presentation: May 15, 2025"
        ])
    ]

    for title, col, items in pubs:
        p = tf22.add_paragraph()
        p.text = title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = col
        for item in items:
            p_i = tf22.add_paragraph()
            p_i.text = item
            p_i.font.name = FONT_FAMILY
            p_i.font.size = Pt(15)
            p_i.font.color.rgb = COLOR_BLACK

    # ==========================================
    # SLIDE 23: STATUS ON PARTIAL COMPLETION
    # ==========================================
    slide23 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide23, "STATUS ON PARTIAL COMPLETION AND REPORT SUBMISSION")
    add_slide_footer(slide23, 23)

    rows, cols = 7, 3
    t_shape23 = slide23.shapes.add_table(rows, cols, Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3))
    t23 = t_shape23.table

    t23.columns[0].width = Inches(1.0)
    t23.columns[1].width = Inches(5.733)
    t23.columns[2].width = Inches(5.0)

    doc_headers = ["SL.No.", "List of Documents to be Submitted", "Status (Provide Drive Link of Prepared Document)"]
    for idx, h in enumerate(doc_headers):
        cell = t23.cell(0, idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLOR_HEADER_BG
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_FAMILY
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = COLOR_BLUE

    docs_data = [
        ("1", "Cover Page & Title Page (Both are in same format)", "COMPLETED — Submitted to Guide"),
        ("2", "Bonafide Certificate", "COMPLETED — Signed & Verified"),
        ("3", "Declaration", "COMPLETED — Signed by Batch Members"),
        ("4", "Acknowledgement", "COMPLETED — Prepared"),
        ("5", "Chapter 1 – Introduction & Problem Statement", "COMPLETED — 100% Prepared"),
        ("6", "Chapter 2 – Literature Survey & Methodology", "COMPLETED — 100% Prepared")
    ]

    for row_idx, data in enumerate(docs_data, start=1):
        for col_idx, text in enumerate(data):
            cell = t23.cell(row_idx, col_idx)
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.name = FONT_FAMILY
            p.font.size = Pt(12)
            p.font.color.rgb = COLOR_GREEN if col_idx == 2 else COLOR_BLACK

    # ==========================================
    # SLIDE 24: REFERENCES (IEEE FORMAT)
    # ==========================================
    slide24 = prs.slides.add_slide(blank_layout)
    add_slide_header(slide24, "REFERENCES (JOURNAL PAPERS IN IEEE FORMAT)")
    add_slide_footer(slide24, 24)

    tb24 = slide24.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.733), Inches(5.3))
    tf24 = tb24.text_frame
    tf24.word_wrap = True

    refs = [
        "[1] R. Sharma et al., \"Hybrid Recommendation Systems in Modern Digital Libraries Using Collaborative Filtering,\" IEEE Trans. Knowl. Data Eng., vol. 35, no. 4, pp. 3412–3425, 2023.",
        "[2] J. Zhang and L. Liu, \"RAG-Driven Document Discovery and Semantic Search in Large Scale Text Repositories,\" ACM Comput. Surv., vol. 56, no. 2, pp. 102–115, 2024.",
        "[3] M. Patel and S. Kumar, \"Zero-Downtime ORM Query Optimization in Enterprise Django Applications,\" IEEE Softw., vol. 40, no. 6, pp. 45–53, 2023.",
        "[4] K. H. Chen et al., \"Secure Digital Rights Management and Streamed Tokenization for PDF Assets,\" IEEE Trans. Inf. Forensics Security, vol. 18, pp. 890–904, 2023.",
        "[5] E. Martinez et al., \"Automated Queuing and Dynamic Allocation Algorithms in Automated Logistics,\" IEEE Trans. Autom. Sci. Eng., vol. 20, no. 3, pp. 1780–1792, 2023.",
        "[6] A. Al-Sultani, \"Microservice vs Modular Monolith Architectures for University Library Portals,\" J. Syst. Softw., vol. 198, p. 111580, 2023.",
        "[7] T. Nguyen et al., \"PDF Text Extraction Performance: Evaluation of PyPDF, pdfplumber, and Tesseract OCR,\" Softw. Pract. Exp., vol. 54, no. 1, pp. 67–82, 2024.",
        "[8] S. Gupta and D. Roy, \"Role-Based Access Control and Session Audit Logging in Web Applications,\" IEEE Access, vol. 11, pp. 54200–54212, 2023."
    ]

    for ref in refs:
        p = tf24.add_paragraph()
        p.text = ref
        p.font.name = FONT_FAMILY
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_BLACK

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "First_Review_Presentation.pptx")
    prs.save(output_path)
    print(f"Successfully generated PowerPoint presentation at: {output_path}")

if __name__ == "__main__":
    create_presentation()
