import streamlit as st
from groq import Groq
from serpapi import GoogleSearch
import json

# ─── Configuración de página ───────────────────────────────────────────────
st.set_page_config(
    page_title="Analizador de Reseñas IA",
    page_icon="🔍",
    layout="centered"
)

st.title("🔍 Analizador de Reseñas IA")
st.caption("Introduce el nombre de cualquier negocio y obtén un informe automático en segundos.")

# ─── API Keys en sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuración")
    groq_key = st.text_input("API Key de Groq", type="password", placeholder="gsk_...")
    serpapi_key = st.text_input("API Key de SerpApi", type="password", placeholder="...")
    st.divider()
    st.markdown("[Obtener Groq API Key →](https://console.groq.com)")
    st.markdown("[Obtener SerpApi API Key →](https://serpapi.com/manage-api-key)")
    st.divider()
    st.markdown("**¿Cómo usarlo?**")
    st.markdown("1. Añade tus API keys\n2. Escribe el nombre del negocio\n3. Pulsa Analizar\n4. Descarga el informe")

# ─── Formulario principal ───────────────────────────────────────────────────
business_name = st.text_input(
    "Nombre del negocio",
    placeholder="Ej: Picalagartos Madrid"
)

analyze_btn = st.button("✨ Analizar negocio", type="primary", use_container_width=True)

# ─── Funciones ──────────────────────────────────────────────────────────────
def get_reviews(business_name: str, api_key: str) -> tuple[list, str]:
    search = GoogleSearch({
        "q": business_name,
        "api_key": api_key,
        "engine": "google_maps",
        "type": "search",
        "hl": "es"
    })
    results = search.get_dict()

    place = None
    if "place_results" in results:
        place = results["place_results"]
        place_id = place.get("place_id", "")
        place_name = place.get("title", business_name)
    elif "local_results" in results:
        place = results["local_results"][0]
        place_id = place.get("place_id", "")
        place_name = place.get("title", business_name)
    else:
        return [], business_name

    if not place_id:
        return [], business_name

    # Obtener reseñas paginando hasta 100
    all_reviews = []
    next_page_token = None

    while len(all_reviews) < 100:
        params = {
            "engine": "google_maps_reviews",
            "place_id": place_id,
            "api_key": api_key,
            "hl": "es"
        }
        if next_page_token:
            params["next_page_token"] = next_page_token

        reviews_search = GoogleSearch(params)
        reviews_data = reviews_search.get_dict()

        batch = [
            r.get("snippet", "")
            for r in reviews_data.get("reviews", [])
            if r.get("snippet")
        ]
        all_reviews.extend(batch)

        # Si no hay más páginas, paramos
        next_page_token = reviews_data.get("serpapi_pagination", {}).get("next_page_token")
        if not next_page_token:
            break

    return all_reviews[:100], place_name

def analyze_reviews(business_name: str, reviews: list, api_key: str) -> dict:
    client = Groq(api_key=api_key)

    reviews_text = "\n".join([f"- {r}" for r in reviews])

    prompt = f"""Eres un experto en análisis de reputación online para negocios.

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
{reviews_text}

Responde SOLO con el JSON, sin texto adicional."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


# ─── Lógica principal ────────────────────────────────────────────────────────
if analyze_btn:
    if not groq_key:
        st.error("Añade tu API Key de Groq en el panel izquierdo.")
    elif not serpapi_key:
        st.error("Añade tu API Key de SerpApi en el panel izquierdo.")
    elif not business_name:
        st.error("Escribe el nombre del negocio.")
    else:
        with st.spinner("Buscando reseñas en Google Maps..."):
            try:
                reviews, place_name = get_reviews(business_name, serpapi_key)

                if not reviews:
                    st.error("No se encontraron reseñas. Prueba con un nombre más específico, por ejemplo: 'Picalagartos Madrid'")
                    st.stop()

                st.success(f"✅ {len(reviews)} reseñas obtenidas de **{place_name}**")

            except Exception as e:
                st.error(f"Error obteniendo reseñas: {str(e)}")
                st.stop()

        with st.spinner("Analizando con IA..."):
            try:
                result = analyze_reviews(place_name, reviews, groq_key)

                # ── Resultados ──────────────────────────────────────────────
                st.divider()
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.subheader(f"📊 Informe: {place_name}")
                    st.write(result["resumen_general"])
                with col2:
                    score = result["puntuacion_estimada"]
                    color = "🟢" if score >= 7 else "🟡" if score >= 5 else "🔴"
                    st.metric(label="Puntuación IA", value=f"{color} {score}/10")

                st.divider()

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("### ✅ Puntos fuertes")
                    for p in result["puntos_fuertes"]:
                        st.success(p)

                with col_b:
                    st.markdown("### ⚠️ Puntos débiles")
                    for p in result["puntos_debiles"]:
                        st.warning(p)

                st.markdown("### 🏷️ Temas más mencionados")
                cols = st.columns(len(result["temas_recurrentes"]))
                for i, tema in enumerate(result["temas_recurrentes"]):
                    cols[i].info(tema)

                st.divider()
                st.markdown("### 💡 Recomendación accionable")
                st.info(result["recomendacion_accionable"])

                st.divider()

                export_data = {
                    "negocio": place_name,
                    "total_reseñas_analizadas": len(reviews),
                    "informe": result
                }

                st.download_button(
                    label="⬇️ Descargar informe (JSON)",
                    data=json.dumps(export_data, ensure_ascii=False, indent=2),
                    file_name=f"informe_{place_name.replace(' ', '_')}.json",
                    mime="application/json"
                )

            except json.JSONDecodeError:
                st.error("Error al procesar la respuesta de la IA. Inténtalo de nuevo.")
            except Exception as e:
                st.error(f"Error en el análisis: {str(e)}")