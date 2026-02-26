import streamlit as st
import anthropic

st.set_page_config(page_title="Chat Anthropic", page_icon="🧠", layout="centered")

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuración")

    api_key = st.text_input("🔑 Anthropic API Key", type="password", placeholder="sk-ant-...")

    st.divider()
    st.subheader("🤖 Modelo")

    model = st.selectbox("Modelo", [
        "claude-opus-4-5",
        "claude-sonnet-4-5",
        "claude-haiku-4-5-20251001",
    ])

    st.divider()
    st.subheader("🎛️ Parámetros")

    max_tokens = st.slider("Max Tokens", min_value=256, max_value=8192, value=1024, step=256,
                           help="Número máximo de tokens en la respuesta.")

    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=1.0, step=0.05,
                            help="0 = más determinista, 1 = más creativo.")

    top_p = st.slider("Top P", min_value=0.0, max_value=1.0, value=0.999, step=0.001,
                      help="Muestrea del top P% de tokens más probables.")

    top_k = st.slider("Top K", min_value=1, max_value=500, value=250, step=1,
                      help="Considera solo los K tokens más probables.")

    st.divider()
    st.subheader("🤖 Personalidad")

    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = ""

    system_input = st.text_area(
        "System Prompt",
        value=st.session_state.system_prompt,
        placeholder="Ej: Eres un asistente experto en ciencia de datos. Responde siempre en español.",
        height=160,
        label_visibility="collapsed"
    )

    if st.button("💾 Guardar personalidad", use_container_width=True):
        st.session_state.system_prompt = system_input
        st.success("¡Guardado!")

    if st.session_state.system_prompt:
        preview = st.session_state.system_prompt
        st.caption(f"✅ Activo: *{preview[:60]}...*" if len(preview) > 60 else f"✅ Activo: *{preview}*")

# ── Main ─────────────────────────────────────────────────
st.title("🧠 Chat con Anthropic")

# Inicializar historial
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input del usuario
if prompt := st.chat_input("Escribe un mensaje..."):
    if not api_key:
        st.warning("Por favor ingresa tu API Key en el panel lateral.")
        st.stop()

    # Agregar y mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Llamar a Anthropic
    client = anthropic.Anthropic(api_key=api_key)
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                kwargs = dict(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    messages=st.session_state.messages,
                )
                if st.session_state.system_prompt:
                    kwargs["system"] = st.session_state.system_prompt

                response = client.messages.create(**kwargs)
                reply = response.content[0].text
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Error: {e}")

# Botón limpiar
if st.session_state.messages:
    if st.button("🗑️ Limpiar conversación"):
        st.session_state.messages = []
        st.rerun()
