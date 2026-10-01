import io
import time
import smtplib
from email.mime.text import MIMEText

import streamlit as st
from google import genai
from PIL import Image

from prompts import SYSTEM_PROMPT


st.set_page_config(
    page_title="AI Snap & Study",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="auto",
)


# ==================================================
# GEMINI (unchanged integration + retry logic)
# ==================================================

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


MODELS = [
    "gemini-3.1-flash-lite"
]


def generate_response(contents):

    last_error = None

    for model in MODELS:

        for attempt in range(3):

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=contents
                )

                return response

            except Exception as e:

                last_error = e

                if "503" in str(e):

                    if attempt < 2:
                        time.sleep(5 * (2 ** attempt))
                    else:
                        break

                else:

                    raise e

    raise last_error


# ==================================================
# GMAIL SMTP (unchanged)
# ==================================================

def send_email(email_address, content, subject):

    message = MIMEText(content, "plain")
    message["Subject"] = subject
    message["From"] = st.secrets["GMAIL_ADDRESS"]
    message["To"] = email_address

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(
            st.secrets["GMAIL_ADDRESS"],
            st.secrets["GMAIL_APP_PASSWORD"]
        )
        server.send_message(message)


# ==================================================
# STYLES
# ==================================================

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

:root {
    --cocoa: #241713;
    --cocoa-2: #3a2620;
    --cream: #FAF6F1;
    --surface: #FFFFFF;
    --line: #EADFD5;
    --ink: #1F1A17;
    --ink-soft: #6B5E56;
    --accent: #6366F1;
    --accent-2: #8B5CF6;
    --radius: 18px;
    --shadow: 0 1px 2px rgba(36,23,19,.05), 0 8px 24px rgba(36,23,19,.06);
}

/* Font is applied only to the app root and inherited. Do NOT use a wildcard
   like [class*="st-"] here: it overrides Streamlit's Material icon font and
   icons render as their names (e.g. "upload"). */
html, body, .stApp {
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
}

.stApp { background: var(--cream); color: var(--ink); }
.block-container { padding-top: 2rem; padding-bottom: 6rem; max-width: 820px; }
img { max-width: 100%; height: auto; }

