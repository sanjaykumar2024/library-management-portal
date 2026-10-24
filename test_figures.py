import os
os.environ['MPLCONFIGDIR'] = '/tmp/mpl'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

os.makedirs('report_figures', exist_ok=True)

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
        # Header
        head_box = patches.FancyBboxPatch((x, y + h - 3.2), w, 3.2, boxstyle="round,pad=0.2", fc=header_color, ec=header_color)
        ax.add_patch(head_box)
        ax.text(x + w/2, y + h - 1.6, name, fontsize=8.5, fontweight='bold', color="#FFFFFF", ha='center', va='center')
        
        # Body
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

    # Draw Connecting Lines with Cardinalities
    def draw_rel(x1, y1, x2, y2, c1="1", c2="N", label=""):
        ax.plot([x1, x2], [y1, y2], color="#475569", lw=1.5, zorder=2)
        ax.text(x1 + (x2-x1)*0.15, y1 + (y2-y1)*0.15 + 1.0, c1, fontsize=8, fontweight='bold', color="#DC2626")
        ax.text(x1 + (x2-x1)*0.85, y1 + (y2-y1)*0.85 + 1.0, c2, fontsize=8, fontweight='bold', color="#2563EB")
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx, my + 1.0, label, fontsize=6.8, style='italic', color="#475569", ha='center',
                    bbox=dict(boxstyle="square,pad=0.1", fc="#FFFFFF", ec="none"))

    # Category -> Book (1:N)
    draw_rel(38, 65, 38, 58, "1", "N", "categorizes")

    # Author <-> Book (M:N)
    draw_rel(21, 32, 29, 32, "M", "N", "writes")

    # Book -> BookCopy (1:N)
    draw_rel(52, 36, 57, 36, "1", "N", "has physical")

    # Book -> EBookMetadata (1:1)
    draw_rel(40, 24, 40, 21, "1", "1", "has digital")

    # Book -> Reservation (1:N)
    draw_rel(46, 58, 57, 70, "1", "N", "requested in")

    # UserProfile -> Reservation (1:N)
    draw_rel(24, 72, 57, 72, "1", "N", "places")

    # UserProfile -> Loan (1:N)
    draw_rel(24, 60, 82, 60, "1", "N", "borrows")

    # BookCopy -> Loan (1:N)
    draw_rel(78, 38, 82, 52, "1", "N", "issued as")

    # Loan -> Fine (1:1)
    draw_rel(90, 48, 90, 36, "1", "1", "incurs")

    # Book -> BookReview (1:N)
    draw_rel(52, 26, 57, 14, "1", "N", "reviews")

    plt.tight_layout()
    plt.savefig('report_figures/fig_4_7_er_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created fig_4_7_er_diagram.png")

create_fig_4_7_er()

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

    # Plot Measured Latency (Blue/Teal)
    bars_meas = ax.barh(y_pos + bar_height/2, measured, bar_height, label='Measured Latency (ms)',
                        color='#0284C7', edgecolor='#0369A1', lw=1.2)

    # Plot Target SLA (Light Red / Coral)
    bars_sla = ax.barh(y_pos - bar_height/2, target_sla, bar_height, label='Target SLA Limit (ms)',
                       color='#FCA5A5', edgecolor='#DC2626', lw=1.2, alpha=0.85)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(operations, fontsize=9.5, fontweight='semibold', color='#1E293B')
    ax.invert_yaxis()  # Labels read top-to-bottom
    ax.set_xlabel('Response Time / Latency (milliseconds)', fontsize=10.5, fontweight='bold', color='#0F172A', labelpad=8)
    ax.set_title('Average System API Response Time vs. Target Service Level Agreement (SLA)',
                 fontsize=11.5, fontweight='bold', color='#1E3A8A', pad=12)

    ax.set_xlim(0, 330)
    ax.grid(axis='x', linestyle='--', alpha=0.4, color='#94A3B8')

    # Value annotations on bars
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

def create_fig_5_4_throughput():
    users = np.array([10, 25, 50, 100, 150, 200, 250, 300, 400, 500])
    throughput = np.array([88, 215, 410, 680, 845, 915, 925, 930, 918, 905]) # requests/sec
    latency = np.array([12.5, 14.1, 16.8, 22.4, 31.2, 42.5, 58.0, 74.2, 108.5, 142.0]) # ms

    fig, ax1 = plt.subplots(figsize=(10, 5.5), dpi=300)

    color_tp = '#1E40AF'
    ax1.set_xlabel('Simultaneous Concurrent Active Users (Load)', fontsize=10.5, fontweight='bold', color='#0F172A', labelpad=8)
    ax1.set_ylabel('System Throughput (Requests / Second)', fontsize=10.5, fontweight='bold', color=color_tp, labelpad=8)

    # Throughput line & fill
    line1 = ax1.plot(users, throughput, color=color_tp, lw=2.5, marker='o', markersize=6, label='Throughput (Req/sec)')
    ax1.fill_between(users, throughput, color='#3B82F6', alpha=0.15)
    ax1.tick_params(axis='y', labelcolor=color_tp)
    ax1.set_ylim(0, 1100)
    ax1.set_xlim(0, 520)
    ax1.grid(True, linestyle='--', alpha=0.35, color='#94A3B8')

    # Peak Throughput Annotation
    ax1.annotate('Peak Saturation Zone\n(~930 Req/sec at 250-300 Users)',
                 xy=(300, 930), xytext=(220, 1010),
                 arrowprops=dict(facecolor='#1E40AF', shrink=0.08, width=1.5, headwidth=7),
                 fontsize=8.5, fontweight='bold', color='#1E40AF',
                 bbox=dict(boxstyle="round,pad=0.4", fc="#EFF6FF", ec="#93C5FD"))

    # Right Y-axis for Latency
    ax2 = ax1.twinx()
    color_lat = '#D97706'
    ax2.set_ylabel('Average Response Latency (ms)', fontsize=10.5, fontweight='bold', color=color_lat, labelpad=8)
    line2 = ax2.plot(users, latency, color=color_lat, lw=2.5, marker='s', markersize=6, linestyle='-.', label='Avg Latency (ms)')
    ax2.tick_params(axis='y', labelcolor=color_lat)
    ax2.set_ylim(0, 180)

    # SLA threshold line
    ax2.axhline(y=100, color='#EF4444', linestyle=':', lw=1.5, label='100 ms SLA Threshold')

    plt.title('System Scalability: Throughput vs. Concurrent Users with Response Latency',
              fontsize=11.5, fontweight='bold', color='#1E3A8A', pad=12)

    # Combined Legend
    lines = line1 + line2 + [matplotlib.lines.Line2D([0], [0], color='#EF4444', linestyle=':', lw=1.5)]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='center right', frameon=True, framealpha=0.95, facecolor='#FFFFFF', edgecolor='#CBD5E1', fontsize=9)

    plt.tight_layout()
    plt.savefig('report_figures/fig_5_4_throughput_concurrency.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created fig_5_4_throughput_concurrency.png")

create_fig_5_3_response_time()
create_fig_5_4_throughput()
