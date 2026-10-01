import streamlit as st
from google import genai
from PIL import Image
import time
import smtplib
from email.mime.text import MIMEText

from prompts import SYSTEM_PROMPT


st.set_page_config(
    page_title="AI Snap & Study",
    page_icon="📚",
    layout="centered"
)


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


def send_email(email_address, content, subject):

    message = MIMEText(
        content,
        "plain"
    )

    message["Subject"] = subject

    message["From"] = st.secrets["GMAIL_ADDRESS"]

    message["To"] = email_address


    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as server:

        server.login(
            st.secrets["GMAIL_ADDRESS"],
            st.secrets["GMAIL_APP_PASSWORD"]
        )

        server.send_message(message)


st.title("📚 AI Snap & Study")

st.write(
    "Upload a question, diagram, textbook page, "
    "or notes and Gemini will explain it."
)


uploaded_file = st.file_uploader(
    "📷 Upload an image",
    type=["jpg", "jpeg", "png", "webp"]
)


if uploaded_file is not None:

    image = Image.open(uploaded_file)

    st.image(
        image,
        caption="Uploaded Image",
        use_container_width=True
    )


    if st.button("🔍 Explain Image"):

        with st.spinner(
            "Gemini is analyzing the image..."
        ):

            try:

                response = generate_response([
                    SYSTEM_PROMPT,
                    image
                ])

                st.session_state["explanation"] = response.text

                st.session_state["chat_history"] = []

            except Exception as e:

                st.error(
                    f"Gemini error: {e}"
                )


if "explanation" in st.session_state:

    st.subheader("🤖 AI Explanation")

    st.markdown(
        st.session_state["explanation"]
    )


    st.divider()

    st.subheader("📧 Email Explanation")

    email_address = st.text_input(
        "Enter email address",
        key="initial_email"
    )


    if st.button(
        "📧 Send Explanation by Email",
        key="send_initial_email"
    ):

        if email_address:

            try:

                send_email(
                    email_address,
                    st.session_state["explanation"],
                    "AI Snap & Study - Explanation"
                )

                st.success(
                    "✅ Explanation sent successfully!"
                )

            except Exception as e:

                st.error(
                    f"Email error: {e}"
                )

        else:

            st.warning(
                "Please enter an email address."
            )


    st.divider()

    st.subheader("💬 Ask AI")


    for i, message in enumerate(
        st.session_state.get(
            "chat_history",
            []
        )
    ):

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )


            if message["role"] == "assistant":

                email_key = f"email_{i}"

                email_address = st.text_input(
                    "Enter email address",
                    key=f"address_{i}"
                )


                if st.button(
                    "📧 Send This Answer by Email",
                    key=email_key
                ):

                    if email_address:

                        try:

                            send_email(
                                email_address,
                                message["content"],
                                "AI Snap & Study - AI Answer"
                            )

                            st.success(
                                "✅ Answer sent successfully!"
                            )

                        except Exception as e:

                            st.error(
                                f"Email error: {e}"
                            )

                    else:

                        st.warning(
                            "Please enter an email address."
                        )


    user_question = st.chat_input(
        "Ask a question about this image..."
    )


    if user_question:

        st.session_state["chat_history"].append({
            "role": "user",
            "content": user_question
        })


        with st.chat_message("user"):

            st.markdown(
                user_question
            )


        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                try:

                    conversation = [
                        SYSTEM_PROMPT,
                        image,
                        "Here is the original explanation:",
                        st.session_state["explanation"]
                    ]


                    for message in st.session_state[
                        "chat_history"
                    ]:

                        conversation.append(
                            f"{message['role']}: "
                            f"{message['content']}"
                        )


                    response = generate_response(
                        conversation
                    )


                    answer = response.text

                    st.markdown(
                        answer
                    )


                    st.session_state[
                        "chat_history"
                    ].append({
                        "role": "assistant",
                        "content": answer
                    })


                except Exception as e:

                    st.error(
                        f"Chat error: {e}"
                    )