# 🔍 Analizador de Reseñas con IA

Herramienta que analiza reseñas de cualquier negocio y genera un informe automático de puntos fuertes, débiles y recomendaciones usando GPT-4o-mini.

## ¿Qué hace?

- Analiza cualquier cantidad de reseñas en segundos
- Detecta puntos fuertes y débiles del negocio
- Identifica temas recurrentes en las opiniones
- Genera una recomendación accionable concreta
- Exporta el informe en JSON

## Instalación

```bash
# 1. Clona o descarga el proyecto
cd review_analyzer

# 2. Crea un entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# 3. Instala dependencias
pip install -r requirements.txt

# 4. Ejecuta la app
streamlit run app.py
```

## Uso

1. Abre la app en tu navegador (se abre automáticamente en `localhost:8501`)
2. Introduce tu API Key de OpenAI en el panel izquierdo
3. Escribe el nombre del negocio
4. Pega las reseñas (una por línea)
5. Pulsa **Analizar reseñas**

## Coste estimado

Cada análisis usa GPT-4o-mini. Con 20 reseñas, el coste es de aproximadamente **$0.001** (menos de 1 céntimo).

## Stack

- **Frontend:** Streamlit
- **IA:** OpenAI GPT-4o-mini
- **Lenguaje:** Python 3.10+

## Próximas mejoras (ideas para el portfolio)

- [ ] Conectar con la API de Google Maps para importar reseñas automáticamente
- [ ] Añadir análisis de sentimiento por categoría (comida, servicio, precio...)
- [ ] Comparar evolución de reseñas en el tiempo
- [ ] Exportar informe en PDF
- [ ] Dashboard multi-negocio

---

Construido con Python + Streamlit + OpenAI API