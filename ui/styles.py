"""Adaptive RAG - Executive Theme with Subtle Background Fills & Thick 2.5px Borders."""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ─── Global Reset ───────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: #f8fafc !important;
    color: #0f172a !important;
}

.stApp {
    background-color: #f8fafc !important;
}

/* Adjust block container top padding so toggle button never overlaps page content */
.block-container {
    padding: 3rem 1.5rem 1rem 1.5rem !important;
    max-width: 100% !important;
}

/* Position native top-left sidebar toggle button cleanly in top bar */
#MainMenu, footer { display: none !important; }
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 3rem !important;
    z-index: 99999 !important;
}
.stDeployButton { display: none !important; }


/* Styled High-Contrast Black Sidebar Toggle Button (Expand / Collapse) */
button[data-testid="stSidebarCollapseButton"],
button[aria-label="Close sidebar"],
button[aria-label="Open sidebar"],
[data-testid="stHeader"] button,
[data-testid="stSidebarHeader"] button {
    background-color: #0f172a !important;
    background: #0f172a !important;
    color: #ffffff !important;
    border: 2px solid #000000 !important;
    border-radius: 8px !important;
    opacity: 1 !important;
    visibility: visible !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2) !important;
    transition: all 0.2s ease !important;
    width: 34px !important;
    height: 34px !important;
    margin: 6px !important;
}

button[data-testid="stSidebarCollapseButton"] *,
button[aria-label="Close sidebar"] *,
button[aria-label="Open sidebar"] *,
[data-testid="stHeader"] button *,
[data-testid="stSidebarHeader"] button * {
    color: #ffffff !important;
    fill: #ffffff !important;
    stroke: #ffffff !important;
}

button[data-testid="stSidebarCollapseButton"]:hover,
button[aria-label="Close sidebar"]:hover,
button[aria-label="Open sidebar"]:hover,
[data-testid="stHeader"] button:hover,
[data-testid="stSidebarHeader"] button:hover {
    background-color: #1e293b !important;
    background: #1e293b !important;
    transform: scale(1.05);
}


/* ─── Sidebar (Soft Tint Panel Background & Thick 2.5px Borders) ── */
section[data-testid="stSidebar"] {
    background-color: #f1f5f9 !important;
    background: #f1f5f9 !important;
    border-right: 2.5px solid #0f172a !important;
}

section[data-testid="stSidebar"] > div {
    background-color: #f1f5f9 !important;
    padding: 0.1rem 0.75rem 0.75rem 0.75rem !important;
    box-sizing: border-box !important;
}


/* App Logo Header */
.app-logo {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 0.38rem 0.55rem;
    border: 2.5px solid #0f172a !important;
    border-radius: 10px;
    background: #ffffff !important;
    margin-bottom: 0.5rem;
    margin-top: -0.25rem !important;
    box-sizing: border-box !important;
}

.app-logo-icon {
    width: 36px;
    height: 36px;
    background: #581c87 !important;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    color: #ffffff !important;
    flex-shrink: 0;
}

.app-logo-name {
    font-size: 1.0rem;
    font-weight: 900;
    color: #0f172a;
    line-height: 1.2;
}

.app-logo-sub {
    font-size: 0.72rem;
    color: #334155;
    font-weight: 700;
}

/* ─── Sidebar Navigation Buttons ─── */
section[data-testid="stSidebar"] div[data-testid="stElementContainer"],
section[data-testid="stSidebar"] div[data-testid="element-container"],
section[data-testid="stSidebar"] div.stButton {
    margin-bottom: 5px !important;
    margin-top: 0 !important;
    padding: 0 !important;
}

/* Inactive Nav Buttons */
section[data-testid="stSidebar"] div.stButton > button {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: 2.5px solid #0f172a !important;
    color: #0f172a !important;
    border-radius: 8px !important;
    padding: 5px 10px !important;
    font-size: 0.86rem !important;
    font-weight: 700 !important;
    text-align: center !important;
    width: 100% !important;
    height: 38px !important;
    min-height: 38px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: none !important;
    transition: all 0.15s ease !important;
    margin: 0 !important;
    white-space: nowrap !important;
}

section[data-testid="stSidebar"] div.stButton > button *,
section[data-testid="stSidebar"] div.stButton > button p,
section[data-testid="stSidebar"] div.stButton > button span {
    color: #0f172a !important;
    font-weight: 700 !important;
}

section[data-testid="stSidebar"] div.stButton > button:hover {
    background: #0f172a !important;
    background-color: #0f172a !important;
    color: #ffffff !important;
}

section[data-testid="stSidebar"] div.stButton > button:hover *,
section[data-testid="stSidebar"] div.stButton > button:hover p,
section[data-testid="stSidebar"] div.stButton > button:hover span {
    color: #ffffff !important;
}

