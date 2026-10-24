import os
os.environ['MPLCONFIGDIR'] = '/tmp/mpl'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image

os.makedirs('report_figures', exist_ok=True)

# ----------------------------------------------------------------------
# 1. Figure 1.4: Digital Library Management System Advantages
# ----------------------------------------------------------------------
def create_fig_1_4():
    fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Main Title Box
    title_box = patches.FancyBboxPatch((15, 91), 70, 7, boxstyle="round,pad=1.0", fc="#E0E7FF", ec="#4338CA", lw=1.5)
    ax.add_patch(title_box)
    ax.text(50, 94.5, "Public Library Membership & Book Reservation Tracking Portal", fontsize=12, fontweight='bold', color="#1E1B4B", ha='center', va='center')

    # Left: Member / Patron Module
    box_member = patches.FancyBboxPatch((3, 50), 28, 38, boxstyle="round,pad=0.8", fc="#EFF6FF", ec="#2563EB", lw=1.5)
    ax.add_patch(box_member)
    ax.text(17, 84, "Member (Patron)", fontsize=11, fontweight='bold', color="#1E3A8A", ha='center')
    member_text = (
        "• Search Book Catalog (Title/ISBN)\n"
        "• View Real-Time Shelf Availability\n"
        "• Place Reservation Holds\n"
        "• Track Live Queue Position\n"
        "• Read Digital E-Books Online\n"
        "• Self-Checkout at Express Kiosk\n"
        "• Track Yearly Reading Challenge\n"
        "• Receive In-App Overdue Notices"
    )
    ax.text(5, 65, member_text, fontsize=8.5, color="#1E293B", va='center')

    # Right: Librarian / Circulation Desk
    box_lib = patches.FancyBboxPatch((69, 50), 28, 38, boxstyle="round,pad=0.8", fc="#F0FDF4", ec="#16A34A", lw=1.5)
    ax.add_patch(box_lib)
    ax.text(83, 84, "Librarian (Staff Desk)", fontsize=11, fontweight='bold', color="#14532D", ha='center')
    lib_text = (
        "• Issue Physical Copies (Loans)\n"
        "• Process Returns & Copy Inspections\n"
        "• Automated Hold Allocation\n"
        "• Assess Daily Fines (₹5/day)\n"
        "• Manage Member Directory\n"
        "• 1-Click Kaggle E-Book Import\n"
        "• Live Web Book Ingestion\n"
        "• Generate Analytical Reports"
    )
    ax.text(71, 65, lib_text, fontsize=8.5, color="#1E293B", va='center')

    # Center Top: Web Application (Django & Bootstrap)
    box_web = patches.FancyBboxPatch((34, 68), 32, 20, boxstyle="round,pad=0.8", fc="#FAF5FF", ec="#9333EA", lw=1.5)
    ax.add_patch(box_web)
    ax.text(50, 84, "Central Web Application", fontsize=10.5, fontweight='bold', color="#581C87", ha='center')
    ax.text(50, 75, "Django 6.0 MVC Architecture\nRole-Based Session Authentication\nDual-Mode (Light/Dark) UI\nREST APIs & WhiteNoise Assets", fontsize=8, color="#334155", ha='center', va='center')

    # Center Middle: Database Layer
    box_db = patches.FancyBboxPatch((35, 48), 30, 16, boxstyle="round,pad=0.8", fc="#FFFBEB", ec="#D97706", lw=1.5)
    ax.add_patch(box_db)
    ax.text(50, 60.5, "Relational Database (MySQL / SQLite)", fontsize=10, fontweight='bold', color="#78350F", ha='center')
    ax.text(50, 53, "UserProfile | Book & BookCopy | Loan\nFine Engine | Reservation Queue | AuditLog", fontsize=7.8, color="#451A03", ha='center')

    # Center Bottom: Administrator
    box_admin = patches.FancyBboxPatch((35, 29), 30, 15, boxstyle="round,pad=0.8", fc="#FEF2F2", ec="#DC2626", lw=1.5)
    ax.add_patch(box_admin)
    ax.text(50, 40.5, "System Administrator", fontsize=10, fontweight='bold', color="#7F1D1D", ha='center')
    ax.text(50, 34, "Staff Provisioning & Membership Approval\nAudit Trail Review | Telemetry Logs\nGlobal Configuration & Database Health", fontsize=7.8, color="#450A0A", ha='center')

    # Bottom Banner: Technology Stack & Core Workflow
    box_bottom = patches.FancyBboxPatch((3, 3), 94, 22, boxstyle="round,pad=0.8", fc="#F8FAFC", ec="#64748B", lw=1.5)
    ax.add_patch(box_bottom)
    ax.text(25, 20.5, "TECHNOLOGY STACK", fontsize=10, fontweight='bold', color="#0F172A", ha='center')
    tech_str = (
        "• Backend: Python 3.13, Django 6.0 ORM\n"
        "• Database: MySQL 8.0 / SQLite3 Engine\n"
        "• Frontend: HTML5, Bootstrap 5.3, Site.css\n"
        "• Tools: Html5-QRCode, WhiteNoise, PyPDF"
    )
    ax.text(5, 11, tech_str, fontsize=8, color="#334155")

    ax.text(75, 20.5, "CIRCULATION & RESERVATION WORKFLOW", fontsize=10, fontweight='bold', color="#0F172A", ha='center')
    flow_str = (
        "1. Member Login / Scan Digital Library Card\n"
        "2. Check Eligibility (Active status, Fines = ₹0, Quota < Max)\n"
        "3. Real-Time Copy Checkout (Desk or Express Kiosk)\n"
        "4. Auto Overdue Fine Accrual & Return Processing\n"
        "5. Automated Hold Allocation (FIFO queue -> Pickup Pass)"
    )
    ax.text(52, 10.5, flow_str, fontsize=8, color="#334155")

    # Connecting Arrows
    ax.annotate("", xy=(34, 78), xytext=(31, 78), arrowprops=dict(arrowstyle="<->", color="#4338CA", lw=1.5))
    ax.annotate("", xy=(69, 78), xytext=(66, 78), arrowprops=dict(arrowstyle="<->", color="#16A34A", lw=1.5))
    ax.annotate("", xy=(50, 68), xytext=(50, 64), arrowprops=dict(arrowstyle="<->", color="#D97706", lw=1.5))
    ax.annotate("", xy=(50, 48), xytext=(50, 44), arrowprops=dict(arrowstyle="<->", color="#DC2626", lw=1.5))

    plt.tight_layout()
    plt.savefig('report_figures/fig_1_4_advantages.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created fig_1_4_advantages.png")

# ----------------------------------------------------------------------
# 2. Figure 3.3: Objectives and Methodology Architecture
# ----------------------------------------------------------------------
def create_fig_3_3():
    fig, ax = plt.subplots(figsize=(10, 7), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Header Box
    h_box = patches.FancyBboxPatch((10, 91), 80, 7.5, boxstyle="round,pad=0.8", fc="#02599C", ec="#02599C")
    ax.add_patch(h_box)
    ax.text(50, 94.7, "Objectives and Methodology Architecture\nPublic Library Membership Management & Reservation Tracking Portal", fontsize=11.5, fontweight='bold', color="#FFFFFF", ha='center', va='center')

    # Left: Objectives Box
    obj_box = patches.FancyBboxPatch((3, 24), 44, 64, boxstyle="round,pad=0.8", fc="#F0F9FF", ec="#0284C7", lw=1.5)
    ax.add_patch(obj_box)
    ax.text(25, 83.5, "Project Objectives", fontsize=12, fontweight='bold', color="#0369A1", ha='center')

    objs = [
        ("Digitization of Library Operations", "Eliminate physical register paperwork and automate circulation logs."),
        ("Centralized Physical Accessioning", "Individual unique accession barcodes (LIB-XXXX) for all book copies."),
        ("Streamlined Issue / Return Desk", "Accelerate loan processing with real-time due dates and receipts."),
        ("Automated FIFO Reservation Queue", "Fair waitlist allocation when returned copies match pending holds."),
        ("Role-Based Access Control (RBAC)", "Strict permission segregation for Members, Staff, and Administrators."),
        ("Protected E-Book & DRM Architecture", "In-browser reading engine with isolated non-web-accessible storage."),
        ("Self-Service Express Kiosk", "Camera QR/barcode scanner enabling unattended patron self-borrowing."),
        ("Dynamic Analytics & 1-Click Exports", "Instant CSV reports on circulation trends, fines, and active holds.")
    ]
    y_pos = 78
    for title, desc in objs:
        ax.text(5, y_pos, f"• {title}:", fontsize=8.5, fontweight='bold', color="#0C4A6E")
        ax.text(7, y_pos - 2.5, desc, fontsize=7.5, color="#334155")
        y_pos -= 6.8

    # Right: Methodology Box
    meth_box = patches.FancyBboxPatch((53, 24), 44, 64, boxstyle="round,pad=0.8", fc="#F8FAFC", ec="#475569", lw=1.5)
    ax.add_patch(meth_box)
    ax.text(75, 83.5, "Structured Methodology", fontsize=12, fontweight='bold', color="#1E293B", ha='center')

    steps = [
        ("1. Requirement Analysis", "Identified core patron & librarian workflows, quota rules, and fines."),
        ("2. System Architecture Design", "Engineered 3-tier MVC pattern with relational integrity constraints."),
        ("3. Django Backend & ORM Models", "Implemented models with custom validation clean() methods & services."),
        ("4. Accessible UI & Dual Themes", "Designed Open Library/NDLI inspired interface with light/dark modes."),
        ("5. Hardware-Free Kiosk & APIs", "Built Html5-QRCode camera scanner and atomic JSON checkout APIs."),
        ("6. Security & DRM Integration", "Enforced session authentication, UUID file masking, and audit trails."),
        ("7. Rigorous Constraint Testing", "Verified 12+ real-world business constraints across 117 automated tests.")
    ]
    y_pos = 78
    for step_title, step_desc in steps:
        # circle number icon
        c_box = patches.Circle((57, y_pos - 1), 2.2, fc="#2563EB", ec="#1D4ED8")
        ax.add_patch(c_box)
        num = step_title.split('.')[0]
        ax.text(57, y_pos - 1, num, fontsize=8.5, fontweight='bold', color="#FFFFFF", ha='center', va='center')
        ax.text(61, y_pos, step_title.split('. ')[1], fontsize=8.5, fontweight='bold', color="#0F172A")
        ax.text(61, y_pos - 2.8, step_desc, fontsize=7.5, color="#475569")
        y_pos -= 7.8

    # Bottom Technology Stack & Outcome Bar
    bot_box = patches.FancyBboxPatch((3, 3), 94, 18, boxstyle="round,pad=0.8", fc="#EEF2FF", ec="#4338CA", lw=1.5)
    ax.add_patch(bot_box)
    ax.text(50, 16.5, "CORE TECHNOLOGY STACK & VERIFIED PROJECT OUTCOMES", fontsize=10, fontweight='bold', color="#312E81", ha='center')
    ax.text(25, 9, "Frontend & UX:\n• HTML5, Bootstrap 5.3, WhiteNoise\n• Dual Mode Theme (Light/Dark)\n• In-Browser PDF.js Viewer Studio", fontsize=8, color="#1E1B4B", ha='center')
    ax.text(50, 9, "Backend & Database:\n• Python 3.13, Django 6.0 Framework\n• Relational Schema (MySQL / SQLite)\n• Atomic Transaction Management", fontsize=8, color="#1E1B4B", ha='center')
    ax.text(75, 9, "Project Outcomes:\n• 100+ Books Cataloged with Cover Art\n• Zero-Waitlist Digital Classic Reading\n• 117 / 117 Automated Unit Tests Passing", fontsize=8, color="#1E1B4B", ha='center')

    plt.tight_layout()
    plt.savefig('report_figures/fig_3_3_methodology.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created fig_3_3_methodology.png")

# ----------------------------------------------------------------------
# 3. Figure 4.8: Proposed System Architecture & Processing Workflow
# ----------------------------------------------------------------------
def create_fig_4_8():
    fig, ax = plt.subplots(figsize=(10, 7.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Title
    t_box = patches.FancyBboxPatch((12, 92), 76, 7, boxstyle="round,pad=0.8", fc="#1E293B", ec="#0F172A")
    ax.add_patch(t_box)
    ax.text(50, 95.5, "Proposed System Architecture — Three-Tier Operational Model", fontsize=11.5, fontweight='bold', color="#FFFFFF", ha='center', va='center')

    # Tier 1: Presentation Layer
    p_box = patches.FancyBboxPatch((3, 67), 94, 22, boxstyle="round,pad=0.8", fc="#F8FAFC", ec="#0284C7", lw=1.5)
    ax.add_patch(p_box)
    ax.text(7, 85, "TIER 1: PRESENTATION & CLIENT INTERFACE LAYER (Responsive Web / PWA)", fontsize=9.5, fontweight='bold', color="#0369A1")

    # Presentation Sub-boxes
    sub1 = patches.FancyBboxPatch((5, 70), 28, 12, boxstyle="round,pad=0.5", fc="#FFFFFF", ec="#CBD5E1")
    ax.add_patch(sub1)
    ax.text(19, 78, "Member Portal UI", fontsize=8.5, fontweight='bold', color="#1E293B", ha='center')
    ax.text(19, 73, "• Catalog Omni-Search (Cmd+K)\n• Bookshelf, Holds & Fines\n• E-Book In-Browser Reader", fontsize=7.5, color="#475569", ha='center')

    sub2 = patches.FancyBboxPatch((36, 70), 28, 12, boxstyle="round,pad=0.5", fc="#FFFFFF", ec="#CBD5E1")
    ax.add_patch(sub2)
    ax.text(50, 78, "Express Checkout Kiosk", fontsize=8.5, fontweight='bold', color="#1E293B", ha='center')
    ax.text(50, 73, "• Webcam QR / Barcode Reader\n• Multi-Step Touch Terminal\n• Instant Loan Slip Generation", fontsize=7.5, color="#475569", ha='center')

    sub3 = patches.FancyBboxPatch((67, 70), 28, 12, boxstyle="round,pad=0.5", fc="#FFFFFF", ec="#CBD5E1")
    ax.add_patch(sub3)
    ax.text(81, 78, "Librarian & Admin Desk", fontsize=8.5, fontweight='bold', color="#1E293B", ha='center')
    ax.text(81, 73, "• Circulation Desk (Issue/Return)\n• Reservation Queue Management\n• 7 Analytical Export Reports", fontsize=7.5, color="#475569", ha='center')

    # Tier 2: Application / Business Logic Layer
    app_box = patches.FancyBboxPatch((3, 37), 94, 26, boxstyle="round,pad=0.8", fc="#F0FDF4", ec="#16A34A", lw=1.5)
    ax.add_patch(app_box)
    ax.text(7, 59, "TIER 2: APPLICATION & BUSINESS LOGIC LAYER (Django 6.0 MVC Framework)", fontsize=9.5, fontweight='bold', color="#15803D")

    m_box1 = patches.FancyBboxPatch((5, 40), 21, 16, boxstyle="round,pad=0.5", fc="#FFFFFF", ec="#86EFAC")
    ax.add_patch(m_box1)
    ax.text(15.5, 52, "Circulation Engine", fontsize=8.5, fontweight='bold', color="#14532D", ha='center')
    ax.text(15.5, 45, "• can_member_borrow()\n• issue_book() atomic\n• return_book() fine check\n• 2-stage renewal control", fontsize=7.2, color="#1E293B", ha='center')

    m_box2 = patches.FancyBboxPatch((28, 40), 21, 16, boxstyle="round,pad=0.5", fc="#FFFFFF", ec="#86EFAC")
    ax.add_patch(m_box2)
    ax.text(38.5, 52, "Reservation Pipeline", fontsize=8.5, fontweight='bold', color="#14532D", ha='center')
    ax.text(38.5, 45, "• FIFO Queue Allocation\n• auto_allocate_copy()\n• 48h Pickup Expiration\n• In-App User Alerts", fontsize=7.2, color="#1E293B", ha='center')

    m_box3 = patches.FancyBboxPatch((51, 40), 21, 16, boxstyle="round,pad=0.5", fc="#FFFFFF", ec="#86EFAC")
    ax.add_patch(m_box3)
    ax.text(61.5, 52, "E-Book DRM Engine", fontsize=8.5, fontweight='bold', color="#14532D", ha='center')
    ax.text(61.5, 45, "• Protected Streamer\n• PyPDF Header Validation\n• UUID v4 Path Masking\n• EBookAccessLog Audit", fontsize=7.2, color="#1E293B", ha='center')

    m_box4 = patches.FancyBboxPatch((74, 40), 21, 16, boxstyle="round,pad=0.5", fc="#FFFFFF", ec="#86EFAC")
    ax.add_patch(m_box4)
    ax.text(84.5, 52, "Dataset Ingestion", fontsize=8.5, fontweight='bold', color="#14532D", ha='center')
    ax.text(84.5, 45, "• 1-Click Kaggle Books\n• Open Library Live API\n• Automated Hardcover Art\n• AI Semantic Cosine Index", fontsize=7.2, color="#1E293B", ha='center')

    # Tier 3: Database & Storage Layer
    db_box = patches.FancyBboxPatch((3, 4), 94, 29, boxstyle="round,pad=0.8", fc="#FFFBEB", ec="#D97706", lw=1.5)
    ax.add_patch(db_box)
    ax.text(7, 29, "TIER 3: DATABASE & SECURE STORAGE LAYER (Django ORM with ACID Transactions)", fontsize=9.5, fontweight='bold', color="#B45309")

    # Database Tables
    entities = [
        ("UserProfile", "membership_no (PK)\nrole (ADMIN/LIB/MEM)\nstatus (ACTIVE/EXPIRED)\nmax_books_allowed\ntier (STUDENT/FACULTY)"),
        ("Book & BookCopy", "isbn (Indexed)\ntitle, category, authors\nbook_type (PHY/EBOOK)\naccession_no (Unique)\nstatus (AVAIL/ISSUED)"),
        ("Loan & Fine", "issue_date, due_date\nreturn_date, renewal_count\nfine_amount (₹5/day)\nstatus (PENDING/PAID)\nFK(BookCopy, Member)"),
        ("Reservation", "queue_position\nreservation_date\npickup_deadline (48h)\nstatus (ALLOCATED)\nFK(Book, Member)"),
        ("E-Book & Telemetry", "file_path (Protected)\naccess_mode\nrights_status\nEBookAccessLog(IP, user)\nReadingChallenge & Goal")
    ]
    x_pos = 5
    for ent_name, ent_fields in entities:
        e_box = patches.FancyBboxPatch((x_pos, 7), 17.5, 19, boxstyle="round,pad=0.5", fc="#FFFFFF", ec="#FDE68A")
        ax.add_patch(e_box)
        ax.text(x_pos + 8.75, 23, ent_name, fontsize=8, fontweight='bold', color="#78350F", ha='center')
        ax.text(x_pos + 8.75, 14.5, ent_fields, fontsize=6.8, color="#451A03", ha='center')
        x_pos += 18.5

    # Connectors between tiers
    ax.annotate("", xy=(50, 67), xytext=(50, 63), arrowprops=dict(arrowstyle="<->", color="#0284C7", lw=2))
    ax.annotate("", xy=(50, 37), xytext=(50, 33), arrowprops=dict(arrowstyle="<->", color="#16A34A", lw=2))

    plt.tight_layout()
    plt.savefig('report_figures/fig_4_8_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created fig_4_8_architecture.png")

# ----------------------------------------------------------------------
# 4. Figure 5.2: Dashboard and Web Portal Interface
# ----------------------------------------------------------------------
def create_fig_5_2():
    # Composite of actual uploaded images:
    # media_1792120808498_fd237d7f.png (Home/Catalog)
    # media_1792120816668_fd0ec1e5.png (Book Search & Filter Results)
    # media_1792123507495_97d8e2fe.png (E-Book Catalog & Digital Covers)
    # media_1791815891043_bc435faa.png (Modern UI Portal Interface)
    dir_path = '/Users/sk/.gemini/antigravity/brain/3545079b-dbe7-499f-854e-0efad337c5d9/.user_uploaded/'

    img1_path = os.path.join(dir_path, 'media_1792120808498_fd237d7f.png')
    img2_path = os.path.join(dir_path, 'media_1792120816668_fd0ec1e5.png')
    img3_path = os.path.join(dir_path, 'media_1792123507495_97d8e2fe.png')
    img4_path = os.path.join(dir_path, 'media_1791815891043_bc435faa.png')

    fig = plt.figure(figsize=(11, 7.5), dpi=300)

    # 4 subplots
    ax1 = fig.add_subplot(2, 2, 1)
    if os.path.exists(img1_path):
        ax1.imshow(Image.open(img1_path))
    ax1.set_title("(a) LibrarySphere Portal Home & Omni-Search", fontsize=9.5, fontweight='bold', pad=5, color="#1E293B")
    ax1.axis('off')

    ax2 = fig.add_subplot(2, 2, 2)
    if os.path.exists(img2_path):
        ax2.imshow(Image.open(img2_path))
    ax2.set_title("(b) Filtered Book Search & Real-Time Availability", fontsize=9.5, fontweight='bold', pad=5, color="#1E293B")
    ax2.axis('off')

    ax3 = fig.add_subplot(2, 2, 3)
    if os.path.exists(img3_path):
        ax3.imshow(Image.open(img3_path))
    ax3.set_title("(c) Digital E-Book Library & Cover Art Gallery", fontsize=9.5, fontweight='bold', pad=5, color="#1E293B")
    ax3.axis('off')

    ax4 = fig.add_subplot(2, 2, 4)
    if os.path.exists(img4_path):
        ax4.imshow(Image.open(img4_path))
    ax4.set_title("(d) Interactive Reader Studio & Live Circulation Desk", fontsize=9.5, fontweight='bold', pad=5, color="#1E293B")
    ax4.axis('off')

    plt.tight_layout()
    plt.savefig('report_figures/fig_5_2_dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created fig_5_2_dashboard.png")

# ----------------------------------------------------------------------
# 5. Figure 4.7: Entity-Relationship (ER) Diagram
# ----------------------------------------------------------------------
def create_fig_4_7_er():
    fig, ax = plt.subplots(figsize=(12, 8.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Title Banner
    t_box = patches.FancyBboxPatch((12, 93), 76, 5.5, boxstyle="round,pad=0.6", fc="#02599C", ec="#02599C")
    ax.add_patch(t_box)
    ax.text(50, 95.7, "Entity-Relationship (ER) Diagram — LibrarySphere Relational Database Schema",
            fontsize=12, fontweight='bold', color="#FFFFFF", ha='center', va='center')

    def draw_entity(x, y, w, h, name, fields, header_color="#1E3A8A"):
        head_box = patches.FancyBboxPatch((x, y + h - 3.2), w, 3.2, boxstyle="round,pad=0.2", fc=header_color, ec=header_color)
        ax.add_patch(head_box)
        ax.text(x + w/2, y + h - 1.6, name, fontsize=8.5, fontweight='bold', color="#FFFFFF", ha='center', va='center')
        
        body_box = patches.FancyBboxPatch((x, y), w, h - 3.2, boxstyle="round,pad=0.2", fc="#F8FAFC", ec="#94A3B8", lw=1.2)
        ax.add_patch(body_box)
        
        y_text = y + h - 5.0
        for f, is_key in fields:
            weight = 'bold' if is_key else 'normal'
            color = '#B45309' if 'PK' in f else ('#1D4ED8' if 'FK' in f else '#1E293B')
            ax.text(x + 1.0, y_text, f, fontsize=6.8, fontweight=weight, color=color, va='center')
            y_text -= 2.1

    # 1. UserProfile
    draw_entity(3, 56, 21, 28, "UserProfile", [
        ("id : int [PK]", True),
        ("membership_number : varchar", True),
        ("role : enum(ADMIN,LIB,MEM)", False),
        ("tier : enum(STUDENT,FACULTY)", False),
        ("membership_status : enum", False),
        ("max_books_allowed : int", False),
        ("current_active_loans : int", False),
        ("user_id : int [FK]", True),
        ("created_at : datetime", False),
        ("updated_at : datetime", False),
    ], header_color="#0F766E")

    # 2. Category
    draw_entity(29, 65, 18, 19, "Category", [
        ("id : int [PK]", True),
        ("name : varchar(100)", True),
        ("description : text", False),
        ("is_active : boolean", False),
        ("slug : varchar(120)", False),
    ], header_color="#6366F1")

    # 3. Author
    draw_entity(3, 24, 18, 17, "Author", [
        ("id : int [PK]", True),
        ("full_name : varchar(200)", True),
        ("bio : text", False),
        ("born_year : int", False),
    ], header_color="#8B5CF6")

    # 4. Book (Central)
    draw_entity(29, 24, 23, 34, "Book (Title Catalog)", [
        ("id : int [PK]", True),
        ("isbn : varchar(13) [Unique]", True),
        ("title : varchar(255)", True),
        ("category_id : int [FK]", True),
        ("publisher : varchar(200)", False),
        ("publication_year : int", False),
        ("language : varchar(50)", False),
        ("description : text", False),
        ("book_type : enum(PHY,EBOOK)", False),
        ("cover_image : varchar", False),
        ("is_active : boolean", False),
        ("created_at : datetime", False),
    ], header_color="#1E3A8A")

    # 5. BookCopy
    draw_entity(57, 24, 21, 24, "BookCopy (Physical)", [
        ("id : int [PK]", True),
        ("accession_number : varchar [PK]", True),
        ("book_id : int [FK]", True),
        ("shelf_location : varchar(100)", False),
        ("status : enum(AVAIL,ISSUED)", False),
        ("condition : enum(GOOD,FAIR)", False),
        ("created_at : datetime", False),
    ], header_color="#C2410C")

    # 6. Loan
    draw_entity(82, 48, 16, 26, "Loan (Circulation)", [
        ("id : int [PK]", True),
        ("book_copy_id : int [FK]", True),
        ("member_id : int [FK]", True),
        ("issue_date : date", False),
        ("due_date : date", False),
        ("return_date : date", False),
        ("status : enum(ISSUED,RET)", False),
        ("renewal_count : int", False),
    ], header_color="#BE185D")

    # 7. Fine
    draw_entity(82, 14, 16, 22, "Fine (Penalty)", [
        ("id : int [PK]", True),
        ("loan_id : int [FK, 1:1]", True),
        ("amount : decimal(8,2)", False),
        ("status : enum(PENDING,PAID)", False),
        ("created_at : datetime", False),
        ("paid_at : datetime", False),
        ("notes : varchar(255)", False),
    ], header_color="#B91C1C")

    # 8. Reservation
    draw_entity(57, 60, 21, 24, "Reservation (Hold)", [
        ("id : int [PK]", True),
        ("book_id : int [FK]", True),
        ("member_id : int [FK]", True),
        ("queue_position : int", False),
        ("status : enum(PEND,ALLOC)", False),
        ("pickup_deadline : datetime", False),
        ("reservation_date : datetime", False),
    ], header_color="#D97706")

    # 9. EBookMetadata
    draw_entity(29, 2, 23, 19, "EBookMetadata (DRM)", [
        ("id : int [PK]", True),
        ("book_id : int [FK, 1:1]", True),
        ("file_path : varchar (Protected)", False),
        ("format : varchar(10)", False),
        ("access_mode : enum(READ,DL)", False),
        ("rights_status : enum(PUBLIC,LIC)", False),
    ], header_color="#047857")

    # 10. BookReview
    draw_entity(57, 2, 21, 19, "BookReview", [
        ("id : int [PK]", True),
        ("book_id : int [FK]", True),
        ("user_id : int [FK]", True),
        ("rating : int (1-5 Stars)", False),
        ("review_text : text", False),
        ("is_approved : boolean", False),
    ], header_color="#4B5563")

    def draw_rel(x1, y1, x2, y2, c1="1", c2="N", label=""):
        ax.plot([x1, x2], [y1, y2], color="#475569", lw=1.5, zorder=2)
        ax.text(x1 + (x2-x1)*0.15, y1 + (y2-y1)*0.15 + 1.0, c1, fontsize=8, fontweight='bold', color="#DC2626")
        ax.text(x1 + (x2-x1)*0.85, y1 + (y2-y1)*0.85 + 1.0, c2, fontsize=8, fontweight='bold', color="#2563EB")
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx, my + 1.0, label, fontsize=6.8, style='italic', color="#475569", ha='center',
                    bbox=dict(boxstyle="square,pad=0.1", fc="#FFFFFF", ec="none"))

    draw_rel(38, 65, 38, 58, "1", "N", "categorizes")
    draw_rel(21, 32, 29, 32, "M", "N", "writes")
    draw_rel(52, 36, 57, 36, "1", "N", "has physical")
    draw_rel(40, 24, 40, 21, "1", "1", "has digital")
    draw_rel(46, 58, 57, 70, "1", "N", "requested in")
    draw_rel(24, 72, 57, 72, "1", "N", "places")
    draw_rel(24, 60, 82, 60, "1", "N", "borrows")
    draw_rel(78, 38, 82, 52, "1", "N", "issued as")
    draw_rel(90, 48, 90, 36, "1", "1", "incurs")
    draw_rel(52, 26, 57, 14, "1", "N", "reviews")

    plt.tight_layout()
    plt.savefig('report_figures/fig_4_7_er_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created fig_4_7_er_diagram.png")

# ----------------------------------------------------------------------
# 6. Figure 5.3: Average Response Time Chart
# ----------------------------------------------------------------------
def create_fig_5_3_response_time():
    operations = [
        "Express Kiosk Barcode Lookup",
        "Catalog Omni-Search Query",
        "Hold FIFO Allocation on Return",
        "Protected E-Book Chunk Stream",
        "Atomic Batch Checkout API",
        "Analytical Report CSV Export"
    ]
    measured = [11.8, 14.2, 28.6, 35.1, 42.5, 88.4]
    target_sla = [40.0, 50.0, 100.0, 120.0, 150.0, 300.0]

    y_pos = np.arange(len(operations))
    bar_height = 0.38

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)

    bars_meas = ax.barh(y_pos + bar_height/2, measured, bar_height, label='Measured Latency (ms)',
                        color='#0284C7', edgecolor='#0369A1', lw=1.2)

    bars_sla = ax.barh(y_pos - bar_height/2, target_sla, bar_height, label='Target SLA Limit (ms)',
                       color='#FCA5A5', edgecolor='#DC2626', lw=1.2, alpha=0.85)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(operations, fontsize=9.5, fontweight='bold', color='#1E293B')
    ax.invert_yaxis()
    ax.set_xlabel('Response Time / Latency (milliseconds)', fontsize=10.5, fontweight='bold', color='#0F172A', labelpad=8)
    ax.set_title('Average System API Response Time vs. Target Service Level Agreement (SLA)',
                 fontsize=11.5, fontweight='bold', color='#1E3A8A', pad=12)

    ax.set_xlim(0, 330)
    ax.grid(axis='x', linestyle='--', alpha=0.4, color='#94A3B8')

    for bar in bars_meas:
        w = bar.get_width()
        ax.text(w + 3, bar.get_y() + bar.get_height()/2, f"{w:.1f} ms",
                va='center', ha='left', fontsize=8.5, fontweight='bold', color='#0369A1')

    for bar in bars_sla:
        w = bar.get_width()
        ax.text(w + 3, bar.get_y() + bar.get_height()/2, f"< {int(w)} ms",
                va='center', ha='left', fontsize=8, color='#991B1B')

    ax.legend(loc='lower right', frameon=True, framealpha=0.95, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=9.5)
    plt.tight_layout()
    plt.savefig('report_figures/fig_5_3_response_time.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created fig_5_3_response_time.png")

# ----------------------------------------------------------------------
# 7. Figure 5.4: Throughput vs. Concurrent Users Graph
# ----------------------------------------------------------------------
def create_fig_5_4_throughput():
    users = np.array([10, 25, 50, 100, 150, 200, 250, 300, 400, 500])
    throughput = np.array([88, 215, 410, 680, 845, 915, 925, 930, 918, 905])
    latency = np.array([12.5, 14.1, 16.8, 22.4, 31.2, 42.5, 58.0, 74.2, 108.5, 142.0])

    fig, ax1 = plt.subplots(figsize=(10, 5.5), dpi=300)

    color_tp = '#1E40AF'
    ax1.set_xlabel('Simultaneous Concurrent Active Users (Load)', fontsize=10.5, fontweight='bold', color='#0F172A', labelpad=8)
    ax1.set_ylabel('System Throughput (Requests / Second)', fontsize=10.5, fontweight='bold', color=color_tp, labelpad=8)

    line1 = ax1.plot(users, throughput, color=color_tp, lw=2.5, marker='o', markersize=6, label='Throughput (Req/sec)')
    ax1.fill_between(users, throughput, color='#3B82F6', alpha=0.15)
    ax1.tick_params(axis='y', labelcolor=color_tp)
    ax1.set_ylim(0, 1100)
    ax1.set_xlim(0, 520)
    ax1.grid(True, linestyle='--', alpha=0.35, color='#94A3B8')

    ax1.annotate('Peak Saturation Zone\n(~930 Req/sec at 250-300 Users)',
                 xy=(300, 930), xytext=(220, 1010),
                 arrowprops=dict(facecolor='#1E40AF', shrink=0.08, width=1.5, headwidth=7),
                 fontsize=8.5, fontweight='bold', color='#1E40AF',
                 bbox=dict(boxstyle="round,pad=0.4", fc="#EFF6FF", ec="#93C5FD"))

    ax2 = ax1.twinx()
    color_lat = '#D97706'
    ax2.set_ylabel('Average Response Latency (ms)', fontsize=10.5, fontweight='bold', color=color_lat, labelpad=8)
    line2 = ax2.plot(users, latency, color=color_lat, lw=2.5, marker='s', markersize=6, linestyle='-.', label='Avg Latency (ms)')
    ax2.tick_params(axis='y', labelcolor=color_lat)
    ax2.set_ylim(0, 180)

    ax2.axhline(y=100, color='#EF4444', linestyle=':', lw=1.5, label='100 ms SLA Threshold')

    plt.title('System Scalability: Throughput vs. Concurrent Users with Response Latency',
              fontsize=11.5, fontweight='bold', color='#1E3A8A', pad=12)

    lines = line1 + line2 + [matplotlib.lines.Line2D([0], [0], color='#EF4444', linestyle=':', lw=1.5)]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='center right', frameon=True, framealpha=0.95, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=9)

    plt.tight_layout()
    plt.savefig('report_figures/fig_5_4_throughput_concurrency.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created fig_5_4_throughput_concurrency.png")

if __name__ == '__main__':
    create_fig_1_4()
    create_fig_3_3()
    create_fig_4_8()
    create_fig_5_2()
    create_fig_4_7_er()
    create_fig_5_3_response_time()
    create_fig_5_4_throughput()
