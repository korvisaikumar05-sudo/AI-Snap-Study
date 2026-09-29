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


MODEL = "gemini-3.8-flash"


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

        with st.spinner("Gemini is analyzing the image..."):

            try:

                response = None

                for attempt in range(5):

                    try:

                        response = client.models.generate_content(
                            model=MODEL,
                            contents=[
                                SYSTEM_PROMPT,
                                image
                            ]
                        )

                        break

                    except Exception as e:

                        if "503" in str(e) and attempt < 4:

                            wait_time = 10 * (2 ** attempt)

                            time.sleep(wait_time)

                        else:

                            raise e


                if response is not None:

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


    st.subheader("📧 Send Explanation by Email")

    email_address = st.text_input(
        "Enter email address"
    )


    if st.button("📧 Send Email"):

        if email_address:

            try:

                message = MIMEText(
                    st.session_state["explanation"],
                    "plain"
                )

                message["Subject"] = (
                    "AI Snap & Study - Explanation"
                )

                message["From"] = (
                    st.secrets["GMAIL_ADDRESS"]
                )

                message["To"] = email_address


                with smtplib.SMTP_SSL(
                    "smtp.gmail.com",
                    465
                ) as server:

                    server.login(
                        st.secrets["GMAIL_ADDRESS"],
                        st.secrets["GMAIL_APP_PASSWORD"]
                    )

                    server.send_message(
                        message
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


    for message in st.session_state.get(
        "chat_history",
        []
    ):

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
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


                    response = None


                    for attempt in range(5):

                        try:

                            response = client.models.generate_content(
                                model=MODEL,
                                contents=conversation
                            )

                            break


                        except Exception as e:

                            if "503" in str(e) and attempt < 4:

                                wait_time = 10 * (2 ** attempt)

                                time.sleep(wait_time)

                            else:

                                raise e


                    if response is not None:

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