/* Active Nav Button (Solid Dark Black) */
.nav-active-wrap div.stButton > button,
section[data-testid="stSidebar"] div.stButton.nav-active > button {
    background: #0f172a !important;
    background-color: #0f172a !important;
    border: 2.5px solid #000000 !important;
    color: #ffffff !important;
    font-weight: 800 !important;
}

.nav-active-wrap button *,
.nav-active-wrap button div p,
.nav-active-wrap button div span {
    color: #ffffff !important;
    font-weight: 800 !important;
}

/* Add Document Button in Sidebar */
section[data-testid="stSidebar"] div.stButton.add-doc-btn > button {
    background: #ffffff !important;
    color: #0f172a !important;
    border: 2.5px solid #0f172a !important;
    border-radius: 8px !important;
    font-weight: 800 !important;
    margin-top: 6px !important;
    justify-content: center !important;
    height: 38px !important;
    min-height: 38px !important;
    white-space: nowrap !important;
}

section[data-testid="stSidebar"] div.stButton.add-doc-btn > button:hover {
    background: #0f172a !important;
    color: #ffffff !important;
}

/* Active Data Sources Section Header */
.sidebar-section-title {
    font-size: 0.72rem;
    font-weight: 800;
    color: #0f172a;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 0.5rem 0.6rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border: 2.5px solid #0f172a !important;
    border-radius: 6px;
    margin: 0.75rem 0 0.5rem 0;
    background: #ffffff !important;
    box-sizing: border-box !important;
}

.source-badge {
    background: #0f172a;
    color: #ffffff;
    font-size: 0.68rem;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 10px;
}

.doc-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    border-radius: 8px;
    background: #ffffff !important;
    border: 2.5px solid #0f172a;
    margin-bottom: 6px;
}

.doc-icon {
    width: 30px;
    height: 30px;
    background: #991b1b;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 800;
    color: #ffffff;
    flex-shrink: 0;
    border: 1.5px solid #7f1d1d;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.doc-icon.txt {
    color: #ffffff;
    background: #075985;
    border-color: #0c4a6e;
}

.doc-details {
    flex: 1;
    min-width: 0;
}

.doc-name {
    font-size: 0.82rem;
    font-weight: 800;
    color: #0f172a;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.doc-meta {
    font-size: 0.70rem;
    color: #475569;
    margin-top: 1px;
}

/* ─── Main Header & Headings ─────────────────────────────────── */
.welcome-title {
    font-size: 1.7rem;
    font-weight: 900;
    color: #0f172a;
    line-height: 1.2;
    padding-bottom: 8px;
    border-bottom: 3px solid #0f172a;
    width: 100%;
}

.welcome-subtitle {
    font-size: 0.88rem;
    color: #475569;
    margin-top: 4px;
    font-weight: 500;
}

/* Feature Architecture Grid (Slight Tint Background) */
.feature-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin: 1rem 0;
}

.feature-card {
    background: #f1f5f9 !important;
    border: 2.5px solid #0f172a;
    border-radius: 10px;
    padding: 14px 16px;
    transition: all 0.2s ease;
}

.feature-card:hover {
    border-color: #000000;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.feature-title {
    font-size: 0.92rem;
    font-weight: 800;
    color: #0f172a;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
}

.feature-desc {
    font-size: 0.80rem;
    color: #334155;
    line-height: 1.45;
}

/* Suggested Prompts Buttons (Slight Tint Background) */
.prompt-btn, .prompt-btn div.stButton {
    width: 100% !important;
}

.prompt-btn button,
div.prompt-btn div.stButton > button,
div[data-testid="column"] .prompt-btn div.stButton > button {
    background: #f1f5f9 !important;
    border: 2.5px solid #0f172a !important;
    color: #0f172a !important;
    border-radius: 20px !important;
    padding: 6px 8px !important;
    font-size: 0.82rem !important;
    font-weight: 800 !important;
    height: 38px !important;
    min-height: 38px !important;
    white-space: nowrap !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: none !important;
    width: 100% !important;
    text-align: center !important;
    transition: all 0.2s ease !important;
}

.prompt-btn button:hover,
div.prompt-btn div.stButton > button:hover,
div[data-testid="column"] .prompt-btn div.stButton > button:hover {
    background: #0f172a !important;
    color: #ffffff !important;
}

/* AI Message Card (Slight Tint Background) */
.ai-message-card {
    background: #f1f5f9 !important;
    border: 2.5px solid #0f172a;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 16px;
}

.ai-icon {
    width: 28px;
    height: 28px;
    background: #0f172a;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    margin-bottom: 10px;
    color: #ffffff;
}

.ai-content {
    font-size: 0.90rem;
    color: #0f172a;
    line-height: 1.6;
    font-weight: 500;
}