/* ---------- Hero ---------- */
.ss-hero {
    background: var(--cocoa);
    background-image: radial-gradient(circle at 100% 0%, rgba(139,92,246,.22), transparent 55%);
    color: #F6EEE7;
    border-radius: 24px;
    padding: 2.2rem 2rem 1.8rem;
    box-shadow: var(--shadow);
    margin-bottom: 1.4rem;
}
.ss-badge {
    display: inline-block; font-size: .75rem; font-weight: 600; letter-spacing: .04em;
    text-transform: uppercase; color: #CFC4FF;
    background: rgba(99,102,241,.18); border: 1px solid rgba(139,92,246,.35);
    padding: .3rem .7rem; border-radius: 999px; margin-bottom: 1rem;
}
.ss-hero h1 {
    font-family: 'Fraunces', Georgia, serif; font-weight: 700;
    font-size: clamp(1.8rem, 5vw, 2.6rem); line-height: 1.12;
    color: #FFF8F2; margin: 0 0 .7rem; padding: 0;
}
.ss-hero p { color: #D9CBC0; font-size: 1.02rem; margin: 0; max-width: 34rem; }

/* ---------- Steps ---------- */
.ss-steps {
    display: flex; flex-wrap: wrap; gap: .4rem; align-items: center; margin-top: 1.6rem;
}
.ss-step {
    font-size: .82rem; font-weight: 600; color: #EADCD1;
    background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.1);
    padding: .38rem .75rem; border-radius: 999px; white-space: nowrap;
}
.ss-step.active { background: var(--accent); border-color: var(--accent); color: #fff; }
.ss-step.done { color: #B9F0CF; border-color: rgba(185,240,207,.35); }
.ss-arrow { color: #8C766A; font-size: .8rem; }

/* ---------- Section headings ---------- */
.ss-section { margin: 2rem 0 .8rem; }
.ss-section h3 {
    font-family: 'Fraunces', Georgia, serif; font-size: 1.35rem; font-weight: 600;
    color: var(--ink); margin: 0; padding: 0;
}
.ss-section p { color: var(--ink-soft); margin: .25rem 0 0; font-size: .95rem; }

/* ---------- Cards (st.container(border=True)) ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--surface);
    border: 1px solid var(--line) !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow);
}

/* ---------- Uploader ---------- */
/* Only the outer dropzone box is styled. Nothing inside it is touched. */
[data-testid="stFileUploaderDropzone"] {
    background: #FCFAF7; border: 1.5px dashed #D8C9BC; border-radius: 14px;
}
.ss-upload-head { text-align: center; padding: .1rem 0 .6rem; }
.ss-upload-head .icon { font-size: 1.6rem; line-height: 1; }
.ss-upload-head h4 { margin: .3rem 0 .15rem; font-size: 1.05rem; font-weight: 700; color: var(--ink); padding: 0; }
.ss-upload-head p { margin: 0; color: var(--ink-soft); font-size: .9rem; }
.ss-upload-head .fmt { margin-top: .35rem; font-size: .72rem; letter-spacing: .08em; color: #A08C80; font-weight: 600; }

[data-testid="stImage"] img { border-radius: 14px; max-height: 520px; object-fit: contain; }

/* ---------- Buttons ---------- */
.stButton > button, .stFormSubmitButton > button, [data-testid="stPopover"] button {
    border-radius: 12px; font-weight: 600; border: 1px solid var(--line);
    background: var(--surface); color: var(--ink); transition: border-color .15s, background .15s;
}
.stButton > button:hover, [data-testid="stPopover"] button:hover { border-color: var(--accent); color: var(--accent); }
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    color: #fff; border: none; padding: .75rem 1.2rem; font-size: 1rem;
    box-shadow: 0 6px 18px rgba(99,102,241,.28);
}
.stButton > button[kind="primary"]:hover { color: #fff; filter: brightness(1.06); }

/* ---------- Inputs ---------- */
.stTextInput input { border-radius: 10px; }

/* ---------- Explanation ---------- */
.ss-label {
    font-size: .75rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase;
    color: var(--accent); margin-bottom: .4rem;
}

/* ---------- Chat ---------- */
[data-testid="stChatMessage"] {
    background: var(--surface); border: 1px solid var(--line);
    border-radius: 16px; padding: .9rem 1rem; margin-bottom: .6rem;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: #EEEFFE; border-color: #DADCFB;
}
[data-testid="stChatInput"] textarea { font-size: 1rem; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] { background: var(--cocoa); }
[data-testid="stSidebar"] { min-width: 240px !important; max-width: 260px !important; }
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p { color: #E9DDD3; }
.ss-side-title { font-family: 'Fraunces', Georgia, serif; font-size: 1.3rem; color: #FFF8F2 !important; font-weight: 700; }
.ss-side-step { display: flex; gap: .6rem; margin: .6rem 0; color: #E9DDD3; }
.ss-side-step b { display: block; color: #FFF8F2 !important; font-size: .92rem; }
.ss-side-step span { font-size: .8rem; color: #BFAEA2 !important; }
.ss-side-about { font-size: .8rem; color: #BFAEA2 !important; line-height: 1.5; }

/* ---------- Footer ---------- */
.ss-footer { text-align: center; color: #A08C80; font-size: .82rem; margin-top: 3rem; }

/* ---------- Responsive ---------- */
@media (max-width: 640px) {
    .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 1rem; }
    .ss-hero { padding: 1.6rem 1.3rem 1.4rem; border-radius: 20px; }
    .ss-hero p { font-size: .95rem; }
    .ss-arrow { display: none; }
    .ss-step { font-size: .76rem; }
    [data-testid="stImage"] img { max-height: 380px; }
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ==================================================
# SESSION STATE
# ==================================================

st.session_state.setdefault("chat_history", [])
st.session_state.setdefault("image_bytes", None)
st.session_state.setdefault("image_id", None)


def reset_for_new_image(file_id, data):
    """A different image was uploaded: clear old explanation & chat."""
    st.session_state["image_id"] = file_id
    st.session_state["image_bytes"] = data
    st.session_state.pop("explanation", None)
    st.session_state["chat_history"] = []


def get_image():
    """Rebuild the PIL image from session state so it survives reruns."""
    data = st.session_state.get("image_bytes")
    if not data:
        return None
    return Image.open(io.BytesIO(data))


def email_popover(content, subject, key, label="📧 Email this answer"):
    """Compact email form revealed on click."""
    with st.popover(label):
        with st.form(key=f"form_{key}", clear_on_submit=False, border=False):
            address = st.text_input(
                "Email address",
                key=f"addr_{key}",
                placeholder="you@example.com",
            )
            sent = st.form_submit_button("Send", type="primary", width="stretch")

        if sent:
            if not address or "@" not in address:
                st.warning("Please enter a valid email address.")
            else:
                with st.spinner("Sending..."):
                    try:
                        send_email(address, content, subject)
                        st.success("✅ Sent successfully!")
                    except Exception as e:
                        st.error(
                            "⚠️ We couldn't send the email. "
                            "Please check the email address and try again."
                        )
                        with st.expander("Technical details"):
                            st.code(str(e))


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:
    st.markdown('<div class="ss-side-title">📚 AI Snap & Study</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown("**How it works**")
    st.markdown(
        """
        <div class="ss-side-step"><div>📷</div><div><b>Upload</b><span>Upload your question</span></div></div>
        <div class="ss-side-step"><div>🤖</div><div><b>Explain</b><span>Get a simple explanation</span></div></div>
        <div class="ss-side-step"><div>💬</div><div><b>Ask</b><span>Ask follow-up questions</span></div></div>
        <div class="ss-side-step"><div>📧</div><div><b>Share</b><span>Email the explanation</span></div></div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("**About**")
    st.markdown(
        '<div class="ss-side-about">AI Snap & Study uses Gemini to explain '
        "educational images in simple language.</div>",
        unsafe_allow_html=True,
    )


# ==================================================
# HERO + PROGRESS
# ==================================================

has_image = st.session_state["image_bytes"] is not None
has_expl = "explanation" in st.session_state
has_chat = len(st.session_state["chat_history"]) > 0

if not has_image:
    stage = 0
elif not has_expl:
    stage = 1
elif not has_chat:
    stage = 3
else:
    stage = 4

steps = ["📷 Upload", "🔍 Explain", "🤖 Understand", "💬 Ask AI", "📧 Share"]
step_html = []
for i, s in enumerate(steps):
    cls = "active" if i == stage else ("done" if i < stage else "")
    step_html.append(f'<span class="ss-step {cls}">{s}</span>')
steps_markup = '<span class="ss-arrow">→</span>'.join(step_html)

st.markdown(
    f"""
    <div class="ss-hero">
        <div class="ss-badge">📚 AI Snap &amp; Study</div>
        <h1>Turn any question into an easy-to-understand explanation.</h1>
        <p>Snap a problem, diagram, or notes. Let AI explain it step by step.</p>
        <div class="ss-steps">{steps_markup}</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# UPLOAD
# ==================================================

with st.container(border=True):
    st.markdown(
        """
        <div class="ss-upload-head">
            <div class="icon">📷</div>
            <h4>Upload your question</h4>
            <p>Upload a clear photo of your question, diagram, or notes.</p>
            <div class="fmt">JPG • PNG • WEBP</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        file_id = getattr(uploaded_file, "file_id", None) or f"{uploaded_file.name}-{uploaded_file.size}"
        if file_id != st.session_state["image_id"]:
            reset_for_new_image(file_id, uploaded_file.getvalue())

    image = get_image()

    if image is not None:
        st.image(image, caption=uploaded_file.name if uploaded_file else None, width="stretch")

        if st.button(
            "🔍 Explain Image" if not has_expl else "🔁 Explain Again",
            type="primary",
            width="stretch",
        ):
            with st.spinner("Gemini is analyzing your image..."):
                try:
                    response = generate_response([SYSTEM_PROMPT, image])
                    st.session_state["explanation"] = response.text
                    st.session_state["chat_history"] = []
                    st.rerun()
                except Exception as e:
                    st.error("⚠️ Gemini couldn't process the image right now. Please try again.")
                    with st.expander("Technical details"):
                        st.code(str(e))


# ==================================================
# EXPLANATION
# ==================================================

if "explanation" in st.session_state:

    st.markdown(
        '<div class="ss-section"><h3>🤖 AI Explanation</h3>'
        "<p>Here's a step-by-step breakdown of your image.</p></div>",
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown('<div class="ss-label">Explanation</div>', unsafe_allow_html=True)
        st.markdown(st.session_state["explanation"])

        email_popover(
            st.session_state["explanation"],
            "AI Snap & Study - Explanation",
            key="initial",
            label="📧 Share Explanation",
        )

    # ==================================================
    # CHAT
    # ==================================================

    st.markdown(
        '<div class="ss-section"><h3>💬 Ask AI</h3>'
        "<p>Have a question about the image? Ask anything.</p></div>",
        unsafe_allow_html=True,
    )

    for i, message in enumerate(st.session_state["chat_history"]):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                email_popover(
                    message["content"],
                    "AI Snap & Study - AI Answer",
                    key=f"answer_{i}",
                )

    user_question = st.chat_input("Ask a question about this image...")

    if user_question:

        st.session_state["chat_history"].append({
            "role": "user",
            "content": user_question
        })

        with st.chat_message("user"):
            st.markdown(user_question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    conversation = [
                        SYSTEM_PROMPT,
                        get_image(),
                        "Here is the original explanation:",
                        st.session_state["explanation"]
                    ]

                    for message in st.session_state["chat_history"]:
                        conversation.append(
                            f"{message['role']}: {message['content']}"
                        )

                    response = generate_response(conversation)
                    answer = response.text

                    st.session_state["chat_history"].append({
                        "role": "assistant",
                        "content": answer
                    })
                    # Rerun so the new answer renders with its own email button
                    st.rerun()

                except Exception as e:
                    # Remove the unanswered question so history stays consistent
                    st.session_state["chat_history"].pop()
                    st.error("⚠️ Gemini couldn't answer right now. Please try again.")
                    with st.expander("Technical details"):
                        st.code(str(e))


# ==================================================
# FOOTER
# ==================================================

st.markdown(
    '<div class="ss-footer">AI Snap & Study • Learn smarter with AI</div>',
    unsafe_allow_html=True,
)
