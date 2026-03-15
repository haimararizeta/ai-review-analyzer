import streamlit as st
from groq import Groq
import json

# ─── Configuración de página ───────────────────────────────────────────────
st.set_page_config(
    page_title="Analizador de Reseñas IA",
    page_icon="🔍",
    layout="centered"
)

st.title("🔍 Analizador de Reseñas con IA")
st.caption("Pega las reseñas de cualquier negocio y obtén un informe automático en segundos.")

# ─── API Key ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input("Tu API Key de OpenAI", type="password", placeholder="sk-...")
    st.markdown("[Obtener API Key →](https://platform.openai.com/api-keys)")
    st.divider()
    st.markdown("**¿Cómo usarlo?**")
    st.markdown("1. Entra tu API key\n2. Escribe el nombre del negocio\n3. Pega las reseñas\n4. Pulsa Analizar")

# ─── Formulario principal ───────────────────────────────────────────────────
business_name = st.text_input(
    "Nombre del negocio",
    placeholder="Ej: Restaurante El Txoko, Donostia"
)

reviews_input = st.text_area(
    "Pega aquí las reseñas (una por línea)",
    height=200,
    placeholder="El servicio fue increíble, muy amables...\nLa comida estaba fría y tardaron mucho...\nMejor pintxos de la ciudad, volveré seguro..."
)

analyze_btn = st.button("✨ Analizar reseñas", type="primary", use_container_width=True)

# ─── Lógica de análisis ─────────────────────────────────────────────────────
def analyze_reviews(business_name: str, reviews: str, api_key: str) -> dict:
    client = Groq(api_key=api_key)

    prompt = f"""Eres un experto en análisis de reputación online para negocios locales.

Analiza las siguientes reseñas del negocio "{business_name}" y devuelve un JSON con esta estructura exacta:

{{
  "resumen_general": "2-3 frases resumiendo la percepción general del negocio",
  "puntuacion_estimada": número del 1 al 10,
  "puntos_fuertes": ["punto 1", "punto 2", "punto 3"],
  "puntos_debiles": ["punto 1", "punto 2", "punto 3"],
  "temas_recurrentes": ["tema 1", "tema 2", "tema 3"],
  "recomendacion_accionable": "Un consejo concreto y práctico para mejorar basado en las reseñas"
}}

RESEÑAS:
{reviews}

Responde SOLO con el JSON, sin texto adicional."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    raw = response.choices[0].message.content.strip()
    # Limpiar posibles backticks de markdown
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


# ─── Mostrar resultados ──────────────────────────────────────────────────────
if analyze_btn:
    if not api_key:
        st.error("Añade tu API Key de OpenAI en el panel izquierdo.")
    elif not business_name:
        st.error("Escribe el nombre del negocio.")
    elif not reviews_input.strip():
        st.error("Pega al menos una reseña.")
    else:
        reviews_list = [r.strip() for r in reviews_input.split("\n") if r.strip()]
        st.info(f"Analizando {len(reviews_list)} reseñas...")

        with st.spinner("La IA está procesando..."):
            try:
                result = analyze_reviews(business_name, reviews_input, api_key)

                # Puntuación general
                st.divider()
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.subheader(f"📊 Informe: {business_name}")
                    st.write(result["resumen_general"])
                with col2:
                    score = result["puntuacion_estimada"]
                    color = "🟢" if score >= 7 else "🟡" if score >= 5 else "🔴"
                    st.metric(label="Puntuación IA", value=f"{color} {score}/10")

                st.divider()

                # Puntos fuertes y débiles
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("### ✅ Puntos fuertes")
                    for p in result["puntos_fuertes"]:
                        st.success(p)

                with col_b:
                    st.markdown("### ⚠️ Puntos débiles")
                    for p in result["puntos_debiles"]:
                        st.warning(p)

                # Temas recurrentes
                st.markdown("### 🏷️ Temas más mencionados")
                cols = st.columns(len(result["temas_recurrentes"]))
                for i, tema in enumerate(result["temas_recurrentes"]):
                    cols[i].info(tema)

                # Recomendación
                st.divider()
                st.markdown("### 💡 Recomendación accionable")
                st.info(result["recomendacion_accionable"])

                # Exportar JSON
                st.divider()
                st.download_button(
                    label="⬇️ Descargar informe (JSON)",
                    data=json.dumps(result, ensure_ascii=False, indent=2),
                    file_name=f"informe_{business_name.replace(' ', '_')}.json",
                    mime="application/json"
                )

            except json.JSONDecodeError:
                st.error("Error al procesar la respuesta de la IA. Inténtalo de nuevo.")
            except Exception as e:
                st.error(f"Error: {str(e)}")