/* Source Pills */
.source-pills-row {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 12px;
    padding-top: 10px;
    border-top: 1.5px solid #e2e8f0;
    font-size: 0.78rem;
    color: #0f172a;
    font-weight: 600;
}

.source-pill {
    background: #0f172a;
    border: 1.5px solid #000000;
    color: #ffffff;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
}

/* Footer Line */
.app-footer {
    font-size: 0.85rem;
    color: #0f172a;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 1rem;
    padding-top: 0.5rem;
    border-top: 2.5px solid #0f172a;
}

/* ─── Right Panel Cards (Slight Tint Background) ─────────────── */
.panel-card {
    background: #f1f5f9 !important;
    border: 2.5px solid #0f172a;
    border-radius: 10px;
    padding: 10px 12px;
    margin-bottom: 8px;
}

.panel-card-title {
    font-size: 0.84rem;
    font-weight: 800;
    color: #0f172a;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 6px;
    padding-bottom: 4px;
    border-bottom: 2.5px solid #0f172a;
}

.panel-time-badge {
    font-size: 0.68rem;
    color: #475569;
    font-weight: 600;
}

.metrics-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
}

.metric-tile {
    background: #e2e8f0 !important;
    border: 2.5px solid #0f172a;
    border-radius: 8px;
    padding: 6px 8px;
}

.metric-label {
    font-size: 0.66rem;
    color: #334155;
    font-weight: 700;
    margin-bottom: 1px;
}

.metric-value {
    font-size: 1.15rem;
    font-weight: 800;
    color: #0f172a;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    letter-spacing: -0.02em;
}

.metric-delta {
    font-size: 0.68rem;
    font-weight: 800;
    margin-top: 2px;
    color: #0f172a;
}

.retrieval-avg-badge {
    background: #0f172a;
    border: 1.5px solid #000000;
    color: #ffffff;
    font-size: 0.70rem;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 5px;
}

/* ─── System Status Grid (Balanced Equal-Proportion Tiles) ───── */
.status-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 6px;
}

.status-tile {
    background: #e2e8f0 !important;
    border: 2.5px solid #0f172a;
    border-radius: 8px;
    padding: 8px 4px;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    height: 88px;
    min-height: 88px;
    box-sizing: border-box !important;
}

.status-service {
    font-size: 0.70rem;
    font-weight: 800;
    color: #0f172a;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2px;
    white-space: nowrap;
    width: 100%;
}

.status-provider {
    font-size: 0.65rem;
    color: #334155;
    margin-top: 1px;
    margin-bottom: 3px;
    font-weight: 700;
    white-space: nowrap;
}

.status-healthy {
    font-size: 0.68rem;
    font-weight: 800;
    color: #0f172a;
    background: #ffffff !important;
    border: 2px solid #0f172a !important;
    border-radius: 6px;
    padding: 2px 0;
    width: 90%;
    text-align: center;
    box-sizing: border-box !important;
}

.all-operational {
    font-size: 0.72rem;
    color: #0f172a;
    font-weight: 800;
    background: #f1f5f9 !important;
    padding: 3px 12px;
    border-radius: 20px;
    border: 2px solid #0f172a;
}

/* Main Action Buttons in Main Content Area */
div.stButton > button {
    background: #0f172a !important;
    background-color: #0f172a !important;
    color: #ffffff !important;
    border: 2.5px solid #000000 !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    transition: all 0.2s ease !important;
    box-shadow: none !important;
}

div.stButton > button *,
div.stButton > button p,
div.stButton > button span {
    color: #ffffff !important;
}

div.stButton > button:hover,
div.stButton > button:focus,
div.stButton > button:active {
    background: #1e293b !important;
    background-color: #1e293b !important;
    color: #ffffff !important;
    border-color: #000000 !important;
}

div.stButton > button:hover *,
div.stButton > button:focus *,
div.stButton > button:active *,
div.stButton > button:hover p,
div.stButton > button:focus p,
div.stButton > button:active p {
    color: #ffffff !important;
}

/* Fix File Uploader Dropzone Container (Thick 2.5px Dashed Border) */
div[data-testid="stFileUploader"] {
    padding: 2px !important;
}

div[data-testid="stFileUploaderDropzone"],
section[data-testid="stFileUploaderDropzone"] {
    background-color: #f1f5f9 !important;
    background: #f1f5f9 !important;
    border: 2.5px dashed #0f172a !important;
    border-radius: 10px !important;
    padding: 12px 14px !important;
    margin: 3px 0 !important;
    box-sizing: border-box !important;
    overflow: visible !important;
}

div[data-testid="stFileUploaderDropzone"] *,
section[data-testid="stFileUploaderDropzone"] * {
    background-color: transparent !important;
    color: #0f172a !important;
}

/* Browse Files Button */
div[data-testid="stFileUploaderDropzone"] button,
section[data-testid="stFileUploaderDropzone"] button {
    background-color: #0f172a !important;
    background: #0f172a !important;
    color: #ffffff !important;
    border: 2px solid #000000 !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    padding: 6px 16px !important;
}

div[data-testid="stFileUploaderDropzone"] button *,
section[data-testid="stFileUploaderDropzone"] button * {
    color: #ffffff !important;
}

/* Uploaded File Chip Container (Thick 2.5px Solid Border & White Background) */
div[data-testid="stFileUploaderFileData"],
[data-testid="stFileUploaderFileData"],
div[data-testid="stFileUploader"] section + ul li,
div[data-testid="stFileUploader"] ul li {
    background-color: #ffffff !important;
    background: #ffffff !important;
    border: 2.5px solid #0f172a !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    margin-top: 8px !important;
    box-sizing: border-box !important;
}

div[data-testid="stFileUploaderFileData"] *,
[data-testid="stFileUploaderFileData"] * {
    color: #0f172a !important;
    font-weight: 800 !important;
    background-color: transparent !important;
}

div[data-testid="stFileUploaderFileData"] button,
[data-testid="stFileUploaderFileData"] button {
    background-color: #0f172a !important;
    background: #0f172a !important;
    color: #ffffff !important;
    border: 2px solid #000000 !important;
    border-radius: 6px !important;
}

/* Fix Chat Input Textarea (Slight Tint Background) */
[data-testid="stChatInput"],
[data-testid="stChatInput"] *,
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] div[data-baseweb="base-input"],
[data-testid="stChatInput"] div[data-baseweb="input"],
[data-testid="stChatInput"] textarea {
    background-color: #ffffff !important;
    background: #ffffff !important;
    color: #0f172a !important;
}

[data-testid="stChatInput"] > div {
    border: 2.5px solid #0f172a !important;
    border-radius: 12px !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #64748b !important;
}

/* Inputs & Selectboxes (High Contrast Executive Theme) */
div[data-baseweb="select"],
div[data-baseweb="select"] > div,
div[data-baseweb="select"] [data-testid="stSelectbox"] {
    background-color: #f1f5f9 !important;
    border: 2.5px solid #0f172a !important;
    border-radius: 8px !important;
    color: #0f172a !important;
}

div[data-baseweb="select"] [data-aria-selected="true"],
div[data-baseweb="select"] span,
div[data-baseweb="select"] div {
    color: #0f172a !important;
    font-weight: 800 !important;
}

div[data-baseweb="select"] svg {
    fill: #0f172a !important;
    color: #0f172a !important;
}

/* Selectbox Dropdown Menu Popover */
ul[data-baseweb="menu"],
div[data-baseweb="popover"],
div[data-baseweb="popover"] ul {
    background-color: #f1f5f9 !important;
    border: 2.5px solid #0f172a !important;
    border-radius: 8px !important;
}

ul[data-baseweb="menu"] li,
div[data-baseweb="popover"] li,
div[data-baseweb="popover"] [role="option"] {
    background-color: #f1f5f9 !important;
    color: #0f172a !important;
    font-weight: 800 !important;
}

ul[data-baseweb="menu"] li:hover,
div[data-baseweb="popover"] li:hover,
div[data-baseweb="popover"] [role="option"]:aria-selected="true",
div[data-baseweb="popover"] [role="option"][aria-selected="true"] {
    background-color: #0f172a !important;
    color: #ffffff !important;
}

ul[data-baseweb="menu"] li:hover *,
div[data-baseweb="popover"] li:hover *,
div[data-baseweb="popover"] [role="option"][aria-selected="true"] * {
    color: #ffffff !important;
}


/* Fix Streamlit Sliders & Labels for Light Executive Theme */
div[data-testid="stWidgetLabel"],
div[data-testid="stWidgetLabel"] *,
label[data-testid="stWidgetLabel"],
label[data-testid="stWidgetLabel"] * {
    color: #0f172a !important;
    font-weight: 800 !important;
}

div[data-testid="stSlider"],
div[data-testid="stSlider"] * {
    color: #0f172a !important;
}

div[data-baseweb="slider"] div[role="slider"] {
    background-color: #0f172a !important;
    border: 2.5px solid #000000 !important;
    box-shadow: none !important;
}

div[data-baseweb="slider"] div[data-testid="stTickBar"] + div,
div[data-baseweb="slider"] > div > div {
    background-color: #0f172a !important;
}

div[data-testid="stSlider"] div[data-testid="stTickBar"] + div span {
    color: #0f172a !important;
    font-weight: 800 !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #f8fafc;
}
::-webkit-scrollbar-thumb {
    background: #94a3b8;
    border-radius: 4px;
}
</style>
"""
